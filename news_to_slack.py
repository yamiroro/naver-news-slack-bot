import os, datetime, requests
from bs4 import BeautifulSoup

NAVER_URL = (
    "https://search.naver.com/search.naver?nso=so%3Add%2Cp%3Aall%2Ca%3Aall"
    "&query=%EC%86%8D%EB%B3%B4+%EC%9D%B4%EB%9E%80&sm=tab_smr&sort=1&ssc=tab.news.all"
)
HEADERS = {"User-Agent": "Mozilla/5.0"}
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

def fetch(limit=10):
    html = requests.get(NAVER_URL, headers=HEADERS, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select(".list_news .news_area a.news_tit")[:limit]
    lines = [f"{i+1}. <{t['href']}|{t['title']}>" for i, t in enumerate(items)]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"📰 *네이버 속보 ({now})*\n" + "\n".join(lines)

def send(text):
    r = requests.post(SLACK_WEBHOOK_URL, json={"text": text}, timeout=10)
    r.raise_for_status()

if __name__ == "__main__":
    send(fetch())
