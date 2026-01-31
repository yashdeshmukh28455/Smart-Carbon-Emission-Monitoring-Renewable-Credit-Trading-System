from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User
from pymongo import MongoClient
from config import Config

auth_bp = Blueprint('auth', __name__)

# Database connection (will be initialized in app.py)
db = None

def init_auth(database):
    global db
    db = database

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user with household information"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'area_sqm', 'occupants']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create user
        user_model = User(db)
        household_data = {
            'area_sqm': float(data['area_sqm']),
            'occupants': int(data['occupants'])
        }
        
        user_id = user_model.create_user(
            email=data['email'],
            password=data['password'],
            household_data=household_data
        )
        
        if not user_id:
            return jsonify({'error': 'Email already exists'}), 409
        
        # Get created user
        user = user_model.get_user_by_id(user_id)
        
        # Create JWT token
        access_token = create_access_token(identity=user_id)
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user_id': user_id,
            'email': user['email'],
            'household': user['household'],
            'access_token': access_token
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        
        if 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password required'}), 400
        
        user_model = User(db)
        user = user_model.verify_password(data['email'], data['password'])
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create JWT token
        access_token = create_access_token(identity=str(user['_id']))
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user_id': str(user['_id']),
            'email': user['email'],
            'household': user['household'],
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user_model = User(db)
        user = user_model.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user_id': str(user['_id']),
            'email': user['email'],
            'household': user['household'],
            'created_at': user['created_at'].isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
