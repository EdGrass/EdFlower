# EdFlower

基于 [qq-botpy](https://github.com/tencent-connect/botpy) 的 QQ 群/频道机器人，提供竞赛信息播报与天气查询功能。

## 功能

| 功能 | 说明 |
|------|------|
| 被动回复 | @ 机器人 + 关键词，返回对应数据文件内容 |
| 主动推送 | 后台扫描 `data/A_*.txt`，发现即推送到目标群并删除 |
| 数据自动刷新 | 每小时自动抓取一次比赛信息与天气，更新 `data/P_*.txt` |

### 支持的查询关键词

| 关键词 | 返回内容 |
|--------|----------|
| `cf` / `codeforces` | Codeforces 即将举办的比赛 |
| `at` / `atcoder` | AtCoder 即将举办的比赛 |
| `weather` / `天气` | 默认城市天气（见 `config.py`） |
| `weather <城市>` / `<城市>天气` | 指定城市天气 |

## 项目结构

```
EdFlower/
├── main.py            # Bot 主入口
├── config.py          # 配置（AppID / Secret / 城市列表等）
├── requirements.txt   # 依赖
├── test_scrapers.py   # 爬虫独立测试脚本
├── scraper/
│   ├── base.py        # 爬虫抽象基类（BaseScraper / HTTPScraper）
│   ├── codeforces.py  # Codeforces 爬虫（官方 API）
│   ├── atcoder.py     # AtCoder 爬虫（爬取官网 HTML）
│   └── weather.py     # 天气爬虫（wttr.in）
└── data/              # 数据文件（自动生成）
    ├── P_atcoder.txt
    ├── P_codeforces.txt
    └── P_weather_<city>.txt
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 `config.py`

```python
BOT_APPID   = "YOUR_APP_ID"      # QQ 机器人 AppID
BOT_SECRET  = "YOUR_BOT_SECRET"  # QQ 机器人 Secret
TARGET_GROUP_OPENID = "..."      # 主动推送目标群 openid
```

其余配置项（城市列表、关键词映射、推送间隔）均在 `config.py` 中，按需修改。

### 3. 测试爬虫（可选）

```bash
# 测试全部爬虫
python test_scrapers.py

# 仅测试 AtCoder
python test_scrapers.py at

# 仅测试天气
python test_scrapers.py weather
```

### 4. 启动 Bot

```bash
python main.py
```

## 数据文件说明

| 前缀 | 含义 | 示例 |
|------|------|------|
| `P_` | Publishable，可发布的缓存数据，由爬虫定时生成 | `P_atcoder.txt` |
| `A_` | Active push，待推送文件，Bot 检测到后推送并删除 | `A_公告.txt` |

## 数据来源

| 爬虫 | 数据源 |
|------|--------|
| Codeforces | [codeforces.com/api](https://codeforces.com/api/contest.list) |
| AtCoder | [atcoder.jp/contests](https://atcoder.jp/contests/) |
| 天气 | [wttr.in](https://wttr.in)（免费，无需 API Key） |

## 依赖

- Python 3.11+
- `qq-botpy >= 1.0.0`
- `aiohttp >= 3.9.0`
