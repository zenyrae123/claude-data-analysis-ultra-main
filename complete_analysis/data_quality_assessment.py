"""
Complete Data Quality Assessment for E-commerce Datasets
Analyzes all datasets in data_storage/ directory
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
import warnings
import sys
warnings.filterwarnings('ignore')

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class DataQualityAssessment:
    """Comprehensive data quality assessment framework"""

    def __init__(self, data_dir='data_storage/'):
        self.data_dir = data_dir
        self.results = {}
        self.datasets = {}

    def load_datasets(self):
        """Load all CSV datasets"""
        print("📂 Loading datasets...")
        files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]

        for file in files:
            try:
                df = pd.read_csv(os.path.join(self.data_dir, file))
                self.datasets[file] = df
                print(f"  ✓ {file}: {df.shape[0]:,} rows × {df.shape[1]} columns")
            except Exception as e:
                print(f"  ✗ {file}: Error loading - {str(e)}")

        return self.datasets

    def assess_completeness(self, df, dataset_name):
        """Assess data completeness (missing values)"""
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        completeness_score = (1 - missing_cells / total_cells) * 100

        missing_by_column = (df.isnull().sum() / len(df) * 100).round(2)
        critical_columns = missing_by_column[missing_by_column > 20].to_dict()

        return {
            'completeness_score': round(completeness_score, 2),
            'missing_cells': int(missing_cells),
            'total_cells': int(total_cells),
            'missing_percentage': round(missing_cells / total_cells * 100, 2),
            'columns_with_missing': missing_by_column.to_dict(),
            'critical_columns': critical_columns
        }

    def assess_accuracy(self, df, dataset_name):
        """Assess data accuracy (outliers and data types)"""
        issues = []

        # Check for numeric outliers using IQR method
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_count = 0

        for col in numeric_cols:
            if df[col].notna().sum() > 0:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                outlier_count += outliers

        # Check for negative values where inappropriate
        for col in numeric_cols:
            if ('price' in col.lower() or 'quantity' in col.lower() or
                'amount' in col.lower() or 'value' in col.lower()):
                if (df[col] < 0).any():
                    issues.append(f"Negative values in {col}")

        # Check data types
        type_issues = []
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                if df[col].dtype != 'datetime64[ns]':
                    try:
                        pd.to_datetime(df[col], errors='coerce')
                    except:
                        type_issues.append(f"{col} cannot be converted to datetime")

        accuracy_score = max(0, 100 - len(issues) * 5 - len(type_issues) * 3)

        return {
            'accuracy_score': round(accuracy_score, 2),
            'outlier_count': int(outlier_count),
            'data_issues': issues,
            'type_issues': type_issues
        }

    def assess_consistency(self, df, dataset_name):
        """Assess data consistency (duplicates, formats)"""
        # Check for duplicates
        duplicate_rows = df.duplicated().sum()
        duplicate_percentage = (duplicate_rows / len(df)) * 100

        # Check for ID consistency (if ID columns exist)
        id_cols = [col for col in df.columns if 'id' in col.lower()]
        consistency_issues = []

        for col in id_cols:
            # Check for NULL IDs
            if df[col].isnull().any():
                consistency_issues.append(f"NULL values found in ID column: {col}")

            # Check for duplicate IDs (if supposed to be unique)
            if df[col].duplicated().any():
                consistency_issues.append(f"Duplicate IDs found in: {col}")

        consistency_score = max(0, 100 - duplicate_percentage - len(consistency_issues) * 5)

        return {
            'consistency_score': round(consistency_score, 2),
            'duplicate_rows': int(duplicate_rows),
            'duplicate_percentage': round(duplicate_percentage, 2),
            'consistency_issues': consistency_issues
        }

    def assess_timeliness(self, df, dataset_name):
        """Assess data timeliness (date ranges, recency)"""
        date_cols = [col for col in df.columns if 'date' in col.lower()]

        timeliness_info = {}

        for col in date_cols:
            try:
                dates = pd.to_datetime(df[col], errors='coerce')
                valid_dates = dates.dropna()

                if len(valid_dates) > 0:
                    date_range = (valid_dates.max() - valid_dates.min()).days
                    most_recent = valid_dates.max()
                    oldest = valid_dates.min()

                    timeliness_info[col] = {
                        'date_range_days': int(date_range),
                        'most_recent_date': str(most_recent),
                        'oldest_date': str(oldest),
                        'valid_dates': int(len(valid_dates)),
                        'missing_dates': int(dates.isnull().sum())
                    }
            except Exception as e:
                timeliness_info[col] = {'error': str(e)}

        # Calculate timeliness score (based on data recency)
        timeliness_score = 85  # Default score
        if timeliness_info:
            # Boost score if data is recent
            for col, info in timeliness_info.items():
                if 'most_recent_date' in info:
                    try:
                        most_recent = pd.to_datetime(info['most_recent_date'])
                        days_old = (pd.Timestamp.now() - most_recent).days
                        if days_old < 30:
                            timeliness_score = min(100, timeliness_score + 5)
                    except:
                        pass

        return {
            'timeliness_score': round(timeliness_score, 2),
            'date_columns': timeliness_info
        }

    def calculate_overall_score(self, completeness, accuracy, consistency, timeliness):
        """Calculate overall data quality score"""
        weights = {
            'completeness': 0.35,
            'accuracy': 0.30,
            'consistency': 0.20,
            'timeliness': 0.15
        }

        overall_score = (
            completeness['completeness_score'] * weights['completeness'] +
            accuracy['accuracy_score'] * weights['accuracy'] +
            consistency['consistency_score'] * weights['consistency'] +
            timeliness['timeliness_score'] * weights['timeliness']
        )

        return round(overall_score, 2)

    def run_assessment(self):
        """Run complete quality assessment on all datasets"""
        print("\n" + "="*70)
        print("🔍 STAGE 1: DATA QUALITY ASSESSMENT")
        print("="*70)

        self.load_datasets()

        for dataset_name, df in self.datasets.items():
            print(f"\n📊 Analyzing: {dataset_name}")
            print("-" * 70)

            # Run all assessments
            completeness = self.assess_completeness(df, dataset_name)
            accuracy = self.assess_accuracy(df, dataset_name)
            consistency = self.assess_consistency(df, dataset_name)
            timeliness = self.assess_timeliness(df, dataset_name)

            # Calculate overall score
            overall_score = self.calculate_overall_score(
                completeness, accuracy, consistency, timeliness
            )

            # Store results
            self.results[dataset_name] = {
                'dataset_name': dataset_name,
                'shape': {'rows': int(df.shape[0]), 'columns': int(df.shape[1])},
                'completeness': completeness,
                'accuracy': accuracy,
                'consistency': consistency,
                'timeliness': timeliness,
                'overall_quality_score': overall_score
            }

            # Print summary
            print(f"  Overall Quality Score: {overall_score}/100")
            print(f"  ✓ Completeness: {completeness['completeness_score']}% (Missing: {completeness['missing_percentage']}%)")
            print(f"  ✓ Accuracy: {accuracy['accuracy_score']}% (Outliers: {accuracy['outlier_count']})")
            print(f"  ✓ Consistency: {consistency['consistency_score']}% (Duplicates: {consistency['duplicate_percentage']}%)")
            print(f"  ✓ Timeliness: {timeliness['timeliness_score']}%")

        return self.results

    def save_results(self, output_dir='complete_analysis/data_quality_report/'):
        """Save assessment results to files"""
        os.makedirs(output_dir, exist_ok=True)

        # Save JSON results
        json_path = os.path.join(output_dir, 'quality_assessment.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Quality assessment saved to: {json_path}")

        # Create issues log
        issues_log = []
        for dataset, results in self.results.items():
            issues_log.append(f"\n{'='*70}\nDataset: {dataset}\n{'='*70}")

            if results['completeness']['critical_columns']:
                issues_log.append("\n⚠️  CRITICAL: Columns with >20% missing data:")
                for col, pct in results['completeness']['critical_columns'].items():
                    issues_log.append(f"    - {col}: {pct}% missing")

            if results['accuracy']['data_issues']:
                issues_log.append("\n⚠️  Data Accuracy Issues:")
                for issue in results['accuracy']['data_issues']:
                    issues_log.append(f"    - {issue}")

            if results['consistency']['consistency_issues']:
                issues_log.append("\n⚠️  Consistency Issues:")
                for issue in results['consistency']['consistency_issues']:
                    issues_log.append(f"    - {issue}")

        log_path = os.path.join(output_dir, 'data_issues.log')
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(issues_log))
        print(f"💾 Issues log saved to: {log_path}")

        # Create recommendations
        recommendations = self.generate_recommendations()
        rec_path = os.path.join(output_dir, 'quality_improvement_recommendations.md')
        with open(rec_path, 'w', encoding='utf-8') as f:
            f.write(recommendations)
        print(f"💾 Recommendations saved to: {rec_path}")

    def generate_recommendations(self):
        """Generate quality improvement recommendations"""
        recommendations = "# Data Quality Improvement Recommendations\n\n"
        recommendations += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for dataset, results in self.results.items():
            recommendations += f"## {dataset}\n\n"
            recommendations += f"**Overall Quality Score**: {results['overall_quality_score']}/100\n\n"

            # Completeness recommendations
            if results['completeness']['completeness_score'] < 95:
                recommendations += "### Completeness Improvements\n\n"
                for col, pct in results['completeness']['columns_with_missing'].items():
                    if pct > 0:
                        recommendations += f"- **{col}**: {pct}% missing - "
                        if pct > 20:
                            recommendations += "Consider imputation or data collection\n"
                        else:
                            recommendations += "Minor missing values acceptable\n"

            # Accuracy recommendations
            if results['accuracy']['accuracy_score'] < 90:
                recommendations += "\n### Accuracy Improvements\n\n"
                for issue in results['accuracy']['data_issues']:
                    recommendations += f"- Address: {issue}\n"

            # Consistency recommendations
            if results['consistency']['duplicate_rows'] > 0:
                recommendations += f"\n### Consistency Improvements\n\n"
                recommendations += f"- Remove {results['consistency']['duplicate_rows']} duplicate rows\n"
                for issue in results['consistency']['consistency_issues']:
                    recommendations += f"- Address: {issue}\n"

            recommendations += "\n" + "-"*70 + "\n\n"

        return recommendations

    def print_summary(self):
        """Print overall summary of quality assessment"""
        print("\n" + "="*70)
        print("📋 DATA QUALITY SUMMARY")
        print("="*70)

        # Calculate average scores across all datasets
        avg_completeness = np.mean([r['completeness']['completeness_score']
                                    for r in self.results.values()])
        avg_accuracy = np.mean([r['accuracy']['accuracy_score']
                               for r in self.results.values()])
        avg_consistency = np.mean([r['consistency']['consistency_score']
                                  for r in self.results.values()])
        avg_timeliness = np.mean([r['timeliness']['timeliness_score']
                                 for r in self.results.values()])
        avg_overall = np.mean([r['overall_quality_score']
                              for r in self.results.values()])

        print(f"\n📊 Average Scores Across All Datasets:")
        print(f"  • Overall Quality: {avg_overall:.2f}/100")
        print(f"  • Completeness: {avg_completeness:.2f}%")
        print(f"  • Accuracy: {avg_accuracy:.2f}%")
        print(f"  • Consistency: {avg_consistency:.2f}%")
        print(f"  • Timeliness: {avg_timeliness:.2f}%")

        # Count datasets by quality tier
        excellent = sum(1 for r in self.results.values() if r['overall_quality_score'] >= 90)
        good = sum(1 for r in self.results.values() if 75 <= r['overall_quality_score'] < 90)
        needs_improvement = sum(1 for r in self.results.values() if r['overall_quality_score'] < 75)

        print(f"\n🎯 Quality Distribution:")
        print(f"  • Excellent (≥90): {excellent} datasets")
        print(f"  • Good (75-89): {good} datasets")
        print(f"  • Needs Improvement (<75): {needs_improvement} datasets")

        print("\n" + "="*70)

        return avg_overall

if __name__ == "__main__":
    # Run quality assessment
    assessor = DataQualityAssessment()
    results = assessor.run_assessment()
    assessor.save_results()
    overall_score = assessor.print_summary()

    print(f"\n{'='*70}")
    print("✅ STAGE 1 COMPLETE: Data Quality Assessment")
    print(f"{'='*70}")
    print(f"\nOverall Data Quality Score: {overall_score:.2f}/100")

    if overall_score >= 75:
        print("\n✓ Data quality is ACCEPTABLE for analysis")
        print("  Proceeding to Stage 2: Exploratory Data Analysis...")
    else:
        print("\n⚠️  Data quality needs improvement before proceeding")
        print("  Please review the recommendations in:")
        print("  complete_analysis/data_quality_report/quality_improvement_recommendations.md")
