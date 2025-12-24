"""
Unit Tests for E-commerce Analysis
Test data preprocessing, analysis functions, and quality checks
"""

import unittest
import pandas as pd
import numpy as np
from data_preprocessing import DataPreprocessor
from quality_checks import DataQualityValidator
from analysis_functions import EcommerceAnalyzer

class TestDataPreprocessing(unittest.TestCase):
    """Test data preprocessing functions"""

    def setUp(self):
        """Set up test data"""
        self.preprocessor = DataPreprocessor()

    def test_load_data(self):
        """Test data loading"""
        # This would require actual test data files
        pass

class TestDataQualityValidator(unittest.TestCase):
    """Test data quality validation"""

    def setUp(self):
        """Set up test validator"""
        self.validator = DataQualityValidator()

    def test_completeness_check(self):
        """Test completeness checking"""
        # Create test dataframe with missing values
        test_df = pd.DataFrame({
            'a': [1, 2, np.nan, 4],
            'b': [5, np.nan, 7, 8]
        })

        result = self.validator.check_completeness(test_df, 'test')

        self.assertIn('completeness_score', result)
        self.assertLess(result['completeness_score'], 100)

    def test_consistency_check(self):
        """Test consistency checking"""
        test_df = pd.DataFrame({
            'id': [1, 2, 2, 4],  # Duplicate ID
            'value': [10, 20, 30, 40]
        })

        result = self.validator.check_consistency(test_df, 'test')

        self.assertIn('duplicate_rows', result)
        self.assertEqual(result['duplicate_rows'], 0)  # No full row duplicates

class TestEcommerceAnalyzer(unittest.TestCase):
    """Test core analysis functions"""

    def setUp(self):
        """Set up test data"""
        self.analyzer = EcommerceAnalyzer(data=None)

    def test_order_metrics(self):
        """Test order metrics calculation"""
        test_orders = pd.DataFrame({
            'order_id': ['O1', 'O2', 'O3'],
            'customer_id': ['C1', 'C2', 'C1'],
            'order_purchase_timestamp': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
        })

        metrics = self.analyzer.calculate_order_metrics(test_orders)

        self.assertEqual(metrics['total_orders'], 3)
        self.assertEqual(metrics['unique_customers'], 2)

    def test_temporal_analysis(self):
        """Test temporal analysis"""
        test_orders = pd.DataFrame({
            'order_id': ['O1', 'O2'],
            'order_purchase_timestamp': pd.to_datetime(['2024-01-01 10:00', '2024-01-01 14:00'])
        })

        result = self.analyzer.temporal_analysis(test_orders)

        self.assertIn('hourly_distribution', result)
        self.assertIn('daily_distribution', result)

class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def test_full_pipeline(self):
        """Test complete analysis pipeline"""
        # This would test the entire pipeline
        pass

if __name__ == '__main__':
    unittest.main()
