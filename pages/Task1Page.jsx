import React, { useState } from 'react';
import axios from 'axios';
import './Task1Page.css';

const Task1Page = () => {
  const [formData, setFormData] = useState({
    companyName: '',
    productName: '',
    productInfo: '',
    keywords: '',
    targetAudience: '',
  });

  const [generatedInfo, setGeneratedInfo] = useState(''); // 홍보문구 저장
  const [loading, setLoading] = useState(false); // 홍보문구 로딩 상태
  const [imageUrl, setImageUrl] = useState(''); // 생성된 이미지 URL
  const [imageLoading, setImageLoading] = useState(false); // 이미지 로딩 상태

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  // 홍보문구 생성 함수
  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:5000/task1/generate-promo', formData);
      setGeneratedInfo(response.data.promoText);
    } catch (error) {
      console.error('Error generating text:', error);
      setGeneratedInfo('문구 생성 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 홍보문구를 기반으로 이미지 생성 함수 (미완성)
  const handleGenerateImage = async () => {
    setImageLoading(true);
    try {
      if (!generatedInfo) {
        alert('홍보 문구를 먼저 생성해주세요!');
        setImageLoading(false);
        return;
      }

      const response = await axios.post('http://127.0.0.1:5000/task1/generate-image1', {
        promoText: generatedInfo,
      });

      if (response.data.imageData) {
        const imageSrc = `data:image/png;base64,${response.data.imageData}`;
        setImageUrl(imageSrc); // Base64 데이터로 이미지 URL 설정
      } else {
        alert('이미지 생성에 실패했습니다.');
      }
    } catch (error) {
      console.error('Error generating image:', error);
      alert('이미지 생성 중 문제가 발생했습니다.');
    } finally {
      setImageLoading(false);
    }
  };

  // 생성된 이미지를 다운로드 (미완성)
  const handleDownloadImage = () => {
    if (!imageUrl) return;

    const a = document.createElement('a');
    a.href = imageUrl;
    a.download = 'promo_image.png'; // 저장될 파일 이름
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="container">
      <div className="form-container">
        <h2>홍보 문구 생성기</h2>
        {Object.keys(formData).map((key) => (
          <div className="form-group" key={key}>
            <label>{key.replace(/([A-Z])/g, ' $1').replace(/^./, (str) => str.toUpperCase())}</label>
            <input
              type="text"
              name={key}
              value={formData[key]}
              onChange={handleChange}
              placeholder="입력하세요"
            />
          </div>
        ))}
        <button className="generate-button" onClick={handleGenerate} disabled={loading}>
          {loading ? '생성 중...' : '자동 생성'}
        </button>
      </div>
      <div className="info-container">
        <h2>홍보 문구</h2>
        <div className="generated-info">{generatedInfo || '자동 생성 버튼을 눌러주세요!'}</div>
        <button
          className="generate-button"
          onClick={handleGenerateImage}
          disabled={!generatedInfo || imageLoading}
        >
          {imageLoading ? '이미지 생성 중...' : '이미지 생성'}
        </button>
        {imageUrl && (
          <div className="image-container">
            <h3>생성된 이미지</h3>
            <img src={imageUrl} alt="홍보 이미지" style={{ maxWidth: '100%', marginBottom: '10px' }} />
            <button className="download-button" onClick={handleDownloadImage}>
              이미지 다운로드
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Task1Page;
