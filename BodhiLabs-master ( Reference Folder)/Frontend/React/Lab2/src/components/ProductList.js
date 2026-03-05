import React from 'react';
import ProductCard from './ProductCard';

function ProductList({products}) {
    return (
        <div className="product-container" data-testid="product-list">
            {products.map((product) => (
                <div key={product.id}>
                    <ProductCard product={product}/>
                </div>
            ))}
        </div>
    );
}

export default ProductList;