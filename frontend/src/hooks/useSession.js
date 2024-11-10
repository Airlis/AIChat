import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { sessionManager } from '../utils/sessionManager';
import { ROUTES } from '../constants/config';

export const useSession = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { sessionId } = useSelector(state => state.app);

  useEffect(() => {
    const session = sessionManager.getSession();
    
    if (!session && sessionId) {
      // Session expired
      dispatch({ type: 'app/reset' });
      navigate(ROUTES.HOME);
    } else if (session && !sessionId) {
      // Restore session
      dispatch({
        type: 'app/restoreSession',
        payload: session
      });
    }
  }, [sessionId, dispatch, navigate]);

  return {
    isAuthenticated: !!sessionId,
    sessionId
  };
}; 