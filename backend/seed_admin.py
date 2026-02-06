import requests
import sys

URL = "http://localhost:5000/api/admin/setup"

data = {
    "email": "admin@carbon.com",
    "password": "admin123",
    "name": "Master Admin"
}

try:
    response = requests.post(URL, json=data)
    if response.status_code == 200:
        print("✅ Admin seeded successfully!")
        print(response.json())
    elif response.status_code == 403:
         print("⚠️ Admin already exists.")
    else:
        print(f"❌ Failed: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
