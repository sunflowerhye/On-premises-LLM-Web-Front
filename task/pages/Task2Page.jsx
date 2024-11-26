import React, { useState } from 'react';
import axios from 'axios';
import './Task1Page.css';

const Task2Page = () => {
  const [formData, setFormData] = useState({
    companyName: '', // 브랜드 이름
    productName: '', // 제품 이름
    productInfo: '', // 제품의 주요 기능 및 효과
    symbol: '', // 제품의 효과를 상징하는 시각적 요소 (ex: 수분을 위한 물방울)
    keywords: '', // 행동 유도 문구
    color: '', // 사용자 지정 색상
  });

  const [imageUrl, setImageUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleGenerateImage = async () => {
    setLoading(true);
    setErrorMessage('');

    try {
      const response = await axios.post('http://localhost:5000/task2/generate-image2', formData);

      if (response.data.imageData) {
        const imageSrc = `data:image/png;base64,${response.data.imageData}`;
        setImageUrl(imageSrc);
      } else {
        setErrorMessage('이미지를 생성할 수 없습니다.');
      }
    } catch (error) {
      console.error('Error generating image:', error);
      setErrorMessage('이미지를 생성하는 중 문제가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!imageUrl) return;

    const a = document.createElement('a');
    a.href = imageUrl;
    a.download = 'generated_image.png'; // 다운로드할 파일 이름
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="container">
      <div className="form-container">
        <h1>광고 이미지 생성</h1>
        <div className="form-group">
          <label>회사명</label>
          <input
            type="text"
            name="companyName"
            value={formData.companyName}
            onChange={handleChange}
            placeholder="회사명을 입력하세요"
          />
        </div>
        <div className="form-group">
          <label>제품명</label>
          <input
            type="text"
            name="productName"
            value={formData.productName}
            onChange={handleChange}
            placeholder="제품명을 입력하세요"
          />
        </div>
        <div className="form-group">
          <label>제품 기능 및 효과</label>
          <input
            type="text"
            name="productInfo"
            value={formData.productInfo}
            onChange={handleChange}
            placeholder="제품의 기능 및 효과를 입력하세요"
          />
        </div>
        <div className="form-group">
          <label>시각적 요소</label>
          <input
            type="text"
            name="symbol"
            value={formData.symbol}
            onChange={handleChange}
            placeholder="시각적 요소(예: 물방울)를 입력하세요"
          />
        </div>
        <div className="form-group">
          <label>키워드</label>
          <input
            type="text"
            name="keywords"
            value={formData.keywords}
            onChange={handleChange}
            placeholder="강조하고 싶은 키워드를 입력하세요"
          />
        </div>
        <div className="form-group">
          <label>색상</label>
          <input
            type="text"
            name="color"
            value={formData.color}
            onChange={handleChange}
            placeholder="원하는 분위기의 색상을 입력하세요"
          />
        </div>

        <button className="generate-button" onClick={handleGenerateImage} disabled={loading}>
          {loading ? '생성 중...' : '이미지 생성'}
        </button>
      </div>

      <div className="info-container">
        <h2>생성된 광고 이미지</h2>
        {errorMessage && <p className="error-message">{errorMessage}</p>}
        {imageUrl ? (
          <div>
            <img src={imageUrl} alt="Generated Advertisement" style={{ maxWidth: '100%', height: 'auto' }} />
            <button className="download-button" onClick={handleDownload}>
              이미지 다운로드
            </button>
          </div>
        ) : (
          <div>이미지 생성 버튼을 눌러주세요!</div>
        )}
      </div>
    </div>
  );
};

export default Task2Page;
