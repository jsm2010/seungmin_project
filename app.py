from flask import Flask, request, jsonify, render_template, session
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# Selenium 관련 import
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
app.secret_key = "bimil"

# 날짜 파싱 함수 (자연어 포함)
def parse_date_input(text):
    today = datetime.today()
    text = text.strip().replace(" ", "")

    # 기본적인 매핑
    date_map = {
        "오늘": today,
        "내일": today + timedelta(days=1),
        "모레": today + timedelta(days=2),
        "어제": today - timedelta(days=1),
        "그저께": today - timedelta(days=2),
    }

    if text in date_map:
        return date_map[text].strftime("%Y%m%d")

    # 요일 매핑 (0=월요일, 6=일요일)
    weekdays = {
        "월요일": 0, "화요일": 1, "수요일": 2,
        "목요일": 3, "금요일": 4, "토요일": 5, "일요일": 6
    }

    # 이번주 / 다음주 / 요일만 처리
    for key, target_weekday in weekdays.items():
        if ("이번주" in text or text == key) and key in text:
            current_weekday = today.weekday()
            diff = target_weekday - current_weekday
            target_date = today + timedelta(days=diff)
            return target_date.strftime("%Y%m%d")

        elif "다음주" in text and key in text:
            current_weekday = today.weekday()
            diff = (7 - current_weekday) + target_weekday
            target_date = today + timedelta(days=diff)
            return target_date.strftime("%Y%m%d")

    # YYYYMMDD 형식 직접 입력
    try:
        parsed_date = datetime.strptime(text, "%Y%m%d")
        return parsed_date.strftime("%Y%m%d")
    except ValueError:
        return None


# 급식 정보 요청
def get_meal_by_date(date_str):
    API_KEY = "ca2a357478f640c98008bec4485b4f69"
    OFFICE_CODE = "B10"
    SCHOOL_CODE = "7021141"

    url = (
        f"https://open.neis.go.kr/hub/mealServiceDietInfo"
        f"?KEY={API_KEY}"
        f"&Type=json"
        f"&ATPT_OFCDC_SC_CODE={OFFICE_CODE}"
        f"&SD_SCHUL_CODE={SCHOOL_CODE}"
        f"&MLSV_YMD={date_str}"
    )

    try:
        response = requests.get(url)
        data = response.json()
        meals = data['mealServiceDietInfo'][1]['row'][0]['DDISH_NM']
        meals = meals.replace('<br/>', '\n')
        date_kor = datetime.strptime(date_str, "%Y%m%d").strftime("%m월 %d일")
        return f"{date_kor} 급식은:\n{meals}"
    except Exception as e:
        print("급식 정보 오류:", e)
        return "해당 날짜의 급식 정보를 찾을 수 없어요."

# 학사일정 파싱 함수 (로컬 HTML 파일)
def parse_school_schedule():
    try:
        with open("school_schedule.html", "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        result = []
        for a_tag in soup.find_all('a', title="클릭하면 내용을 보실 수 있습니다."): # 클릭하면 내용을 보실 수 있습니다.라는 title을 가진 a태그 찾기
            td_tag = a_tag.find_parent('td')
            td_text = td_tag.get_text(strip=True) if td_tag else ''
            date_part = ''
            content_text = td_text
            for i, ch in enumerate(td_text):
                if ch.isdigit():
                    date_part += ch
                else:
                    content_text = td_text[i:]
                    break
            title = f"{date_part}일"
            content = content_text
            result.append((title, content))
        return result
    except Exception as e:
        print("학사일정 파싱 오류:", e)
        return []

# Selenium을 활용한 실시간 공지사항 크롤링 함수
def fetch_notices_with_selenium():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 창 띄우지 않고 실행
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://jeondong.sen.ms.kr/19967/subMenu.do")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.flag_notice"))
        )

        results = []
        notices = driver.find_elements(By.CSS_SELECTOR, "span.flag_notice")
        for notice in notices:
            tr = notice.find_element(By.XPATH, "./ancestor::tr")
            subject_td = tr.find_element(By.CSS_SELECTOR, "td.subject")
            title = subject_td.text.strip()
            results.append(title)
    except Exception as e:
        results = [f"공지사항 크롤링 오류: {e}"]
    finally:
        driver.quit()

    return results

# 챗봇 응답 처리
def get_bot_response(message): 
    if session.get("awaiting_meal_date"):
        session["awaiting_meal_date"] = False
        parsed_date = parse_date_input(message)
        if parsed_date:
            return get_meal_by_date(parsed_date)
        else:
            return "날짜 형식이 올바르지 않아요. 예: '오늘', '내일', 또는 '20250604'처럼 입력해 주세요."

    message = message.lower()

    if "급식" in message:
        session["awaiting_meal_date"] = True
        return "언제 급식이 궁금하신가요? '오늘', '내일', 또는 '20250604' 형식으로 입력해 주세요."

    elif "학사일정" in message:
        schedule = parse_school_schedule()
        if not schedule:
            return "학사일정 정보를 불러올 수 없어요."
        response = ""
        for title, content in schedule[:5]:
            response += f"[{title}] {content}<br>"
        return response.strip()

    elif "공지사항" in message:
        notices = fetch_notices_with_selenium()
        if not notices:
            return "🔍 공지된 게시물이 없습니다."
        if len(notices) == 1 and notices[0].startswith("공지사항 크롤링 오류"):
            return notices[0]

        response = ""
        for title in notices[:5]:
            response += f"<br>[공지] {title}"
        response += '<br><br>더 많은 정보는 <a href="https://jeondong.sen.ms.kr/19967/subMenu.do" target="_blank">이곳에서 확인</a>하실 수 있어요.'
        return response.strip()

    elif "가정통신문" in message:
        return '가정통신문은 <a href="https://jeondong.sen.ms.kr/19968/subMenu.do" target="_blank">이곳에서 확인</a>하실 수 있어요.'

    elif "전동중" in message or "전동중학교" in message:
        return (
            '전동중학교는 1985년 3월 5일 개교한 서울특별시 동대문구 휘경2동 소재 공립 중학교입니다. '
            '더 많은 정보는 <a href="https://jeondong.sen.ms.kr/19961/subMenu.do" target="_blank">이곳에서 확인</a>하실 수 있어요.'
        )

    elif "안녕" in message:
        return "안녕하세요! 무엇을 도와드릴까요?"

    else:
        return "죄송해요, 이해하지 못했어요. 다른 질문을 해 주세요."

# 기본 페이지
@app.route("/")
def index():
    return render_template("index.html")

# 챗봇 API
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "message가 없습니다."}), 400
    bot_response = get_bot_response(user_message)
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
