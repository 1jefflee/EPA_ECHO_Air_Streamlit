import unittest
import pandas as pd
import zipfile
import numpy as np

class TestStreamlitApp(unittest.TestCase):

    def setUp(self):
        # Setup code for the tests
        self.zip_file_path = '../data/filtered_echo_data.zip'
        self.csv_file_name = 'filtered_echo_data.csv'
        self.df = None
        
        with zipfile.ZipFile(self.zip_file_path, 'r') as z:
            with z.open(self.csv_file_name) as f:
                self.df = pd.read_csv(f, low_memory=False)

    def _check_columns(self, expected_columns):
        """ Helper method to check if expected columns are present in the DataFrame """
        for col in expected_columns:
            self.assertIn(col, self.df.columns, f"Missing column: {col}")

    def test_data_loading(self):
        # Try block to catch failures and print custom messages
        try:
            # Ensure data loads correctly
            self.assertIsNotNone(self.df, "DataFrame should not be None")
            self.assertGreater(len(self.df), 0, "DataFrame should not be empty.")
            print("test_data_loading: Passed")
        
        except AssertionError as e:
            print(f"test_data_loading: Failed - {str(e)}")
            raise

        # Ensure required columns are present
        expected_columns = [
            'REGISTRY_ID', 'REPORTING_YEAR', 'ANNUAL_EMISSION',
            'FIPS_CODE', 'EPA_REGION_CODE', 'POSTAL_CODE'
        ]
        try:
            self._check_columns(expected_columns)
            print("test_data_loading_columns: Passed")
        except AssertionError as e:
            print(f"test_data_loading_columns: Failed - {str(e)}")
            raise

if __name__ == '__main__':
    unittest.main()