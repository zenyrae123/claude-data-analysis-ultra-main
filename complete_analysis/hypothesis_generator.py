"""
Research Hypothesis Generation for E-commerce Analysis
Generates testable hypotheses based on data patterns and correlations
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

class HypothesisGenerator:
    """Generate research hypotheses from exploratory analysis results"""

    def __init__(self, data_dir='data_storage/', eda_results_dir='complete_analysis/exploratory_analysis/'):
        self.data_dir = data_dir
        self.eda_results_dir = eda_results_dir
        self.datasets = {}
        self.eda_results = {}
        self.hypotheses = []

    def load_data(self):
        """Load datasets and EDA results"""
        print("📂 Loading data and analysis results...")

        # Load datasets
        files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        for file in files:
            try:
                df = pd.read_csv(os.path.join(self.data_dir, file))
                self.datasets[file] = df
                print(f"  ✓ {file}")
            except:
                pass

        # Load EDA results
        eda_path = os.path.join(self.eda_results_dir, 'exploratory_analysis_results.json')
        if os.path.exists(eda_path):
            with open(eda_path, 'r', encoding='utf-8') as f:
                self.eda_results = json.load(f)
            print(f"  ✓ EDA results loaded")

        return self.datasets, self.eda_results

    def generate_correlation_hypotheses(self):
        """Generate hypotheses based on correlations"""
        print("\n🔗 Generating correlation-based hypotheses...")

        hypotheses = []

        # Cross-dataset correlation hypotheses
        if 'Orders.csv' in self.datasets and 'Order Items.csv' in self.datasets:
            orders = self.datasets['Orders.csv']
            order_items = self.datasets['Order Items.csv']

            merged = pd.merge(orders, order_items, on='order_id', how='inner')

            # Price vs Freight correlation
            if 'price' in merged.columns and 'freight_value' in merged.columns:
                corr = merged[['price', 'freight_value']].corr().iloc[0, 1]
                if not np.isnan(corr):
                    hypotheses.append({
                        'id': 'HYP_001',
                        'category': 'Correlation Analysis',
                        'title': 'Product Price and Shipping Cost Relationship',
                        'hypothesis': f'There is a {"positive" if corr > 0 else "negative"} correlation (r={corr:.3f}) between product price and freight value.',
                        'rationale': 'Higher-priced items may incur different shipping costs due to weight, value insurance, or shipping method.',
                        'test_method': 'Pearson correlation test, linear regression analysis',
                        'expected_outcome': 'Significant correlation between price and freight',
                        'business_impact': 'Pricing strategy optimization, shipping cost structure',
                        'datasets': ['Orders.csv', 'Order Items.csv']
                    })

        # Product dimension correlations
        if 'Products.csv' in self.datasets:
            products = self.datasets['Products.csv']
            dim_cols = ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']
            available_dims = [col for col in dim_cols if col in products.columns]

            if len(available_dims) >= 2:
                hypotheses.append({
                    'id': 'HYP_002',
                    'category': 'Product Analysis',
                    'title': 'Product Dimensions and Weight Correlation',
                    'hypothesis': 'Product weight strongly correlates with product dimensions (length, width, height).',
                    'rationale': 'Larger products tend to be heavier, affecting shipping costs and warehouse storage requirements.',
                    'test_method': 'Multi-variable correlation analysis, principal component analysis',
                    'expected_outcome': 'Strong positive correlation (r > 0.5) between weight and dimensions',
                    'business_impact': 'Shipping cost estimation, warehouse optimization, packaging design',
                    'datasets': ['Products.csv']
                })

        print(f"  Generated {len(hypotheses)} correlation hypotheses")
        return hypotheses

    def generate_temporal_hypotheses(self):
        """Generate hypotheses based on temporal patterns"""
        print("\n📅 Generating temporal hypotheses...")

        hypotheses = []

        # Order timing patterns
        if 'Orders.csv' in self.datasets:
            orders = self.datasets['Orders.csv'].copy()

            # Parse dates
            for col in ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_customer_date']:
                if col in orders.columns:
                    orders[col] = pd.to_datetime(orders[col], errors='coerce')

            # Day of week analysis
            if 'order_purchase_timestamp' in orders.columns:
                orders['day_of_week'] = orders['order_purchase_timestamp'].dt.dayofweek
                orders['hour'] = orders['order_purchase_timestamp'].dt.hour

                dow_counts = orders['day_of_week'].value_counts()
                if len(dow_counts) > 0:
                    peak_day = dow_counts.index[0]
                    hypotheses.append({
                        'id': 'HYP_003',
                        'category': 'Temporal Analysis',
                        'title': 'Weekly Purchase Pattern Variation',
                        'hypothesis': f'Purchase volume varies significantly by day of week, with peak activity on day {peak_day}.',
                        'rationale': 'Consumer behavior shows weekly patterns due to work schedules and weekend leisure time.',
                        'test_method': 'ANOVA test, chi-square test for independence',
                        'expected_outcome': 'Significant variation in purchase volume across days',
                        'business_impact': 'Marketing campaign scheduling, resource allocation, inventory planning',
                        'datasets': ['Orders.csv']
                    })

                # Hour of day analysis
                hour_counts = orders['hour'].value_counts()
                if len(hour_counts) > 0:
                    peak_hour = hour_counts.index[0]
                    hypotheses.append({
                        'id': 'HYP_004',
                        'category': 'Temporal Analysis',
                        'title': 'Daily Purchase Time Distribution',
                        'hypothesis': f'Purchase activity peaks during hour {peak_hour}:00, showing clear daily pattern.',
                        'rationale': 'Shopping behavior follows daily routines, with peaks during lunch hours and evenings.',
                        'test_method': 'Time series analysis, hourly distribution comparison',
                        'expected_outcome': 'Significant hourly variation in purchase patterns',
                        'business_impact': 'Ad scheduling, server capacity planning, customer support staffing',
                        'datasets': ['Orders.csv']
                    })

            # Delivery time analysis
            if 'order_purchase_timestamp' in orders.columns and 'order_delivered_customer_date' in orders.columns:
                orders['delivery_days'] = (
                    orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']
                ).dt.days

                valid_deliveries = orders['delivery_days'].dropna()
                if len(valid_deliveries) > 0:
                    avg_delivery = valid_deliveries.mean()
                    hypotheses.append({
                        'id': 'HYP_005',
                        'category': 'Logistics Analysis',
                        'title': 'Delivery Time Consistency',
                        'hypothesis': f'Average delivery time is {avg_delivery:.1f} days with significant variation across regions.',
                        'rationale': 'Delivery times vary by distance, location, and logistics efficiency.',
                        'test_method': 'Descriptive statistics, regional comparison analysis',
                        'expected_outcome': 'Significant variation in delivery times by customer location',
                        'business_impact': 'Customer satisfaction improvement, logistics optimization, delivery expectation management',
                        'datasets': ['Orders.csv', 'Customers.csv']
                    })

        print(f"  Generated {len(hypotheses)} temporal hypotheses")
        return hypotheses

    def generate_customer_hypotheses(self):
        """Generate customer behavior hypotheses"""
        print("\n👥 Generating customer behavior hypotheses...")

        hypotheses = []

        # Customer geographic distribution
        if 'Customers.csv' in self.datasets:
            customers = self.datasets['Customers.csv']

            if 'customer_state' in customers.columns:
                state_counts = customers['customer_state'].value_counts()
                top_states = state_counts.head(3)

                hypotheses.append({
                    'id': 'HYP_006',
                    'category': 'Customer Analysis',
                    'title': 'Geographic Customer Concentration',
                    'hypothesis': f'Customer distribution is highly concentrated, with top 3 states (top: {top_states.index[0]}) accounting for {top_states.sum() / len(customers) * 100:.1f}% of customers.',
                    'rationale': 'E-commerce adoption varies by region due to infrastructure, economic development, and digital literacy.',
                    'test_method': 'Chi-square goodness-of-fit test, geographic concentration analysis',
                    'expected_outcome': 'Significant deviation from uniform distribution across states',
                    'business_impact': 'Regional marketing strategies, logistics hub placement, market expansion planning',
                    'datasets': ['Customers.csv']
                })

        # Customer order frequency
        if 'Orders.csv' in self.datasets:
            orders = self.datasets['Orders.csv']

            if 'customer_id' in orders.columns:
                orders_per_customer = orders['customer_id'].value_counts()
                repeat_customers = (orders_per_customer > 1).sum()
                repeat_rate = repeat_customers / len(orders_per_customer) * 100

                hypotheses.append({
                    'id': 'HYP_007',
                    'category': 'Customer Behavior',
                    'title': 'Customer Repeat Purchase Rate',
                    'hypothesis': f'{repeat_rate:.1f}% of customers have made repeat purchases, indicating customer loyalty level.',
                    'rationale': 'High repeat purchase rate indicates strong customer retention and satisfaction.',
                    'test_method': 'Cohort analysis, retention rate calculation',
                    'expected_outcome': 'Repeat purchase rate varies by customer segment and product category',
                    'business_impact': 'Customer loyalty programs, retention strategies, LTV optimization',
                    'datasets': ['Orders.csv', 'Customers.csv']
                })

        print(f"  Generated {len(hypotheses)} customer hypotheses")
        return hypotheses

    def generate_product_hypotheses(self):
        """Generate product-related hypotheses"""
        print("\n📦 Generating product hypotheses...")

        hypotheses = []

        # Product category analysis
        if 'Products.csv' in self.datasets and 'Categories.csv' in self.datasets:
            products = self.datasets['Products.csv']
            categories = self.datasets['Categories.csv']

            if 'product_category_name' in products.columns:
                category_counts = products['product_category_name'].value_counts()

                if len(category_counts) > 0:
                    top_category = category_counts.index[0]
                    hypotheses.append({
                        'id': 'HYP_008',
                        'category': 'Product Analysis',
                        'title': 'Product Category Concentration',
                        'hypothesis': f'Product catalog is dominated by category "{top_category}" with {category_counts.iloc[0]} products.',
                        'rationale': 'Certain product categories have higher market demand and seller participation.',
                        'test_method': 'Category distribution analysis, Pareto analysis (80/20 rule)',
                        'expected_outcome': 'Top 20% of categories represent 80% of products',
                        'business_impact': 'Category management, inventory strategy, marketplace positioning',
                        'datasets': ['Products.csv', 'Categories.csv']
                    })

        # Product price distribution
        if 'Order Items.csv' in self.datasets:
            order_items = self.datasets['Order Items.csv']

            if 'price' in order_items.columns:
                prices = order_items['price'].dropna()
                median_price = prices.median()
                mean_price = prices.mean()

                if not np.isnan(median_price) and not np.isnan(mean_price):
                    hypotheses.append({
                        'id': 'HYP_009',
                        'category': 'Product Analysis',
                        'title': 'Product Price Distribution Pattern',
                        'hypothesis': f'Product prices show right-skewed distribution (median: ${median_price:.2f}, mean: ${mean_price:.2f}).',
                        'rationale': 'Most products are low-to-mid price, with fewer high-value luxury items.',
                        'test_method': 'Distribution analysis, skewness test, price segment analysis',
                        'expected_outcome': 'Right-skewed distribution with long tail of high-priced items',
                        'business_impact': 'Price segmentation strategy, commission structure, target customer definition',
                        'datasets': ['Order Items.csv']
                    })

        print(f"  Generated {len(hypotheses)} product hypotheses")
        return hypotheses

    def generate_review_hypotheses(self):
        """Generate review and satisfaction hypotheses"""
        print("\n⭐ Generating review hypotheses...")

        hypotheses = []

        if 'Reviews.csv' in self.datasets:
            reviews = self.datasets['Reviews.csv']

            # Review score distribution
            if 'review_score' in reviews.columns:
                score_dist = reviews['review_score'].value_counts().sort_index()
                avg_score = reviews['review_score'].mean()

                if len(score_dist) > 0:
                    hypotheses.append({
                        'id': 'HYP_010',
                        'category': 'Customer Satisfaction',
                        'title': 'Customer Satisfaction Score Distribution',
                        'hypothesis': f'Average review score is {avg_score:.2f}/5.0, indicating overall customer satisfaction level.',
                        'rationale': 'Review scores reflect product quality, delivery experience, and customer service.',
                        'test_method': 'Descriptive statistics, score distribution analysis',
                        'expected_outcome': 'Score distribution shows polarization (high 4-5 stars or low 1-2 stars)',
                        'business_impact': 'Quality monitoring, seller performance evaluation, customer experience improvement',
                        'datasets': ['Reviews.csv']
                    })

            # Review timing
            if 'review_creation_date' in reviews.columns:
                reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'], errors='coerce')

                # Check if there's a delay pattern
                if 'order_delivered_customer_date' in reviews.columns:
                    reviews['order_delivered_customer_date'] = pd.to_datetime(reviews['order_delivered_customer_date'], errors='coerce')

                    # This would require merging with Orders dataset - skip for now
                    pass

            # Review comment length analysis (if comment exists)
            if 'review_comment_message' in reviews.columns:
                reviews['comment_length'] = reviews['review_comment_message'].str.len().fillna(0)
                avg_comment_length = reviews['comment_length'].mean()

                if avg_comment_length > 0:
                    hypotheses.append({
                        'id': 'HYP_011',
                        'category': 'Customer Feedback',
                        'title': 'Review Comment Length and Score Relationship',
                        'hypothesis': f'Customers leaving longer comments (avg: {avg_comment_length:.0f} chars) show different score patterns.',
                        'rationale': 'Detailed comments often indicate strong opinions (very positive or very negative).',
                        'test_method': 'Correlation analysis, sentiment analysis by score',
                        'expected_outcome': 'Negative reviews tend to have longer comments than positive reviews',
                        'business_impact': 'Review sentiment analysis, automated feedback triage, customer insight extraction',
                        'datasets': ['Reviews.csv']
                    })

        print(f"  Generated {len(hypotheses)} review hypotheses")
        return hypotheses

    def generate_payment_hypotheses(self):
        """Generate payment-related hypotheses"""
        print("\n💳 Generating payment hypotheses...")

        hypotheses = []

        if 'Order Payments.csv' in self.datasets:
            payments = self.datasets['Order Payments.csv']

            # Payment method distribution
            if 'payment_type' in payments.columns:
                payment_types = payments['payment_type'].value_counts()
                top_method = payment_types.index[0]
                top_pct = payment_types.iloc[0] / len(payments) * 100

                hypotheses.append({
                    'id': 'HYP_012',
                    'category': 'Payment Analysis',
                    'title': 'Payment Method Preference',
                    'hypothesis': f'Payment method "{top_method}" dominates with {top_pct:.1f}% of all transactions.',
                    'rationale': 'Payment preferences vary by region, demographics, and order value.',
                    'test_method': 'Chi-square test, payment method vs order value analysis',
                    'expected_outcome': 'Significant preference for specific payment methods',
                    'business_impact': 'Payment gateway optimization, checkout flow design, payment cost reduction',
                    'datasets': ['Order Payments.csv']
                })

            # Payment installments
            if 'payment_installments' in payments.columns:
                avg_installments = payments['payment_installments'].mean()
                installment_rate = (payments['payment_installments'] > 1).mean() * 100

                hypotheses.append({
                    'id': 'HYP_013',
                    'category': 'Payment Analysis',
                    'title': 'Installment Payment Usage',
                    'hypothesis': f'{installment_rate:.1f}% of orders use installment payments, with average {avg_installments:.1f} installments.',
                    'rationale': 'Installments enable larger purchases by spreading cost over time.',
                    'test_method': 'Installment vs total value correlation analysis',
                    'expected_outcome': 'Higher order values correlate with more installments',
                    'business_impact': 'Financing strategy, credit risk management, average order value optimization',
                    'datasets': ['Order Payments.csv', 'Order Items.csv']
                })

        print(f"  Generated {len(hypotheses)} payment hypotheses")
        return hypotheses

    def generate_seller_hypotheses(self):
        """Generate seller-related hypotheses"""
        print("\n🏪 Generating seller hypotheses...")

        hypotheses = []

        if 'Sellers.csv' in self.datasets and 'Order Items.csv' in self.datasets:
            sellers = self.datasets['Sellers.csv']
            order_items = self.datasets['Order Items.csv']

            # Seller geographic distribution
            if 'seller_state' in sellers.columns:
                state_counts = sellers['seller_state'].value_counts()
                top_seller_state = state_counts.index[0]

                hypotheses.append({
                    'id': 'HYP_014',
                    'category': 'Seller Analysis',
                    'title': 'Seller Geographic Distribution',
                    'hypothesis': f'Sellers are concentrated in state "{top_seller_state}", indicating regional business hubs.',
                    'rationale': 'Sellers cluster in commercial centers with good logistics infrastructure.',
                    'test_method': 'Geographic concentration analysis, seller vs customer location comparison',
                    'expected_outcome': 'Significant seller concentration in specific states',
                    'business_impact': 'Seller acquisition strategy, logistics network design, regional marketing',
                    'datasets': ['Sellers.csv', 'Customers.csv']
                })

        print(f"  Generated {len(hypotheses)} seller hypotheses")
        return hypotheses

    def generate_validation_plan(self, hypothesis):
        """Generate validation plan for a hypothesis"""
        plan = {
            'hypothesis_id': hypothesis['id'],
            'validation_steps': [
                '1. Data preparation and cleaning',
                '2. Descriptive statistics and visualization',
                '3. Statistical testing',
                '4. Effect size calculation',
                '5. Business impact assessment'
            ],
            'required_metrics': [
                'Statistical significance (p-value < 0.05)',
                'Effect size (Cohen\'s d or correlation strength)',
                'Confidence interval (95%)',
                'Business impact magnitude'
            ],
            'potential_challenges': [
                'Data quality issues (missing values, outliers)',
                'Sample size limitations',
                'Confounding variables',
                'Causality vs correlation'
            ]
        }
        return plan

    def run_hypothesis_generation(self):
        """Run complete hypothesis generation workflow"""
        print("\n" + "="*70)
        print("🔍 STAGE 3: RESEARCH HYPOTHESIS GENERATION")
        print("="*70)

        self.load_data()

        # Generate all hypothesis types
        all_hypotheses = []
        all_hypotheses.extend(self.generate_correlation_hypotheses())
        all_hypotheses.extend(self.generate_temporal_hypotheses())
        all_hypotheses.extend(self.generate_customer_hypotheses())
        all_hypotheses.extend(self.generate_product_hypotheses())
        all_hypotheses.extend(self.generate_review_hypotheses())
        all_hypotheses.extend(self.generate_payment_hypotheses())
        all_hypotheses.extend(self.generate_seller_hypotheses())

        # Add validation plans to each hypothesis
        for hyp in all_hypotheses:
            hyp['validation_plan'] = self.generate_validation_plan(hyp)

        self.hypotheses = all_hypotheses
        return all_hypotheses

    def save_results(self, output_dir='complete_analysis/hypothesis_reports/'):
        """Save hypothesis reports"""
        os.makedirs(output_dir, exist_ok=True)

        # Save JSON with all hypotheses
        json_path = os.path.join(output_dir, 'research_hypotheses.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.hypotheses, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Hypotheses saved to: {json_path}")

        # Generate markdown report
        self._generate_markdown_report(output_dir)

    def _generate_markdown_report(self, output_dir):
        """Generate comprehensive markdown report"""
        report = "# Research Hypotheses Report\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        report += "## Executive Summary\n\n"
        report += f"This report presents {len(self.hypotheses)} testable research hypotheses "
        report += f"generated from exploratory analysis of {len(self.datasets)} e-commerce datasets.\n\n"

        # Group by category
        categories = {}
        for hyp in self.hypotheses:
            cat = hyp['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(hyp)

        report += "## Hypothesis Categories\n\n"
        for cat, hyps in categories.items():
            report += f"- **{cat}**: {len(hyps)} hypotheses\n"

        report += "\n---\n\n"

        # Detailed hypotheses
        for i, hyp in enumerate(self.hypotheses, 1):
            report += f"## {hyp['id']}: {hyp['title']}\n\n"
            report += f"**Category**: {hyp['category']}\n\n"
            report += f"**Hypothesis**: {hyp['hypothesis']}\n\n"
            report += f"**Rationale**: {hyp['rationale']}\n\n"
            report += f"**Test Method**: {hyp['test_method']}\n\n"
            report += f"**Expected Outcome**: {hyp['expected_outcome']}\n\n"
            report += f"**Business Impact**: {hyp['business_impact']}\n\n"
            report += f"**Data Sources**: {', '.join(hyp['datasets'])}\n\n"

            report += "### Validation Plan\n\n"
            for step in hyp['validation_plan']['validation_steps']:
                report += f"{step}\n"
            report += "\n"

            report += "---\n\n"

        # Save report
        report_path = os.path.join(output_dir, 'research_hypotheses.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"💾 Markdown report saved to: {report_path}")

        # Generate experimental design document
        self._generate_experimental_design(output_dir)

    def _generate_experimental_design(self, output_dir):
        """Generate experimental design document"""
        design = "# Experimental Design Document\n\n"
        design += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        design += "## Overview\n\n"
        design += "This document outlines the experimental design for validating "
        design += f"{len(self.hypotheses)} research hypotheses.\n\n"

        design += "## Statistical Framework\n\n"
        design += "### Significance Level\n"
        design += "- Alpha (α): 0.05\n"
        design += "- Confidence Level: 95%\n"
        design += "- Power: 0.80\n\n"

        design += "### Test Selection Criteria\n\n"
        design += "- **Correlation tests**: Pearson (normal), Spearman (non-normal)\n"
        design += "- **Group comparisons**: t-test (2 groups), ANOVA (3+ groups)\n"
        design += "- **Categorical data**: Chi-square test\n"
        design += "- **Distribution analysis**: Shapiro-Wilk test\n\n"

        design += "## Prioritized Hypotheses\n\n"

        # Prioritize by business impact
        priority_hypotheses = sorted(self.hypotheses,
                                   key=lambda x: len(x.get('business_impact', '')),
                                   reverse=True)[:5]

        for i, hyp in enumerate(priority_hypotheses, 1):
            design += f"### Priority {i}: {hyp['id']}\n\n"
            design += f"**Title**: {hyp['title']}\n\n"
            design += f"**Hypothesis**: {hyp['hypothesis']}\n\n"
            design += f"**Test**: {hyp['test_method']}\n\n"
            design += "**Data Requirements**:\n"
            for ds in hyp['datasets']:
                design += f"- {ds}\n"
            design += "\n"

        design += "## Validation Timeline\n\n"
        design += "1. **Week 1**: Data preparation and cleaning\n"
        design += "2. **Week 2**: Descriptive analysis and visualization\n"
        design += "3. **Week 3**: Statistical testing\n"
        design += "4. **Week 4**: Results interpretation and reporting\n\n"

        design_path = os.path.join(output_dir, 'experimental_design.md')
        with open(design_path, 'w', encoding='utf-8') as f:
            f.write(design)
        print(f"💾 Experimental design saved to: {design_path}")

    def print_summary(self):
        """Print hypothesis summary"""
        print("\n" + "="*70)
        print("📋 HYPOTHESIS GENERATION SUMMARY")
        print("="*70)

        # Count by category
        categories = {}
        for hyp in self.hypotheses:
            cat = hyp['category']
            categories[cat] = categories.get(cat, 0) + 1

        print(f"\n📊 Hypotheses Generated: {len(self.hypotheses)} total\n")
        print("By Category:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {cat}: {count} hypotheses")

        print("\n🎯 Top 5 Prioritized Hypotheses:")
        priority = sorted(self.hypotheses,
                         key=lambda x: len(x.get('business_impact', '')),
                         reverse=True)[:5]

        for i, hyp in enumerate(priority, 1):
            print(f"  {i}. [{hyp['id']}] {hyp['title']}")
            print(f"     → {hyp.get('business_impact', '')[:60]}...")

        print("\n" + "="*70)

if __name__ == "__main__":
    # Run hypothesis generation
    generator = HypothesisGenerator()
    hypotheses = generator.run_hypothesis_generation()
    generator.save_results()
    generator.print_summary()

    print("\n✅ STAGE 3 COMPLETE: Research Hypothesis Generation")
    print("  All hypotheses generated with validation plans")
    print("  Proceeding to Stage 4: Data Visualization...")
