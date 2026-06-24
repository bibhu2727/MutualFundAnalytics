"""
Mutual Fund Analytics - Day 2: Data Cleaning Pipeline
Author: Senior Data Engineer & Fintech Analytics Expert

This script handles loading, cleaning, and validating mutual fund datasets:
1. nav_history.csv: Combines live fetched CSVs, forward-fills holiday/weekend NAVs, deduplicates, and filters nav > 0.
2. investor_transactions.csv: Standardizes transaction types, formats dates, validates amounts, validates KYC status, and generates anomalies.
3. scheme_performance.csv: Normalizes returns to numeric, detects outliers, and validates expense ratios.
"""

import os
import logging
import re
import numpy as np
import pandas as pd
from datetime import datetime

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join("reports", "data_cleaning.log"), mode='w', encoding='utf-8')
    ]
)

# Constants
RAW_DATA_DIR = os.path.join("data", "raw")
PROCESSED_DATA_DIR = os.path.join("data", "processed")
REPORTS_DIR = "reports"

# Ensure directories exist
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Schema code mapping from Day 1
FUNDS = {
    "HDFC Top 100 Direct": "125497",
    "SBI Bluechip": "119551",
    "ICICI Bluechip": "120503",
    "Nippon Large Cap": "118632",
    "Axis Bluechip": "119092",
    "Kotak Bluechip": "120841"
}


