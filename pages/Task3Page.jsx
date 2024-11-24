import React, { useState } from 'react';
import axios from 'axios';

const Task3Page = () => {
  const [formData, setFormData] = useState({
    goal: '',
    strategy: '',
    targetAudience: '',
    budget: '',
  });

  const [generatedInfo, setGeneratedInfo] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/task3/generate-marketing-plan', formData);
      setGeneratedInfo(response.data.marketingPlan || '기획안 생성 중 오류가 발생했습니다.');
    } catch (error) {
      console.error('Error generating text:', error);
      setGeneratedInfo('문구 생성 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await axios.post(
        'http://localhost:5000/task3/download-marketing-plan',
        formData,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'event_plan.docx');
      document.body.appendChild(link);
      link.click();
    } catch (error) {
      console.error('Error downloading the file:', error);
    }
  };

  return (
    <div className="container">
      <div className="form-container">
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
        <button
          className="generate-button"
          onClick={handleGenerate}
          disabled={loading}
          style={{ marginRight: '1rem' }} 
        >
          {loading ? '생성 중...' : '자동 생성'}
        </button>
        <button
          className="download-button"
          onClick={handleDownload}
          disabled={!generatedInfo}
        >
          파일 다운로드
        </button>
      </div>
      <div className="info-container">
        <h2>생성된 기획안</h2>
        <div className="generated-info">
          <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word', color: '#000', fontSize: '1.2em', textAlign: 'left' }}>
            {generatedInfo || '자동 생성 버튼을 눌러주세요!'}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default Task3Page;
