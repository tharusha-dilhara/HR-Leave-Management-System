# app/models/user.py
from werkzeug.security import check_password_hash
from app.utils.db import db

class User:
    @staticmethod
    def find_by_username(username):
        return db.users.find_one({"username": username})

    @staticmethod
    def check_password(user_password_hash, password):
        return check_password_hash(user_password_hash, password)