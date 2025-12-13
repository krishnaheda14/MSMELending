# Demo Customer Profiles

## Overview

The platform includes **10 pre-configured customer profiles** (CUST_MSM_00001 through CUST_MSM_00010), each with specialized characteristics to demonstrate different credit scenarios.

### Profile Characteristics

| Customer ID | Profile Type | Key Characteristics | Expected Behavior |
|------------|-------------|---------------------|-------------------|
| **CUST_MSM_00001** | Baseline | Random seed baseline | General validation |
| **CUST_MSM_00002** | High Seasonality | Extreme monthly variations | 3-5x peak/trough cycles |
| **CUST_MSM_00003** | High Debt | Heavy loan burden | DSR > 40%, many EMI transactions |
| **CUST_MSM_00004** | High Growth | Strong revenue growth | 50-100% YoY credit growth |
| **CUST_MSM_00005** | Stable Income | Very consistent cashflow | CV < 15%, low seasonality |
| **CUST_MSM_00006** | High Bounce Rate | Payment failures | 5-8% transaction failure rate |
| **CUST_MSM_00007** | Declining Business | Revenue declining | Negative growth trend |
| **CUST_MSM_00008** | Customer Concentration | 70% revenue from top 3 | High dependency risk |
| **CUST_MSM_00009** | High Growth #2 | Another growth example | Similar to 00004 |
| **CUST_MSM_00010** | High Seasonality #2 | Another seasonal example | Similar to 00002 |

---

## Detailed Profile Descriptions

### CUST_MSM_00001 - Baseline Profile
**Use Case:** Standard validation and testing

**Characteristics:**
- Random seed generation (original)
- Natural variation in all metrics
- No specific modifications applied

**Demo Points:**
- Show complete pipeline flow
- Explain data aggregation from 7 sources
- Demonstrate normal business operations

---

### CUST_MSM_00002 - High Seasonality
**Use Case:** Seasonal business patterns (e.g., festival sales, tourism)

**Characteristics:**
- Extreme monthly income variation (3-5x amplitude)
- Peak months followed by lean months in 3-month cycles
- Seasonality Index > 100%

**Demo Points:**
- Show seasonality detection
- Explain seasonal business risk
- Demonstrate cashflow planning needs
- Show monthly breakdown chart with peaks/troughs

**Expected Metrics:**
- ⚠️ High Seasonality Index (>100%)
- ⚠️ High Income Stability CV (>50%)
- ✓ Variable monthly surplus

---

### CUST_MSM_00003 - High Debt Business
**Use Case:** Heavy loan burden, working capital loans

**Characteristics:**
- 10% additional debt transactions
- Large EMI amounts (₹15,000-₹50,000)
- Multiple loan types (term, working capital)
- DSR typically >40%

**Demo Points:**
- Show debt servicing ratio calculation
- Explain debt sustainability
- Show EMI consistency tracking
- Demonstrate cashflow squeeze from debt

**Expected Metrics:**
- ⚠️ High Debt Servicing Ratio (>40%)
- ⚠️ Lower net surplus
- ⚠️ Reduced working capital

---

### CUST_MSM_00004 - High Growth Business
**Use Case:** Rapidly growing startup or expansion phase

**Characteristics:**
- Credits increase 1x to 3x over analysis period
- Strong upward revenue trend
- Expanding transaction volumes

**Demo Points:**
- Show credit growth rate calculation
- Demonstrate growth trajectory analysis
- Explain scalability indicators
- Show trend visualization

**Expected Metrics:**
- ✓ High Credit Growth Rate (50-100%+)
- ✓ Increasing monthly surplus trend
- ✓ Strong inflow/outflow ratio

---

### CUST_MSM_00005 - Stable Income Business
**Use Case:** Mature business with predictable cashflow

**Characteristics:**
- Monthly income varies by <10%
- Consistent transaction patterns
- Low seasonality (<20%)
- Coefficient of Variation <15%

**Demo Points:**
- Show income stability metrics
- Explain low-risk profile
- Demonstrate predictability
- Show consistent EMI payment capability

**Expected Metrics:**
- ✓ Low Income Stability CV (<15%)
- ✓ Low Seasonality Index (<20%)
- ✓ Consistent monthly surplus
- ✓ Excellent for credit approval

