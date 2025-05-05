"""
Configuration manager for the Recipe Keeper application.
Loads environment variables securely and provides application configuration.
"""
import os
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class with common settings."""
    # Secret key for secure sessions and CSRF protection
    SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_hex(32)
    
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'recipe_keeper')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
    
    # Maximum file upload size (10MB)
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    
    # Image upload directory
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')
    
    # Allowed image extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Number of salt rounds for password hashing
    BCRYPT_LOG_ROUNDS = 12

class DevelopmentConfig(Config):
    """Configuration for development environment."""
    DEBUG = True
    DEVELOPMENT = True
    ENV = 'development'
    # Additional development-specific settings here

class ProductionConfig(Config):
    """Configuration for production environment."""
    DEBUG = False
    DEVELOPMENT = False
    ENV = 'production'
    
    # In production, ensure SECRET_KEY is set in environment variables
    # and not generated dynamically
    @property
    def SECRET_KEY(self):
        key = os.getenv('SECRET_KEY')
        if not key:
            raise ValueError("SECRET_KEY must be set in environment for production")
        return key
    
    # In production, ensure database password is set
    @property
    def DB_PASSWORD(self):
        password = os.getenv('DB_PASSWORD')
        if not password:
            raise ValueError("DB_PASSWORD must be set in environment for production")
        return password

class TestingConfig(Config):
    """Configuration for testing environment."""
    TESTING = True
    ENV = 'testing'
    # Use a separate database for testing
    DB_NAME = os.getenv('TEST_DB_NAME', 'recipe_keeper_test')
    # Use a fixed secret key for testing
    SECRET_KEY = 'test-secret-key'

# Configuration dictionary to select the appropriate configuration class
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """
    Returns the appropriate configuration based on the environment.
    
    Returns:
        Config: The configuration object for the current environment.
    """
    env = os.getenv('FLASK_ENV', 'default')
    return config.get(env, config['default'])()

# Shortcut to get the database URI
def get_db_uri():
    """
    Returns the database URI for the current environment.
    
    Returns:
        str: The database URI string.
    """
    config_obj = get_config()
    return f"postgresql://{config_obj.DB_USER}:{config_obj.DB_PASSWORD}@{config_obj.DB_HOST}/{config_obj.DB_NAME}"
	
	
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
MAIL_USE_TLS = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
