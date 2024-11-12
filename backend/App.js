import React, { useState } from 'react';
import './App.css';
import Signup from './signup';
import Login from './login';

function App() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [token, setToken] = useState('');

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch("http://54.164.175.7:5000/chat", {  // 최신 IP로 변경
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({ message }),
    });
    

    const data = await res.json();
    setResponse(data.response);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Chat with GPT-4</h1>
        <Signup />
        <Login setToken={setToken} />
        <form onSubmit={handleChatSubmit}>
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
