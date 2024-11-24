import React, { useState, useEffect, useRef } from 'react';
import './index.css';
import MyChart from "./MyChart.jsx";

function App() {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [showVisualization, setShowVisualization] = useState(false);
    const chatRef = useRef(null);

    // Прокрутка вниз при обновлении сообщений
    useEffect(() => {
        if (chatRef.current) {
            chatRef.current.scrollTop = chatRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSendMessage = () => {
        if (inputValue.trim()) {
            setMessages([...messages, { sender: 'you', text: inputValue }]);
            setInputValue('');
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            handleSendMessage(); // Отправка сообщения при нажатии Enter
        }
    };

    return (
        <div className="mockup-container">
            <header className="header">
                <div className="header-buttons">
                    <button className="dropdown">Choose dataset ▼</button>
                    <button className="dropdown">Predictive model ▼</button>
                    <button className="upload-btn">Upload dataset</button>
                </div>
            </header>
            <div className="content">
                <div className={`chat-section ${showVisualization ? 'with-visualization' : ''}`} ref={chatRef}>
                    {messages.map((message, index) => (
                        <div
                            key={index}
                            className={message.sender === 'you' ? 'response-bubble' : 'chat-bubble'}
                        >
                            <span>{message.sender}</span>
                            <p>{message.text}</p>
                        </div>
                    ))}
                </div>
                {showVisualization && (
                    <div className="visualization-section">
                        <h2>Visualized Data</h2>
                        <p>Here will be your data visualization content.</p>
                    </div>
                )}
            </div>
            <div className="chat-input-container">
                <input
                    type="text"
                    className="chat-input"
                    placeholder="Write here..."
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown} // Обработка нажатия клавиш
                />
                <button className="send-btn" onClick={handleSendMessage}>
                    Send
                </button>
            </div>
            <footer className="footer">
                <button
                    className="toggle-visualization-btn"
                    onClick={() => setShowVisualization(!showVisualization)}
                >
                    {showVisualization ? 'Hide Visualization' : 'Show Visualization'}
                </button>
            </footer>
        </div>
    );
    // return (
    //     <MyChart/>
    // );
}

export default App;
