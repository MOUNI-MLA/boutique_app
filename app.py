from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from config import MONGO_URI, SECRET_KEY
from utils.auth import login_required
from flask import Flask
app = Flask(__name__)
app.secret_key = SECRET_KEY

# Database setup
client = MongoClient(MONGO_URI)
db = client.get_database()

# Collections
users = db.users
products = db.products

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = users.find_one({"username": username})
        if existing_user:
            return "Username already exists"

        hashed_pw = generate_password_hash(password)
        users.insert_one({
            "username": username,
            "password": hashed_pw
        })
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    all_products = products.find()
    return render_template('dashboard.html', products=all_products)

@app.route('/add-product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = float(request.form['price'])

        products.insert_one({
            "name": name,
            "category": category,
            "price": price
        })
        return redirect(url_for('dashboard'))
    return render_template('add_product.html')

@app.route('/delete/<product_id>')
@login_required
def delete_product(product_id):
    products.delete_one({"_id": ObjectId(product_id)})
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True)
