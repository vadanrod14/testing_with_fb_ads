import pandas as pd
import numpy as np
import logging
import textwrap
from pathlib import Path
from typing import Optional, List
from difflib import SequenceMatcher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
REQUIRED_COLUMNS = [
    'Campaign name', 'Ad Set Name', 'Ad name', 'Cost per result',
    'CPC (cost per link click)', 'Amount spent (GBP)', 'Results'
]

def analyze_campaigns(
    csv_file: str,
    min_percentile: float = 20
) -> Optional[pd.DataFrame]:
    """
    Analyze marketing campaigns by sorting them based on cost efficiency metrics.
    
    Args:
        csv_file: Path to the CSV file containing campaign data
        min_percentile: Minimum percentile threshold for filtering campaigns (0-100)
        
    Returns:
        DataFrame containing sorted and filtered campaigns, or None if validation fails
        
    Raises:
        ValueError: If min_percentile is not between 0 and 100
        FileNotFoundError: If the CSV file doesn't exist
    """
    # Validate min_percentile
    if not 0 <= min_percentile <= 100:
        raise ValueError("min_percentile must be between 0 and 100")
    
    # Check if file exists
    if not Path(csv_file).is_file():
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    try:
        # Read the CSV file
        logging.info(f"Reading CSV file: {csv_file}")
        df = pd.read_csv(csv_file)
        
        # Validate required columns
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Convert cost columns to numeric, removing currency symbols if present
        numeric_columns = ['Cost per result', 'CPC (cost per link click)', 
                         'Amount spent (GBP)', 'Results']
        
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Check for negative values
            if (df[col] < 0).any():
                logging.warning(f"Negative values found in {col}")
                
            # Check for null values after conversion
            null_count = df[col].isnull().sum()
            if null_count > 0:
                logging.warning(f"Found {null_count} null values in {col}")
        
        # Calculate minimum thresholds for spend and results
        if len(df) >= 5:
            logging.info(f"Calculating {min_percentile}th percentile thresholds")
            min_spend = df['Amount spent (GBP)'].quantile(min_percentile/100)
            min_results = df['Results'].quantile(min_percentile/100)
        else:
            logging.warning("Insufficient data for percentile calculation, using mean-based thresholds")
            min_spend = df['Amount spent (GBP)'].mean() * 0.5
            min_results = df['Results'].mean() * 0.5
        
        # Filter campaigns with sufficient data
        qualified_campaigns = df[
            (df['Amount spent (GBP)'] >= min_spend) & 
            (df['Results'] >= min_results)
        ]
        
        if qualified_campaigns.empty:
            logging.warning("No campaigns met the minimum thresholds")
            return None
        
        # Sort by cost per result first, then by CPC
        sorted_campaigns = qualified_campaigns.sort_values(
            by=['Cost per result', 'CPC (cost per link click)']
        )
        
        logging.info(f"Successfully analyzed {len(sorted_campaigns)} campaigns")
        return sorted_campaigns
        
    except Exception as e:
        logging.error(f"Error analyzing campaigns: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # Analyze the campaigns
        result = analyze_campaigns('Historic Report CA.csv')
        
        if result is not None:
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
            
            # Get top 5 performing ads
            top_5_ads = result.head(5)
            
            # Read the modified Best performing Ads CSV
            best_ads_df = pd.read_csv('Best_performing_Ads_modified.csv')
            
            # Create a copy of top_5_ads
            merged_df = top_5_ads.copy()
            merged_df = merged_df.rename(columns={'Ad name': 'Ad Name'})
            
            # Merge with best_ads_df directly on Ad Name
            merged_df = pd.merge(
                merged_df,
                best_ads_df,
                on='Ad Name',
                how='left'
            )
            
            # Drop unnecessary columns
            merged_df = merged_df.drop(['Image briefing'], axis=1, errors='ignore')
            logging.info(f"Merged {len(merged_df)} ads with Best performing Ads data")
            
            print("\nTop 5 Performing Ads with Additional Details:")
            print("-" * 100)  # Visual separator
            
            pd.set_option('display.max_colwidth', 100)  # Increase column width for better readability
            formatted_df = merged_df[[
                'Ad Name', 'Cost per result', 'Results', 
                'Amount spent (GBP)', 'Primary Text', 'Headline'
            ]].copy()
            
            # Format numeric columns
            formatted_df['Cost per result'] = formatted_df['Cost per result'].apply(lambda x: f'£{x:.2f}')
            formatted_df['Amount spent (GBP)'] = formatted_df['Amount spent (GBP)'].apply(lambda x: f'£{x:,.2f}')
            
            # Format text columns to be more readable
            def format_text(text):
                if pd.isna(text):
                    return 'N/A'
                return text.replace('\n', ' ')
            
            formatted_df['Primary Text'] = formatted_df['Primary Text'].apply(format_text)
            formatted_df['Headline'] = formatted_df['Headline'].apply(format_text)
            
            # Print with better formatting
            print("\nPerformance Metrics:")
            print(formatted_df[['Ad Name', 'Cost per result', 'Results', 'Amount spent (GBP)']].to_string(index=False))
            
            print("\nAd Content Details:")
            for _, row in formatted_df.iterrows():
                print("\n" + "-" * 80)
                print(f"Ad Name: {row['Ad Name']}")
                print(f"Primary Text: {row['Primary Text']}")
                print(f"Headline: {row['Headline']}")
            print("-" * 80)
        else:
            print("No campaigns met the analysis criteria")
            
    except Exception as e:
        logging.error(f"Script execution failed: {str(e)}")

# Fixes #7