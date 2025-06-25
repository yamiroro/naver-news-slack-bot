import os
import datetime
import urllib.parse
import requests

# === 설정 ===
KEYWORD = "이란 속보"
MAX_ARTICLES = 10

NAVER_API_URL = "https://openapi.naver.com/v1/search/news.json"
HEADERS = {
    "X-Naver-Client-Id": os.environ["NAVER_CLIENT_ID"],
    "X-Naver-Client-Secret": os.environ["NAVER_CLIENT_SECRET"],
}
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

# === 허용 뉴스 도메인 리스트 ===
ALLOWED_DOMAINS = [
    "news.naver.com",
    "yna.co.kr",
    "yonhapnewstv.co.kr",  # ✅ 연합뉴스TV 추가
    "joins.com",
    "hani.co.kr",
    "donga.com",
    "khan.co.kr",
    "mbn.co.kr",
    "news1.kr",
    "segye.com"
]

# === 필터링 ===
def is_news_domain(url: str) -> bool:
    return any(domain in url for domain in ALLOWED_DOMAINS)

def keyword_match(item, keyword: str) -> bool:
    content = f"{item['title']} {item['description']}".lower()
    keywords = keyword.lower().split()
    return any(k in content for k in keywords)  # "이란" 또는 "속보" 중 하나만 포함돼도 통과

# === 뉴스 수집 및 필터 ===
def fetch_news() -> str:
    params = {
        "query": urllib.parse.quote(KEYWORD, safe=""),
        "display": 20,
        "sort": "date"
    }
    resp = requests.get(NAVER_API_URL, headers=HEADERS, params=params, timeout=10)
    resp.raise_for_status()

    items = resp.json().get("items", [])
    filtered = [
        it for it in items
        if is_news_domain(it["link"]) and keyword_match(it, KEYWORD)
    ][:MAX_ARTICLES]

    if not filtered:
        return f"❗️‘{KEYWORD}’ 관련된 뉴스가 없습니다."

    lines = []
    for i, it in enumerate(filtered):
        title = it["title"].replace("<b>", "").replace("</b>", "").strip()
        link = it["link"]
        lines.append(f"{i+1}. <{link}|{title}>")

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"📰 *네이버 최신 뉴스 / ‘{KEYWORD}’ ({ts})*\n" + "\n".join(lines)

# === Slack 전송 ===
def post_to_slack(message: str):
    resp = requests.post(SLACK_WEBHOOK_URL, json={"text": message}, timeout=10)
    resp.raise_for_status()

# === 실행 ===
if __name__ == "__main__":
    post_to_slack(fetch_news())
