import { configureStore } from '@reduxjs/toolkit';
import appReducer from '../redux/slices/appSlice';

const store = configureStore({
  reducer: {
    app: appReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ['app/submitUrl/fulfilled', 'app/submitAnswer/fulfilled'],
        // Ignore these field paths in all actions
        ignoredActionPaths: ['payload.timestamp'],
        // Ignore these paths in the state
        ignoredPaths: ['app.messages.timestamp']
      }
    })
});

export default store; 