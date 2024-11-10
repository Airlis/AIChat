import React, { useState } from 'react';
import { Input, Button } from 'antd';
import { useDispatch } from 'react-redux';
import { submitUrl } from '../redux/chatSlice';

const UrlInput = () => {
  const [url, setUrl] = useState('');
  const dispatch = useDispatch();

  const handleSubmit = () => {
    if (url) {
      dispatch(submitUrl(url));
      setUrl('');
    }
  };

  return (
    <div style={{ maxWidth: '500px', margin: '20px auto' }}>
      <Input.Group compact>
        <Input 
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter website URL"
          style={{ width: 'calc(100% - 80px)' }}
        />
        <Button type="primary" onClick={handleSubmit}>
          Analyze
        </Button>
      </Input.Group>
    </div>
  );
};

export default UrlInput; 