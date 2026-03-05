"""
Vulnerable Ecommerce Application for Lab-G
Contains intentional XSS vulnerability in product reviews
"""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
import os
import sqlite3
from functools import wraps
from datetime import datetime
import models
import flag_generator

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'vuln3r4bl3_s3cr3t')

# Admin credentials
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'SecureAdminPass2025!')

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            return "Access Denied: Admin Only", 403
        return f(*args, **kwargs)
    return decorated_function

def sanitize_review(text):
    """
    INTENTIONALLY WEAK SANITIZATION
    Only removes <script> tags but allows event handlers
    This is the vulnerability students should exploit
    """
    sanitized = text.replace('<script>', '', ).replace('</script>', '', )
    sanitized = sanitized.replace('<SCRIPT>', '', ).replace('</SCRIPT>', '', )
    return sanitized

@app.route('/')
def index():
    """Home page - Product catalog"""
    models.track_page_access('home')

    conn = models.get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY created_at DESC LIMIT 12')
    products = cursor.fetchall()
    conn.close()

    # Check if reconnaissance is complete for FLAG1
    if models.check_recon_complete():
        flag1 = flag_generator.generate_flag1()
    else:
        flag1 = None

    return render_template('index.html', products=products, flag1=flag1)

@app.route('/products')
def products():
    """All products page"""
    models.track_page_access('products')

    conn = models.get_db()
    cursor = conn.cursor()

    category = request.args.get('category')
    if category:
        cursor.execute('SELECT * FROM products WHERE category = ? ORDER BY name', (category,))
    else:
        cursor.execute('SELECT * FROM products ORDER BY category, name')

    products = cursor.fetchall()

    # Get unique categories
    cursor.execute('SELECT DISTINCT category FROM products ORDER BY category')
    categories = [row[0] for row in cursor.fetchall()]

    conn.close()

    return render_template('products.html', products=products, categories=categories, selected_category=category)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page with reviews"""
    conn = models.get_db()
    cursor = conn.cursor()

    # Get product
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()

    if not product:
        return "Product not found", 404

    # Get reviews (VULNERABLE - no HTML escaping)
    cursor.execute('''
        SELECT r.*, u.username
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.product_id = ?
        ORDER BY r.created_at DESC
    ''', (product_id,))
    reviews = cursor.fetchall()

    conn.close()

    return render_template('product.html', product=product, reviews=reviews)

@app.route('/product/<int:product_id>/review', methods=['POST'])
@login_required
def submit_review(product_id):
    """Submit product review - VULNERABLE TO XSS"""
    rating = request.form.get('rating', 5)
    review_text = request.form.get('review_text', '')

    if not review_text:
        return redirect(url_for('product_detail', product_id=product_id))

    # INTENTIONALLY WEAK SANITIZATION
    sanitized_review = sanitize_review(review_text)

    conn = models.get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO reviews (product_id, user_id, username, rating, review_text)
        VALUES (?, ?, ?, ?, ?)
    ''', (product_id, session['user_id'], session['username'], rating, sanitized_review))

    conn.commit()
    conn.close()

    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/reviews')
def all_reviews():
    """All reviews page - This is where XSS triggers for victim"""
    models.track_page_access('reviews')

    conn = models.get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT r.*, p.name as product_name, p.image_url
        FROM reviews r
        JOIN products p ON r.product_id = p.id
        ORDER BY r.created_at DESC
    ''')
    reviews = cursor.fetchall()

    conn.close()

    return render_template('reviews.html', reviews=reviews)

@app.route('/cart')
@login_required
def cart():
    """Shopping cart page"""
    models.track_page_access('cart')

    conn = models.get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT c.*, p.name, p.price, p.image_url, (c.quantity * p.price) as subtotal
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (session['user_id'],))
    cart_items = cursor.fetchall()

    total = sum(item['subtotal'] for item in cart_items)

    conn.close()

    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """Add product to cart"""
    quantity = int(request.form.get('quantity', 1))

    conn = models.get_db()
    cursor = conn.cursor()

    # Check if item already in cart
    cursor.execute('SELECT * FROM cart WHERE user_id = ? AND product_id = ?',
                   (session['user_id'], product_id))
    existing = cursor.fetchone()

    if existing:
        cursor.execute('UPDATE cart SET quantity = quantity + ? WHERE user_id = ? AND product_id = ?',
                       (quantity, session['user_id'], product_id))
    else:
        cursor.execute('INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)',
                       (session['user_id'], product_id, quantity))

    conn.commit()
    conn.close()

    return redirect(url_for('cart'))

@app.route('/cart/remove/<int:cart_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_id):
    """Remove item from cart"""
    conn = models.get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cart WHERE id = ? AND user_id = ?', (cart_id, session['user_id']))
    conn.commit()
    conn.close()

    return redirect(url_for('cart'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = models.get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = bool(user['is_admin'])

            next_url = request.args.get('next', url_for('index'))
            return redirect(next_url)
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        conn = models.get_db()
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                           (username, password, email))
            conn.commit()

            # Auto-login
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = False

            conn.close()
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('register.html', error="Username already exists")

    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard - shows all reviews"""
    conn = models.get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT r.*, p.name as product_name
        FROM reviews r
        JOIN products p ON r.product_id = p.id
        ORDER BY r.created_at DESC
    ''')
    reviews = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) as total_users FROM users WHERE is_admin = 0')
    user_count = cursor.fetchone()['total_users']

    cursor.execute('SELECT COUNT(*) as total_reviews FROM reviews')
    review_count = cursor.fetchone()['total_reviews']

    cursor.execute('SELECT COUNT(*) as total_products FROM products')
    product_count = cursor.fetchone()['total_products']

    conn.close()

    return render_template('admin.html', reviews=reviews,
                           user_count=user_count,
                           review_count=review_count,
                           product_count=product_count)

@app.route('/api/admin/profile')
@admin_required
def admin_profile_api():
    """Admin profile API - Contains FLAG4"""
    # Update admin's secret flag
    flag4 = flag_generator.generate_flag4()

    conn = models.get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET secret_flag = ? WHERE username = ?', (flag4, 'admin'))
    conn.commit()

    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    return jsonify({
        'username': user['username'],
        'email': user['email'],
        'isAdmin': bool(user['is_admin']),
        'secretFlag': user['secret_flag']
    })

@app.route('/api/zap-report', methods=['POST'])
def zap_report_trigger():
    """Triggered when ZAP report is generated - FLAG2"""
    flag2 = flag_generator.generate_flag2()

    # Save flag to labDirectory
    try:
        with open('/home/labDirectory/flag2.txt', 'w') as f:
            f.write(flag2)
    except:
        pass

    return jsonify({'status': 'success', 'flag': flag2})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

# ============================================================================
# EXPLOIT SERVER ROUTES (Integrated from standalone exploit-server)
# ============================================================================

def init_exploit_db():
    """Initialize exploit database"""
    conn = models.get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exfiltrated_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flag TEXT,
            data TEXT,
            source_ip TEXT,
            user_agent TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

@app.route('/exploit-dashboard')
@app.route('/dashboard')
def exploit_dashboard():
    """Hacker-themed dashboard showing captured flags (port 30000/dashboard)"""
    conn = models.get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM exfiltrated_data
        ORDER BY timestamp DESC
        LIMIT 50
    ''')
    captures = cursor.fetchall()

    conn.close()

    return render_template('exploit_dashboard.html', captures=captures)

