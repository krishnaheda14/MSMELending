# Data Generation Issues and Fixes

## Issues Identified

### 1. Working Capital Gap Calculation ✅ CORRECT

**How it's calculated:**
```
Working Capital Gap (days) = (Average Monthly Surplus) / (Daily Expenses)
Where:
  - Average Monthly Surplus = Average of (Monthly Credits - Monthly Debits)
  - Daily Expenses = Average Monthly Debits / 30
```

**Example for CUST_MSM_00007:**
- Total Inflow: ₹1,087,620,320.54
- Total Outflow: ₹295,364,459.53
- Over ~48 months (4 years): Avg Monthly Surplus = (1087M - 295M) / 48 = ₹16.5M/month
- Avg Monthly Debits = 295M / 48 = ₹6.15M/month
- Daily Expenses = 6.15M / 30 = ₹205k/day
- **Working Capital Gap = 16.5M / 205k = 80.5 days** ✅

This is **CORRECT** - it shows how many days the business can sustain with current surplus.

---

### 2. **CRITICAL BUG: Profile Application Overwrites All Customers' Data** 🔴

**The Problem:**
```python
# In generate_specialized_customers.py and apply_profile.py:
def apply_customer_profile(customer_id, profile_type):
    # Loads raw/raw_transactions.ndjson (SHARED FILE!)
    txn_file = f'raw/raw_transactions.ndjson'
    transactions = []
    with open(txn_file, 'r') as f:
        for line in f:
            transactions.append(json.loads(line))
    
    # Modifies ALL transactions
    if profile_type == 'declining':
        transactions = modify_transactions_for_declining_business(transactions)
    
    # Saves back to SAME shared file
    with open(txn_file, 'w') as f:
        for txn in transactions:
            f.write(json.dumps(txn) + '\n')
```

**What happens:**
1. `generate_all_specialized.bat` runs for CUST_MSM_00002 (high seasonality)
2. Generates base data → writes to `raw/raw_transactions.ndjson`
3. Applies high_seasonality modifier → **overwrites entire file**
4. Then runs for CUST_MSM_00007 (declining)
5. Generates NEW base data → overwrites again
6. Applies declining modifier → **ALL 50,000 transactions become declining**
7. **Result: CUST_MSM_00007 gets declining data, but CUST_MSM_00002 also gets declining data!**

This is why CUST_MSM_00007 (declining) shows **positive growth** - it's using the LAST profile applied (or base data from another customer).

---

### 3. Unrealistic Bulk Scale Settings 🔴

**Current config.json:**
```json
{
  "scale": {
    "transactions": 50000,      // ❌ Generated for ALL customers combined
    "gst_profiles": 500,         // ❌ 500 GST returns for one customer?
    "insurance_policies": 1000,  // ❌ 1000 policies for one customer?
    "ondc_orders": 2000,         // ❌ Only 2000 orders vs 50k transactions?
    "ocen_applications": 300     // ❌ 300 loan applications?
  }
}
```

**Issues:**
- **50,000 transactions** for a SINGLE customer over 4 years = 1,042 txns/month = **34 txns/day** (unrealistic for MSME)
- **1,000 insurance policies** for one customer is absurd
- **500 GST returns** = ~10 returns/month = multiple GST registrations? (Normal: 1-2 returns/month)
- **GST turnover ₹40.5 BILLION** vs **Bank credits ₹1 BILLION** = massive mismatch

**Root cause:** These were bulk generation settings for an entire database, not per-customer.

---

### 4. GST vs Bank Reconciliation Mismatch 🔴

**Example (CUST_MSM_00001):**
- GST Turnover: ₹40,515,976,984.87 (₹40.5 Billion)
- Bank Credits: ₹1,087,620,320.54 (₹1 Billion)
- Variance: ₹39.4 Billion (3,728% of bank!)

**Why this happens:**
1. GST generator creates 500 returns with large turnovers
2. Transaction generator creates 50k transactions but with smaller amounts
3. GST monthly aggregation sums ALL returns (should only count once per month)
4. No correlation between GST profiles and actual transactions

**For realistic reconciliation:**
- GST Turnover should be ≈ Bank Credits (±10-20% for timing/unrecorded cash)
- Currently off by **40x**

---

## Recommended Fixes

