import pandas as pd
import numpy as np

def analyze_campaigns(csv_file, min_percentile=20):
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Convert cost columns to numeric, removing currency symbols if present
    df['Cost per result'] = pd.to_numeric(df['Cost per result'], errors='coerce')
    df['CPC (cost per link click)'] = pd.to_numeric(df['CPC (cost per link click)'], errors='coerce')
    df['Amount spent (GBP)'] = pd.to_numeric(df['Amount spent (GBP)'], errors='coerce')
    df['Results'] = pd.to_numeric(df['Results'], errors='coerce')
    
    # Calculate minimum thresholds for spend and results (20th percentile)
    if len(df) >= 5:  # Only calculate percentiles if we have enough data
        min_spend = df['Amount spent (GBP)'].quantile(min_percentile/100)
        min_results = df['Results'].quantile(min_percentile/100)
    else:
        # If not enough data, use mean values as thresholds
        min_spend = df['Amount spent (GBP)'].mean() * 0.5
        min_results = df['Results'].mean() * 0.5
    
    # Filter campaigns with sufficient data
    qualified_campaigns = df[
        (df['Amount spent (GBP)'] >= min_spend) & 
        (df['Results'] >= min_results)
    ]
    
    # Sort by cost per result first, then by CPC
    sorted_campaigns = qualified_campaigns.sort_values(
        by=['Cost per result', 'CPC (cost per link click)']
    )
    
    return sorted_campaigns

if __name__ == "__main__":
    # Analyze the campaigns
    result = analyze_campaigns('Historic Report CA.csv')
    
    # Display results
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print("\nSorted campaigns (by cost per result and CPC):")
    print(result[['Campaign name', 'Ad Set Name', 'Ad name', 'Cost per result', 
                  'CPC (cost per link click)', 'Results', 'Amount spent (GBP)']])
    
    print("\nAnalysis Summary:")
    print(f"Total campaigns analyzed: {len(result)}")
    print(f"Average Cost per Result: £{result['Cost per result'].mean():.2f}")
    print(f"Average CPC: £{result['CPC (cost per link click)'].mean():.2f}")

# Fixes #5