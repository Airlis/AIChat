import React, { useState } from 'react';
import { Input, Button, Alert, Space } from 'antd';
import { useDispatch, useSelector } from 'react-redux';
import { submitUrl, resetChat, clearUrlError } from '../redux/chatSlice';

// Allows users to input a website URL and submit it for analysis.
const UrlInput = () => {
  const [url, setUrl] = useState(''); 
  const dispatch = useDispatch();
  const { urlError } = useSelector(state => state.chat);

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
      // Display an error message if the URL is invalid
      dispatch({
        type: 'chat/submitUrl/rejected',
        payload: 'Please enter a valid URL.',
      });
    }
  };

  const handleUrlChange = (e) => {
    setUrl(e.target.value);
    if (urlError) {
      dispatch(clearUrlError());
    }
  };

  return (
    <div style={{ maxWidth: '800px', width: '100%', margin: '20px auto' }}>
      {urlError && (
        <Alert
          message="Error"
          description={urlError}
          type="error"
          showIcon
          style={{ marginBottom: '10px' }}
        />
      )}
      <Space.Compact style={{ width: '100%' }}>
        <Input
          value={url}
          onChange={handleUrlChange}
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