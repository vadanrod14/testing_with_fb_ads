import pandas as pd
import numpy as np
import os

def process_campaign_data() -> pd.DataFrame:
    """
    Process Facebook ad campaign data from CSV file.
    Filters and sorts campaigns based on performance metrics.
    
    Returns:
        pandas.DataFrame: Sorted and filtered campaign data with performance metrics
    """
    if not os.path.exists('Historic Report CA.csv'):
        raise FileNotFoundError("Campaign data CSV file not found")

    try:
        # Read the CSV file
        df = pd.read_csv('Historic Report CA.csv')
        
        # For small datasets (less than 10 rows), skip percentile filtering
        if len(df) >= 10:
            min_results = df['Results'].quantile(0.25)  # 25th percentile for results
            min_spend = df['Amount spent (GBP)'].quantile(0.25)  # 25th percentile for spend
            
            # Filter campaigns with sufficient data
            filtered_df = df[
                (df['Results'] >= min_results) & 
                (df['Amount spent (GBP)'] >= min_spend)
            ]
        else:
            filtered_df = df  # Use all data for small datasets
        
        # Sort by cost per result and CPC
        sorted_df = filtered_df.sort_values(
            by=['Cost per result', 'CPC (cost per link click)'],
            ascending=[True, True]
        )
        
        return sorted_df
        
    except pd.errors.EmptyDataError:
        raise ValueError("CSV file is empty")
    except pd.errors.ParserError:
        raise ValueError("Error parsing CSV file")
    except pd.errors.DtypeWarning:
        raise TypeError("Data type mismatch in CSV file")
    except KeyError as e:
        raise KeyError(f"Missing expected column: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    try:
        result = process_campaign_data()
        print("\nTop performing campaigns sorted by cost per result and CPC:")
        print(result[['Campaign name', 'Cost per result', 'CPC (cost per link click)', 'Results', 'Amount spent (GBP)']].to_string())
    except Exception as e:
        print(f"Error: {e}")

# Fixes #3