import React from 'react';
import { Typography, Space } from 'antd';
import { UserOutlined, RobotOutlined } from '@ant-design/icons';
import classNames from 'classnames';

const { Text } = Typography;

const Message = ({ message, isLast, onOptionClick, loading }) => {
  const messageClasses = classNames('message', {
    'message-user': message.type === 'answer',
    'message-bot': message.type === 'question',
    'message-result': message.type === 'classification'
  });

  const renderContent = () => {
    switch (message.type) {
      case 'question':
        return (
          <>
            <RobotOutlined className="message-icon" />
            <div className="message-content">
              <Text>{message.content}</Text>
              {isLast && message.options && (
                <Space className="message-options" wrap>
                  {message.options.map((option, index) => (
                    <button
                      key={index}
                      onClick={() => onOptionClick(option)}
                      disabled={loading}
                      className="option-button"
                    >
                      {option}
                    </button>
                  ))}
                </Space>
              )}
            </div>
          </>
        );

      case 'answer':
        return (
          <>
            <div className="message-content user">
              <Text>{message.content}</Text>
            </div>
            <UserOutlined className="message-icon" />
          </>
        );

      case 'classification':
        return (
          <div className="classification-content">
            <h3>Classification Result:</h3>
            <div className="interests">
              <h4>Interests:</h4>
              {message.content.interests.map((interest, i) => (
                <Text key={i} className="interest-tag">{interest}</Text>
              ))}
            </div>
            {message.content.relevant_sections && (
              <div className="relevant-sections">
                <h4>Relevant Content:</h4>
                {message.content.relevant_sections.map((section, i) => (
                  <Text key={i} className="section-text">{section}</Text>
                ))}
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className={messageClasses}>
      {renderContent()}
    </div>
  );
};

export default React.memo(Message); 