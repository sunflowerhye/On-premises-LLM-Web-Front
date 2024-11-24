import React, { useState } from 'react';
import axios from 'axios';
import './Task1Page.css';

function Task4Page() {
    const [formData, setFormData] = useState({
        product1: '',
        product2: '',
    });
    const [comparisonData, setComparisonData] = useState(null);
    const [ingredientInfo, setIngredientInfo] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({
            ...formData,
            [name]: value,
        });
    };

    const handleCompare = async () => {
        setLoading(true);
        setError('');
        setComparisonData(null);
        setIngredientInfo('');

        try {
            const compareResponse = await axios.post('http://127.0.0.1:5000/task4/compare', formData);
            setComparisonData(compareResponse.data);

            const commonIngredients = compareResponse.data.comparison.common_ingredients;

            // 공통 성분에 대한 추가 설명 요청
            if (!commonIngredients || commonIngredients.length === 0) {
                setIngredientInfo('공통 성분이 없어 추가 설명이 없습니다.');
            } else {
                try {
                    const explanation = await axios.post('http://127.0.0.1:5000/task4/explain', {
                        ingredients: commonIngredients,
                    });
                    setIngredientInfo(explanation.data.explanation || '설명이 제공되지 않았습니다.');
                } catch (explainError) {
                    console.error("OpenAPI 호출 실패:", explainError);
                    setIngredientInfo('OpenAPI 호출 중 문제가 발생했습니다. 서버 로그를 확인하세요.');
                }
            }
        } catch (compareError) {
            console.error("Compare API 호출 실패:", compareError);
            setError('제품 비교 중 문제가 발생했습니다. 입력값을 확인하세요.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <div className="form-container">
                <h2>화장품 성분 비교</h2>
                {Object.keys(formData).map((key) => (
                    <div className="form-group" key={key}>
                        <label>{key === 'product1' ? '첫 번째 제품명' : '두 번째 제품명'}</label>
                        <input
                            type="text"
                            name={key}
                            value={formData[key]}
                            onChange={handleChange}
                            placeholder="제품명을 입력하세요"
                        />
                    </div>
                ))}
                <button
                    className="generate-button"
                    onClick={handleCompare}
                    disabled={loading}
                >
                    {loading ? '비교 중...' : '비교하기'}
                </button>
            </div>

            <div className="info-container">
                <h2>비교 결과</h2>
                {error && <p className="error-message">{error}</p>}
                {comparisonData ? (
                    <table className="comparison-table">
                        <thead>
                            <tr>
                                <th>항목</th>
                                <th>{comparisonData.product1.name}</th>
                                <th>{comparisonData.product2.name}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>유사도 점수</td>
                                <td>{comparisonData.product1.score}</td>
                                <td>{comparisonData.product2.score}</td>
                            </tr>
                            <tr>
                                <td>공통 성분</td>
                                <td colSpan="2">
                                    {comparisonData.comparison.common_ingredients.join(', ') || '없음'}
                                </td>
                            </tr>
                            <tr>
                                <td>고유 성분</td>
                                <td>{comparisonData.comparison.unique_to_product1.join(', ') || '없음'}</td>
                                <td>{comparisonData.comparison.unique_to_product2.join(', ') || '없음'}</td>
                            </tr>
                        </tbody>
                    </table>
                ) : (
                    <p className="generated-info">비교 결과가 여기에 표시됩니다.</p>
                )}
                {ingredientInfo && (
                    <div className="ingredient-info">
                        <h3>주요 성분 설명</h3>
                        <p>{ingredientInfo}</p>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Task4Page;