@app.route('/exfil', methods=['GET', 'POST'])
def exfiltrate():
    """
    Exfiltration endpoint - receives data from XSS payload
    Triggers FLAG3 when first called
    """
    # Get data from request
    if request.method == 'POST':
        data = request.get_json() or {}
        flag = data.get('flag', '')
    else:
        flag = request.args.get('flag', '')
        data = dict(request.args)

    source_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', '')

    # Store in database
    conn = models.get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO exfiltrated_data (flag, data, source_ip, user_agent)
        VALUES (?, ?, ?, ?)
    ''', (flag, str(data), source_ip, user_agent))

    conn.commit()
    conn.close()

    # Write to labDirectory for grading
    if flag:
        try:
            os.makedirs('/home/labDirectory', exist_ok=True)
            with open('/home/labDirectory/exfiltrated-flag.txt', 'w') as f:
                f.write(flag)
        except Exception as e:
            print(f"Error writing to labDirectory: {e}")

        # Trigger FLAG3 (first exfiltration attempt)
        try:
            flag3 = flag_generator.generate_flag3()
            print(f"FLAG3 triggered: {flag3}")
        except Exception as e:
            print(f"Error generating FLAG3: {e}")

    print(f"[EXFILTRATION] Flag: {flag}, IP: {source_ip}")

    # Return success
    return jsonify({'status': 'success', 'message': 'Data received'}), 200

@app.route('/test')
def test():
    """Test endpoint to verify server is accessible"""
    return jsonify({
        'status': 'online',
        'message': 'Server is running',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/captures')
def get_captures():
    """API endpoint to get captured data"""
    conn = models.get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM exfiltrated_data
        ORDER BY timestamp DESC
        LIMIT 50
    ''')
    captures = cursor.fetchall()

    conn.close()

    return jsonify([dict(row) for row in captures])

@app.route('/clear-captures', methods=['POST'])
def clear_data():
    """Clear all captured data"""
    conn = models.get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM exfiltrated_data')
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': 'All data cleared'})

# ============================================================================

if __name__ == '__main__':
    # Initialize database and create admin
    models.init_db()
    models.create_admin_user(ADMIN_PASSWORD)
    init_exploit_db()

    # Run app on port 30000 (not 5000)
    app.run(host='0.0.0.0', port=30000, debug=False)
