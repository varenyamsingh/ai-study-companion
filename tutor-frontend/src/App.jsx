import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    { text: "Hello! I'm your Smart Tutor. How can I help you with your notes today?", sender: 'tutor' }
  ]);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  // Auto-scroll to bottom of chat
  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleAction = async (userMessage) => {
    if (!userMessage.trim()) return;
    
    setMessages(prev => [...prev, { text: userMessage, sender: 'user' }]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:8000/chat', { message: userMessage });
      setMessages(prev => [...prev, { text: response.data.reply, sender: 'tutor' }]);
    } catch (error) {
      setMessages(prev => [...prev, { text: "⚠️ Error connecting to backend. Is uvicorn running?", sender: 'tutor' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🎓 Smart Tutor AI</h1>
        <button className="quiz-btn" onClick={() => handleAction('quiz')}>📝 Take Quiz</button>
      </header>

      <div className="chat-window">
        {messages.map((msg, i) => (
          <div key={i} className={`message-bubble ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
        {loading && <div className="message-bubble tutor">Thinking...</div>}
        <div ref={chatEndRef} />
      </div>

      <div className="input-area">
        <input 
          value={input} 
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleAction(input)}
          placeholder="Ask a question about your PDF..."
        />
        <button onClick={() => handleAction(input)} disabled={loading}>Send</button>
      </div>
    </div>
  );
}

export default App;