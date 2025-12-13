# Remaining UI Improvements - Summary

## ✅ Completed Changes

1. ✅ **Added "Apply Customer ID" button** - Next to customer ID input in Pipeline Monitor
2. ✅ **Restored Consent & Fetch step** - Added back as Step 0 (simulated AA consent)
3. ✅ **Updated pipeline flow** - Now shows 5 steps (0: Consent, 1: Clean, 2: Analytics, 3: Score, 4: Decision)
4. ✅ **Updated customer profile grid** - Now reflects honest description (random data with different seeds)
5. ✅ **Updated documentation** - CUSTOMER_PROFILES.md now clarifies that datasets are randomly generated
6. ✅ **Created formatters utility** - formatCurrency, formatNumber, formatPercent functions
7. ✅ **Started EarningsVsSpendings improvements** - Added imports and state for expansion

## 🔄 In Progress / TODO

### EarningsVsSpendings.js Major Updates Needed:

1. **Format all money values with commas** using formatCurrency()
   - Net Surplus
   - Monthly inflow/outflow
   - All transaction amounts
   - Top customers amounts

2. **Fix "unknown" in top customers** 
   - Need to fetch customer/user names from the transaction data
   - Map user_ids to actual names

3. **Add info (i) buttons for ALL parameters** with detailed calculations:
   - Seasonality Index - show formula, data sources, actual values
   - Income Stability (CV) - show mean, std dev, CV calculation
   - Expense Composition - show category breakdown from data
   - Business Health metrics - show source data
   - Each metric needs its own detailed modal

4. **Limit monthly cashflow to first 10 items**
   - Add "Expand for more" button
   - Show trend chart below the table

5. **Make explanations dynamic** based on actual customer data
   - Currently all showing same generic text
   - Should reference actual values from the dataset
   - Show real transaction patterns, not placeholders

6. **Remove parameters without necessary data**
   - Check if all calculated metrics have supporting data
   - Don't show metrics if underlying data is missing

7. **Explain data sources for each parameter**
   - For every metric, list:
     - Which dataset files are used (transactions.ndjson, gst.ndjson, etc.)
     - What fields are extracted
     - How the calculation is performed
     - Example with real numbers

## Backend Changes Needed

### analytics/financial_metrics.py
- Update calculation functions to include detailed breakdowns
- Add data source references in output
- Include intermediate calculation steps
- Return sample data points used in calculations

### analytics/generate_summaries.py  
- Pass customer names/user mappings to earnings_spendings
- Include trend data for charts
- Add month-by-month breakdowns

## Testing Checklist

Once changes are complete, test with multiple customers:

- [ ] CUST_MSM_00001 - Verify calculations use actual data
- [ ] CUST_MSM_00005 - Verify seasonality detection works
- [ ] CUST_MSM_00007 - Verify limited history is handled
- [ ] All customers - Verify money formatting with commas
- [ ] All customers - Verify info buttons show correct calculations
- [ ] All customers - Verify top customers show names not "unknown"
- [ ] All customers - Verify explanations are unique and data-driven

## Priority Order

1. **HIGH**: Fix unknown customer names (breaks credibility)
2. **HIGH**: Add comma formatting to all money values (readability)
3. **MEDIUM**: Add detailed info buttons with calculations
4. **MEDIUM**: Make explanations dynamic based on data
5. **MEDIUM**: Limit cashflow display with expand button
6. **LOW**: Add trend chart below cashflow table

---

## Current Status

The system is now:
- ✅ Demo-ready with 10 generated customers
- ✅ Has realistic AA consent flow (simulated)
- ✅ Has proper 4-step pipeline
- ✅ Has honest documentation about random data
- ⚠️ Needs EarningsVsSpendings improvements for polished demo
- ⚠️ Needs dynamic explanations using actual data

**Estimated time for remaining UI polish: 2-3 hours**
