import zipfile
import os
import json

# ZIP 파일 경로와 추출할 디렉토리 설정
zip_file_path = r'C:\Users\qhfma\Downloads\On-premises-LLM-Web-Front-kyeonghwan\dataSet4.zip'  # ZIP 파일 경로
extract_dir = r'C:\Users\qhfma\Downloads\On-premises-LLM-Web-Front-kyeonghwan\output'  # JSON 파일 추출 디렉토리

# ZIP 파일 추출
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)
print("ZIP 파일이 성공적으로 추출되었습니다.")

# 추출된 파일 목록 확인
extracted_files = os.listdir(extract_dir)
print("추출된 파일:", extracted_files)

# JSON 파일 처리
json_data = []
for file in extracted_files:
    if file.endswith('.json'):  # JSON 파일만 처리
        file_path = os.path.join(extract_dir, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)  # JSON 파일 읽기
                json_data.append(data)
                print(f"{file} 파일이 성공적으로 로드되었습니다.")
        except Exception as e:
            print(f"{file} 파일 로드 중 오류 발생: {str(e)}")

# 모든 JSON 데이터를 활용 (예: 병합, 처리 등)
print(f"총 {len(json_data)}개의 JSON 파일이 로드되었습니다.")

# 필요한 경우 JSON 데이터를 병합하여 처리
# 예: 모든 데이터를 병합하여 하나의 리스트로 만들기
merged_data = []
for data in json_data:
    if isinstance(data, list):
        merged_data.extend(data)  # 리스트인 경우 병합
    elif isinstance(data, dict):
        merged_data.append(data)  # 딕셔너리인 경우 추가
