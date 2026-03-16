"""
scraper/atcoder.py — AtCoder 比赛信息爬虫
数据来源：AtCoder Problems 非官方 API（https://kenkoooo.com/atcoder）
"""
import time
from typing import Any

from .base import HTTPScraper

AC_API = "https://kenkoooo.com/atcoder/resources/contests.json"
MAX_CONTESTS = 8


class AtCoderScraper(HTTPScraper):
    OUTPUT_FILE = "P_atcoder.txt"

    # AtCoder Problems API 需要 User-Agent，否则可能 403
    HEADERS = {"User-Agent": "EdFlower-Bot/1.0"}

    async def fetch(self) -> Any:
        return await self.get_json(AC_API, headers=self.HEADERS)

    def format(self, raw: Any) -> str:
        now = int(time.time())

        upcoming = [c for c in raw if c["start_epoch_second"] > now]
        upcoming.sort(key=lambda c: c["start_epoch_second"])
        upcoming = upcoming[:MAX_CONTESTS]

        lines = ["📌 AtCoder 即将举办的比赛", "=" * 30]

        if upcoming:
            lines.append("🕐 即将举办")
            for c in upcoming:
                start = c["start_epoch_second"]
                dur   = c["duration_second"]
                start_str = time.strftime("%m-%d %H:%M", time.localtime(start))
                dur_h = dur // 3600
                dur_m = (dur % 3600) // 60
                diff  = start - now
                days  = diff // 86400
                hours = (diff % 86400) // 3600
                countdown = f"{days}天{hours}小时后" if days else f"{hours}小时后"
                lines.append(
                    f"  • {c['title']}\n"
                    f"    开始: {start_str}  时长: {dur_h}h{dur_m:02d}m  ({countdown})"
                )
        else:
            lines.append("暂无即将举办的比赛。")

        lines.append("")
        lines.append(f"更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        return "\n".join(lines)
