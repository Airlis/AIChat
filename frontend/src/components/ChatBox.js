import React from 'react';
import { Card, Button, Alert } from 'antd';
import { useSelector, useDispatch } from 'react-redux';
import { submitAnswer } from '../redux/chatSlice';
import '../styles/components/Chatbot.css';

// Displays questions, collects user answers, and shows classification results.
const ChatBox = () => {
  const { messages } = useSelector(state => state.chat);
  const dispatch = useDispatch();
  const { error } = useSelector(state => state.chat);

  const hasClassification = messages.some(msg => msg.type === 'classification');

  const handleAnswer = (answer) => {
    dispatch(submitAnswer(answer));
  };

  const lastQuestionIndex = messages
    .map((msg, index) => (msg.type === 'question' ? index : null))
    .filter((index) => index !== null)
    .pop();

  if (error) {
    return <Alert message="Error" description={error} type="error" showIcon />;
  }

  return (
    <Card style={{ maxWidth: '800px', margin: '20px auto' }}>
      {error && (
        <Alert
          message="Error"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: '20px' }}
        />
      )}
      {messages.map((msg, index) => (
        <div key={msg.id || index} style={{ marginBottom: '20px' }}>
          {/* Question */}
          {msg.type === 'question' && (
            <div>
              <p>{msg.content}</p>
              { !hasClassification && (
                  <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                    {msg.options.map((option, i) => (
                      <Button 
                        key={i} 
                        onClick={() => handleAnswer(option)}
                        aria-label={`Option: ${option}`}
                        disabled={index !== lastQuestionIndex}
                      >
                        {option}
                      </Button>
                    ))}
                  </div>
                )
              }
            </div>
          )}

          {/* Answer */}
          {msg.type === 'answer' && (
            <p style={{ textAlign: 'right', color: '#1890ff' }}>
              {msg.content}
            </p>
          )}

          {/* Classification */}
          {msg.type === 'classification' && (
            <div 
              style={{ 
                background: '#f0f2f5',
                padding: '10px', 
                borderRadius: '4px' 
              }}
            >
              <h4>Classification Results:</h4>
              {msg.content.interests && (
                <>
                  <p><strong>Interests:</strong></p>
                  <ul>
                    {msg.content.interests.map((interest, i) => (
                      <li key={i}>{interest}</li>
                    ))}
                  </ul>
                </>
              )}
              {msg.content.relevant_sections && (
                <>
                  <p><strong>Relevant Sections:</strong></p>
                  <ul>
                    {msg.content.relevant_sections.map((section, i) => (
                      <li key={i}>{section}</li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          )}
        </div>
      ))}
    </Card>
  );
};

export default ChatBox; 