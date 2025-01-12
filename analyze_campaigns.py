import pandas as pd
import argparse
import logging
import sys
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Analyze Facebook ad campaign performance data.")
    parser.add_argument('--min-results', type=int, default=100,
                      help='Minimum number of results to consider a campaign tested.')
    parser.add_argument('--min-amount-spent', type=float, default=1000,
                      help='Minimum amount spent in GBP.')
    parser.add_argument('--csv-file', type=str, default='Historic Report CA.csv',
                      help='Path to the CSV file.')
    parser.add_argument('--output-file', type=str, default='sorted_campaigns.csv',
                      help='Path to save the sorted results.')
    return parser.parse_args()

def validate_dataframe(df: pd.DataFrame) -> bool:
    """Validate that the dataframe has all required columns."""
    required_columns = [
        'Campaign name', 'Ad Set Name', 'Ad name', 'Results',
        'Cost per result', 'CPC (cost per link click)', 'Amount spent (GBP)'
    ]
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        logger.error(f"Missing required columns: {missing_cols}")
        return False
    return True

def load_and_process_data(file_path: str, min_results: int, min_amount_spent: float) -> pd.DataFrame:
    """Load and process campaign data from CSV file."""
    logger.info(f"Loading data from {file_path}")
    
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Validate dataframe
    if not validate_dataframe(df):
        raise ValueError("Invalid CSV file format")
    
    # Filter campaigns that have been tested enough
    tested_campaigns = df[
        (df['Results'] >= min_results) &
        (df['Amount spent (GBP)'] >= min_amount_spent)
    ]
    
    logger.info(f"Found {len(tested_campaigns)} campaigns meeting minimum thresholds "
                f"(min_results={min_results}, min_amount_spent={min_amount_spent})")
    
    # Sort by cost per result first, then by CPC
    sorted_campaigns = tested_campaigns.sort_values(
        by=['Cost per result', 'CPC (cost per link click)'],
        ascending=[True, True]
    )
    
    return sorted_campaigns

def display_results(campaigns: pd.DataFrame) -> None:
    """Display the sorted campaign results in a formatted table.
    
    Args:
        campaigns: DataFrame containing the sorted campaign data
    """
    if campaigns.empty:
        logger.warning("No campaigns meet the minimum testing criteria.")
        return
        
    columns = [
        'Campaign name', 'Ad Set Name', 'Ad name',
        'Results', 'Cost per result', 'CPC (cost per link click)',
        'Amount spent (GBP)'
    ]
    
    logger.info("Displaying top performing campaigns")
    print("\nTop performing campaigns (sorted by cost per result and CPC):")
    print("=" * 80)
    print(campaigns[columns].to_string(index=False))

def main() -> None:
    """Main function to execute the campaign analysis pipeline."""
    args = parse_arguments()
    
    try:
        # Load and process data
        sorted_campaigns = load_and_process_data(
            args.csv_file,
            args.min_results,
            args.min_amount_spent
        )
        
        # Display results
        display_results(sorted_campaigns)
        
        # Save results to CSV
        sorted_campaigns.to_csv(args.output_file, index=False)
        logger.info(f"Results have been saved to '{args.output_file}'")
        
    except FileNotFoundError:
        logger.error(f"Could not find the CSV file '{args.csv_file}'")
        sys.exit(1)
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error processing data: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Fixes #1