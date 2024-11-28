import React, { useState } from 'react';
import axios from 'axios';
import { saveAs } from 'file-saver';
import { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType } from 'docx';
import './Task1Page.css';

function Task2Page() {
    const [formData, setFormData] = useState({ product1: '', product2: '' });
    const [comparisonData, setComparisonData] = useState(null);
    const [ingredientInfo, setIngredientInfo] = useState('');
    const [fileContent, setFileContent] = useState('');
    const [fileName, setFileName] = useState('');

    const [loading, setLoading] = useState(false);
    const [dragging, setDragging] = useState(false);
    const [error, setError] = useState('');

    const handleFileUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                setFileContent(event.target.result);
                setFileName(file.name);
            };
            reader.readAsText(file);
        }
    };

    const handleFileRemove = () => {
        setFileContent('');
        setFileName('');
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragging(false);
        const file = e.dataTransfer.files[0];
        if (file) {
            handleFileUpload({ target: { files: [file] } });
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setDragging(true);
    };

    const handleDragLeave = () => {
        setDragging(false);
    };

    const handleCompare = async () => {
        setLoading(true);
        setError('');
        setComparisonData(null);
        setIngredientInfo('');
        try {
            const response = await axios.post('http://127.0.0.1:5000/task2/compare', {
                product1: formData.product1,
                product2: formData.product2,
                fileContent,
            });
            setComparisonData(response.data);

            if (response.data.comparison.common_ingredients.length > 0) {
                const explainResponse = await axios.post('http://127.0.0.1:5000/task2/explain', {
                    ingredients: response.data.comparison.common_ingredients,
                });
                setIngredientInfo(explainResponse.data.explanation);
            } else {
                setIngredientInfo('공통 성분이 없습니다.');
            }
        } catch (err) {
            setError(err.response?.data?.error || '비교 중 문제가 발생했습니다.');
        } finally {
            setLoading(false);
        }
    };

    const roundToFirstDecimal = (value) => {
        return Math.round(value * 10) / 10;
    };

    const handleDownload = async () => {
        if (!comparisonData) return;
    
        const table = new Table({
            rows: [
                new TableRow({
                    children: [
                        new TableCell({
                            children: [
                                new Paragraph({
                                    text: "제품명",
                                    alignment: AlignmentType.CENTER,
                                }),
                            ],
                            width: { size: 20, type: WidthType.PERCENTAGE },
                        }),
                        new TableCell({
                            children: [
                                new Paragraph({
                                    text: comparisonData.product1.name,
                                    alignment: AlignmentType.CENTER,
                                }),
                            ],
                            width: { size: 40, type: WidthType.PERCENTAGE },
                        }),
                        new TableCell({
                            children: [
                                new Paragraph({
                                    text: comparisonData.product2.name,
                                    alignment: AlignmentType.CENTER,
                                }),
                            ],
                            width: { size: 40, type: WidthType.PERCENTAGE },
                        }),
                    ],
                }),
                new TableRow({
                    children: [
                        new TableCell({
                            children: [
                                new Paragraph({
                                    text: "유사도 점수",
                                    alignment: AlignmentType.CENTER,
                                }),
                            ],
                        }),
                        new TableCell({
                            children: [
                                new Paragraph({
                                    text: roundToFirstDecimal(comparisonData.product1.score).toString(),
                                    alignment: AlignmentType.CENTER,
                                }),
                            ],
                        }),
                        new TableCell({
                            children: [
                                new Paragraph({
                                    text: roundToFirstDecimal(comparisonData.product2.score).toString(),
                                    alignment: AlignmentType.CENTER,
                                }),
                            ],
                        }),
                    ],
                }),
                new TableRow({
                    children: [
                        new TableCell({
                            children: [
                                new Paragraph({
                                    text: "공통 성분",
                                    alignment: AlignmentType.CENTER,
                                }),
                            ],
                        }),
                        new TableCell({
                            children: [
                                new Paragraph({
                                    text: comparisonData.comparison.common_ingredients.join(', ') || '없음',
                                    alignment: AlignmentType.CENTER,
                                }),
                            ],
                            columnSpan: 2,
                        }),
                    ],
                }),
                new TableRow({
                    children: [
                        new TableCell({
                            children: [
                                new Paragraph({
                                    text: "고유 성분",
                                    alignment: AlignmentType.CENTER,
                                }),
                            ],
                        }),
                        new TableCell({
                            children: [
                                new Paragraph({
                                    text: comparisonData.comparison.unique_to_product1.join(', ') || '없음',
                                    alignment: AlignmentType.CENTER,
                                }),
                            ],
                        }),
                        new TableCell({
                            children: [
                                new Paragraph({
                                    text: comparisonData.comparison.unique_to_product2.join(', ') || '없음',
                                    alignment: AlignmentType.CENTER,
                                }),
                            ],
                        }),
                    ],
                }),
            ],
        });
    
        const explanationHeading = new Paragraph({
            children: [new TextRun("주요 성분 설명")],
            heading: "Heading2",
            spacing: { before: 400, after: 200 },
        });
    
        const explanationParagraph = new Paragraph({
            text: ingredientInfo || "주요 성분 설명이 없습니다.",
            spacing: { before: 400, after: 400 },
        });
    
        const doc = new Document({
            sections: [
                {
                    children: [
                        new Paragraph({
                            children: [new TextRun("성분 비교 결과")],
                            heading: "Heading1",
                        }),
                        table,
                        explanationHeading,
                        explanationParagraph,
                    ],
                },
            ],
        });
    
        const blob = await Packer.toBlob(doc);
        saveAs(blob, '성분비교결과.docx');
    };
    

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    return (
        <div className="container">
            <div className="form-container">
                <h2>화장품 성분 비교</h2>
                <div className="form-group">
                    <label>첫 번째 제품명</label>
                    <input
                        type="text"
                        name="product1"
                        value={formData.product1}
                        onChange={handleChange}
                        placeholder="제품명을 입력하세요"
                    />
                </div>
                <div className="form-group">
                    <label>두 번째 제품명</label>
                    <input
                        type="text"
                        name="product2"
                        value={formData.product2}
                        onChange={handleChange}
                        placeholder="제품명을 입력하세요"
                    />
                </div>
                <div className="form-group">
                    <label>파일 첨부</label>
                    <div
                        onDrop={handleDrop}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        style={{
                            border: dragging ? '2px dashed #4caf50' : '2px dashed #ccc',
                            padding: '20px',
                            textAlign: 'center',
                            marginBottom: '20px',
                            backgroundColor: dragging ? '#f9fff9' : '#fff',
                        }}
                    >
                        {fileContent ? (
                            <div>
                                <p>
                                    <strong>업로드된 파일:</strong> {fileName}
                                </p>
                                <button onClick={handleFileRemove}>파일 삭제</button>
                            </div>
                        ) : (
                            '여기로 파일을 드래그하거나 업로드 버튼을 사용하세요.'
                        )}
                    </div>
                    <div style={{ textAlign: 'center', marginTop: '10px' }}>
                        <label htmlFor="fileUpload" style={{ cursor: 'pointer', color: '#007BFF' }}>
                            파일 업로드 클릭
                        </label>
                        <input
                            id="fileUpload"
                            type="file"
                            accept=".txt,.csv,.json"
                            onChange={handleFileUpload}
                            style={{ display: 'none' }}
                        />
                    </div>
                </div>
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
                                <th>제품명</th>
                                <th>{comparisonData.product1.name}</th>
                                <th>{comparisonData.product2.name}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>유사도 점수</td>
                                <td>{roundToFirstDecimal(comparisonData.product1.score)}</td>
                                <td>{roundToFirstDecimal(comparisonData.product2.score)}</td>
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
                    <div>
                        <h3>주요 성분 설명</h3>
                        <p>{ingredientInfo}</p>
                    </div>
                )}
                <button
                    className="download-button"
                    onClick={handleDownload}
                    disabled={!comparisonData}
                >
                    결과 다운로드
                </button>
            </div>
        </div>
    );
}

export default Task2Page;
