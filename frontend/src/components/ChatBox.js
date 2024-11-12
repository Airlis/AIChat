import React, { useEffect, useRef, useState } from 'react';
import { Alert, Button, Card, Avatar } from 'antd';
import { RobotOutlined, UserOutlined } from '@ant-design/icons';
import { useSelector, useDispatch } from 'react-redux';
import { submitAnswer, answerQuestion } from '../redux/chatSlice';
import '../styles/components/Chatbox.css';

const ChatBox = () => {
  const { messages, error, loading } = useSelector((state) => state.chat);
  const dispatch = useDispatch();
  const chatEndRef = useRef(null);

  const hasClassification = messages.some((msg) => msg.type === 'classification');

  const [selectedOption, setSelectedOption] = useState(null);

  const handleAnswer = (answer) => {
    if (!loading) {
      setSelectedOption(answer);
      dispatch(answerQuestion(answer));
      dispatch(submitAnswer(answer));
    }
  };

  const lastQuestionIndex = messages
    .map((msg, index) => (msg.type === 'question' ? index : null))
    .filter((index) => index !== null)
    .pop();

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => {
    // Find the last message
    const lastMessage = messages[messages.length - 1];

    // If the last message is a question and not loading, reset selectedOption
    if (lastMessage && lastMessage.type === 'question' && !loading) {
      setSelectedOption(null);
    }
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
                              disabled={
                                loading ||
                                index !== lastQuestionIndex ||
                                selectedOption !== null
                              }
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
