import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { submitAnswer, addMessage } from '../redux/slices/appSlice';

export const useChat = () => {
  const dispatch = useDispatch();
  const {
    messages,
    currentQuestion,
    loading,
    errors,
    classification
  } = useSelector(state => state.app);

  const handleSubmitAnswer = useCallback(async (answer) => {
    try {
      dispatch(addMessage({
        type: 'answer',
        content: answer
      }));
      await dispatch(submitAnswer(answer)).unwrap();
    } catch (error) {
      // Error handled by Redux
    }
  }, [dispatch]);

  return {
    messages,
    currentQuestion,
    loading,
    errors,
    classification,
    handleSubmitAnswer
  };
};