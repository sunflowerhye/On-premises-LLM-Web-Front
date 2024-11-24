from flask import Blueprint, request, jsonify
from common import find_best_match, data, call_openai_api

task4 = Blueprint('task4', __name__)

# Task4: 성분 비교
@task4.route('/compare', methods=['POST'])
def compare():
    try:
        product1_name = request.json.get('product1', '')
        product2_name = request.json.get('product2', '')

        # 제품명으로 매칭
        product1_match, product1_score = find_best_match(product1_name, '제품명')
        product2_match, product2_score = find_best_match(product2_name, '제품명')

        if not product1_match or not product2_match:
            return jsonify({'error': '입력된 제품명을 찾을 수 없습니다.'}), 404

        # 매칭된 데이터 가져오기
        product1_data = data[data['제품명'] == product1_match].iloc[0]
        product2_data = data[data['제품명'] == product2_match].iloc[0]

        # 성분 데이터 정리
        ingredients1 = set(product1_data['모든성분'].split(','))
        ingredients2 = set(product2_data['모든성분'].split(','))

        # 비교 결과 생성
        comparison = {
            'common_ingredients': list(ingredients1 & ingredients2),
            'unique_to_product1': list(ingredients1 - ingredients2),
            'unique_to_product2': list(ingredients2 - ingredients1)
        }

        return jsonify({
            'product1': {
                'name': product1_match,
                'score': product1_score,
                'ingredients': list(ingredients1)
            },
            'product2': {
                'name': product2_match,
                'score': product2_score,
                'ingredients': list(ingredients2)
            },
            'comparison': comparison
        })

    except Exception as e:
        print(f"Error in /compare endpoint: {e}")
        return jsonify({'error': f"서버 오류 발생: {e}"}), 500

# Task4: 성분 설명
@task4.route('/explain', methods=['POST'])
def explain():
    try:
        ingredients = request.json.get('ingredients', [])
        if not ingredients:
            return jsonify({'explanation': '성분 데이터가 없습니다.'}), 400

        # OpenAI API를 사용하여 설명 생성
        messages = [{"role": "system", "content": "당신은 한국어로 성분 정보를 설명하는 어시스턴트입니다."}]
        for ingredient in ingredients:
            messages.append({"role": "user", "content": f"{ingredient} 성분은 스킨케어에서 어떤 효과가 있나요?"})

        explanation = call_openai_api(messages)
        return jsonify({'explanation': explanation})

    except Exception as e:
        print(f"Error in /explain endpoint: {e}")
        return jsonify({'error': f"서버 오류 발생: {e}"}), 500
    