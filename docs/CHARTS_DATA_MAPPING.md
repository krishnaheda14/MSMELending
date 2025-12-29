# Customer Profile - Chart Data Mapping Guide

This document maps each chart to its data source and explains the scaling logic.

---

## Chart-to-Data Mapping

### Tab 1: Transactions

| Chart | Data Source | X-Axis | Y-Axis | Scale |
|-------|-------------|--------|--------|-------|
| Transaction Amount Pie | `transaction_summary.by_type` | N/A | Transaction amounts | ₹ (formatted) |
| Transaction Count Bar | `transaction_summary.by_type` | Type (Credit/Debit) | Count | Whole numbers |

**Data Structure:**
```json
{
  "by_type": {
    "CREDIT": { "count": 1500, "amount": 50000000 },
    "DEBIT": { "count": 1200, "amount": 35000000 }
  }
}
```

---

### Tab 2: GST Summary

| Chart | Data Source | X-Axis | Y-Axis | Scale |
|-------|-------------|--------|--------|-------|
| Monthly Turnover Area | `gst_summary.monthly_turnover` | Month | Turnover amount | ₹K (thousands) |

**Data Structure:**
```json
{
  "monthly_turnover": {
    "01-2024": 1500000,
    "02-2024": 1750000,
    "03-2024": 1600000
  }
}
```

**Scaling Logic:**
```javascript
tickFormatter={(value) => `₹${(value/1000).toFixed(1)}K`}
// Example: 1500000 → ₹1500.0K
```

---

### Tab 3: Earnings & Spendings

| Chart | Data Source | X-Axis | Y-Axis | Scale |
|-------|-------------|--------|--------|-------|
| Monthly Cashflow Bar | `earnings_spendings.cashflow_metrics.monthly_inflow/outflow` | Month | Amount | ₹M (millions) |
| Top Customers Bar | `earnings_spendings.cashflow_metrics.top_customers` | Customer name | Revenue | ₹M (millions) |
| Expense Composition Pie | `earnings_spendings.expense_composition` | N/A | Amount | ₹ (formatted) |
| Credit Health Bar | `earnings_spendings.credit_behavior` | Metric name | Score (normalized) | 0-100 scale |

**Data Structure:**
```json
{
  "cashflow_metrics": {
    "monthly_inflow": { "01-2024": 2500000, "02-2024": 3000000 },
    "monthly_outflow": { "01-2024": 1800000, "02-2024": 2200000 },
    "top_customers": [
      { "name": "Customer A", "amount": 5000000 },
      { "name": "Customer B", "amount": 4500000 }
    ]
  },
  "expense_composition": {
    "essential_spend": 10000000,
    "non_essential_spend": 5000000,
    "debt_servicing": 3000000
  },
  "credit_behavior": {
    "bounces": 2,
    "emi_consistency_score": 85.5,
    "credit_utilization_ratio": 45.2,
    "default_probability_score": 15.8,
    "debt_to_income_ratio": 35.0,
    "payment_regularity_score": 92.0
  }
}
```

**Credit Health Normalization:**
```javascript
// Invert scores where lower is better
{ metric: 'Default Risk', score: 100 - (credit.default_probability_score || 0) }
{ metric: 'DTI Health', score: Math.max(0, 100 - (credit.debt_to_income_ratio || 0)) }
{ metric: 'Credit Utilization', score: Math.max(0, 100 - (credit.credit_utilization_ratio || 0)) }

// Keep scores where higher is better
{ metric: 'EMI Consistency', score: credit.emi_consistency_score || 0 }
{ metric: 'Payment Regularity', score: credit.payment_regularity_score || 0 }
```

---

### Tab 4: Credit (Loans)

| Chart | Data Source | X-Axis | Y-Axis | Scale |
|-------|-------------|--------|--------|-------|
| Loan Count Pie | `credit.loan_types` | N/A | Count | Whole numbers |
| Outstanding by Type Bar | `credit.outstanding_by_type` | Loan type | Amount | ₹L (lakhs) |

**Data Structure:**
```json
{
  "loan_types": {
    "Personal Loan": 3,
    "Business Loan": 2,
    "Home Loan": 1
  },
  "outstanding_by_type": {
    "Personal Loan": 500000,
    "Business Loan": 2000000,
    "Home Loan": 5000000
  }
}
```

**Scaling Logic:**
```javascript
tickFormatter={(value) => `₹${(value/100000).toFixed(1)}L`}
// Example: 2000000 → ₹20.0L
```

---

### Tab 5: OCEN (Loan Applications)

| Chart | Data Source | X-Axis | Y-Axis | Scale |
|-------|-------------|--------|--------|-------|
| Application Status Pie | Calculated from `ocen.total_applications` & `approved_count` | N/A | Count | Whole numbers |
| Applications by Purpose Bar | `ocen.by_purpose` | Loan purpose | Application count | Whole numbers |