### Fix 1: Per-Customer Data Generation (CRITICAL)

**Option A: Generate separate raw files per customer**
```python
def apply_customer_profile(customer_id, profile_type):
    # Use customer-specific file
    txn_file = f'raw/{customer_id}_transactions.ndjson'
    gst_file = f'raw/{customer_id}_gst.ndjson'
    # ... etc
```

**Option B: Filter by customer_id field**
```python
# In generator, add customer_id to each record:
{
  "transaction_id": "TXN_001",
  "customer_id": "CUST_MSM_00007",  # Add this!
  "amount": 5000,
  ...
}

# Then filter when applying profiles:
transactions = [t for t in all_transactions if t['customer_id'] == customer_id]
```

**Option B is RECOMMENDED** - maintains single source file but isolates by customer.

---

### Fix 2: Realistic Per-Customer Scales

**Suggested config.json updates:**
```json
{
  "scale_per_customer": {
    "transactions_per_year": 500,     // ~42/month, ~1.4/day ✅
    "gst_returns_per_year": 12,       // 1/month (monthly filing) ✅
    "insurance_policies": 15,          // 10-20 policies ✅
    "mutual_fund_portfolios": 3,       // 2-5 funds ✅
    "ondc_orders_per_year": 200,      // ~17/month ✅
    "ocen_applications_total": 5       // 3-8 loan applications ✅
  },
  "gst_turnover_per_customer": {
    "min": 5000000,      // ₹50 Lakh/year
    "max": 50000000      // ₹5 Crore/year
  }
}
```

**For 10 customers over 4 years:**
- Total transactions: 10 × 500 × 4 = **20,000** ✅
- Total GST returns: 10 × 12 × 4 = **480** ✅
- Total insurance: 10 × 15 = **150** ✅
- Total ONDC: 10 × 200 × 4 = **8,000** ✅

---

### Fix 3: Reconcile GST with Bank Transactions

**Method 1: Generate GST from transactions**
```python
# Sum all CREDIT transactions per month → use as GST turnover
monthly_credits = group_by_month(transactions)
gst_returns = []
for month, total in monthly_credits.items():
    gst_returns.append({
        "filing_period": month,
        "total_turnover": total * 1.1  # +10% for cash/unrecorded
    })
```

**Method 2: Generate transactions from GST**
```python
# After generating GST returns, create matching transactions
for gst_return in gst_returns:
    turnover = gst_return['total_turnover']
    # Create ~40 transactions that sum to turnover
    for _ in range(40):
        amount = turnover / 40 * random.uniform(0.5, 1.5)
        create_transaction(amount=amount, month=gst_return['filing_period'])
```

**Method 1 is RECOMMENDED** - ensures 1:1 correlation.

---

### Fix 4: Profile-Specific Modifiers (Post-Fix 1)

**After fixing isolation, update modifiers:**

```python
# For declining business:
def modify_transactions_for_declining_business(transactions):
    """Create NEGATIVE growth: start high, end low"""
    sorted_txns = sorted(transactions, key=lambda x: x.get('date', ''))
    
    for i, txn in enumerate(sorted_txns):
        if txn.get('type', '').upper() in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
            # Start at 2.0x, decline to 0.3x
            progress = i / len(sorted_txns)
            decline_factor = 2.0 - (progress * 1.7)  # 2.0 → 0.3
            txn['amount'] = float(txn['amount']) * decline_factor
    
    return sorted_txns

# For high growth:
def modify_transactions_for_high_growth(transactions):
    """Create POSITIVE growth: start low, end high"""
    sorted_txns = sorted(transactions, key=lambda x: x.get('date', ''))
    
    for i, txn in enumerate(sorted_txns):
        if txn.get('type', '').upper() in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
            # Start at 0.5x, grow to 3.0x
            progress = i / len(sorted_txns)
            growth_factor = 0.5 + (progress * 2.5)  # 0.5 → 3.0
            txn['amount'] = float(txn['amount']) * growth_factor
    
    return sorted_txns
```

---

## Profile Characteristics (After Fixes)

### CUST_MSM_00002 - High Seasonality
**Modifier:** Amplify monthly variation (3x peak, 0.3x trough, cycling every 3 months)
**Expected metrics:**
- Seasonality Index: >100%
- Income Stability CV: >50%

