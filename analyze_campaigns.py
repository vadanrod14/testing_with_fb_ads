import pandas as pd

# Read the CSV file
df = pd.read_csv('Historic Report CA.csv')

# Define minimum thresholds for testing
MIN_RESULTS = 100  # Minimum number of results to consider campaign tested
MIN_AMOUNT_SPENT = 1000  # Minimum amount spent in GBP

# Filter campaigns that have been tested enough
tested_campaigns = df[
    (df['Results'] >= MIN_RESULTS) & 
    (df['Amount spent (GBP)'] >= MIN_AMOUNT_SPENT)
]

# Sort by cost per result first, then by CPC (cost per link click)
sorted_campaigns = tested_campaigns.sort_values(
    by=['Cost per result', 'CPC (cost per link click)'],
    ascending=[True, True]
)

# Display results
print("\nTop performing campaigns (sorted by cost per result and CPC):")
print("=" * 80)
columns_to_display = [
    'Campaign name', 'Ad Set Name', 'Ad name',
    'Results', 'Cost per result', 'CPC (cost per link click)',
    'Amount spent (GBP)'
]

print(sorted_campaigns[columns_to_display].to_string(index=False))

# Save results to a new CSV
sorted_campaigns.to_csv('sorted_campaigns.csv', index=False)
print("\nResults have been saved to 'sorted_campaigns.csv'")

# Fixes #1