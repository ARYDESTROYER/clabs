import React from 'react';
import '../csses/CartIcon.css';
import { useSelector } from 'react-redux';

const CartIcon = () => {

  const cartCount = useSelector(state => state.cart.cartCount);

  return (
    <div className="cart-icon" data-testid="cart-icon">
      {/* Inline SVG for a shopping cart */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="currentColor"
        className="cart-svg"
      >
        <path d="M7 4V2C7 0.89543 7.89543 0 9 0H15C16.1046 0 17 0.89543 17 2V4H21C22.1046 4 23 4.89543 23 6C23 7.10457 22.1046 8 21 8H19L17.7345 18.5272C17.6029 19.5142 16.7692 20.291 15.7731 20.2929H8.22692C7.2308 20.291 6.3971 19.5142 6.26549 18.5272L5 8H3C1.89543 8 1 7.10457 1 6C1 4.89543 1.89543 4 3 4H7ZM9 4H15V2H9V4ZM9 6H8.1582L9.42262 17H14.5774L15.8418 6H9ZM9 23C9 22.4477 8.55228 22 8 22C7.44772 22 7 22.4477 7 23C7 23.5523 7.44772 24 8 24C8.55228 24 9 23.5523 9 23ZM16 23C16 22.4477 15.5523 22 15 22C14.4477 22 14 22.4477 14 23C14 23.5523 14.4477 24 15 24C15.5523 24 16 23.5523 16 23Z" />
      </svg>
      <span className="cart-count" data-testid="cart-count">{cartCount}</span>
    </div>
  );
};

export default CartIcon;
