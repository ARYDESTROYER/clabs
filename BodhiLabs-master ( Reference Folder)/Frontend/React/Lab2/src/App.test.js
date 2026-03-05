import { render, screen, within } from '@testing-library/react';
import ProductCard from './components/ProductCard';
import ProductList from './components/ProductList';
import products from './testProductList'

test('ProductList rendered with ProductCard for each product: ', () => {
  // Render ProductList with sample products
  render(<ProductList products={products} />);

  // Check if the product list container is in the document
  const productList = screen.getByTestId('product-list');
  expect(productList).toBeInTheDocument();

  // Check if the correct number of ProductCard components are rendered
  products.forEach((product) => {
    expect(screen.getByText(product.name)).toBeInTheDocument();
    expect(screen.getByText(`Price: ${product.price}`)).toBeInTheDocument();
  });
});

test('Rendered all ProductCard components: ', () => {
  // Render the ProductList component with 50 products
  render(<ProductList products={products} />);

  // Check that exactly 50 product cards are rendered
  const productCards = screen.getAllByRole('heading', { level: 2 });
  expect(productCards).toHaveLength(50);
});

// Pick a random product to check (for example, the product with id 10)
const randomNum = Math.floor(Math.random()*50)+1
const randomProduct = products.find(product => product.id === randomNum);

test('Rendered a random product correctly: ', () => {
  render(<ProductCard product={randomProduct} />);
  
  // Check if the product name is displayed
  const productName = screen.getByText(randomProduct.name);
  expect(productName).toBeInTheDocument();
});

test('Each rendered ProductCard has + and - buttons on them: ', () => {
  render(<ProductCard product={randomProduct} />);

  const productCard = screen.getAllByTestId('product-card')[0];

  const addButton = within(productCard).getByRole('button', { name: '+' });
  const subtractButton = within(productCard).getByRole('button', { name: '-' });
  expect(addButton).toBeInTheDocument();
  expect(subtractButton).toBeInTheDocument();
});
