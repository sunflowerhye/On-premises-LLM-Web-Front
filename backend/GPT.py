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

    # 데이터셋에서 기업 이름 찾기
    matching_companies = data[data['Name'].str.contains(user_input, case=False, na=False)]

    if not matching_companies.empty:
        # 기업 이름이 포함된 경우 데이터셋 정보를 반환
        company_info = matching_companies.iloc[0]
        response_message = f"{company_info['Name']}에 대한 정보입니다: {company_info['Rank']}위에 위치해 있습니다."
        return jsonify({'response': response_message})  # 데이터셋 정보를 반환
    else:
        try:
            # ChatCompletion API 호출
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": user_input}]
            )
            bot_response = response.choices[0].message['content']
            return jsonify({'response': bot_response})
        except Exception as e:
            return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)