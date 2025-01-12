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
    """Validate that the dataframe has all required columns with correct data types."""
    required_columns = [
        'Campaign name', 'Ad Set Name', 'Ad name', 'Results',
        'Cost per result', 'CPC (cost per link click)', 'Amount spent (GBP)'
    ]
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        logger.error(f"Missing required columns: {missing_cols}")
        return False

    # Check for numeric data types
    numeric_columns = ['Results', 'Cost per result', 'CPC (cost per link click)', 'Amount spent (GBP)']
    for col in numeric_columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            logger.error(f"Column '{col}' must be numeric")
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
    total_campaigns = len(df)
    tested_campaigns = df[
        (df['Results'] >= min_results) &
        (df['Amount spent (GBP)'] >= min_amount_spent)
    ]
    
    tested_campaigns_count = len(tested_campaigns)
    filtered_out_count = total_campaigns - tested_campaigns_count
    
    logger.info(f"Total campaigns analyzed: {total_campaigns}")
    logger.info(f"Campaigns meeting thresholds: {tested_campaigns_count}")
    logger.info(f"Campaigns filtered out: {filtered_out_count}")
    logger.info(f"Minimum thresholds: results >= {min_results}, amount spent >= {min_amount_spent} GBP")
    
    # Sort by cost per result first, then by CPC
    sorted_campaigns = tested_campaigns.sort_values(
        by=['Cost per result', 'CPC (cost per link click)'],
        ascending=[True, True]
    )
    
    return sorted_campaigns

def display_results(campaigns: pd.DataFrame) -> None:
    """Display the sorted campaign results in a formatted table and show top performer stats.
    
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
    
    # Display detailed stats for the best performing campaign
    best_campaign = campaigns.iloc[0]
    print("\nBest Performing Campaign Details:")
    print("=" * 40)
    print(f"Campaign: {best_campaign['Campaign name']}")
    print(f"Ad Set: {best_campaign['Ad Set Name']}")
    print(f"Ad: {best_campaign['Ad name']}")
    print("-" * 40)
    print(f"Results: {best_campaign['Results']:,.0f}")
    print(f"Cost per Result: £{best_campaign['Cost per result']:.2f}")
    print(f"CPC: £{best_campaign['CPC (cost per link click)']:.2f}")
    print(f"Total Spent: £{best_campaign['Amount spent (GBP)']:,.2f}")
    if 'CTR (all)' in campaigns.columns:
        print(f"CTR: {best_campaign['CTR (all)']:.2%}")
    print("=" * 40)

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