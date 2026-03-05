import React from 'react';
import '../csses/ProductCard.css';
import { useDispatch } from 'react-redux';
import { incrementCart, decrementCart } from '../store';

const ProductCard = ({ product }) => {
  const dispatch = useDispatch();

  const add2Cart = () => dispatch(incrementCart());
  const removeFromCart = () => dispatch(decrementCart());

  return (
    <div className="product-card" data-testid="product-card">
      <h2>{product.name}</h2>
      <p>Price: {product.price}</p>
      <div>
        <button onClick={add2Cart}>+</button>
        <button onClick={removeFromCart}>-</button>
      </div>
    </div>
  );
};

export default ProductCard;
