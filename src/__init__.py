""" Initialize the Flask app. """
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

cors = CORS()

jwt = JWTManager()
bcrypt = Bcrypt()

# Import all models here to ensure they are registered with SQLAlchemy
from src.models.shopping_list import ShoppingList
from src.models.user import User
from src.models.category import Category
from src.models.item import Item


def create_app(config_class="src.config.DevelopmentConfig") -> Flask:
    """
    Create a Flask app with the given configuration class.
    The default configuration class is DevelopmentConfig.
    """
    load_dotenv()

    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config.from_object(config_class)

    from src.models import db
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    register_extensions(app)
    register_routes(app)
    register_handlers(app)

    create_db_tables(app)
        
    return app


def create_db_tables(app):
    from src.models import db
    with app.app_context():
        db.create_all()

def register_extensions(app: Flask) -> None:
    """Register the extensions for the Flask app"""
    cors.init_app(app, resources={r"/*": {"origins": "*"}})


def register_routes(app: Flask) -> None:
    """Import and register the routes for the Flask app"""

    # Import the routes here to avoid circular imports
    from src.controllers.users import users_bp
    from src.controllers.shopping_lists import shopping_lists_bp
    from src.controllers.categories import categories_bp
    from src.controllers.items import items_bp
    from src.controllers.auth import auth_bp
    from src.controllers.admin import admin_bp
    from src.controllers.home import home_bp

    # Register the blueprints in the app
    app.register_blueprint(users_bp)
    app.register_blueprint(shopping_lists_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(home_bp)


def register_handlers(app: Flask) -> None:
    """Register the error handlers for the Flask app."""
    app.errorhandler(404)(lambda e: (
        {"error": "Not found", "message": str(e)}, 404
    )
    )
    app.errorhandler(400)(
        lambda e: (
            {"error": "Bad request", "message": str(e)}, 400
        )
    )
