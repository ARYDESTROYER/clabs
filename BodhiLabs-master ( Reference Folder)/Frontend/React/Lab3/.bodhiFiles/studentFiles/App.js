import React from 'react';
import './App.css';
import Footer from './components/Footer';
import Header from './components/Header';
import CartIcon from './components/CartIcon';
import ProductCard from './components/ProductCard';
import products from './productList'

function App() {
  // Write the logic for maintaining and updating cart value

  // end logic code here
  // don't change any code in the below lines except the ProductCard and CartIcon component code
  // CartIcon has a prop named itemCount, how can you modify it according to your usecase?
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
        <CartIcon/>
      <Footer />
    </div>
  );
}

export default App;