**Data Structure:**
```json
{
  "total_applications": 50,
  "approved_count": 35,
  "approval_rate": 70.0,
  "by_purpose": {
    "Working Capital": 20,
    "Equipment Purchase": 15,
    "Expansion": 10,
    "Inventory": 5
  }
}
```

**Status Calculation:**
```javascript
const statusData = [
  { name: 'Approved', value: data.approved_count || 0 },
  { name: 'Rejected', value: (data.total_applications || 0) - (data.approved_count || 0) }
];
```

---

### Tab 6: ONDC (Digital Commerce)

| Chart | Data Source | X-Axis | Y-Axis | Scale |
|-------|-------------|--------|--------|-------|
| Top Categories Bar | `ondc.by_category` | Category name | Order value | ₹L (lakhs) |
| Order Count Pie | `ondc.by_category` | N/A | Order count | Whole numbers |
| Top Providers Bar | `ondc.by_provider` | Provider name | Order count | Whole numbers |

**Data Structure:**
```json
{
  "total_orders": 250,
  "total_order_value": 5000000,
  "provider_diversity": 15,
  "by_category": {
    "Electronics": { "count": 50, "value": 2000000 },
    "Groceries": { "count": 100, "value": 1500000 },
    "Clothing": { "count": 75, "value": 1000000 }
  },
  "by_provider": {
    "Provider A": 80,
    "Provider B": 70,
    "Provider C": 60
  }
}
```

**Scaling Logic:**
```javascript
// For large values
tickFormatter={(value) => `₹${(value/100000).toFixed(1)}L`}
// Example: 2000000 → ₹20.0L

// Average order value calculated as:
const avgOrderValue = (data.total_order_value || 0) / (data.total_orders || 1);
```

---

### Tab 7: Mutual Funds

| Chart | Data Source | X-Axis | Y-Axis | Scale |
|-------|-------------|--------|--------|-------|
| AMC Distribution Pie | `mutual_funds.by_amc` | N/A | Portfolio value | ₹ (formatted) |
| Invested vs Current Bar | `mutual_funds.by_amc` | AMC name | Amount | ₹L (lakhs) |

**Data Structure:**
```json
{
  "total_portfolios": 12,
  "total_invested": 5000000,
  "total_current_value": 6500000,
  "by_amc": {
    "HDFC Mutual Fund": {
      "count": 4,
      "invested": 2000000,
      "value": 2500000
    },
    "ICICI Prudential": {
      "count": 3,
      "invested": 1500000,
      "value": 2000000
    }
  }
}
```

**Returns Calculation:**
```javascript
const totalReturns = (data.total_current_value || 0) - (data.total_invested || 0);
const returnPercentage = data.total_invested > 0 
  ? ((totalReturns / data.total_invested) * 100).toFixed(2)
  : 0;
// Example: (6500000 - 5000000) / 5000000 * 100 = 30.00%
```

---

### Tab 8: Insurance

| Chart | Data Source | X-Axis | Y-Axis | Scale |
|-------|-------------|--------|--------|-------|
| Coverage Distribution Pie | `insurance.by_type` | N/A | Coverage amount | ₹ (formatted) |
| Coverage Amount Bar | `insurance.by_type` | Policy type | Coverage | ₹Cr (crores) |

**Data Structure:**
```json
{
  "total_policies": 5,
  "total_coverage": 50000000,
  "total_premium": 500000,
  "by_type": {
    "Life Insurance": {
      "count": 2,
      "coverage": 30000000
    },
    "Health Insurance": {
      "count": 2,
      "coverage": 15000000
    },
    "Business Insurance": {
      "count": 1,
      "coverage": 5000000
    }
  }
}
```

**Scaling Logic:**
```javascript
tickFormatter={(value) => `₹${(value/10000000).toFixed(1)}Cr`}
// Example: 30000000 → ₹3.0Cr

// Average premium per policy
const avgPremium = (data.total_premium || 0) / (data.total_policies || 1);
```

---

## Scale Selection Decision Tree

```
Is the value type CURRENCY?
├─ Yes
│  ├─ Is max value < 100,000?
│  │  └─ Use: ₹{value} (full amount)
│  ├─ Is max value < 10,000,000?
│  │  └─ Use: ₹{value/1000}K (thousands)
│  ├─ Is max value < 100,000,000?
│  │  └─ Use: ₹{value/100000}L (lakhs)
│  └─ Otherwise
│     └─ Use: ₹{value/10000000}Cr (crores)
│
├─ Is the value type PERCENTAGE?
│  └─ Use: {value}% with domain [0, 100]
│
├─ Is the value type COUNT?
│  └─ Use: {value} (whole number)
│
└─ Is the value type SCORE?
   ├─ Normalize to 0-100 scale for comparison charts
   └─ Show original value in tooltip
```

---

## Formatting Functions Reference

