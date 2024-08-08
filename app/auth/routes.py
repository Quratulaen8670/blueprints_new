from flask import Blueprint, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import re
from pymongo import MongoClient
from .decorators import admin_required
from flask_jwt_extended import create_access_token

auth = Blueprint('auth', __name__)


# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['employee_database']
users = db['users']


@auth.route('/')
def index():
    return jsonify({"message": "Welcome! Please use /auth/signup or /auth/signin"})


@auth.route('/SignIn', methods=['POST'])
def signin():
    data = request.json
    username_or_email = data.get('username')
    password = data.get('password')

    user = users.find_one({'$or': [{'username': username_or_email}, {'email': username_or_email}]})
    if user and check_password_hash(user['password'], password):
        access_token = create_access_token(identity=user['username'])
        response = {
            "message": "Logged in successfully.",
            "access_token": access_token,
            "username": user['username'],
            "is_admin": user.get('is_admin', False)
        }
        return jsonify(response)
    else:
        return jsonify({"error": "Invalid username/email or password."}), 401



@auth.route('/SignUp', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('Password')
    confirm_password = data.get('ConfirmPassword')

    # Set is_admin to True if the username is 'admin'
    is_admin = username.lower() == 'admin'

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


