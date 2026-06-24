# Scheme Performance Validation Report
- **Source File:** `data/raw/scheme_performance.csv`
- **Total Schemes Processed:** 6
- **Validation Issues Found:** 4

## Detailed Validation Log

| Scheme/AMFI Code | Field | Issue Description | Severity | Action Taken |
|:---|:---|:---|:---|:---|
| Multiple | returns_1y | Missing performance value | Medium | Imputed 1 missing records with category median (14.2%) |
| 118632 | expense_ratio | Expense ratio of 0.05% is out of bounds [0.1%, 2.5%] | High | Clipped to boundary value |
| 119092 | expense_ratio | Expense ratio of 3.2% is out of bounds [0.1%, 2.5%] | High | Clipped to boundary value |
| 119092 | returns_3y | Extreme Return Outlier detected (120.0%) | Critical | Clipped return to 25.0% to prevent database distortions |