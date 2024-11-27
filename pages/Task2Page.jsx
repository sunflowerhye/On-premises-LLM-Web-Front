import React, { useState } from 'react';
import axios from 'axios';
import './Task1Page.css'; // 기존 스타일 유지

const Task2Page = () => {
  const [formData, setFormData] = useState({
    goal: '', // 목적
    targetAudience: '', // 타겟층
    spaceAndBudget: '', // 공간과 예산
    customerInterest: '', // 주요 고객 관심사
    theme: '', // 이벤트 주제
  });

  const [generatedPlan, setGeneratedPlan] = useState('');
  const [loadingIndoor, setLoadingIndoor] = useState(false); // 실내 기획 로딩 상태
  const [loadingOutdoor, setLoadingOutdoor] = useState(false); // 실외 기획 로딩 상태
  const [loadingTimetable, setLoadingTimetable] = useState(false); // 타임테이블 로딩 상태
  const [showTimetableButton, setShowTimetableButton] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleGenerateIndoorPlan = async () => {
    setLoadingIndoor(true);
    try {
      const response = await axios.post('http://localhost:5000/task2/generate-indoor-event-plan', {
        ...formData,
        environment: '실내', // 환경 설정
      });
      setGeneratedPlan(response.data.eventPlan || '기획 생성 중 오류가 발생했습니다.');
      setShowTimetableButton(true);
    } catch (error) {
      console.error('Error generating indoor event plan:', error);
      setGeneratedPlan('기획 생성 중 오류가 발생했습니다.');
    } finally {
      setLoadingIndoor(false);
    }
  };

  const handleGenerateOutdoorPlan = async () => {
    setLoadingOutdoor(true);
    try {
      const response = await axios.post('http://localhost:5000/task2/generate-outdoor-event-plan', {
        ...formData,
        environment: '실외', // 환경 설정
      });
      setGeneratedPlan(response.data.eventPlan || '기획 생성 중 오류가 발생했습니다.');
      setShowTimetableButton(true);
    } catch (error) {
      console.error('Error generating outdoor event plan:', error);
      setGeneratedPlan('기획 생성 중 오류가 발생했습니다.');
    } finally {
      setLoadingOutdoor(false);
    }
  };

  const handleDownloadTimetable = async () => {
    setLoadingTimetable(true);
    try {
      const response = await axios.post(
        'http://localhost:5000/task2/download-timetable',
        formData,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'event_timetable.docx');
      document.body.appendChild(link);
      link.click();
    } catch (error) {
      console.error('Error downloading timetable:', error);
    } finally {
      setLoadingTimetable(false);
    }
  };

  return (
    <div className="container">
      <div className="form-container">
        <h1>부스/이벤트 기획</h1>
        {Object.keys(formData).map((key) => (
          <div className="form-group" key={key}>
            <label>
              {{
                goal: 'Goal',
                targetAudience: 'Target Audience',
                spaceAndBudget: 'Space and Budget',
                customerInterest: 'Customer Interest',
                theme: 'Event Theme',
              }[key]}
            </label>
            <input
              type="text"
              name={key}
              value={formData[key]}
              onChange={handleChange}
              placeholder={{
                goal: '이벤트의 목적을 입력하세요.',
                targetAudience: '이벤트 대상을 입력하세요.',
                spaceAndBudget: '예: 10평, 200만 원',
                customerInterest: '예: 친환경 제품, SNS 활동',
                theme: '예: 자연 친화적인 라이프스타일',
              }[key]}
            />
          </div>
        ))}
        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', justifyContent: 'center' }}>
          <button
            className="generate-button"
            onClick={handleGenerateIndoorPlan}
            disabled={loadingIndoor || loadingOutdoor}
          >
            {loadingIndoor ? '실내 기획 생성 중...' : '실내 기획 생성'}
          </button>
          <button
            className="generate-button"
            onClick={handleGenerateOutdoorPlan}
            disabled={loadingIndoor || loadingOutdoor}
          >
            {loadingOutdoor ? '실외 기획 생성 중...' : '실외 기획 생성'}
          </button>
        </div>
        {showTimetableButton && (
          <div style={{ marginTop: '1rem', textAlign: 'center' }}>
            <button
              className="generate-button"
              onClick={handleDownloadTimetable}
              disabled={loadingTimetable}
            >
              {loadingTimetable ? '타임 테이블 생성 중...' : '타임 테이블 다운로드'}
            </button>
          </div>
        )}
      </div>

      <div className="info-container">
        <h2>부스/이벤트 기획</h2>
        <div
          className="generated-info"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: generatedPlan ? 'auto' : '200px',
            border: '1px dashed #ccc', 
            borderRadius: '0', 
            padding: '1rem',
            backgroundColor: '#f9f9f9',
            fontSize: '1.2em',
          }}
        >
          <pre
            style={{
              whiteSpace: 'pre-wrap',
              wordWrap: 'break-word',
              fontSize: '1em',
              textAlign: generatedPlan ? 'left' : 'center',
            }}
          >
            {generatedPlan || '기획 생성 버튼을 눌러주세요!'}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default Task2Page;
