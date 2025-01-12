import os
import pandas as pd
import numpy as np
from typing import Optional

def process_campaign_data() -> pd.DataFrame:
    """
    Process Facebook ad campaign data from CSV file.
    Filters and sorts campaigns based on performance metrics.
    
    The function:
    1. Validates the existence of the CSV file
    2. Calculates minimum thresholds using 25th percentile
    3. Filters campaigns based on minimum results and spend
    4. Sorts by cost per result and cost per click
    
    Returns:
        pd.DataFrame: Sorted and filtered campaign data
        
    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        pd.errors.EmptyDataError: If the CSV file is empty
    """
    # Validate CSV file exists
    if not os.path.exists('Historic Report CA.csv'):
        raise FileNotFoundError("Campaign data CSV file not found")
        
    # Read the CSV file
    df = pd.read_csv('Historic Report CA.csv')
    
    # Validate DataFrame is not empty
    if df.empty:
        raise pd.errors.EmptyDataError("The CSV file is empty")
    
    # Required columns for processing
    required_columns = [
        'Results', 
        'Amount spent (GBP)', 
        'Cost per result', 
        'CPC (cost per link click)',
        'Campaign name',
        'Ad Set Name'
    ]
    
    # Validate required columns exist
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    # Validate numeric columns have valid data
    numeric_columns = ['Results', 'Amount spent (GBP)', 'Cost per result', 'CPC (cost per link click)']
    for col in numeric_columns:
        if not pd.to_numeric(df[col], errors='coerce').notnull().all():
            raise ValueError(f"Column '{col}' contains invalid numeric values")
    
    # Calculate minimum thresholds based on dataset size
    # Use mean - std for small datasets (less than 10 records)
    if len(df) < 10:
        min_results = df['Results'].mean() - df['Results'].std()
        min_amount_spent = df['Amount spent (GBP)'].mean() - df['Amount spent (GBP)'].std()
    else:
        # Use 25th percentile for larger datasets
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