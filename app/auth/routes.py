# app/auth/routes.py
import os
import jwt
import datetime
from flask import Blueprint, request, jsonify
from app.models.user import User

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    user_data = User.find_by_username(username)

    if not user_data or not User.check_password(user_data['password'], password):
        return jsonify({"message": "Invalid credentials"}), 401

    token = jwt.encode({
        'user_id': user_data['employee_id'],
        'username': user_data['username'],
        'role': user_data['role'],
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }, os.getenv("SECRET_KEY", "default_secret_key_for_dev"), algorithm="HS256")

    return jsonify({
        "message": "Login successful",
        "token": token,
        "role": user_data['role'],
        "username": user_data['username']
    })