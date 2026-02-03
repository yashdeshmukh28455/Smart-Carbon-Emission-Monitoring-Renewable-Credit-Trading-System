from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.emission import Emission
from models.emission_factor import EmissionFactor
from services.emission_calculator import EmissionCalculator
from utils.calibration import SensorCalibration

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
    
    Supports RAW sensor data OR pre-calculated values.
    
    Expected payload (one of):
    1. Raw Hardware Data:
    {
        "raw_current_volts": 2.65,  # ACS712 output
        "raw_co2_ppm": 450,         # MH-Z19C output
        "duration_seconds": 300     # Measurement interval (default 300s)
    }
    
    2. Direct Values (Legacy/Simulated):
    {
        "electricity_kwh": 5.2,
        "combustion_ppm": 450
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        electricity_kwh = 0.0
        combustion_ppm = 0.0
        
        # --- PATH 1: Raw Sensor Data Processing ---
        if 'raw_current_volts' in data:
            raw_volts = float(data['raw_current_volts'])
            duration_sec = float(data.get('duration_seconds', 300)) # Default 5 mins
            duration_hours = duration_sec / 3600.0
            
            # 1. Calibrate Voltage -> Amps
            amps = SensorCalibration.calibrate_current(raw_volts)
            
            # 2. Convert Amps -> Watts
            watts = SensorCalibration.amps_to_power(amps)
            
            # 3. Convert Watts -> kWh
            electricity_kwh = SensorCalibration.power_to_kwh(watts, duration_hours)
            
        elif 'electricity_kwh' in data:
            # Legacy/Direct input path
            electricity_kwh = float(data['electricity_kwh'])
            
        # --- PATH 2: CO2 Sensor Processing ---
        if 'raw_co2_ppm' in data:
            raw_ppm = float(data['raw_co2_ppm'])
            # Calibrate PPM (baseline correction)
            combustion_ppm = SensorCalibration.calibrate_co2_ppm(raw_ppm)
            
        elif 'combustion_ppm' in data:
             # Legacy/Direct input path
            combustion_ppm = float(data['combustion_ppm'])
            
        # Validate data integrity
        if electricity_kwh < 0 or combustion_ppm < 0:
             return jsonify({'error': 'Negative values not allowed'}), 400

        # Fetch dynamic emission factors
        factor_model = EmissionFactor(db)
        current_factors = factor_model.get_current_factors()

        # Calculate CO2 emissions using rule-based calculator
        emissions = EmissionCalculator.calculate_total_co2(
            electricity_kwh, 
            combustion_ppm, 
            factors=current_factors
        )
        
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
            'processed_data': {
                'electricity_kwh': electricity_kwh,
                'combustion_ppm': combustion_ppm
            },
            'calculated_emissions': emissions
        }), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@iot_bp.route('/calculation-method', methods=['GET'])
def get_calculation_method():
    """Get explanation of emission calculation methodology"""
    # Create temp instance to fetch factors (no db access here in route definition, need to fix design or just use default explain)
    # Ideally should pass db-fetched factors. For now, create a new EmissionCalculator method that doesn't need instances if possible,
    # or just use default.
    return jsonify(EmissionCalculator.explain_calculation()), 200
