from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config

# Import db and models
from models import db

# Import blueprint registration function
from routes import register_blueprints


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # PRODUCTION CORS CONFIGURATION
    # Restricts access to only your frontend domain
    CORS(app,
         origins=[
             "http://localhost:*",                          # Local development (any port)
             "http://127.0.0.1:*",                          # Local development
             "https://medicafrica-frontend.vercel.app",     # Your production frontend
             "https://*.vercel.app"                         # Vercel preview deployments
         ],
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=True)

    JWTManager(app)

    # Register all blueprints at once
    register_blueprints(app)

    # Health check
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Hospital API is running',
            'version': '1.0.0'
        }), 200

    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'Hospital Check-In API',
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth/*',
                'appointments': '/api/appointments/*',
                'queue': '/api/queue/*',
                'news': '/api/news/*'
            }
        }), 200

    # Create tables
    with app.app_context():
        db.create_all()
        print("✓ Database tables created!")

    return app


# Create app instance at module level for Gunicorn
app = create_app()

if __name__ == '__main__':
    app.run()