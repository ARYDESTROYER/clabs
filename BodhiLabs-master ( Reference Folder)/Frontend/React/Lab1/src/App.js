import React from 'react';
import './App.css';
import Header from './components/Header';
import Footer from './components/Footer';
import ProductList from './components/ProductList';

function App() {
  return (
    <div className="App">
      <Header />
        <main>
          <ProductList/>
        </main>
      <Footer />
    </div>
  );
}

export default App;
