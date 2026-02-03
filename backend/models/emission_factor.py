
from datetime import datetime
from config import Config

class EmissionFactor:
    """
    Model for managing emission factors in MongoDB
    Allows admin/policy-makers to update factors without code changes.
    """
    
    def __init__(self, db):
        self.collection = db['emission_factors']
        
    def get_current_factors(self):
        """
        Get the latest active emission factors.
        Falls back to Config defaults if not found in DB.
        """
        # Try to find the latest active factor document
        factor_doc = self.collection.find_one(
            {'is_active': True},
            sort=[('created_at', -1)]
        )
        
        if factor_doc:
            return {
                'electricity_kwh': factor_doc.get('electricity_kwh', Config.EMISSION_FACTOR_KWH),
                'combustion_ppm': factor_doc.get('combustion_ppm', Config.COMBUSTION_PPM_TO_KG_FACTOR),
                'source': factor_doc.get('source', 'Database Override')
            }
            
        # Fallback to hardcoded config
        return {
            'electricity_kwh': Config.EMISSION_FACTOR_KWH,
            'combustion_ppm': Config.COMBUSTION_PPM_TO_KG_FACTOR,
            'source': 'Default Configuration'
        }
        
    def update_factors(self, electricity_kwh, combustion_ppm, source="Admin Update"):
        """
        Create a new active emission factor record.
        Preserves history by creating new doc rather than updating.
        """
        new_factor = {
            'electricity_kwh': float(electricity_kwh),
            'combustion_ppm': float(combustion_ppm),
            'source': source,
            'is_active': True,
            'created_at': datetime.utcnow()
        }
        
        # Insert new factor
        return self.collection.insert_one(new_factor).inserted_id
