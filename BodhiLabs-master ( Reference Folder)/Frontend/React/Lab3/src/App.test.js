import { render, screen, fireEvent, within } from '@testing-library/react';
import App from './App';

// Test Cart icon displays 0 initially
test('Initial value of cart count is 0: ', () => {
  render(<App />);
  const text = screen.getByText('0');
  expect(text).toBeInTheDocument();
});

test('Cart value increments when + button is clicked: ', () => {
  render(<App />);
  const productCards = screen.getAllByTestId('product-card');
  const incrementButton = within(productCards[0]).getByText('+');
  const valueElement = screen.getByTestId('cart-icon');
  const initialValue = parseInt(valueElement.textContent, 10);
  fireEvent.click(incrementButton);
  expect(valueElement).toHaveTextContent((initialValue+1).toString());
});

test('Cart value decrements when - button is clicked: ', () => {
  render(<App />);
  const productCards = screen.getAllByTestId('product-card');
  const incrementButton = within(productCards[0]).getByText('+');
  const decrementButton = within(productCards[0]).getByText('-');
  const valueElement = screen.getByTestId('cart-icon');
  const initialValue = parseInt(valueElement.textContent, 10);
  for (let i=0;i<10;i++) {
    fireEvent.click(incrementButton);
  }
  fireEvent.click(decrementButton);
  expect(valueElement).toHaveTextContent((initialValue+10-1).toString());
});

test('Rendered cart count does not go below 0: ', () => {
  render(<App />);
  const productCards = screen.getAllByTestId('product-card');
  const decrementButton = within(productCards[0]).getByText('-');
  fireEvent.click(decrementButton);  // try to decrement from 0
  const cartCount = screen.getByText('0');
  expect(cartCount).toBeInTheDocument();
});
