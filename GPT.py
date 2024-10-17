from flask import Flask, request, jsonify, render_template
import openai

app = Flask(__name__)

# OpenAI API 키 설정
openai.api_key = ''  


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    try:
        # ChatCompletion API 호출
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_input}]
        )
        # 응답에서 메시지 내용 추출
        bot_response = response.choices[0].message['content']
        return jsonify({'response': bot_response})  # JSON으로 응답
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # 에러 메시지 반환

if __name__ == '__main__':
    app.run(debug=True)