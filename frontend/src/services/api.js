import axios from 'axios';
import { API_URL } from '../constants/config';

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Simplified interceptors
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    if (!error.response) {
      throw new Error('Network error. Please check if the backend server is running.');
    }
    throw error;
  }
);

export default api;