from flask import Flask, request, jsonify, render_template, session
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

app = Flask(__name__)
app.secret_key = "your_secret_key"

# 날짜 텍스트 파싱 함수
def parse_date_input(text):
    today = datetime.today()
    text = text.strip().replace(" ", "")
    date_map = {
        "오늘": today,
        "내일": today + timedelta(days=1),
        "모레": today + timedelta(days=2),
        "어제": today - timedelta(days=1),
        "그저께": today - timedelta(days=2),
    }

    if text in date_map:
        return date_map[text].strftime("%Y%m%d")

    try:
        parsed_date = datetime.strptime(text, "%Y%m%d")
        return parsed_date.strftime("%Y%m%d")
    except ValueError:
        return None

# 급식 정보 조회 함수
def get_meal_by_date(date_str):
    API_KEY = "ca2a357478f640c98008bec4485b4f69"
    OFFICE_CODE = "B10"
    SCHOOL_CODE = "7021141"

    url = (
        f"https://open.neis.go.kr/hub/mealServiceDietInfo"
        f"?KEY={API_KEY}&Type=json"
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

# 학사일정 텍스트 포맷 함수
def format_schedule(text):
    # 1. 괄호 안 숫자는 일시적으로 치환
    bracket_numbers = re.findall(r'\((\d+(?:,\d+)*)\)', text)
    for i, bn in enumerate(bracket_numbers):
        text = text.replace(f'({bn})', f'__BRACKET{i}__')

    # 2. 일반 숫자에 '일' 붙이기
    text = re.sub(r'(?<![가-힣a-zA-Z\(])(\d{1,2})(?![가-힣a-zA-Z\)\d])', r'\1일', text)

    # 3. 치환한 괄호 안 숫자 복원
    for i, bn in enumerate(bracket_numbers):
        text = text.replace(f'__BRACKET{i}__', f'({bn})')

    # 4. 날짜 시작 시 줄바꿈 (예: 6일현충일 → 6일\n현충일)
    text = re.sub(r'(\d{1,2}일)(?=[가-힣])', r'\1\n', text)

    return text

# 학사일정 크롤링 함수
def get_academic_schedule():
    url = "https://jeondong.sen.ms.kr/19970/subMenu.do"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tags = soup.find_all('a', title="클릭하면 내용을 보실 수 있습니다.")

        seen_tds = set()
        schedule_list = []

        for a_tag in a_tags:
            td = a_tag.find_parent('td')
            if td:
                td_text = td.get_text(strip=True)
                if td_text not in seen_tds:
                    formatted = format_schedule(td_text)
                    schedule_list.append(formatted)
                    seen_tds.add(td_text)

        if not schedule_list:
            return "학사일정 정보를 찾을 수 없어요."
        return "\n".join(schedule_list)

    except Exception as e:
        print("학사일정 크롤링 오류:", e)
        return "학사일정 정보를 가져오는 중 오류가 발생했어요."

# 챗봇 응답 함수
def get_bot_response(message):
    message = message.lower()

    if session.get("awaiting_meal_date"):
        session["awaiting_meal_date"] = False
        parsed_date = parse_date_input(message)
        if parsed_date:
            return get_meal_by_date(parsed_date)
        else:
            return "날짜 형식이 올바르지 않아요. 예: '오늘', '내일', 또는 '20250604'처럼 입력해 주세요."

    if "급식" in message:
        session["awaiting_meal_date"] = True
        return "언제 급식이 궁금하신가요? '오늘', '내일', 또는 '20250604' 형식으로 입력해 주세요."
    elif "학사일정" in message or "행사" in message:
        return get_academic_schedule()
    elif "공지" in message or "공지사항" in message:
        return '학교 공지사항은 <a href="https://jeondong.sen.ms.kr/19967/subMenu.do" target="_blank">이곳에서 확인</a>하실 수 있어요.'
    elif "가정통신문" in message or "통신문" in message:
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

# 라우터 설정
@app.route("/")
def index():
    return render_template("index.html")

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
