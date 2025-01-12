import pandas as pd
import numpy as np

def analyze_campaigns():
    """
    Analyze Facebook campaign data, sorting by performance metrics and filtering for statistical significance.
    
    Returns:
        pd.DataFrame: Processed and sorted campaign data
    """
    # Read the CSV file
    df = pd.read_csv('Historic Report CA.csv')
    
    # Calculate minimum thresholds (would be more meaningful with more data)
    min_results = df['Results'].median() * 0.5
    min_spend = df['Amount spent (GBP)'].median() * 0.5
    
    # Filter for campaigns with sufficient data
    significant_campaigns = df[
        (df['Results'] >= min_results) & 
        (df['Amount spent (GBP)'] >= min_spend)
    ]
    
    if len(significant_campaigns) == 0:
        print("Warning: No campaigns meet the minimum threshold criteria")
        return df
    
    # Sort by cost per result and CPC
    sorted_campaigns = significant_campaigns.sort_values(
        by=['Cost per result', 'CPC (cost per link click)'],
        ascending=[True, True]
    )
    
    return sorted_campaigns[['Campaign name', 'Ad name', 'Results', 
                           'Cost per result', 'CPC (cost per link click)', 
                           'Amount spent (GBP)', 'CTR (all)']]

if __name__ == '__main__':
    try:
        results = analyze_campaigns()
        print("\nTop performing campaigns (sorted by cost per result and CPC):")
        print(results.to_string(index=False))
    except FileNotFoundError:
        print("Error: 'Historic Report CA.csv' file not found")
    except Exception as e:
        print(f"Error processing campaign data: {str(e)}")

# Fixes #3