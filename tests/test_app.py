"""
Unit tests for the Streamlit app functionality.

This module tests data loading and integrity checks for the Echo
Air Emissions data, ensuring that required columns and data
structure are present.
"""

import zipfile
import unittest
import pandas as pd

class TestStreamlitApp(unittest.TestCase):
    """
    Test class for the Streamlit app. Sets up test data and
    verifies expected behaviors and data integrity checks.
    """

    def setUp(self):
        """
        Sets up the test environment by loading the Echo Air
        Emissions data from a zipped CSV file. Data is loaded
        into a DataFrame for use in tests.
        """
        # Setup code for the tests
        self.zip_file_path = '../data/filtered_echo_data.zip'
        self.csv_file_name = 'filtered_echo_data.csv'
        self.df = None

        with zipfile.ZipFile(self.zip_file_path, 'r') as z:
            with z.open(self.csv_file_name) as f:
                self.df = pd.read_csv(f, low_memory=False)

    def _check_columns(self, expected_columns):
        """Helper method to check if expected columns are present in the DataFrame."""
        for col in expected_columns:
            self.assertIn(col, self.df.columns, f"Missing column: {col}")

    def test_data_loading(self):
        """
        Tests that the data loads correctly into a DataFrame
        and that required columns are present.
        """
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
