from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # ✅ ADD THIS
from dotenv import load_dotenv
import os
from flask_login import LoginManager
from app.extensions import db
from app.models.users import User 
from app.routes.model_routes import api_bp
from app.routes.main_routes import main as main_routes
from app.routes.api_routes import api as api_routes

# Create login manager and migrate globally
login_manager = LoginManager()
migrate = Migrate()  # ✅ ADD THIS

def create_app():
    # Load environment variables
    load_dotenv()

    # Create Flask app
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)  # ✅ REGISTER FLASK-MIGRATE HERE
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(main_routes)
    app.register_blueprint(api_routes)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
