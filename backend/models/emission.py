from datetime import datetime, timedelta
from bson import ObjectId

class Emission:
    """Emission model for storing and querying carbon emission data"""
    
    def __init__(self, db):
        self.collection = db.emissions
        # Create indexes for efficient querying
        self.collection.create_index([('user_id', 1), ('timestamp', -1)])
        self.collection.create_index('timestamp')
    
    def add_emission(self, user_id, electricity_kwh, electricity_co2_kg, 
                     combustion_ppm, combustion_co2_kg, source='iot'):
        """
        Add a new emission record
        
        Args:
            user_id: User ID
            electricity_kwh: Electricity consumption in kWh
            electricity_co2_kg: Calculated CO2 from electricity
            combustion_ppm: Combustion CO2 in ppm
            combustion_co2_kg: Calculated CO2 from combustion
            source: 'iot' or 'simulated'
        
        Returns:
            emission_id
        """
        emission_doc = {
            'user_id': ObjectId(user_id),
            'timestamp': datetime.utcnow(),
            'electricity_kwh': electricity_kwh,
            'electricity_co2_kg': electricity_co2_kg,
            'combustion_ppm': combustion_ppm,
            'combustion_co2_kg': combustion_co2_kg,
            'total_co2_kg': electricity_co2_kg + combustion_co2_kg,
            'source': source
        }
        
        result = self.collection.insert_one(emission_doc)
        return str(result.inserted_id)
    
    def get_emissions_by_period(self, user_id, period='daily', limit=30):
        """
        Get aggregated emissions by period
        
        Args:
            user_id: User ID
            period: 'daily', 'monthly', or 'yearly'
            limit: Number of records to return
        
        Returns:
            List of aggregated emissions
        """
        if period == 'daily':
            group_format = '%Y-%m-%d'
        elif period == 'monthly':
            group_format = '%Y-%m'
        else:  # yearly
            group_format = '%Y'
        
        pipeline = [
            {'$match': {'user_id': ObjectId(user_id)}},
            {'$sort': {'timestamp': -1}},
            {'$group': {
                '_id': {'$dateToString': {'format': group_format, 'date': '$timestamp'}},
                'total_co2_kg': {'$sum': '$total_co2_kg'},
                'electricity_co2_kg': {'$sum': '$electricity_co2_kg'},
                'combustion_co2_kg': {'$sum': '$combustion_co2_kg'},
                'electricity_kwh': {'$sum': '$electricity_kwh'},
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': -1}},
            {'$limit': limit}
        ]
        
        results = list(self.collection.aggregate(pipeline))
        
        # Format results
        formatted = []
        for r in results:
            formatted.append({
                'period': r['_id'],
                'total_co2_kg': round(r['total_co2_kg'], 2),
                'electricity_co2_kg': round(r['electricity_co2_kg'], 2),
                'combustion_co2_kg': round(r['combustion_co2_kg'], 2),
                'electricity_kwh': round(r['electricity_kwh'], 2),
                'record_count': r['count']
            })
        
        return formatted
    
    def get_total_emissions(self, user_id, start_date=None):
        """
        Get total emissions for a user
        
        Args:
            user_id: User ID
            start_date: Optional start date (defaults to beginning of current year)
        
        Returns:
            Total CO2 in kg
        """
        if start_date is None:
            # Default to start of current year
            start_date = datetime(datetime.utcnow().year, 1, 1)
        
        pipeline = [
            {'$match': {
                'user_id': ObjectId(user_id),
                'timestamp': {'$gte': start_date}
            }},
            {'$group': {
                '_id': None,
                'total_co2_kg': {'$sum': '$total_co2_kg'},
                'electricity_co2_kg': {'$sum': '$electricity_co2_kg'},
                'combustion_co2_kg': {'$sum': '$combustion_co2_kg'}
            }}
        ]
        
        result = list(self.collection.aggregate(pipeline))
        
        if result:
            return {
                'total_co2_kg': round(result[0]['total_co2_kg'], 2),
                'electricity_co2_kg': round(result[0]['electricity_co2_kg'], 2),
                'combustion_co2_kg': round(result[0]['combustion_co2_kg'], 2)
            }
        
        return {
            'total_co2_kg': 0,
            'electricity_co2_kg': 0,
            'combustion_co2_kg': 0
        }
    
    def get_recent_emissions(self, user_id, days=30):
        """Get raw emission records for the last N days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        emissions = self.collection.find({
            'user_id': ObjectId(user_id),
            'timestamp': {'$gte': start_date}
        }).sort('timestamp', 1)
        
        results = []
        for e in emissions:
            results.append({
                'timestamp': e['timestamp'].isoformat(),
                'electricity_kwh': e['electricity_kwh'],
                'electricity_co2_kg': e['electricity_co2_kg'],
                'combustion_ppm': e['combustion_ppm'],
                'combustion_co2_kg': e['combustion_co2_kg'],
                'total_co2_kg': e['total_co2_kg'],
                'source': e['source']
            })
        
        return results
