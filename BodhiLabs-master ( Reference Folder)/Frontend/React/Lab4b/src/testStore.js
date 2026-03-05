import { configureStore, createSlice } from '@reduxjs/toolkit';

const testSlice = createSlice({
  name: 'cart',
  initialState: { cartCount: 0 },
  reducers: {
    testResetCart: (state) => {
      state.cartCount = 0;
    },
  },
});

export const { testResetCart } = testSlice.actions;

// Middleware to log state changes
const logMiddleware = storeAPI => next => action => {
  const result = next(action); // Pass the action to the next middleware or reducer
  console.log('Cart Count:', storeAPI.getState().cart.cartCount); // Log the cart count after action
  return result;
};

// Create the store 
const testStore = configureStore({
  reducer: {
    cart: testSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'], // Ignore redux-persist actions
      },
    }).concat(logMiddleware),
});

export default testStore
