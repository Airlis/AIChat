import React, { useState } from 'react';
import { Input, Button, message, Alert, Space } from 'antd';
import { useDispatch, useSelector } from 'react-redux';
import { submitUrl, resetChat } from '../redux/chatSlice';

// Allows users to input a website URL and submit it for analysis.
const UrlInput = () => {
  const [url, setUrl] = useState(''); 
  const dispatch = useDispatch();
  const { error } = useSelector(state => state.chat);

  const isValidUrl = (urlString) => {
    let testUrl = urlString;
    if (!/^https?:\/\//i.test(testUrl)) {
      testUrl = 'http://' + testUrl;
    }
    try {
      new URL(testUrl);
      return testUrl; // Return the processed, valid URL
    } catch (e) {
      return null; // Return null if invalid
    }
  };

  const handleSubmit = () => {
    const processedUrl = isValidUrl(url);
    if (processedUrl) {
      dispatch(resetChat());
      dispatch(submitUrl(processedUrl));
      setUrl('');
    } else {
      message.error('Please enter a valid URL.');
    }
  };

  if (error) {
    return <Alert message="Error" description={error} type="error" showIcon />;
  }

  return (
    <div style={{ maxWidth: '800px', width: '100%', margin: '20px auto' }}>
      <Space.Compact style={{ width: '100%' }}>
        <Input 
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter website URL"
          style={{ width: 'calc(100% - 80px)' }}
          aria-label='Website URL'
        />
        <Button type="primary" onClick={handleSubmit} aria-label='Analyze URL'>
          Analyze
        </Button>
      </Space.Compact>
    </div>
  );
};

export default UrlInput; 