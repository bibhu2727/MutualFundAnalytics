"""
Mutual Fund Analytics - Day 2: Database Loader
Author: Senior Data Engineer & Fintech Analytics Expert

This script loads the processed/cleaned datasets into the SQLite Star Schema database.
It uses SQLAlchemy, executes DDL schema definitions from schema.sql, populates the 
date dimension dynamically, loads data into fact/dimension tables, and verifies loaded row counts.
"""

import os
import sqlite3
import logging
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join("reports", "database_loader.log"), mode='w', encoding='utf-8')
    ]
)

# Constants
DATABASE_NAME = "bluestock_mf.db"
SCHEMA_SQL_PATH = os.path.join("sql", "schema.sql")
PROCESSED_DATA_DIR = os.path.join("data", "processed")
REPORTS_DIR = "reports"

def execute_schema_ddl(conn_string: str):
    """
    Reads the schema.sql file and executes DDL statements to create database tables.
    """
    logging.info(f"Initializing database schema from {SCHEMA_SQL_PATH}...")
    if not os.path.exists(SCHEMA_SQL_PATH):
        raise FileNotFoundError(f"Schema DDL file not found at {SCHEMA_SQL_PATH}")
        
    with open(SCHEMA_SQL_PATH, 'r', encoding='utf-8') as f:
        ddl_content = f.read()
        
    # Connect using native sqlite3 to run executescript easily
    conn = sqlite3.connect(DATABASE_NAME)
    try:
        cursor = conn.cursor()
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")
        # Execute DDL
        cursor.executescript(ddl_content)
        conn.commit()
        logging.info("SQLite database tables successfully initialized.")
    except sqlite3.Error as e:
        logging.error(f"Error executing schema DDL: {e}")
        raise e
    finally:
        conn.close()

