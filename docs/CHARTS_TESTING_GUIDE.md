# Chart Testing & Verification Guide

## Quick Test Instructions

### Step 1: Start the Backend
```powershell
cd f:\MSMELending\data_lake\api_panel
python app.py
```
Expected output: Server running on `http://localhost:5000`

### Step 2: Open Frontend
Navigate to: `http://localhost:5000`

### Step 3: Test Customer Profile Charts

#### 3.1 Select a Customer
- Click on "Customer Profile" in sidebar
- Select customer: **CUST_MSM_00001** (recommended for testing)

#### 3.2 Verify Each Tab

##### ✅ Transactions Tab
**Expected Charts:**
1. **Pie Chart**: Transaction Amount Distribution
   - Check: Green (Credit) and Red (Debit) slices
   - Verify: Percentages add up to 100%
   - Hover: Tooltip shows formatted currency (₹)

2. **Bar Chart**: Transaction Count by Type
   - Check: Two bars (Credit, Debit)
   - Verify: Y-axis shows whole numbers
   - Hover: Tooltip shows count

**Test Cases:**
- [ ] Pie chart renders without errors
- [ ] Bar chart displays correct counts
- [ ] Colors match (Green=Credit, Red=Debit)
- [ ] Tooltips show formatted values

---

##### ✅ GST Summary Tab
**Expected Charts:**
1. **Area Chart**: Monthly GST Turnover (Last 12 Months)
   - Check: Blue gradient fill
   - Verify: X-axis labels at angle (readable)
   - Verify: Y-axis shows ₹K format (e.g., "₹1500K")
   - Hover: Tooltip shows full currency

**Test Cases:**
- [ ] Chart shows 12 data points (or less if data is limited)
- [ ] X-axis labels don't overlap
- [ ] Y-axis uses K/L abbreviation appropriately
- [ ] Gradient fill visible
- [ ] Tooltip accurate

---

##### ✅ Earnings & Spendings Tab
**Expected Charts:**
1. **Bar Chart**: Monthly Inflow vs Outflow
   - Check: Dual bars (Green=Inflow, Red=Outflow)
   - Verify: Y-axis shows ₹M format (millions)
   - Verify: Last 12 months displayed

2. **Horizontal Bar Chart**: Top 10 Customers
   - Check: Revenue amounts
   - Verify: Customer names truncated if long
   - Verify: Y-axis shows ₹M format

3. **Pie Chart**: Expense Composition
   - Check: 3 slices (Essential, Non-Essential, Debt)
   - Verify: Percentages labeled
   - Hover: Shows formatted amounts

4. **Bar Chart**: Credit Health Indicators
   - Check: 5 bars with different colors
   - Verify: Y-axis scale 0-100
   - Check: Higher bars = better health

**Test Cases:**
- [ ] All 4 charts render
- [ ] Monthly comparison chart shows both inflow/outflow
- [ ] Expense pie shows 3 categories
- [ ] Credit health normalized to 0-100
- [ ] Colors appropriate for each metric
- [ ] No overlapping labels

---

##### ✅ Credit (Loans) Tab
**Expected Charts:**
1. **Pie Chart**: Loan Count by Type
   - Check: Multiple colored slices for loan types
   - Verify: Percentages labeled

2. **Bar Chart**: Outstanding Amount by Loan Type
   - Check: Bars for each loan type
   - Verify: Y-axis shows ₹L format (lakhs)
   - Verify: Red color (indicates debt)

**Test Cases:**
- [ ] Pie chart shows loan distribution
- [ ] Bar chart displays outstanding amounts
- [ ] Y-axis uses lakh abbreviation
- [ ] All loan types visible

---

##### ✅ OCEN Tab
**Expected Charts:**
1. **Pie Chart**: Application Status (Approved vs Rejected)
   - Check: Green (Approved) and Red (Rejected)
   - Verify: Matches approval rate shown in cards

2. **Bar Chart**: Applications by Loan Purpose
   - Check: Bars for each purpose
   - Verify: Y-axis shows whole numbers

**Test Cases:**
- [ ] Status pie shows correct proportions
- [ ] Purpose bar chart displays all categories
- [ ] Colors correct (Green=Approved, Red=Rejected)
- [ ] Approval rate card matches pie chart

---

