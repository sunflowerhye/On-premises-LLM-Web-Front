from flask import Blueprint, request, jsonify
from common import find_best_match, data, call_openai_api

task2 = Blueprint('task2', __name__)

def parse_file(file_content):
    try:
        # 파일 내용을 라인별로 나누기
        lines = file_content.splitlines()
        print(f"파싱 중인 파일 내용: {lines}")  # 디버깅을 위한 출력
        parsed_data = {}

        for line in lines:
            # ':'를 기준으로 제품명과 성분을 분리
            if ':' in line:
                product_name, ingredients = line.split(":", 1)
                ingredients_list = [ingredient.strip() for ingredient in ingredients.split(',')]  # 성분 분리
                parsed_data[product_name.strip()] = ingredients_list
            else:
                print(f"형식 오류: '{line}' 라인에서 ':' 구분자가 없습니다.")
                
        print(f"파싱된 데이터: {parsed_data}")  # 파싱 결과를 출력
        return parsed_data
    except Exception as e:
        print(f"파일 파싱 중 오류: {e}")
        return None


# Task2: 성분 비교
# @task2.route('/compare', methods=['POST'])
# def compare():
#     try:
#         product1_name = request.json.get('product1', '')
#         product2_name = request.json.get('product2', '')
#         file_content = request.json.get('fileContent', '')  # 파일 내용이 있다면 받기

#         # 파일 내용이 있으면 파싱하여 데이터에 반영
#         if file_content:
#             parsed_data = parse_file(file_content)
#             if parsed_data:
#                 # 파일에서 제공된 데이터를 사용하여 성분 비교를 진행
#                 product1_name = parsed_data.get('product1', product1_name)
#                 product2_name = parsed_data.get('product2', product2_name)

#         # 제품명으로 매칭
#         product1_match, product1_score = find_best_match(product1_name, '제품명')
#         product2_match, product2_score = find_best_match(product2_name, '제품명')

#         if not product1_match or not product2_match:
#             return jsonify({'error': '입력된 제품명을 찾을 수 없습니다.'}), 404

#         # 매칭된 데이터 가져오기
#         product1_data = data[data['제품명'] == product1_match].iloc[0]
#         product2_data = data[data['제품명'] == product2_match].iloc[0]

#         # 성분 데이터 정리
#         ingredients1 = set(product1_data['모든성분'].split(','))
#         ingredients2 = set(product2_data['모든성분'].split(','))

#         # 비교 결과 생성
#         comparison = {
#             'common_ingredients': list(ingredients1 & ingredients2),
#             'unique_to_product1': list(ingredients1 - ingredients2),
#             'unique_to_product2': list(ingredients2 - ingredients1)
#         }

#         return jsonify({
#             'product1': {
#                 'name': product1_match,
#                 'score': product1_score,
#                 'ingredients': list(ingredients1)
#             },
#             'product2': {
#                 'name': product2_match,
#                 'score': product2_score,
#                 'ingredients': list(ingredients2)
#             },
#             'comparison': comparison
#         })

#     except Exception as e:
#         print(f"Error in /compare endpoint: {e}")
#         return jsonify({'error': f"서버 오류 발생: {e}"}), 500

@task2.route('/compare', methods=['POST'])
def compare():
    try:
        product1_name = request.json.get('product1', '').strip().lower()
        product2_name = request.json.get('product2', '').strip().lower()
        file_content = request.json.get('fileContent', '')  # 파일 내용이 있다면 받기

        # 파일 내용이 있으면 파싱하여 데이터에 반영
        if file_content:
            parsed_data = parse_file(file_content)
            if parsed_data:
                # 파일에서 제공된 데이터를 사용하여 성분 비교를 진행
                product1_name = parsed_data.get(product1_name, product1_name)
                product2_name = parsed_data.get(product2_name, product2_name)

        # 제품명으로 매칭
        product1_match, product1_score = find_best_match(product1_name, '제품명')
        product2_match, product2_score = find_best_match(product2_name, '제품명')

        if not product1_match or not product2_match:
            return jsonify({'error': '입력된 제품명을 찾을 수 없습니다.'}), 404

        # 매칭된 데이터 가져오기
        product1_data = data[data['제품명'] == product1_match].iloc[0]
        product2_data = data[data['제품명'] == product2_match].iloc[0]

        # 성분 데이터 정리 (소문자 및 공백 제거)
        ingredients1 = set(ingredient.strip().lower() for ingredient in product1_data['모든성분'].split(','))
        ingredients2 = set(ingredient.strip().lower() for ingredient in product2_data['모든성분'].split(','))

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


# Task2: 성분 설명
@task2.route('/explain', methods=['POST'])
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
    
    
