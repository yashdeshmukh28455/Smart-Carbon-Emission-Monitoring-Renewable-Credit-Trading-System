from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from config import Config
import os

# Import route blueprints
from routes.auth import auth_bp, init_auth
from routes.household import household_bp, init_household
from routes.iot import iot_bp, init_iot
from routes.emissions import emissions_bp, init_emissions
from routes.credits import credits_bp, init_credits
from routes.predictions import predictions_bp, init_predictions
from routes.demo import demo_bp, init_demo
from routes.debug import debug_bp, init_debug
from routes.marketplace import marketplace_bp, init_marketplace

def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    
    # Configuration
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.JWT_ACCESS_TOKEN_EXPIRES
    
    # Enable CORS for frontend with proper configuration
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Handle OPTIONS requests (CORS preflight) - don't require JWT
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            return '', 200
    
    # Connect to MongoDB
    try:
        client = MongoClient(Config.MONGO_URI)
        db = client.get_database()
        print(f"✅ Connected to MongoDB: {db.name}")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise
    
    # Initialize route modules with database
    init_auth(db)
    init_household(db)
    init_iot(db)
    init_emissions(db)
    init_credits(db)
    init_predictions(db)
    init_demo(db)
    init_debug(db)
    init_marketplace(db)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(household_bp, url_prefix='/api/household')
    app.register_blueprint(iot_bp, url_prefix='/api/iot')
    app.register_blueprint(emissions_bp, url_prefix='/api/emissions')
    app.register_blueprint(credits_bp, url_prefix='/api/credits')
    app.register_blueprint(predictions_bp, url_prefix='/api/predictions')
    app.register_blueprint(demo_bp, url_prefix='/api/demo')
    app.register_blueprint(debug_bp, url_prefix='/api/debug')
    app.register_blueprint(marketplace_bp, url_prefix='/api/marketplace')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Smart Carbon Trading Platform API',
            'version': '1.0.0'
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'Smart Carbon Emission Monitoring & Renewable Credit Trading Platform',
            'api_version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'household': '/api/household',
                'iot': '/api/iot',
                'emissions': '/api/emissions',
                'credits': '/api/credits',
                'predictions': '/api/predictions',
                'demo': '/api/demo',
                'health': '/api/health'
            },
            'documentation': 'See README.md for full API documentation'
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Starting Smart Carbon Trading Platform API...")
    print("📡 Server running on http://localhost:5000")
    print("📚 API Documentation: http://localhost:5000")
    # Force reload trigger
    app.run(debug=True, host='0.0.0.0', port=5000)
