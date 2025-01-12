import pandas as pd
import numpy as np

def process_campaign_data() -> pd.DataFrame:
    """
    Process Facebook ad campaign data from CSV file.
    Sorts campaigns by cost per result and cost per click, considering minimum thresholds
    for results and amount spent to ensure statistical significance.
    
    Returns:
        pandas.DataFrame: Sorted and filtered campaign data
    """
    # Read the CSV file
    df = pd.read_csv('Historic Report CA.csv')
    
    # Calculate percentiles for results and amount spent
    # Since we have a small dataset, we'll use lower thresholds
    # In a larger dataset, we would use percentiles
    min_results = df['Results'].median() * 0.5
    min_spend = df['Amount spent (GBP)'].median() * 0.5
    
    # Filter campaigns that have been tested enough
    filtered_df = df[
        (df['Results'] >= min_results) & 
        (df['Amount spent (GBP)'] >= min_spend)
    ]
    
    # Sort by cost per result first, then by CPC
    sorted_df = filtered_df.sort_values(
        by=['Cost per result', 'CPC (cost per link click)'],
        ascending=[True, True]
    )
    
    # Add efficiency score column (normalized combination of both metrics)
    sorted_df['efficiency_score'] = (
        sorted_df['Cost per result'].rank(ascending=True) + 
        sorted_df['CPC (cost per link click)'].rank(ascending=True)
    ) / 2
    
    return sorted_df

if __name__ == '__main__':
    try:
        result_df = process_campaign_data()
        print("\nProcessed Campaign Data:")
        print("------------------------")
        print(result_df[['Campaign name', 'Results', 'Cost per result', 
                        'CPC (cost per link click)', 'Amount spent (GBP)',
                        'efficiency_score']].to_string())
    except Exception as e:
        print(f"Error processing campaign data: {e}")

# Fixes #3