# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from flask_mysql_connector import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import openai
import os

# .env 파일 로드
load_dotenv('secret.env')

app = Flask(__name__)

# MySQL 설정 (환경 변수에서 불러오기)
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DATABASE'] = os.getenv('MYSQL_DATABASE')


mysql = MySQL(app)

# JWT 설정
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

@app.route('/')
def index():
    return render_template('index.html')

# OpenAI API 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

CORS(app, resources={r"/*": {"origins": "*"}})

# 회원가입 엔드포인트
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({"error": "모든 필드가 필요합니다."}), 400

    hashed_password = generate_password_hash(password)
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
    if cursor.fetchone():
        return jsonify({"error": "사용자 이름 또는 이메일이 이미 존재합니다."}), 400

    cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, hashed_password, email))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "사용자가 성공적으로 등록되었습니다."}), 201

# 로그인 엔드포인트
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()

    if user and check_password_hash(user[2], password):  # user[2]는 해싱된 비밀번호
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"error": "ID 혹은 비밀번호가 틀렸습니다."}), 401

# 질문을 보내고 GPT-4의 응답을 받는 엔드포인트
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message')
    
    if not message:
        return jsonify({"error": "메시지를 입력하세요."}), 400

    # OpenAI API 호출
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=message,
            max_tokens=150
        )
        gpt_response = response.choices[0].text.strip()
        return jsonify({"response": gpt_response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# MySQL 연결 테스트 엔드포인트
@app.route('/test_db')
def test_db():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT DATABASE();")
        current_db = cursor.fetchone()
        cursor.close()
        return {"status": "success", "connected_db": current_db}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
