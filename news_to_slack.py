import os, datetime, urllib.parse, requests

# ─────────────────────────────────────────────
KEYWORD = "속보 이란"          # 원하는 검색어
DISPLAY = 10                  # 가져올 기사 수
API_URL = "https://openapi.naver.com/v1/search/news.json"
HEADERS = {
    "X-Naver-Client-Id":     os.environ["NAVER_CLIENT_ID"],
    "X-Naver-Client-Secret": os.environ["NAVER_CLIENT_SECRET"],
}

SLACK_WEBHOOK = os.environ["SLACK_WEBHOOK_URL"]
# ─────────────────────────────────────────────


def fetch_news() -> str:
    params = {
        "query": urllib.parse.quote(KEYWORD, safe=""),
        "display": DISPLAY,
        "sort": "date",        # 최신순
    }
    resp = requests.get(API_URL, headers=HEADERS, params=params, timeout=10)
    resp.raise_for_status()
    items = resp.json().get("items", [])

    if not items:
        return f"❗ '{KEYWORD}' 관련 기사를 찾지 못했습니다."

    lines = []
    for i, it in enumerate(items[:DISPLAY]):
        title = it["title"].replace("<b>", "").replace("</b>", "")
        link  = it["link"]
        lines.append(f"{i+1}. <{link}|{title}>")

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"📰 *네이버 최신 뉴스 / ‘{KEYWORD}’ ({ts})*\n" + "\n".join(lines)


def post_to_slack(msg: str):
    requests.post(SLACK_WEBHOOK, json={"text": msg}, timeout=10).raise_for_status()


if __name__ == "__main__":
    post_to_slack(fetch_news())
