from datetime import datetime
from config import Config

class CarbonLimitService:
    """
    Service for managing carbon limits and user status
    """
    
    def __init__(self, user_model, emission_model, credit_model):
        self.user_model = user_model
        self.emission_model = emission_model
        self.credit_model = credit_model
    
    def get_user_status(self, user_id):
        """
        Get comprehensive carbon status for a user
        
        Returns:
            dict with status, emissions, limit, percentage, excess, etc.
        """
        # Get user and their carbon limit
        user = self.user_model.get_user_by_id(user_id)
        if not user:
            return None
        
        annual_limit = user['household']['annual_carbon_limit_kg']
        
        # Get total emissions for current year
        year_start = datetime(datetime.utcnow().year, 1, 1)
        emissions = self.emission_model.get_total_emissions(user_id, year_start)
        total_emitted = emissions['total_co2_kg']
        
        # Get active credits
        total_credits = self.credit_model.get_total_active_credits(user_id)
        
        # Calculate net emissions (after credits)
        net_emissions = max(0, total_emitted - total_credits)
        
        # Calculate percentage used
        percentage_used = (net_emissions / annual_limit) * 100 if annual_limit > 0 else 0
        
        # Determine status
        status = self._determine_status(percentage_used)
        
        # Calculate excess if over limit
        excess_co2 = max(0, net_emissions - annual_limit)
        
        return {
            'status': status,
            'annual_limit_kg': annual_limit,
            'total_emitted_kg': total_emitted,
            'electricity_co2_kg': emissions['electricity_co2_kg'],
            'combustion_co2_kg': emissions['combustion_co2_kg'],
            'active_credits_kg': total_credits,
            'net_emissions_kg': net_emissions,
            'percentage_used': round(percentage_used, 2),
            'excess_co2_kg': round(excess_co2, 2),
            'remaining_budget_kg': round(max(0, annual_limit - net_emissions), 2),
            'needs_credits': excess_co2 > 0
        }
    
    def _determine_status(self, percentage_used):
        """
        Determine status based on percentage of limit used
        
        Returns:
            'safe', 'warning', or 'exceeded'
        """
        if percentage_used <= Config.STATUS_SAFE_THRESHOLD * 100:
            return 'safe'
        elif percentage_used <= Config.STATUS_WARNING_THRESHOLD * 100:
            return 'warning'
        else:
            return 'exceeded'
    
    def calculate_required_credits(self, excess_co2_kg):
        """
        Calculate credit options to offset excess emissions
        
        Args:
            excess_co2_kg: Amount of CO2 over the limit
        
        Returns:
            dict with credit options
        """
        if excess_co2_kg <= 0:
            return None
        
        options = []
        for credit_type, info in Config.CREDIT_TYPES.items():
            options.append({
                'type': credit_type,
                'name': info['name'],
                'description': info['description'],
                'icon': info['icon'],
                'amount_kg': round(excess_co2_kg, 2),
                'price_usd': round(excess_co2_kg * info['price_per_kg'], 2),
                'price_per_kg': info['price_per_kg']
            })
        
        return {
            'excess_co2_kg': round(excess_co2_kg, 2),
            'credit_options': options,
            'recommendation': 'Purchase credits to neutralize your carbon footprint'
        }
    
    def get_status_color(self, status):
        """Get color code for status badge"""
        colors = {
            'safe': '#10b981',      # Green
            'warning': '#fbbf24',   # Yellow
            'exceeded': '#ef4444'   # Red
        }
        return colors.get(status, '#6b7280')
    
    def get_status_message(self, status, percentage_used):
        """Get user-friendly status message"""
        if status == 'safe':
            return f"You're doing great! Only {percentage_used:.1f}% of your carbon budget used."
        elif status == 'warning':
            return f"Approaching limit! {percentage_used:.1f}% of your carbon budget used."
        else:
            return f"Limit exceeded! You've used {percentage_used:.1f}% of your carbon budget. Please purchase renewable credits."
