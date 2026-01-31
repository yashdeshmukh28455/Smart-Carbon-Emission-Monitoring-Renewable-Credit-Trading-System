from datetime import datetime, timedelta
from bson import ObjectId
import uuid

class Credit:
    """Credit model for renewable energy carbon credits"""
    
    def __init__(self, db):
        self.collection = db.credits
        # Create indexes
        self.collection.create_index([('user_id', 1), ('status', 1)])
        self.collection.create_index('expiry_date')
    
    def purchase_credit(self, user_id, credit_type, amount_kg_co2):
        """
        Purchase renewable energy credits
        
        Args:
            user_id: User ID
            credit_type: 'solar', 'wind', or 'bio'
            amount_kg_co2: Amount of CO2 to offset in kg
        
        Returns:
            credit_id
        """
        credit_doc = {
            'user_id': ObjectId(user_id),
            'credit_type': credit_type,
            'amount_kg_co2': amount_kg_co2,
            'purchase_date': datetime.utcnow(),
            'expiry_date': datetime.utcnow() + timedelta(days=365),  # Valid for 1 year
            'status': 'active',
            'transaction_id': str(uuid.uuid4())
        }
        
        result = self.collection.insert_one(credit_doc)
        return str(result.inserted_id)
    
    def get_active_credits(self, user_id):
        """Get all active (non-expired) credits for a user"""
        now = datetime.utcnow()
        
        credits = self.collection.find({
            'user_id': ObjectId(user_id),
            'status': 'active',
            'expiry_date': {'$gte': now}
        }).sort('purchase_date', -1)
        
        results = []
        for c in credits:
            results.append({
                'id': str(c['_id']),
                'credit_type': c['credit_type'],
                'amount_kg_co2': c['amount_kg_co2'],
                'purchase_date': c['purchase_date'].isoformat(),
                'expiry_date': c['expiry_date'].isoformat(),
                'transaction_id': c['transaction_id'],
                'days_remaining': (c['expiry_date'] - now).days
            })
        
        return results
    
    def get_total_active_credits(self, user_id):
        """Get total amount of active credits"""
        now = datetime.utcnow()
        
        pipeline = [
            {'$match': {
                'user_id': ObjectId(user_id),
                'status': 'active',
                'expiry_date': {'$gte': now}
            }},
            {'$group': {
                '_id': None,
                'total_offset_kg': {'$sum': '$amount_kg_co2'}
            }}
        ]
        
        result = list(self.collection.aggregate(pipeline))
        
        if result:
            return round(result[0]['total_offset_kg'], 2)
        return 0
    
    def get_credit_history(self, user_id):
        """Get all credit purchase history"""
        credits = self.collection.find({
            'user_id': ObjectId(user_id)
        }).sort('purchase_date', -1)
        
        results = []
        now = datetime.utcnow()
        
        for c in credits:
            is_expired = c['expiry_date'] < now
            results.append({
                'id': str(c['_id']),
                'credit_type': c['credit_type'],
                'amount_kg_co2': c['amount_kg_co2'],
                'purchase_date': c['purchase_date'].isoformat(),
                'expiry_date': c['expiry_date'].isoformat(),
                'transaction_id': c['transaction_id'],
                'status': 'expired' if is_expired else c['status']
            })
        
        return results
    
    def expire_old_credits(self):
        """Mark expired credits (background job)"""
        now = datetime.utcnow()
        
        result = self.collection.update_many(
            {
                'status': 'active',
                'expiry_date': {'$lt': now}
            },
            {'$set': {'status': 'expired'}}
        )
        
        return result.modified_count
