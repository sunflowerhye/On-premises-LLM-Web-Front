import zipfile
import os
import pandas as pd

# ZIP 파일 경로와 추출할 디렉토리 설정
zip_file_path = r'C:\On-premises-LLM-Web-Front\fortune-500-companies-19552021.zip' 
extract_dir = r'C:\On-premises-LLM-Web-Front\extracted_files'

# ZIP 파일 추출
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

# 추출된 파일 목록 확인
extracted_files = os.listdir(extract_dir)
print("추출된 파일:", extracted_files)

# CSV 파일 경로 설정 
csv_file_path = os.path.join(extract_dir, 'fortune500.csv')

# 데이터셋 읽기
data = pd.read_csv(csv_file_path)

# 데이터 확인
print(data.head())
