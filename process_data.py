import pandas as pd
import numpy as np

def process_campaign_data():
    # Read the CSV file
    df = pd.read_csv('Historic Report CA.csv')
    
    # Calculate minimum thresholds (25th percentile) for results and amount spent
    min_results = df['Results'].quantile(0.25)
    min_amount_spent = df['Amount spent (GBP)'].quantile(0.25)
    
    # Filter data to ensure enough testing
    filtered_df = df[
        (df['Results'] >= min_results) & 
        (df['Amount spent (GBP)'] >= min_amount_spent)
    ]
    
    # Sort by cost per result and then by CPC
    sorted_df = filtered_df.sort_values(
        by=['Cost per result', 'CPC (cost per link click)'],
        ascending=[True, True]
    )
    
    # Display results
    print("\nProcessed Campaign Data:")
    print("------------------------")
    print(f"Total campaigns analyzed: {len(df)}")
    print(f"Campaigns meeting minimum thresholds: {len(filtered_df)}")
    print(f"Minimum results threshold (25th percentile): {min_results:.2f}")
    print(f"Minimum amount spent threshold (25th percentile): £{min_amount_spent:.2f}")
    
    print("\nTop performing campaigns (sorted by cost per result and CPC):")
    print(sorted_df[['Campaign name', 'Ad Set Name', 'Results', 
                     'Cost per result', 'CPC (cost per link click)', 
                     'Amount spent (GBP)']].to_string())
    
    return sorted_df

if __name__ == "__main__":
    try:
        result_df = process_campaign_data()
        print("\nData processing completed successfully!")
    except Exception as e:
        print(f"Error processing data: {str(e)}")

# Fixes #3