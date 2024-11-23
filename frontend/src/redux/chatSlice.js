import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';
import { API_URL } from '../constants/config';
import { v4 as uuidv4 } from 'uuid';

// Async thunk to submit the URL
export const submitUrl = createAsyncThunk(
  'chat/submitUrl',
  async (url, { rejectWithValue }) => {
    try {
      const response = await axios.post(`${API_URL}/api/scrape`, { url });
      return response.data;
    } catch (error) {
      // Check if the error response exists and has a message
      if (error.response && error.response.data && error.response.data.error) {
        // Return the custom error message from the server
        return rejectWithValue(error.response.data.error);
      } else {
        return rejectWithValue('An unexpected error occurred.');
      }
    }
  }
);

// Async thunk to submit the user's answer and get the bot's response
export const submitAnswer = createAsyncThunk(
  'chat/submitAnswer',
  async (answer, { getState, rejectWithValue }) => {
    try {
      const { sessionId } = getState().chat;
      const response = await axios.post(
        `${API_URL}/api/respond`,
        { answer },
        { headers: { 'Session-Id': sessionId } }
      );
      return response.data;
    } catch (error) {
      if (error.response && error.response.data && error.response.data.error) {
        return rejectWithValue(error.response.data.error);
      } else {
        return rejectWithValue('An unexpected error occurred.');
      }
    }
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
    urlError: null,
    chatError: null,
  },
  reducers: {
    resetChat: (state) => {
      state.messages = [];
      state.sessionId = null;
      state.loading = false;
      state.urlError = null;
      state.chatError = null;
    },
    clearUrlError: (state) => {
      state.urlError = null;
    },
    clearChatError: (state) => {
      state.chatError = null;
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
        state.urlError = null;
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
        state.urlError = action.payload || 'Failed to submit URL';
      })
      // Handling submitAnswer
      .addCase(submitAnswer.pending, (state) => {
        state.loading = true;
        state.chatError = null;
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
        state.chatError = action.payload || 'Failed to submit answer';
      });
  },
});

export const { resetChat, clearUrlError, clearChatError } = chatSlice.actions;

export default chatSlice.reducer;