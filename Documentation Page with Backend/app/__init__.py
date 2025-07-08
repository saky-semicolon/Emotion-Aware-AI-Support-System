from flask import Flask
from .extensions import db
from main_routes import main

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')  # relative to app/

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.register_blueprint(main)

    return app
