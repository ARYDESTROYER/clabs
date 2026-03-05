import React from 'react';
import '../csses/ProductCard.css';

// Modify the ProductCard component so that it can increment and decrement
// the cart icon value using the '+' and '-' buttons
const ProductCard = ({ product }) => {
  return (
    <div className="product-card" data-testid="product-card">
      <h2>{product.name}</h2>
      <p>Price: {product.price}</p>
      <div>
        <button>+</button>
        <button>-</button>
      </div>
    </div>
  );
};

export default ProductCard;