##### ✅ ONDC Tab
**Expected Charts:**
1. **Bar Chart**: Top 10 Categories by Order Value
   - Check: Sorted by value (descending)
   - Verify: Y-axis shows ₹L format
   - Verify: X-axis labels angled

2. **Pie Chart**: Order Count by Category (Top 6)
   - Check: Multi-colored slices
   - Verify: Percentages labeled

3. **Horizontal Bar Chart**: Top 10 Providers
   - Check: Sorted by order count
   - Verify: Provider names visible

**Test Cases:**
- [ ] All 3 charts render
- [ ] Category value chart sorted correctly
- [ ] Pie shows top 6 categories only
- [ ] Provider chart horizontal layout
- [ ] No label overlap

---

##### ✅ Mutual Funds Tab
**Expected Charts:**
1. **Pie Chart**: Portfolio Distribution by AMC
   - Check: Multiple AMCs represented
   - Verify: Percentages add up to 100%

2. **Bar Chart**: Invested vs Current Value
   - Check: Dual bars (Yellow=Invested, Green=Current)
   - Verify: Y-axis shows ₹L format
   - Check: Green bars taller = profit

**Test Cases:**
- [ ] AMC pie shows distribution
- [ ] Comparison chart shows gains/losses
- [ ] Returns card shows correct calculation
- [ ] Color coding: Green=positive, Red=negative

---

##### ✅ Insurance Tab
**Expected Charts:**
1. **Pie Chart**: Coverage Distribution by Type
   - Check: Policy types represented
   - Verify: Percentages labeled

2. **Bar Chart**: Coverage Amount by Type
   - Check: Bars for each policy type
   - Verify: Y-axis shows ₹Cr format (crores)

**Test Cases:**
- [ ] Coverage pie accurate
- [ ] Bar chart uses crore scale
- [ ] Policy type cards match chart data
- [ ] Total coverage adds up

---

## Automated Test Checklist

### Visual Tests
```
For EACH chart:
1. Chart container exists: ✓
2. ResponsiveContainer renders: ✓
3. No React errors in console: ✓
4. Data points visible: ✓
5. Axes labeled correctly: ✓
6. Legend present (if applicable): ✓
7. Tooltips functional: ✓
8. Colors distinct: ✓
```

### Data Tests
```
For EACH tab:
1. Data fetches successfully: ✓
2. No null/undefined errors: ✓
3. Arrays have expected length: ✓
4. Numbers formatted correctly: ✓
5. Percentages in 0-100 range: ✓
6. Currency shows ₹ symbol: ✓
```

### Responsive Tests
```
Screen sizes to test:
1. Mobile (375px): ✓
2. Tablet (768px): ✓
3. Desktop (1024px): ✓
4. Large (1440px): ✓

For each size:
- Charts stack vertically on mobile
- Charts side-by-side on desktop
- No horizontal scroll
- Text readable
```

---

## Common Issues & Solutions

### Issue 1: Chart Not Rendering
**Symptoms:** Empty space where chart should be

**Checks:**
```javascript
// 1. Data exists?
console.log('Data:', data);

// 2. Array has items?
console.log('Chart data length:', chartData.length);

// 3. Check for null values
const filteredData = data.filter(item => item.value !== null);
```

**Solution:** Ensure data is not null/undefined before rendering

---

### Issue 2: X-Axis Labels Overlapping
**Symptoms:** Labels on top of each other

**Solution:**
```javascript
<XAxis 
  dataKey="name" 
  angle={-45}        // Angle the labels
  textAnchor="end"   // Align text
  height={80}        // Increase height
  tick={{ fontSize: 10 }} // Reduce font size
/>
```

---

### Issue 3: Y-Axis Not Scaling Properly
**Symptoms:** All bars/lines at bottom of chart

**Checks:**
```javascript
// Check value ranges
console.log('Min:', Math.min(...data.map(d => d.value)));
console.log('Max:', Math.max(...data.map(d => d.value)));
```

**Solution:**
```javascript
// Add domain
<YAxis domain={[0, 'auto']} />

// Or use dataMax
<YAxis domain={[0, 'dataMax + 1000']} />
```

---

### Issue 4: Tooltip Shows Raw Numbers
**Symptoms:** "2500000" instead of "₹2.5M"

**Solution:**
```javascript
<Tooltip content={<CustomTooltip formatter={formatCurrency} />} />
```

---

### Issue 5: Pie Chart Too Small/Large
**Symptoms:** Pie doesn't fit container

