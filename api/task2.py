from flask import Blueprint, request, jsonify
import openai
import base64
import requests

task2 = Blueprint('task2', __name__)

#Task2 이미지 생성(미완성)
@task2.route('/generate-image2', methods=['POST'])
def generate_image2():
    try:
        data = request.json
        company_name = data.get('companyName', '')
        product_name = data.get('productName', '')
        product_info = data.get('productInfo', '')
        symbol = data.get('symbol', '')
        color = data.get('color', '')

        if not (company_name and product_name and product_info):
            return jsonify({'error': '필수 입력 값(회사명, 제품명, 제품 정보)이 누락되었습니다.'}), 400

        prompt = (
            f"브랜드 '{company_name}'를 위한 고급 광고 배너를 만드세요. "
            f"홍보 중인 제품은 '{product_name}'이며, '{product_info}'라는 기능으로 유명합니다. "
            f"디자인에는 '{symbol}'을 포함하고, '{color}' 색상을 사용하세요. "
            "우아하고 고급스러운 느낌을 주도록 만드세요."
        )

        response = openai.Image.create(prompt=prompt, n=1, size="512x512")
        image_url = response['data'][0]['url']
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            image_data = base64.b64encode(image_response.content).decode('utf-8')
            return jsonify({'imageData': image_data})
        else:
            return jsonify({'error': '이미지를 다운로드하는 중 문제가 발생했습니다.'}), 500

    except Exception as e:
        print(f"Error in /generate-image2 endpoint: {e}")
        return jsonify({'error': f"서버 오류 발생: {e}"}), 500
