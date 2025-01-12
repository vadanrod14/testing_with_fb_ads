import pandas as pd
import argparse

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

def load_and_process_data(file_path, min_results, min_amount_spent):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Filter campaigns that have been tested enough
    tested_campaigns = df[
        (df['Results'] >= min_results) &
        (df['Amount spent (GBP)'] >= min_amount_spent)
    ]
    
    # Sort by cost per result first, then by CPC
    sorted_campaigns = tested_campaigns.sort_values(
        by=['Cost per result', 'CPC (cost per link click)'],
        ascending=[True, True]
    )
    
    return sorted_campaigns

def display_results(campaigns):
    if campaigns.empty:
        print("No campaigns meet the minimum testing criteria.")
        return
        
    print("\nTop performing campaigns (sorted by cost per result and CPC):")
    print("=" * 80)
    columns = [
        'Campaign name', 'Ad Set Name', 'Ad name',
        'Results', 'Cost per result', 'CPC (cost per link click)',
        'Amount spent (GBP)'
    ]
    print(campaigns[columns].to_string(index=False))

def main():
    args = parse_arguments()
    
    try:
        sorted_campaigns = load_and_process_data(
            args.csv_file,
            args.min_results,
            args.min_amount_spent
        )
        display_results(sorted_campaigns)
        
        # Save results to CSV
        sorted_campaigns.to_csv(args.output_file, index=False)
        print(f"\nResults have been saved to '{args.output_file}'")
        
    except FileNotFoundError:
        print(f"Error: Could not find the CSV file '{args.csv_file}'")
    except Exception as e:
        print(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()

# Fixes #1