from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import mysql.connector
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret_key_123" 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root", # password 'root' nu iruntha anga mathikonga
        database="homedb"
    )

# --- AUTH ROUTES ---
@app.route('/')
def home():
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM content WHERE Email = %s AND Password = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['user'] = user['Email']
            session['user_id'] = user['id']
            session['role'] = user['Role'] if user['Role'] else 'User'
            return redirect(url_for('viewproduct' if session['role'] == 'Admin' else 'index'))
        else:
            return "<h1>Invalid Credentials! <a href='/login'>Try again</a></h1>"
            
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register_logic():
    if request.method == 'GET':
        return render_template("register.html")
        
    fname, lname = request.form.get('fname'), request.form.get('lname')
    email, phone, password = request.form.get('email'), request.form.get('phone'), request.form.get('password')
    full_name = f"{fname} {lname}"
    role = 'Admin' if email == 'admin@gmail.com' else 'User'

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO content (Name, Email, Password, Phone, Role) VALUES (%s, %s, %s, %s, %s)", 
                     (full_name, email, password, phone, role))
        conn.commit()
        return redirect(url_for('login_page'))
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        cursor.close()
        conn.close()

# --- ADMIN ROUTES (Product Management) ---
@app.route('/viewproduct')
def viewproduct():
    if 'user' not in session: return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM product")
    products = cursor.fetchall()
    
    sql = """
        SELECT f.*, c.Name as user_name, p.product_name 
        FROM feedback f
        LEFT JOIN content c ON f.user_id = c.id
        LEFT JOIN product p ON f.product_id = p.id
        ORDER BY f.id DESC
    """
    cursor.execute(sql)
    feedbacks = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template("viewproduct.html", products=products, feedbacks=feedbacks)

@app.route('/save_product', methods=['POST'])
def save_product():
    product_name, category = request.form.get('product_name'), request.form.get('category')
    price, quantity = request.form.get('price'), request.form.get('quantity')
    image = request.files['image']

    filename = secure_filename(image.filename) if image else "default.jpg"
    if image:
        upload_path = os.path.join(BASE_DIR, 'static/uploads')
        if not os.path.exists(upload_path): os.makedirs(upload_path)
        image.save(os.path.join(upload_path, filename))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO product (product_name, category, price, quantity, image) VALUES (%s, %s, %s, %s, %s)", 
                 (product_name, category, price, quantity, filename))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('viewproduct'))

@app.route('/editproduct/<int:id>')
def edit_page(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM product WHERE id = %s", (id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("editproduct.html", product=product)

@app.route('/deleteproduct/<int:id>')
def delete_product(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM feedback WHERE product_id=%s", (id,))
        cursor.execute("DELETE FROM product WHERE id=%s", (id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('viewproduct'))

# --- USER ROUTES (Shopping) ---
@app.route('/index')
def index():
    if 'user_id' not in session: return redirect(url_for('login_page'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM product")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/product/<int:id>')
def product_detail(id):
    if 'user_id' not in session: return redirect(url_for('login_page'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM product WHERE id = %s", (id,))
    product = cursor.fetchone()

    # JOIN feedback with content to get the user's name
    query = """
        SELECT f.*, c.Name 
        FROM feedback f 
        JOIN content c ON f.user_id = c.id 
        WHERE f.product_id = %s 
        ORDER BY f.id DESC
    """
    cursor.execute(query, (id,))
    feedbacks = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('product_detail.html', product=product, feedbacks=feedbacks)



@app.route('/submit_feedback/<int:pid>', methods=['POST'])
def submit_feedback(pid):
    if 'user_id' not in session: return redirect(url_for('login_page'))
    description = request.form.get('description')
    user_id = session.get('user_id')
    if description:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO feedback (user_id, product_id, description) VALUES (%s, %s, %s)", (user_id, pid, description))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for('product_detail', id=pid))

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Login required"})

    try:
        data = request.get_json()
        user_id = session['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Database-la data save aagum
        sql = "INSERT INTO orders (order_id, user_id, item_name, qty, total_price) VALUES (%s, %s, %s, %s, %s)"
        values = (data['order_id'], user_id, data['item_name'], data['qty'], data['total_price'])
        
        cursor.execute(sql, values)
        conn.commit()
        
        cursor.close()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)})



@app.route('/my_orders')
def my_orders():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Orders-ai fetch pannuvom (Unga table name 'purchase' nu vechikitta)
    user_id = int(session['user_id']) # String-ah number-ah mathurom
    cursor.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY id DESC", (user_id,))
    
    #cursor.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY id DESC", (user_id,))
    orders = cursor.fetchall()
    
    # Feedbacks-aiyum fetch pannuvom
    cursor.execute("SELECT * FROM feedback WHERE user_id = %s ORDER BY id DESC", (user_id,))
    feedbacks = cursor.fetchall()


    
    cursor.close()
    conn.close()
    
    return render_template('my_orders.html', orders=orders, feedbacks=feedbacks)

@app.route('/cart')
def cart(): return render_template('cart.html')

@app.route('/billing')
def billing():
    return render_template('billing.html')


@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True)