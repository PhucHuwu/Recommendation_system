from flask import Blueprint

# Import all route blueprints
from app.routes.auth import auth_bp
from app.routes.anime import anime_bp
from app.routes.rating import rating_bp
from app.routes.recommendation import recommendation_bp
from app.routes.history import history_bp
from app.routes.admin import admin_bp
from app.routes.search import search_bp


def register_blueprints(app):
    """Register all blueprints with the app"""
    api_prefix = app.config.get('API_PREFIX', '/api')
    
    app.register_blueprint(auth_bp, url_prefix=f'{api_prefix}/auth')
    app.register_blueprint(anime_bp, url_prefix=f'{api_prefix}/anime')
    app.register_blueprint(rating_bp, url_prefix=f'{api_prefix}/rating')
    app.register_blueprint(recommendation_bp, url_prefix=f'{api_prefix}/recommendation')
    app.register_blueprint(history_bp, url_prefix=f'{api_prefix}/history')
    app.register_blueprint(admin_bp, url_prefix=f'{api_prefix}/admin')
    app.register_blueprint(search_bp, url_prefix=f'{api_prefix}/search')