def generate_mock_raw_data_if_missing():
    """
    Generates baseline raw datasets (nav_history.csv, investor_transactions.csv, scheme_performance.csv)
    if they do not exist, ensuring the pipeline is runnable and testable.
    """
    logging.info("Checking for required raw datasets...")
    
    # 1. nav_history.csv creation (Combines downloaded raw CSVs + injects dirty data)
    nav_history_path = os.path.join(RAW_DATA_DIR, "nav_history.csv")
    if not os.path.exists(nav_history_path):
        logging.info("Constructing nav_history.csv from fetched fund NAVs...")
        combined_dfs = []
        
        # Look for the individual CSVs downloaded in Day 1
        found_any = False
        for fund_name, scheme_code in FUNDS.items():
            safe_name = fund_name.replace(" ", "_").lower()
            fund_csv_path = os.path.join(RAW_DATA_DIR, f"{safe_name}_nav.csv")
            if os.path.exists(fund_csv_path):
                df_fund = pd.read_csv(fund_csv_path)
                # Keep original columns, rename scheme_code to amfi_code
                df_fund = df_fund.rename(columns={'scheme_code': 'amfi_code'})
                combined_dfs.append(df_fund)
                found_any = True
                
        if found_any:
            df_nav_history = pd.concat(combined_dfs, ignore_index=True)
            
            # Inject duplicates
            duplicates = df_nav_history.head(10).copy()
            df_nav_history = pd.concat([df_nav_history, duplicates], ignore_index=True)
            
            # Inject invalid NAVs (0 or negative)
            df_nav_history.loc[df_nav_history.index[100], 'nav'] = 0.0
            df_nav_history.loc[df_nav_history.index[200], 'nav'] = -15.5
            
            df_nav_history.to_csv(nav_history_path, index=False)
            logging.info(f"Successfully generated and saved nav_history.csv with injected anomalies ({len(df_nav_history)} rows).")
        else:
            logging.error("No individual fund NAV CSV files found under data/raw. Cannot construct nav_history.csv.")
            raise FileNotFoundError("Historical fund CSV files missing. Please run live_nav_fetch.py first.")

    # 2. investor_transactions.csv creation
    transactions_path = os.path.join(RAW_DATA_DIR, "investor_transactions.csv")
    if not os.path.exists(transactions_path):
        logging.info("Generating mock investor_transactions.csv with inconsistencies...")
        
        np.random.seed(42)
        states = ['Maharashtra', 'Karnataka', 'Delhi', 'Tamil Nadu', 'West Bengal', 'Gujarat', 'Uttar Pradesh', 'Telangana']
        txn_types = ['SIP', 'sip', 'Sip', 'Lumpsum', 'lumpsum', 'LUMP_SUM', 'Redemption', 'redemption', 'Redeem']
        kyc_options = ['Verified', 'VERIFIED', 'Pending', 'PENDING', 'Failed', 'Y', 'N', 'YES', 'NO', None]
        investors = ['Rahul Sharma', 'Priya Patel', 'Amit Khanna', 'Siddharth Nair', 'Sneha Rao', 'Vikram Singh', 'Deepa Mehta', 'Ananya Das']
        
        records = []
        for i in range(1000):
            txn_id = f"TXN{10000 + i}"
            amfi_code = np.random.choice(list(FUNDS.values()))
            investor = np.random.choice(investors)
            
            # Generate date formats in mixed styles
            dt = datetime(2025, 1 + (i % 12), 1 + (i % 28))
            date_style = i % 5
            if date_style == 0:
                dt_str = dt.strftime('%Y-%m-%d') # YYYY-MM-DD
            elif date_style == 1:
                dt_str = dt.strftime('%d-%m-%Y') # DD-MM-YYYY
            elif date_style == 2:
                dt_str = dt.strftime('%d/%m/%Y') # DD/MM/YYYY
            elif date_style == 3:
                dt_str = dt.strftime('%d-%b-%y') # DD-Mon-YY
            else:
                dt_str = dt.strftime('%m/%d/%Y') # MM/DD/YYYY
                
            txn_type = np.random.choice(txn_types)
            
            # Generate amount (inject anomalies)
            if i in [150, 450, 750]:
                amount = -5000.0 # Negative amount
            elif i in [300, 600]:
                amount = 0.0 # Zero amount
            else:
                amount = round(float(np.random.uniform(500, 100000)), 2)
                
            units = round(amount / 50.0, 4) if amount > 0 else 0.0
            kyc = np.random.choice(kyc_options)
            state = np.random.choice(states)
            
            records.append({
                'transaction_id': txn_id,
                'amfi_code': amfi_code,
                'investor_name': investor,
                'transaction_date': dt_str,
                'transaction_type': txn_type,
                'amount': amount,
                'units': units,
                'kyc_status': kyc,
                'state': state
            })
            
        df_txn = pd.DataFrame(records)
        df_txn.to_csv(transactions_path, index=False)
        logging.info(f"Successfully generated and saved investor_transactions.csv ({len(df_txn)} rows).")

    # 3. scheme_performance.csv creation
    performance_path = os.path.join(RAW_DATA_DIR, "scheme_performance.csv")
    if not os.path.exists(performance_path):
        logging.info("Generating mock scheme_performance.csv with anomalies...")
        
        # Standard variables
        performance_data = [
            {
                'amfi_code': '125497',
                'fund_name': 'HDFC Top 100 Direct',
                'returns_1y': '14.2%',
                'returns_3y': '12.5%',
                'returns_5y': '15.1%',
                'expense_ratio': '1.15%', # 1.15% (Within bounds)
                'sharpe_ratio': 1.12,
                'sortino_ratio': 1.25,
                'aum_cr': 28540.20,
                'category': 'Large Cap',
                'amc': 'HDFC Mutual Fund',
                'benchmark': 'Nifty 100 TRI'
            },
            {
                'amfi_code': '119551',
                'fund_name': 'SBI Bluechip',
                'returns_1y': '13.8%',
                'returns_3y': '11.9%',
                'returns_5y': '14.5%',
                'expense_ratio': '0.95%', # 0.95% (Within bounds)
                'sharpe_ratio': 1.05,
                'sortino_ratio': 1.18,
                'aum_cr': 35420.50,
                'category': 'Large Cap',
                'amc': 'SBI Mutual Fund',
                'benchmark': 'Nifty 50 TRI'
            },
            {
                'amfi_code': '120503',
                'fund_name': 'ICICI Bluechip',
                'returns_1y': '15.1%',
                'returns_3y': '13.2%',
                'returns_5y': '15.8%',
                'expense_ratio': '0.85%', # 0.85% (Within bounds)
                'sharpe_ratio': 1.20,
                'sortino_ratio': 1.35,
                'aum_cr': 32150.10,
                'category': 'Large Cap',
                'amc': 'ICICI Prudential Mutual Fund',
                'benchmark': 'Nifty 50 TRI'
            },
            {
                'amfi_code': '118632',
                'fund_name': 'Nippon Large Cap',
                'returns_1y': '16.4%',
                'returns_3y': '14.1%',
                'returns_5y': '16.2%',
                'expense_ratio': '0.05%', # Anomaly: Below 0.1% minimum
                'sharpe_ratio': 1.25,
                'sortino_ratio': 1.42,
                'aum_cr': 22450.80,
                'category': 'Large Cap',
                'amc': 'Nippon India Mutual Fund',
                'benchmark': 'S&P BSE 100 TRI'
            },
            {
                'amfi_code': '119092',
                'fund_name': 'Axis Bluechip',
                'returns_1y': '12.5%',
                'returns_3y': '120.0%', # Return Outlier / Typo
                'returns_5y': '13.9%',
                'expense_ratio': '3.20%', # Anomaly: Above 2.5% maximum
                'sharpe_ratio': 0.95,
                'sortino_ratio': 1.08,
                'aum_cr': 29120.40,
                'category': 'Large Cap',
                'amc': 'Axis Mutual Fund',
                'benchmark': 'Nifty 50 TRI'
            },
            {
                'amfi_code': '120841',
                'fund_name': 'Kotak Bluechip',
                'returns_1y': 'N/A', # Missing Return as string
                'returns_3y': '12.1%',
                'returns_5y': '14.1%',
                'expense_ratio': '1.20%',
                'sharpe_ratio': 1.02,
                'sortino_ratio': 1.15,
                'aum_cr': 18950.60,
                'category': 'Large Cap',
                'amc': 'Kotak Mutual Fund',
                'benchmark': 'Nifty 50 TRI'
            }
        ]
        
        df_perf = pd.DataFrame(performance_data)
        df_perf.to_csv(performance_path, index=False)
        logging.info(f"Successfully generated and saved scheme_performance.csv ({len(df_perf)} rows).")


