from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_mysql_connector import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import openai
import os

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
        cursor.close()
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
@jwt_required()
def chat():
    data = request.get_json()
    message = data.get('message')
    username = get_jwt_identity()

    if not message:
        return jsonify({"error": "메시지를 입력하세요."}), 400

    # OpenAI API 호출
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  
            prompt=message,
            max_tokens=150
        )
        gpt_response = response.choices[0].text.strip()

        # 검색 기록 저장 (요약된 제목 포함)
        title = message[:30]  # 앞 30자를 제목으로 사용
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO search_history (username, title, query, response) VALUES (%s, %s, %s, %s)", 
                       (username, title, message, gpt_response))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"response": gpt_response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 특정 사용자의 검색 기록을 조회하는 엔드포인트 (제목만 조회)
@app.route('/get_history', methods=['GET'])
@jwt_required()
def get_history():
    username = get_jwt_identity()

    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT id, title FROM search_history WHERE username = %s ORDER BY id DESC", (username,))
    history = cursor.fetchall()
    cursor.close()

    return jsonify(history), 200

    #대화내용 삭제
@app.route('/delete_conversation/<int:history_id>', methods=['DELETE'])
@jwt_required()
def delete_conversation(history_id):
    username = get_jwt_identity()

    # 삭제 처리
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM search_history WHERE id = %s AND username = %s", 
                   (history_id, username))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "대화가 성공적으로 삭제되었습니다."}), 200



# 특정 검색 기록의 상세 대화를 조회하는 엔드포인트
@app.route('/get_conversation/<int:history_id>', methods=['GET'])
@jwt_required()
def get_conversation(history_id):
    username = get_jwt_identity()

    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT query, response FROM search_history WHERE id = %s AND username = %s", (history_id, username))
    conversation = cursor.fetchone()
    cursor.close()

    if conversation:
        return jsonify(conversation), 200
    else:
        return jsonify({"error": "대화를 찾을 수 없습니다."}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
