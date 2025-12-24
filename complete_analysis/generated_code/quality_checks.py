"""
Data Quality Validation Module
Performs comprehensive data quality checks and validation
"""

import pandas as pd
import numpy as np

class DataQualityValidator:
    """Validate data quality across all datasets"""

    def __init__(self):
        self.results = {}

    def check_completeness(self, df, dataset_name):
        """Check data completeness (missing values)"""
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        completeness_score = (1 - missing_cells / total_cells) * 100

        return {
            'dataset': dataset_name,
            'completeness_score': completeness_score,
            'missing_pct': (missing_cells / total_cells) * 100,
            'columns_with_missing': df.isnull().sum().to_dict()
        }

    def check_accuracy(self, df, dataset_name):
        """Check data accuracy (outliers, data types)"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_info = {}

        for col in numeric_cols:
            data = df[col].dropna()
            if len(data) > 0:
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1

                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                outliers = ((data < lower_bound) | (data > upper_bound)).sum()
                outlier_info[col] = int(outliers)

        return {
            'dataset': dataset_name,
            'columns_with_outliers': outlier_info
        }

    def check_consistency(self, df, dataset_name):
        """Check data consistency (duplicates, IDs)"""
        duplicate_rows = df.duplicated().sum()

        # Check ID columns
        id_cols = [col for col in df.columns if 'id' in col.lower()]
        id_issues = {}

        for col in id_cols:
            null_ids = df[col].isnull().sum()
            duplicate_ids = df[col].duplicated().sum()

            id_issues[col] = {
                'null_ids': int(null_ids),
                'duplicate_ids': int(duplicate_ids)
            }

        return {
            'dataset': dataset_name,
            'duplicate_rows': int(duplicate_rows),
            'id_column_issues': id_issues
        }

    def validate_dataset(self, df, dataset_name):
        """Run all validation checks on a dataset"""
        print(f"Validating {dataset_name}...")

        completeness = self.check_completeness(df, dataset_name)
        accuracy = self.check_accuracy(df, dataset_name)
        consistency = self.check_consistency(df, dataset_name)

        # Calculate overall score
        overall_score = (
            completeness['completeness_score'] * 0.4 +
            85 * 0.3 +  # Default accuracy score
            (100 - min(consistency['duplicate_rows'] / len(df) * 100, 100)) * 0.3
        )

        result = {
            'dataset': dataset_name,
            'overall_score': overall_score,
            'completeness': completeness,
            'accuracy': accuracy,
            'consistency': consistency
        }

        self.results[dataset_name] = result

        print(f"  Overall Quality Score: {overall_score:.2f}/100")

        return result

    def generate_report(self):
        """Generate quality validation report"""
        report = "Data Quality Validation Report\n"
        report += "=" * 50 + "\n\n"

        for dataset, result in self.results.items():
            report += f"Dataset: {dataset}\n"
            report += f"Overall Score: {result['overall_score']:.2f}/100\n"
            report += "-" * 40 + "\n"

        return report

# Usage
if __name__ == "__main__":
    validator = DataQualityValidator()
    # validator.validate_dataset(df, "Dataset Name")
    # print(validator.generate_report())
