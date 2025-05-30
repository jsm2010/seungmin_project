from flask import Flask, request, jsonify #flask 클래스 가져옴

app = Flask(__name__) #flask 클래스의 인스턴스 생성. 이 인스턴스는 WSGI 애플리케이션이 됨

@app.route("/") # route() 데코레이터로 어떤 URL이 함수를 트리거해야 하는지 Flask에 알림
def hello_world():
    return "<p>Hello, World!</p>" #사용자의 브라우저에 표시하려는 메시지 반환

@app.route("/hi") # route() 데코레이터로 어떤 URL이 함수를 트리거해야 하는지 Flask에 알림
def hi_world():
    return "<p>Hi, World!</p>" #사용자의 브라우저에 표시하려는 메시지 반환

@app.route('/chat', methods=['GET', 'POST'])
def chat_response():
    data = request.get_json()
    data = request
    user_message = data.get('message', '')

    # 간단한 응답 로직 (추후에 GPT나 다른 처리 로직으로 연결 예정)
    if "급식" in user_message:
        response_text = "오늘의 급식은 김치볶음밥입니다."
    else:
        response_text = "무슨 말인지 잘 모르겠어요. 다시 한 번 말씀해 주세요."

    return jsonify({"response": response_text})

if __name__ == '__main__': # python 인터프리터로 직접 실행한다면 현재 동작되는 유일한 서버라는 것을 보장
    app.run(debug=True) # 로컬서버로 실행