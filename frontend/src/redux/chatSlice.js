import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';
import { API_URL } from '../constants/config';
import { v4 as uuidv4 } from 'uuid';

// Async thunk to submit the URL
export const submitUrl = createAsyncThunk(
  'chat/submitUrl',
  async (url) => {
    const response = await axios.post(`${API_URL}/api/scrape`, { url });
    return response.data;
  }
);

// Async thunk to submit the user's answer and get the bot's response
export const submitAnswer = createAsyncThunk(
  'chat/submitAnswer',
  async (answer, { getState }) => {
    const { sessionId, messages } = getState().chat;

    // Prepare data for the API call; messages already include the user's answer
    const response = await axios.post(
      `${API_URL}/api/respond`,
      { answer, messages },
      { headers: { 'Session-Id': sessionId } }
    );
    return response.data; // The bot's response
  }
);

// Action to mark the last question as answered and add user's message
export const answerQuestion = (answer) => (dispatch, getState) => {
  const state = getState();
  const messages = state.chat.messages;

  // Find the last question index
  const lastQuestionIndex = messages
    .map((msg, index) => (msg.type === 'question' ? index : null))
    .filter((index) => index !== null)
    .pop();

  if (lastQuestionIndex !== undefined) {
    dispatch({
      type: 'chat/answerQuestion',
      payload: {
        answer,
        questionIndex: lastQuestionIndex,
      },
    });
  }
};

// Chat slice
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
    // Reducer for answering a question
    answerQuestion: (state, action) => {
      const { answer, questionIndex } = action.payload;

      // Mark the question as answered
      if (state.messages[questionIndex]) {
        state.messages[questionIndex].answered = true;
      }

      // Add the user's message
      state.messages.push({
        id: uuidv4(),
        type: 'answer',
        content: answer,
      });
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
          id: uuidv4(),
          type: 'question',
          content: action.payload.question,
          options: action.payload.options,
          answered: false, // Initialize as unanswered
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
            answered: false, // Initialize as unanswered
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