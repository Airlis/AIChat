import api from './api';
import { API_ENDPOINTS } from '../constants/config';

export const chatService = {
  submitUrl: async (url) => {
    try {
      const response = await api.post(API_ENDPOINTS.SCRAPE, { url });
      return {
        sessionId: response.headers['session-id'] || response.headers['Session-Id'],
        question: response.data.question
      };
    } catch (error) {
      throw error;
    }
  },

  submitAnswer: async (answer) => {
    try {
      const response = await api.post(API_ENDPOINTS.RESPOND, { answer });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};