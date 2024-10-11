import openai
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# OpenAI API 키 설정
openai.api_key = " "

@app.route('/')
def index():
    return render_template('index.html')  # HTML 파일을 렌더링

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')  # 웹에서 받은 질문

    
    response = openai.Completion.create(
        model=" ",  # gpt-4?
        prompt=user_message,
        max_tokens=100,
        temperature=0.7
    )

    gpt_response = response['choices'][0]['text']
    return jsonify({'response': gpt_response.strip()})

if __name__ == '__main__':
    app.run(debug=True)
