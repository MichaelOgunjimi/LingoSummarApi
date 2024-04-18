import os
from dotenv import load_dotenv

# Get the absolute directory path for config.py
current_dir = os.path.abspath(os.path.dirname(__file__))

# Construct the path to the .env file
dotenv_path = os.path.join(os.path.abspath(current_dir), '.env')

# Load the .env file
load_dotenv(dotenv_path)


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')

    # MongoDB settings
    MONGODB_SETTINGS = {
        'host': os.getenv('MONGODB_URI')
    }

    DEBUG = os.getenv('FLASK_DEBUG', False)  # Default to False if not set
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')  # Default to production if not set
    FLASK_RUN_PORT = os.getenv('FLASK_RUN_PORT', 5000)  # Default to 5000 if not set

    # Dynamically construct the UPLOAD_FOLDER path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

