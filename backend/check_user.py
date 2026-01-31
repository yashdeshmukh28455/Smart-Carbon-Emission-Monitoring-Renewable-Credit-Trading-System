from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGO_URI)
db = client.get_database()

user = db.users.find_one()
if user:
    print(f"Email: {user.get('email')}")
    print(f"User ID: {user.get('_id')}")
else:
    print("No users found")
