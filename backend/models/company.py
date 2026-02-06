from bson import ObjectId
from datetime import datetime
import secrets

class Company:
    """Model for external companies selling credits"""
    
    def __init__(self, db):
        self.collection = db.companies
        self.collection.create_index('email', unique=True)
        self.collection.create_index('api_key', unique=True)
    
    def create_company(self, name, email, description, contact_person):
        """
        Register a new company
        """
        if self.collection.find_one({'email': email}):
            return None
            
        api_key = f"sk_live_{secrets.token_hex(16)}"
        
        company_doc = {
            'name': name,
            'email': email,
            'description': description,
            'contact_person': contact_person,
            'status': 'pending',  # pending, approved, suspended
            'api_key': api_key,
            'credits_sold_total': 0.0,
            'revenue_total': 0.0,
            'created_at': datetime.utcnow(),
            'approved_at': None
        }
        
        result = self.collection.insert_one(company_doc)
        return str(result.inserted_id)
        
    def approve_company(self, company_id):
        """Approve a company to start selling"""
        self.collection.update_one(
            {'_id': ObjectId(company_id)},
            {'$set': {
                'status': 'approved',
                'approved_at': datetime.utcnow()
            }}
        )
        return self.get_company_by_id(company_id)
        
    def get_company_by_id(self, company_id):
        return self.collection.find_one({'_id': ObjectId(company_id)})
        
    def get_all_companies(self, status=None):
        query = {}
        if status:
            query['status'] = status
        return list(self.collection.find(query).sort('created_at', -1))
