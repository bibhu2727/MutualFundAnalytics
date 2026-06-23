import pandas as pd
import os
import logging
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants for directory paths
RAW_DATA_DIR = os.path.join("data", "raw")
REPORTS_DIR = "reports"
REPORT_FILE = os.path.join(REPORTS_DIR, "day1_data_quality_report.md")

def check_required_files() -> List[str]:
    """
    Checks if required legacy datasets (fund_master.csv and nav_history.csv) exist.
    
    Returns:
        List[str]: A list of missing files.
    """
    required_files = ["fund_master.csv", "nav_history.csv"]
    missing_files = []
    
    for file in required_files:
        file_path = os.path.join(RAW_DATA_DIR, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
            
    if missing_files:
        # Display a professional warning message
        print("\n" + "!"*60)
        print("MISSING DATASET WARNING:")
        for file in missing_files:
            print(f" - '{file}' was not found in '{RAW_DATA_DIR}'.")
        print("Note: These files are required for comprehensive historical analysis.")
        print("Execution will continue with available live-fetched datasets.")
        print("!"*60 + "\n")
        
        logging.warning(f"Missing required datasets: {', '.join(missing_files)}")
    else:
        logging.info("All required baseline datasets found.")
        
    return missing_files

def read_and_summarize_data() -> Dict:
    """
    Reads all CSV files in the raw data directory, prints a summary, 
    and returns a dictionary of metrics for the report.
    
    Returns:
        Dict: Summaries for each processed dataset.
    """
    if not os.path.exists(RAW_DATA_DIR):
        logging.error(f"Directory {RAW_DATA_DIR} does not exist.")
        return {}
        
    # Get all CSV files in the raw directory
    csv_files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith('.csv')]
    
    if not csv_files:
        logging.warning(f"No CSV files found in {RAW_DATA_DIR}.")
        return {}
        
    summaries = {}
    
    for file in csv_files:
        file_path = os.path.join(RAW_DATA_DIR, file)
        try:
            # Read the CSV file into a Pandas DataFrame
            df = pd.read_csv(file_path)
            
            # Print the required data summary to console
            print("\n" + "="*50)
            print(f"Dataset Name: {file}")
            print("="*50)
            print(f"Shape (Rows, Columns): {df.shape}")
            print(f"\nColumn Names:\n{list(df.columns)}")
            print(f"\nData Types:\n{df.dtypes}")
            print(f"\nFirst 5 Rows:\n{df.head()}")
            print(f"\nMissing Values:\n{df.isnull().sum()}")
            print(f"\nDuplicate Rows: {df.duplicated().sum()}")
            print("="*50)
            
            # Store summary data to use in the Markdown report
            summaries[file] = {
                "shape": df.shape,
                "columns": list(df.columns),
                "missing_values": df.isnull().sum().to_dict(),
                "duplicate_rows": df.duplicated().sum()
            }
            
        except Exception as e:
            logging.error(f"Error reading {file}: {e}")
            
    return summaries

def validate_scheme_codes() -> Optional[Dict]:
    """
    Validates AMFI scheme codes between fund_master and nav_history, if they are present.
    
    Returns:
        Optional[Dict]: A dictionary of validation results, or None if files are missing.
    """
    master_path = os.path.join(RAW_DATA_DIR, "fund_master.csv")
    history_path = os.path.join(RAW_DATA_DIR, "nav_history.csv")
    
    # If the legacy files don't exist, we can't perform this specific validation
    if not os.path.exists(master_path) or not os.path.exists(history_path):
        logging.info("Skipping scheme code validation: 'fund_master.csv' and/or 'nav_history.csv' missing.")
        return None
        
    try:
        master_df = pd.read_csv(master_path)
        history_df = pd.read_csv(history_path)
        
        # Ensure scheme_code column exists before comparing
        if 'scheme_code' not in master_df.columns or 'scheme_code' not in history_df.columns:
            logging.error("Column 'scheme_code' missing in one of the validation datasets.")
            return None
            
        # Convert columns to sets for easy mathematical difference operations
        master_codes = set(master_df['scheme_code'].unique())
        history_codes = set(history_df['scheme_code'].unique())
        
        # Identify missing codes using set differences
        codes_in_history_not_master = history_codes - master_codes
        codes_in_master_not_history = master_codes - history_codes
        
        validation_results = {
            "total_master_codes": len(master_codes),
            "total_history_codes": len(history_codes),
            "codes_missing_in_master": len(codes_in_history_not_master),
            "codes_missing_in_history": len(codes_in_master_not_history)
        }
        
        return validation_results
        
    except Exception as e:
        logging.error(f"Error during scheme code validation: {e}")
        return None

def generate_report(summaries: Dict, validation_results: Optional[Dict]):
    """
    Generates a Markdown report summarizing data quality and saves it to the reports folder.
    
    Args:
        summaries (Dict): Dictionary containing metrics for each dataset.
        validation_results (Optional[Dict]): Results from AMFI code validation.
    """
    # Create reports directory if it doesn't exist
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
        
    report_content = ["# Day 1 Data Quality Report\n"]
    
    report_content.append("## Data Ingestion Summary\n")
    if not summaries:
        report_content.append("No datasets were processed. Please run the `live_nav_fetch.py` script first.\n")
    else:
        for file, stats in summaries.items():
            report_content.append(f"### File: `{file}`")
            report_content.append(f"- **Shape:** {stats['shape'][0]} rows, {stats['shape'][1]} columns")
            report_content.append(f"- **Columns:** {', '.join(stats['columns'])}")
            report_content.append(f"- **Duplicate Rows:** {stats['duplicate_rows']}")
            report_content.append(f"- **Missing Values:**")
            
            has_missing = False
            for col, missing in stats['missing_values'].items():
                if missing > 0:
                    report_content.append(f"  - `{col}`: {missing} missing")
                    has_missing = True
                    
            if not has_missing:
                report_content.append("  - None (Dataset is complete)")
            report_content.append("\n")
            
    report_content.append("## AMFI Scheme Code Validation\n")
    if validation_results:
        report_content.append(f"- **Total schemes in Master:** {validation_results['total_master_codes']}")
        report_content.append(f"- **Total schemes in History:** {validation_results['total_history_codes']}")
        report_content.append(f"- **Schemes in History but missing in Master:** {validation_results['codes_missing_in_master']}")
        report_content.append(f"- **Schemes in Master but missing in History:** {validation_results['codes_missing_in_history']}\n")
    else:
        report_content.append("> **Note:** Validation skipped. `fund_master.csv` and/or `nav_history.csv` were not found in the `data/raw` directory.\n")
        
    try:
        # Write the compiled content to the markdown file
        with open(REPORT_FILE, "w", encoding='utf-8') as f:
            f.write("\n".join(report_content))
        logging.info(f"Data quality report successfully saved to {REPORT_FILE}")
    except Exception as e:
        logging.error(f"Error writing report file: {e}")

def main():
    """
    Main function to execute the data ingestion and validation pipeline.
    """
    logging.info("Starting Data Ingestion Process...")
    
    # 1. Check for required baseline files
    check_required_files()
    
    # 2. Read and summarize available CSV files
    summaries = read_and_summarize_data()
    
    # 3. Validate AMFI scheme codes (if baseline files exist)
    validation_results = validate_scheme_codes()
    
    # 4. Generate Markdown report
    generate_report(summaries, validation_results)
    
    logging.info("Data Ingestion Process Completed.")

if __name__ == "__main__":
    main()
