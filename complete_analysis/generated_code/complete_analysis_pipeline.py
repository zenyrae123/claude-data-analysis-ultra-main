"""
Complete E-commerce Analysis Pipeline
End-to-end analysis from raw data to insights
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

from data_preprocessing import DataPreprocessor
from quality_checks import DataQualityValidator
from analysis_functions import EcommerceAnalyzer

class CompleteAnalysisPipeline:
    """Complete analysis workflow"""

    def __init__(self, data_dir='data_storage/'):
        self.data_dir = data_dir
        self.preprocessor = DataPreprocessor(data_dir)
        self.validator = DataQualityValidator()
        self.analyzer = None
        self.results = {}

    def run(self):
        """Run complete analysis pipeline"""
        print("="*70)
        print("E-COMMERCE ANALYSIS PIPELINE")
        print("="*70)

        # Stage 1: Load and clean data
        print("\n[1/5] Loading and cleaning data...")
        self.preprocessor.load_all_data()
        self.preprocessor.clean_orders()
        self.preprocessor.clean_customers()
        self.preprocessor.clean_order_items()
        self.preprocessor.clean_payments()
        self.preprocessor.clean_reviews()
        self.preprocessor.merge_datasets()

        data = self.preprocessor.get_clean_data()

        # Stage 2: Validate data quality
        print("\n[2/5] Validating data quality...")
        for name, df in data.items():
            if 'Orders' in name or 'Customers' in name:
                self.validator.validate_dataset(df, name)

        # Stage 3: Core analysis
        print("\n[3/5] Running core analysis...")
        self.analyzer = EcommerceAnalyzer(data)

        if 'Orders_clean' in data:
            self.results['order_metrics'] = self.analyzer.calculate_order_metrics(data['Orders_clean'])
            self.results['temporal_patterns'] = self.analyzer.temporal_analysis(data['Orders_clean'])

        if 'Orders_clean' in data and 'Customers_clean' in data:
            self.results['customer_behavior'] = self.analyzer.analyze_customer_behavior(
                data['Orders_clean'], data['Customers_clean']
            )

        if 'Order_Items_clean' in data:
            self.results['product_performance'] = self.analyzer.analyze_product_performance(data['Order_Items_clean'])

        if 'Reviews_clean' in data:
            self.results['satisfaction'] = self.analyzer.calculate_satisfaction_metrics(data['Reviews_clean'])

        if 'Payments_clean' in data:
            self.results['payment_patterns'] = self.analyzer.payment_analysis(data['Payments_clean'])

        # Stage 4: Generate insights
        print("\n[4/5] Generating insights...")
        self.generate_insights()

        # Stage 5: Create report
        print("\n[5/5] Creating report...")
        self.create_summary_report()

        return self.results

    def generate_insights(self):
        """Generate key insights from analysis"""
        self.results['insights'] = []

        # Order trend insight
        if 'order_metrics' in self.results:
            orders = self.results['order_metrics']
            insight = f"Processed {orders.get('total_orders', 0):,} orders from "
            insight += f"{orders.get('unique_customers', 0):,} unique customers"
            self.results['insights'].append(insight)

        # Satisfaction insight
        if 'satisfaction' in self.results:
            sat = self.results['satisfaction']
            avg_score = sat.get('avg_review_score', 0)
            if avg_score > 0:
                insight = f"Average customer satisfaction: {avg_score:.2f}/5.0"
                self.results['insights'].append(insight)

        # Repeat customer insight
        if 'customer_behavior' in self.results:
            repeat_rate = self.results['customer_behavior'].get('repeat_customer_rate', 0)
            insight = f"Repeat customer rate: {repeat_rate*100:.1f}%"
            self.results['insights'].append(insight)

    def create_summary_report(self):
        """Create summary report"""
        report = "\n" + "="*70
        report += "\nANALYSIS SUMMARY"
        report += "\n" + "="*70 + "\n"

        for key, value in self.results.items():
            if key != 'insights':
                report += f"\n{key.upper()}:\n"
                report += str(value) + "\n"

        report += "\nKEY INSIGHTS:\n"
        for i, insight in enumerate(self.results.get('insights', []), 1):
            report += f"{i}. {insight}\n"

        print(report)

        return report

    def export_results(self, output_dir='complete_analysis/generated_code/'):
        """Export analysis results"""
        import json
        import os

        os.makedirs(output_dir, exist_ok=True)

        # Export results as JSON
        results_path = f"{output_dir}/analysis_results.json"

        # Convert non-serializable objects
        serializable_results = {}
        for key, value in self.results.items():
            if isinstance(value, dict):
                serializable_results[key] = {
                    k: str(v) if not isinstance(v, (int, float, str, list, dict)) else v
                    for k, v in value.items()
                }
            else:
                serializable_results[key] = str(value)

        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Results exported to: {results_path}")

# Main execution
if __name__ == "__main__":
    pipeline = CompleteAnalysisPipeline()
    results = pipeline.run()
    pipeline.export_results()

    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE")
    print("="*70)
