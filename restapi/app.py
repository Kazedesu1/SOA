from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)
DATABASE = 'website.db'

@app.route('/')
def index():
    return render_template('client.html')

@app.route("/searching")
def search_page():
    return render_template("search.html")

@app.route("/cart")
def cart_page():
    return render_template("cart.html")

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# === Dịch vụ đăng ký tài khoản ===
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user (name, email, password) VALUES (?, ?, ?)', (name, email, password))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Đăng ký thành công'}), 201

# === Dịch vụ đăng nhập ===
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM user WHERE email = ? AND password = ?', (email, password)).fetchone()
    conn.close()

    if user:
        return jsonify({'message': 'Đăng nhập thành công'})
    else:
        return jsonify({'message': 'Sai email hoặc mật khẩu'}), 401

# === Dịch vụ tìm kiếm sản phẩm ===
@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('q', '')

    conn = get_db_connection()
    results = conn.execute("SELECT * FROM storages WHERE model LIKE ?", ('%' + keyword + '%',)).fetchall()
    conn.close()

    return jsonify([dict(row) for row in results])

# === Dịch vụ thêm sản phẩm vào giỏ hàng ===
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json
    user_email = data.get('user_email')
    product_id = data.get('product_id')
    purchase_date = data.get('purchase_date')  # YYYY-MM-DD

    conn = get_db_connection()
    conn.execute('INSERT INTO orders (user_email, product_id, purchase_date) VALUES (?, ?, ?)',
                 (user_email, product_id, purchase_date))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Đã thêm vào giỏ hàng'})

# === Dịch vụ thanh toán và giao hàng ===
@app.route('/checkout', methods=['POST'])
def checkout():
    data = request.json
    user_email = data.get('user_email')

    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders WHERE user_email = ?', (user_email,)).fetchall()
    conn.execute('DELETE FROM orders WHERE user_email = ?', (user_email,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Thanh toán thành công và đang giao hàng', 'orders': [dict(row) for row in orders]})

# === Chạy Flask app ===
if __name__ == '__main__':
    app.run(debug=True)
