import React, { useEffect, useState, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { submitAnswers } from '../redux/slices/appSlice';
import { useNavigate } from 'react-router-dom';
import { ChatList } from 'react-chat-elements';
import 'react-chat-elements/dist/main.css';
import { v4 as uuidv4 } from 'uuid';

const Chatbot = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { questions } = useSelector((state) => state.app);
  const [messages, setMessages] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});

  const displayNextQuestion = useCallback(() => {
    const question = questions[currentQuestionIndex];
    setMessages((prevMessages) => [
      ...prevMessages,
      {
        position: 'left',
        type: 'text',
        text: question.questionText,
        date: new Date(),
        id: uuidv4(),
      },
    ]);
  }, [questions, currentQuestionIndex]);

  useEffect(() => {
    if (questions && questions.length > 0) {
      displayNextQuestion();
    }
  }, [questions, displayNextQuestion]);

  const handleUserResponse = (option) => {
    setMessages((prevMessages) => [
      ...prevMessages,
      {
        position: 'right',
        type: 'text',
        text: option,
        date: new Date(),
        id: uuidv4(),
      },
    ]);

    setUserAnswers({ ...userAnswers, [currentQuestionIndex]: option });

    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setTimeout(displayNextQuestion, 500);
    } else {
      // Submit answers to backend
      dispatch(submitAnswers(userAnswers))
        .unwrap()
        .then(() => {
          navigate('/results');
        })
        .catch((err) => {
          console.error('Failed to submit answers:', err);
        });
    }
  };

  if (!questions || questions.length === 0) {
    return <p>No questions available.</p>;
  }

  const options = questions[currentQuestionIndex].options;

  return (
    <div style={{ maxWidth: 600, margin: '20px auto' }}>
      <ChatList className="chat-list" dataSource={messages} />

      <div style={{ marginTop: 20 }}>
        {options.map((option, index) => (
          <button
            key={index}
            className="chat-button"
            onClick={() => handleUserResponse(option)}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
};

export default Chatbot;
