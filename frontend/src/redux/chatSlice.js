import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';
import {API_URL} from '../constants/config'

export const submitUrl = createAsyncThunk(
  'chat/submitUrl',
  async (url) => {
    const response = await axios.post(`${API_URL}/api/scrape`, { url });
    return response.data;
  }
);

export const submitAnswer = createAsyncThunk(
  'chat/submitAnswer',
  async (answer, { getState }) => {
    const { sessionId } = getState().chat;
    const response = await axios.post(`${API_URL}/api/respond`, 
      { answer },
      { headers: { 'Session-Id': sessionId } }
    );
    return response.data;
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [],
    sessionId: null,
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      // Handling submitUrl
      .addCase(submitUrl.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(submitUrl.fulfilled, (state, action) => {
        state.loading = false;
        state.sessionId = action.payload.session_id;
        state.messages.push({
          type: 'question',
          content: action.payload.question,
          options: action.payload.options,
        });
      })
      .addCase(submitUrl.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to submit URL';
      })
      // Handling submitAnswer
      .addCase(submitAnswer.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(submitAnswer.fulfilled, (state, action) => {
        state.loading = false;
        state.messages.push({
          type: 'answer',
          content: action.meta.arg,
        });
        if (action.payload.classification) {
          state.messages.push({
            type: 'classification',
            content: action.payload.classification,
          });
        } else {
          state.messages.push({
            type: 'question',
            content: action.payload.question,
            options: action.payload.options,
          });
        }
      })
      .addCase(submitAnswer.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to submit answer';
      });
  },
});

export default chatSlice.reducer; 