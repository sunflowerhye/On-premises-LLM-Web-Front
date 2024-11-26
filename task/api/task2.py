from flask import Blueprint, request, jsonify
import openai
import base64
import requests
import os

task2 = Blueprint('task2', __name__)

# OpenAI API 키 환경 변수에서 가져오기
openai.api_key = os.getenv('OPENAI_API_KEY')

@task2.route('/generate-image2', methods=['POST'])
def generate_image2():
    try:
        data = request.json
        company_name = data.get('companyName', '').strip()
        product_name = data.get('productName', '').strip()
        product_info = data.get('productInfo', '').strip()
        symbol = data.get('symbol', '').strip()
        color = data.get('color', '').strip()

        # 필수 입력 값 확인
        if not (company_name and product_name and product_info):
            return jsonify({'error': '필수 입력 값(회사명, 제품명, 제품 정보)이 누락되었습니다.'}), 400

        # Prompt 구성
        prompt = (
            f"A luxurious and elegant advertisement banner for the brand '{company_name}'. "
            f"The product being promoted is '{product_name}', known for its feature: '{product_info}'. "
            f"Include the symbol '{symbol}' and use the color '{color}'. "
            f"Design the banner to exude sophistication and premium quality."
        )

        # OpenAI 이미지 생성 요청
        response = openai.Image.create(prompt=prompt, n=1, size="512x512")

        # 이미지 URL 가져오기
        image_url = response['data'][0]['url']
        
        # 이미지 데이터 다운로드
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            # Base64로 인코딩된 이미지 데이터 반환
            image_data = base64.b64encode(image_response.content).decode('utf-8')
            return jsonify({'imageData': image_data, 'imageUrl': image_url})
        else:
            return jsonify({'error': '이미지를 다운로드하는 중 문제가 발생했습니다.'}), 500

    except openai.error.OpenAIError as api_error:
        print(f"OpenAI API Error: {api_error}")
        return jsonify({'error': f"OpenAI API 오류 발생: {str(api_error)}"}), 500
    except requests.exceptions.RequestException as req_error:
        print(f"Image Download Error: {req_error}")
        return jsonify({'error': f"이미지 다운로드 오류 발생: {str(req_error)}"}), 500
    except Exception as e:
        print(f"Error in /generate-image2 endpoint: {e}")
        return jsonify({'error': f"서버 오류 발생: {str(e)}"}), 500
