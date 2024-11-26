#협력업체 행사 진행 이력 검색
from flask import Blueprint, request, jsonify
from common import find_best_match, data

task6 = Blueprint('task6', __name__)

# Task6: 협업 업체 유사 행사 경력 확인
@task6.route('/check-partners', methods=['POST'])
def check_partners():
    try:
        # 입력 데이터
        input_data = request.json
        partner_candidates = input_data.get('candidates', [])  # 후보 업체 리스트
        event_type = input_data.get('eventType', '')  # 원하는 행사 유형

        if not partner_candidates or not event_type:
            return jsonify({'error': '협업 후보 또는 행사 유형이 누락되었습니다.'}), 400

        # 결과 저장
        results = []

        for candidate in partner_candidates:
            # 후보와 유사한 이름 찾기
            matched_partner, match_score = find_best_match(candidate, '업체명')
            if matched_partner:
                # 후보 업체의 과거 행사 데이터 가져오기
                partner_data = data[data['업체명'] == matched_partner].iloc[0]
                past_events = partner_data['행사 이력']  # 예: "뷰티 박람회, 패션쇼, 뷰티 제품 출시회"
                
                # 행사 유형 유사성 확인
                related_events = [event for event in past_events.split(', ') if event_type in event]
                
                # 결과 추가
                results.append({
                    'candidate': candidate,
                    'matched_partner': matched_partner,
                    'match_score': match_score,
                    'related_events': related_events,
                    'past_events': past_events
                })
            else:
                results.append({
                    'candidate': candidate,
                    'error': '해당 업체를 찾을 수 없습니다.'
                })

        return jsonify({'results': results})

    except Exception as e:
        print(f"Error in /check-partners endpoint: {e}")
        return jsonify({'error': f"서버 오류 발생: {e}"}), 500
