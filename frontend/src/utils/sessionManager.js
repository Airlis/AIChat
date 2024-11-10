const SESSION_KEY = 'chat_session';

export const sessionManager = {
  saveSession: (sessionData) => {
    try {
      localStorage.setItem(SESSION_KEY, JSON.stringify({
        ...sessionData,
        timestamp: Date.now()
      }));
    } catch (error) {
      console.error('Failed to save session:', error);
    }
  },

  getSession: () => {
    try {
      const session = localStorage.getItem(SESSION_KEY);
      if (!session) return null;

      const parsedSession = JSON.parse(session);
      const hoursSinceCreation = (Date.now() - parsedSession.timestamp) / (1000 * 60 * 60);
      
      // Session expires after 24 hours
      if (hoursSinceCreation > 24) {
        sessionManager.clearSession();
        return null;
      }

      return parsedSession;
    } catch (error) {
      console.error('Failed to get session:', error);
      return null;
    }
  },

  clearSession: () => {
    try {
      localStorage.removeItem(SESSION_KEY);
    } catch (error) {
      console.error('Failed to clear session:', error);
    }
  },

  updateSession: (updates) => {
    try {
      const currentSession = sessionManager.getSession();
      if (!currentSession) return false;

      sessionManager.saveSession({
        ...currentSession,
        ...updates
      });
      return true;
    } catch (error) {
      console.error('Failed to update session:', error);
      return false;
    }
  }
}; 