**Solution:**
```javascript
<Pie
  cx="50%"           // Center X
  cy="50%"           // Center Y
  outerRadius={90}   // Adjust size
  // ...
/>
```

---

## Performance Benchmarks

### Expected Load Times (on localhost)
- **Tab Switch:** < 100ms
- **Chart Render:** < 200ms per chart
- **Data Fetch:** < 500ms
- **Tooltip Hover:** Instant

### Memory Usage
- **Initial Load:** ~50MB
- **All Tabs Viewed:** ~80MB
- **Memory Leaks:** None (verify with Chrome DevTools)

---

## Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Fully Supported |
| Firefox | 88+ | ✅ Fully Supported |
| Safari | 14+ | ✅ Fully Supported |
| Edge | 90+ | ✅ Fully Supported |
| IE 11 | - | ❌ Not Supported |

---

## Test Data Validation

### Customer CUST_MSM_00001 Expected Data:
```json
{
  "transactions": {
    "total": 2766,
    "credit_count": ~1500,
    "debit_count": ~1200
  },
  "gst": {
    "monthly_turnover": "12 months of data"
  },
  "earnings": {
    "total_inflow": "₹26.35Cr",
    "total_outflow": "₹15.45Cr",
    "net_surplus": "₹10.90Cr"
  },
  "credit": {
    "bureau_score": "750",
    "open_loans": "5-8",
    "loan_types": "Multiple types"
  },
  "ocen": {
    "total_applications": "50+",
    "approval_rate": "60-80%"
  },
  "ondc": {
    "total_orders": "200+",
    "categories": "10+ categories"
  },
  "mutual_funds": {
    "portfolios": "10+",
    "returns": "Positive"
  },
  "insurance": {
    "policies": "5+",
    "coverage": "₹5Cr+"
  }
}
```

---

## Screenshot Locations
(To be captured during testing)

```
docs/screenshots/
├── transactions_tab_charts.png
├── gst_tab_chart.png
├── earnings_tab_charts.png
├── credit_tab_charts.png
├── ocen_tab_charts.png
├── ondc_tab_charts.png
├── mutual_funds_tab_charts.png
└── insurance_tab_charts.png
```

---

## Testing Commands

### 1. Check for Console Errors
```javascript
// In browser console
console.clear();
// Navigate through all tabs
// Look for errors (red text)
```

### 2. Verify Chart Data
```javascript
// In browser console
// After loading a tab
const data = document.querySelector('[data-testid="chart"]');
console.log('Chart rendered:', !!data);
```

### 3. Check Responsive Behavior
```
1. Open DevTools (F12)
2. Toggle Device Toolbar (Ctrl+Shift+M)
3. Test each preset:
   - iPhone 12 Pro (390px)
   - iPad (768px)
   - Desktop (1024px)
```

---

## Sign-Off Checklist

Before marking charts as complete:

- [ ] All 8 tabs have charts
- [ ] No console errors
- [ ] All scales appropriate (K/L/Cr/M/%/count)
- [ ] Colors consistent and meaningful
- [ ] Tooltips formatted correctly
- [ ] Responsive on mobile/tablet/desktop
- [ ] Data matches expected values
- [ ] Build completes successfully
- [ ] No performance issues
- [ ] Documentation complete
- [ ] Screenshots captured (if required)

---

## Rollback Plan

If charts cause issues:

1. **Revert CustomerProfile.js:**
   ```powershell
   git checkout HEAD~1 -- data_lake/frontend/src/components/CustomerProfile.js
   ```

2. **Rebuild:**
   ```powershell
   cd data_lake/frontend
   npm run build
   ```

3. **Restart Backend:**
   ```powershell
   # Stop current process (Ctrl+C)
   python app.py
   ```

---

## Support & Troubleshooting

### Check Logs
```powershell
# Backend logs
tail -f data_lake/logs/app.log

# Browser console
F12 → Console tab
```

### Debug Mode
```javascript
// Add to CustomerProfile.js temporarily
console.log('Profile Data:', profileData);
console.log('Chart Data:', chartData);
```

### Force Refresh
```
1. Clear browser cache: Ctrl+Shift+Delete
2. Hard reload: Ctrl+Shift+R
3. Rebuild frontend: npm run build
```

---

*Last Updated: December 2024*
*Test Status: Ready for QA*
