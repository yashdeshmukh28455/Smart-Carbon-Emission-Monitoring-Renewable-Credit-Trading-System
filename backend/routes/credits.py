from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.credit import Credit
from services.credit_service import CreditService

credits_bp = Blueprint('credits', __name__)

db = None

def init_credits(database):
    global db
    db = database

@credits_bp.route('/types', methods=['GET'])
def get_credit_types():
    """Get available credit types"""
    try:
        credit_service = CreditService(None)
        types = credit_service.get_available_credit_types()
        
        return jsonify({
            'credit_types': types
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@credits_bp.route('/purchase', methods=['POST'])
@jwt_required()
def purchase_credits():
    """
    Purchase renewable energy credits
    
    Expected payload:
    {
        "credit_type": "solar",
        "amount_kg_co2": 150.5
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'credit_type' not in data or 'amount_kg_co2' not in data:
            return jsonify({'error': 'credit_type and amount_kg_co2 required'}), 400
        
        credit_model = Credit(db)
        credit_service = CreditService(credit_model)
        
        result = credit_service.purchase_credits(
            user_id,
            data['credit_type'],
            float(data['amount_kg_co2'])
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@credits_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_credits():
    """Get user's active credits"""
    try:
        user_id = get_jwt_identity()
        
        credit_model = Credit(db)
        credit_service = CreditService(credit_model)
        
        summary = credit_service.get_credit_summary(user_id)
        
        return jsonify(summary), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@credits_bp.route('/history', methods=['GET'])
@jwt_required()
def get_credit_history():
    """Get credit purchase history"""
    try:
        user_id = get_jwt_identity()
        
        credit_model = Credit(db)
        history = credit_model.get_credit_history(user_id)
        
        return jsonify({
            'history': history
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
