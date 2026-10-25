"""Step 7: KMeans segmentation with tenure, monthly charges, and service count."""
import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

DATA_PATH = "Telco-Customer-Churn.csv"
OUT_DIR = "step7_segments"
os.makedirs(OUT_DIR, exist_ok=True)
df = pd.read_csv(DATA_PATH)
df["tenure"] = pd.to_numeric(df["tenure"], errors="coerce")
df["MonthlyCharges"] = pd.to_numeric(df["MonthlyCharges"], errors="coerce")
service_cols = ["PhoneService", "MultipleLines", "InternetService", "OnlineSecurity", "OnlineBackup",
                "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
service_cols = [c for c in service_cols if c in df.columns]

def count_services(row):
    total = 0
    for col in service_cols:
        value = str(row[col]).strip()
        total += int(value in ("DSL", "Fiber optic")) if col == "InternetService" else int(value == "Yes")
    return total

df["service_count"] = df.apply(count_services, axis=1)
features = ["tenure", "MonthlyCharges", "service_count"]
df = df.dropna(subset=features + ["Churn"]).copy()
df["cluster"] = KMeans(n_clusters=4, random_state=42, n_init=10).fit_predict(
    StandardScaler().fit_transform(df[features])
)
summary = df.groupby("cluster").agg(
    customers=("Churn", "size"),
    median_tenure=("tenure", "median"),
    avg_monthly_charges=("MonthlyCharges", "mean"),
    avg_services=("service_count", "mean"),
    month_to_month_share=("Contract", lambda s: (s == "Month-to-month").mean() * 100),
    churn_rate=("Churn", lambda s: (s == "Yes").mean() * 100)
).reset_index()

def segment_name(r):
    if r["median_tenure"] <= 10 and r["avg_monthly_charges"] < 50:
        return "New, low-bill, fewer-service customers"
    if r["median_tenure"] <= 15 and r["avg_monthly_charges"] >= 50:
        return "Early-tenure, high-bill customers"
    if r["median_tenure"] >= 40 and r["avg_monthly_charges"] >= 60:
        return "Established, high-bill multi-service customers"
    return "Long-tenure, lower-bill customers"

summary["segment_name"] = summary.apply(segment_name, axis=1)
if summary["segment_name"].duplicated().any():
    for idx in summary.index[summary["segment_name"].duplicated(keep=False)]:
        summary.loc[idx, "segment_name"] += f" (Group {int(summary.loc[idx, 'cluster'])+1})"
summary = summary.sort_values("churn_rate", ascending=False)
summary.to_csv(f"{OUT_DIR}/segment_summary.csv", index=False)
name_map = dict(zip(summary["cluster"], summary["segment_name"]))
df["segment"] = df["cluster"].map(name_map)
df[["customerID", "segment", "tenure", "MonthlyCharges", "service_count", "Contract", "Churn"]].to_csv(
    f"{OUT_DIR}/customer_segment_assignments.csv", index=False)

plot_df = summary.sort_values("churn_rate")
plt.figure(figsize=(10, 6))
plt.barh(plot_df["segment_name"], plot_df["churn_rate"])
plt.xlabel("Churn rate (%)"); plt.ylabel("Segment"); plt.title("Customer Segment Churn Rates")
plt.grid(axis="x", alpha=.25); plt.tight_layout()
plt.savefig(f"{OUT_DIR}/segment_churn_rates.png", dpi=180, bbox_inches="tight")
plt.close()
print(summary[["segment_name", "customers", "median_tenure", "avg_monthly_charges", "avg_services",
               "month_to_month_share", "churn_rate"]].to_string(index=False))