### CUST_MSM_00003 - High Debt
**Modifier:** Add 10% more DEBIT transactions, mark as loan repayments
**Expected metrics:**
- Debt Servicing Ratio: >40%
- Many EMI/loan transactions

### CUST_MSM_00004 - High Growth
**Modifier:** Credits grow from 0.5x → 3.0x over time
**Expected metrics:**
- TTM Revenue Growth: >50%
- QoQ Revenue Growth: >30%
- Credit Growth Rate: >20%

### CUST_MSM_00005 - Stable Income
**Modifier:** Normalize all credits to ±5% of mean
**Expected metrics:**
- Income Stability CV: <15%
- Seasonality Index: <20%

### CUST_MSM_00006 - High Bounce
**Modifier:** Mark 7% of DEBITs as FAILED/BOUNCED
**Expected metrics:**
- Bounce Count: >20
- EMI Consistency: <50%

### CUST_MSM_00007 - Declining
**Modifier:** Credits decline from 2.0x → 0.3x over time
**Expected metrics:**
- TTM Revenue Growth: **NEGATIVE** (<-10%)
- QoQ Revenue Growth: **NEGATIVE**
- Credit Growth Rate: **NEGATIVE**
- Surplus Trend: "decreasing"

### CUST_MSM_00008 - Customer Concentration
**Modifier:** Assign 70% of credits to 3 customers, increase amounts
**Expected metrics:**
- Top Customer Dependence: >60%

---

## Implementation Steps

### Step 1: Add customer_id to all generators
```bash
# Update generators/generate_transactions.py
# Update generators/generate_gst.py
# Update generators/generate_insurance.py
# etc.
```

### Step 2: Update config.json with per-customer scales
```bash
# Edit config.json
```

### Step 3: Fix apply_profile.py to filter by customer_id
```bash
# Edit apply_profile.py
```

### Step 4: Regenerate ALL customers
```bash
cd data_lake
python cleanup_old_data.py
python generate_all_specialized.bat
```

### Step 5: Verify profiles
```bash
# Check CUST_MSM_00007 has NEGATIVE growth
# Check CUST_MSM_00004 has POSITIVE growth
# Check GST ≈ Bank Credits (within 20%)
```

---

## Quick Verification Commands

```powershell
# Check all customers' growth rates:
Get-ChildItem f:\MSMELending\data_lake\analytics\*_earnings_spendings.json | ForEach-Object {
    $json = Get-Content $_.FullName | ConvertFrom-Json
    $cust = $_.Name -replace '_earnings_spendings.json',''
    Write-Host "$cust : TTM=$($json.business_health.ttm_revenue_growth)% QoQ=$($json.business_health.qoq_revenue_growth)%"
}

# Check GST vs Bank reconciliation:
Get-ChildItem f:\MSMELending\data_lake\analytics\*_earnings_spendings.json | ForEach-Object {
    $json = Get-Content $_.FullName | ConvertFrom-Json
    $cust = $_.Name -replace '_earnings_spendings.json',''
    $gst = [math]::Round($json.cashflow_metrics.gst_turnover / 10000000, 1)
    $bank = [math]::Round($json.cashflow_metrics.bank_turnover / 10000000, 1)
    Write-Host "$cust : GST=₹${gst}Cr Bank=₹${bank}Cr Ratio=$([math]::Round($gst/$bank, 1))x"
}
```

---

## Summary

**Root Causes:**
1. ✅ Working capital calculation is **correct**
2. 🔴 Profile modifiers **overwrite shared files** → all customers get same data
3. 🔴 Bulk generation scales **unrealistic for single customer**
4. 🔴 GST and bank transactions **not correlated**

**Priority Fixes:**
1. **CRITICAL:** Add customer_id filtering (Fix 1 Option B)
2. **HIGH:** Update per-customer scales (Fix 2)
3. **HIGH:** Correlate GST with transactions (Fix 3 Method 1)
4. **MEDIUM:** Verify profile modifiers produce expected trends (Fix 4)

**Expected Outcome:**
- CUST_MSM_00007: **Negative growth** (-20% to -50%)
- CUST_MSM_00004: **High growth** (+50% to +100%)
- All customers: GST ≈ Bank (within ±20%)
- Realistic counts: ~2000 txns, ~50 GST returns, ~15 policies per customer
