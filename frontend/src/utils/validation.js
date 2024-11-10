export const isValidUrl = (string) => {
  try {
    new URL(string);
    return true;
  } catch (_) {
    return false;
  }
};

export const sanitizeUrl = (url) => {
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    return `https://${url}`;
  }
  return url;
};

export const validateMessage = (message) => {
  if (!message || !message.type) {
    throw new Error('Invalid message format');
  }

  switch (message.type) {
    case 'question':
      if (!message.content || !Array.isArray(message.options)) {
        throw new Error('Invalid question format');
      }
      break;
    case 'classification':
      if (!message.content.interests || !Array.isArray(message.content.interests)) {
        throw new Error('Invalid classification format');
      }
      break;
    case 'answer':
      if (!message.content) {
        throw new Error('Invalid answer format');
      }
      break;
    default:
      throw new Error('Unknown message type');
  }

  return true;
}; 