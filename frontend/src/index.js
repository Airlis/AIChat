import React from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import chatReducer from './redux/chatSlice';
import App from './App';
import 'antd/dist/reset.css';

const store = configureStore({
  reducer: {
    chat: chatReducer
  }
});

const root = createRoot(document.getElementById('root'));
root.render(
  <Provider store={store}>
    <App />
  </Provider>
);
