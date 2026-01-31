import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

class AIPredictor:
    """
    AI-based emission prediction using Linear Regression
    
    WHY LINEAR REGRESSION:
    - Explainable: Coefficients show feature importance
    - Fast training and inference
    - Sufficient for trend-based prediction
    - No overfitting risk with limited data
    - Judge-friendly explanation
    
    ML is used ONLY for prediction, NOT for core emission calculations.
    """
    
    def __init__(self, emission_model):
        self.emission_model = emission_model
        self.model = None
        self.feature_names = ['day_of_month', 'month', 'occupants', 'avg_electricity_7d', 'avg_combustion_7d']
    
    def train_model(self, user_id, user_data):
        """
        Train Linear Regression model on user's historical data
        
        Args:
            user_id: User ID
            user_data: User document with household info
        
        Returns:
            Training metrics
        """
        # Get historical emissions (last 30 days minimum)
        emissions = self.emission_model.get_recent_emissions(user_id, days=60)
        
        if len(emissions) < 7:
            return {
                'success': False,
                'message': 'Insufficient data for training. Need at least 7 days of emission records.'
            }
        
        # Prepare features and target
        df = pd.DataFrame(emissions)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Extract features
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['occupants'] = user_data['household']['occupants']
        
        # Rolling averages (7-day window)
        df['avg_electricity_7d'] = df['electricity_co2_kg'].rolling(window=7, min_periods=1).mean()
        df['avg_combustion_7d'] = df['combustion_co2_kg'].rolling(window=7, min_periods=1).mean()
        
        # Prepare training data
        X = df[self.feature_names].values
        y = df['total_co2_kg'].values
        
        # Train model
        self.model = LinearRegression()
        self.model.fit(X, y)
        
        # Calculate R² score
        r2_score = self.model.score(X, y)
        
        return {
            'success': True,
            'model_type': 'Linear Regression',
            'r2_score': round(r2_score, 4),
            'training_samples': len(emissions),
            'coefficients': {
                name: round(coef, 4) 
                for name, coef in zip(self.feature_names, self.model.coef_)
            },
            'intercept': round(self.model.intercept_, 4)
        }
    
    def predict_emissions(self, user_id, user_data, days_ahead=7):
        """
        Predict future emissions
        
        Args:
            user_id: User ID
            user_data: User document
            days_ahead: Number of days to predict (default 7)
        
        Returns:
            Predictions with dates
        """
        # Train model if not already trained
        if self.model is None:
            training_result = self.train_model(user_id, user_data)
            if not training_result['success']:
                return training_result
        
        # Get recent data for feature calculation
        recent_emissions = self.emission_model.get_recent_emissions(user_id, days=14)
        
        if len(recent_emissions) < 7:
            return {
                'success': False,
                'message': 'Insufficient recent data for prediction'
            }
        
        df = pd.DataFrame(recent_emissions)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Calculate current averages
        avg_electricity = df['electricity_co2_kg'].tail(7).mean()
        avg_combustion = df['combustion_co2_kg'].tail(7).mean()
        occupants = user_data['household']['occupants']
        
        # Generate predictions
        predictions = []
        start_date = datetime.utcnow()
        
        for i in range(days_ahead):
            future_date = start_date + timedelta(days=i+1)
            
            # Prepare features
            features = np.array([[
                future_date.day,
                future_date.month,
                occupants,
                avg_electricity,
                avg_combustion
            ]])
            
            # Predict
            predicted_co2 = self.model.predict(features)[0]
            
            predictions.append({
                'date': future_date.strftime('%Y-%m-%d'),
                'predicted_co2_kg': round(max(0, predicted_co2), 2)  # Ensure non-negative
            })
        
        return {
            'success': True,
            'predictions': predictions,
            'model_type': 'Linear Regression',
            'prediction_horizon_days': days_ahead
        }
    
    def get_prediction_with_warning(self, user_id, user_data):
        """
        Get predictions and check if user will exceed limit
        
        Returns:
            Predictions + warning if limit will be exceeded
        """
        # Get predictions
        prediction_result = self.predict_emissions(user_id, user_data, days_ahead=30)
        
        if not prediction_result['success']:
            return prediction_result
        
        # Calculate total predicted emissions
        total_predicted = sum(p['predicted_co2_kg'] for p in prediction_result['predictions'])
        
        # Get current emissions
        year_start = datetime(datetime.utcnow().year, 1, 1)
        current_emissions = self.emission_model.get_total_emissions(user_id, year_start)
        current_total = current_emissions['total_co2_kg']
        
        # Get annual limit
        annual_limit = user_data['household']['annual_carbon_limit_kg']
        
        # Check if will exceed
        projected_total = current_total + total_predicted
        will_exceed = projected_total > annual_limit
        
        # Convert numpy types to Python native types for JSON serialization
        return {
            **prediction_result,
            'current_emissions_kg': float(current_total),
            'predicted_next_30d_kg': round(float(total_predicted), 2),
            'projected_total_kg': round(float(projected_total), 2),
            'annual_limit_kg': float(annual_limit),
            'will_exceed_limit': bool(will_exceed),
            'warning': 'Warning: Predictions indicate you will exceed your carbon limit!' if will_exceed else None
        }
    
    def explain_model(self):
        """
        Explain the AI model for transparency
        
        Returns:
            Model explanation for judges/users
        """
        if self.model is None:
            return {
                'message': 'Model not trained yet'
            }
        
        return {
            'model_type': 'Linear Regression',
            'why_linear_regression': [
                'Explainable: Each feature has a clear coefficient showing its impact',
                'Fast: Training and prediction in milliseconds',
                'Transparent: No black-box decision making',
                'Sufficient: Captures emission trends effectively',
                'Judge-friendly: Easy to explain in presentations'
            ],
            'features_used': self.feature_names,
            'feature_importance': {
                name: round(abs(coef), 4)
                for name, coef in zip(self.feature_names, self.model.coef_)
            },
            'how_it_works': 'The model learns patterns from your historical emission data and predicts future emissions based on time patterns and household characteristics.',
            'ml_scope': 'ML is used ONLY for predictions. Core emission calculations remain rule-based and transparent.',
            'future_enhancements': [
                'LSTM for complex temporal patterns (mentioned as future scope)',
                'Multi-household collaborative filtering',
                'Weather-based adjustments'
            ]
        }
