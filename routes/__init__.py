"""
Routes package initialization
Registers all API blueprints
"""

from routes.auth import auth_bp
from routes.appointments import appointments_bp
from routes.queue import queue_bp
from routes.news import news_bp

# Export all blueprints
__all__ = [
    'auth_bp',
    'appointments_bp',
    'queue_bp',
    'news_bp'
]


def register_blueprints(app):
    """
    Helper function to register all blueprints at once
    Usage: register_blueprints(app)
    """
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(appointments_bp, url_prefix='/api/appointments')
    app.register_blueprint(queue_bp, url_prefix='/api/queue')
    app.register_blueprint(news_bp, url_prefix='/api/news')

    print("✓ All blueprints registered successfully")