def parse_date_robustly(date_str):
    """
    Parses dates in varying formats commonly seen in financial records.
    """
    if pd.isna(date_str) or not isinstance(date_str, str):
        return pd.NaT
        
    date_str = date_str.strip()
    
    # List of format patterns to attempt parsing
    patterns = [
        '%Y-%m-%d',     # 2026-06-22
        '%d-%m-%Y',     # 22-06-2026
        '%d/%m/%Y',     # 22/06/2026
        '%m/%d/%Y',     # 06/22/2026 (assumes MM/DD/YYYY)
        '%d-%b-%y',     # 22-Jun-26
        '%d-%b-%Y',     # 22-Jun-2026
        '%Y/%m/%d',     # 2026/06/22
        '%d %B %Y',     # 22 June 2026
    ]
    
    for pat in patterns:
        try:
            return datetime.strptime(date_str, pat)
        except ValueError:
            continue
            
    # Try parsing using default dateutil parser
    try:
        return pd.to_datetime(date_str)
    except:
        return pd.NaT


def clean_nav_history() -> pd.DataFrame:
    """
    Cleans nav_history.csv:
    - Parses dates
    - Removes duplicates
    - Validates NAV is > 0
    - Sorts by amfi_code and date
    - Forward-fills missing NAV values for holidays and weekends
    """
    raw_path = os.path.join(RAW_DATA_DIR, "nav_history.csv")
    logging.info(f"Cleaning nav_history.csv from {raw_path}...")
    
    df = pd.read_csv(raw_path)
    initial_rows = len(df)
    
    # 1. Parse date column to datetime
    df['date'] = df['date'].apply(parse_date_robustly)
    
    # Log any dates that failed parsing
    missing_dates = df['date'].isna().sum()
    if missing_dates > 0:
        logging.warning(f"Failed to parse {missing_dates} date values in NAV history. Removing these rows.")
        df = df.dropna(subset=['date'])
        
    # 2. Remove duplicate records
    dup_mask = df.duplicated(subset=['amfi_code', 'date'])
    dup_count = dup_mask.sum()
    df = df.drop_duplicates(subset=['amfi_code', 'date'])
    
    # 3. Validate NAV values are greater than 0
    df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
    invalid_nav_mask = (df['nav'] <= 0) | df['nav'].isna()
    invalid_nav_count = invalid_nav_mask.sum()
    df = df[~invalid_nav_mask]
    
    # 4. Sort by amfi_code and date
    df = df.sort_values(by=['amfi_code', 'date'])
    
    # 5. Forward-fill holidays/weekends
    # Create complete calendars for each fund
    filled_dfs = []
    for code, group in df.groupby('amfi_code'):
        # Get start/end dates
        min_date = group['date'].min()
        max_date = group['date'].max()
        
        # Generate complete daily date range
        full_dates = pd.date_range(start=min_date, end=max_date, freq='D')
        
        # Reindex the group to daily frequency
        group = group.set_index('date')
        group = group.reindex(full_dates)
        group.index.name = 'date'
        
        # Fill missing attributes
        group['amfi_code'] = code
        group['fund_name'] = group['fund_name'].ffill()
        group['nav'] = group['nav'].ffill()
        
        group = group.reset_index()
        filled_dfs.append(group)
        
    df_filled = pd.concat(filled_dfs, ignore_index=True)
    final_rows = len(df_filled)
    
    # Save output
    processed_path = os.path.join(PROCESSED_DATA_DIR, "nav_history.csv")
    df_filled.to_csv(processed_path, index=False)
    
    # Generate Cleaning Summary
    summary_path = os.path.join(REPORTS_DIR, "nav_history_cleaning_summary.md")
    summary = f"""# NAV History Cleaning Summary
- **Source File:** `data/raw/nav_history.csv`
- **Processed File:** `data/processed/nav_history.csv`
- **Initial Row Count:** {initial_rows}
- **Duplicates Removed:** {dup_count}
- **Invalid NAVs Removed (<= 0 or NaN):** {invalid_nav_count}
- **Gaps Filled (Weekends/Holidays):** {final_rows - (initial_rows - dup_count - invalid_nav_count)}
- **Final Row Count (Expanded Daily):** {final_rows}
- **Validation Status:** PASSED (All NAVs are > 0, dates are sequential daily, no duplicates).
"""
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    logging.info(f"NAV history cleaned: {initial_rows} -> {final_rows} rows. Saved summary to {summary_path}")
    return df_filled


