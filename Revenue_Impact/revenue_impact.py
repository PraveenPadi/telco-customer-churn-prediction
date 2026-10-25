"""Step 10: Revenue impact scenarios for the top 10% churn-risk customers.

Run from the project folder:
    pip install pandas numpy scikit-learn
    python step10_revenue_impact.py

Uses the same train/test split and HistGradientBoosting settings as Step 8.
Financial results are scenario estimates, not guaranteed savings.
"""
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.utils.class_weight import compute_sample_weight

DATA_PATH = "Telco-Customer-Churn.csv"
OUT_DIR = "step10_revenue"
TARGET_SHARE = 0.10
DISCOUNT_RATE = 0.15
DISCOUNT_MONTHS = 6
EXPECTED_REMAINING_LIFETIME_MONTHS = 12
SUCCESS_RATES = {"Low": 0.20, "Base": 0.30, "High": 0.40}

# Load and prepare data
df = pd.read_csv(DATA_PATH)
y = df["Churn"].map({"No": 0, "Yes": 1})
X = df.drop(columns=["Churn", "customerID"], errors="ignore").copy()

for col in ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"]:
    if col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce")

numeric = X.select_dtypes(include=["number"]).columns.tolist()
categorical = [c for c in X.columns if c not in numeric]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

preprocessor = ColumnTransformer([
    ("num", SimpleImputer(strategy="median"), numeric),
    ("cat", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ]), categorical)
])

X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)

weights = compute_sample_weight(class_weight="balanced", y=y_train)
model = HistGradientBoostingClassifier(
    max_iter=200,
    learning_rate=0.08,
    max_leaf_nodes=15,
    l2_regularization=1.0,
    random_state=42
)
model.fit(X_train_processed, y_train, sample_weight=weights)

# Select the highest-risk 10% of the held-out test customers
test_results = pd.DataFrame({
    "customerID": df.loc[X_test.index, "customerID"].values,
    "actual_churn": y_test.values,
    "churn_probability": model.predict_proba(X_test_processed)[:, 1],
    "monthly_charge": pd.to_numeric(
        df.loc[X_test.index, "MonthlyCharges"], errors="coerce"
    ).values
}).sort_values("churn_probability", ascending=False)

target_count = max(1, int(np.ceil(TARGET_SHARE * len(test_results))))
targeted = test_results.head(target_count).copy()

n = len(targeted)
avg_probability = targeted["churn_probability"].mean()
avg_monthly_charge = targeted["monthly_charge"].mean()

# As specified in the project brief
expected_saved_revenue_per_success = (
    n * avg_probability * avg_monthly_charge
    * EXPECTED_REMAINING_LIFETIME_MONTHS
)
offer_cost = n * DISCOUNT_RATE * avg_monthly_charge * DISCOUNT_MONTHS
break_even_success_rate = offer_cost / expected_saved_revenue_per_success

rows = []
for scenario, success_rate in SUCCESS_RATES.items():
    saved_revenue = expected_saved_revenue_per_success * success_rate
    net_benefit = saved_revenue - offer_cost
    rows.append({
        "Scenario": scenario,
        "Success rate": success_rate,
        "Customers targeted": n,
        "Average predicted churn probability": avg_probability,
        "Average monthly charge": avg_monthly_charge,
        "Expected saved revenue": saved_revenue,
        "Offer cost": offer_cost,
        "Net benefit": net_benefit,
        "Break-even success rate": break_even_success_rate
    })

os.makedirs(OUT_DIR, exist_ok=True)
scenario_df = pd.DataFrame(rows)
scenario_df.to_csv(f"{OUT_DIR}/revenue_impact_scenarios.csv", index=False)
targeted.to_csv(f"{OUT_DIR}/targeted_customers_top10pct.csv", index=False)

print("\nSTEP 10 — REVENUE IMPACT MODEL")
print(f"Evaluation test set: {len(test_results):,} customers")
print(f"Top 10% targeted: {n:,} customers")
print(f"Average predicted churn probability in target group: {avg_probability:.1%}")
print(f"Average monthly charge in target group: {avg_monthly_charge:.2f}")
print(f"Offer cost (15% for 6 months): {offer_cost:,.2f}")
print(f"Break-even offer success rate: {break_even_success_rate:.1%}\n")
print(scenario_df[[
    "Scenario", "Success rate", "Expected saved revenue",
    "Offer cost", "Net benefit"
]].to_string(index=False, formatters={
    "Success rate": "{:.0%}".format,
    "Expected saved revenue": "{:,.2f}".format,
    "Offer cost": "{:,.2f}".format,
    "Net benefit": "{:,.2f}".format
}))
print(f"\nFiles saved in '{OUT_DIR}/':")
print("- revenue_impact_scenarios.csv")
print("- targeted_customers_top10pct.csv")
