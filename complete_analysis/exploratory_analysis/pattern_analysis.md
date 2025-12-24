# Exploratory Data Analysis Report

Generated: 2025-12-24 12:10:45

## Overview

This report presents comprehensive exploratory analysis of 8 e-commerce datasets.

## Categories.csv

**Dimensions**: 71 rows × 2 columns  
**Memory Usage**: 0.01 MB


---

## Customers.csv

**Dimensions**: 99,441 rows × 5 columns  
**Memory Usage**: 29.62 MB


---

## Order Items.csv

**Dimensions**: 112,650 rows × 7 columns  
**Memory Usage**: 39.43 MB

### 📈 Key Trends

- ↓ shipping_limit_date: -98.9% growth

### ⚠️ Notable Outliers

- **order_item_id**: 12.4% outliers (range: 1.00 - 1.00)
- **price**: 7.5% outliers (range: -102.60 - 277.40)
- **freight_value**: 10.8% outliers (range: 0.98 - 33.25)

---

## Order Payments.csv

**Dimensions**: 103,886 rows × 5 columns  
**Memory Usage**: 17.81 MB


### ⚠️ Notable Outliers

- **payment_sequential**: 4.4% outliers (range: 1.00 - 1.00)
- **payment_installments**: 6.1% outliers (range: -3.50 - 8.50)
- **payment_value**: 7.7% outliers (range: -115.78 - 344.41)

---

## Orders.csv

**Dimensions**: 99,441 rows × 8 columns  
**Memory Usage**: 56.88 MB

### 📈 Key Trends

- ↑ order_delivered_carrier_date: 19134.5% growth
- ↑ order_delivered_customer_date: 20221.3% growth

---

## Products.csv

**Dimensions**: 32,951 rows × 9 columns  
**Memory Usage**: 6.79 MB


### ⚠️ Notable Outliers

- **product_name_lenght**: 0.9% outliers (range: 19.50 - 79.50)
- **product_description_lenght**: 6.4% outliers (range: -610.50 - 1921.50)
- **product_photos_qty**: 2.6% outliers (range: -2.00 - 6.00)

---

## Reviews.csv

**Dimensions**: 99,224 rows × 7 columns  
**Memory Usage**: 42.74 MB

### 📈 Key Trends

- ↑ review_creation_date: 17181.2% growth

### ⚠️ Notable Outliers

- **review_score**: 14.7% outliers (range: 2.50 - 6.50)

---

## Sellers.csv

**Dimensions**: 3,095 rows × 4 columns  
**Memory Usage**: 0.66 MB


---

## Cross-Dataset Insights

### Orders.csv + Order Items.csv

- **average_order_value**: 140.64
- **total_records_analyzed**: 112,650.00
