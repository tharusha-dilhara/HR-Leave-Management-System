from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    # Load environment variables from .env file
    load_dotenv()
    
    # මෙම පේළිය මගින් 'app' variable එක නිර්මාණය කරයි
    app = Flask(__name__)
    
    # SECRET_KEY එක config කිරීම
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "a_default_secret_key_for_development")
    
    # Import and register blueprints
    from .api.chat import chat_bp
    from .auth.routes import auth_bp
    
    # 'app' variable එක දැන් register_blueprint සඳහා භාවිතා කරයි
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    print("✅ Flask App created and Blueprints registered.")
    
    return app