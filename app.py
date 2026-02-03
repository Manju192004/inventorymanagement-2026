from flask import Flask, render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret_key_123" 


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="homedb"
    )



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
        sql = "SELECT * FROM content WHERE Email = %s AND Password = %s"
        cursor.execute(sql, (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['user'] = user['Email']
            session['role'] = user.get('Role', 'User')

            if session['role'] == 'Admin':
                return redirect(url_for('viewproduct'))
            else:
                return redirect(url_for('index'))
        else:
            return "<h1>Invalid Credentials! <a href='/login'>Try again</a></h1>"
            
    return render_template("login.html")

@app.route('/register', methods=['POST'])
def register_logic():
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    #phone = request.form.get('phone')
    password = request.form.get('password')
    
    full_name = f"{fname} {lname}"
    role = 'Admin' if email == 'admin@gmail.com' else 'User'

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO content (Name, Email, Password, Phone, Role) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (full_name, email, password, role))
        conn.commit()
        return redirect(url_for('login_page'))
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        cursor.close()
        conn.close()


@app.route('/viewproduct')
def viewproduct():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Products edukkuroom
    cursor.execute("SELECT * FROM product")
    products = cursor.fetchall()
    
    # Feedbacks edukkuroom (Pudhu lines)
    cursor.execute("SELECT * FROM feedback ORDER BY id DESC")
    feedbacks = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Rendu data-vaiyum HTML-ku anupuroom
    return render_template("viewproduct.html", products=products, feedbacks=feedbacks)

@app.route('/addproducts')
def addproducts():
    return render_template("addproducts.html")

@app.route('/save_product', methods=['POST'])
def save_product():
    product_name = request.form.get('product_name')
    category = request.form.get('category')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    image = request.files['image']

    if image:
        filename = secure_filename(image.filename)
        image.save(os.path.join('static/uploads', filename))
    else:
        filename = "default.jpg"

    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO product (product_name, category, price, quantity, image) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, (product_name, category, price, quantity, filename))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('viewproduct'))

@app.route('/editproduct/<int:id>')
def edit_page(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM product WHERE id=%s", (id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("editproduct.html", product=product)

@app.route('/update_product', methods=['POST'])
def update_product():
    pid = request.form.get('id')
    name = request.form.get('product_name')
    cat = request.form.get('category')
    prc = request.form.get('price')
    qty = request.form.get('quantity')

    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "UPDATE product SET product_name=%s, category=%s, price=%s, quantity=%s WHERE id=%s"
    cursor.execute(sql, (name, cat, prc, qty, pid))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('viewproduct'))

@app.route('/deleteproduct/<int:id>')
def delete_product(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM product WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('viewproduct'))



@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM product LIMIT 8")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", products=products)

@app.route('/cart')
def cart(pid=None):
    return render_template('cart.html')

  
@app.route('/billing')
def billing():
    return render_template('billing.html')

@app.route('/review') # User intha URL-ku thaan povaanga
def review_page():
    return render_template('feedback.html') # Unga file peyar sariyaa irukanum



@app.route('/save_feedback', methods=['POST'])
def save_feedback():
    rating = request.form.get('rating')
    description = request.form.get('description')

    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO feedback (rating, description) VALUES (%s, %s)"
    cursor.execute(sql, (rating, description))
    conn.commit()
    cursor.close()
    conn.close()
    
    # JavaScript-ku success message anupuroom
    return {"status": "success"}


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)