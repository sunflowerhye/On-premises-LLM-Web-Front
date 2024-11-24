from flask import Blueprint, request, jsonify
from common import call_openai_api, data

task1 = Blueprint('task1', __name__)

# 감성적 홍보 문구 생성
@task1.route('/generate-promo-emotional', methods=['POST'])
def generate_promo_emotional():
    try:
        input_data = request.json
        company_name = input_data.get('companyName', '')
        product_name = input_data.get('productName', '')
        product_info = input_data.get('productInfo', '')
        keywords = input_data.get('keywords', '')
        target_audience = input_data.get('targetAudience', '')

        messages = [
            {"role": "system", "content": "당신은 감성적인 홍보 문구를 작성하는 마케팅 전문가입니다."},
            {"role": "user", "content": (
                f"다음은 제품 정보입니다:\n"
                f"- 회사명: {company_name}\n"
                f"- 제품명: {product_name}\n"
                f"- 제품 설명: {product_info}\n"
                f"- 홍보 키워드: {keywords}\n"
                f"- 타겟 대상: {target_audience}\n\n"
                f"제품의 느낌과 감동을 전하는 감성적인 홍보 문구를 한국어로 자연스럽게 작성해주세요."
            )}
        ]
        promo_text = call_openai_api(messages)
        return jsonify({'promoText': promo_text})
    except Exception as e:
        print(f"Error in /generate-promo-emotional endpoint: {e}")
        return jsonify({'error': f"서버 오류 발생: {e}"}), 500

# 효과 강조 홍보 문구 생성
@task1.route('/generate-promo-effect', methods=['POST'])
def generate_promo_effect():
    try:
        input_data = request.json
        company_name = input_data.get('companyName', '')
        product_name = input_data.get('productName', '')
        product_info = input_data.get('productInfo', '')
        keywords = input_data.get('keywords', '')
        target_audience = input_data.get('targetAudience', '')

        messages = [
            {"role": "system", "content": "당신은 제품의 효과를 강조한 홍보 문구를 작성하는 마케팅 전문가입니다."},
            {"role": "user", "content": (
                f"다음은 제품 정보입니다:\n"
                f"- 회사명: {company_name}\n"
                f"- 제품명: {product_name}\n"
                f"- 제품 설명: {product_info}\n"
                f"- 홍보 키워드: {keywords}\n"
                f"- 타겟 대상: {target_audience}\n\n"
                f"제품의 주요 효과와 뛰어난 특징을 강조하는 홍보 문구를 한국어로 자연스럽게 작성해주세요."
            )}
        ]
        promo_text = call_openai_api(messages)
        return jsonify({'promoText': promo_text})
    except Exception as e:
        print(f"Error in /generate-promo-effect endpoint: {e}")
        return jsonify({'error': f"서버 오류 발생: {e}"}), 500

# 스토리텔링 홍보 문구 생성
@task1.route('/generate-promo-storytelling', methods=['POST'])
def generate_promo_storytelling():
    try:
        input_data = request.json
        company_name = input_data.get('companyName', '')
        product_name = input_data.get('productName', '')
        product_info = input_data.get('productInfo', '')
        keywords = input_data.get('keywords', '')
        target_audience = input_data.get('targetAudience', '')

        messages = [
            {"role": "system", "content": "당신은 스토리텔링 기반의 홍보 문구를 작성하는 마케팅 전문가입니다."},
            {"role": "user", "content": (
                f"다음은 제품 정보입니다:\n"
                f"- 회사명: {company_name}\n"
                f"- 제품명: {product_name}\n"
                f"- 제품 설명: {product_info}\n"
                f"- 홍보 키워드: {keywords}\n"
                f"- 타겟 대상: {target_audience}\n\n"
                f"제품의 스토리를 감성적으로 전달할 수 있는 홍보 문구를 한국어로 자연스럽게 작성해주세요."
            )}
        ]
        promo_text = call_openai_api(messages)
        return jsonify({'promoText': promo_text})
    except Exception as e:
        print(f"Error in /generate-promo-storytelling endpoint: {e}")
        return jsonify({'error': f"서버 오류 발생: {e}"}), 500