---

### CUST_MSM_00006 - High Bounce Rate
**Use Case:** Cashflow management issues, payment failures

**Characteristics:**
- 5-8% of debit transactions marked as FAILED
- Insufficient funds issues
- Payment declines and bounces

**Demo Points:**
- Show bounce detection algorithm
- Explain credit behavior impact
- Demonstrate payment discipline scoring
- Show failed transaction list

**Expected Metrics:**
- ⚠️ High Bounce Count (>10 transactions)
- ⚠️ Payment discipline issues
- ⚠️ Credit score penalty
- ⚠️ Likely rejection

---

### CUST_MSM_00007 - Declining Business
**Use Case:** Business in decline, market challenges

**Characteristics:**
- Revenue declining from 1.5x to 0.2x over period
- Negative growth rate
- Shrinking transaction volumes

**Demo Points:**
- Show declining trend detection
- Explain business viability concerns
- Demonstrate red flags
- Show negative growth calculations

**Expected Metrics:**
- ⚠️ Negative Credit Growth Rate (-30% to -80%)
- ⚠️ Declining monthly surplus
- ⚠️ Deteriorating metrics over time
- ⚠️ High rejection risk

---

### CUST_MSM_00008 - Customer Concentration Risk
**Use Case:** Over-dependence on few customers

**Characteristics:**
- 70% of revenue from top 3 customers
- High concentration risk
- Top Customer Dependence >60%

**Demo Points:**
- Show customer concentration calculation
- Explain diversification risk
- Demonstrate top customer analysis
- Show dependency metrics

**Expected Metrics:**
- ⚠️ High Top Customer Dependence (>60%)
- ⚠️ Concentration risk flag
- ⚠️ Vulnerability to customer loss
- ⚠️ May need collateral/guarantees

---

## Demo Flow Recommendations

### For High-Quality Credit Demo (Approve)
**Use:** CUST_MSM_00005 (Stable Income)
- Shows excellent payment discipline
- Low risk metrics across the board
- Strong approval case

### For Risky Credit Demo (Reject)
**Use:** CUST_MSM_00006 (High Bounce) or CUST_MSM_00007 (Declining)
- Clear red flags
- Multiple concerning metrics
- Justifiable rejection

### For Edge Case Demo (Manual Review)
**Use:** CUST_MSM_00002 (High Seasonality) or CUST_MSM_00003 (High Debt)
- Mixed indicators
- Needs human judgment
- Conditional approval scenarios

### For Growth Story Demo
**Use:** CUST_MSM_00004 or CUST_MSM_00009 (High Growth)
- Positive momentum
- Investment opportunity
- Higher risk tolerance justified

---

## Technical Notes

### Data Generation Process
1. **Base Generation**: Random seed creates foundation
2. **Profile Modification**: Specific fields modified to inject characteristics
3. **Analytics Regeneration**: Calculations run on modified data

### Consistency
- Each profile regeneration maintains its core characteristics
- Exact values will vary slightly due to random elements
- Key behavioral patterns remain consistent

### Verification
After generation, verify each profile in the "Earnings vs Spendings" tab:
- Check key metrics match expected ranges
- Verify info buttons show correct calculations
- Confirm explanations are metric-specific

---

## Quick Reference Commands

### Generate All Specialized Profiles
```bash
python generate_specialized_customers.py
```

### Regenerate Single Customer
```bash
# First generate base data
python generate_all.py --customer-id CUST_MSM_00002

# Then apply profile modifications
python generate_specialized_customers.py --customer-id CUST_MSM_00002

# Finally regenerate analytics
python analytics/generate_summaries.py --customer-id CUST_MSM_00002
```

---

## Usage in UI

1. **Select Customer**: Click on customer card (Random Seed #X will show profile type after generation)
2. **Apply**: Click "Apply Customer ID" button
3. **Run Pipeline**: Execute all 5 steps (Consent → Clean → Analytics → Score → Decision)
4. **View Results**: 
   - Analytics & Insights tab: Composite scores
   - Earnings vs Spendings tab: Detailed metrics with info buttons
5. **Explore Calculations**: Click ℹ️ buttons to see formulas and breakdowns

---

**All data is pre-generated and ready - just select and apply!**
