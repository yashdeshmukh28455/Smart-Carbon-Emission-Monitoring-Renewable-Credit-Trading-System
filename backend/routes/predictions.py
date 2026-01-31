from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.emission import Emission
from services.ai_predictor import AIPredictor

predictions_bp = Blueprint('predictions', __name__)

db = None

def init_predictions(database):
    global db
    db = database

@predictions_bp.route('/forecast', methods=['GET'])
@jwt_required()
def get_forecast():
    """Get AI-based emission predictions"""
    try:
        user_id = get_jwt_identity()
        days_ahead = int(request.args.get('days', 7))
        
        print(f"[PREDICTIONS] Forecast request for user: {user_id}, days: {days_ahead}")
        
        # Get user data
        user_model = User(db)
        user = user_model.get_user_by_id(user_id)
        
        if not user:
            print(f"[PREDICTIONS] User not found: {user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        print(f"[PREDICTIONS] User found: {user.get('email')}")
        
        # Get predictions
        emission_model = Emission(db)
        predictor = AIPredictor(emission_model)
        
        result = predictor.get_prediction_with_warning(user_id, user)
        
        print(f"[PREDICTIONS] Prediction result: success={result.get('success')}")
        
        # Return appropriate status code based on result
        if result.get('success'):
            return jsonify(result), 200
        else:
            # Return 200 with success=False for insufficient data
            return jsonify(result), 200
        
    except ValueError as e:
        print(f"[PREDICTIONS] ValueError: {e}")
        return jsonify({
            'success': False,
            'error': 'Invalid parameter',
            'message': str(e)
        }), 400
    except Exception as e:
        print(f"[PREDICTIONS] Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@predictions_bp.route('/train', methods=['POST'])
@jwt_required()
def train_model():
    """Train prediction model on user's data"""
    try:
        user_id = get_jwt_identity()
        
        # Get user data
        user_model = User(db)
        user = user_model.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Train model
        emission_model = Emission(db)
        predictor = AIPredictor(emission_model)
        
        result = predictor.train_model(user_id, user)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@predictions_bp.route('/explain', methods=['GET'])
@jwt_required()
def explain_model():
    """Get AI model explanation"""
    try:
        user_id = get_jwt_identity()
        
        # Get user data
        user_model = User(db)
        user = user_model.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Train model first if needed
        emission_model = Emission(db)
        predictor = AIPredictor(emission_model)
        predictor.train_model(user_id, user)
        
        explanation = predictor.explain_model()
        
        return jsonify(explanation), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
