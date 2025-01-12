import unittest
import pandas as pd
import os
from campaign_processor import process_campaign_data

class TestCampaignProcessor(unittest.TestCase):
    def test_process_campaign_data(self):
        # Test that the function runs without errors
        df = process_campaign_data()
        
        # Test that we get a DataFrame back
        self.assertIsInstance(df, pd.DataFrame)
        
        # Test that the DataFrame is sorted by cost per result
        self.assertTrue(
            df['Cost per result'].is_monotonic_increasing,
            "Data should be sorted by cost per result"
        )
        
        # Test that required columns are present
        required_columns = [
            'Campaign name', 'Results', 'Cost per result',
            'CPC (cost per link click)', 'Amount spent (GBP)',
            'efficiency_score'
        ]
        for col in required_columns:
            self.assertIn(col, df.columns)
        
        # Test that efficiency score is calculated correctly
        self.assertEqual(
            len(df['efficiency_score'].unique()),
            len(df),
            "Each row should have a unique efficiency score"
        )

if __name__ == '__main__':
    unittest.main()