import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance globally
db = SQLAlchemy()

# Import models and blueprints after db is defined to avoid circular imports
# but before create_app uses them.
from .models import User  # Ensures User model is known to SQLAlchemy via db instance
from .routes import admin_bp

def create_app(config_class=None):
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.urandom(24)
    # For simplicity, using a relative path for SQLite.
    # In a production environment, this would be more robust.
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(admin_bp)

    # Create database tables if they don't exist
    # This is a simple approach for development.
    # For production, migrations (e.g., Flask-Migrate) are recommended.
    with app.app_context():
        # Ensure all models are imported before calling create_all
        # User model is already imported above. If there were more models,
        # they should be imported here or in .models and .models should be imported.
        db.create_all()

    return app
