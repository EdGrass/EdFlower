"""
scraper/base.py — 爬虫抽象基类
所有具体爬虫继承此类，统一 fetch / format / save 接口。
"""
import os
import asyncio
from abc import ABC, abstractmethod
from typing import Any

import aiohttp


class BaseScraper(ABC):
    """通用异步爬虫基类。"""

    OUTPUT_FILE: str = ""          # 子类覆盖，例如 "P_codeforces.txt"
    DATA_DIR: str    = "./data"

    # ── 公共入口 ─────────────────────────────────────────
    async def run(self) -> str:
        """抓取 → 格式化 → 写文件，返回最终文本。"""
        raw  = await self.fetch()
        text = self.format(raw)
        await self.save(text)
        return text

    # ── 子类必须实现 ──────────────────────────────────────
    @abstractmethod
    async def fetch(self) -> Any:
        """从远端获取原始数据，返回解析后的对象（dict / list 等）。"""

    @abstractmethod
    def format(self, raw: Any) -> str:
        """将原始数据格式化为可读字符串。"""

    # ── 通用工具 ──────────────────────────────────────────
    async def save(self, text: str) -> None:
        """将文本异步写入 DATA_DIR/OUTPUT_FILE。"""
        os.makedirs(self.DATA_DIR, exist_ok=True)
        path = os.path.join(self.DATA_DIR, self.OUTPUT_FILE)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._write, path, text)

    @staticmethod
    def _write(path: str, text: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)


class HTTPScraper(BaseScraper, ABC):
    """带 HTTP 请求能力的爬虫基类。"""

    TIMEOUT = aiohttp.ClientTimeout(total=15)

    async def get_json(self, url: str, **kwargs) -> Any:
        async with aiohttp.ClientSession(timeout=self.TIMEOUT) as session:
            async with session.get(url, **kwargs) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def get_text(self, url: str, **kwargs) -> str:
        async with aiohttp.ClientSession(timeout=self.TIMEOUT) as session:
            async with session.get(url, **kwargs) as resp:
                resp.raise_for_status()
                return await resp.text()
