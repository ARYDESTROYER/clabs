import { configureStore, createSlice } from '@reduxjs/toolkit';
import { persistReducer, persistStore } from 'redux-persist';
import storage from 'redux-persist/lib/storage'; // Default is localStorage

// Initial state of cartCount
const initialState = {
  // write here
};

// Create slice (automatically creates action creators and reducer)
const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    incrementCart: (state) => {
      // increment cart logic here
    },
    decrementCart: (state) => {
      // decrement cart logic here
    },
    resetCart: (state) => {
      // reset cart logic here
    },
  },
});

// Export the actions 

// Configure persist
const persistConfig = {
  // Declare the key for localStorage (could be anything)
  // Use localStorage for persistence
  key: 'cartCount', // The key for localStorage (could be anything)
  storage, // Use localStorage for persistence
};

const persistedReducer = persistReducer(persistConfig, cartSlice.reducer);


// Create the store 
const store = configureStore({
  reducer: {
    cart: persistedReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'], // Ignore redux-persist actions
      },
    }),
});

// Create the persistor
export const persistor = persistStore(store);

export default store;
