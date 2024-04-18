from flask import Flask
from flask_cors import CORS
from flask_mongoengine import MongoEngine
from config import Config

# Initialize the database
db = MongoEngine()


def create_app(config_class=Config):
    # Create the Flask application
    app = Flask(__name__)

    # Load configurations from the config class
    app.config.from_object(config_class)

    # Setup CORS with specific origins allowed
    CORS(app, resources={r"/api/*": {"origins": ["https://www.lingosummar.com", "https://lingosummar.netlify.app"]}})

    # Initialize MongoDB with Flask
    db.init_app(app)

    # Test database connection in the application context
    with app.app_context():
        try:
            db.connection.admin.command('ping')
        except Exception as e:
            app.logger.error(f"Could not connect to MongoDB: {e}")

    # Import and register the blueprint for API routes
    from app.routes.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    # Disable strict slashes globally, making trailing slash optional for all routes
    app.url_map.strict_slashes = False

    return app
