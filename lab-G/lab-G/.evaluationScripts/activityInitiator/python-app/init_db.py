"""
Initialize database with realistic ecommerce products
"""
import os
import sys
import models

# Sample products for electronics ecommerce store
PRODUCTS = [
    {
        'name': 'MacBook Pro 16" M3 Max',
        'description': 'Powerful laptop with M3 Max chip, 36GB RAM, 1TB SSD. Perfect for developers and content creators.',
        'price': 3499.00,
        'category': 'Laptops',
        'image_url': '/static/images/products/macbook.jpg',
        'stock': 15
    },
    {
        'name': 'Dell XPS 15 Developer Edition',
        'description': 'Premium Ubuntu laptop with Intel i7, 32GB RAM, 1TB SSD. Pre-configured for developers.',
        'price': 2299.00,
        'category': 'Laptops',
        'image_url': '/static/images/products/dell-xps.jpg',
        'stock': 22
    },
    {
        'name': 'ThinkPad X1 Carbon Gen 11',
        'description': 'Business ultrabook with Intel i7, 16GB RAM, 512GB SSD. Legendary keyboard and durability.',
        'price': 1899.00,
        'category': 'Laptops',
        'image_url': '/static/images/products/thinkpad.jpg',
        'stock': 30
    },
    {
        'name': 'iPhone 15 Pro Max',
        'description': 'Latest flagship with A17 Pro chip, titanium design, 256GB storage, advanced camera system.',
        'price': 1199.00,
        'category': 'Smartphones',
        'image_url': '/static/images/products/iphone15.jpg',
        'stock': 50
    },
    {
        'name': 'Samsung Galaxy S24 Ultra',
        'description': 'Premium Android phone with S Pen, 12GB RAM, 512GB storage, 200MP camera.',
        'price': 1299.00,
        'category': 'Smartphones',
        'image_url': '/static/images/products/galaxy-s24.jpg',
        'stock': 45
    },
    {
        'name': 'Google Pixel 8 Pro',
        'description': 'Pure Android experience with best-in-class AI features, 12GB RAM, exceptional camera.',
        'price': 999.00,
        'category': 'Smartphones',
        'image_url': '/static/images/products/pixel8.jpg',
        'stock': 35
    },
    {
        'name': 'iPad Pro 12.9" M2',
        'description': 'Professional tablet with M2 chip, 256GB storage, Liquid Retina XDR display.',
        'price': 1099.00,
        'category': 'Tablets',
        'image_url': '/static/images/products/ipad-pro.jpg',
        'stock': 28
    },
    {
        'name': 'Samsung Galaxy Tab S9 Ultra',
        'description': 'Premium Android tablet with S Pen, 14.6" AMOLED display, 12GB RAM.',
        'price': 1199.00,
        'category': 'Tablets',
        'image_url': '/static/images/products/tab-s9.jpg',
        'stock': 20
    },
    {
        'name': 'Sony WH-1000XM5',
        'description': 'Industry-leading noise cancelling headphones with 30hr battery, premium sound quality.',
        'price': 399.00,
        'category': 'Audio',
        'image_url': '/static/images/products/sony-xm5.jpg',
        'stock': 60
    },
    {
        'name': 'AirPods Pro 2nd Gen',
        'description': 'Premium wireless earbuds with active noise cancellation, spatial audio, MagSafe charging.',
        'price': 249.00,
        'category': 'Audio',
        'image_url': '/static/images/products/airpods-pro.jpg',
        'stock': 75
    },
    {
        'name': 'Logitech MX Master 3S',
        'description': 'Ergonomic wireless mouse for productivity, 8K DPI sensor, quiet clicks, USB-C charging.',
        'price': 99.00,
        'category': 'Accessories',
        'image_url': '/static/images/products/mx-master.jpg',
        'stock': 100
    },
    {
        'name': 'Keychron K8 Pro Mechanical Keyboard',
        'description': 'Hot-swappable wireless mechanical keyboard with RGB, Mac and Windows compatible.',
        'price': 109.00,
        'category': 'Accessories',
        'image_url': '/static/images/products/keychron.jpg',
        'stock': 85
    },
    {
        'name': 'LG 27" 4K UHD Monitor',
        'description': '27-inch IPS display with 4K resolution, USB-C connectivity, HDR10 support.',
        'price': 449.00,
        'category': 'Monitors',
        'image_url': '/static/images/products/lg-monitor.jpg',
        'stock': 40
    },
    {
        'name': 'Dell UltraSharp 32" 4K',
        'description': 'Professional 32" 4K monitor with 99% sRGB, USB-C hub, height-adjustable stand.',
        'price': 699.00,
        'category': 'Monitors',
        'image_url': '/static/images/products/dell-monitor.jpg',
        'stock': 25
    },
    {
        'name': 'Anker PowerCore 26800mAh',
        'description': 'High-capacity portable charger with dual USB ports, charges iPhone 11 times.',
        'price': 65.00,
        'category': 'Accessories',
        'image_url': '/static/images/products/anker-battery.jpg',
        'stock': 120
    }
]

def main():
    """Initialize database"""
    print("Initializing database...")

    # Create schema
    models.init_db()
    print("✓ Database schema created")

    # Create admin user
    admin_password = os.environ.get('ADMIN_PASSWORD', 'SecureAdminPass2025!')
    models.create_admin_user(admin_password)
    print("✓ Admin user created")

    # Insert products
    conn = models.get_db()
    cursor = conn.cursor()

    for product in PRODUCTS:
        cursor.execute('''
            INSERT INTO products (name, description, price, category, image_url, stock)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            product['name'],
            product['description'],
            product['price'],
            product['category'],
            product['image_url'],
            product['stock']
        ))

    conn.commit()
    print(f"✓ Inserted {len(PRODUCTS)} products")

    # Create sample reviews
    sample_reviews = [
        (1, 1, 'johndoe', 5, 'Amazing laptop! The M3 Max is incredibly fast for video editing.'),
        (1, 1, 'alice_dev', 5, 'Best development machine I\'ve ever owned. Compiles are lightning fast!'),
        (2, 1, 'bob_linux', 4, 'Great Linux laptop but wish the battery life was better.'),
        (4, 1, 'sarahtech', 5, 'The camera on this phone is absolutely incredible!'),
        (9, 1, 'musiclover', 5, 'Best noise cancelling headphones on the market. Worth every penny.'),
    ]

    for product_id, user_id, username, rating, review_text in sample_reviews:
        cursor.execute('''
            INSERT INTO reviews (product_id, user_id, username, rating, review_text)
            VALUES (?, ?, ?, ?, ?)
        ''', (product_id, user_id, username, rating, review_text))

    conn.commit()
    print(f"✓ Inserted {len(sample_reviews)} sample reviews")

    conn.close()
    print("\n✓ Database initialization complete!")

if __name__ == '__main__':
    main()
