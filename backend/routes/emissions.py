from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.emission import Emission
from models.user import User
from models.credit import Credit
from services.carbon_limit_service import CarbonLimitService

emissions_bp = Blueprint('emissions', __name__)

db = None

def init_emissions(database):
    global db
    db = database

@emissions_bp.route('/daily', methods=['GET'])
@jwt_required()
def get_daily_emissions():
    """Get daily aggregated emissions"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 30))
        
        emission_model = Emission(db)
        emissions = emission_model.get_emissions_by_period(user_id, 'daily', limit)
        
        return jsonify({
            'period': 'daily',
            'emissions': emissions
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@emissions_bp.route('/monthly', methods=['GET'])
@jwt_required()
def get_monthly_emissions():
    """Get monthly aggregated emissions"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 12))
        
        emission_model = Emission(db)
        emissions = emission_model.get_emissions_by_period(user_id, 'monthly', limit)
        
        return jsonify({
            'period': 'monthly',
            'emissions': emissions
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@emissions_bp.route('/yearly', methods=['GET'])
@jwt_required()
def get_yearly_emissions():
    """Get yearly aggregated emissions"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 5))
        
        emission_model = Emission(db)
        emissions = emission_model.get_emissions_by_period(user_id, 'yearly', limit)
        
        return jsonify({
            'period': 'yearly',
            'emissions': emissions
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@emissions_bp.route('/status', methods=['GET'])
@jwt_required()
def get_emission_status():
    """Get comprehensive carbon status"""
    try:
        user_id = get_jwt_identity()
        
        # Initialize services
        user_model = User(db)
        emission_model = Emission(db)
        credit_model = Credit(db)
        
        carbon_service = CarbonLimitService(user_model, emission_model, credit_model)
        status = carbon_service.get_user_status(user_id)
        
        if not status:
            return jsonify({'error': 'User not found'}), 404
        
        # Add status message and color
        status['status_message'] = carbon_service.get_status_message(
            status['status'], 
            status['percentage_used']
        )
        status['status_color'] = carbon_service.get_status_color(status['status'])
        
        # Add credit recommendations if exceeded
        if status['needs_credits']:
            recommendations = carbon_service.calculate_required_credits(status['excess_co2_kg'])
            status['credit_recommendations'] = recommendations
        
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@emissions_bp.route('/total', methods=['GET'])
@jwt_required()
def get_total_emissions():
    """Get total emissions for current year"""
    try:
        user_id = get_jwt_identity()
        
        emission_model = Emission(db)
        total = emission_model.get_total_emissions(user_id)
        
        return jsonify(total), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
