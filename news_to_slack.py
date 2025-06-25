import requests
import os
from datetime import datetime
from html import unescape
import re

# 환경 변수에서 비밀 정보 가져오기
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# 검색 키워드
QUERY = "이란 속보"
DISPLAY_COUNT = 10

# Naver API 호출
url = "https://openapi.naver.com/v1/search/news.json"
headers = {
    "X-Naver-Client-Id": NAVER_CLIENT_ID,
    "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
}
params = {
    "query": QUERY,
    "display": DISPLAY_COUNT,
    "start": 1,
    "sort": "date"
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

# 뉴스 메시지 구성
items = data.get("items", [])
if items:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"*네이버 최신 뉴스 / ‘{QUERY}’ ({now})*\n"
    for i, item in enumerate(items, 1):
        title = unescape(re.sub(r"<.*?>", "", item["title"]))
        link = item["link"]
        message += f"{i}. <{link}|{title}>\n"
else:
    message = f"❗ ‘{QUERY}’ 관련된 뉴스가 없습니다."

# Slack 전송
slack_response = requests.post(SLACK_WEBHOOK_URL, json={"text": message})
print("Slack 전송 상태:", slack_response.status_code)
