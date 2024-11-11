import React from 'react';
import { useEffect, useRef } from 'react';
import { Alert, Button } from 'antd';
import { useSelector, useDispatch } from 'react-redux';
import { submitAnswer } from '../redux/chatSlice';
import '../styles/components/Chatbot.css'; // Ensure this CSS file includes the styles for chat bubbles

// Displays questions, collects user answers, and shows classification results.
const ChatBox = () => {
  const { messages, error } = useSelector((state) => state.chat);
  const dispatch = useDispatch();
  const chatEndRef = useRef(null);

  const hasClassification = messages.some((msg) => msg.type === 'classification');

  const handleAnswer = (answer) => {
    dispatch(submitAnswer(answer));
  };

  const lastQuestionIndex = messages
    .map((msg, index) => (msg.type === 'question' ? index : null))
    .filter((index) => index !== null)
    .pop();

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div style={{ maxWidth: '800px', width: '100%', margin: '20px auto' }}>
      {error && (
        <Alert message="Error" description={error} type="error" showIcon style={{ marginBottom: '20px' }} />
      )}
      <div className="chat-container">
        {messages.map((msg, index) => (
          <div key={msg.id || index} className="message-row">
            {/* Chatbot Message */}
            {msg.type === 'question' && (
              <div className="message-bubble chatbot">
                <p>{msg.content}</p>
                {!hasClassification && index === lastQuestionIndex && (
                  <div className="options-container">
                    {msg.options.map((option, i) => (
                      <Button
                        key={i}
                        onClick={() => handleAnswer(option)}
                        aria-label={`Option: ${option}`}
                        disabled={index !== lastQuestionIndex}
                        className="option-button"
                      >
                        {option}
                      </Button>
                    ))}
                    <div ref={chatEndRef} />
                  </div>
                )}
              </div>
            )}

            {/* User Message */}
            {msg.type === 'answer' && (
              <div className="message-bubble user">
                <p>{msg.content}</p>
              </div>
            )}

            {/* Classification Result */}
            {msg.type === 'classification' && (
              <div className="message-bubble classification">
                <h4>Classification Results:</h4>
                {msg.content.interests && (
                  <>
                    <p>
                      <strong>Interests:</strong>
                    </p>
                    <ul>
                      {msg.content.interests.map((interest, i) => (
                        <li key={i}>{interest}</li>
                      ))}
                    </ul>
                  </>
                )}
                {msg.content.relevant_sections && (
                  <>
                    <p>
                      <strong>Relevant Sections:</strong>
                    </p>
                    {msg.content.relevant_sections.map((section, i) => (
                      <p key={i}>{section}</p>
                    ))}
                  </>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChatBox;