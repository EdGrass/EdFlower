"""
scraper/atcoder.py — AtCoder 比赛信息爬虫
数据来源：AtCoder 官网 https://atcoder.jp/contests/
"""
import re
import time
from datetime import datetime, timezone, timedelta
from typing import Any

from .base import HTTPScraper

AC_URL = "https://atcoder.jp/contests/?lang=ja"
MAX_CONTESTS = 8
JST = timezone(timedelta(hours=9))

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en;q=0.9",
}


class AtCoderScraper(HTTPScraper):
    OUTPUT_FILE = "P_atcoder.txt"

    async def fetch(self) -> Any:
        return await self.get_text(AC_URL, headers=HEADERS)

    def format(self, raw: Any) -> str:
        # Extract the upcoming contests section
        start = raw.find("contest-table-upcoming")
        end   = raw.find("contest-table-active", start)
        if end == -1:
            end = raw.find('<hr>', start + 100)
        section = raw[start:end] if start != -1 else ""

        # Parse each <tr> row
        rows = re.findall(r"<tr>(.*?)</tr>", section, re.DOTALL)

        now = datetime.now(tz=JST)
        contests = []
        for row in rows:
            time_m  = re.search(r"fixtime-full'>([^<]+)</time>", row)
            name_m  = re.search(r'href="/contests/[^"]+">([^<]+)</a>', row)
            dur_tds = re.findall(r'<td[^>]*class="text-center"[^>]*>(.*?)</td>', row, re.DOTALL)
            if not (time_m and name_m):
                continue
            start_str = time_m.group(1).strip()      # e.g. "2026-03-21 21:00:00+0900"
            title     = name_m.group(1).strip()
            duration  = dur_tds[1].strip() if len(dur_tds) >= 2 else "?"
            rated     = re.sub(r"<[^>]+>", "", dur_tds[2]).strip() if len(dur_tds) >= 3 else "?"
            try:
                dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S%z")
            except ValueError:
                continue
            contests.append((dt, title, duration, rated))

        contests = contests[:MAX_CONTESTS]

        lines = ["📌 AtCoder 即将举办的比赛", "=" * 30]
        if contests:
            lines.append("🕐 即将举办")
            for dt, title, duration, rated in contests:
                diff    = dt - now
                total_s = int(diff.total_seconds())
                days    = total_s // 86400
                hours   = (total_s % 86400) // 3600
                countdown = f"{days}天{hours}小时后" if days else f"{hours}小时后"
                start_local = dt.astimezone().strftime("%m-%d %H:%M")
                rated_str   = f"  Rated: {rated}" if rated and rated != "-" else ""
                lines.append(
                    f"  • {title}\n"
                    f"    开始: {start_local}  时长: {duration}  ({countdown}){rated_str}"
                )
        else:
            lines.append("暂无即将举办的比赛。")

        lines.append("")
        lines.append(f"更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        return "\n".join(lines)
