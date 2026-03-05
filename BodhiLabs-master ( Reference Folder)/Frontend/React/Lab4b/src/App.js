import React from 'react';
import './App.css';
import Footer from './components/Footer';
import Header from './components/Header';
import CartIcon from './components/CartIcon';
import Reset from './components/Reset';
import ProductCard from './components/ProductCard';
import products from './productList'

function App() {
  return (
    <div className="App">
      <Header />
        <main>
          <div className="product-container">
            {products.map((product) => (
              <div key={product.id}>
                  <ProductCard product={product} />
              </div>
            ))}
          </div>
        </main>
        <CartIcon />
        <Reset />
      <Footer />
    </div>
  );
}

export default App;
