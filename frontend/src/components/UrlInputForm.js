import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Input, Button, Alert } from 'antd';
import { submitUrl } from '../redux/slices/appSlice';

const UrlInputForm = () => {
  const [url, setUrl] = useState('');
  const dispatch = useDispatch();
  const { loading, errors } = useSelector((state) => state.app);

  const handleSubmit = async () => {
    if (!url) return;

    try {
      // Add http:// if not present
      const formattedUrl = url.startsWith('http') ? url : `https://${url}`;
      await dispatch(submitUrl(formattedUrl)).unwrap();
    } catch (error) {
      // Error is handled by Redux
      console.error('Error submitting URL:', error);
    }
  };

  return (
    <div className="url-input-container">
      {errors.url && (
        <Alert
          message="Error"
          description={errors.url}
          type="error"
          showIcon
          closable
          className="error-alert"
        />
      )}
      <div className="input-group">
        <Input
          placeholder="Enter website URL (e.g., www.example.com)"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onPressEnter={handleSubmit}
          disabled={loading.url}
        />
        <Button
          type="primary"
          onClick={handleSubmit}
          loading={loading.url}
        >
          Analyze
        </Button>
      </div>
    </div>
  );
};

export default UrlInputForm;
