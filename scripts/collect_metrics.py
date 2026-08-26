# scripts/collect_metrics.py
import json
import os
import sys
from datetime import datetime

# Add parent directory to path so we can import model
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def collect_metrics():
    """Simulate collecting metrics from pipeline"""
    
    # For demo purposes, we generate sample metrics
    # In production, these would come from GitHub Actions
    metrics = {
        "test_pass_rate": 0.85,
        "critical_vulns": 2,
        "high_vulns": 3,
        "medium_vulns": 5,
        "build_time": 120,
        "code_churn": 8,
        "past_failures": 1,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Save metrics.json
    with open('metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print("✅ metrics.json created")
    print(json.dumps(metrics, indent=2))
    
    return metrics

def run_risk_prediction(metrics):
    """Run risk prediction using the ML model"""
    try:
        from model import predictor
        
        result = predictor.predict_risk(metrics)
        
        # Save risk-decision.json
        with open('risk-decision.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print("\n✅ risk-decision.json created")
        print(json.dumps(result, indent=2))
        
        return result
    except Exception as e:
        print(f"⚠️ Error running prediction: {e}")
        return None

if __name__ == "__main__":
    print("="*60)
    print("📊 AI DevSecOps - Metric Collector")
    print("="*60)
    
    metrics = collect_metrics()
    result = run_risk_prediction(metrics)
    
    if result:
        print("\n" + "="*60)
        print(f"🤖 Decision: {result.get('decision', 'N/A')}")
        print(f"📊 Risk Score: {result.get('risk_score', 'N/A')}%")
        print("="*60)
    else:
        print("⚠️ Run the FastAPI server first: uvicorn app:app --host 127.0.0.1 --port 8000")