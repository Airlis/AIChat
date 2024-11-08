// src/redux/slices/appSlice.js

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Async action to submit the URL and get questions
export const submitUrl = createAsyncThunk('app/submitUrl', async (url, { dispatch }) => {
  try {
    const response = await axios.post('http://localhost:5000/api/scrape', { url });
    const sessionId = response.headers['session-id'] || response.headers['Session-Id'];
    dispatch(setSessionId(sessionId));
    return response.data.questions;
  } catch (error) {
    throw error.response ? error.response.data : error;
  }
});

// Async action to submit answers and get results
export const submitAnswers = createAsyncThunk('app/submitAnswers', async (answers, { getState }) => {
  const state = getState();
  const sessionId = state.app.sessionId;
  try {
    const response = await axios.post(
      'http://localhost:5000/api/submit-answers',
      { answers },
      { headers: { 'Session-Id': sessionId } }
    );
    return response.data.results;
  } catch (error) {
    throw error.response ? error.response.data : error;
  }
});

const appSlice = createSlice({
  name: 'app',
  initialState: {
    loading: false,
    questions: [],
    error: null,
    results: null,
    sessionId: null,
  },
  reducers: {
    reset: (state) => {
      state.loading = false;
      state.questions = [];
      state.error = null;
      state.results = null;
      state.sessionId = null;
    },
    setSessionId: (state, action) => {
      state.sessionId = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Handle submitUrl actions
      .addCase(submitUrl.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.questions = [];
        state.results = null;
      })
      .addCase(submitUrl.fulfilled, (state, action) => {
        state.loading = false;
        state.questions = action.payload;
      })
      .addCase(submitUrl.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch questions.';
      })
      // Handle submitAnswers actions
      .addCase(submitAnswers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(submitAnswers.fulfilled, (state, action) => {
        state.loading = false;
        state.results = action.payload;
      })
      .addCase(submitAnswers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to submit answers.';
      });
  },
});

export const { reset, setSessionId } = appSlice.actions;

export default appSlice.reducer;
