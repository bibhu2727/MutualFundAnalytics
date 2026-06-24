# Mutual Fund Analytics

## Project Overview
This project is an end-to-end ETL (Extract, Transform, Load) pipeline for mutual fund data, developed as part of a Fintech internship capstone. The pipeline automates fetching daily Net Asset Value (NAV) data for selected mutual funds from a public API, performs data ingestion, data quality checks, and produces summary reports.

## Folder Structure
```text
MutualFundAnalytics/
│
├── data/
│   ├── raw/                  # Stores raw CSV files downloaded from API
│   └── processed/            # Stores cleaned and transformed data
├── notebooks/                # Jupyter notebooks for Exploratory Data Analysis (EDA)
├── sql/                      # SQL scripts for database operations
├── dashboard/                # Code for visual dashboards
├── reports/                  # Markdown reports detailing data quality
├── data_ingestion.py         # Script to ingest data and generate quality reports
├── live_nav_fetch.py         # Script to fetch live NAV data from API
├── requirements.txt          # Python dependencies required for the project
├── README.md                 # Project documentation
└── .gitignore                # Files to ignore in Git version control
```

## Installation Instructions

1. **Clone the repository** to your local machine:
   ```bash
   git clone <your-github-repo-url>
   cd MutualFundAnalytics
   ```

2. **Set up a virtual environment** (Highly recommended to keep dependencies isolated):
   ```bash
   python -m venv venv
   
   # Activate the environment:
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## API Details
The project retrieves mutual fund data from the public API: `https://api.mfapi.in`
- **Endpoint format**: `https://api.mfapi.in/mf/{scheme_code}`
- **Response format**: JSON containing fund metadata and a list of historical NAVs with dates.

## How to Run Scripts

### 1. Fetching Live NAV Data
Run the following command to fetch NAV data for the targeted mutual funds (HDFC, SBI, ICICI, Nippon, Axis, Kotak) and save them as CSV files:
```bash
python live_nav_fetch.py
```
*This will create several CSV files inside the `data/raw/` directory.*

### 2. Running Data Ingestion & Quality Checks
Run the following command to ingest the downloaded CSVs and automatically generate a data quality report:
```bash
python data_ingestion.py
```
*This script will output dataset summaries to the terminal and generate a `day1_data_quality_report.md` file in the `reports/` directory.*

### 3. Running Data Cleaning & ETL Pipeline (Day 2)
Run the following command to execute the robust data cleaning pipeline:
```bash
python data_cleaning.py
```
*This script will read individual fund NAV CSVs, combine them into `nav_history.csv` in `data/raw/` (and generate mock transaction/performance data if missing). It then cleans the datasets, performs validations, forward-fills weekend/holiday gaps, and saves the outputs to `data/processed/`. It also generates detailed anomaly and validation reports in `reports/`.*

### 4. Running Database Loading & Schema Verification (Day 2)
Run the following command to initialize the star schema and load the processed data into SQLite:
```bash
python database_loader.py
```
*This script reads DDL from `sql/schema.sql`, creates `bluestock_mf.db`, populates dimensions and fact tables, dynamically generates the calendar dimension `dim_date`, and runs a verification audit checking database row counts against sources.*

### 5. Running Analytical SQL Queries
Open `sql/queries.sql` to inspect or execute the 10 business-focused analytical queries (e.g., Top 5 funds by AUM, Avg Monthly NAV, YoY SIP growth, State analysis, Category-wise performance, Redemption analysis).

## Expected Outputs

**When you run `data_cleaning.py`**:
- You will see logging messages indicating raw files checks, database combinations, date parsing, gap filling, and report generation.
- Detailed markdown cleaning summaries are saved to `reports/nav_history_cleaning_summary.md`, `reports/investor_transactions_anomaly_report.md`, and `reports/scheme_performance_validation_report.md`.

**When you run `database_loader.py`**:
- A console loading report is outputted checking rows.
- The SQLite file `bluestock_mf.db` is built in the project root.
- A loading verification report is saved to `reports/database_loading_report.md`.

