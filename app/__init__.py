from config import Config
from flask import Flask, g
from flask_cors import CORS
from pymongo import MongoClient
import sys

# Initialize MongoDB client
mongo_client = None
mongo_db = None


def get_db():
    """Get database connection for the current request context."""
    if 'db' not in g:
        g.db = mongo_db
    return g.db


def create_app(config_class=Config):
    print("Starting Flask app initialization...", file=sys.stderr, flush=True)
    
    # Create the Flask application
    app = Flask(__name__)
    print("Flask app instance created", file=sys.stderr, flush=True)

    # Load configurations from the config class
    app.config.from_object(config_class)
    print("Configuration loaded", file=sys.stderr, flush=True)

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
    print("CORS configured", file=sys.stderr, flush=True)

    # Initialize MongoDB with PyMongo - non-blocking
    global mongo_client, mongo_db
    print("Initializing MongoDB connection...", file=sys.stderr, flush=True)
    try:
        # Create client with shorter timeout to avoid hanging
        mongo_client = MongoClient(
            app.config['MONGODB_URI'],
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
            socketTimeoutMS=3000
        )
        print("MongoDB client created, testing connection...", file=sys.stderr, flush=True)
        
        # Test connection with timeout - don't block indefinitely
        mongo_client.admin.command('ping', maxTimeMS=3000)
        
        # Get database name from URI or use default
        mongo_db = mongo_client.get_default_database()
        app.logger.info(f"Connected to MongoDB database: {mongo_db.name}")
        print(f"✓ MongoDB connected: {mongo_db.name}", file=sys.stderr, flush=True)
    except Exception as e:
        app.logger.error(f"Could not connect to MongoDB: {e}")
        print(f"⚠ MongoDB connection failed: {e}", file=sys.stderr, flush=True)
        # Don't block - allow app to start even if MongoDB is unavailable
        mongo_db = None
        mongo_client = None

    # Make db available to routes via get_db()
    @app.teardown_appcontext
    def close_db(error):
        """Close database connection at the end of request."""
        if error:
            app.logger.error(f"Request error: {error}")

    print("Registering blueprints...", file=sys.stderr, flush=True)
    # Import and register the blueprint for API routes
    from app.routes.routes import bp as routes_bp
    app.register_blueprint(routes_bp)
    print("Blueprints registered", file=sys.stderr, flush=True)

    # Disable strict slashes globally, making trailing slash optional for all routes
    app.url_map.strict_slashes = False

    print("✓ Flask app initialization complete", file=sys.stderr, flush=True)
    return app