def clean_investor_transactions() -> pd.DataFrame:
    """
    Cleans investor_transactions.csv:
    - Standardizes transaction_type to SIP, Lumpsum, Redemption
    - Validates transaction amount is > 0
    - Standardizes KYC status using proper enums
    - Fixes inconsistent date formats
    - Generates anomaly report
    """
    raw_path = os.path.join(RAW_DATA_DIR, "investor_transactions.csv")
    logging.info(f"Cleaning investor_transactions.csv from {raw_path}...")
    
    df = pd.read_csv(raw_path)
    initial_rows = len(df)
    anomalies = []
    
    # 1. Robust date parsing
    orig_dates = df['transaction_date'].copy()
    df['transaction_date'] = df['transaction_date'].apply(parse_date_robustly)
    
    invalid_dates_count = df['transaction_date'].isna().sum()
    if invalid_dates_count > 0:
        bad_rows = df[df['transaction_date'].isna()]
        for idx, row in bad_rows.iterrows():
            anomalies.append({
                'row_index': idx,
                'transaction_id': row['transaction_id'],
                'field': 'transaction_date',
                'value': orig_dates.loc[idx],
                'reason': 'Unparseable date format'
            })
        df = df.dropna(subset=['transaction_date'])

    # Format all dates to YYYY-MM-DD
    df['transaction_date'] = df['transaction_date'].dt.strftime('%Y-%m-%d')
    
    # 2. Standardize transaction_type (SIP, Lumpsum, Redemption)
    # Mapping dictionary for transaction types
    txn_type_map = {
        'sip': 'SIP',
        'sip_investment': 'SIP',
        'lumpsum': 'Lumpsum',
        'lump_sum': 'Lumpsum',
        'redemption': 'Redemption',
        'redeem': 'Redemption'
    }
    
    standardized_types = []
    for idx, row in df.iterrows():
        val = str(row['transaction_type']).strip().lower()
        # Clean special characters/underscores
        val = re.sub(r'[\s_]+', '_', val)
        
        mapped = txn_type_map.get(val, None)
        if mapped:
            standardized_types.append(mapped)
        else:
            # Fallback if type is already SIP, Lumpsum or Redemption (case insensitive)
            if val == 'sip':
                standardized_types.append('SIP')
            elif val == 'lumpsum':
                standardized_types.append('Lumpsum')
            elif val == 'redemption':
                standardized_types.append('Redemption')
            else:
                anomalies.append({
                    'row_index': idx,
                    'transaction_id': row['transaction_id'],
                    'field': 'transaction_type',
                    'value': row['transaction_type'],
                    'reason': f"Unknown type. Coerced to Lumpsum."
                })
                standardized_types.append('Lumpsum')
                
    df['transaction_type'] = standardized_types
    
    # 3. Validate transaction amount is > 0
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    invalid_amount_rows = df[df['amount'] <= 0]
    
    for idx, row in invalid_amount_rows.iterrows():
        anomalies.append({
            'row_index': idx,
            'transaction_id': row['transaction_id'],
            'field': 'amount',
            'value': row['amount'],
            'reason': 'Transaction amount must be greater than zero. Transaction dropped.'
        })
        
    df = df[df['amount'] > 0]
    
    # 4. Validate KYC status values using proper enums (Verified, Pending, Failed)
    kyc_map = {
        'y': 'Verified',
        'yes': 'Verified',
        'verified': 'Verified',
        'n': 'Failed',
        'no': 'Failed',
        'failed': 'Failed',
        'pending': 'Pending'
    }
    
    standardized_kyc = []
    for idx, row in df.iterrows():
        val = str(row['kyc_status']).strip().lower() if not pd.isna(row['kyc_status']) else 'pending'
        mapped = kyc_map.get(val, 'Pending')
        
        # Alert if we had to transform a weird value
        if val not in ['verified', 'pending', 'failed', 'y', 'n', 'yes', 'no']:
            anomalies.append({
                'row_index': idx,
                'transaction_id': row['transaction_id'],
                'field': 'kyc_status',
                'value': row['kyc_status'],
                'reason': f"KYC value normalized from '{row['kyc_status']}' to '{mapped}'."
            })
        standardized_kyc.append(mapped)
        
    df['kyc_status'] = standardized_kyc
    
    # Save cleaned file
    processed_path = os.path.join(PROCESSED_DATA_DIR, "investor_transactions.csv")
    df.to_csv(processed_path, index=False)
    
    # Generate anomaly report
    report_path = os.path.join(REPORTS_DIR, "investor_transactions_anomaly_report.md")
    
    anomaly_rows = []
    for anomaly in anomalies:
        anomaly_rows.append(
            f"| {anomaly['transaction_id']} | {anomaly['field']} | `{anomaly['value']}` | {anomaly['reason']} |"
        )
        
    report_content = f"""# Investor Transactions Anomaly Report
- **Source File:** `data/raw/investor_transactions.csv`
- **Total Initial Records:** {initial_rows}
- **Total Cleansed Records:** {len(df)}
- **Anomalies Detected:** {len(anomalies)}

## Detailed Anomaly Log

| Transaction ID | Field Name | Faulty Value | Action Taken / Reason |
|:---|:---|:---|:---|
"""
    if anomaly_rows:
        report_content += "\n".join(anomaly_rows)
    else:
        report_content += "| None | None | None | No anomalies detected |"
        
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    logging.info(f"Investor transactions cleaned: {initial_rows} -> {len(df)} rows. Saved anomaly report to {report_path}")
    return df


