import React from 'react';
import { Card, Button } from 'antd';
import { useSelector, useDispatch } from 'react-redux';
import { reset } from '../redux/slices/appSlice';
import { useNavigate } from 'react-router-dom';

const Results = () => {
  const { results } = useSelector((state) => state.app);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleRestart = () => {
    dispatch(reset());
    navigate('/');
  };

  if (!results) {
    return <p>No results available.</p>;
  }

  return (
    <Card style={{ maxWidth: 600, margin: '50px auto', textAlign: 'center' }}>
      <h2>Your Classification</h2>
      <p>{results}</p>
      <Button type="primary" onClick={handleRestart}>
        Start Over
      </Button>
    </Card>
  );
};

export default Results;
