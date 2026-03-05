import { configureStore, createSlice } from '@reduxjs/toolkit';

// Initial state
const initialState = {
  cartCount: 0,
};

// Create slice (automatically creates action creators and reducer)
const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    incrementCart: (state) => {
      state.cartCount += 1;
    },
    decrementCart: (state) => {
      state.cartCount = Math.max(0, state.cartCount - 1);
    },
    resetCart: (state) => {
      state.cartCount = 0;
    },
  },
});

// Export the actions 
export const { incrementCart, decrementCart, resetCart } = cartSlice.actions;

// Create the store 
const store = configureStore({
  reducer: {
    cart: cartSlice.reducer,
  },
});

export default store;
