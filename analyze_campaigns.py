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
            
            # Read the Best performing Ads CSV
            best_ads_df = pd.read_csv('Best performing Ads - Sheet1.csv')
            
            # Function to calculate string similarity
            def string_similarity(a, b):
                return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

            # Create a mapping between ads using campaign name and content
            merged_df = pd.DataFrame()
            for _, row in top_5_ads.iterrows():
                ad_name = row['Ad name']
                campaign_name = row['Campaign name'].lower()
                
                # Calculate similarity scores based on campaign name and ad content
                similarity_scores = []
                for _, best_ad in best_ads_df.iterrows():
                    # Check if keywords from campaign name appear in the ad content
                    campaign_keywords = ['seniors', 'life insurance', 'family']
                    keyword_matches = sum(1 for kw in campaign_keywords if kw in campaign_name and 
                                       (kw.lower() in str(best_ad['Primary Text']).lower() or 
                                        kw.lower() in str(best_ad['Headline']).lower()))
                    
                    similarity_scores.append(keyword_matches / len(campaign_keywords))
                
                best_match_idx = np.argmax(similarity_scores)
                best_match_score = similarity_scores[best_match_idx]
                best_match = best_ads_df.iloc[best_match_idx]
                
                logging.info(f"Matching '{ad_name}' (campaign: {campaign_name}) with content: {best_match['Headline']} (score: {best_match_score:.2f})")
                
                if best_match_score > 0.3:  # At least 30% of keywords match
                    merged_row = pd.concat([row, best_match])
                    logging.info(f"Found match for '{ad_name}'")
                else:
                    # If no good match found, create a row with NaN values for best_ads columns
                    empty_best_ad = pd.Series({col: None for col in best_ads_df.columns})
                    merged_row = pd.concat([row, empty_best_ad])
                    logging.info(f"No good match found for '{ad_name}'")
                merged_df = pd.concat([merged_df, merged_row.to_frame().T], ignore_index=True)
            
            print("\nTop 5 Performing Ads with Additional Details:")
            print("-" * 100)  # Visual separator
            
            pd.set_option('display.max_colwidth', 40)  # Limit column width for better display
            formatted_df = merged_df[[
                'Ad name', 'Cost per result', 'Results', 
                'Amount spent (GBP)', 'Primary Text', 'Headline'
            ]].copy()
            
            # Format numeric columns
            formatted_df['Cost per result'] = formatted_df['Cost per result'].apply(lambda x: f'£{x:.2f}')
            formatted_df['Amount spent (GBP)'] = formatted_df['Amount spent (GBP)'].apply(lambda x: f'£{x:,.2f}')
            
            # Wrap long text
            def wrap_text(text, width=40):
                if pd.isna(text):
                    return None
                return '\n'.join(textwrap.wrap(str(text), width=width))
            
            formatted_df['Primary Text'] = formatted_df['Primary Text'].apply(wrap_text)
            formatted_df['Headline'] = formatted_df['Headline'].apply(wrap_text)
            
            # Print with better formatting
            print(formatted_df.to_string(index=False))
            print("-" * 100)  # Visual separator
        else:
            print("No campaigns met the analysis criteria")
            
    except Exception as e:
        logging.error(f"Script execution failed: {str(e)}")

# Fixes #7