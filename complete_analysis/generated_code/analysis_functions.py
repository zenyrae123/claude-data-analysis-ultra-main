"""
Core Analysis Functions for E-commerce Data
Statistical analysis, pattern discovery, and metrics calculation
"""

import pandas as pd
import numpy as np
from scipy import stats

class EcommerceAnalyzer:
    """Core analysis functions for e-commerce data"""

    def __init__(self, data):
        self.data = data

    def calculate_order_metrics(self, orders_df):
        """Calculate key order metrics"""
        metrics = {}

        if 'order_id' in orders_df.columns:
            metrics['total_orders'] = len(orders_df)

        if 'order_purchase_timestamp' in orders_df.columns:
            orders_df['order_date'] = pd.to_datetime(orders_df['order_purchase_timestamp']).dt.date
            metrics['unique_days'] = orders_df['order_date'].nunique()
            metrics['avg_orders_per_day'] = metrics['total_orders'] / metrics['unique_days']

        if 'customer_id' in orders_df.columns:
            metrics['unique_customers'] = orders_df['customer_id'].nunique()

        return metrics

    def analyze_customer_behavior(self, orders_df, customers_df):
        """Analyze customer behavior patterns"""
        # Merge orders with customers
        merged = pd.merge(orders_df, customers_df, on='customer_id', how='left')

        analysis = {}

        # Orders per customer
        orders_per_customer = merged.groupby('customer_id').size()
        analysis['avg_orders_per_customer'] = orders_per_customer.mean()
        analysis['repeat_customer_rate'] = (orders_per_customer > 1).sum() / len(orders_per_customer)

        # Geographic distribution
        if 'customer_state' in merged.columns:
            analysis['top_states'] = merged['customer_state'].value_counts().head(5).to_dict()

        return analysis

    def analyze_product_performance(self, order_items_df, products_df=None):
        """Analyze product performance metrics"""
        analysis = {}

        if 'product_id' in order_items_df.columns:
            # Sales per product
            product_sales = order_items_df.groupby('product_id').agg({
                'order_id': 'count',
                'price': 'sum'
            }).rename(columns={'order_id': 'order_count', 'price': 'total_revenue'})

            analysis['top_products'] = product_sales.nlargest(10, 'order_count').to_dict()

        if 'price' in order_items_df.columns:
            analysis['avg_product_price'] = order_items_df['price'].mean()
            analysis['median_product_price'] = order_items_df['price'].median()

        return analysis

    def calculate_satisfaction_metrics(self, reviews_df):
        """Calculate customer satisfaction metrics"""
        metrics = {}

        if 'review_score' in reviews_df.columns:
            metrics['avg_review_score'] = reviews_df['review_score'].mean()
            metrics['median_review_score'] = reviews_df['review_score'].median()

            # Score distribution
            score_dist = reviews_df['review_score'].value_counts(normalize=True)
            metrics['positive_review_rate'] = score_dist.get(5, 0) + score_dist.get(4, 0)

        return metrics

    def temporal_analysis(self, orders_df):
        """Analyze temporal patterns in orders"""
        if 'order_purchase_timestamp' not in orders_df.columns:
            return {}

        orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])

        analysis = {}

        # By hour
        orders_df['hour'] = orders_df['order_purchase_timestamp'].dt.hour
        analysis['hourly_distribution'] = orders_df.groupby('hour').size().to_dict()

        # By day of week
        orders_df['day_of_week'] = orders_df['order_purchase_timestamp'].dt.dayofweek
        analysis['daily_distribution'] = orders_df.groupby('day_of_week').size().to_dict()

        # By month
        orders_df['month'] = orders_df['order_purchase_timestamp'].dt.to_period('M')
        analysis['monthly_trend'] = orders_df.groupby('month').size().to_dict()

        return analysis

    def payment_analysis(self, payments_df):
        """Analyze payment patterns"""
        analysis = {}

        if 'payment_type' in payments_df.columns:
            analysis['payment_type_distribution'] = payments_df['payment_type'].value_counts(normalize=True).to_dict()

        if 'payment_installments' in payments_df.columns:
            analysis['avg_installments'] = payments_df['payment_installments'].mean()
            analysis['installment_rate'] = (payments_df['payment_installments'] > 1).mean()

        if 'payment_value' in payments_df.columns:
            analysis['avg_payment_value'] = payments_df['payment_value'].mean()
            analysis['total_payment_value'] = payments_df['payment_value'].sum()

        return analysis

    def correlation_analysis(self, df, cols):
        """Perform correlation analysis on specified columns"""
        available_cols = [col for col in cols if col in df.columns]

        if len(available_cols) < 2:
            return {}

        corr_matrix = df[available_cols].corr()

        # Find strong correlations
        strong_corrs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.5:
                    strong_corrs.append({
                        'var1': corr_matrix.columns[i],
                        'var2': corr_matrix.columns[j],
                        'correlation': corr_val
                    })

        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'strong_correlations': strong_corrs
        }

# Usage example
if __name__ == "__main__":
    analyzer = EcommerceAnalyzer(data=None)
    # metrics = analyzer.calculate_order_metrics(orders_df)
    # print(metrics)
