from flask import Blueprint, request, jsonify
from common import call_openai_api

task1 = Blueprint('task1', __name__)

def generate_promo_message(role: str, content: str):
    """OpenAI API 호출을 위한 공통 함수."""
    messages = [
        {"role": "system", "content": role},
        {"role": "user", "content": content}
    ]
    return call_openai_api(messages)

def validate_request_data(data: dict):
    """필수 입력 데이터 검증 함수."""
    required_fields = ['companyName', 'productName', 'productInfo', 'keywords', 'targetAudience']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        raise ValueError(f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}")
    return data

@task1.route('/generate-promo', methods=['POST'])
def generate_promo():
    try:
        input_data = request.json
        validate_request_data(input_data)

        company_name = input_data['companyName']
        product_name = input_data['productName']
        product_info = input_data['productInfo']
        keywords = input_data['keywords']
        target_audience = input_data['targetAudience']
        promo_type = input_data.get('promoType', 'emotional')  # 기본값: 'emotional'

        roles = {
            'emotional': "당신은 감성적인 홍보 문구를 작성하는 마케팅 전문가입니다.",
            'effect': "당신은 제품의 효과를 강조한 홍보 문구를 작성하는 마케팅 전문가입니다.",
            'storytelling': "당신은 스토리텔링 기반의 홍보 문구를 작성하는 마케팅 전문가입니다."
        }
        role = roles.get(promo_type, roles['emotional'])

        content = (
            f"다음은 제품 정보입니다:\n"
            f"- 회사명: {company_name}\n"
            f"- 제품명: {product_name}\n"
            f"- 제품 설명: {product_info}\n"
            f"- 홍보 키워드: {keywords}\n"
            f"- 타겟 대상: {target_audience}\n\n"
            f"제품의 {promo_type} 홍보 문구를 한국어로 자연스럽게 작성해주세요."
        )

        promo_text = generate_promo_message(role, content)
        return jsonify({'promoText': promo_text})

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Error in /generate-promo endpoint: {e}")
        return jsonify({'error': f"서버 오류 발생: {e}"}), 500
