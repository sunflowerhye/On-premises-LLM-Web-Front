import React, { useState } from 'react';
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Flask 서버로 POST 요청 보내기
    const res = await fetch("http://localhost:5000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    const data = await res.json();
    setResponse(data.response); // GPT 응답 설정
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Chat with GPT-4</h1>
        <form onSubmit={handleSubmit}>
          <input 
            type="text" 
            value={message} 
            onChange={(e) => setMessage(e.target.value)} 
            placeholder="Ask me anything" 
          />
          <button type="submit">Send</button>
        </form>
        {response && <p>Response: {response}</p>}
      </header>
    </div>
  );
}

export default App;
