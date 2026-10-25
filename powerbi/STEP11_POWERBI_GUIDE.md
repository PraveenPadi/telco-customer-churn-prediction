# Step 11 — Power BI dashboard setup

## Files
- `dashboard_customers.csv`: customer attributes, actual churn, model churn probability, risk band, tenure band, and top-10%-target flag.
- `dashboard_scenarios.csv`: scenario selector values (20%, 30%, 40%).

## Import
Power BI Desktop → Home → Get data → Text/CSV → import both CSVs.
Keep `dashboard_scenarios` disconnected (do not create a relationship).

## Page 1 — Churn overview
KPI cards: Churn Rate, Revenue at Risk (Monthly), Customers in Top 10% Risk Group, Average Monthly Charge.
Suggested visuals:
- Bar chart: Contract vs Churn Rate.
- Bar chart: InternetService vs Churn Rate.
- Line chart: TenureBand vs Churn Rate. Sort TenureBand in this order: 0–6, 7–12, 13–24, 25–48, 49–60, 61–72 months.
- Slicers: Contract, InternetService, PaymentMethod, SeniorCitizen.
Note: churn by tenure band is not a true survival/retention curve.

## Page 2 — Retention action planner
- Table: customerID, Contract, tenure, MonthlyCharges, ChurnProbability, RiskBand, TargetTop10Pct. Filter TargetTop10Pct = True and sort probability descending.
- Slicer: dashboard_scenarios[Scenario].
- Cards: Targeted Customers, Projected Saved Revenue, Offer Cost, Projected Net Benefit, Break-even Success Rate.

## DAX measures
Assume tables are named `dashboard_customers` and `dashboard_scenarios`.

```DAX
Customer Count =
DISTINCTCOUNT(dashboard_customers[customerID])

Churned Customers =
CALCULATE(
    DISTINCTCOUNT(dashboard_customers[customerID]),
    dashboard_customers[Churn] = "Yes"
)

Churn Rate =
DIVIDE([Churned Customers], [Customer Count], 0)

Monthly Revenue =
SUM(dashboard_customers[MonthlyCharges])

Targeted Customers =
CALCULATE(
    DISTINCTCOUNT(dashboard_customers[customerID]),
    dashboard_customers[TargetTop10Pct] = TRUE()
)

Revenue at Risk (Monthly) =
CALCULATE(
    SUM(dashboard_customers[MonthlyCharges]),
    dashboard_customers[TargetTop10Pct] = TRUE()
)

Average Target Churn Probability =
CALCULATE(
    AVERAGE(dashboard_customers[ChurnProbability]),
    dashboard_customers[TargetTop10Pct] = TRUE()
)

Average Target Monthly Charge =
CALCULATE(
    AVERAGE(dashboard_customers[MonthlyCharges]),
    dashboard_customers[TargetTop10Pct] = TRUE()
)

Selected Success Rate =
SELECTEDVALUE(dashboard_scenarios[SuccessRate], 0.30)

Projected Saved Revenue =
[Targeted Customers]
    * [Average Target Churn Probability]
    * [Selected Success Rate]
    * [Average Target Monthly Charge]
    * 12

Offer Cost =
[Targeted Customers] * 0.15 * [Average Target Monthly Charge] * 6

Projected Net Benefit =
[Projected Saved Revenue] - [Offer Cost]

Break-even Success Rate =
DIVIDE(
    [Offer Cost],
    [Targeted Customers]
        * [Average Target Churn Probability]
        * [Average Target Monthly Charge]
        * 12,
    0
)
```

## Important notes
- Churn probability is produced by fitting the model to the full dataset, so these are in-sample scores for dashboard prototyping, not independent out-of-sample predictions. For production, use a separately validated model and calibrated probabilities.
- Revenue at risk is an estimate of monthly charges for flagged customers, not guaranteed lost revenue.
- Scenario calculations follow the project assumptions and do not account for discounting future cash flows or customers who would have stayed without the offer.
