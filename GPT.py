from flask import Flask, request, jsonify, render_template
import openai
import pandas as pd

app = Flask(__name__)

# OpenAI API 키 설정
openai.api_key = ''
# 데이터셋 읽기
data = pd.read_csv('extracted_files/fortune500.csv')  



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']

     # 기업 이름을 찾기 위한 데이터셋에서 확인
    matching_companies = data[data['Name'].str.contains(user_input, case=False, na=False)]  # 사용자 입력에 기업 이름이 포함되어 있는지 확인

    if not matching_companies.empty:
        # 기업 이름이 포함된 경우, 해당 기업의 정보를 가져옴
        company_info = matching_companies.iloc[0]  # 첫 번째 매칭된 기업의 정보를 가져옵니다.
        response_message = f"{company_info['Name']}에 대한 정보입니다: {company_info['Rank']}"  # 필요한 정보를 적절히 선택
    else:
        response_message = "해당 기업을 찾을 수 없습니다."
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