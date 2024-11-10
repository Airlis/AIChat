import React from 'react';
import { useSelector } from 'react-redux';
import { Card, List, Tag, Typography } from 'antd';
import { useNavigate } from 'react-router-dom';

const { Title, Text } = Typography;

const Results = () => {
  const { classification } = useSelector(state => state.app);
  const navigate = useNavigate();

  React.useEffect(() => {
    if (!classification) {
      navigate('/');
    }
  }, [classification, navigate]);

  if (!classification) return null;

  return (
    <div className="results-container">
      <Card title="Classification Results">
        <div className="interests-section">
          <Title level={4}>Interests</Title>
          <div className="tags-container">
            {classification.interests.map((interest, i) => (
              <Tag key={i} color="blue">{interest}</Tag>
            ))}
          </div>
        </div>

        <div className="relevant-sections">
          <Title level={4}>Relevant Content</Title>
          <List
            dataSource={classification.relevant_sections}
            renderItem={(section) => (
              <List.Item>
                <Text>{section}</Text>
              </List.Item>
            )}
          />
        </div>

        {classification.primary_interest && (
          <div className="primary-interest">
            <Title level={4}>Primary Interest</Title>
            <Tag color="green" style={{ fontSize: '16px' }}>
              {classification.primary_interest}
            </Tag>
          </div>
        )}
      </Card>
    </div>
  );
};

export default Results;
