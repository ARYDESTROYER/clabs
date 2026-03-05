import React from 'react';
import { useDispatch } from 'react-redux';
import { resetCart } from '../store'; 
import '../csses/ResetButton.css';

const ResetButton = () => {
  const dispatch = useDispatch();

  const handleReset = () => {
    dispatch(resetCart());
  };

  return (
    <button className="reset-button" onClick={handleReset} data-testid="reset-button">
      Reset Cart
    </button>
  );
};

export default ResetButton;

