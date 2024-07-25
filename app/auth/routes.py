from flask import Blueprint, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import re
from pymongo import MongoClient

auth = Blueprint('auth', __name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['employee_database']
users = db['users']


@auth.route('/')
def index():
    return jsonify({"message": "Welcome! Please use /auth/signup or /auth/signin"})


@auth.route('/SignIn', methods=['GET', 'POST'])
def signin():
    data = request.json
    username_or_email = data.get('username')
    password = data.get('password')

    user = users.find_one({'$or': [{'username': username_or_email}, {'email': username_or_email}]})
    if user and check_password_hash(user['password'], password):
        session['username'] = user['username']
        session['is_admin'] = user.get('is_admin', False)
        response = {
            "message": "Logged in successfully.",
            "username": user['username'],
            "is_admin": user.get('is_admin', False)
        }
        return jsonify(response)
    else:
        return jsonify({"error": "Invalid username/email or password."}), 401


@auth.route('/SignUp', methods=['GET', 'POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('Password')
    confirm_password = data.get('ConfirmPassword')
    is_admin = username == 'admin'

    if not username or not email or not password or not confirm_password:
        return jsonify({"error": "All fields are required."}), 400

    if password != confirm_password:
        return jsonify({"error": "Passwords do not match."}), 400

    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        return jsonify({"error": "Invalid email address."}), 400

    if users.find_one({'username': username}):
        return jsonify({"error": "Username already exists."}), 400
    if users.find_one({'email': email}):
        return jsonify({"error": "Email already exists."}), 400

    hashed_password = generate_password_hash(password)
    new_user = {
        'username': username,
        'email': email,
        'password': hashed_password,
        'is_admin': is_admin
    }
    users.insert_one(new_user)
    return jsonify({"message": "Account created successfully. Please log in."})


@auth.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session or not session.get('is_admin', False):
        return jsonify({"error": "You do not have permission to access this page."}), 403
    return jsonify({"message": "Welcome to the admin dashboard."})
