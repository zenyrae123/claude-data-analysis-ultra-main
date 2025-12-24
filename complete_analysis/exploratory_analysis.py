"""
Exploratory Data Analysis for E-commerce Datasets
Comprehensive statistical analysis, pattern discovery, and anomaly detection
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
import warnings
import sys
from scipy import stats
from scipy.stats import skew, kurtosis
import itertools

warnings.filterwarnings('ignore')

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class ExploratoryDataAnalysis:
    """Comprehensive exploratory data analysis framework"""

    def __init__(self, data_dir='data_storage/'):
        self.data_dir = data_dir
        self.datasets = {}
        self.analysis_results = {}

    def load_datasets(self):
        """Load all CSV datasets"""
        print("📂 Loading datasets for exploratory analysis...")
        files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]

        for file in files:
            try:
                df = pd.read_csv(os.path.join(self.data_dir, file))
                self.datasets[file] = df
                print(f"  ✓ {file}: {df.shape[0]:,} rows × {df.shape[1]} columns")
            except Exception as e:
                print(f"  ✗ {file}: Error loading - {str(e)}")

        return self.datasets

    def statistical_summary(self, df, dataset_name):
        """Generate comprehensive statistical summary"""
        print(f"\n  📊 Statistical Summary for {dataset_name}")

        summary = {
            'basic_info': {
                'rows': int(df.shape[0]),
                'columns': int(df.shape[1]),
                'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024**2, 2)
            },
            'numeric_stats': {},
            'categorical_stats': {},
            'temporal_stats': {}
        }

        # Numeric columns statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols[:10]:  # Limit to first 10 numeric columns
            data = df[col].dropna()
            if len(data) > 0:
                summary['numeric_stats'][col] = {
                    'count': int(len(data)),
                    'missing': int(df[col].isnull().sum()),
                    'mean': float(data.mean()),
                    'median': float(data.median()),
                    'std': float(data.std()),
                    'min': float(data.min()),
                    'max': float(data.max()),
                    'q25': float(data.quantile(0.25)),
                    'q75': float(data.quantile(0.75)),
                    'skewness': float(skew(data)),
                    'kurtosis': float(kurtosis(data))
                }

        # Categorical columns statistics
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols[:8]:  # Limit to first 8 categorical columns
            value_counts = df[col].value_counts()
            summary['categorical_stats'][col] = {
                'unique_count': int(df[col].nunique()),
                'most_common': value_counts.head(5).to_dict(),
                'missing': int(df[col].isnull().sum())
            }

        # Temporal columns statistics
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        for col in date_cols:
            try:
                dates = pd.to_datetime(df[col], errors='coerce')
                valid_dates = dates.dropna()
                if len(valid_dates) > 0:
                    summary['temporal_stats'][col] = {
                        'start_date': str(valid_dates.min()),
                        'end_date': str(valid_dates.max()),
                        'span_days': int((valid_dates.max() - valid_dates.min()).days),
                        'missing_count': int(dates.isnull().sum())
                    }
            except:
                pass

        print(f"    • {len(numeric_cols)} numeric columns analyzed")
        print(f"    • {len(categorical_cols)} categorical columns analyzed")
        print(f"    • {len(summary['temporal_stats'])} temporal columns analyzed")

        return summary

    def discover_patterns(self, df, dataset_name):
        """Discover patterns in the data"""
        print(f"\n  🔍 Discovering patterns in {dataset_name}")

        patterns = {
            'trends': [],
            'seasonal_patterns': [],
            'distribution_patterns': [],
            'association_patterns': []
        }

        # Check for temporal trends (if date columns exist)
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        if date_cols:
            for date_col in date_cols[:2]:  # Check up to 2 date columns
                try:
                    dates = pd.to_datetime(df[date_col], errors='coerce')
                    df_temp = df.copy()
                    df_temp['_date'] = dates
                    df_temp['_year'] = dates.dt.year
                    df_temp['_month'] = dates.dt.month
                    df_temp['_dayofweek'] = dates.dt.dayofweek

                    # Year-over-year trend
                    if df_temp['_year'].nunique() > 1:
                        yearly_counts = df_temp['_year'].value_counts().sort_index()
                        if len(yearly_counts) >= 2:
                            growth_rate = ((yearly_counts.iloc[-1] - yearly_counts.iloc[0]) /
                                         yearly_counts.iloc[0] * 100)
                            patterns['trends'].append({
                                'type': 'yearly_trend',
                                'column': date_col,
                                'growth_rate': round(growth_rate, 2),
                                'yearly_counts': yearly_counts.to_dict()
                            })

                    # Day of week pattern
                    dow_counts = df_temp['_dayofweek'].value_counts().sort_index()
                    if len(dow_counts) > 0:
                        patterns['seasonal_patterns'].append({
                            'type': 'day_of_week_pattern',
                            'column': date_col,
                            'distribution': dow_counts.to_dict()
                        })

                except Exception as e:
                    pass

        # Distribution patterns for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols[:5]:  # Check first 5 numeric columns
            data = df[col].dropna()
            if len(data) > 0:
                dist_type = 'normal'
                _, p_value = stats.normaltest(data)
                if p_value < 0.05:
                    if skew(data) > 1:
                        dist_type = 'right_skewed'
                    elif skew(data) < -1:
                        dist_type = 'left_skewed'
                    else:
                        dist_type = 'non_normal'

                patterns['distribution_patterns'].append({
                    'column': col,
                    'distribution_type': dist_type,
                    'skewness': round(float(skew(data)), 3),
                    'kurtosis': round(float(kurtosis(data)), 3)
                })

        print(f"    • {len(patterns['trends'])} trends identified")
        print(f"    • {len(patterns['seasonal_patterns'])} seasonal patterns found")
        print(f"    • {len(patterns['distribution_patterns'])} distribution patterns analyzed")

        return patterns

    def analyze_correlations(self, df, dataset_name):
        """Analyze correlations between variables"""
        print(f"\n  🔗 Analyzing correlations in {dataset_name}")

        correlations = {
            'strong_correlations': [],
            'moderate_correlations': [],
            'correlation_matrix': {}
        }

        # Only analyze numeric columns
        numeric_df = df.select_dtypes(include=[np.number])

        if numeric_df.shape[1] > 1:
            # Calculate correlation matrix
            corr_matrix = numeric_df.corr()

            # Find strong correlations (|r| > 0.7)
            strong_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:
                        strong_corr.append({
                            'variable_1': corr_matrix.columns[i],
                            'variable_2': corr_matrix.columns[j],
                            'correlation': round(float(corr_value), 3),
                            'strength': 'strong_positive' if corr_value > 0 else 'strong_negative'
                        })

            # Find moderate correlations (0.4 < |r| <= 0.7)
            moderate_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_value = corr_matrix.iloc[i, j]
                    if 0.4 < abs(corr_value) <= 0.7:
                        moderate_corr.append({
                            'variable_1': corr_matrix.columns[i],
                            'variable_2': corr_matrix.columns[j],
                            'correlation': round(float(corr_value), 3),
                            'strength': 'moderate_positive' if corr_value > 0 else 'moderate_negative'
                        })

            correlations['strong_correlations'] = strong_corr[:10]  # Limit to top 10
            correlations['moderate_correlations'] = moderate_corr[:10]

            # Store simplified correlation matrix (only top correlations)
            for col in corr_matrix.columns[:8]:  # Limit to first 8 columns
                correlations['correlation_matrix'][col] = {
                    k: round(float(v), 3) for k, v in list(corr_matrix[col].items())[:8]
                }

        print(f"    • {len(correlations['strong_correlations'])} strong correlations found")
        print(f"    • {len(correlations['moderate_correlations'])} moderate correlations found")

        return correlations

    def detect_anomalies(self, df, dataset_name):
        """Detect anomalies and outliers"""
        print(f"\n  ⚠️  Detecting anomalies in {dataset_name}")

        anomalies = {
            'statistical_outliers': [],
            'value_anomalies': [],
            'missing_data_patterns': []
        }

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols[:8]:  # Check first 8 numeric columns
            data = df[col].dropna()

            if len(data) > 0:
                # IQR method for outlier detection
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                outliers = data[(data < lower_bound) | (data > upper_bound)]

                if len(outliers) > 0:
                    outlier_pct = (len(outliers) / len(data)) * 100
                    anomalies['statistical_outliers'].append({
                        'column': col,
                        'outlier_count': int(len(outliers)),
                        'outlier_percentage': round(outlier_pct, 2),
                        'lower_bound': float(lower_bound),
                        'upper_bound': float(upper_bound),
                        'min_outlier': float(outliers.min()),
                        'max_outlier': float(outliers.max())
                    })

                # Z-score method for extreme values
                z_scores = np.abs(stats.zscore(data))
                extreme_outliers = data[z_scores > 3]
                if len(extreme_outliers) > 0:
                    anomalies['value_anomalies'].append({
                        'column': col,
                        'extreme_outlier_count': int(len(extreme_outliers)),
                        'sample_values': extreme_outliers.head(3).tolist()
                    })

        # Missing data patterns
        for col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 0:
                anomalies['missing_data_patterns'].append({
                    'column': col,
                    'missing_percentage': round(missing_pct, 2),
                    'missing_count': int(df[col].isnull().sum())
                })

        print(f"    • {len(anomalies['statistical_outliers'])} columns with outliers")
        print(f"    • {len(anomalies['value_anomalies'])} columns with extreme values")
        print(f"    • {len(anomalies['missing_data_patterns'])} columns with missing data")

        return anomalies

    def cross_dataset_analysis(self):
        """Perform cross-dataset analysis"""
        print("\n  🔄 Performing cross-dataset analysis...")

        cross_analysis = {
            'relationships': [],
            'merged_insights': []
        }

        # Try to merge related datasets
        if 'Orders.csv' in self.datasets and 'Order Items.csv' in self.datasets:
            orders = self.datasets['Orders.csv']
            order_items = self.datasets['Order Items.csv']

            # Merge orders with items
            merged = pd.merge(orders, order_items, on='order_id', how='inner')

            if len(merged) > 0:
                # Calculate average order value
                if 'price' in merged.columns and 'freight_value' in merged.columns:
                    merged['total_value'] = merged['price'] + merged['freight_value']
                    avg_order_value = merged['total_value'].mean()

                    cross_analysis['relationships'].append({
                        'datasets': ['Orders.csv', 'Order Items.csv'],
                        'merge_key': 'order_id',
                        'merged_records': int(len(merged)),
                        'insights': {
                            'average_order_value': round(float(avg_order_value), 2),
                            'total_records_analyzed': int(len(merged))
                        }
                    })

        if 'Customers.csv' in self.datasets and 'Orders.csv' in self.datasets:
            customers = self.datasets['Customers.csv']
            orders = self.datasets['Orders.csv']

            # Analyze customer orders
            merged = pd.merge(customers, orders, on='customer_id', how='inner')

            if len(merged) > 0 and 'customer_state' in merged.columns:
                state_distribution = merged['customer_state'].value_counts().head(5)
                cross_analysis['merged_insights'].append({
                    'analysis': 'geographic_distribution',
                    'top_states': state_distribution.to_dict()
                })

        print(f"    • {len(cross_analysis['relationships'])} cross-dataset relationships found")
        print(f"    • {len(cross_analysis['merged_insights'])} merged insights generated")

        return cross_analysis

    def run_analysis(self):
        """Run complete exploratory analysis"""
        print("\n" + "="*70)
        print("🔍 STAGE 2: EXPLORATORY DATA ANALYSIS")
        print("="*70)

        self.load_datasets()

        for dataset_name, df in self.datasets.items():
            print(f"\n{'='*70}")
            print(f"📊 Analyzing: {dataset_name}")
            print(f"{'='*70}")

            # Run all analyses
            stats_summary = self.statistical_summary(df, dataset_name)
            patterns = self.discover_patterns(df, dataset_name)
            correlations = self.analyze_correlations(df, dataset_name)
            anomalies = self.detect_anomalies(df, dataset_name)

            # Store results
            self.analysis_results[dataset_name] = {
                'statistical_summary': stats_summary,
                'patterns': patterns,
                'correlations': correlations,
                'anomalies': anomalies
            }

        # Cross-dataset analysis
        cross_analysis = self.cross_dataset_analysis()
        self.analysis_results['_cross_dataset_analysis'] = cross_analysis

        return self.analysis_results

    def save_results(self, output_dir='complete_analysis/exploratory_analysis/'):
        """Save analysis results"""
        os.makedirs(output_dir, exist_ok=True)

        # Save JSON results
        json_path = os.path.join(output_dir, 'exploratory_analysis_results.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Analysis results saved to: {json_path}")

        # Generate statistical summary CSV
        summary_data = []
        for dataset, results in self.analysis_results.items():
            if dataset != '_cross_dataset_analysis':
                summary_data.append({
                    'dataset': dataset,
                    'rows': results['statistical_summary']['basic_info']['rows'],
                    'columns': results['statistical_summary']['basic_info']['columns'],
                    'numeric_columns': len(results['statistical_summary']['numeric_stats']),
                    'categorical_columns': len(results['statistical_summary']['categorical_stats']),
                    'temporal_columns': len(results['statistical_summary']['temporal_stats']),
                    'trends_found': len(results['patterns']['trends']),
                    'strong_correlations': len(results['correlations']['strong_correlations']),
                    'outlier_columns': len(results['anomalies']['statistical_outliers'])
                })

        summary_df = pd.DataFrame(summary_data)
        summary_csv = os.path.join(output_dir, 'statistical_summary.csv')
        summary_df.to_csv(summary_csv, index=False, encoding='utf-8')
        print(f"💾 Statistical summary saved to: {summary_csv}")

        # Generate markdown report
        self._generate_markdown_report(output_dir)

    def _generate_markdown_report(self, output_dir):
        """Generate markdown analysis report"""
        report = "# Exploratory Data Analysis Report\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        report += "## Overview\n\n"
        report += f"This report presents comprehensive exploratory analysis of {len(self.datasets)} e-commerce datasets.\n\n"

        for dataset, results in self.analysis_results.items():
            if dataset == '_cross_dataset_analysis':
                continue

            report += f"## {dataset}\n\n"

            # Basic Info
            basic = results['statistical_summary']['basic_info']
            report += f"**Dimensions**: {basic['rows']:,} rows × {basic['columns']} columns  \n"
            report += f"**Memory Usage**: {basic['memory_usage_mb']} MB\n\n"

            # Key Patterns
            if results['patterns']['trends']:
                report += "### 📈 Key Trends\n\n"
                for trend in results['patterns']['trends'][:3]:
                    if trend['type'] == 'yearly_trend':
                        direction = "↑" if trend['growth_rate'] > 0 else "↓"
                        report += f"- {direction} {trend['column']}: {trend['growth_rate']:.1f}% growth\n"

            # Strong Correlations
            if results['correlations']['strong_correlations']:
                report += "\n### 🔗 Strong Correlations\n\n"
                for corr in results['correlations']['strong_correlations'][:5]:
                    direction = "positive" if corr['correlation'] > 0 else "negative"
                    report += f"- **{corr['variable_1']}** ↔ **{corr['variable_2']}**: "
                    report += f"{corr['correlation']:.3f} ({direction})\n"

            # Key Anomalies
            if results['anomalies']['statistical_outliers']:
                report += "\n### ⚠️ Notable Outliers\n\n"
                for outlier in results['anomalies']['statistical_outliers'][:3]:
                    report += f"- **{outlier['column']}**: {outlier['outlier_percentage']:.1f}% outliers "
                    report += f"(range: {outlier['lower_bound']:.2f} - {outlier['upper_bound']:.2f})\n"

            report += "\n---\n\n"

        # Cross-dataset insights
        if '_cross_dataset_analysis' in self.analysis_results:
            cross = self.analysis_results['_cross_dataset_analysis']
            report += "## Cross-Dataset Insights\n\n"
            for rel in cross['relationships']:
                report += f"### {rel['datasets'][0]} + {rel['datasets'][1]}\n\n"
                for key, value in rel['insights'].items():
                    if isinstance(value, (int, float)):
                        report += f"- **{key}**: {value:,.2f}\n"

        # Save report
        report_path = os.path.join(output_dir, 'pattern_analysis.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"💾 Markdown report saved to: {report_path}")

    def print_summary(self):
        """Print analysis summary"""
        print("\n" + "="*70)
        print("📋 EXPLORATORY ANALYSIS SUMMARY")
        print("="*70)

        total_trends = sum(len(r['patterns']['trends'])
                          for r in self.analysis_results.values()
                          if isinstance(r, dict) and 'patterns' in r)

        total_correlations = sum(len(r['correlations']['strong_correlations'])
                                for r in self.analysis_results.values()
                                if isinstance(r, dict) and 'correlations' in r)

        total_anomalies = sum(len(r['anomalies']['statistical_outliers'])
                             for r in self.analysis_results.values()
                             if isinstance(r, dict) and 'anomalies' in r)

        print(f"\n📊 Key Findings:")
        print(f"  • Total trends identified: {total_trends}")
        print(f"  • Total strong correlations: {total_correlations}")
        print(f"  • Total outlier patterns: {total_anomalies}")

        # Show top correlations across all datasets
        print(f"\n🔗 Top Strong Correlations Across All Datasets:")
        all_correlations = []
        for dataset, results in self.analysis_results.items():
            if isinstance(results, dict) and 'correlations' in results:
                for corr in results['correlations']['strong_correlations']:
                    corr['dataset'] = dataset
                    all_correlations.append(corr)

        # Sort by absolute correlation value
        all_correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)

        for i, corr in enumerate(all_correlations[:5], 1):
            direction = "↑" if corr['correlation'] > 0 else "↓"
            print(f"  {i}. [{corr['dataset']}] {corr['variable_1']} ↔ {corr['variable_2']}: "
                  f"{corr['correlation']:.3f} {direction}")

        print("\n" + "="*70)

if __name__ == "__main__":
    # Run exploratory analysis
    eda = ExploratoryDataAnalysis()
    results = eda.run_analysis()
    eda.save_results()
    eda.print_summary()

    print("\n✅ STAGE 2 COMPLETE: Exploratory Data Analysis")
    print("  All statistical summaries, patterns, and correlations analyzed")
    print("  Proceeding to Stage 3: Hypothesis Generation...")