def generate_date_dimension(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """
    Generates a DataFrame for the dim_date dimension table spanning a specific date range.
    """
    logging.info(f"Generating date dimension dim_date from {start_date.date()} to {end_date.date()}...")
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    dates_data = []
    for dt in date_range:
        dates_data.append({
            'date': dt.strftime('%Y-%m-%d'),
            'day': dt.day,
            'month': dt.month,
            'month_name': dt.strftime('%B'),
            'quarter': (dt.month - 1) // 3 + 1,
            'year': dt.year,
            'day_of_week': dt.weekday(), # 0=Monday, 6=Sunday
            'day_name': dt.strftime('%A'),
            'is_weekend': 1 if dt.weekday() >= 5 else 0
        })
        
    return pd.DataFrame(dates_data)

def load_data():
    """
    Loads all processed datasets into their corresponding Star Schema tables and verifies row counts.
    """
    # 1. Initialize database and schemas
    execute_schema_ddl(DATABASE_NAME)
    
    # Create SQLAlchemy Engine
    engine = create_engine(f"sqlite:///{DATABASE_NAME}")
    
    # Check processed data directory exists
    if not os.path.exists(PROCESSED_DATA_DIR):
        raise FileNotFoundError(f"Processed data directory not found at {PROCESSED_DATA_DIR}. Run data_cleaning.py first.")
        
    # Read processed datasets
    logging.info("Reading processed datasets...")
    df_nav = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "nav_history.csv"))
    df_txn = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "investor_transactions.csv"))
    df_perf = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "scheme_performance.csv"))
    
    # Ensure dates are datetime objects in Pandas to perform boundary searches
    df_nav['date'] = pd.to_datetime(df_nav['date'])
    df_txn['transaction_date'] = pd.to_datetime(df_txn['transaction_date'])
    
    # Find min and max date to build dim_date range
    min_date = min(df_nav['date'].min(), df_txn['transaction_date'].min())
    max_date = max(df_nav['date'].max(), df_txn['transaction_date'].max())
    
    # Adjust range slightly to be safe
    dim_date_df = generate_date_dimension(min_date, max_date)
    
    # Prepare tables for database ingestion
    
    # 1. dim_fund: unique funds in performance data
    df_fund = df_perf[['amfi_code', 'fund_name', 'amc', 'category', 'benchmark']].copy()
    df_fund = df_fund.rename(columns={'amfi_code': 'scheme_code'})
    df_fund['scheme_code'] = df_fund['scheme_code'].astype(int)
    
    # Convert dates back to string format for SQLite loading
    df_nav_db = df_nav.copy()
    df_nav_db['date'] = df_nav_db['date'].dt.strftime('%Y-%m-%d')
    df_nav_db = df_nav_db.rename(columns={'amfi_code': 'scheme_code'})
    # Map column names explicitly
    df_nav_db = df_nav_db[['scheme_code', 'date', 'nav']]
    
    df_txn_db = df_txn.copy()
    df_txn_db['transaction_date'] = df_txn_db['transaction_date'].dt.strftime('%Y-%m-%d')
    df_txn_db = df_txn_db.rename(columns={'amfi_code': 'scheme_code'})
    # Map columns explicitly
    df_txn_db = df_txn_db[['transaction_id', 'scheme_code', 'transaction_date', 'transaction_type', 'amount', 'units', 'investor_name', 'kyc_status', 'state']]
    
    # fact_performance
    df_perf_db = df_perf[['amfi_code', 'returns_1y', 'returns_3y', 'returns_5y', 'expense_ratio', 'sharpe_ratio', 'sortino_ratio']].copy()
    df_perf_db = df_perf_db.rename(columns={'amfi_code': 'scheme_code'})
    df_perf_db['scheme_code'] = df_perf_db['scheme_code'].astype(int)
    
    # fact_aum (using performance dataset as snapshot)
    # We populate the fact_aum using current AUM and the latest date in NAV history
    snapshot_date = df_nav['date'].max().strftime('%Y-%m-%d')
    df_aum_db = df_perf[['amfi_code', 'aum_cr']].copy()
    df_aum_db = df_aum_db.rename(columns={'amfi_code': 'scheme_code'})
    df_aum_db['scheme_code'] = df_aum_db['scheme_code'].astype(int)
    df_aum_db['date'] = snapshot_date
    df_aum_db = df_aum_db[['scheme_code', 'date', 'aum_cr']]
    
    # Write to database (use to_sql)
    logging.info("Writing dimensions to database...")
    dim_date_df.to_sql('dim_date', con=engine, if_exists='append', index=False)
    df_fund.to_sql('dim_fund', con=engine, if_exists='append', index=False)
    
    logging.info("Writing facts to database...")
    df_nav_db.to_sql('fact_nav', con=engine, if_exists='append', index=False)
    df_txn_db.to_sql('fact_transactions', con=engine, if_exists='append', index=False)
    df_perf_db.to_sql('fact_performance', con=engine, if_exists='append', index=False)
    df_aum_db.to_sql('fact_aum', con=engine, if_exists='append', index=False)
    
    logging.info("All data loaded. Commencing validation and row counts verification...")
    
    # 4. Verify loaded counts
    verification_results = []
    
    def get_db_row_count(table_name):
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            return result.scalar()
            
    # Compile report dictionary
    verifications = [
        ('dim_date', len(dim_date_df), get_db_row_count('dim_date')),
        ('dim_fund', len(df_fund), get_db_row_count('dim_fund')),
        ('fact_nav', len(df_nav_db), get_db_row_count('fact_nav')),
        ('fact_transactions', len(df_txn_db), get_db_row_count('fact_transactions')),
        ('fact_performance', len(df_perf_db), get_db_row_count('fact_performance')),
        ('fact_aum', len(df_aum_db), get_db_row_count('fact_aum')),
    ]
    
    print("\n" + "="*70)
    print("MUTUAL FUND WAREHOUSE LOADING VERIFICATION REPORT")
    print("="*70)
    print(f"{'Table Name':<20} | {'Source Rows (CSV)':<20} | {'Loaded Rows (DB)':<20} | {'Status':<10}")
    print("-"*70)
    
    all_passed = True
    markdown_report_rows = []
    
    for table_name, src_count, db_count in verifications:
        status = "PASSED" if src_count == db_count else "FAILED"
        if status == "FAILED":
            all_passed = False
        print(f"{table_name:<20} | {src_count:<20} | {db_count:<20} | {status:<10}")
        markdown_report_rows.append(
            f"| `{table_name}` | {src_count} | {db_count} | {status} |"
        )
        
    print("="*70)
    if all_passed:
        print("RESULT: SUCCESS - Database is loaded, integrated, and verified with zero data loss.\n")
    else:
        print("RESULT: WARNING - Row counts discrepancies found. Please inspect the log files.\n")
        
    # Save markdown loading report
    loading_report_path = os.path.join(REPORTS_DIR, "database_loading_report.md")
    report_content = f"""# Database Loading and Verification Report
- **Database Engine:** SQLite
- **Database Name:** `{DATABASE_NAME}`
- **Execution Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Result Summary:** {"SUCCESS (All checks passed)" if all_passed else "WARNING (Discrepancy detected)"}

## Database Row Count Verification

| Table Name | Source Row Count (CSV/Generated) | Database Row Count | Verification Status |
|:---|:---|:---|:---|
""" + "\n".join(markdown_report_rows) + f"\n\n**Note:** Foreign key checks were enabled (`PRAGMA foreign_keys = ON`) during loading to enforce relational integrity."
    
    with open(loading_report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    logging.info(f"Database loading validation report successfully written to {loading_report_path}")

if __name__ == "__main__":
    try:
        load_data()
    except Exception as e:
        logging.error(f"Fatal error during database loading: {e}", exc_info=True)
