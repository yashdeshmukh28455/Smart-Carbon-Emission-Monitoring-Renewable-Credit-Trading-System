from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.emission import Emission
from services.emission_calculator import EmissionCalculator

iot_bp = Blueprint('iot', __name__)

db = None

def init_iot(database):
    global db
    db = database

@iot_bp.route('/emission', methods=['POST'])
@jwt_required()
def receive_emission_data():
    """
    Receive emission data from IoT devices (ESP32 + sensors)
    
    Expected payload:
    {
        "electricity_kwh": 5.2,
        "combustion_ppm": 450
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if 'electricity_kwh' not in data or 'combustion_ppm' not in data:
            return jsonify({'error': 'electricity_kwh and combustion_ppm required'}), 400
        
        electricity_kwh = float(data['electricity_kwh'])
        combustion_ppm = float(data['combustion_ppm'])
        
        # Calculate CO2 emissions using rule-based calculator
        emissions = EmissionCalculator.calculate_total_co2(electricity_kwh, combustion_ppm)
        
        # Store in database
        emission_model = Emission(db)
        emission_id = emission_model.add_emission(
            user_id=user_id,
            electricity_kwh=electricity_kwh,
            electricity_co2_kg=emissions['electricity_co2_kg'],
            combustion_ppm=combustion_ppm,
            combustion_co2_kg=emissions['combustion_co2_kg'],
            source='iot'
        )
        
        return jsonify({
            'success': True,
            'message': 'Emission data recorded',
            'emission_id': emission_id,
            'calculated_emissions': emissions
        }), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@iot_bp.route('/calculation-method', methods=['GET'])
def get_calculation_method():
    """Get explanation of emission calculation methodology"""
    return jsonify(EmissionCalculator.explain_calculation()), 200
