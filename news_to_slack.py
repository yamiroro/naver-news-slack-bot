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
    "yonhapnewstv.co.kr",
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
    resp = requests.get(NAVER_API_URL, headers=HEADERS, params=param
