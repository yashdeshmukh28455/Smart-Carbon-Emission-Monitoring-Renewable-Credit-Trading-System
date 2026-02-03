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
    
    def calculate_annual_limit(self, area_sqm, occupants):
        """
        Calculate annual carbon limit based on house specs.
        Formula: (Area * Base_Per_Sqm) + (Occupants * Per_Occupant)
        """
        base_limit = area_sqm * Config.CARBON_LIMIT_BASE_PER_SQM
        occupant_limit = occupants * Config.CARBON_LIMIT_PER_OCCUPANT
        return round(base_limit + occupant_limit, 2)

    def calculate_carbon_score(self, percentage_used, credit_dependency_ratio=0):
        """
        Calculate Carbon Score (A+ to F) based on usage efficiency.
        
        Grading Scale:
        A+ : < 50% usage
        A  : 50-70% usage
        B  : 70-85% usage
        C  : 85-100% usage
        D  : 100-120% usage (Warning)
        F  : > 120% usage (Critical)
        """
        if percentage_used < 50:
            return 'A+'
        elif percentage_used < 70:
            return 'A'
        elif percentage_used < 85:
            return 'B'
        elif percentage_used <= 100:
            return 'C'
        elif percentage_used < 120:
            return 'D'
        else:
            return 'F'

    def get_user_status(self, user_id):
        """
        Get comprehensive carbon status for a user
        """
        # Get user and their carbon limit
        user = self.user_model.get_user_by_id(user_id)
        if not user:
            return None
        
        household = user.get('household', {})
        area_sqm = household.get('area_sqm', 0)
        occupants = household.get('occupants', 0)
        
        # Calculate limit dynamically to ensure it's always up to date with config
        annual_limit = self.calculate_annual_limit(area_sqm, occupants)
        
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
        
        # Determine status and score
        status = self._determine_status(percentage_used)
        score = self.calculate_carbon_score(percentage_used)
        
        # Calculate excess if over limit
        excess_co2 = max(0, net_emissions - annual_limit)
        
        return {
            'status': status,
            'carbon_score': score,
            'annual_limit_kg': annual_limit,
            'total_emitted_kg': total_emitted,
            'electricity_co2_kg': emissions['electricity_co2_kg'],
            'combustion_co2_kg': emissions['combustion_co2_kg'],
            'active_credits_kg': total_credits,
            'net_emissions_kg': net_emissions,
            'percentage_used': round(percentage_used, 2),
            'excess_co2_kg': round(excess_co2, 2),
            'remaining_budget_kg': round(max(0, annual_limit - net_emissions), 2),
            'needs_credits': excess_co2 > 0,
            'limit_explanation': self.explain_limit_formula(area_sqm, occupants)
        }
    
    def explain_limit_formula(self, area_sqm, occupants):
        """Explain how the limit was calculated"""
        return {
            'formula': f"({area_sqm}m² × {Config.CARBON_LIMIT_BASE_PER_SQM}) + ({occupants} people × {Config.CARBON_LIMIT_PER_OCCUPANT})",
            'base_limit': area_sqm * Config.CARBON_LIMIT_BASE_PER_SQM,
            'occupant_limit': occupants * Config.CARBON_LIMIT_PER_OCCUPANT
        }

    def _determine_status(self, percentage_used):
        # ... existing logic ...
        if percentage_used <= Config.STATUS_SAFE_THRESHOLD * 100:
            return 'safe'
        elif percentage_used <= Config.STATUS_WARNING_THRESHOLD * 100:
            return 'warning'
        else:
            return 'exceeded'
    
    def calculate_required_credits(self, excess_co2_kg):
        # ... existing logic ...
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
        # ... existing logic ...
        colors = {
            'safe': '#10b981',      # Green
            'warning': '#fbbf24',   # Yellow
            'exceeded': '#ef4444'   # Red
        }
        return colors.get(status, '#6b7280')

    def get_status_message(self, status, percentage_used):
        # ... existing logic ...
        if status == 'safe':
            return f"You're doing great! Only {percentage_used:.1f}% of your carbon budget used."
        elif status == 'warning':
            return f"Approaching limit! {percentage_used:.1f}% of your carbon budget used."
        else:
            return f"Limit exceeded! You've used {percentage_used:.1f}% of your carbon budget. Please purchase renewable credits."
    
    def get_sustainability_tips(self, status, electricity_co_kg=0, combustion_co_kg=0):
        """
        Get smart sustainability tips based on usage profile
        """
        tips = []
        
        # Status-based tips
        if status == 'safe':
            tips.append("🌟 Great job maintaining low emissions! Consider investing in long-term offsets.")
        elif status == 'warning':
            tips.append("⚠️ You are nearing your limit. Try reducing high-consumption appliance usage.")
        else:
            tips.append("🚨 Limit exceeded. Immediate action required: offset carbon or switch to renewables.")
            
        # Usage-based specific tips
        if electricity_co_kg > combustion_co_kg:
            tips.append("💡 High electricity usage detected. Switch to LED bulbs and unplug idle devices.")
            tips.append("🌞 Consider installing solar panels or switching to a green energy provider.")
        else:
            tips.append("🔥 High combustion emissions. Check your heating system efficiency.")
            tips.append("🚗 Verify vehicle emissions or reduce car travel if applicable.")
            
        return tips
