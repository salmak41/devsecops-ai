# def calculate_risk(test_pass_rate, vulnerabilities, build_time):
#     risk_score = (1 - test_pass_rate) * 0.5 + (vulnerabilities * 0.1) + (build_time / 1000)

#     if risk_score > 0.7:
#         decision = "BLOCK"
#     else:
#         decision = "DEPLOY"

#     return round(risk_score, 2), decision

# model.py - AI-Powered Risk Prediction with XGBoost
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib
import os
import json
from datetime import datetime

class RiskPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_path = 'risk_model.pkl'
        self.scaler_path = 'scaler.pkl'
        self.metrics_path = 'model_metrics.json'
        self._load_or_train()
    
    def _generate_synthetic_data(self, n_samples=5000):
        """Generate realistic CI/CD pipeline data for training"""
        np.random.seed(42)
        
        # Features
        test_pass_rate = np.random.uniform(0.5, 1.0, n_samples)
        critical_vulns = np.random.poisson(2, n_samples)
        high_vulns = np.random.poisson(3, n_samples)
        medium_vulns = np.random.poisson(5, n_samples)
        build_time = np.random.normal(120, 30, n_samples)
        code_churn = np.random.poisson(10, n_samples)
        past_failures = np.random.poisson(1, n_samples)
        
        # Target: Deployment Success (1) or Failure (0)
        success = np.ones(n_samples)
        for i in range(n_samples):
            # Calculate risk score
            risk = (1 - test_pass_rate[i]) * 0.5
            risk += (critical_vulns[i] / 10) * 0.3
            risk += (high_vulns[i] / 15) * 0.1
            risk += (past_failures[i] / 5) * 0.1
            
            if risk > 0.45 or test_pass_rate[i] < 0.6:
                success[i] = 0  # Failure
        
        # Create DataFrame
        data = pd.DataFrame({
            'test_pass_rate': test_pass_rate,
            'critical_vulns': critical_vulns,
            'high_vulns': high_vulns,
            'medium_vulns': medium_vulns,
            'build_time': build_time,
            'code_churn': code_churn,
            'past_failures': past_failures,
            'success': success
        })
        return data
    
    def _train_models(self):
        """Train and compare multiple ML models"""
        print("="*60)
        print("🔄 TRAINING ML MODELS FOR DEPLOYMENT RISK PREDICTION")
        print("="*60)
        
        # Generate data
        data = self._generate_synthetic_data(5000)
        X = data.drop('success', axis=1)
        y = data['success']
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # --- Model 1: Logistic Regression ---
        print("\n📊 Training Logistic Regression...")
        lr = LogisticRegression(max_iter=1000)
        lr.fit(X_train_scaled, y_train)
        lr_pred = lr.predict(X_test_scaled)
        lr_metrics = {
            'accuracy': accuracy_score(y_test, lr_pred),
            'precision': precision_score(y_test, lr_pred),
            'recall': recall_score(y_test, lr_pred),
            'f1': f1_score(y_test, lr_pred)
        }
        print(f"   ✅ Accuracy: {lr_metrics['accuracy']:.4f}")
        
        # --- Model 2: Random Forest ---
        print("\n📊 Training Random Forest...")
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_train_scaled, y_train)
        rf_pred = rf.predict(X_test_scaled)
        rf_metrics = {
            'accuracy': accuracy_score(y_test, rf_pred),
            'precision': precision_score(y_test, rf_pred),
            'recall': recall_score(y_test, rf_pred),
            'f1': f1_score(y_test, rf_pred)
        }
        print(f"   ✅ Accuracy: {rf_metrics['accuracy']:.4f}")
        
        # --- Model 3: XGBoost ---
        print("\n📊 Training XGBoost...")
        xgb = XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        xgb.fit(X_train_scaled, y_train)
        xgb_pred = xgb.predict(X_test_scaled)
        xgb_metrics = {
            'accuracy': accuracy_score(y_test, xgb_pred),
            'precision': precision_score(y_test, xgb_pred),
            'recall': recall_score(y_test, xgb_pred),
            'f1': f1_score(y_test, xgb_pred)
        }
        print(f"   ✅ Accuracy: {xgb_metrics['accuracy']:.4f}")
        
        # --- Select Best Model ---
        models = {
            'Logistic Regression': (lr, lr_metrics),
            'Random Forest': (rf, rf_metrics),
            'XGBoost': (xgb, xgb_metrics)
        }
        
        best_model_name = max(models, key=lambda k: models[k][1]['accuracy'])
        self.model, best_metrics = models[best_model_name]
        
        print("\n" + "="*60)
        print(f"🏆 BEST MODEL: {best_model_name}")
        print(f"   Accuracy:  {best_metrics['accuracy']:.4f}")
        print(f"   Precision: {best_metrics['precision']:.4f}")
        print(f"   Recall:    {best_metrics['recall']:.4f}")
        print(f"   F1-Score:  {best_metrics['f1']:.4f}")
        print("="*60)
        
        # --- Save Model and Metrics ---
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        # Save metrics
        metrics_data = {
            'model': best_model_name,
            'metrics': best_metrics,
            'all_models': {
                'Logistic Regression': lr_metrics,
                'Random Forest': rf_metrics,
                'XGBoost': xgb_metrics
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'samples': len(data)
        }
        
        with open(self.metrics_path, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        print(f"\n✅ Model saved to: {self.model_path}")
        print(f"✅ Metrics saved to: {self.metrics_path}")
        
        # Show confusion matrix
        cm = confusion_matrix(y_test, xgb_pred)
        print(f"\n📊 Confusion Matrix:")
        print(f"   [[{cm[0][0]}, {cm[0][1]}]")
        print(f"    [{cm[1][0]}, {cm[1][1]}]")
        
        return best_metrics
    
    def _load_or_train(self):
        """Load existing model or train new one"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            print("✅ Loaded existing ML model.")
            
            # Load metrics
            if os.path.exists(self.metrics_path):
                with open(self.metrics_path) as f:
                    metrics = json.load(f)
                print(f"   📊 Model: {metrics['model']}")
                print(f"   📊 Accuracy: {metrics['metrics']['accuracy']:.4f}")
            return
        
        print("🔄 No model found. Training new model...")
        self._train_models()
    
    def predict_risk(self, features):
        """
        Predict deployment risk from pipeline metrics
        
        features: dict with:
            - test_pass_rate: float (0-1)
            - critical_vulns: int
            - high_vulns: int
            - medium_vulns: int
            - build_time: float (seconds)
            - code_churn: int
            - past_failures: int
        
        Returns: dict with risk_score, success_probability, decision
        """
        # Ensure all features exist
        required = ['test_pass_rate', 'critical_vulns', 'high_vulns', 
                    'medium_vulns', 'build_time', 'code_churn', 'past_failures']
        
        for key in required:
            if key not in features:
                features[key] = 0
        
        # Convert to DataFrame
        X_input = pd.DataFrame([[
            features['test_pass_rate'],
            features['critical_vulns'],
            features['high_vulns'],
            features['medium_vulns'],
            features['build_time'],
            features['code_churn'],
            features['past_failures']
        ]], columns=required)
        
        # Scale
        X_scaled = self.scaler.transform(X_input)
        
        # Get probability of Success
        success_prob = self.model.predict_proba(X_scaled)[0][1]
        risk_score = (1 - success_prob) * 100
        
        # Decision threshold: 70%
        decision = "BLOCK" if risk_score > 70 else "DEPLOY"
        
        # Feature importance (explainability)
        top_factors = []
        if features['test_pass_rate'] < 0.7:
            top_factors.append(f"Low test pass rate ({features['test_pass_rate']:.2f})")
        if features['critical_vulns'] > 2:
            top_factors.append(f"High critical vulnerabilities ({features['critical_vulns']})")
        if features['past_failures'] > 2:
            top_factors.append(f"Multiple past failures ({features['past_failures']})")
        if features['build_time'] > 180:
            top_factors.append(f"Long build time ({features['build_time']}s)")
        
        return {
            'risk_score': round(risk_score, 2),
            'success_probability': round(success_prob * 100, 2),
            'decision': decision,
            'top_factors': top_factors if top_factors else ['No major risks detected'],
            'model': type(self.model).__name__
        }


# Singleton instance
predictor = RiskPredictor()


# ----- YOUR ORIGINAL calculate_risk function (for backward compatibility) -----
def calculate_risk(test_pass_rate, vulnerabilities, build_time):
    """
    Original function - kept for backward compatibility
    Now uses the ML model for better predictions
    """
    # Convert to ML features
    features = {
        'test_pass_rate': test_pass_rate,
        'critical_vulns': vulnerabilities,
        'high_vulns': 0,
        'medium_vulns': 0,
        'build_time': build_time,
        'code_churn': 0,
        'past_failures': 0
    }
    
    # Use ML model
    result = predictor.predict_risk(features)
    
    # Return in original format
    return result['risk_score'] / 100, result['decision'] 
