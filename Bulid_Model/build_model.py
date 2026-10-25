"""Step 8: Churn model comparison. Install pandas scikit-learn matplotlib."""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, precision_score, recall_score, confusion_matrix, roc_curve
from sklearn.utils.class_weight import compute_sample_weight

DATA_PATH = "Telco-Customer-Churn.csv"
OUT_DIR = "step8_model"
os.makedirs(OUT_DIR, exist_ok=True)
df = pd.read_csv(DATA_PATH)
y = df["Churn"].map({"No": 0, "Yes": 1})
X = df.drop(columns=["Churn", "customerID"], errors="ignore").copy()
for col in ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"]:
    if col in X:
        X[col] = pd.to_numeric(X[col], errors="coerce")
numeric = X.select_dtypes(include=["number"]).columns.tolist()
categorical = [c for c in X.columns if c not in numeric]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

preprocessor_lr = ColumnTransformer([
    ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric),
    ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                      ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical)
])
lr = Pipeline([("preprocess", preprocessor_lr),
               ("model", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42))])
lr.fit(X_train, y_train)
lr_prob = lr.predict_proba(X_test)[:, 1]

preprocessor_gb = ColumnTransformer([
    ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), numeric),
    ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                      ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), categorical)
])
Xtr = preprocessor_gb.fit_transform(X_train)
Xte = preprocessor_gb.transform(X_test)
weights = compute_sample_weight(class_weight="balanced", y=y_train)
gb = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.08, max_leaf_nodes=15,
                                    l2_regularization=1.0, random_state=42)
gb.fit(Xtr, y_train, sample_weight=weights)
gb_prob = gb.predict_proba(Xte)[:, 1]

threshold = 0.35
def report(name, prob):
    pred = (prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, pred, labels=[0,1]).ravel()
    return {"Model": name, "ROC-AUC": roc_auc_score(y_test, prob),
            "Precision": precision_score(y_test, pred, zero_division=0),
            "Recall": recall_score(y_test, pred, zero_division=0),
            "Threshold": threshold, "TN": tn, "FP": fp, "FN": fn, "TP": tp}

results = pd.DataFrame([report("Logistic regression (balanced)", lr_prob),
                        report("HistGradientBoosting (balanced sample weights)", gb_prob)])
results.to_csv(f"{OUT_DIR}/model_comparison.csv", index=False)
print(results.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, name, prob in [(axes[0], "Logistic regression", lr_prob), (axes[1], "Gradient boosting", gb_prob)]:
    pred = (prob >= threshold).astype(int)
    cm = confusion_matrix(y_test, pred, labels=[0,1])
    ax.imshow(cm)
    ax.set_title(name); ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
    ax.set_xticks([0,1], labels=["No churn", "Churn"]); ax.set_yticks([0,1], labels=["No churn", "Churn"])
    for (i,j), value in np.ndenumerate(cm):
        ax.text(j, i, str(value), ha="center", va="center")
fig.suptitle(f"Confusion matrices (threshold={threshold})")
fig.tight_layout(); fig.savefig(f"{OUT_DIR}/confusion_matrices.png", dpi=180); plt.close(fig)

fig, ax = plt.subplots(figsize=(7,5))
for name, prob in [("Logistic regression", lr_prob), ("Gradient boosting", gb_prob)]:
    fpr, tpr, _ = roc_curve(y_test, prob)
    ax.plot(fpr, tpr, label=f"{name} (AUC={roc_auc_score(y_test, prob):.3f})")
ax.plot([0,1], [0,1], "--"); ax.set_xlabel("False positive rate"); ax.set_ylabel("Recall")
ax.set_title("ROC curve comparison"); ax.legend(); ax.grid(alpha=.25)
fig.tight_layout(); fig.savefig(f"{OUT_DIR}/roc_curve_comparison.png", dpi=180); plt.close(fig)
