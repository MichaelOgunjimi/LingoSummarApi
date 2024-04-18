from config import Config
from flask import Flask
from flask_cors import CORS
from flask_mongoengine import MongoEngine

db = MongoEngine()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app, resources={r"/api/*": {"origins": ["https://www.api.lingosummar.com", "https://lingosummar.netlify.app/", "https://www.lingosummar.com/"]}})

    # Initialize extensions
    db.init_app(app)

    # Optional: Test database connection
    with app.app_context():
        try:
            # Attempt a simple operation to check connectivity
            db.connection.admin.command('ping')
        except Exception as e:
            app.logger.error(f"Could not connect to MongoDB: {e}")

    # Register blueprints
    from app.routes.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
