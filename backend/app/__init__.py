from flask import Flask, send_from_directory
from flask_cors import CORS
import logging
import os

from app.config import Config
from app.api import api_bp


def create_app(config=Config):
    """Application factory pattern."""
    app = Flask(__name__, static_folder=config.FRONTEND_BUILD_PATH, static_url_path='/')
    
    # Configure CORS
    CORS(app)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Serve React frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        """Serve the React app."""
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
    
    return app
