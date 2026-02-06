from pymongo import MongoClient
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/carbon_db')
client = MongoClient(MONGO_URI)
db = client.get_database()

email = "admin@carbon.com"
new_password = "admin123"

# Hash password
password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

result = db.admins.update_one(
    {'email': email},
    {'$set': {'password_hash': password_hash}}
)

if result.matched_count > 0:
    print(f"✅ Password for {email} reset to '{new_password}'")
else:
    print(f"❌ User {email} not found. Creating new admin...")
    admin_doc = {
        'email': email,
        'password_hash': password_hash,
        'name': 'Master Admin',
        'role': 'super_admin'
    }
    db.admins.insert_one(admin_doc)
    print(f"✅ Created new admin {email} with password '{new_password}'")
