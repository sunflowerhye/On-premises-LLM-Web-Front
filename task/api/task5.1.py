#이미지 생성 +후처리
from flask import Blueprint, request, jsonify
from common import find_best_match, data
from PIL import Image, ImageEnhance, ImageFilter
import base64
from io import BytesIO
import requests

task6 = Blueprint('task6', __name__)

# 후처리 함수: 이미지 선명도 및 대비 향상
def enhance_image(image_data):
    try:
        # 이미지를 Base64로 디코딩하여 이미지 객체로 변환
        img_data = base64.b64decode(image_data)
        img = Image.open(BytesIO(img_data))

        # 대비 향상 (텍스트를 더 선명하게 하기 위해 대비를 증가시킴)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(0.8)  # 대비를 2배로 증가 (필요에 따라 값 조정)

        # 이미지 선명도 향상 (블러를 제거하여 더 선명하게 만들기)
        img = img.filter(ImageFilter.SHARPEN)

        # 결과 이미지를 저장하거나 Base64로 다시 인코딩
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        enhanced_image_data = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return enhanced_image_data

    except Exception as e:
        print(f"이미지 후처리 오류: {str(e)}")
        return None

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
                
                # 이미지 생성 (예시로 Base64 데이터로 받기)
                image_url = partner_data.get('image_url', None)
                if image_url:
                    # 이미지 다운로드
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        # 이미지를 Base64로 인코딩
                        original_image_data = base64.b64encode(image_response.content).decode('utf-8')
                        # 후처리 적용
                        enhanced_image_data = enhance_image(original_image_data)
                    else:
                        enhanced_image_data = None
                else:
                    enhanced_image_data = None

                # 결과 추가
                results.append({
                    'candidate': candidate,
                    'matched_partner': matched_partner,
                    'match_score': match_score,
                    'related_events': related_events,
                    'past_events': past_events,
                    'enhanced_image': enhanced_image_data
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
