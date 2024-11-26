from flask import Blueprint, request, jsonify
import openai
import requests
import base64

task5 = Blueprint('task5', __name__)

# Task5: 홍보 이미지 생성
@task5.route('/generate-ad-image', methods=['POST'])
def generate_ad_image():
    try:
        # 요청 데이터 추출
        data = request.json
        brand_name = data.get('brandName', '브랜드')
        product_name = data.get('productName', '제품')
        product_features = data.get('productFeatures', '특징 없음')
        primary_color = data.get('color', 'blue')  # 기본 색상
        style = data.get('style', 'modern and elegant')  # 디자인 스타일

        # OpenAI DALL·E 프롬프트 생성
        prompt = (
            f"Create a visually stunning advertisement for the brand '{brand_name}'. "
            f"The product is '{product_name}', which is known for '{product_features}'. "
            f"The design should feature the primary color '{primary_color}' and have a '{style}' look. "
            f"Ensure the image feels luxurious and grabs attention."
        )

        # OpenAI API 요청
        response = openai.Image.create(
            prompt=prompt,
            n=1,  # 생성할 이미지 개수
            size="512x512"  # 이미지 크기
        )

        # 생성된 이미지 URL 가져오기
        image_url = response['data'][0]['url']

        # 이미지 다운로드 및 Base64 인코딩
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            image_data = base64.b64encode(image_response.content).decode('utf-8')
            return jsonify({'image': image_data})
        else:
            return jsonify({'error': '이미지 다운로드 실패'}), 500

    except Exception as e:
        print(f"Error in /generate-ad-image endpoint: {e}")
        return jsonify({'error': f"서버 오류 발생: {str(e)}"}), 500
