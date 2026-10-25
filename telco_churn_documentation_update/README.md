# Telco Customer Churn: Prediction, Explanation, and Retention Economics

This project explores which telecom customers are more likely to leave, evaluates churn prediction models, explains important predictors, and estimates the potential financial impact of retention offers.

> **Main result:** In the supplied dataset, **1,869 of 7,043 customers churned (26.5%)**. At a decision threshold of 0.35, logistic regression achieved ROC-AUC **0.841** and recall **90.6%**. A separate scenario analysis estimates the break-even success rate for a proposed retention offer at **8.30%**, under stated assumptions. Scenario values are not guaranteed savings.

## Project questions

- Which customer and account characteristics are associated with churn?
- How well can a model identify customers who churn?
- Which factors contribute most to model predictions?
- What might the financial impact look like if a retention offer is made to the highest-risk customers?
- How can results be communicated in a Power BI dashboard?

## Dataset

`Telco-Customer-Churn.csv` contains **7,043 rows and 21 columns**, with one row per customer. The target is `Churn` (`Yes`/`No`); `customerID` is an identifier and should not be used as a predictive feature.

| Dataset fact | Value |
|---|---:|
| Customers | 7,043 |
| Customers marked churned | 1,869 |
| Observed churn rate | 26.5% |
| Sum of monthly charges | 456,116.60 |
| Average monthly charge | 64.76 |
| Recorded tenure range | 0–72 months |

The dataset does not specify a currency in the project files, so charge values are presented in dataset units.

## Results at a glance

The models below were evaluated on the stratified 20% test split. The precision, recall, and confusion-matrix counts use a 0.35 classification threshold.

| Model | ROC-AUC | Precision | Recall | TN | FP | FN | TP |
|---|---:|---:|---:|---:|---:|---:|---:|
| Logistic regression (balanced class weights) | 0.8413 | 0.4478 | 0.9064 | 617 | 418 | 35 | 339 |
| HistGradientBoosting (balanced sample weights) | 0.8381 | 0.4668 | 0.8636 | 666 | 369 | 51 | 323 |

At this threshold, logistic regression finds more churners (higher recall), while gradient boosting has somewhat higher precision. The preferred model depends on retention capacity and the relative cost of missed churners and unnecessary offers.

The revenue scenario script ranks the held-out test customers by predicted risk and selects the top 10% (**141 customers**). For this group, the average predicted churn probability is **90.41%**, average monthly charge is **79.05**, and the modeled break-even offer success rate is **8.30%**. With a 15% discount for 6 months and an assumed 12 months of remaining customer value, estimated net benefit is **14,152.21** (20% success), **26,243.91** (30%), and **38,335.60** (40%). These are assumption-driven scenario estimates, not measured causal savings.

See [`docs/one_page_summary.md`](docs/one_page_summary.md) for the executive summary and limitations.

## Project files

- `Telco-Customer-Churn.csv` — source dataset.
- `build_model.py` — model training and evaluation workflow.
- `model_comparison.csv` — model metrics at the selected threshold.
- `confusion_matrices.png` — confusion matrix comparison.
- `roc_curve_comparison.png` — ROC curve comparison.
- `step9_shap.py` and `step9_shap/` — model explanation workflow and outputs, where generated.
- `step10_revenue_impact.py` — held-out test-set targeting and retention scenario estimates.
- `STEP11_POWERBI_GUIDE.md` — Power BI setup instructions and measures.
- `dashboard_customers.csv` and `dashboard_scenarios.csv` — Power BI prototype input files.
- `docs/one_page_summary.md` — one-page executive summary.

Generated outputs may be created in subfolders when scripts run. Check the script's `OUT_DIR` setting for the exact destination.

## Getting started

### 1. Set up Python

Use Python 3.10 or later if possible. From the project directory, install the core dependencies:

```bash
python -m pip install pandas numpy matplotlib seaborn scikit-learn
```

For SHAP explanations, install SHAP as well:

```bash
python -m pip install shap
```

### 2. Check the dataset

```python
import pandas as pd

df = pd.read_csv("Telco-Customer-Churn.csv")
print("Shape:", df.shape)
print(df["Churn"].value_counts(dropna=False))
print("Churn rate:", (df["Churn"] == "Yes").mean())
```

Expected shape: `(7043, 21)`. The observed churn rate should be approximately 26.5%.

### 3. Train and evaluate models

Run the modeling script from the directory containing the CSV:

```bash
python build_model.py
```

Review `model_comparison.csv`, `roc_curve_comparison.png`, and `confusion_matrices.png` if those outputs are produced by the script. Keep the same split and threshold when comparing metrics. ROC-AUC measures ranking quality across thresholds; precision and recall in the results table are threshold-dependent.

### 4. Run SHAP explanations

```bash
python step9_shap.py
```

Review the generated plots and tables in `step9_shap/`. Interpret these as explanations of model behavior, not proof that a feature causes churn. If SHAP is not installed or the script reports a compatibility error, install a compatible SHAP version for your Python and scikit-learn environment.

### 5. Run the retention scenario model

```bash
python step10_revenue_impact.py
```

The script uses a stratified 80/20 train/test split (`random_state=42`), fits preprocessing on the training data, trains a HistGradientBoosting classifier, and scores the held-out test set. It targets the highest-risk 10% and writes scenario results and the targeted customer list to `step10_revenue/`.

Scenario assumptions in the script:

- Targeted share: 10% of held-out test customers.
- Discount: 15% for 6 months.
- Expected remaining customer lifetime: 12 months.
- Intervention success scenarios: 20%, 30%, and 40%.

These assumptions should be reviewed with business stakeholders. The simple calculation does not establish how many customers the offer would actually save, and may count customers who would have stayed without intervention.

### 6. Build the Power BI report

Import `dashboard_customers.csv` and `dashboard_scenarios.csv` into Power BI Desktop and follow [`STEP11_POWERBI_GUIDE.md`](STEP11_POWERBI_GUIDE.md). Suggested report pages:

1. **Churn Overview:** KPI cards, churn rate by contract, internet service and tenure, plus slicers.
2. **Retention Planner:** high-risk customer table, success-rate scenario selector, projected saved revenue, offer cost, and net benefit.

**Dashboard warning:** if `dashboard_customers.csv` contains churn probabilities generated by fitting on the full dataset, those scores are in-sample prototype values. For reliable assessment or production use, generate scores for unseen customers using a model trained only on prior/training data.

## Method notes

- The target is `Churn`; `customerID` is excluded from model features.
- Numeric fields such as `TotalCharges` should be converted to numeric and conversion failures inspected.
- Imputation, encoding, and all other learned preprocessing must be fit on training data only to prevent leakage.
- The supplied model comparison uses a stratified 20% test split with `random_state=42` and a 0.35 decision threshold for precision, recall, and confusion-matrix counts.
- Model outputs are probabilities or scores, not certainties. Probability calibration should be checked before using scores as expected churn rates.

## Limitations and responsible use

1. The dataset is a snapshot and may not represent current customers or other markets.
2. Feature associations and SHAP values do not prove causation.
3. The selected threshold yields many false positives; targeting capacity and business costs should guide the threshold.
4. Revenue scenarios depend on assumed intervention success, discount, and customer lifetime. They are not observed or causal savings.
5. A controlled experiment is needed to estimate incremental retention from an offer.
6. Validate on later-period or external data, monitor drift, and review fairness and customer-impact considerations before deployment.

## Recommended next step

Run a small controlled retention pilot using the risk ranking, compare outcomes against a control group, and update the scenario assumptions with observed offer costs and incremental retention results before scaling.
