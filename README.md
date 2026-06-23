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

## Expected Outputs

**When you run `live_nav_fetch.py`**:
- You will see logging messages indicating the successful retrieval of data.
- Example: `2024-05-18 10:00:00 - INFO - Successfully saved HDFC Top 100 Direct data to data\raw\hdfc_top_100_direct_nav.csv`

**When you run `data_ingestion.py`**:
- A professional warning will display if the legacy datasets `fund_master.csv` and `nav_history.csv` are missing.
- For each downloaded CSV file, a structured summary of its shape, columns, data types, first 5 rows, and missing values will be printed directly to the console.
- A final report file will be generated at `reports/day1_data_quality_report.md` for sharing with stakeholders.
