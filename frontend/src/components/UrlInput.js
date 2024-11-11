import React, { useState } from 'react';
import { Input, Button, message, Spin, Alert } from 'antd';
import { useDispatch, useSelector } from 'react-redux';
import { submitUrl } from '../redux/chatSlice';

// Allows users to input a website URL and submit it for analysis.
const UrlInput = () => {
  const [url, setUrl] = useState(''); 
  const dispatch = useDispatch();
  const { loading, error } = useSelector(state => state.chat);

  const isValidUrl = (urlString) => {
    try {
      new URL(urlString);
      return true;
    } catch (e) {
      return false;
    }
  };

  const handleSubmit = () => {
    if (isValidUrl(url)) {
      dispatch(submitUrl(url));
      setUrl('');
    } else {
      message.error('Please enter a valid URL.');
    }
  };

  if (loading) {
    return <Spin tip="Loading..." />;
  }

  if (error) {
    return <Alert message="Error" description={error} type="error" showIcon />;
  }

  return (
    <div style={{ maxWidth: '500px', margin: '20px auto' }}>
      <Input.Group compact>
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
      </Input.Group>
    </div>
  );
};

export default UrlInput; 