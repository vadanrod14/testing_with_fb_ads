import unittest
import pandas as pd
import os
from process_campaigns import process_campaign_data

class TestProcessCampaignData(unittest.TestCase):
    def setUp(self):
        # Create a sample CSV file for testing
        self.test_data = pd.DataFrame({
            'Campaign name': ['Test1', 'Test2'],
            'Cost per result': [10.5, 8.2],
            'CPC (cost per link click)': [0.5, 0.4],
            'Results': [100, 150],
            'Amount spent (GBP)': [1050, 1230]
        })
        self.test_data.to_csv('Historic Report CA.csv', index=False)

    def tearDown(self):
        # Clean up the test file
        if os.path.exists('Historic Report CA.csv'):
            os.remove('Historic Report CA.csv')

    def test_process_campaign_data(self):
        result = process_campaign_data()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)  # Should have both test rows
        # Check if sorting worked (Test2 should be first due to lower cost)
        self.assertEqual(result.iloc[0]['Campaign name'], 'Test2')

    def test_file_not_found(self):
        if os.path.exists('Historic Report CA.csv'):
            os.remove('Historic Report CA.csv')
        with self.assertRaises(FileNotFoundError):
            process_campaign_data()

if __name__ == '__main__':
    unittest.main()