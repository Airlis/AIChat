// Contains configuration constants like API endpoints and error messages./*
export const API_URL = process.env.REACT_APP_API_URL;
export const API_ENDPOINTS = {
  SCRAPE: '/api/scrape',
  RESPOND: '/api/respond'
};
export const REQUEST_TIMEOUT = parseInt(process.env.REACT_APP_TIMEOUT || '30000');
export const MAX_RETRIES = parseInt(process.env.REACT_APP_MAX_RETRIES || '3');
export const ERROR_MESSAGES = {
  NETWORK: 'Network error. Please check your connection.',
  SERVER: 'Server error. Please try again later.',
  INVALID_URL: 'Please enter a valid URL.',
  SESSION_EXPIRED: 'Your session has expired. Please start over.',
  RATE_LIMIT: 'Too many requests. Please try again later.'
};
