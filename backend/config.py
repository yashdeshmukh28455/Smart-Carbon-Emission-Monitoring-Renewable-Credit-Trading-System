import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/carbon_platform')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET', 'your_secret_key_change_this')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    
    # Emission Calculation Factors
    EMISSION_FACTOR_KWH = float(os.getenv('EMISSION_FACTOR_KWH', 0.85))  # kg CO2 per kWh
    COMBUSTION_PPM_TO_KG_FACTOR = float(os.getenv('COMBUSTION_PPM_TO_KG_FACTOR', 0.0018))
    
    # Carbon Limit Calculation
    CARBON_LIMIT_BASE_PER_SQM = float(os.getenv('CARBON_LIMIT_BASE_PER_SQM', 50))  # kg CO2 per sq.m per year
    CARBON_LIMIT_PER_OCCUPANT = float(os.getenv('CARBON_LIMIT_PER_OCCUPANT', 1000))  # kg CO2 per person per year
    
    # Credit Pricing (simulated)
    CREDIT_TYPES = {
        'solar': {
            'name': 'Solar Energy Credits',
            'description': 'Offset via solar power generation',
            'price_per_kg': 0.15,  # USD per kg CO2
            'icon': '☀️'
        },
        'wind': {
            'name': 'Wind Energy Credits',
            'description': 'Offset via wind power generation',
            'price_per_kg': 0.12,
            'icon': '💨'
        },
        'bio': {
            'name': 'Bio-Energy Credits',
            'description': 'Offset via biomass energy',
            'price_per_kg': 0.10,
            'icon': '🌱'
        }
    }
    
    # Status Thresholds
    STATUS_SAFE_THRESHOLD = 0.70  # 70% of limit
    STATUS_WARNING_THRESHOLD = 1.0  # 100% of limit
