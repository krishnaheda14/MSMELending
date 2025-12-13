# Testing Guide - Updated Features

## What's New
✅ **Apply Customer ID Button** - Click to load a different customer
✅ **Comma Formatting** - All money values show ₹1,23,456.78
✅ **Info Buttons (ℹ️)** - Click to see detailed calculations
✅ **Monthly Cashflow Limit** - Shows first 10 months, expand to see more
✅ **Fixed Top Customers** - No more "unknown" customers
✅ **Consent Step Restored** - Step 0 simulates AA consent flow

## How to Test

### 1. Start the Application
The server is already running at:
- **Backend**: http://localhost:5000
- **Frontend**: http://localhost:3000

### 2. Test Customer Selection
1. Open http://localhost:3000
2. You'll see the Pipeline Monitor with 10 customers (CUST_MSM_00001 through CUST_MSM_00010)
3. Click on any customer card (they all say "Random Seed #X")
4. Click the **"Apply Customer ID"** button (or press Enter)
5. Watch the pipeline run through all 5 steps

### 3. Test Earnings vs Spendings Tab
1. After pipeline completes, go to **"Earnings vs Spendings"** tab
2. You should see:
   - ✅ All money values formatted with commas: ₹12,34,567.89
   - ✅ Info buttons (ℹ️) next to each metric title
   - ✅ Monthly cashflow showing only first 10 months
   - ✅ "Show All (X months)" button if more than 10 months
   - ✅ Top 3 customers showing as "Customer-XXX" (not "unknown")

### 4. Test Calculation Details
1. Click any **Info (ℹ️)** button
2. Modal should show:
   - **Formula**: Mathematical formula (e.g., "(Max Month - Min Month) ÷ Avg Month × 100")
   - **Calculation Breakdown**: Actual values used
   - **Explanation**: What it means and how to interpret
3. Try these specific metrics:
   - Income Stability (CV) - Shows coefficient of variation explanation
   - Seasonality Index - Shows max/min/avg monthly values
   - Top Customer Dependence - Shows risk assessment

### 5. Test Monthly Cashflow Expansion
1. Scroll to "Monthly Cashflow Breakdown" table
2. If more than 10 months of data:
   - Should show only first 10 rows
   - "Show All (X months)" button at bottom with ChevronDown icon
   - Click to expand and see all months
   - Click again to collapse back to 10

### 6. Test Different Customers
Try different customer IDs to see variations:
- CUST_MSM_00001 - Original customer
- CUST_MSM_00005 - Mid-range random seed
- CUST_MSM_00010 - Highest random seed
Each should show different:
- Transaction counts
- Income patterns
- Seasonality indices
- Top customer lists

## What to Look For

### ✅ Success Indicators
- No "unknown" in top customers list
- All money values have commas (₹1,23,456.78)
- Info buttons work and show detailed modals
- Cashflow table limited to 10 rows by default
- Expand button works smoothly
- Pipeline completes all 5 steps (0-4)
- Apply Customer ID button responds to clicks and Enter key

### ❌ Potential Issues
If you see:
- "NaN" or "—" values: Some data might be missing for that customer
- Very high seasonality index (>1000%): Random data can have extreme variations
- Empty top customers: Transaction data might not have counterparty information
- "unknown" still showing: Analytics might not have been regenerated

## Quick Fixes

### Re-generate Analytics
If data looks wrong:
```powershell
cd f:\MSMELending\data_lake
python analytics/generate_summaries.py --customer-id CUST_MSM_00001
```

### Rebuild Frontend
If UI changes don't appear:
```powershell
cd f:\MSMELending\data_lake\frontend
npm run build
```

### Restart Server
If needed:
1. Press Ctrl+C in the terminal running the server
2. Run: `cd f:\MSMELending\data_lake; cmd /c run_fullstack.bat`

## Screenshots to Verify

### Pipeline Monitor
- [ ] Shows 5 steps: Consent (0) → Clean (1) → Analytics (2) → Score (3) → Decision (4)
- [ ] Customer cards show "Random Seed #1" through "Random Seed #10"
- [ ] "Apply Customer ID" button visible and functional
- [ ] Warning message about random data visible

### Earnings Tab
- [ ] All amounts show commas: ₹1,23,456.78
- [ ] Blue info (ℹ️) icons next to metric titles
- [ ] Monthly table shows max 10 rows initially
- [ ] Top customers show "Customer-XXX" labels
- [ ] Color coding (green for positive, red for negative)

### Calculation Modals
- [ ] Formula displayed in blue box
- [ ] Breakdown shows all input values with ₹ symbols
- [ ] Explanation text is data-specific (uses actual customer values)
- [ ] Close button works

---

**All tests passing?** You're good to go! 🎉

**Found issues?** Check the troubleshooting section above or regenerate analytics.
