#이미지 생성 +후처리
from flask import Blueprint, request, jsonify
import openai
import requests
import base64
from PIL import Image, ImageEnhance, ImageFilter
import io

task5 = Blueprint('task5', __name__)

# 이미지 후처리 함수
def post_process_image(image_data):
    try:
        # 이미지를 바이너리로 변환
        image = Image.open(io.BytesIO(image_data))

        # 선명도 향상 (Sharpening)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)  # 선명도를 두 배 증가시킴

        # 배경 흐림 처리 (Gaussian Blur)
        background = image.copy()
        background = background.filter(ImageFilter.GaussianBlur(5))  # 배경 흐림 효과 적용

        # 대비 조정 (Contrast Enhancement)
        enhancer_contrast = ImageEnhance.Contrast(image)
        image = enhancer_contrast.enhance(0.8)  # 대비를 0.8배로 감소시킴

        # 후처리된 이미지를 메모리에 저장
        output_image = io.BytesIO()
        image.save(output_image, format="PNG")
        output_image.seek(0)

        return output_image
    except Exception as e:
        print(f"Error in image post-processing: {e}")
        return None

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

        # 이미지 다운로드
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            # 후처리 함수 호출
            processed_image = post_process_image(image_response.content)
            if processed_image:
                # 후처리된 이미지를 Base64로 인코딩
                image_data = base64.b64encode(processed_image.read()).decode('utf-8')
                return jsonify({'image': image_data})
            else:
                return jsonify({'error': '이미지 후처리 실패'}), 500
        else:
            return jsonify({'error': '이미지 다운로드 실패'}), 500

    except Exception as e:
        print(f"Error in /generate-ad-image endpoint: {e}")
        return jsonify({'error': f"서버 오류 발생: {str(e)}"}), 500
