import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios'; // Директива import должна быть на верхнем уровне
import './index.css';
import MyChart from './MyChart.jsx';

function App() {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [showVisualization, setShowVisualization] = useState(false);
    const [welcomeScreen, setWelcomeScreen] = useState(true); // Управляет показом приветствующей страницы
    const [userQuery, setUserQuery] = useState(''); // Текст, введенный на приветственной странице
    const [chartData, setChartData] = useState(null); // Данные для визуализации
    const chatRef = useRef(null);

    // Прокрутка вниз при обновлении сообщений
    useEffect(() => {
        if (chatRef.current) {
            chatRef.current.scrollTop = chatRef.current.scrollHeight;
        }
    }, [messages]);

    const sendMessageToServer = async (message) => {
        try {
            const response = await axios.post('http://localhost:8000/get_analyse', {
                message,
            });

            const data = response.data; // В axios данные находятся в свойстве `data`
            console.log(data);

            if (data.analysis) {
                // Добавляем ответ бота
                setMessages((prev) => [
                    ...prev,
                    { sender: 'bot', text: data.analysis },
                ]);

                // Устанавливаем данные для графика
                if (data.chart) {
                    setChartData({
                        type: data.chartType,
                        data: data.chart.data,
                        xKey: data.chart.xKey,
                        yKeys: data.chart.yKeys,
                    });
                    setShowVisualization(true); // Показываем график
                }
            } else {
                setMessages((prev) => [
                    ...prev,
                    { sender: 'bot', text: 'No data available for the query.' },
                ]);
            }
        } catch (error) {
            console.error(error);
            setMessages((prev) => [
                ...prev,
                { sender: 'bot', text: 'Error connecting to the server.' },
            ]);
        }
    };

    const handleSendMessage = () => {
        if (inputValue.trim()) {
            setMessages([...messages, { sender: 'you', text: inputValue }]);
            sendMessageToServer(inputValue); // Отправляем запрос на сервер
            setInputValue('');
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            handleSendMessage(); // Отправка сообщения при нажатии Enter
        }
    };

    const handleStart = () => {
        if (userQuery.trim()) {
            setMessages([...messages, { sender: 'you', text: userQuery }]); // Добавляем запрос в чат
            sendMessageToServer(userQuery); // Отправляем запрос на сервер
        }
        const welcomeScreenElement = document.querySelector('.welcome-screen');
        welcomeScreenElement.classList.add('fade-out'); // Добавляем эффект исчезновения
        setTimeout(() => setWelcomeScreen(false), 500); // Скрываем экран после анимации
    };

    return (
        <div className="mockup-container">
            {welcomeScreen ? (
                <div className="welcome-screen">
                    <div className="welcome-content">
                        <div className="header-buttons centered-buttons">
                            <button className="dropdown">Choose dataset ▼</button>
                            <button className="dropdown">Predictive model ▼</button>
                            <button className="upload-btn">Upload dataset</button>
                        </div>
                        <h1>What can I do for you?</h1>
                        <div className="welcome-input-container">
                            <input
                                type="text"
                                className="welcome-input"
                                placeholder="Enter your request..."
                                value={userQuery}
                                onChange={(e) => setUserQuery(e.target.value)} // Сохраняем текст
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') handleStart(); // Переход по Enter
                                }}
                            />
                        </div>
                    </div>
                </div>
            ) : (
                <>
                    <header className="header">
                        <div className="header-buttons right-aligned-buttons">
                            <button className="dropdown">Choose dataset ▼</button>
                            <button className="dropdown">Predictive model ▼</button>
                            <button className="upload-btn">Upload dataset</button>
                        </div>
                    </header>
                    <div className="content">
                        <div
                            className={`chat-section ${showVisualization ? 'with-visualization' : ''}`}
                            ref={chatRef}
                        >
                            {messages.map((message, index) => (
                                <div
                                    key={index}
                                    className={
                                        message.sender === 'you' ? 'response-bubble' : 'chat-bubble'
                                    }
                                >
                                    <span>{message.sender}</span>
                                    <p>
                                        {typeof message.text === 'string'
                                            ? message.text
                                            : JSON.stringify(message.text.analysis)} {/* Обработка объекта */}
                                    </p>
                                </div>
                            ))}
                        </div>

                        {showVisualization && (
                            <div className="visualization-section">
                                <h2>Visualized Data</h2>
                                <MyChart
                                />
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
                </>
            )}
        </div>
    );
}

export default App;
