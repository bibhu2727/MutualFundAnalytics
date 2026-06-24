# Investor Transactions Anomaly Report
- **Source File:** `data/raw/investor_transactions.csv`
- **Total Initial Records:** 1000
- **Total Cleansed Records:** 995
- **Anomalies Detected:** 5

## Detailed Anomaly Log

| Transaction ID | Field Name | Faulty Value | Action Taken / Reason |
|:---|:---|:---|:---|
| TXN10150 | amount | `-5000.0` | Transaction amount must be greater than zero. Transaction dropped. |
| TXN10300 | amount | `0.0` | Transaction amount must be greater than zero. Transaction dropped. |
| TXN10450 | amount | `-5000.0` | Transaction amount must be greater than zero. Transaction dropped. |
| TXN10600 | amount | `0.0` | Transaction amount must be greater than zero. Transaction dropped. |
| TXN10750 | amount | `-5000.0` | Transaction amount must be greater than zero. Transaction dropped. |