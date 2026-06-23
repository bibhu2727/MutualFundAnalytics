import requests
import pandas as pd
import logging
import os

# Set up logging for professional tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants
API_URL = "https://api.mfapi.in/mf/"
FUNDS = {
    "HDFC Top 100 Direct": "125497",
    "SBI Bluechip": "119551",
    "ICICI Bluechip": "120503",
    "Nippon Large Cap": "118632",
    "Axis Bluechip": "119092",
    "Kotak Bluechip": "120841"
}
DATA_DIR = os.path.join("data", "raw")

def fetch_nav_data(fund_name: str, scheme_code: str) -> pd.DataFrame:
    """
    Fetches NAV data for a given mutual fund scheme from mfapi.in.
    
    Args:
        fund_name (str): The name of the mutual fund.
        scheme_code (str): The AMFI scheme code for the fund.
        
    Returns:
        pd.DataFrame: A Pandas DataFrame containing the NAV history, or None if failed.
    """
    try:
        url = f"{API_URL}{scheme_code}"
        logging.info(f"Fetching data for {fund_name} (Scheme Code: {scheme_code})...")
        
        # Adding a timeout is a good practice for API requests
        response = requests.get(url, timeout=10)
        
        # Raise an exception if the HTTP request returned an unsuccessful status code
        response.raise_for_status() 
        
        data = response.json()
        
        if "data" not in data or not data["data"]:
            logging.warning(f"No NAV data found for {fund_name}.")
            return None
        
        # Extract the historical NAV data
        nav_data = data["data"]
        
        # Convert JSON to Pandas DataFrame
        df = pd.DataFrame(nav_data)
        
        # Add scheme code and fund name columns for reference
        df['scheme_code'] = scheme_code
        df['fund_name'] = fund_name
        
        # Reorder columns to make them more readable
        df = df[['scheme_code', 'fund_name', 'date', 'nav']]
        
        return df

    except requests.exceptions.RequestException as e:
        logging.error(f"Network error fetching data for {fund_name}: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred for {fund_name}: {e}")
        return None

def save_to_csv(df: pd.DataFrame, fund_name: str):
    """
    Saves the DataFrame to a CSV file in the raw data directory.
    
    Args:
        df (pd.DataFrame): The DataFrame to save.
        fund_name (str): The name of the fund used to generate the filename.
    """
    try:
        # Ensure the directory exists
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            logging.info(f"Created directory: {DATA_DIR}")
            
        # Clean fund name for file naming (e.g., "SBI Bluechip" -> "sbi_bluechip")
        safe_name = fund_name.replace(" ", "_").lower()
        file_path = os.path.join(DATA_DIR, f"{safe_name}_nav.csv")
        
        # Save DataFrame to CSV without the index column
        df.to_csv(file_path, index=False)
        logging.info(f"Successfully saved {fund_name} data to {file_path}")
        
    except Exception as e:
        logging.error(f"Error saving data for {fund_name}: {e}")

def main():
    """
    Main entry point for the script. Iterates over FUNDS and fetches data.
    """
    logging.info("Starting live NAV data fetch process...")
    
    for fund_name, scheme_code in FUNDS.items():
        df = fetch_nav_data(fund_name, scheme_code)
        
        if df is not None:
            save_to_csv(df, fund_name)
            
    logging.info("Live NAV data fetch process completed.")

if __name__ == "__main__":
    main()
