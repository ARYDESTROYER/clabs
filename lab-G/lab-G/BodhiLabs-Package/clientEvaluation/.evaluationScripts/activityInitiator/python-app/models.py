"""
Database models for the ecommerce application
"""
import sqlite3
import os
from datetime import datetime

DATABASE_PATH = os.environ.get('DATABASE_PATH', '/app/data/ecommerce.db')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with schema"""
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            is_admin INTEGER DEFAULT 0,
            secret_flag TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT,
            image_url TEXT,
            stock INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Reviews table (VULNERABLE - stores unsanitized HTML)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            rating INTEGER NOT NULL,
            review_text TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Shopping cart table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # Page access tracking (for FLAG1)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS page_access (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page TEXT NOT NULL,
            accessed_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def create_admin_user(password):
    """Create admin user with secret flag"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO users (username, password, email, is_admin, secret_flag)
            VALUES (?, ?, ?, 1, '')
        ''', ('admin', password, 'admin@techstore.local'))
        conn.commit()
    except sqlite3.IntegrityError:
        # Admin already exists
        pass
    finally:
        conn.close()

def track_page_access(page):
    """Track page access for FLAG1"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO page_access (page) VALUES (?)', (page,))
    conn.commit()
    conn.close()

def check_recon_complete():
    """Check if all required pages have been accessed"""
    required_pages = ['home', 'products', 'cart', 'reviews']
    conn = get_db()
    cursor = conn.cursor()

    accessed_pages = set()
    cursor.execute('SELECT DISTINCT page FROM page_access')
    for row in cursor.fetchall():
        accessed_pages.add(row[0])

    conn.close()
    return all(page in accessed_pages for page in required_pages)
