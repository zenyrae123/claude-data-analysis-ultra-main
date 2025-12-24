"""
Comprehensive Data Visualization for E-commerce Analysis
Creates interactive dashboards, charts, and visual storyboards
"""

import pandas as pd
import numpy as np
import os
import json
import warnings
import sys
import base64
from datetime import datetime
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class DataVisualization:
    """Comprehensive data visualization framework"""

    def __init__(self, data_dir='data_storage/', output_dir='complete_analysis/visualizations/'):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.datasets = {}
        self.visualizations = {}

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Configure matplotlib for Chinese support
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

    def load_datasets(self):
        """Load all datasets"""
        print("📂 Loading datasets for visualization...")
        files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]

        for file in files:
            try:
                df = pd.read_csv(os.path.join(self.data_dir, file))
                self.datasets[file] = df
                print(f"  ✓ {file}")
            except Exception as e:
                print(f"  ✗ {file}: {str(e)}")

        return self.datasets

    def create_overview_dashboard(self):
        """Create overview dashboard with key metrics"""
        print("\n📊 Creating overview dashboard...")

        dashboard_data = {
            'title': 'E-commerce Overview Dashboard',
            'metrics': {},
            'charts': []
        }

        # Key metrics
        if 'Orders.csv' in self.datasets:
            orders = self.datasets['Orders.csv']
            dashboard_data['metrics']['total_orders'] = int(len(orders))

        if 'Customers.csv' in self.datasets:
            customers = self.datasets['Customers.csv']
            dashboard_data['metrics']['total_customers'] = int(len(customers))

        if 'Products.csv' in self.datasets:
            products = self.datasets['Products.csv']
            dashboard_data['metrics']['total_products'] = int(len(products))

        if 'Sellers.csv' in self.datasets:
            sellers = self.datasets['Sellers.csv']
            dashboard_data['metrics']['total_sellers'] = int(len(sellers))

        if 'Order Items.csv' in self.datasets and 'Orders.csv' in self.datasets:
            order_items = self.datasets['Order Items.csv']
            orders = self.datasets['Orders.csv']
            merged = pd.merge(orders, order_items, on='order_id', how='inner')

            if 'price' in merged.columns:
                total_revenue = merged['price'].sum()
                dashboard_data['metrics']['total_revenue'] = round(float(total_revenue), 2)

                avg_order_value = merged.groupby('order_id')['price'].sum().mean()
                dashboard_data['metrics']['avg_order_value'] = round(float(avg_order_value), 2)

        print(f"  • {len(dashboard_data['metrics'])} key metrics calculated")

        return dashboard_data

    def create_trend_analysis_charts(self):
        """Create trend analysis visualizations"""
        print("\n📈 Creating trend analysis charts...")

        charts = []

        # Order timeline chart
        if 'Orders.csv' in self.datasets:
            orders = self.datasets['Orders.csv'].copy()

            if 'order_purchase_timestamp' in orders.columns:
                orders['order_purchase_timestamp'] = pd.to_datetime(
                    orders['order_purchase_timestamp'], errors='coerce'
                )
                orders['order_date'] = orders['order_purchase_timestamp'].dt.date
                orders['order_month'] = orders['order_purchase_timestamp'].dt.to_period('M')

                # Daily orders trend
                daily_orders = orders.groupby('order_date').size()

                fig, ax = plt.subplots(figsize=(14, 6))
                daily_orders.plot(ax=ax, linewidth=1.5, color='#2E86AB')
                ax.set_title('Daily Order Trend', fontsize=16, fontweight='bold')
                ax.set_xlabel('Date', fontsize=12)
                ax.set_ylabel('Number of Orders', fontsize=12)
                ax.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                plt.tight_layout()

                chart_path = os.path.join(self.output_dir, 'daily_orders_trend.png')
                plt.savefig(chart_path, dpi=150, bbox_inches='tight')
                plt.close()

                charts.append({
                    'name': 'Daily Orders Trend',
                    'file': 'daily_orders_trend.png',
                    'description': 'Time series showing daily order volume over time'
                })

                # Monthly orders chart
                monthly_orders = orders.groupby('order_month').size()

                fig, ax = plt.subplots(figsize=(12, 6))
                monthly_orders.plot(kind='bar', ax=ax, color='#A23B72')
                ax.set_title('Monthly Orders Distribution', fontsize=16, fontweight='bold')
                ax.set_xlabel('Month', fontsize=12)
                ax.set_ylabel('Number of Orders', fontsize=12)
                ax.grid(True, alpha=0.3, axis='y')
                plt.xticks(rotation=45)
                plt.tight_layout()

                chart_path = os.path.join(self.output_dir, 'monthly_orders_distribution.png')
                plt.savefig(chart_path, dpi=150, bbox_inches='tight')
                plt.close()

                charts.append({
                    'name': 'Monthly Orders Distribution',
                    'file': 'monthly_orders_distribution.png',
                    'description': 'Bar chart showing order distribution by month'
                })

                # Day of week heatmap
                orders['day_of_week'] = orders['order_purchase_timestamp'].dt.dayofweek
                orders['hour'] = orders['order_purchase_timestamp'].dt.hour

                heatmap_data = orders.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)

                fig, ax = plt.subplots(figsize=(14, 8))
                sns.heatmap(heatmap_data, cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Order Count'})
                ax.set_title('Order Activity Heatmap (Day of Week vs Hour)',
                           fontsize=16, fontweight='bold')
                ax.set_xlabel('Hour of Day', fontsize=12)
                ax.set_ylabel('Day of Week (0=Mon, 6=Sun)', fontsize=12)
                plt.tight_layout()

                chart_path = os.path.join(self.output_dir, 'order_activity_heatmap.png')
                plt.savefig(chart_path, dpi=150, bbox_inches='tight')
                plt.close()

                charts.append({
                    'name': 'Order Activity Heatmap',
                    'file': 'order_activity_heatmap.png',
                    'description': 'Heatmap showing order patterns by day and hour'
                })

        print(f"  • {len(charts)} trend charts created")

        return charts

    def create_distribution_plots(self):
        """Create distribution analysis plots"""
        print("\n📊 Creating distribution plots...")

        plots = []

        # Price distribution
        if 'Order Items.csv' in self.datasets:
            order_items = self.datasets['Order Items.csv']

            if 'price' in order_items.columns:
                fig, axes = plt.subplots(1, 2, figsize=(16, 6))

                # Histogram
                axes[0].hist(order_items['price'].dropna(), bins=50,
                           color='#2E86AB', edgecolor='black', alpha=0.7)
                axes[0].set_title('Product Price Distribution', fontsize=14, fontweight='bold')
                axes[0].set_xlabel('Price (BRL)', fontsize=12)
                axes[0].set_ylabel('Frequency', fontsize=12)
                axes[0].grid(True, alpha=0.3, axis='y')
                axes[0].axvline(order_items['price'].median(), color='red',
                               linestyle='--', linewidth=2, label=f'Median: {order_items["price"].median():.2f}')
                axes[0].legend()

                # Box plot
                axes[1].boxplot(order_items['price'].dropna(), vert=True)
                axes[1].set_title('Price Distribution Box Plot', fontsize=14, fontweight='bold')
                axes[1].set_ylabel('Price (BRL)', fontsize=12)
                axes[1].grid(True, alpha=0.3, axis='y')

                plt.tight_layout()

                plot_path = os.path.join(self.output_dir, 'price_distribution.png')
                plt.savefig(plot_path, dpi=150, bbox_inches='tight')
                plt.close()

                plots.append({
                    'name': 'Product Price Distribution',
                    'file': 'price_distribution.png',
                    'description': 'Price distribution analysis with histogram and box plot'
                })

                # Freight value distribution
                if 'freight_value' in order_items.columns:
                    fig, ax = plt.subplots(figsize=(12, 6))

                    ax.scatter(order_items['price'], order_items['freight_value'],
                              alpha=0.3, s=10, color='#A23B72')
                    ax.set_title('Price vs Freight Value Scatter Plot',
                               fontsize=16, fontweight='bold')
                    ax.set_xlabel('Price (BRL)', fontsize=12)
                    ax.set_ylabel('Freight Value (BRL)', fontsize=12)
                    ax.grid(True, alpha=0.3)

                    # Add trend line
                    valid_data = order_items[['price', 'freight_value']].dropna()
                    if len(valid_data) > 0:
                        z = np.polyfit(valid_data['price'], valid_data['freight_value'], 1)
                        p = np.poly1d(z)
                        ax.plot(valid_data['price'], p(valid_data['price']),
                               "r--", linewidth=2, label='Trend Line')
                        ax.legend()

                    plt.tight_layout()

                    plot_path = os.path.join(self.output_dir, 'price_vs_freight.png')
                    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
                    plt.close()

                    plots.append({
                        'name': 'Price vs Freight Value',
                        'file': 'price_vs_freight.png',
                        'description': 'Scatter plot showing relationship between price and shipping cost'
                    })

        # Review score distribution
        if 'Reviews.csv' in self.datasets:
            reviews = self.datasets['Reviews.csv']

            if 'review_score' in reviews.columns:
                score_counts = reviews['review_score'].value_counts().sort_index()

                fig, ax = plt.subplots(figsize=(10, 6))
                colors = ['#F18F01', '#C73E1D', '#F18F01', '#6A994E', '#6A994E']
                score_counts.plot(kind='bar', color=colors, ax=ax, edgecolor='black')
                ax.set_title('Customer Review Score Distribution',
                           fontsize=16, fontweight='bold')
                ax.set_xlabel('Review Score', fontsize=12)
                ax.set_ylabel('Count', fontsize=12)
                ax.grid(True, alpha=0.3, axis='y')

                # Add percentage labels
                total = len(reviews)
                for i, (idx, val) in enumerate(score_counts.items()):
                    pct = val / total * 100
                    ax.text(i, val + 100, f'{pct:.1f}%', ha='center', fontsize=10)

                plt.tight_layout()

                plot_path = os.path.join(self.output_dir, 'review_score_distribution.png')
                plt.savefig(plot_path, dpi=150, bbox_inches='tight')
                plt.close()

                plots.append({
                    'name': 'Review Score Distribution',
                    'file': 'review_score_distribution.png',
                    'description': 'Distribution of customer review scores (1-5 stars)'
                })

        print(f"  • {len(plots)} distribution plots created")

        return plots

    def create_geographical_analysis(self):
        """Create geographical visualizations"""
        print("\n🗺️  Creating geographical analysis...")

        geo_charts = []

        # Customer state distribution
        if 'Customers.csv' in self.datasets:
            customers = self.datasets['Customers.csv']

            if 'customer_state' in customers.columns:
                state_counts = customers['customer_state'].value_counts().head(15)

                fig, ax = plt.subplots(figsize=(12, 8))
                state_counts.plot(kind='barh', color='#2E86AB', ax=ax)
                ax.set_title('Top 15 Customer States by Order Count',
                           fontsize=16, fontweight='bold')
                ax.set_xlabel('Number of Customers', fontsize=12)
                ax.set_ylabel('State', fontsize=12)
                ax.grid(True, alpha=0.3, axis='x')

                # Add value labels
                for i, (idx, val) in enumerate(state_counts.items()):
                    ax.text(val, i, f' {val:,}', va='center', fontsize=9)

                plt.tight_layout()

                chart_path = os.path.join(self.output_dir, 'customer_state_distribution.png')
                plt.savefig(chart_path, dpi=150, bbox_inches='tight')
                plt.close()

                geo_charts.append({
                    'name': 'Customer State Distribution',
                    'file': 'customer_state_distribution.png',
                    'description': 'Horizontal bar chart showing top 15 customer states'
                })

        # Seller state distribution
        if 'Sellers.csv' in self.datasets:
            sellers = self.datasets['Sellers.csv']

            if 'seller_state' in sellers.columns:
                state_counts = sellers['seller_state'].value_counts().head(15)

                fig, ax = plt.subplots(figsize=(12, 8))
                state_counts.plot(kind='barh', color='#A23B72', ax=ax)
                ax.set_title('Top 15 Seller States',
                           fontsize=16, fontweight='bold')
                ax.set_xlabel('Number of Sellers', fontsize=12)
                ax.set_ylabel('State', fontsize=12)
                ax.grid(True, alpha=0.3, axis='x')

                for i, (idx, val) in enumerate(state_counts.items()):
                    ax.text(val, i, f' {val:,}', va='center', fontsize=9)

                plt.tight_layout()

                chart_path = os.path.join(self.output_dir, 'seller_state_distribution.png')
                plt.savefig(chart_path, dpi=150, bbox_inches='tight')
                plt.close()

                geo_charts.append({
                    'name': 'Seller State Distribution',
                    'file': 'seller_state_distribution.png',
                    'description': 'Horizontal bar chart showing top 15 seller states'
                })

        print(f"  • {len(geo_charts)} geographical charts created")

        return geo_charts

    def create_payment_analysis_charts(self):
        """Create payment analysis visualizations"""
        print("\n💳 Creating payment analysis charts...")

        payment_charts = []

        if 'Order Payments.csv' in self.datasets:
            payments = self.datasets['Order Payments.csv']

            # Payment type distribution
            if 'payment_type' in payments.columns:
                payment_counts = payments['payment_type'].value_counts()

                fig, ax = plt.subplots(figsize=(10, 8))
                colors = ['#2E86AB', '#A23B72', '#F18F01', '#6A994E']
                wedges, texts, autotexts = ax.pie(payment_counts, labels=payment_counts.index,
                                                  autopct='%1.1f%%', colors=colors[:len(payment_counts)],
                                                  startangle=90)
                ax.set_title('Payment Type Distribution', fontsize=16, fontweight='bold')

                # Enhance text
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(12)

                plt.tight_layout()

                chart_path = os.path.join(self.output_dir, 'payment_type_distribution.png')
                plt.savefig(chart_path, dpi=150, bbox_inches='tight')
                plt.close()

                payment_charts.append({
                    'name': 'Payment Type Distribution',
                    'file': 'payment_type_distribution.png',
                    'description': 'Pie chart showing distribution of payment methods'
                })

            # Payment installments distribution
            if 'payment_installments' in payments.columns:
                install_counts = payments['payment_installments'].value_counts().sort_index()

                fig, ax = plt.subplots(figsize=(14, 6))
                install_counts.plot(kind='bar', color='#2E86AB', ax=ax)
                ax.set_title('Payment Installments Distribution',
                           fontsize=16, fontweight='bold')
                ax.set_xlabel('Number of Installments', fontsize=12)
                ax.set_ylabel('Count', fontsize=12)
                ax.grid(True, alpha=0.3, axis='y')
                plt.xticks(rotation=0)

                plt.tight_layout()

                chart_path = os.path.join(self.output_dir, 'payment_installments_distribution.png')
                plt.savefig(chart_path, dpi=150, bbox_inches='tight')
                plt.close()

                payment_charts.append({
                    'name': 'Payment Installments Distribution',
                    'file': 'payment_installments_distribution.png',
                    'description': 'Bar chart showing distribution of installment counts'
                })

            # Payment value distribution
            if 'payment_value' in payments.columns:
                fig, axes = plt.subplots(1, 2, figsize=(16, 6))

                # Histogram
                axes[0].hist(payments['payment_value'].dropna(), bins=50,
                           color='#A23B72', edgecolor='black', alpha=0.7)
                axes[0].set_title('Payment Value Distribution', fontsize=14, fontweight='bold')
                axes[0].set_xlabel('Payment Value (BRL)', fontsize=12)
                axes[0].set_ylabel('Frequency', fontsize=12)
                axes[0].grid(True, alpha=0.3, axis='y')

                # Box plot
                axes[1].boxplot(payments['payment_value'].dropna(), vert=True)
                axes[1].set_title('Payment Value Box Plot', fontsize=14, fontweight='bold')
                axes[1].set_ylabel('Payment Value (BRL)', fontsize=12)
                axes[1].grid(True, alpha=0.3, axis='y')

                plt.tight_layout()

                chart_path = os.path.join(self.output_dir, 'payment_value_distribution.png')
                plt.savefig(chart_path, dpi=150, bbox_inches='tight')
                plt.close()

                payment_charts.append({
                    'name': 'Payment Value Distribution',
                    'file': 'payment_value_distribution.png',
                    'description': 'Payment value distribution with histogram and box plot'
                })

        print(f"  • {len(payment_charts)} payment charts created")

        return payment_charts

    def create_product_analysis_charts(self):
        """Create product analysis visualizations"""
        print("\n📦 Creating product analysis charts...")

        product_charts = []

        if 'Products.csv' in self.datasets:
            products = self.datasets['Products.csv']

            # Product category analysis
            if 'product_category_name' in products.columns:
                category_counts = products['product_category_name'].value_counts().head(15)

                fig, ax = plt.subplots(figsize=(12, 8))
                category_counts.plot(kind='barh', color='#6A994E', ax=ax)
                ax.set_title('Top 15 Product Categories',
                           fontsize=16, fontweight='bold')
                ax.set_xlabel('Number of Products', fontsize=12)
                ax.set_ylabel('Category', fontsize=12)
                ax.grid(True, alpha=0.3, axis='x')

                plt.tight_layout()

                chart_path = os.path.join(self.output_dir, 'product_category_distribution.png')
                plt.savefig(chart_path, dpi=150, bbox_inches='tight')
                plt.close()

                product_charts.append({
                    'name': 'Product Category Distribution',
                    'file': 'product_category_distribution.png',
                    'description': 'Horizontal bar chart showing top 15 product categories'
                })

            # Product weight vs dimensions
            if 'product_weight_g' in products.columns:
                fig, ax = plt.subplots(figsize=(10, 6))

                weights = products['product_weight_g'].dropna()
                ax.hist(weights, bins=50, color='#F18F01', edgecolor='black', alpha=0.7)
                ax.set_title('Product Weight Distribution',
                           fontsize=16, fontweight='bold')
                ax.set_xlabel('Weight (grams)', fontsize=12)
                ax.set_ylabel('Frequency', fontsize=12)
                ax.grid(True, alpha=0.3, axis='y')

                # Add median line
                median_weight = weights.median()
                ax.axvline(median_weight, color='red', linestyle='--',
                          linewidth=2, label=f'Median: {median_weight:.0f}g')
                ax.legend()

                plt.tight_layout()

                chart_path = os.path.join(self.output_dir, 'product_weight_distribution.png')
                plt.savefig(chart_path, dpi=150, bbox_inches='tight')
                plt.close()

                product_charts.append({
                    'name': 'Product Weight Distribution',
                    'file': 'product_weight_distribution.png',
                    'description': 'Histogram showing product weight distribution'
                })

        print(f"  • {len(product_charts)} product charts created")

        return product_charts

    def create_interactive_dashboard_html(self):
        """Create interactive HTML dashboard"""
        print("\n🌐 Creating interactive HTML dashboard...")

        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-commerce Analysis Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }

        .metric-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }

        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }

        .metric-card h3 {
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }

        .metric-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }

        .content {
            padding: 30px;
        }

        .section {
            margin-bottom: 40px;
        }

        .section h2 {
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }

        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
        }

        .chart-card {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .chart-card img {
            width: 100%;
            height: auto;
            display: block;
        }

        .chart-info {
            padding: 20px;
        }

        .chart-info h3 {
            color: #333;
            margin-bottom: 10px;
        }

        .chart-info p {
            color: #666;
            line-height: 1.6;
        }

        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
        }

        @media (max-width: 768px) {
            .chart-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛒 E-commerce Analysis Dashboard</h1>
            <p>Complete Data Analysis Report | Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        </div>

        <div class="metrics">
"""

        # Add metrics cards
        if 'Orders.csv' in self.datasets:
            html_content += f"""
            <div class="metric-card">
                <h3>Total Orders</h3>
                <div class="value">{len(self.datasets['Orders.csv']):,}</div>
            </div>
"""

        if 'Customers.csv' in self.datasets:
            html_content += f"""
            <div class="metric-card">
                <h3>Total Customers</h3>
                <div class="value">{len(self.datasets['Customers.csv']):,}</div>
            </div>
"""

        if 'Products.csv' in self.datasets:
            html_content += f"""
            <div class="metric-card">
                <h3>Total Products</h3>
                <div class="value">{len(self.datasets['Products.csv']):,}</div>
            </div>
"""

        if 'Sellers.csv' in self.datasets:
            html_content += f"""
            <div class="metric-card">
                <h3>Total Sellers</h3>
                <div class="value">{len(self.datasets['Sellers.csv']):,}</div>
            </div>
"""

        html_content += """
        </div>

        <div class="content">
            <div class="section">
                <h2>📈 Trend Analysis</h2>
                <div class="chart-grid">
"""

        # Add trend charts
        trend_charts = ['daily_orders_trend.png', 'monthly_orders_distribution.png', 'order_activity_heatmap.png']
        for chart in trend_charts:
            chart_path = os.path.join(self.output_dir, chart)
            if os.path.exists(chart_path):
                with open(chart_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()
                html_content += f"""
                    <div class="chart-card">
                        <img src="data:image/png;base64,{img_data}" alt="{chart}">
                    </div>
"""

        html_content += """
                </div>
            </div>

            <div class="section">
                <h2>📊 Distribution Analysis</h2>
                <div class="chart-grid">
"""

        # Add distribution charts
        dist_charts = ['price_distribution.png', 'price_vs_freight.png', 'review_score_distribution.png']
        for chart in dist_charts:
            chart_path = os.path.join(self.output_dir, chart)
            if os.path.exists(chart_path):
                with open(chart_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()
                html_content += f"""
                    <div class="chart-card">
                        <img src="data:image/png;base64,{img_data}" alt="{chart}">
                    </div>
"""

        html_content += """
                </div>
            </div>

            <div class="section">
                <h2>🗺️ Geographic Analysis</h2>
                <div class="chart-grid">
"""

        # Add geo charts
        geo_charts = ['customer_state_distribution.png', 'seller_state_distribution.png']
        for chart in geo_charts:
            chart_path = os.path.join(self.output_dir, chart)
            if os.path.exists(chart_path):
                with open(chart_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()
                html_content += f"""
                    <div class="chart-card">
                        <img src="data:image/png;base64,{img_data}" alt="{chart}">
                    </div>
"""

        html_content += """
                </div>
            </div>

            <div class="section">
                <h2>💳 Payment Analysis</h2>
                <div class="chart-grid">
"""

        # Add payment charts
        payment_charts = ['payment_type_distribution.png', 'payment_installments_distribution.png', 'payment_value_distribution.png']
        for chart in payment_charts:
            chart_path = os.path.join(self.output_dir, chart)
            if os.path.exists(chart_path):
                with open(chart_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()
                html_content += f"""
                    <div class="chart-card">
                        <img src="data:image/png;base64,{img_data}" alt="{chart}">
                    </div>
"""

        html_content += """
                </div>
            </div>

            <div class="section">
                <h2>📦 Product Analysis</h2>
                <div class="chart-grid">
"""

        # Add product charts
        product_charts = ['product_category_distribution.png', 'product_weight_distribution.png']
        for chart in product_charts:
            chart_path = os.path.join(self.output_dir, chart)
            if os.path.exists(chart_path):
                with open(chart_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()
                html_content += f"""
                    <div class="chart-card">
                        <img src="data:image/png;base64,{img_data}" alt="{chart}">
                    </div>
"""

        html_content += """
                </div>
            </div>
        </div>

        <div class="footer">
            <p>Generated by Claude Data Analysis Assistant | Complete Analysis Report</p>
        </div>
    </div>
</body>
</html>
"""

        # Save HTML dashboard
        dashboard_path = os.path.join(self.output_dir, 'interactive_dashboard.html')
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"  ✓ Interactive dashboard saved to: {dashboard_path}")

        return dashboard_path

    def run_visualization_creation(self):
        """Run complete visualization workflow"""
        print("\n" + "="*70)
        print("🎨 STAGE 4: DATA VISUALIZATION")
        print("="*70)

        self.load_datasets()

        # Create all visualizations
        dashboard = self.create_overview_dashboard()
        trend_charts = self.create_trend_analysis_charts()
        distribution_plots = self.create_distribution_plots()
        geo_charts = self.create_geographical_analysis()
        payment_charts = self.create_payment_analysis_charts()
        product_charts = self.create_product_analysis_charts()

        # Create interactive dashboard
        dashboard_path = self.create_interactive_dashboard_html()

        # Store all results
        self.visualizations = {
            'dashboard': dashboard,
            'trend_charts': trend_charts,
            'distribution_plots': distribution_plots,
            'geographical_charts': geo_charts,
            'payment_charts': payment_charts,
            'product_charts': product_charts,
            'interactive_dashboard': dashboard_path
        }

        return self.visualizations

    def save_visualization_index(self):
        """Save index of all visualizations"""
        index_path = os.path.join(self.output_dir, 'visualization_index.json')

        # Prepare index for JSON serialization
        index = {
            'total_visualizations': sum(len(v) if isinstance(v, list) else 0
                                       for v in self.visualizations.values()
                                       if isinstance(v, list)),
            'charts': []
        }

        for chart_type, charts in self.visualizations.items():
            if isinstance(charts, list):
                for chart in charts:
                    chart['category'] = chart_type
                    index['charts'].append(chart)

        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Visualization index saved to: {index_path}")

    def print_summary(self):
        """Print visualization summary"""
        print("\n" + "="*70)
        print("📋 VISUALIZATION SUMMARY")
        print("="*70)

        total_charts = sum(len(v) if isinstance(v, list) else 0
                          for v in self.visualizations.values()
                          if isinstance(v, list))

        print(f"\n📊 Total Visualizations Created: {total_charts}\n")

        print("By Category:")
        for key, value in self.visualizations.items():
            if isinstance(value, list) and len(value) > 0:
                print(f"  • {key}: {len(value)} charts")

        print(f"\n🌐 Interactive Dashboard:")
        if 'interactive_dashboard' in self.visualizations:
            print(f"  ✓ {self.visualizations['interactive_dashboard']}")

        print("\n" + "="*70)

if __name__ == "__main__":
    # Run visualization creation
    viz = DataVisualization()
    visualizations = viz.run_visualization_creation()
    viz.save_visualization_index()
    viz.print_summary()

    print("\n✅ STAGE 4 COMPLETE: Data Visualization")
    print("  All visualizations created successfully")
    print("  Proceeding to Stage 5: Code Generation...")
