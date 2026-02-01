
from config import Config

class CreditService:
    """
    Service for managing renewable energy credit purchases
    """
    
    def __init__(self, credit_model):
        self.credit_model = credit_model
    
    def purchase_credits(self, user_id, credit_type, amount_kg_co2):
        """
        Process credit purchase (simulated for demo)
        
        Args:
            user_id: User ID
            credit_type: 'solar', 'wind', or 'bio'
            amount_kg_co2: Amount of CO2 to offset
        
        Returns:
            Purchase confirmation
        """
        # Validate credit type
        if credit_type not in Config.CREDIT_TYPES:
            raise ValueError(f"Invalid credit type. Must be one of: {', '.join(Config.CREDIT_TYPES.keys())}")
        
        if amount_kg_co2 <= 0:
            raise ValueError("Credit amount must be positive")
        
        # Get credit info
        credit_info = Config.CREDIT_TYPES[credit_type]
        
        # Calculate price
        total_price = amount_kg_co2 * credit_info['price_per_kg']
        
        # Create credit record
        credit_id = self.credit_model.purchase_credit(user_id, credit_type, amount_kg_co2)
        
        return {
            'success': True,
            'credit_id': credit_id,
            'credit_type': credit_type,
            'credit_name': credit_info['name'],
            'amount_kg_co2': round(amount_kg_co2, 2),
            'price_usd': round(total_price, 2),
            'message': f'Successfully purchased {amount_kg_co2:.2f} kg CO2 offset via {credit_info["name"]}',
            'valid_until': 'Valid for 1 year from purchase date'
        }
    
    def get_credit_summary(self, user_id):
        """
        Get summary of user's credits
        
        Returns:
            Active credits and total offset capacity
        """
        active_credits = self.credit_model.get_active_credits(user_id)
        total_offset = self.credit_model.get_total_active_credits(user_id)
        
        # Group by type
        by_type = {}
        for credit in active_credits:
            ctype = credit['credit_type']
            if ctype not in by_type:
                by_type[ctype] = {
                    'type': ctype,
                    'name': Config.CREDIT_TYPES[ctype]['name'],
                    'icon': Config.CREDIT_TYPES[ctype]['icon'],
                    'total_kg': 0,
                    'count': 0
                }
            by_type[ctype]['total_kg'] += credit['amount_kg_co2']
            by_type[ctype]['count'] += 1
        
        return {
            'total_active_offset_kg': total_offset,
            'active_credits': active_credits,
            'by_type': list(by_type.values()),
            'credit_count': len(active_credits)
        }
    
    def get_available_credit_types(self):
        """Get all available credit types with details"""
        types = []
        for ctype, info in Config.CREDIT_TYPES.items():
            types.append({
                'type': ctype,
                'name': info['name'],
                'description': info['description'],
                'icon': info['icon'],
                'price_per_kg': info['price_per_kg']
            })
        return types
