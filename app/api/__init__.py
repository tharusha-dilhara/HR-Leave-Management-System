# app/__init__.py
from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    # Load environment variables from .env file
    load_dotenv()
    
    app = Flask(__name__)
    
    # Import and register blueprints
    from .api.chat import chat_bp
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    
    print("✅ Flask App created and Blueprints registered.")
    
    return app