### Currency Formatter
```javascript
const formatCurrency = (value) => {
  if (value >= 10000000) return `₹${(value/10000000).toFixed(2)}Cr`;
  if (value >= 100000) return `₹${(value/100000).toFixed(2)}L`;
  if (value >= 1000) return `₹${(value/1000).toFixed(2)}K`;
  return `₹${value.toFixed(2)}`;
};
```

### Number Formatter
```javascript
const formatNumber = (value) => {
  if (!value) return '0';
  return value.toLocaleString('en-IN');
};
```

### Percentage Formatter
```javascript
const formatPercent = (value) => {
  return `${value.toFixed(2)}%`;
};
```

---

## Chart Height Guidelines

| Chart Type | Data Points | Recommended Height | Reason |
|------------|-------------|-------------------|---------|
| Pie Chart | Any | 280px | Standard circular display |
| Bar Chart (Vertical) | < 10 items | 280px | Comfortable spacing |
| Bar Chart (Vertical) | 10-20 items | 350px | Prevents crowding |
| Bar Chart (Horizontal) | Any | 280-350px | Depends on label length |
| Line/Area Chart | < 50 points | 300px | Standard time series |
| Line/Area Chart | > 50 points | 400px | Better trend visibility |

---

## Color Mapping by Context

| Context | Color | Hex | Usage |
|---------|-------|-----|-------|
| Positive/Profit | Green | #10B981 | Inflow, Gains, Approved |
| Negative/Loss | Red | #EF4444 | Outflow, Losses, Rejected |
| Warning | Yellow | #F59E0B | Moderate risk, Pending |
| Information | Blue | #3B82F6 | Neutral metrics |
| Primary Action | Blue | #3B82F6 | Interactive elements |
| Credit Score (High) | Green | #10B981 | Good scores (>70) |
| Credit Score (Medium) | Yellow | #F59E0B | Medium scores (40-70) |
| Credit Score (Low) | Red | #EF4444 | Poor scores (<40) |

---

## Responsive Breakpoints

```javascript
// Tailwind CSS breakpoints used:
'grid-cols-1'           // Mobile: 1 column (< 640px)
'md:grid-cols-2'        // Tablet: 2 columns (≥ 768px)
'md:grid-cols-3'        // Desktop: 3 columns (≥ 768px)
'md:grid-cols-4'        // Desktop: 4 columns (≥ 768px)
'lg:grid-cols-2'        // Large: 2 columns (≥ 1024px)

// Chart containers
'w-full'                // 100% width on all devices
ResponsiveContainer     // Adapts to parent width
```

---

## Data Validation Examples

### Example 1: Safe Array Access
```javascript
const topCustomersData = cashflow.top_customers?.slice(0, 10).map(c => ({
  name: c.name?.length > 20 ? c.name.substring(0, 20) + '...' : c.name,
  amount: c.amount
})) || [];

// Returns [] if:
// - cashflow is null/undefined
// - top_customers is null/undefined
// - Array is empty
```

### Example 2: Zero Value Filtering
```javascript
const expenseData = [
  { name: 'Essential', value: expenses.essential_spend || 0 },
  { name: 'Non-Essential', value: expenses.non_essential_spend || 0 },
  { name: 'Debt Servicing', value: expenses.debt_servicing || 0 }
].filter(item => item.value > 0);

// Prevents:
// - Empty pie chart slices
// - Division by zero in percentages
// - Misleading visualizations
```

### Example 3: Safe Division
```javascript
const avgOrderValue = (data.total_order_value || 0) / (data.total_orders || 1);

// Prevents:
// - Division by zero
// - NaN values
// - Crashed charts
```

---

## Tooltip Format Examples

### Currency Tooltip
```javascript
<Tooltip content={<CustomTooltip formatter={formatCurrency} />} />
// Displays: "₹2.5L" instead of "2500000"
```

### Percentage Tooltip
```javascript
<Tooltip 
  formatter={(value) => `${value.toFixed(2)}%`}
  labelFormatter={(label) => `Month: ${label}`}
/>
// Displays: "Month: Jan-2024" and "45.50%"
```

### Multi-Line Tooltip
```javascript
// When chart has multiple bars/lines:
{payload.map((entry, index) => (
  <p key={index} style={{ color: entry.color }}>
    {entry.name}: {formatter(entry.value)}
  </p>
))}
// Displays:
// Inflow: ₹2.5M
// Outflow: ₹1.8M
```

---

## Performance Optimization Notes

1. **Data Slicing:**
   ```javascript
   .slice(-12)  // Only last 12 months
   .slice(0, 10) // Only top 10 items
   ```

2. **Conditional Rendering:**
   ```javascript
   {categoryOrderData.length > 0 && (
     <div>Chart Component</div>
   )}
   ```

3. **Memoization Opportunity:**
   ```javascript
   // Future enhancement - useMemo for expensive calculations
   const expenseData = useMemo(() => [...], [expenses]);
   ```

---

*This guide should be used in conjunction with CHARTS_IMPLEMENTATION_SUMMARY.md for complete understanding.*
