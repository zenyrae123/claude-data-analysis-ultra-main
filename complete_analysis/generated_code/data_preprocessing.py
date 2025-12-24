"""
Data Preprocessing Module for E-commerce Analysis
Handles data loading, cleaning, and preparation
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DataPreprocessor:
    """Data preprocessing and cleaning"""

    def __init__(self, data_dir='data_storage/'):
        self.data_dir = data_dir
        self.data = {}

    def load_all_data(self):
        """Load all datasets"""
        print("Loading datasets...")

        datasets = ['Orders.csv', 'Customers.csv', 'Order Items.csv',
                   'Order Payments.csv', 'Products.csv', 'Reviews.csv',
                   'Sellers.csv', 'Categories.csv']

        for dataset in datasets:
            try:
                df = pd.read_csv(f"{self.data_dir}/{dataset}")
                self.data[dataset.replace('.csv', '')] = df
                print(f"  ✓ Loaded {dataset}: {df.shape[0]:,} rows")
            except Exception as e:
                print(f"  ✗ Error loading {dataset}: {e}")

        return self.data

    def clean_orders(self):
        """Clean and preprocess orders data"""
        if 'Orders' not in self.data:
            return None

        df = self.data['Orders'].copy()

        # Convert date columns
        date_cols = ['order_purchase_timestamp', 'order_approved_at',
                    'order_delivered_carrier_date', 'order_delivered_customer_date',
                    'order_estimated_delivery_date']

        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Extract features
        df['order_year'] = df['order_purchase_timestamp'].dt.year
        df['order_month'] = df['order_purchase_timestamp'].dt.month
        df['order_day_of_week'] = df['order_purchase_timestamp'].dt.dayofweek
        df['order_hour'] = df['order_purchase_timestamp'].dt.hour

        # Calculate delivery time
        if 'order_delivered_customer_date' in df.columns:
            df['delivery_days'] = (
                df['order_delivered_customer_date'] - df['order_purchase_timestamp']
            ).dt.days

        # Handle missing values
        df['order_delivered_customer_date'].fillna(df['order_estimated_delivery_date'], inplace=True)

        self.data['Orders_clean'] = df
        return df

    def clean_customers(self):
        """Clean and preprocess customers data"""
        if 'Customers' not in self.data:
            return None

        df = self.data['Customers'].copy()

        # Encode categorical variables
        if 'customer_state' in df.columns:
            df['customer_state_code'] = df['customer_state'].astype('category').cat.codes

        self.data['Customers_clean'] = df
        return df

    def clean_order_items(self):
        """Clean and preprocess order items data"""
        if 'Order Items' not in self.data:
            return None

        df = self.data['Order Items'].copy()

        # Calculate total item value
        if 'price' in df.columns and 'freight_value' in df.columns:
            df['total_item_value'] = df['price'] + df['freight_value']

        self.data['Order_Items_clean'] = df
        return df

    def clean_payments(self):
        """Clean and preprocess payments data"""
        if 'Order Payments' not in self.data:
            return None

        df = self.data['Order Payments'].copy()

        # Flag installment payments
        if 'payment_installments' in df.columns:
            df['is_installment'] = df['payment_installments'] > 1

        self.data['Payments_clean'] = df
        return df

    def clean_reviews(self):
        """Clean and preprocess reviews data"""
        if 'Reviews' not in self.data:
            return None

        df = self.data['Reviews'].copy()

        # Convert date columns
        if 'review_creation_date' in df.columns:
            df['review_creation_date'] = pd.to_datetime(df['review_creation_date'], errors='coerce')

        if 'review_answer_timestamp' in df.columns:
            df['review_answer_timestamp'] = pd.to_datetime(df['review_answer_timestamp'], errors='coerce')

        # Create sentiment score (simple: 4-5 positive, 3 neutral, 1-2 negative)
        if 'review_score' in df.columns:
            df['sentiment'] = df['review_score'].apply(
                lambda x: 'positive' if x >= 4 else 'neutral' if x == 3 else 'negative'
            )

        # Comment length
        if 'review_comment_message' in df.columns:
            df['comment_length'] = df['review_comment_message'].str.len().fillna(0)

        self.data['Reviews_clean'] = df
        return df

    def merge_datasets(self):
        """Merge related datasets"""
        print("Merging datasets...")

        if 'Orders_clean' in self.data and 'Order_Items_clean' in self.data:
            # Merge orders with items
            orders_items = pd.merge(
                self.data['Orders_clean'],
                self.data['Order_Items_clean'],
                on='order_id',
                how='inner'
            )
            self.data['Orders_Items_merged'] = orders_items
            print(f"  ✓ Orders + Items merged: {len(orders_items):,} rows")

        if 'Orders_clean' in self.data and 'Customers_clean' in self.data:
            # Merge orders with customers
            orders_customers = pd.merge(
                self.data['Orders_clean'],
                self.data['Customers_clean'],
                on='customer_id',
                how='left'
            )
            self.data['Orders_Customers_merged'] = orders_customers
            print(f"  ✓ Orders + Customers merged: {len(orders_customers):,} rows")

        return self.data

    def get_clean_data(self):
        """Get all cleaned and merged data"""
        return self.data

    def export_cleaned_data(self, output_dir='complete_analysis/generated_code/'):
        """Export cleaned datasets"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        for name, df in self.data.items():
            if 'clean' in name.lower() or 'merged' in name.lower():
                path = f"{output_dir}/{name}.csv"
                df.to_csv(path, index=False)
                print(f"  ✓ Exported {name}")

# Usage example
if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    preprocessor.load_all_data()
    preprocessor.clean_orders()
    preprocessor.clean_customers()
    preprocessor.clean_order_items()
    preprocessor.clean_payments()
    preprocessor.clean_reviews()
    preprocessor.merge_datasets()
    preprocessor.export_cleaned_data()
