# scripts/build_dataset.py
"""
Appends the current run's metrics.json, plus an auto-computed outcome label,
as one row to dataset.csv. Run this AFTER collect_metrics.py in the pipeline.

Label rule (intentionally separate from the risk-score formula in model.py):
    outcome = 0 (FAIL) if failed_tests > 0 OR critical_vulns > 0
    outcome = 1 (SUCCESS) otherwise
"""
import json
import os
import csv
from datetime import datetime

METRICS_PATH = "metrics.json"
DATASET_PATH = "dataset.csv"

FIELDS = [
    "timestamp",
    "test_pass_rate",
    "total_tests",
    "failed_tests",
    "critical_vulns",
    "high_vulns",
    "medium_vulns",
    "bandit_issues",
    "build_time",
    "code_churn",
    "past_failures",
    "outcome",
]


def compute_label(metrics):
    """Auto-label: fail if any test failed OR any critical vuln found."""
    failed_tests = metrics.get("failed_tests", 0)
    critical_vulns = metrics.get("critical_vulns", 0)
    if failed_tests > 0 or critical_vulns > 0:
        return 0  # FAIL
    return 1  # SUCCESS


def append_row(metrics):
    row = {field: metrics.get(field, 0) for field in FIELDS if field != "outcome"}
    row["timestamp"] = metrics.get("timestamp", datetime.utcnow().isoformat() + "Z")
    row["outcome"] = compute_label(metrics)

    file_exists = os.path.exists(DATASET_PATH)
    with open(DATASET_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"✅ Appended row to {DATASET_PATH} — outcome: {'SUCCESS' if row['outcome'] == 1 else 'FAIL'}")
    return row


if __name__ == "__main__":
    if not os.path.exists(METRICS_PATH):
        print(f"❌ {METRICS_PATH} not found — run collect_metrics.py first")
        exit(1)

    with open(METRICS_PATH) as f:
        metrics = json.load(f)

    row = append_row(metrics)
    print(json.dumps(row, indent=2))