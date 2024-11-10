/**
 * @typedef {Object} Question
 * @property {string} question - The question text
 * @property {string[]} options - Array of possible answers
 */

/**
 * @typedef {Object} Classification
 * @property {string[]} interests - User's identified interests
 * @property {string[]} relevant_sections - Relevant content sections
 * @property {string} [primary_interest] - Optional main interest category
 */

/**
 * @typedef {Object} Message
 * @property {'question' | 'answer' | 'classification'} type - Message type identifier
 * @property {string | Question | Classification} content - Message content based on type
 * @property {string[]} [options] - Optional answer options for questions
 * @property {number} timestamp - Unix timestamp of message creation
 * @property {string} [error] - Optional error message
 */

/**
 * @typedef {Object} LoadingState
 * @property {boolean} url - URL submission loading state
 * @property {boolean} answer - Answer submission loading state
 */

/**
 * @typedef {Object} ErrorState
 * @property {string | null} url - URL submission error
 * @property {string | null} answer - Answer submission error
 */

/**
 * @typedef {Object} ChatState
 * @property {LoadingState} loading - Loading states
 * @property {ErrorState} errors - Error states
 * @property {string | null} sessionId - Current session identifier
 * @property {Message[]} messages - Chat message history
 * @property {Question | null} currentQuestion - Current active question
 * @property {Classification | null} classification - Final classification result
 */

/**
 * @typedef {Object} ApiResponse
 * @property {string} sessionId - Session identifier from server
 * @property {Question | Classification} data - Response data
 * @property {string} [error] - Optional error message
 * @property {number} timestamp - Server response timestamp
 */

/**
 * @typedef {Object} ApiError
 * @property {string} message - Error message
 * @property {string} code - Error code
 * @property {number} status - HTTP status code
 */

export {};  // Ensures this is treated as a module