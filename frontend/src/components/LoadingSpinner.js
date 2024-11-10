import React from 'react';
import { Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

const LoadingSpinner = ({ size = 'large', tip = 'Loading...' }) => (
  <div className="loading-container">
    <Spin 
      indicator={<LoadingOutlined style={{ fontSize: 24 }} spin />}
      size={size}
      tip={tip}
    />
  </div>
);

export default LoadingSpinner; 