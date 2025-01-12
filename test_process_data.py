import unittest
import pandas as pd
import os
from process_data import process_campaign_data

class TestProcessCampaignData(unittest.TestCase):
    def setUp(self):
        # Create a sample CSV file for testing
        self.test_data = pd.DataFrame({
            'Campaign name': ['Test Campaign 1', 'Test Campaign 2'],
            'Ad Set Name': ['Ad Set 1', 'Ad Set 2'],
            'Results': [150, 200],           # Both above 25th percentile
            'Amount spent (GBP)': [1500, 2000], # Both above 25th percentile
            'Cost per result': [10, 20],
            'CPC (cost per link click)': [0.5, 1.0]
        })
        self.test_data.to_csv('Historic Report CA.csv', index=False)

    def tearDown(self):
        # Clean up test file
        if os.path.exists('Historic Report CA.csv'):
            os.remove('Historic Report CA.csv')

    def test_file_not_found(self):
        # Remove the file to test FileNotFoundError
        os.remove('Historic Report CA.csv')
        with self.assertRaises(FileNotFoundError):
            process_campaign_data()

    def test_processing_output(self):
        df = process_campaign_data()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)  # Should contain both test records
        # Check if sorting works (Campaign 1 should be first due to lower cost)
        self.assertEqual(df.iloc[0]['Campaign name'], 'Test Campaign 1')

    def test_empty_file(self):
        # Create empty CSV file
        pd.DataFrame().to_csv('Historic Report CA.csv', index=False)
        with self.assertRaises(pd.errors.EmptyDataError):
            process_campaign_data()

    def test_missing_columns(self):
        # Create CSV with missing columns
        pd.DataFrame({'Campaign name': ['Test']}).to_csv('Historic Report CA.csv', index=False)
        with self.assertRaises(ValueError):
            process_campaign_data()

if __name__ == '__main__':
    unittest.main()