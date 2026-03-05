import { render, screen, fireEvent, within } from '@testing-library/react';
import App from './App';
import { Provider } from 'react-redux';
import store from './store';
import testStore from './testStore';
import { resetCart } from './store';
import { testResetCart } from './testStore';

// Helper function to render App with a fresh Redux store
const renderWithRedux = () => {
  render(
    <Provider store={store}>
      <App />
    </Provider>
  );

  return store;
};

beforeEach(() => {
  localStorage.clear();
  testStore.dispatch(testResetCart());
});

// Test Cart icon displays 0 initially
test('Initial value of cart count is 0: ', () => {
  renderWithRedux();
  const text = screen.getByText('0');
  expect(text).toBeInTheDocument();
});

test('Cart value increments when + button is clicked: ', () => {
  renderWithRedux();
  const productCards = screen.getAllByTestId('product-card');
  const incrementButton = within(productCards[0]).getByText('+');
  const valueElement = screen.getByTestId('cart-icon');
  const initialValue = parseInt(valueElement.textContent, 10);
  fireEvent.click(incrementButton);
  expect(valueElement).toHaveTextContent((initialValue + 1).toString());
});

test('Cart value decrements when - button is clicked: ', () => {
  renderWithRedux();
  const productCards = screen.getAllByTestId('product-card');
  const incrementButton = within(productCards[0]).getByText('+');
  const decrementButton = within(productCards[0]).getByText('-');
  const valueElement = screen.getByTestId('cart-icon');
  const initialValue = parseInt(valueElement.textContent, 10);
  
  for (let i = 0; i < 10; i++) {
    fireEvent.click(incrementButton);
  }
  
  fireEvent.click(decrementButton);
  expect(valueElement).toHaveTextContent((initialValue + 10 - 1).toString());
});

test('Cart value resets when "Reset Cart" button is clicked: ', () => {
  renderWithRedux();
  const productCards = screen.getAllByTestId('product-card');
  const incrementButton = within(productCards[0]).getByText('+');
  const valueElement = screen.getByTestId('cart-icon');
  const initialValue = parseInt(valueElement.textContent, 10);
  fireEvent.click(incrementButton);
  fireEvent.click(incrementButton);
  fireEvent.click(incrementButton);
  // Now value should be 3 in the cart
  const resetButton = screen.getByTestId('reset-button');
  fireEvent.click(resetButton);
  expect(valueElement).toHaveTextContent((0).toString());
});

test('Cart count persists after page reload', () => {
  renderWithRedux();
  const productCards = screen.getAllByTestId('product-card');
  const incrementButton = within(productCards[0]).getByText('+');
  const valueElement = screen.getByTestId('cart-icon');
  const initialValue = parseInt(valueElement.textContent, 10);
  fireEvent.click(incrementButton);
  expect(valueElement).toHaveTextContent((initialValue + 1).toString());
  renderWithRedux();
  expect(valueElement).toHaveTextContent((initialValue + 1).toString());
});
