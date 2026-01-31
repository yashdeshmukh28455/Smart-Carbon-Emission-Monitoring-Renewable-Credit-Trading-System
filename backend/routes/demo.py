from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.emission import Emission
from utils.demo_data_generator import DemoDataGenerator

demo_bp = Blueprint('demo', __name__)

db = None

def init_demo(database):
    global db
    db = database

@demo_bp.route('/generate-data', methods=['POST'])
@jwt_required()
def generate_demo_data():
    """
    Generate demo emission data
    
    Expected payload:
    {
        "days": 30,
        "pattern": "gradual_increase"  // or "stable" or "random"
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        days = int(data.get('days', 30))
        pattern = data.get('pattern', 'gradual_increase')
        
        emission_model = Emission(db)
        generator = DemoDataGenerator(emission_model)
        
        records_created = generator.generate_emissions(user_id, days, pattern)
        
        return jsonify({
            'success': True,
            'message': f'Generated {records_created} days of demo data',
            'records_created': records_created,
            'pattern': pattern
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@demo_bp.route('/simulate-exceed', methods=['POST'])
@jwt_required()
def simulate_exceed():
    """Generate data that will exceed carbon limit"""
    try:
        user_id = get_jwt_identity()
        
        emission_model = Emission(db)
        generator = DemoDataGenerator(emission_model)
        
        records_created = generator.generate_exceed_scenario(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Generated data to simulate limit exceed scenario',
            'records_created': records_created,
            'note': 'Check your status - you should now be over the carbon limit!'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@demo_bp.route('/simulate-safe', methods=['POST'])
@jwt_required()
def simulate_safe():
    """Generate data that stays within carbon limit"""
    try:
        user_id = get_jwt_identity()
        
        emission_model = Emission(db)
        generator = DemoDataGenerator(emission_model)
        
        records_created = generator.generate_safe_scenario(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Generated data for safe scenario',
            'records_created': records_created,
            'note': 'Your emissions should be within the carbon limit'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
