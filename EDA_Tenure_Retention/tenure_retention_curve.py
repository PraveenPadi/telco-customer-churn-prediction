"""
Step 5: Retention-by-tenure curve (descriptive proxy).

This plots the share of customers in the supplied cross-sectional dataset
whose recorded tenure is at least each month. It is NOT a true cohort
retention/survival curve because signup dates and observation dates are absent.
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "Telco-Customer-Churn.csv"
OUTPUT_PATH = PROJECT_DIR / "reports" / "tenure_retention_curve.png"

df = pd.read_csv(DATA_PATH)
df["tenure"] = pd.to_numeric(df["tenure"], errors="coerce")
tenure = df["tenure"].dropna()

if tenure.empty:
    raise ValueError("No valid numeric tenure values were found.")

months = range(0, int(tenure.max()) + 1)
share_at_least_month = [(tenure >= month).mean() * 100 for month in months]

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

plt.figure(figsize=(9, 5.5))
plt.plot(months, share_at_least_month, marker=".", markersize=4)
plt.title("Share of Customers with Recorded Tenure ≥ Month")
plt.xlabel("Month (m)")
plt.ylabel("Customers with tenure ≥ m (%)")
plt.xlim(0, max(months))
plt.ylim(0, 100)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=160)
plt.show()

print(f"Customers used: {len(tenure):,}")
print(f"Maximum recorded tenure: {int(tenure.max())} months")
print(f"Saved plot to: {OUTPUT_PATH}")
