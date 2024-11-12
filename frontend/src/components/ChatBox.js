import React, { useEffect, useRef } from 'react';
import { Alert, Button, Card, Avatar } from 'antd';
import { RobotOutlined, UserOutlined } from '@ant-design/icons';
import { useSelector, useDispatch } from 'react-redux';
import { submitAnswer, answerQuestion } from '../redux/chatSlice'; // Import answerQuestion
import '../styles/components/Chatbox.css';

const ChatBox = () => {
  const { messages, error, loading } = useSelector((state) => state.chat);
  const dispatch = useDispatch();
  const chatEndRef = useRef(null);

  const hasClassification = messages.some((msg) => msg.type === 'classification');

  const handleAnswer = (answer) => {
    dispatch(answerQuestion(answer)); // Mark question as answered and add user's message
    dispatch(submitAnswer(answer));   // Then submit the answer to get the bot's response
  };

  const lastQuestionIndex = messages
    .map((msg, index) => (msg.type === 'question' ? index : null))
    .filter((index) => index !== null)
    .pop();

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <>
      {error && (
        <Alert
          message="Error"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: '20px' }}
        />
      )}
      <div className="chatbox-wrapper">
        <Card className="chatbox" bodyStyle={{ padding: '10px' }}>
          <div className="chat-container">
            {messages.map((msg, index) => (
              <div key={msg.id || index} className={`message-row ${msg.type}`}>
                {/* Chatbot Message */}
                {msg.type === 'question' && (
                  <div className="chat-message chatbot">
                    <Avatar icon={<RobotOutlined />} />
                    <div className="chat-message-content">
                      <p>{msg.content}</p>
                      {!hasClassification && index === lastQuestionIndex && !msg.answered && (
                        <div className="options-container">
                          {msg.options.map((option, i) => (
                            <Button
                              key={i}
                              onClick={() => handleAnswer(option)}
                              aria-label={`Option: ${option}`}
                              disabled={loading || index !== lastQuestionIndex}
                              className="option-button"
                            >
                              {option}
                            </Button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* User Message */}
                {msg.type === 'answer' && (
                  <div className="chat-message user">
                    <Avatar icon={<UserOutlined />} />
                    <div className="chat-message-content">
                      <p>{msg.content}</p>
                    </div>
                  </div>
                )}

                {/* Classification Result */}
                {msg.type === 'classification' && (
                  <div className="chat-message classification">
                    <Avatar icon={<RobotOutlined />} />
                    <div className="chat-message-content">
                      <div className="classification-result">
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
                    </div>
                  </div>
                )}
              </div>
            ))}

            {/* Typing Indicator */}
            {loading && (
              <div className="message-row chatbot">
                <div className="chat-message">
                  <Avatar icon={<RobotOutlined />} />
                  <div className="chat-message-content typing-indicator">
                    <span className="typing-ellipsis">
                      <span></span>
                      <span></span>
                      <span></span>
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>
        </Card>
      </div>
    </>
  );
};

export default ChatBox;