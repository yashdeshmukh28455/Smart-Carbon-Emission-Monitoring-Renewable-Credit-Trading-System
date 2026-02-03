from config import Config

class EmissionCalculator:
    """
    Rule-based carbon emission calculator
    
    This service uses TRANSPARENT, EXPLAINABLE formulas to calculate CO2 emissions.
    NO MACHINE LEARNING is used here - only scientific emission factors.
    """
    
    @staticmethod
    def calculate_electricity_co2(kwh, factor=None):
        """
        Calculate CO2 emissions from electricity consumption
        """
        if kwh < 0:
            raise ValueError("Electricity consumption cannot be negative")
            
        used_factor = factor if factor is not None else Config.EMISSION_FACTOR_KWH
        
        co2_kg = kwh * used_factor
        return round(co2_kg, 4)
    
    @staticmethod
    def calculate_combustion_co2(ppm, factor=None):
        """
        Calculate CO2 emissions from combustion
        """
        if ppm < 0:
            raise ValueError("PPM cannot be negative")
            
        used_factor = factor if factor is not None else Config.COMBUSTION_PPM_TO_KG_FACTOR
        
        co2_kg = ppm * used_factor
        return round(co2_kg, 4)
    
    @staticmethod
    def calculate_total_co2(electricity_kwh, combustion_ppm, factors=None):
        """
        Calculate total CO2 emissions from both sources
        
        Args:
            electricity_kwh: Electricity consumption
            combustion_ppm: Combustion CO2 concentration
            factors: Dict with 'electricity_kwh' and 'combustion_ppm' factors
        """
        elec_factor = factors.get('electricity_kwh') if factors else None
        comb_factor = factors.get('combustion_ppm') if factors else None
        
        electricity_co2 = EmissionCalculator.calculate_electricity_co2(electricity_kwh, elec_factor)
        combustion_co2 = EmissionCalculator.calculate_combustion_co2(combustion_ppm, comb_factor)
        
        return {
            'electricity_co2_kg': electricity_co2,
            'combustion_co2_kg': combustion_co2,
            'total_co2_kg': round(electricity_co2 + combustion_co2, 4),
            'factors_used': {
                'electricity': elec_factor or Config.EMISSION_FACTOR_KWH,
                'combustion': comb_factor or Config.COMBUSTION_PPM_TO_KG_FACTOR
            }
        }
    
    @staticmethod
    def explain_calculation(factors=None):
        """
        Return explanation of calculation methodology
        """
        elec_val = factors.get('electricity_kwh') if factors else Config.EMISSION_FACTOR_KWH
        comb_val = factors.get('combustion_ppm') if factors else Config.COMBUSTION_PPM_TO_KG_FACTOR
        source = factors.get('source', 'Default Configuration') if factors else 'System Default'
        
        return {
            'methodology': 'Rule-Based Transparent Calculation',
            'electricity_formula': f'CO2 (kg) = kWh × {elec_val}',
            'combustion_formula': f'CO2 (kg) = ppm × {comb_val}',
            'emission_factor_source': source,
            'why_not_ml': 'Core calculations must be transparent, auditable, and explainable. ML is used only for predictions, not calculations.',
            'scientific_basis': 'Based on standard emission factors from energy authorities'
        }
