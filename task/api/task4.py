from flask import Blueprint, request, jsonify
from common import find_best_match, data, call_openai_api

task4 = Blueprint('task4', __name__)

# Task4: 성분 비교
@task4.route('/compare', methods=['POST'])
def compare():
    try:
        # 입력된 제품명
        product1_name = request.json.get('product1', '').strip().lower()
        product2_name = request.json.get('product2', '').strip().lower()

        # 제품명 매칭
        product1_match, product1_score = find_best_match(product1_name, '제품명')
        product2_match, product2_score = find_best_match(product2_name, '제품명')

        if not product1_match:
            return jsonify({'error': f"'{product1_name}' 제품을 찾을 수 없습니다."}), 404
        if not product2_match:
            return jsonify({'error': f"'{product2_name}' 제품을 찾을 수 없습니다."}), 404

        # 매칭된 제품 데이터 가져오기
        product1_data = data[data['제품명'].str.lower() == product1_match.lower()].iloc[0]
        product2_data = data[data['제품명'].str.lower() == product2_match.lower()].iloc[0]

        # 성분 리스트 정리 (소문자 변환 및 공백 제거)
        ingredients1 = set(map(str.strip, map(str.lower, product1_data['모든성분'].split(','))))
        ingredients2 = set(map(str.strip, map(str.lower, product2_data['모든성분'].split(','))))

        # 비교 결과 생성
        comparison = {
            'common_ingredients': sorted(ingredients1 & ingredients2),
            'unique_to_product1': sorted(ingredients1 - ingredients2),
            'unique_to_product2': sorted(ingredients2 - ingredients1)
        }

        # JSON 응답
        return jsonify({
            'product1': {
                'name': product1_data['제품명'],
                'score': product1_score,
                'ingredients': sorted(ingredients1)
            },
            'product2': {
                'name': product2_data['제품명'],
                'score': product2_score,
                'ingredients': sorted(ingredients2)
            },
            'comparison': comparison
        })

    except Exception as e:
        print(f"Error in /compare endpoint: {e}")
        return jsonify({'error': f"서버 오류 발생: {str(e)}"}), 500


# Task4: 성분 설명
@task4.route('/explain', methods=['POST'])
def explain():
    try:
        # 입력된 성분 리스트
        ingredients = request.json.get('ingredients', [])
        if not ingredients:
            return jsonify({'error': '성분 데이터가 없습니다.'}), 400

        # OpenAI API 요청을 위한 메시지 구성
        messages = [{"role": "system", "content": "당신은 한국어로 성분 정보를 설명하는 어시스턴트입니다."}]
        for ingredient in ingredients:
            messages.append({"role": "user", "content": f"{ingredient} 성분은 스킨케어에서 어떤 효과가 있나요?"})

        # OpenAI API 호출
        explanation = call_openai_api(messages)
        if not explanation:
            return jsonify({'error': 'OpenAI API로부터 응답을 받을 수 없습니다.'}), 500

        # 결과 반환
        return jsonify({'explanation': explanation})

    except Exception as e:
        print(f"Error in /explain endpoint: {e}")
        return jsonify({'error': f"서버 오류 발생: {str(e)}"}), 500
