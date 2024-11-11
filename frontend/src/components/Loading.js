import React from 'react';
import { Spin } from 'antd';

const LoadingOverlay = () => (
    <div style={styles.overlay}>
      <Spin tip="Loading..." size="large">
        {/* Placeholder div to enable the tip */}
        <div style={{ width: '100%', height: '100%' }}></div>
      </Spin>
    </div>
  );
  

const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    backgroundColor: 'rgba(255, 255, 255, 0.7)', // semi-transparent background
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 9999,
  },
};

export default LoadingOverlay;