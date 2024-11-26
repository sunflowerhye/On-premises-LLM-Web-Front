import React, { useState } from 'react';
import axios from 'axios';

const Task1Page = () => {
  const [formData, setFormData] = useState({
    companyName: '',
    productName: '',
    productInfo: '',
    keywords: '',
    targetAudience: '',
  });

  const [generatedInfo, setGeneratedInfo] = useState('');
  const [loadingButton, setLoadingButton] = useState(''); // 클릭된 버튼 상태 관리

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleGenerate = async (endpoint) => {
    setLoadingButton(endpoint); // 현재 버튼의 상태만 로딩 중으로 설정
    try {
      const response = await axios.post(`http://127.0.0.1:5000/task1/${endpoint}`, formData);
      setGeneratedInfo(response.data.promoText);
    } catch (error) {
      console.error('Error generating text:', error);
      setGeneratedInfo('문구 생성 중 오류가 발생했습니다.');
    } finally {
      setLoadingButton(''); // 로딩 상태 초기화
    }
  };

  return (
    <div className="container">
      <div className="form-container">
        <h2>홍보 문구 생성기</h2>
        {Object.keys(formData).map((key) => (
          <div className="form-group" key={key}>
            <label>
              {key.replace(/([A-Z])/g, ' $1').replace(/^./, (str) => str.toUpperCase())}
            </label>
            <input
              type="text"
              name={key}
              value={formData[key]}
              onChange={handleChange}
              placeholder="입력하세요"
            />
          </div>
        ))}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '1rem' }}>
          <button
            className="generate-button"
            onClick={() => handleGenerate('generate-promo-emotional')}
            disabled={loadingButton === 'generate-promo-emotional'}
          >
            {loadingButton === 'generate-promo-emotional'
              ? '감성적 홍보 생성 중...'
              : '감성적 홍보 생성'}
          </button>
          <button
            className="generate-button"
            onClick={() => handleGenerate('generate-promo-effect')}
            disabled={loadingButton === 'generate-promo-effect'}
          >
            {loadingButton === 'generate-promo-effect'
              ? '효과 강조 홍보 생성 중...'
              : '효과 강조 홍보 생성'}
          </button>
          <button
            className="generate-button"
            onClick={() => handleGenerate('generate-promo-humor')}
            disabled={loadingButton === 'generate-promo-humor'}
          >
            {loadingButton === 'generate-promo-humor'
              ? '유머 홍보 생성 중...'
              : '유머 홍보 생성'}
          </button>
          <button
            className="generate-button"
            onClick={() => handleGenerate('generate-promo-personalized')}
            disabled={loadingButton === 'generate-promo-personalized'}
          >
            {loadingButton === 'generate-promo-personalized'
              ? '맞춤형 홍보 생성 중...'
              : '맞춤형 홍보 생성'}
          </button>
        </div>
      </div>
      <div className="info-container">
        <h2>홍보 문구</h2>
        <div className="generated-info">{generatedInfo || '버튼을 눌러 홍보 문구를 생성하세요!'}</div>
      </div>
    </div>
  );
};

export default Task1Page;
