from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User

household_bp = Blueprint('household', __name__)

db = None

def init_household(database):
    global db
    db = database

@household_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_household_profile():
    """Get household profile"""
    try:
        user_id = get_jwt_identity()
        user_model = User(db)
        user = user_model.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'household': user['household']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@household_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_household_profile():
    """Update household profile and recalculate carbon limit"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'area_sqm' not in data or 'occupants' not in data:
            return jsonify({'error': 'area_sqm and occupants required'}), 400
        
        user_model = User(db)
        new_limit = user_model.update_household(
            user_id,
            float(data['area_sqm']),
            int(data['occupants'])
        )
        
        return jsonify({
            'success': True,
            'message': 'Household profile updated',
            'area_sqm': float(data['area_sqm']),
            'occupants': int(data['occupants']),
            'annual_carbon_limit_kg': new_limit
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@household_bp.route('/limit', methods=['GET'])
@jwt_required()
def get_carbon_limit():
    """Get carbon limit information"""
    try:
        user_id = get_jwt_identity()
        user_model = User(db)
        user = user_model.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'annual_carbon_limit_kg': user['household']['annual_carbon_limit_kg'],
            'area_sqm': user['household']['area_sqm'],
            'occupants': user['household']['occupants']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
