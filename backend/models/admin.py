from pymongo import MongoClient
from datetime import datetime
import bcrypt

class Admin:
    """Admin model for platform management"""
    
    def __init__(self, db):
        self.collection = db.admins
        # Create indexes
        self.collection.create_index('email', unique=True)
    
    def create_admin(self, email, password, name="Admin"):
        """
        Create a new admin user
        
        Args:
            email: Admin email
            password: Plain text password
            name: Admin name
        
        Returns:
            admin_id or None if email exists
        """
        # Check if admin exists
        if self.collection.find_one({'email': email}):
            return None
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        admin_doc = {
            'email': email,
            'password_hash': password_hash,
            'name': name,
            'role': 'super_admin',
            'created_at': datetime.utcnow()
        }
        
        result = self.collection.insert_one(admin_doc)
        return str(result.inserted_id)
    
    def verify_password(self, email, password):
        """Verify admin credentials"""
        admin = self.collection.find_one({'email': email})
        if not admin:
            return None
        
        if bcrypt.checkpw(password.encode('utf-8'), admin['password_hash']):
            return admin
        return None
    
    def get_admin_by_id(self, admin_id):
        """Get admin by ID"""
        from bson import ObjectId
        return self.collection.find_one({'_id': ObjectId(admin_id)})
