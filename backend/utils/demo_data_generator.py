import random
from datetime import datetime, timedelta
from services.emission_calculator import EmissionCalculator

class DemoDataGenerator:
    """
    Generate realistic demo data for hackathon presentations
    """
    
    def __init__(self, emission_model):
        self.emission_model = emission_model
    
    def generate_emissions(self, user_id, days=30, pattern='gradual_increase'):
        """
        Generate realistic emission data
        
        Args:
            user_id: User ID
            days: Number of days of data to generate
            pattern: 'gradual_increase', 'stable', or 'random'
        
        Returns:
            Number of records created
        """
        records_created = 0
        
        for i in range(days):
            # Calculate date (going backwards from today)
            date_offset = days - i - 1
            
            # Generate realistic values based on pattern
            if pattern == 'gradual_increase':
                # Gradually increasing emissions (to demonstrate limit exceed)
                base_electricity = 8 + (i * 0.3)  # kWh per day
                base_combustion = 300 + (i * 10)  # ppm
            elif pattern == 'stable':
                # Stable emissions
                base_electricity = 10
                base_combustion = 400
            else:  # random
                base_electricity = random.uniform(5, 15)
                base_combustion = random.uniform(250, 600)
            
            # Add daily variation
            electricity_kwh = base_electricity + random.uniform(-1, 1)
            combustion_ppm = base_combustion + random.uniform(-50, 50)
            
            # Ensure non-negative
            electricity_kwh = max(0, electricity_kwh)
            combustion_ppm = max(0, combustion_ppm)
            
            # Calculate CO2
            emissions = EmissionCalculator.calculate_total_co2(electricity_kwh, combustion_ppm)
            
            # Add to database
            self.emission_model.add_emission(
                user_id=user_id,
                electricity_kwh=electricity_kwh,
                electricity_co2_kg=emissions['electricity_co2_kg'],
                combustion_ppm=combustion_ppm,
                combustion_co2_kg=emissions['combustion_co2_kg'],
                source='simulated'
            )
            
            records_created += 1
        
        return records_created
    
    def generate_exceed_scenario(self, user_id):
        """
        Generate data that will definitely exceed the carbon limit
        Perfect for demo purposes
        """
        # Generate 30 days of high emissions
        return self.generate_emissions(user_id, days=30, pattern='gradual_increase')
    
    def generate_safe_scenario(self, user_id):
        """
        Generate data that stays within carbon limit
        """
        return self.generate_emissions(user_id, days=30, pattern='stable')
