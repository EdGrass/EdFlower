"""
main.py — EdFlower QQ 频道机器人入口
功能：
  1. 被动回复：@ 机器人 + 关键词 → 读取对应 P_*.txt 回复
  2. 主动推送：后台循环扫描 data/ 中的 A_*.txt，发现即推送并删除
"""
import asyncio
import glob
import logging
import os

import botpy
from botpy.message import Message

import config
from scraper import AtCoderScraper, CodeforceScraper, WeatherScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("EdFlower")


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def read_data_file(filename: str) -> str:
    """同步读取 DATA_DIR 下的文件，文件不存在时返回提示语。"""
    path = os.path.join(config.DATA_DIR, filename)
    if not os.path.exists(path):
        return f"⚠️ 数据文件 {filename} 尚未生成，请稍后再试。"
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip() or f"⚠️ 数据文件 {filename} 为空。"


def parse_keyword(content: str) -> str | None:
    """从消息正文中匹配关键词，返回对应文件名；未匹配返回 None。"""
    lower = content.lower()

    # 天气：优先匹配"weather <城市>"或"<城市>天气"
    if "weather" in lower or "天气" in lower:
        for alias, city in config.CITY_ALIAS.items():
            if alias in lower:
                return f"P_weather_{city.lower()}.txt"
        # 没有指定城市 → 默认第一个城市
        default = config.WEATHER_CITIES[0]
        return f"P_weather_{default.lower()}.txt"

    for kw, filename in config.KEYWORD_FILE_MAP.items():
        if kw in lower:
            return filename

    return None


# ── 机器人客户端 ───────────────────────────────────────────────────────────────

class EdFlowerBot(botpy.Client):
    """QQ 频道机器人主类。"""

    # ── 生命周期 ──────────────────────────────────────────
    async def on_ready(self):
        logger.info("Bot 已就绪：%s", self.robot.name)
        asyncio.create_task(self._refresh_data_loop())
        asyncio.create_task(self._push_loop())

    # ── 被动回复（频道 @ 消息）────────────────────────────
    async def on_at_message_create(self, message: Message):
        content = message.content or ""
        content = content.replace(f"<@!{self.robot.id}>", "").strip()
        logger.info("频道消息 [%s]: %s", message.author.username, content)
        reply_text = self._build_reply(content)
        await message.reply(content=reply_text)

    # ── 被动回复（群聊 @ 消息）────────────────────────────
    async def on_group_at_message_create(self, message):
        content = message.content or ""
        content = content.replace(f"<@!{self.robot.id}>", "").strip()
        logger.info("群消息 [%s]: %s", message.author.member_openid, content)
        reply_text = self._build_reply(content)
        await self.api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0,
            content=reply_text,
            msg_id=message.id,
        )

    def _build_reply(self, content: str) -> str:
        filename = parse_keyword(content)
        if filename:
            return read_data_file(filename)
        city_list = " / ".join(config.WEATHER_CITIES)
        return (
            "👋 你好！我是 EdFlower，可用指令：\n"
            "  cf / codeforces          — Codeforces 比赛\n"
            "  at / atcoder             — AtCoder 比赛\n"
            f"  weather / 天气           — 默认城市天气（{config.WEATHER_CITIES[0]}）\n"
            f"  weather <城市> / <城市>天气 — 指定城市天气\n"
            f"  支持城市: {city_list}"
        )

    # ── 主动推送后台任务 ──────────────────────────────────
    async def _push_loop(self):
        """每隔 PUSH_INTERVAL 秒扫描 data/A_*.txt，发现即推送并删除。"""
        logger.info("主动推送任务已启动，间隔 %d 秒", config.PUSH_INTERVAL)
        while True:
            await asyncio.sleep(config.PUSH_INTERVAL)
            pattern = os.path.join(config.DATA_DIR, "A_*.txt")
            for filepath in glob.glob(pattern):
                await self._push_file(filepath)

    async def _push_file(self, filepath: str):
        try:
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(None, self._read_and_delete, filepath)
            if text:
                await self.api.post_group_message(
                    group_openid=config.TARGET_GROUP_OPENID,
                    msg_type=0,   # 0 = 纯文本
                    content=text,
                )
                logger.info("已推送文件: %s", filepath)
        except Exception as e:
            logger.error("推送文件 %s 失败: %s", filepath, e)

    @staticmethod
    def _read_and_delete(filepath: str) -> str:
        """读取文件内容后立即删除，防止重复推送（原子性保障）。"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read().strip()
            os.remove(filepath)
            return text
        except FileNotFoundError:
            return ""

    # ── 数据定时刷新 ──────────────────────────────────────
    async def _refresh_data_loop(self):
        """每小时自动抓取一次比赛信息和天气，更新 P_*.txt。"""
        scrapers = [
            CodeforceScraper(),
            AtCoderScraper(),
            *[WeatherScraper(city=c) for c in config.WEATHER_CITIES],
        ]
        while True:
            for scraper in scrapers:
                try:
                    await scraper.run()
                    logger.info("数据已刷新: %s", scraper.OUTPUT_FILE)
                except Exception as e:
                    logger.error("爬虫 %s 失败: %s", scraper.__class__.__name__, e)
            await asyncio.sleep(3600)  # 每小时刷新一次


# ── 程序入口 ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    os.makedirs(config.DATA_DIR, exist_ok=True)

    intents = botpy.Intents(public_guild_messages=True, public_messages=True)
    client  = EdFlowerBot(intents=intents)
    client.run(appid=config.BOT_APPID, secret=config.BOT_SECRET)
