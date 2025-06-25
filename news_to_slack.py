import os, datetime, requests
from bs4 import BeautifulSoup

# ① 검색 URL ------------------------------------------------------------------
#  - where=news 파라미터로 ‘뉴스’ 탭 고정
#  - sort=1   → 최신순
NAVER_URL = (
    "https://search.naver.com/search.naver"
    "?where=news&sm=tab_opt"
    "&sort=1&query=%EC%86%8D%EB%B3%B4+%EC%9D%B4%EB%9E%80"
)

# ② 요청 헤더 (User-Agent + Referer) -------------------------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://search.naver.com/",
    "Accept-Language": "ko-KR,ko;q=0.9",
}

# ③ Slack Webhook URL은 GitHub Secret으로 주입
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]  # 필수

# -----------------------------------------------------------------------------


def fetch_latest(limit: int = 10) -> str:
    """네이버 뉴스 검색 결과에서 최신 뉴스 제목·링크 추출 후 문자열 반환"""
    resp = requests.get(NAVER_URL, headers=HEADERS, timeout=10)
    resp.raise_for_status()  # 2xx 아니면 예외

    soup = BeautifulSoup(resp.text, "html.parser")
    anchors = soup.select("a.news_tit")  # 모든 뉴스 제목 앵커

    # 예외 처리: 셀렉터에 실패하면 경고 메시지 반환
    if not anchors:
        return "❗️뉴스 항목을 찾지 못했습니다. (셀렉터 확인 필요)"

    lines = []
    for i, a in enumerate(anchors[:limit]):
        title = a.get_text(strip=True)
        link = a["href"]
        lines.append(f"{i + 1}. <{link}|{title}>")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"📰 *네이버 속보 ({now})*\n" + "\n".join(lines)


def post_to_slack(message: str):
    """메시지를 Slack으로 전송"""
    resp = requests.post(
        SLACK_WEBHOOK_URL,
        json={"text": message},
        timeout=10,
    )
    resp.raise_for_status()


if __name__ == "__main__":
    post_to_slack(fetch_latest())
