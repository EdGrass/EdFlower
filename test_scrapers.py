"""
test_scrapers.py — 独立测试爬虫，无需 Bot 凭证
用法：python test_scrapers.py
"""
import asyncio
import sys
from scraper import CodeforceScraper, AtCoderScraper, WeatherScraper
import config


async def test(name: str, scraper):
    print(f"\n{'='*40}")
    print(f"测试: {name}")
    print('='*40)
    try:
        text = await scraper.run()
        print(text)
        print(f"\n✅ 已写入: ./data/{scraper.OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ 失败: {e}")


async def main():
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "all"

    if target in ("all", "cf"):
        await test("Codeforces", CodeforceScraper())

    if target in ("all", "at"):
        await test("AtCoder", AtCoderScraper())

    if target in ("all", "weather"):
        for city in config.WEATHER_CITIES:
            await test(f"Weather - {city}", WeatherScraper(city=city))


if __name__ == "__main__":
    asyncio.run(main())
