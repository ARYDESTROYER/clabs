import React, {useState} from 'react';
import './App.css';
import Footer from './components/Footer';
import Header from './components/Header';
import CartIcon from './components/CartIcon';
import ProductCard from './components/ProductCard';
import products from './productList'

function App() {
  const [cartCount, setCartCount] = useState(0);

  const incrementCart = () => setCartCount(cartCount+1);
  const decrementCart = () => setCartCount(cartCount>0?cartCount-1:0);

  return (
    <div className="App">
      <Header />
        <main>
          <div className="product-container">
            {products.map((product) => (
              <div key={product.id}>
                  <ProductCard product={product} incrementCart={incrementCart} decrementCart={decrementCart} />
              </div>
            ))}
          </div>
        </main>
        <CartIcon itemCount={cartCount}/>
      <Footer />
    </div>
  );
}

export default App;
