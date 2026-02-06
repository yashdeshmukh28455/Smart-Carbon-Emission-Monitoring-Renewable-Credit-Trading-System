from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.admin import Admin
from models.company import Company
from models.payment import Payment
from models.marketplace_listing import MarketplaceListing
from functools import wraps

admin_bp = Blueprint('admin', __name__)

db = None

def init_admin(database):
    global db
    db = database

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt_identity()
            # simple check - in prod check role in db
            # Here we assume admin tokens are issued with a specific identity prefix or just verify existence
            # For now, we'll fetch user and check if in admin collection
            admin_model = Admin(db)
            if not admin_model.get_admin_by_id(claims):
                return jsonify({'error': 'Admin access required'}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

@admin_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
            
        admin_model = Admin(db)
        admin = admin_model.verify_password(data['email'], data['password'])
        
        if not admin:
            return jsonify({'error': 'Invalid admin credentials'}), 401
            
        access_token = create_access_token(identity=str(admin['_id']))
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'admin': {
                'id': str(admin['_id']),
                'email': admin['email'],
                'name': admin['name']
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/setup', methods=['POST'])
def setup_first_admin():
    """Temporary endpoint to create first admin"""
    try:
        data = request.get_json()
        admin_model = Admin(db)
        
        # Check if any admin exists
        if db.admins.count_documents({}) > 0:
             return jsonify({'error': 'Admin already initialized'}), 403
             
        admin_id = admin_model.create_admin(data['email'], data['password'], data.get('name', 'Admin'))
        return jsonify({'success': True, 'admin_id': admin_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/companies', methods=['GET', 'POST'])
@admin_required()
def manage_companies():
    try:
        company_model = Company(db)
        
        if request.method == 'POST':
            data = request.get_json()
            company_id = company_model.create_company(
                data['name'], data['email'], data.get('description',''), data.get('contact_person','')
            )
            if not company_id:
                return jsonify({'error': 'Company email already exists'}), 400
            return jsonify({'success': True, 'company_id': company_id})
            
        else:
            companies = company_model.get_all_companies()
            # Convert ObjectIds to strings
            for c in companies:
                c['_id'] = str(c['_id'])
                if c.get('approved_at'): c['approved_at'] = c['approved_at'].isoformat()
                c['created_at'] = c['created_at'].isoformat()
            return jsonify({'success': True, 'companies': companies})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/companies/<company_id>/approve', methods=['PUT'])
@admin_required()
def approve_company(company_id):
    try:
        company_model = Company(db)
        company = company_model.approve_company(company_id)
        if not company:
             return jsonify({'error': 'Company not found'}), 404
             
        return jsonify({'success': True, 'message': 'Company approved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/trades', methods=['GET'])
@admin_required()
def get_all_trades():
    try:
        payment_model = Payment(db)
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        trades = payment_model.get_all_payments(limit, offset)
        return jsonify({'success': True, 'trades': trades})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/stats', methods=['GET'])
@admin_required()
def get_stats():
    try:
        # Simple aggregation stats
        total_users = db.users.count_documents({})
        total_companies = db.companies.count_documents({})
        
        pipeline = [
            {'$match': {'status': 'completed'}},
            {'$group': {'_id': None, 'total_carbon': {'$sum': '$amount_kg_co2'}, 'total_volume': {'$sum': '$total_amount'}}}
        ]
        trade_stats = list(db.payments.aggregate(pipeline))
        
        stats = {
            'total_users': total_users,
            'total_companies': total_companies,
            'total_carbon_traded': trade_stats[0]['total_carbon'] if trade_stats else 0,
            'total_volume_traded': trade_stats[0]['total_volume'] if trade_stats else 0
        }
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
