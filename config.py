# ── Bot 凭证 ──────────────────────────────────────────────
BOT_APPID  = "YOUR_APP_ID"       # QQ 机器人 AppID
BOT_TOKEN  = "YOUR_BOT_TOKEN"    # QQ 机器人 Token

# ── 主动推送目标群聊 openid ──────────────────────────────
# 在 QQ 开放平台后台或通过机器人收到的群消息事件中获取 group_openid
TARGET_GROUP_OPENID = "1078274152"

# ── 主动推送扫描间隔（秒）────────────────────────────────
PUSH_INTERVAL = 60

# ── 数据目录 ──────────────────────────────────────────────
DATA_DIR = "./data"

# ── 天气城市列表（wttr.in 格式，支持中英文城市名）────────
# 第一个城市为默认城市（直接发 "weather" 时返回）
WEATHER_CITIES = [
    "Hangzhou",
    "Suzhou",
    "Changzhou",
    "Wuxi",
    "Shanghai",
    "Beijing",
    "Tianjin"
]

# 城市别名映射：用户输入关键词 → WEATHER_CITIES 中的城市名
# 可按需添加中文别名
CITY_ALIAS: dict[str, str] = {
    "杭州":     "Hangzhou",
    "hangzhou": "Hangzhou",
    "苏州":     "Suzhou",
    "suzhou":   "Suzhou",
    "常州":     "Changzhou",
    "changzhou":"Changzhou",
    "无锡":     "Wuxi",
    "wuxi":     "Wuxi",
    "上海":     "Shanghai",
    "shanghai": "Shanghai",
    "北京":     "Beijing",
    "beijing":  "Beijing",
    "天津":     "Tianjin",
    "tianjin":  "Tianjin",
}

# ── 关键词 → 数据文件 映射（天气在 main.py 中动态解析）──
KEYWORD_FILE_MAP = {
    "cf":         "P_codeforces.txt",
    "codeforces": "P_codeforces.txt",
    "at":         "P_atcoder.txt",
    "atcoder":    "P_atcoder.txt",
}
