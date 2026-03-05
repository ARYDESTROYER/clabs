import React from 'react';
import products from '../productList';

function ProductList() {
    return (
        // write your code inside the <div> </div>
        // Should contain all the products
        <div data-testid="product-list">
            <h2>Product List</h2>
            <ul>
                {products.map((product) => (
                    <li key={product.id}>
                        {product.name} - ${product.price}
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default ProductList;