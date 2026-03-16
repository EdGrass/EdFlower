"""
scraper/codeforces.py — Codeforces 比赛信息爬虫
数据来源：https://codeforces.com/api/contest.list（官方公开 API）
"""
import time
from typing import Any

from .base import HTTPScraper

CF_API = "https://codeforces.com/api/contest.list"
MAX_CONTESTS = 8   # 最多展示几场近期/即将举办的比赛


class CodeforceScraper(HTTPScraper):
    OUTPUT_FILE = "P_codeforces.txt"

    async def fetch(self) -> Any:
        data = await self.get_json(CF_API)
        if data.get("status") != "OK":
            raise RuntimeError(f"Codeforces API 返回异常: {data}")
        return data["result"]

    def format(self, raw: Any) -> str:
        now = int(time.time())

        upcoming = [c for c in raw if c["phase"] == "BEFORE"]
        upcoming.sort(key=lambda c: c.get("startTimeSeconds", 0))
        upcoming = upcoming[:MAX_CONTESTS]

        lines = ["📌 Codeforces 即将举办的比赛", "=" * 30]

        if upcoming:
            lines.append("🕐 即将举办")
            for c in upcoming:
                start = c.get("startTimeSeconds")
                dur   = c.get("durationSeconds", 0)
                if start:
                    start_str = time.strftime("%m-%d %H:%M", time.localtime(start))
                    dur_h = dur // 3600
                    dur_m = (dur % 3600) // 60
                    diff  = start - now
                    if diff > 0:
                        days  = diff // 86400
                        hours = (diff % 86400) // 3600
                        countdown = f"{days}天{hours}小时后" if days else f"{hours}小时后"
                    else:
                        countdown = "即将开始"
                    lines.append(
                        f"  • {c['name']}\n"
                        f"    开始: {start_str}  时长: {dur_h}h{dur_m:02d}m  ({countdown})"
                    )
                else:
                    lines.append(f"  • {c['name']}  (时间待定)")
        else:
            lines.append("暂无即将举办的比赛。")

        lines.append("")
        lines.append(f"更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        return "\n".join(lines)
