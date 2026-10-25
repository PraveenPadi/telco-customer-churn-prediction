# Which customers are likely to leave, why, and how much revenue can we save by targeting them?

## Project Overview

This project uses the Telco Customer Churn dataset to understand
customer churn, identify patterns associated with customers leaving, and
build a foundation for predicting churn risk. The business goal is to
help a telecom company prioritize retention efforts and estimate the
potential value of successful interventions.

## Business Questions

-   **Who is likely to churn?** Identify customers with characteristics
    associated with a higher likelihood of leaving.
-   **Why might they leave?** Explore how contract type, tenure,
    services, billing, payment method, and monthly charges relate to
    churn.
-   **How much revenue could be saved?** Estimate the monthly revenue
    associated with at-risk customers and model potential retention
    scenarios. Revenue saved is an estimate, not a guaranteed outcome.

## Dataset

The file `Telco-Customer-Churn.csv` contains **7,043 rows and 21
columns**. Each row represents one customer.

  -----------------------------------------------------------------------
  Item                                Description
  ----------------------------------- -----------------------------------
  Target column                       `Churn` (`Yes` or `No`)

  Customer identifier                 `customerID`

  Customer profile                    `gender`, `SeniorCitizen`,
                                      `Partner`, `Dependents`

  Account and usage                   `tenure`, `PhoneService`,
                                      `MultipleLines`, `InternetService`

  Optional services                   `OnlineSecurity`, `OnlineBackup`,
                                      `DeviceProtection`, `TechSupport`,
                                      `StreamingTV`, `StreamingMovies`

  Contract and billing                `Contract`, `PaperlessBilling`,
                                      `PaymentMethod`

  Charges                             `MonthlyCharges`, `TotalCharges`
  -----------------------------------------------------------------------

### Initial dataset facts

-   Customer count: **7,043**
-   Number of columns: **21**
-   Customers marked as churned: **1,869**
-   Observed churn rate: **26.5%**
-   Monthly charges summed across all customer rows: **456,116.60**
-   Average monthly charge per customer: **64.76**
-   Recorded tenure range: **0--72 months**

These figures describe the supplied dataset; they do not by themselves
establish causes of churn or the revenue that a retention campaign can
recover.

## Project Workflow

1.  **Data understanding** --- inspect columns, data types, category
    values, and the distribution of `Churn`.
2.  **Data cleaning** --- check duplicate records, handle blanks, and
    convert `TotalCharges` to numeric. Validate any rows that become
    missing during conversion.
3.  **Exploratory data analysis (EDA)** --- compare churn rates across
    tenure, contract, internet service, support options, payment method,
    and charge levels.
4.  **Feature preparation** --- exclude `customerID` from model
    features, encode categorical variables, and split data into training
    and test sets using a reproducible approach.
5.  **Modeling** --- establish a baseline and compare suitable
    classifiers such as logistic regression and tree-based models.
6.  **Evaluation** --- assess precision, recall, F1-score, ROC-AUC, and
    the confusion matrix. Since retention teams have limited capacity,
    evaluate how well the model identifies likely churners at a
    practical targeting threshold.
7.  **Business impact** --- estimate the revenue associated with flagged
    customers and compare retention scenarios using explicit assumptions
    about campaign cost, intervention success, and customer value.

## Suggested Analysis

-   Churn rate by `Contract`
-   Churn rate by `tenure` bands
-   Churn rate by `InternetService` and support-related services
-   Churn rate by `PaymentMethod`
-   Distribution of `MonthlyCharges` and `TotalCharges` for churned
    versus retained customers
-   Feature importance or model explanations to understand which factors
    contribute to predictions

Associations in the data should not automatically be interpreted as
causes. Use model explanations as decision support and validate proposed
retention actions with experiments where possible.

## Revenue-Saving Framework

A simple scenario estimate is:

**Expected net value = (customers targeted × intervention success rate ×
expected retained-customer value) − campaign cost**

For a monthly revenue view, calculate the sum of `MonthlyCharges` for
customers flagged as at risk, then apply an assumed save rate and
campaign cost. This is a scenario estimate, not proof that all flagged
revenue would otherwise be lost. Use a defined time horizon and avoid
counting revenue beyond that horizon.

## Tools

A typical implementation can use:

-   Python
-   pandas and NumPy for data handling
-   Matplotlib and Seaborn for visualization
-   scikit-learn for preprocessing, model training, and evaluation
-   Jupyter Notebook for exploratory analysis

## Getting Started

1.  Place `Telco-Customer-Churn.csv` in the project directory.

2.  Install the packages needed for your analysis:

    ``` bash
    pip install pandas numpy matplotlib seaborn scikit-learn jupyter
    ```

3.  Load and inspect the data:

    ``` python
    import pandas as pd

    df = pd.read_csv("Telco-Customer-Churn.csv")
    print(df.shape)
    print(df.head())
    print(df["Churn"].value_counts(normalize=True))
    ```

4.  Continue with data cleaning, EDA, model development, and revenue
    scenario analysis.

## Important Considerations

-   Treat `customerID` as an identifier, not a predictive feature.
-   Convert `TotalCharges` to numeric and inspect conversion failures
    before modeling.
-   Prevent data leakage by fitting preprocessing steps on the training
    data only.
-   Choose a targeting threshold based on retention-team capacity and
    the costs of false positives and false negatives.
-   Evaluate whether a retention action actually changes outcomes; a
    high churn score alone does not prove that a customer can be
    persuaded to stay.
-   Confirm currency and business assumptions before interpreting charge
    totals as financial estimates.

## Expected Outcome

The project should produce an interpretable churn-risk model, a summary
of the strongest churn-associated factors, a prioritized list of
customers for review, and transparent retention scenarios showing the
potential revenue impact of targeted outreach.
