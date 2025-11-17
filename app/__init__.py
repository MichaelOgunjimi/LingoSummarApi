from config import Config
from flask import Flask, g
from flask_cors import CORS
from pymongo import MongoClient

# Initialize MongoDB client
mongo_client = None
mongo_db = None


def get_db():
    """Get database connection for the current request context."""
    if 'db' not in g:
        g.db = mongo_db
    return g.db


def create_app(config_class=Config):
    # Create the Flask application
    app = Flask(__name__)

    # Load configurations from the config class
    app.config.from_object(config_class)

    # Setup CORS - allow all origins in development, specific in production
    if app.config.get('DEBUG', False):
        # Development: Allow all origins
        CORS(app, resources={r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": False
        }})
    else:
        # Production: Specific origins only
        CORS(app, resources={r"/api/*": {
            "origins": [
                "https://www.lingosummar.com",
                "https://lingosummar.netlify.app",
                "https://lingosummar.com"
            ]
        }})

    # Initialize MongoDB with PyMongo
    global mongo_client, mongo_db
    try:
        mongo_client = MongoClient(
            app.config['MONGODB_URI'],
            serverSelectionTimeoutMS=5000
        )
        # Test connection
        mongo_client.admin.command('ping')
        # Get database name from URI or use default
        mongo_db = mongo_client.get_default_database()
        app.logger.info(f"Connected to MongoDB database: {mongo_db.name}")
    except Exception as e:
        app.logger.error(f"Could not connect to MongoDB: {e}")
        mongo_db = None

    # Make db available to routes via get_db()
    @app.teardown_appcontext
    def close_db(error):
        """Close database connection at the end of request."""
        if error:
            app.logger.error(f"Request error: {error}")

    # Import and register the blueprint for API routes
    from app.routes.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    # Disable strict slashes globally, making trailing slash optional for all routes
    app.url_map.strict_slashes = False

    return app
