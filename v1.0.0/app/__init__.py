# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.extensions import db
from dotenv import load_dotenv
import os

def create_app():
    # Load environment variables from .env file
    load_dotenv()

    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)

    # Import and register blueprints here to avoid circular import issues
    from app.routes.main_routes import main as main_routes
    from app.routes.api_routes import api as api_routes

    app.register_blueprint(main_routes)
    app.register_blueprint(api_routes)

    return app
