from pymongo import MongoClient
from datetime import datetime
import bcrypt
from config import Config

class User:
    """User model for authentication and household management"""
    
    def __init__(self, db):
        self.collection = db.users
        # Create indexes
        self.collection.create_index('email', unique=True)
    
    def create_user(self, email, password, household_data):
        """
        Create a new user with household information
        
        Args:
            email: User email
            password: Plain text password (will be hashed)
            household_data: dict with 'area_sqm' and 'occupants'
        
        Returns:
            user_id or None if email exists
        """
        # Check if user exists
        if self.collection.find_one({'email': email}):
            return None
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Calculate annual carbon limit
        annual_limit = self._calculate_carbon_limit(
            household_data['area_sqm'],
            household_data['occupants']
        )
        
        user_doc = {
            'email': email,
            'password_hash': password_hash,
            'household': {
                'area_sqm': household_data['area_sqm'],
                'occupants': household_data['occupants'],
                'annual_carbon_limit_kg': annual_limit
            },
            'created_at': datetime.utcnow()
        }
        
        result = self.collection.insert_one(user_doc)
        return str(result.inserted_id)
    
    def verify_password(self, email, password):
        """Verify user credentials"""
        user = self.collection.find_one({'email': email})
        if not user:
            return None
        
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            return user
        return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        from bson import ObjectId
        return self.collection.find_one({'_id': ObjectId(user_id)})
    
    def get_user_by_email(self, email):
        """Get user by email"""
        return self.collection.find_one({'email': email})
    
    def update_household(self, user_id, area_sqm, occupants):
        """Update household information and recalculate carbon limit"""
        from bson import ObjectId
        
        annual_limit = self._calculate_carbon_limit(area_sqm, occupants)
        
        self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {
                'household.area_sqm': area_sqm,
                'household.occupants': occupants,
                'household.annual_carbon_limit_kg': annual_limit
            }}
        )
        
        return annual_limit
    
    def _calculate_carbon_limit(self, area_sqm, occupants):
        """
        Calculate annual carbon limit based on household size
        Formula: (area * base_per_sqm) + (occupants * per_occupant)
        """
        return (area_sqm * Config.CARBON_LIMIT_BASE_PER_SQM) + \
               (occupants * Config.CARBON_LIMIT_PER_OCCUPANT)
