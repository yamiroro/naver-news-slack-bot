import os, datetime, requests
from bs4 import BeautifulSoup

NAVER_URL = (
    "https://search.naver.com/search.naver"
    "?where=news&sm=tab_opt&sort=1&query=%EC%86%8D%EB%B3%B4+%EC%9D%B4%EB%9E%80"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://search.naver.com/",
    "Accept-Language": "ko-KR,ko;q=0.9",
}

SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]


def fetch_latest(limit=10) -> str:
    resp = requests.get(NAVER_URL, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    news_areas = soup.select(".list_news .news_area")

    if not news_areas:
        return "❗ 뉴스 항목을 찾지 못했습니다."

    lines = []
    for i, area in enumerate(news_areas[:limit]):
        a_tag = area.select_one("a.news_tit")
        if a_tag:
            title = a_tag.get("title") or a_tag.get_text(strip=True)
            link = a_tag.get("href")
            lines.append(f"{i + 1}. <{link}|{title}>")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"📰 *네이버 속보 ({now})*\n" + "\n".join(lines)


def post_to_slack(message: str):
    resp = requests.post(
        SLACK_WEBHOOK_URL,
        json={"text": message},
        timeout=10,
    )
    resp.raise_for_status()


if __name__ == "__main__":
    post_to_slack(fetch_latest())
