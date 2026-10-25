
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.utils.class_weight import compute_sample_weight

# Load dataset
df = pd.read_csv("Telco-Customer-Churn.csv")

y = df["Churn"].map({"No": 0, "Yes": 1})
X = df.drop(columns=["Churn", "customerID"], errors="ignore")

for col in ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"]:
    if col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce")

numeric = X.select_dtypes(include=["number"]).columns.tolist()
categorical = [c for c in X.columns if c not in numeric]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Preprocess data
preprocessor = ColumnTransformer([
    ("num", SimpleImputer(strategy="median"), numeric),
    ("cat", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(
            handle_unknown="ignore", sparse_output=False
        ))
    ]), categorical)
])

X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)

# Train gradient boosting model
weights = compute_sample_weight("balanced", y_train)

model = HistGradientBoostingClassifier(
    max_iter=200,
    learning_rate=0.08,
    max_leaf_nodes=15,
    l2_regularization=1.0,
    random_state=42
)

model.fit(X_train_processed, y_train, sample_weight=weights)

# Run SHAP
os.makedirs("step9_shap", exist_ok=True)

background = X_train_processed[:50]
sample = X_test_processed[:100]

explainer = shap.Explainer(model.predict_proba, background)
shap_values = explainer(
    sample,
    max_evals=2 * X_train_processed.shape[1] + 1
)

values = shap_values.values
if values.ndim == 3:
    values = values[:, :, 1]

# Group encoded features into original features
feature_names = preprocessor.get_feature_names_out()
importance = {}

for feature in X.columns:
    if feature in numeric:
        indices = [
            i for i, name in enumerate(feature_names)
            if name == f"num__{feature}"
        ]
    else:
        indices = [
            i for i, name in enumerate(feature_names)
            if name.startswith(f"cat__{feature}_")
        ]

    if indices:
        contribution = values[:, indices].sum(axis=1)
        importance[feature] = np.mean(np.abs(contribution))

results = pd.DataFrame(
    importance.items(),
    columns=["Feature", "Mean_abs_SHAP"]
).sort_values("Mean_abs_SHAP", ascending=False)

results.to_csv(
    "step9_shap/shap_feature_importance.csv", index=False
)

# Plot top 5 features
top5 = results.head(5).sort_values("Mean_abs_SHAP")

plt.figure(figsize=(9, 5))
plt.barh(top5["Feature"], top5["Mean_abs_SHAP"])
plt.xlabel("Mean absolute SHAP importance")
plt.title("Top 5 Features Influencing Customer Churn")
plt.tight_layout()
plt.savefig("step9_shap/shap_top_features.png", dpi=180)
plt.show()

print("\nTop 5 SHAP Features:")
print(results.head(5).to_string(index=False))
print("\nResults saved in the step9_shap folder.")
