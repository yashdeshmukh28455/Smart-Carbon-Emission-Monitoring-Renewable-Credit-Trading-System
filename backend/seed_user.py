import requests
import sys

URL = "http://localhost:5000/api/auth/register"

data = {
    "email": "user@carbon.com",
    "password": "user123",
    "area_sqm": 120,
    "occupants": 4
}

try:
    response = requests.post(URL, json=data)
    if response.status_code == 201:
        print("✅ User seeded successfully!")
        print(response.json())
    elif response.status_code == 409:
         print("⚠️ User already exists.")
    else:
        print(f"❌ Failed: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
