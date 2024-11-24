from flask import Blueprint, request, jsonify
from common import call_openai_api, data, find_best_match

task1 = Blueprint('task1', __name__)

#Task1 홍보 문구 생성
@task1.route('/generate-promo', methods=['POST'])
def generate_promo():
    try:
        input_data = request.json
        company_name = input_data.get('companyName', '')
        product_name = input_data.get('productName', '')
        product_info = input_data.get('productInfo', '')
        keywords = input_data.get('keywords', '')
        target_audience = input_data.get('targetAudience', '')

        filtered_data = data[data['제품명'].str.contains(product_name, na=False, case=False)]
        dataset_info = "관련 데이터셋 정보를 찾을 수 없습니다."
        if not filtered_data.empty:
            matched_product = filtered_data.iloc[0]
            dataset_info = (
                f"관련 제품 성분 정보: {matched_product['모든성분']}\n"
                f"관련 제품 브랜드: {matched_product['브랜드명']}"
            )

        messages = [
            {"role": "system", "content": "당신은 마케팅 전문가로서 홍보 문구를 작성하는 어시스턴트입니다."},
            {"role": "user", "content": (
                f"다음은 제품 정보입니다:\n"
                f"- 회사명: {company_name}\n"
                f"- 제품명: {product_name}\n"
                f"- 제품 설명: {product_info}\n"
                f"- 홍보 키워드: {keywords}\n"
                f"- 타겟 대상: {target_audience}\n"
                f"{dataset_info}\n"
                f"한국어로 독창적이고 감성적이며 매력적인 광고 문구를 만들어주세요."
            )}
        ]
        promo_text = call_openai_api(messages)
        return jsonify({'promoText': promo_text})

    except Exception as e:
        print(f"Error in /generate-promo endpoint: {e}")
        return jsonify({'error': f"서버 오류 발생: {e}"}), 500


#Task1 홍보 이미지 생성(미완성)