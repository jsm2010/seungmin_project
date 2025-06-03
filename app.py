from flask import Flask, request, jsonify, render_template, session
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "your_secret_key"  # 세션 사용을 위한 비밀키

# 날짜 파싱 함수 (자연어 포함)
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

    # 숫자 8자리 날짜 (예: 20250604)
    try:
        parsed_date = datetime.strptime(text, "%Y%m%d")
        return parsed_date.strftime("%Y%m%d")
    except ValueError:
        return None

# 급식 정보 요청 함수
def get_meal_by_date(date_str):
    API_KEY = "ca2a357478f640c98008bec4485b4f69"
    OFFICE_CODE = "B10"   # 예: B10
    SCHOOL_CODE = "7021141"     # 예: 7010569

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

# 챗봇 응답 처리
def get_bot_response(message):
    # 이전에 "급식" 요청 후 날짜 기다리는 중이면
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
    elif "시간표" in message:
        return "오늘은 수학, 과학, 영어 수업이 있습니다."
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