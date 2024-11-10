export const handleApiError = (error) => {
  if (error.response) {
    const { status, data } = error.response;
    switch (status) {
      case 400:
        return {
          message: data.message || 'Invalid request',
          code: 'BAD_REQUEST'
        };
      case 429:
        return {
          message: 'Rate limit exceeded. Please try again later.',
          code: 'RATE_LIMIT'
        };
      default:
        return {
          message: data.message || 'Server error',
          code: 'SERVER_ERROR'
        };
    }
  }
  return {
    message: 'Network error. Please check your connection.',
    code: 'NETWORK_ERROR'
  };
};