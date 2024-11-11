import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';
import {API_URL} from '../constants/config'
import { v4 as uuidv4 } from 'uuid';

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
    const response = await axios.post(
      `${API_URL}/api/respond`, 
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
  reducers: {
    resetChat: (state) => {
      state.messages = [];
      state.sessionId = null;
      state.loading = false;
      state.error = null;
    },
  },
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
          // keep tracking new question
          id: uuidv4(),
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
          id: uuidv4(),
          type: 'answer',
          content: action.meta.arg,  // The user's answer
        });
        if (action.payload.classification) {
          state.messages.push({
            id: uuidv4(),
            type: 'classification',
            content: action.payload.classification,
          });
        } else {
          state.messages.push({
            id: uuidv4(),
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

export const { resetChat } = chatSlice.actions;

export default chatSlice.reducer; 