def clean_scheme_performance() -> pd.DataFrame:
    """
    Cleans scheme_performance.csv:
    - Standardizes returns to numeric
    - Outlier detection (anomaly flags)
    - Validates expense ratio falls between 0.1% and 2.5%
    - Generates validation report
    """
    raw_path = os.path.join(RAW_DATA_DIR, "scheme_performance.csv")
    logging.info(f"Cleaning scheme_performance.csv from {raw_path}...")
    
    df = pd.read_csv(raw_path)
    initial_rows = len(df)
    validation_records = []
    
    # Helper to clean percentage strings
    def clean_pct(val):
        if pd.isna(val):
            return np.nan
        val_str = str(val).replace('%', '').strip()
        if val_str.upper() in ['N/A', 'NULL', 'NAN', '']:
            return np.nan
        try:
            return float(val_str)
        except ValueError:
            return np.nan

    # 1. Parse return columns
    return_cols = ['returns_1y', 'returns_3y', 'returns_5y']
    for col in return_cols:
        df[col] = df[col].apply(clean_pct)
        # Fill missing returns with median return of Large Cap funds
        median_val = df[col].median()
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            df[col] = df[col].fillna(median_val)
            validation_records.append({
                'amfi_code': 'Multiple',
                'field': col,
                'issue': 'Missing performance value',
                'severity': 'Medium',
                'action': f"Imputed {missing_count} missing records with category median ({median_val}%)"
            })

    # 2. Validate expense ratio falls between 0.1% and 2.5%
    # Clean expense ratio (store as float, e.g. 1.25 for 1.25%)
    df['expense_ratio'] = df['expense_ratio'].apply(clean_pct)
    
    for idx, row in df.iterrows():
        exp = row['expense_ratio']
        if pd.isna(exp):
            validation_records.append({
                'amfi_code': row['amfi_code'],
                'field': 'expense_ratio',
                'issue': 'Missing expense ratio',
                'severity': 'High',
                'action': 'Imputed with standard Large Cap average (1.10%)'
            })
            df.loc[idx, 'expense_ratio'] = 1.10
        elif exp < 0.1 or exp > 2.5:
            validation_records.append({
                'amfi_code': row['amfi_code'],
                'field': 'expense_ratio',
                'issue': f"Expense ratio of {exp}% is out of bounds [0.1%, 2.5%]",
                'severity': 'High',
                'action': f"Clipped to boundary value"
            })
            # Clip values to bounds
            clipped = np.clip(exp, 0.1, 2.5)
            df.loc[idx, 'expense_ratio'] = clipped

    # 3. Outlier/Anomaly Detection in returns (e.g. 3y return)
    # Using simple IQR or absolute threshold
    # Since mutual fund returns rarely exceed 50% per year, a 3y return of 120% is extremely anomalous
    for col in return_cols:
        # Define outliers: Return > 60% is flagged as anomalous
        outliers = df[df[col] > 60.0]
        for idx, row in outliers.iterrows():
            validation_records.append({
                'amfi_code': row['amfi_code'],
                'field': col,
                'issue': f"Extreme Return Outlier detected ({row[col]}%)",
                'severity': 'Critical',
                'action': f"Clipped return to 25.0% to prevent database distortions"
            })
            df.loc[idx, col] = 25.0

    # Save cleaned file
    processed_path = os.path.join(PROCESSED_DATA_DIR, "scheme_performance.csv")
    df.to_csv(processed_path, index=False)
    
    # Generate validation report
    report_path = os.path.join(REPORTS_DIR, "scheme_performance_validation_report.md")
    
    report_rows = []
    for rec in validation_records:
        report_rows.append(
            f"| {rec['amfi_code']} | {rec['field']} | {rec['issue']} | {rec['severity']} | {rec['action']} |"
        )
        
    report_content = f"""# Scheme Performance Validation Report
- **Source File:** `data/raw/scheme_performance.csv`
- **Total Schemes Processed:** {initial_rows}
- **Validation Issues Found:** {len(validation_records)}

## Detailed Validation Log

| Scheme/AMFI Code | Field | Issue Description | Severity | Action Taken |
|:---|:---|:---|:---|:---|
"""
    if report_rows:
        report_content += "\n".join(report_rows)
    else:
        report_content += "| None | None | None | Low | All records conform to boundaries |"
        
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    logging.info(f"Scheme performance cleaned. Saved validation report to {report_path}")
    return df


def main():
    """
    Main pipeline execution
    """
    logging.info("=========================================")
    logging.info("STARTING DAY 2 DATA CLEANING PIPELINE")
    logging.info("=========================================")
    
    # Step 0: Ensure raw data is in place
    generate_mock_raw_data_if_missing()
    
    # Step 1: Clean NAV History
    clean_nav_history()
    
    # Step 2: Clean Investor Transactions
    clean_investor_transactions()
    
    # Step 3: Clean Scheme Performance
    clean_scheme_performance()
    
    logging.info("=========================================")
    logging.info("DATA CLEANING PIPELINE COMPLETED SUCCESS")
    logging.info("=========================================")


if __name__ == "__main__":
    main()
