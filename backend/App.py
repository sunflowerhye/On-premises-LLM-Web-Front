from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_mysql_connector import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import openai
import os
import uuid  # 고유 conversation_id 생성을 위한 라이브러리
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
jwt = JWTManager(app)


@jwt.unauthorized_loader
def custom_unauthorized_response(err):
    logging.error(f"jwt 인증실패:{err}")
    return jsonify({"error":str(err)}),401

@jwt.invalid_token_loader
def custom_invalid_token_response(err):
    logging.error(f"유표x토큰:{err}")
    return jsonify({"error":set(err)}),401

@jwt.expired_token_loader
def custom_expired_token_response(header,payload):
    logging.error("토큰만료")
    return jsonify({"error":""}),401


# 환경 변수 로드
load_dotenv('secret.env')


# MySQL 설정 (환경 변수에서 불러오기)
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DATABASE'] = os.getenv('MYSQL_DATABASE')

mysql = MySQL(app)

# JWT 설정
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

# OpenAI API 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# CORS 설정
CORS(app, resources={r"/*": {"origins": "*"}})

# 로깅 설정
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')


# 회원가입 엔드포인트
@app.route('/signup', methods=['POST'])
def signup():
    try:
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
            logging.warning("회원가입 실패: 사용자 이름 또는 이메일이 이미 존재합니다.")
            return jsonify({"error": "사용자 이름 또는 이메일이 이미 존재합니다."}), 400

        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, hashed_password, email))
        mysql.connection.commit()
        cursor.close()

        logging.info(f"회원가입 성공: {username}")
        return jsonify({"message": "사용자가 성공적으로 등록되었습니다."}), 201
    except Exception as e:
        logging.error(f"회원가입 중 오류 발생: {e}")
        return jsonify({"error": str(e)}), 500


# 로그인 엔드포인트
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[2], password):  # user[2]는 해싱된 비밀번호

            access_token = create_access_token(identity=username)
            logging.info(f"로그인 성공: {username}")
            return jsonify(access_token=access_token), 200
        else:
            logging.warning("로그인 실패: ID 혹은 비밀번호가 틀렸습니다.")
            return jsonify({"error": "ID 혹은 비밀번호가 틀렸습니다."}), 401
    except Exception as e:
        logging.error(f"로그인 중 오류 발생: {e}")
        return jsonify({"error": str(e)}), 500


# 로그아웃 엔드포인트 (JWT 기반으로 구현 시 클라이언트에서 처리)
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        username = get_jwt_identity()
        logging.info(f"로그아웃 성공: {username}")
        return jsonify({"message": "로그아웃 성공"}), 200
    except Exception as e:
        logging.error(f"로그아웃 중 오류 발생: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    try:
        # JWT에서 사용자 이름 가져오기
        username = get_jwt_identity()
        data = request.get_json()

        # 클라이언트에서 받은 데이터
        title = data.get('title')  # 선택된 대화 제목
        message  = data.get('message')  # 새로 입력한 질문

        # 데이터 검증
        if not title or not message:
            logging.warning("잘못된 요청: 제목 또는 질문이 없음.")
            return jsonify({"error": "제목과 질문을 모두 제공해야 합니다."}), 400

        # 사용자 ID 가져오기
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()

        if user_id is None:
            logging.warning("사용자 조회 실패")
            return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404

        user_id = user_id[0]

        # 제목으로 conversation_id 찾기
        cursor.execute(
            "SELECT conversation_id FROM search_history WHERE user_id = %s AND title = %s",
            (user_id, title)
        )
        conversation = cursor.fetchone()

        if not conversation:
            logging.warning(f"대화 조회 실패: 제목 '{title}'에 해당하는 대화를 찾을 수 없음.")
            return jsonify({"error": "해당 제목에 대한 대화를 찾을 수 없습니다."}), 404

        conversation_id = conversation[0]

        # OpenAI API 호출 (GPT-4 응답 생성)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": message}],
            max_tokens=150
        )
        gpt_response = response['choices'][0]['message']['content'].strip() if response['choices'] else "응답 없음"

        if not gpt_response:
            logging.error("응답 없음")
            return jsonify({"error": "GPT-4 응답 없음"}), 500

        # 기존 대화에 질문과 답변 추가
        cursor.execute(
            """
            UPDATE search_history 
            SET query = CONCAT(query, '\n', %s), response = CONCAT(response, '\n', %s)
            WHERE user_id = %s AND conversation_id = %s
            """,
            (message, gpt_response, user_id, conversation_id)
        )

        # 변경 사항 저장
        mysql.connection.commit()
        cursor.close()

        logging.info(f"대화 업데이트 성공: 사용자 {username}, 제목 '{title}'")

        return jsonify({
            "message": "대화가 성공적으로 업데이트되었습니다.",
            "title": title,
            "new_query": message,
            "response": gpt_response
        }), 200

    except Exception as e:
        logging.error(f"대화 업데이트 중 오류 발생: {e}")
        return jsonify({"error": str(e)}), 500
        

  




