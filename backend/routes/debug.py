from flask import Blueprint, jsonify
from models.user import User
from models.emission import Emission
from services.ai_predictor import AIPredictor
import traceback

debug_bp = Blueprint('debug', __name__)

db = None

def init_debug(database):
    global db
    db = database

@debug_bp.route('/test-predictions', methods=['GET'])
def test_predictions():
    """Test predictions without authentication for debugging"""
    try:
        # Get first user
        user_model = User(db)
        users = list(db.users.find())
        
        if not users:
            return jsonify({'error': 'No users found'}), 404
        
        user = users[0]
        user_id = str(user['_id'])
        
        # Test predictions
        emission_model = Emission(db)
        predictor = AIPredictor(emission_model)
        
        result = predictor.get_prediction_with_warning(user_id, user)
        
        return jsonify({
            'debug': True,
            'user_email': user.get('email'),
            'user_id': user_id,
            'result': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc()
        }), 500
