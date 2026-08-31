# # scripts/collect_metrics.py
# import json
# import os
# import sys
# from datetime import datetime

# # Add parent directory to path so we can import model
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# def collect_metrics():
#     """Simulate collecting metrics from pipeline"""
    
#     # For demo purposes, we generate sample metrics
#     # In production, these would come from GitHub Actions
#     metrics = {
#         "test_pass_rate": 0.85,
#         "critical_vulns": 2,
#         "high_vulns": 3,
#         "medium_vulns": 5,
#         "build_time": 120,
#         "code_churn": 8,
#         "past_failures": 1,
#         "timestamp": datetime.utcnow().isoformat() + "Z"
#     }
    
#     # Save metrics.json
#     with open('metrics.json', 'w') as f:
#         json.dump(metrics, f, indent=2)
    
#     print("✅ metrics.json created")
#     print(json.dumps(metrics, indent=2))
    
#     return metrics

# def run_risk_prediction(metrics):
#     """Run risk prediction using the ML model"""
#     try:
#         from model import predictor
        
#         result = predictor.predict_risk(metrics)
        
#         # Save risk-decision.json
#         with open('risk-decision.json', 'w') as f:
#             json.dump(result, f, indent=2)
        
#         print("\n✅ risk-decision.json created")
#         print(json.dumps(result, indent=2))
        
#         return result
#     except Exception as e:
#         print(f"⚠️ Error running prediction: {e}")
#         return None

# if __name__ == "__main__":
#     print("="*60)
#     print("📊 AI DevSecOps - Metric Collector")
#     print("="*60)
    
#     metrics = collect_metrics()
#     result = run_risk_prediction(metrics)
    
#     if result:
#         print("\n" + "="*60)
#         print(f"🤖 Decision: {result.get('decision', 'N/A')}")
#         print(f"📊 Risk Score: {result.get('risk_score', 'N/A')}%")
#         print("="*60)
#     else:
#         print("⚠️ Run the FastAPI server first: uvicorn app:app --host 127.0.0.1 --port 8000")


# scripts/collect_metrics.py
import json
import os
import sys
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def parse_test_results(path="test-results/junit.xml"):
    """Parse pytest JUnit XML for real pass rate."""
    if not os.path.exists(path):
        print(f"⚠️  {path} not found — defaulting test_pass_rate to 0.0")
        return {"test_pass_rate": 0.0, "total_tests": 0, "failed_tests": 0}
    tree = ET.parse(path)
    root = tree.getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    tests = int(suite.attrib.get("tests", 0))
    failures = int(suite.attrib.get("failures", 0))
    errors = int(suite.attrib.get("errors", 0))
    failed = failures + errors
    pass_rate = (tests - failed) / tests if tests > 0 else 0.0
    return {
        "test_pass_rate": round(pass_rate, 4),
        "total_tests": tests,
        "failed_tests": failed,
    }


def parse_trivy(path="trivy-report.json"):
    """Parse Trivy JSON for real vuln counts by severity."""
    counts = {"critical_vulns": 0, "high_vulns": 0, "medium_vulns": 0}
    if not os.path.exists(path):
        print(f"⚠️  {path} not found — defaulting vuln counts to 0")
        return counts
    with open(path) as f:
        data = json.load(f)
    for result in data.get("Results", []):
        for vuln in result.get("Vulnerabilities", []) or []:
            sev = vuln.get("Severity", "").upper()
            if sev == "CRITICAL":
                counts["critical_vulns"] += 1
            elif sev == "HIGH":
                counts["high_vulns"] += 1
            elif sev == "MEDIUM":
                counts["medium_vulns"] += 1
    return counts


def parse_bandit(path="bandit-report.json"):
    """Parse Bandit JSON for real static-analysis issue count."""
    if not os.path.exists(path):
        print(f"⚠️  {path} not found — defaulting bandit_issues to 0")
        return {"bandit_issues": 0}
    with open(path) as f:
        data = json.load(f)
    return {"bandit_issues": len(data.get("results", []))}


def get_build_time():
    """Read build time in seconds, passed in via env var from the workflow."""
    val = os.environ.get("BUILD_TIME_SECONDS")
    if val is None:
        print("⚠️  BUILD_TIME_SECONDS not set — defaulting build_time to 0")
        return 0
    return int(val)


def get_code_churn():
    """Real code churn: lines changed vs previous commit."""
    try:
        out = subprocess.check_output(
            ["git", "diff", "--stat", "HEAD~1", "HEAD"], text=True
        )
        last_line = out.strip().split("\n")[-1] if out.strip() else ""
        churn = 0
        for token in last_line.replace(",", "").split():
            if token.isdigit():
                churn += int(token)
        return churn if last_line else 0
    except Exception as e:
        print(f"⚠️  Could not compute code churn: {e}")
        return 0


def collect_metrics():
    metrics = {}
    metrics.update(parse_test_results())
    metrics.update(parse_trivy())
    metrics.update(parse_bandit())
    metrics["build_time"] = get_build_time()
    metrics["code_churn"] = get_code_churn()
    metrics["past_failures"] = 0  # placeholder until historical tracking exists
    metrics["timestamp"] = datetime.utcnow().isoformat() + "Z"

    with open("metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("✅ metrics.json created (REAL data)")
    print(json.dumps(metrics, indent=2))
    return metrics


def run_risk_prediction(metrics):
    try:
        from model import predictor
        result = predictor.predict_risk(metrics)
        with open("risk-decision.json", "w") as f:
            json.dump(result, f, indent=2)
        print("\n✅ risk-decision.json created")
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        print(f"⚠️ Error running prediction: {e}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("📊 AI DevSecOps - Metric Collector")
    print("=" * 60)
    metrics = collect_metrics()
    result = run_risk_prediction(metrics)
    if result:
        print("\n" + "=" * 60)
        print(f"🤖 Decision: {result.get('decision', 'N/A')}")
        print(f"📊 Risk Score: {result.get('risk_score', 'N/A')}%")
        print("=" * 60)