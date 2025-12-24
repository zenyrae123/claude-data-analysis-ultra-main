# Experimental Design Document

Generated: 2025-12-24 12:12:37

## Overview

This document outlines the experimental design for validating 14 research hypotheses.

## Statistical Framework

### Significance Level
- Alpha (α): 0.05
- Confidence Level: 95%
- Power: 0.80

### Test Selection Criteria

- **Correlation tests**: Pearson (normal), Spearman (non-normal)
- **Group comparisons**: t-test (2 groups), ANOVA (3+ groups)
- **Categorical data**: Chi-square test
- **Distribution analysis**: Shapiro-Wilk test

## Prioritized Hypotheses

### Priority 1: HYP_005

**Title**: Delivery Time Consistency

**Hypothesis**: Average delivery time is 12.1 days with significant variation across regions.

**Test**: Descriptive statistics, regional comparison analysis

**Data Requirements**:
- Orders.csv
- Customers.csv

### Priority 2: HYP_010

**Title**: Customer Satisfaction Score Distribution

**Hypothesis**: Average review score is 4.09/5.0, indicating overall customer satisfaction level.

**Test**: Descriptive statistics, score distribution analysis

**Data Requirements**:
- Reviews.csv

### Priority 3: HYP_006

**Title**: Geographic Customer Concentration

**Hypothesis**: Customer distribution is highly concentrated, with top 3 states (top: SP) accounting for 66.6% of customers.

**Test**: Chi-square goodness-of-fit test, geographic concentration analysis

**Data Requirements**:
- Customers.csv

### Priority 4: HYP_011

**Title**: Review Comment Length and Score Relationship

**Hypothesis**: Customers leaving longer comments (avg: 28 chars) show different score patterns.

**Test**: Correlation analysis, sentiment analysis by score

**Data Requirements**:
- Reviews.csv

### Priority 5: HYP_009

**Title**: Product Price Distribution Pattern

**Hypothesis**: Product prices show right-skewed distribution (median: $74.99, mean: $120.65).

**Test**: Distribution analysis, skewness test, price segment analysis

**Data Requirements**:
- Order Items.csv

## Validation Timeline

1. **Week 1**: Data preparation and cleaning
2. **Week 2**: Descriptive analysis and visualization
3. **Week 3**: Statistical testing
4. **Week 4**: Results interpretation and reporting

