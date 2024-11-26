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
        # background = image.copy()
        # background = background.filter(ImageFilter.GaussianBlur(5))  # 배경 흐림 효과 적용

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

# 제품 종류별 프롬프트 생성 함수
def generate_product_prompt(brand_name, product_name, product_type, primary_color, style):
    prompts = {
        "toner": (
            f"Create a fresh and rejuvenating advertisement for the brand '{brand_name}'. "
            f"The product is a skin toner called '{product_name}', known for its soothing and hydrating effects. "
            f"The design should feature a calming color palette with '{primary_color}' as the base, showcasing clean and fresh skincare vibes. "
            f"Ensure the image feels pure and natural, evoking a sense of balance and harmony in the skin."
        ),
        "lotion": (
            f"Create a luxurious and moisturizing advertisement for the brand '{brand_name}'. "
            f"The product is '{product_name}', a nourishing lotion known for its deep hydration and softening effects. "
            f"The design should incorporate '{primary_color}' to convey a soothing and rich texture. "
            f"Ensure the atmosphere is elegant, luxurious, and emphasizes the comfort and care the lotion provides to the skin."
        ),
        "essence": (
            f"Design an elegant and powerful advertisement for the brand '{brand_name}'. "
            f"The product is '{product_name}', a revitalizing essence known for its skin-strengthening properties. "
            f"The design should highlight luxurious tones, focusing on the transformative power of the essence with '{primary_color}' as the accent color. "
            f"Create an image that communicates glowing, youthful skin and vitality."
        ),
        "sunscreen": (
            f"Create a protective and vibrant advertisement for the brand '{brand_name}'. "
            f"The product is '{product_name}', a high-performance sunscreen known for its powerful protection against UV rays. "
            f"The design should incorporate bright and bold elements, with '{primary_color}' as the dominant color, symbolizing protection and energy. "
            f"Ensure the image feels strong, reliable, and conveys a sense of outdoor adventure and safety."
        ),
        "cleanser": (
            f"Create a refreshing and purifying advertisement for the brand '{brand_name}'. "
            f"The product is '{product_name}', a gentle cleanser that removes impurities and refreshes the skin. "
            f"The design should feature soft, light tones, with '{primary_color}' as a primary accent color, emphasizing cleanliness and clarity. "
            f"Ensure the atmosphere is refreshing, evoking a sense of cleanliness and purity."
        ),
        "emulsion": (
            f"Design a smooth and hydrating advertisement for the brand '{brand_name}'. "
            f"The product is '{product_name}', an emulsion that deeply nourishes and locks in moisture. "
            f"The design should incorporate '{primary_color}' as a subtle yet elegant tone, reflecting the creamy and smooth texture of the product. "
            f"Ensure the image feels soft and moisturizing, focusing on hydration and skin radiance."
        ),
        "mask": (
            f"Create an indulgent and rejuvenating advertisement for the brand '{brand_name}'. "
            f"The product is '{product_name}', a luxurious face mask known for its deep rejuvenation and skin-purifying qualities. "
            f"The design should use calming and rich tones, with '{primary_color}' as a highlight, conveying a spa-like atmosphere. "
            f"Make sure the image communicates relaxation, rejuvenation, and self-care."
        ),
    }

    return prompts.get(product_type, "Invalid product type")

# Task5: 홍보 이미지 생성
@task5.route('/generate-ad-image', methods=['POST'])
def generate_ad_image():
    try:
        # 요청 데이터 추출
        data = request.json
        brand_name = data.get('brandName', '브랜드')
        product_name = data.get('productName', '제품')
        product_features = data.get('productFeatures', '특징 없음')
        primary_color = data.get('color', 'violet')  # 기본 색상
        style = data.get('style', 'modern and elegant')  # 디자인 스타일
        product_type = data.get('productType', 'toner')  # 제품 종류

        # 제품 종류에 맞는 프롬프트 생성
        prompt = generate_product_prompt(brand_name, product_name, product_type, primary_color, style)

        # OpenAI API 요청
        response = openai.Image.create(
            prompt=prompt,
            n=1,  # 생성할 이미지 개수
            size="1024x1024"  # 이미지 크기('256x256', '512x512', '1024x1024', '1024x1792', '1792x1024')
            quality="hd", #("standard","hd")
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
