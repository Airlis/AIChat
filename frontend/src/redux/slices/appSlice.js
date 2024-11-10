// src/redux/slices/appSlice.js

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';
import { API_URL, API_ENDPOINTS } from '../../constants/config';
import api from '../../services/api';

// Async thunks
export const submitUrl = createAsyncThunk(
  'app/submitUrl', 
  async (url, { rejectWithValue }) => {
    try {
      console.log('Submitting URL:', url);
      const response = await api.post('/api/scrape', { 
        url,
      });
      console.log('Response:', response);
      
      return {
        sessionId: response.headers['session-id'] || response.headers['Session-Id'],
        question: response.data.question
      };
    } catch (error) {
      console.error('Submit URL Error:', error);
      return rejectWithValue(error.message);
    }
  }
);

export const submitAnswer = createAsyncThunk(
  'app/submitAnswer', 
  async (answer, { getState, rejectWithValue }) => {
    try {
      const state = getState();
      const response = await axios.post(
        `${API_URL}${API_ENDPOINTS.RESPOND}`,
        { answer },
        { headers: { 'Session-Id': state.app.sessionId } }
      );
      return response.data;
    } catch (error) {
      return rejectWithValue(
        error.response?.data?.message || 
        error.message || 
        'Network error occurred'
      );
    }
  }
);

const appSlice = createSlice({
  name: 'app',
  initialState: {
    loading: {
      url: false,
      answer: false
    },
    errors: {
      url: null,
      answer: null
    },
    sessionId: null,
    messages: [],
    currentQuestion: null,
    classification: null
  },
  reducers: {
    addMessage: (state, action) => {
      state.messages.push({
        ...action.payload,
        timestamp: Date.now()
      });
    },
    reset: (state) => {
      state.loading = { url: false, answer: false };
      state.errors = { url: null, answer: null };
      state.sessionId = null;
      state.messages = [];
      state.currentQuestion = null;
      state.classification = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(submitUrl.pending, (state) => {
        state.loading.url = true;
        state.errors.url = null;
      })
      .addCase(submitUrl.fulfilled, (state, action) => {
        state.loading.url = false;
        state.sessionId = action.payload.sessionId;
        state.currentQuestion = action.payload.question;
        state.messages.push({
          type: 'question',
          content: action.payload.question.question,
          options: action.payload.question.options,
          timestamp: Date.now()
        });
      })
      .addCase(submitUrl.rejected, (state, action) => {
        state.loading.url = false;
        state.errors.url = action.error.message;
      })
      .addCase(submitAnswer.pending, (state) => {
        state.loading.answer = true;
        state.errors.answer = null;
      })
      .addCase(submitAnswer.fulfilled, (state, action) => {
        state.loading.answer = false;
        if (action.payload.classification) {
          state.classification = action.payload.classification;
          state.messages.push({
            type: 'classification',
            content: action.payload.classification,
            timestamp: Date.now()
          });
        } else if (action.payload.question) {
          state.currentQuestion = action.payload.question;
          state.messages.push({
            type: 'question',
            content: action.payload.question.question,
            options: action.payload.question.options,
            timestamp: Date.now()
          });
        }
      })
      .addCase(submitAnswer.rejected, (state, action) => {
        state.loading.answer = false;
        state.errors.answer = action.error.message;
      });
  }
});

export const { addMessage, reset } = appSlice.actions;
export default appSlice.reducer;