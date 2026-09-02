"""
One-time fix: recompute the 'outcome' column in dataset.csv using a
corrected label rule that accounts for the base Docker image's
baseline vulnerability floor (critical_vulns == 3 in every run,
regardless of app-level risk).

Old (broken) rule: FAIL if failed_tests > 0 OR critical_vulns > 0
New (fixed) rule:  FAIL if failed_tests > 0 OR critical_vulns > 3

Run this once locally, then commit the corrected dataset.csv.
"""
import csv

DATASET_PATH = "dataset.csv"
CRITICAL_VULN_BASELINE = 3  # observed floor from base image; app-caused
                             # critical vulns would push this higher


def compute_label(row):
    failed_tests = int(row["failed_tests"])
    critical_vulns = int(row["critical_vulns"])
    if failed_tests > 0 or critical_vulns > CRITICAL_VULN_BASELINE:
        return 0  # FAIL
    return 1  # SUCCESS


def relabel():
    with open(DATASET_PATH, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    changed = 0
    for row in rows:
        new_label = compute_label(row)
        if str(new_label) != row["outcome"]:
            changed += 1
        row["outcome"] = str(new_label)

    with open(DATASET_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Relabeled {len(rows)} rows. {changed} labels changed.")

    success_count = sum(1 for r in rows if r["outcome"] == "1")
    fail_count = sum(1 for r in rows if r["outcome"] == "0")
    print(f"   SUCCESS: {success_count}, FAIL: {fail_count}")


if __name__ == "__main__":
    relabel()