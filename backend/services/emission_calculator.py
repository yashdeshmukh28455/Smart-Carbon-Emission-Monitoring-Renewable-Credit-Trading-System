from config import Config

class EmissionCalculator:
    """
    Rule-based carbon emission calculator
    
    This service uses TRANSPARENT, EXPLAINABLE formulas to calculate CO2 emissions.
    NO MACHINE LEARNING is used here - only scientific emission factors.
    """
    
    @staticmethod
    def calculate_electricity_co2(kwh):
        """
        Calculate CO2 emissions from electricity consumption
        
        Formula: kWh × emission_factor
        Default factor: 0.85 kg CO2 per kWh (average grid emission)
        
        Args:
            kwh: Electricity consumption in kilowatt-hours
        
        Returns:
            CO2 emissions in kg
        """
        if kwh < 0:
            raise ValueError("Electricity consumption cannot be negative")
        
        co2_kg = kwh * Config.EMISSION_FACTOR_KWH
        return round(co2_kg, 4)
    
    @staticmethod
    def calculate_combustion_co2(ppm):
        """
        Calculate CO2 emissions from combustion (gas stoves, heaters, etc.)
        
        Conversion: ppm → mg/m³ → grams → kg
        Formula: ppm × conversion_factor
        
        Args:
            ppm: CO2 concentration in parts per million
        
        Returns:
            CO2 emissions in kg
        """
        if ppm < 0:
            raise ValueError("PPM cannot be negative")
        
        # Convert ppm to kg CO2
        # Typical conversion: ppm × 0.0018 (assuming standard conditions)
        co2_kg = ppm * Config.COMBUSTION_PPM_TO_KG_FACTOR
        return round(co2_kg, 4)
    
    @staticmethod
    def calculate_total_co2(electricity_kwh, combustion_ppm):
        """
        Calculate total CO2 emissions from both sources
        
        Args:
            electricity_kwh: Electricity consumption
            combustion_ppm: Combustion CO2 concentration
        
        Returns:
            dict with breakdown and total
        """
        electricity_co2 = EmissionCalculator.calculate_electricity_co2(electricity_kwh)
        combustion_co2 = EmissionCalculator.calculate_combustion_co2(combustion_ppm)
        
        return {
            'electricity_co2_kg': electricity_co2,
            'combustion_co2_kg': combustion_co2,
            'total_co2_kg': round(electricity_co2 + combustion_co2, 4)
        }
    
    @staticmethod
    def explain_calculation():
        """
        Return explanation of calculation methodology
        For transparency and judge presentation
        """
        return {
            'methodology': 'Rule-Based Transparent Calculation',
            'electricity_formula': f'CO2 (kg) = kWh × {Config.EMISSION_FACTOR_KWH}',
            'combustion_formula': f'CO2 (kg) = ppm × {Config.COMBUSTION_PPM_TO_KG_FACTOR}',
            'emission_factor_source': 'Average grid emission factor (configurable)',
            'why_not_ml': 'Core calculations must be transparent, auditable, and explainable. ML is used only for predictions, not calculations.',
            'scientific_basis': 'Based on standard emission factors from energy authorities'
        }
