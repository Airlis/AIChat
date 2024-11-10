import React, { useRef, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RobotOutlined, UserOutlined } from '@ant-design/icons';
import { submitAnswer } from '../redux/slices/appSlice';

const Chatbot = () => {
  const dispatch = useDispatch();
  const { messages, loading } = useSelector((state) => state.app);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const isCurrentQuestion = (index) => {
    return index === messages.filter(m => m.type === 'question').length - 1 
           && !messages.some(m => m.type === 'classification');
  };

  const handleOptionClick = async (option) => {
    if (loading.answer) return;
    
    dispatch({
      type: 'app/addMessage',
      payload: {
        type: 'answer',
        content: option
      }
    });

    await dispatch(submitAnswer(option));
  };

  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.type}`}>
            {message.type === 'question' && (
              <>
                <RobotOutlined className="message-icon" />
                <div className="message-content">
                  <p>{message.content}</p>
                  <div className="options-container">
                    {message.options.map((option, i) => (
                      <button
                        key={i}
                        onClick={() => handleOptionClick(option)}
                        disabled={!isCurrentQuestion(index) || loading.answer}
                        className="chat-button"
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}
            {message.type === 'answer' && (
              <>
                <div className="message-content user">
                  <p>{message.content}</p>
                </div>
                <UserOutlined className="message-icon" />
              </>
            )}
            {message.type === 'classification' && (
              <div className="classification-result">
                <h3>Classification Result:</h3>
                <div className="interests">
                  <h4>Interests:</h4>
                  {message.content.interests.map((interest, i) => (
                    <p key={i}>{interest}</p>
                  ))}
                </div>
                <div className="relevant-sections">
                  <h4>Relevant Content:</h4>
                  {message.content.relevant_sections.map((section, i) => (
                    <p key={i}>{section}</p>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>
    </div>
  );
};

export default Chatbot;
