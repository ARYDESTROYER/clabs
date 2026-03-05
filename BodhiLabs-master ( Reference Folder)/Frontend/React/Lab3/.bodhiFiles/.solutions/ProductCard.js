import React from 'react';
import '../csses/ProductCard.css';

const ProductCard = ({ product, incrementCart, decrementCart }) => {
  return (
    <div className="product-card" data-testid="product-card">
      <h2>{product.name}</h2>
      <p>Price: {product.price}</p>
      <div>
        <button onClick={incrementCart}>+</button>
        <button onClick={decrementCart}>-</button>
      </div>
    </div>
  );
};

export default ProductCard;
