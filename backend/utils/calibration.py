
class SensorCalibration:
    """
    Utility for calibrating and converting raw sensor data.
    
    Sensors:
    - ACS712 (Current Sensor): Measures Amps
    - MH-Z19C (CO2 Sensor): Measures PPM
    """
    
    # --- ACS712 Calibration Constants ---
    # Sensitivity: 30A module = 0.066 V/A, 20A = 0.100 V/A, 5A = 0.185 V/A
    ACS712_SENSITIVITY = 0.185  # Assuming 5A module for household/demo use
    VOLTAGE_OFFSET = 2.5        # Zero current output voltage (VCC/2 for 5V)
    NOISE_THRESHOLD_AMPS = 0.05 # Cutoff for noise (ignore currents below 50mA)
    SYSTEM_VOLTAGE = 230        # Standard AC Voltage (India/EU)
    
    # --- MH-Z19C Calibration Constants ---
    MHZ19_BASELINE_PPM = 400    # Global average outdoor CO2 baseline
    
    @staticmethod
    def calibrate_current(raw_voltage):
        """
        Convert raw sensor voltage to Amps.
        Formula: Amps = (SensorVoltage - Offset) / Sensitivity
        """
        # Remove DC offset to get AC component (simplified for simulation)
        # In real hardware, this would involve RMS calculation over a period
        current_amps = abs(raw_voltage - SensorCalibration.VOLTAGE_OFFSET) / SensorCalibration.ACS712_SENSITIVITY
        
        # Noise filtering
        if current_amps < SensorCalibration.NOISE_THRESHOLD_AMPS:
            return 0.0
            
        return round(current_amps, 4)

    @staticmethod
    def amps_to_power(amps, power_factor=0.9):
        """
        Convert Amps to Watts.
        Formula: P(W) = V * I * PF
        """
        return round(SensorCalibration.SYSTEM_VOLTAGE * amps * power_factor, 2)
        
    @staticmethod
    def power_to_kwh(watts, duration_hours):
        """
        Convert Power (W) to Energy (kWh).
        Formula: E(kWh) = (Watts * Hours) / 1000
        """
        return round((watts * duration_hours) / 1000.0, 6)
    
    @staticmethod
    def calibrate_co2_ppm(raw_ppm):
        """
        Calibrate and validate CO2 PPM readings.
        """
        # MH-Z19C range: 400-5000ppm
        # If below baseline, clamp to baseline (sensor drift)
        if raw_ppm < SensorCalibration.MHZ19_BASELINE_PPM:
            return SensorCalibration.MHZ19_BASELINE_PPM
            
        # Upper sanity check (unlikely to exceed 5000 in normal home)
        if raw_ppm > 10000:
             # Likely sensor error/spike
            return 10000 
            
        return int(raw_ppm)
