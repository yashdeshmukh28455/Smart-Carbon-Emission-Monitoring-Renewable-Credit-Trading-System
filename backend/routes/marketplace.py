from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.marketplace_service import MarketplaceService

marketplace_bp = Blueprint('marketplace', __name__)

db = None

def init_marketplace(database):
    global db
    db = database

@marketplace_bp.route('/listings', methods=['GET'])
def get_listings():
    """Get all active marketplace listings with optional filters"""
    try:
        filters = {}
        if request.args.get('credit_type'):
            filters['credit_type'] = request.args.get('credit_type')
        if request.args.get('max_price'):
            filters['max_price'] = request.args.get('max_price')
        if request.args.get('min_amount'):
            filters['min_amount'] = request.args.get('min_amount')
        
        marketplace_service = MarketplaceService(db)
        listings = marketplace_service.get_marketplace_listings(filters)
        
        return jsonify({
            'success': True,
            'listings': listings,
            'count': len(listings)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@marketplace_bp.route('/listing/<listing_id>', methods=['GET'])
def get_listing_details(listing_id):
    """Get detailed information about a specific listing"""
    try:
        marketplace_service = MarketplaceService(db)
        listing = marketplace_service.get_listing_details(listing_id)
        
        return jsonify({
            'success': True,
            'listing': listing
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@marketplace_bp.route('/sell', methods=['POST'])
@jwt_required()
def create_sell_listing():
    """
    Create a new sell listing
    
    Expected payload:
    {
        "credit_type": "solar",
        "amount_kg_co2": 100,
        "price_per_kg": 0.15
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        required_fields = ['credit_type', 'amount_kg_co2', 'price_per_kg']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        marketplace_service = MarketplaceService(db)
        listing = marketplace_service.create_sell_listing(
            user_id,
            data['credit_type'],
            float(data['amount_kg_co2']),
            float(data['price_per_kg'])
        )
        
        return jsonify({
            'success': True,
            'message': 'Listing created successfully',
            'listing': listing
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@marketplace_bp.route('/buy/<listing_id>', methods=['POST'])
@jwt_required()
def initiate_purchase(listing_id):
    """
    Initiate a purchase from marketplace
    
    Expected payload:
    {
        "amount_kg_co2": 50,
        "payment_method": "upi"
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'amount_kg_co2' not in data or 'payment_method' not in data:
            return jsonify({'error': 'amount_kg_co2 and payment_method required'}), 400
        
        marketplace_service = MarketplaceService(db)
        payment = marketplace_service.initiate_purchase(
            user_id,
            listing_id,
            float(data['amount_kg_co2']),
            data['payment_method']
        )
        
        return jsonify({
            'success': True,
            'message': 'Payment initiated',
            'payment': payment
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@marketplace_bp.route('/payment/<payment_id>/complete', methods=['POST'])
@jwt_required()
def complete_payment(payment_id):
    """
    Complete a payment (simulate payment verification)
    
    Expected payload:
    {
        "payment_reference": "UPI123456789"
    }
    """
    try:
        data = request.get_json()
        payment_reference = data.get('payment_reference')
        
        marketplace_service = MarketplaceService(db)
        result = marketplace_service.complete_purchase(payment_id, payment_reference)
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@marketplace_bp.route('/listing/<listing_id>', methods=['DELETE'])
@jwt_required()
def cancel_listing(listing_id):
    """Cancel a user's listing"""
    try:
        user_id = get_jwt_identity()
        
        marketplace_service = MarketplaceService(db)
        listing = marketplace_service.cancel_listing(listing_id, user_id)
        
        return jsonify({
            'success': True,
            'message': 'Listing cancelled successfully',
            'listing': listing
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@marketplace_bp.route('/my-listings', methods=['GET'])
@jwt_required()
def get_my_listings():
    """Get all listings created by the current user"""
    try:
        user_id = get_jwt_identity()
        
        marketplace_service = MarketplaceService(db)
        listings = marketplace_service.get_user_listings(user_id)
        
        return jsonify({
            'success': True,
            'listings': listings,
            'count': len(listings)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@marketplace_bp.route('/my-trades', methods=['GET'])
@jwt_required()
def get_my_trades():
    """Get user's complete trading history"""
    try:
        user_id = get_jwt_identity()
        
        marketplace_service = MarketplaceService(db)
        trades = marketplace_service.get_user_trades(user_id)
        
        return jsonify({
            'success': True,
            'trades': trades
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
