from flask import Flask, render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from flask import jsonify
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret_key_123" 


def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
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
            session['user_id'] = user['id']  # Intha line romba mukkiyam!
            session['role'] = user.get('Role', 'User')


            if session['role'] == 'Admin':
                return redirect(url_for('viewproduct'))
            else:
                return redirect(url_for('index'))
        else:
            return "<h1>Invalid Credentials! <a href='/login'>Try again</a></h1>"
            
    return render_template("login.html")

@app.route('/register')
def register_page():
    return render_template("register.html")

@app.route('/register', methods=['POST'])
def register_logic():
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    
    full_name = f"{fname} {lname}"
    role = 'Admin' if email == 'admin@gmail.com' else 'User'

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO content (Name, Email, Password, Phone, Role) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (full_name, email, password,phone, role))
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
    
    # 1. Products-ah eppovum pola edukkuroom
    cursor.execute("SELECT * FROM product")
    products = cursor.fetchall()
    
    # 2. Feedbacks edukkuroom (JOIN use panni Names-ah edukkuroom)
    # feedback table-la irukra user_id vechi content table-la irukra Name-ah link panrom
    # feedback table-la irukra product_id vechi product table-la irukra product_name-ah link panrom
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


# Intha mari maathunga
@app.route('/review')
@app.route('/review/<int:pid>')
def review_page(pid=None):
    # Sidebar-la irunthu vantha pid None-ah irukkum, card-la irunthu vantha ID irukkum
    return render_template('feedback.html', product_id=pid)


@app.route('/save_feedback', methods=['POST'])
def save_feedback():
    try:
        # 1. HTML Form-la irundhu data-vai edukkurom
        pid = request.form.get('product_id')
        rating = request.form.get('rating')
        description = request.form.get('description')
        
        # 2. Login-la save panna user_id-ah inga edukkurom
        uid = session.get('user_id')

        # User login pannala na error kaatum
        if not uid:
            return jsonify({"status": "error", "message": "User not logged in! Please login first."})

        # 3. Sidebar vazhiyaa vandha product_id empty-ah irukkum
        # MySQL-la integer column-ku empty string set aagathu, so None (NULL) nu maathuroom
        if pid == '' or pid == 'None' or pid is None:
            final_pid = None
        else:
            final_pid = int(pid)

        # 4. Database-la save panrom
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Inga uid kattiyaayam pass pannanum (appo thaan yar feedback nu store aagum)
        sql = "INSERT INTO feedback (product_id, user_id, rating, description) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (final_pid, uid, rating, description))
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "message": "Feedback saved successfully!"})

    except Exception as e:
        print(f"Error: {str(e)}") # Terminal-la error-ah check panna
        return jsonify({"status": "error", "message": str(e)})


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)

    