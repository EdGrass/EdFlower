"""
scraper/weather.py — 天气信息爬虫
数据来源：wttr.in（免费、无需 API Key，支持中文城市名）
"""
import time
from typing import Any

from .base import HTTPScraper


class WeatherScraper(HTTPScraper):

    def __init__(self, city: str = "Hangzhou"):
        self.city = city
        self.OUTPUT_FILE = f"P_weather_{city.lower()}.txt"

    async def fetch(self) -> Any:
        # format=j1 返回 JSON 格式天气数据
        url = f"https://wttr.in/{self.city}?format=j1&lang=zh"
        return await self.get_json(url)

    def format(self, raw: Any) -> str:
        try:
            # wttr.in may wrap response under a "data" key
            data   = raw.get("data", raw)
            cur    = data["current_condition"][0]
            # nearest_area removed in newer API; fall back to configured city name
            if "nearest_area" in data:
                area   = data["nearest_area"][0]
                city   = area["areaName"][0]["value"]
                region = area["region"][0]["value"]
                city_str = f"{city}, {region}"
            else:
                city_str = self.city

            temp_c  = cur["temp_C"]
            feels   = cur["FeelsLikeC"]
            desc    = cur["lang_zh"][0]["value"] if cur.get("lang_zh") else cur["weatherDesc"][0]["value"]
            humidity = cur["humidity"]
            wind_kmh = cur["windspeedKmph"]
            wind_dir = cur["winddir16Point"]
            vis      = cur["visibility"]

            # 未来 3 天预报
            forecasts = []
            for day in data.get("weather", [])[:3]:
                date    = day["date"]
                max_t   = day["maxtempC"]
                min_t   = day["mintempC"]
                desc3   = day["hourly"][4]["lang_zh"][0]["value"] if day["hourly"][4].get("lang_zh") else \
                          day["hourly"][4]["weatherDesc"][0]["value"]
                forecasts.append(f"  {date}  {min_t}~{max_t}°C  {desc3}")

            lines = [
                f"🌤 {city_str} 天气",
                "=" * 30,
                f"当前: {desc}  {temp_c}°C (体感 {feels}°C)",
                f"湿度: {humidity}%  风速: {wind_kmh} km/h {wind_dir}  能见度: {vis} km",
                "",
                "📅 未来 3 天",
            ] + forecasts + [
                "",
                f"更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            ]
        except (KeyError, IndexError) as e:
            lines = [f"天气数据解析失败: {e}"]

        return "\n".join(lines)