#새로운 채팅 개설
@app.route('/new_chat', methods=['POST'])
@jwt_required()
def new_chat():
    try:
       username= get_jwt_identity()
       data = request.get_json()

       cursor = mysql.connection.cursor()
       cursor.execute("SELECT id FROM users WHERE username = %s",(username,))
       user_id=cursor.fetchone()


       if user_id is None:
        logging.warning("실패")
        return jsonify({"error":""}),404

       user_id=user_id[0]

       cursor.execute("SELECT MAX(CAST(SUBSTRING(title, 3) AS UNSIGNED)) FROM search_history WHERE user_id = %s"
,(user_id,))
       count=cursor.fetchone()[0]
       title=f"대화{count+1}"

       conversation_id = str(uuid.uuid4())

       message=data.get('message', '')

       cursor.execute(
            """
           INSERT INTO search_history (user_id, conversation_id, title, query, response)
           VALUES (%s, %s, %s, %s, %s)
            """, (user_id, conversation_id, title, message, "답변")

               )


       mysql.connection.commit()
       cursor.close()


       return jsonify({
           "새로운채팅":"시작",
           "id":conversation_id
           }),200

    except Exception as e:
           logging.error(f"채팅오류: {e}")
           return jsonify({"error": str(e)}),500

# 특정 사용자의 검색 기록을 조회하는 엔드포인트 (제목만 조회)
@app.route('/get_history', methods=['GET'])
@jwt_required()
def get_history():
    try:
        username = get_jwt_identity()

        # 사용자 ID 가져오기
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()

        if user_id is None:
            return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404

        user_id = user_id[0]

        # 검색 기록 조회
        cursor.execute(
            "SELECT id, title FROM search_history WHERE user_id = %s ORDER BY id DESC",
            (user_id,)
        )
        history = cursor.fetchall()
        cursor.close()

        # JSON 형태로 변환
        history_list = [{"id": record[0], "title": record[1]} for record in history]

        logging.info(f"검색 기록 조회 성공: {username}")
        return jsonify(history_list), 200
    except Exception as e:
        logging.error(f"검색 기록 조회 중 오류 발생: {e}")
        return jsonify({"error": str(e)}), 500


# 특정 검색 기록의 상세 대화를 조회하는 엔드포인트
@app.route('/get_conversation/<int:history_id>', methods=['GET'])
@jwt_required()
def get_conversation(history_id):
    try:
        username = get_jwt_identity()

        # 사용자 ID 가져오기
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()

        if user_id is None:
            return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404

        user_id = user_id[0]

        # 대화 내용 조회
        cursor.execute(
            "SELECT query, response FROM search_history WHERE id = %s AND user_id = %s",
            (history_id, user_id)
        )
        conversation = cursor.fetchone()
        cursor.close()

        if conversation:
            logging.info(f"상세 대화 조회 성공: 사용자 {username}, 기록 ID: {history_id}")
            return jsonify({"query": conversation[0], "response": conversation[1]}), 200
        else:
            logging.warning(f"상세 대화 조회 실패: 대화를 찾을 수 없습니다.")
            return jsonify({"error": "대화를 찾을 수 없습니다."}), 404
    except Exception as e:
        logging.error(f"상세 대화 조회 중 오류 발생: {e}")
        return jsonify({"error": str(e)}), 500


# 대화 삭제 엔드포인트
@app.route('/delete_conversation/<int:history_id>', methods=['DELETE'])
@jwt_required()
def delete_conversation(history_id):
    try:
        username = get_jwt_identity()

        # 사용자 ID 가져오기
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()

        if user_id is None:
            return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404

        user_id = user_id[0]

        # 대화 삭제
        cursor.execute("DELETE FROM search_history WHERE id = %s AND user_id = %s", (history_id, user_id))
        mysql.connection.commit()
        cursor.close()

        logging.info(f"대화 삭제 성공: 사용자 {username}, 기록 ID: {history_id}")
        return jsonify({"message": "대화가 성공적으로 삭제되었습니다."}), 200
    except Exception as e:
        logging.error(f"대화 삭제 중 오류 발생: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)                                                                          