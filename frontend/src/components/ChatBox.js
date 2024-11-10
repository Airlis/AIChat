import React from 'react';
import { Card, Button } from 'antd';
import { useSelector, useDispatch } from 'react-redux';
import { submitAnswer } from '../redux/chatSlice';
import '../styles/components/Chatbot.css';

const ChatBox = () => {
  const { messages } = useSelector(state => state.chat);
  const dispatch = useDispatch();

  const handleAnswer = (answer) => {
    dispatch(submitAnswer(answer));
  };

  return (
    <Card style={{ maxWidth: '500px', margin: '20px auto' }}>
      {messages.map((msg, index) => (
        <div key={index} style={{ marginBottom: '20px' }}>
          {/* Question */}
          {msg.type === 'question' && (
            <div>
              <p>{msg.content}</p>
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                {msg.options.map((option, i) => (
                  <Button 
                    key={i} 
                    onClick={() => handleAnswer(option)}
                  >
                    {option}
                  </Button>
                ))}
              </div>
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
            <div style={{ background: '#f0f2f5', padding: '10px', borderRadius: '4px' }}>
              <h4>Classification Results:</h4>
              <ul>
                {msg.content.interests.map((interest, i) => (
                  <li key={i}>{interest}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ))}
    </Card>
  );
};

export default ChatBox; 