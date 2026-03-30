import sys, os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app():
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )

    # Secret key
    app.secret_key = (
        os.environ.get("SESSION_SECRET")
        or os.environ.get("FLASK_SECRET_KEY")
        or "nirix-secret-key"
    )

    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = "web.login"
    login_manager.login_message_category = "info"

    # ==========================
    # IMPORT ALL MODELS HERE
    # ==========================
    from app.models.user import User
    from app.models.role import Role
    from app.models.vehicle import Vehicle
    from app.models.log import Log
    from app.models.test import Test   # <-- contains FK to Vehicle

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ==========================
    # REGISTER BLUEPRINTS
    # ==========================
    from app.api import api_bp
    from app.web import web_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(web_bp)

    # ==========================
    # CREATE TABLES
    # ==========================
    with app.app_context():
        db.create_all()  # NOW all models are known

    return app
