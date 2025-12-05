import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from app.config import config

# MongoDB client (will be initialized in create_app)
mongo_client = None
db = None


def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])
    JWTManager(app)
    
    # Initialize MongoDB
    global mongo_client, db
    mongo_client = MongoClient(app.config['MONGODB_URI'])
    db = mongo_client[app.config['MONGODB_DB']]
    
    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'API is running'}
    
    return app


def get_db():
    """Get database instance"""
    return db
