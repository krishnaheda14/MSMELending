# Profile-Aware Data Generation - Complete Implementation Summary

**Date**: December 14, 2025  
**Purpose**: Fix inconsistencies between customer profiles and their GST/mutual fund/insurance/OCEN/ONDC data

---

## Problem Statement

The original raw data files (GST, mutual funds, insurance, OCEN, ONDC) were not aligned with customer profiles assigned via `apply_profile.py`. This caused:

1. **Inconsistent Analytics**: Customer labeled "High Growth" had flat GST turnover; "Declining" had growing revenue
2. **Zero Counts**: Many customers showed 0 mutual funds, insurance, OCEN, ONDC despite being realistic MSMEs
3. **No Fraud Detection**: Missing fraud indicators to demonstrate our analytics capabilities
4. **Profile Mismatch**: Raw transactions were modified by profiles, but GST/other datasets were generic

---

## Solution Implemented

### 1. Created Profile-Aware Data Generator (`generate_profile_aware_data.py`)

A comprehensive script that generates GST, mutual funds, insurance, OCEN, and ONDC data matching each customer's assigned profile.

#### Customer Profile Assignments:
```
CUST_MSM_00001: baseline (no modification)
CUST_MSM_00002: high_seasonality
CUST_MSM_00003: high_debt
CUST_MSM_00004: high_growth
CUST_MSM_00005: stable_income
CUST_MSM_00006: fraud (⭐ NEW - fraud detection showcase)
CUST_MSM_00007: declining
CUST_MSM_00008: customer_concentration
CUST_MSM_00009: high_growth
CUST_MSM_00010: high_seasonality
```

### 2. Profile-Specific Data Generation Logic

#### A. GST Returns (`ProfileAwareGSTGenerator`)
- **High Growth**: Turnover increases from 30% → 300% over 36 months
  - Example: CUST_MSM_00004 - ₹94,993 (Dec 2022) → ₹759,946 (Nov 2025)
  
- **Declining**: Turnover decreases from 150% → 20% over 36 months
  - Example: CUST_MSM_00007 - ₹1,061,939 (Dec 2022) → ₹173,509 (Nov 2025)
  
- **High Seasonality**: Strong seasonal peaks (3-5× multiplier) during festival months (Oct-Dec)
  - Example: CUST_MSM_00002, CUST_MSM_00010
  
- **Stable Income**: Consistent turnover (±5% variation)
  - Example: CUST_MSM_00005
  
- **Fraud** (⭐ NEW): 
  - Inflated turnover (1.5-2.5× actual)
  - High ITC ratio (>95% of output tax)
  - Late filings (30+ days)
  - Turnover mismatch with bank statements
  - Example: CUST_MSM_00006 - 53 fraud indicators detected across 31 GST returns

#### B. Mutual Funds (`ProfileAwareMutualFundGenerator`)
- **High Growth/Stable Income**: 3-6 portfolios, strong returns (15-45%)
- **Declining**: 1-3 portfolios, negative returns (-10% to +5%)
- **Fraud**: 4-7 portfolios but with losses (-20% to -5%) showing poor investment decisions

#### C. Insurance (`ProfileAwareInsuranceGenerator`)
- **High Growth**: ₹1M - ₹5M coverage, 3-5 policies
- **Declining**: ₹200K - ₹800K coverage, 1-2 policies
- **Fraud**: Over-insured (₹3M - ₹10M), some lapsed policies (non-payment)

#### D. OCEN Loan Applications (`ProfileAwareOCENGenerator`)
- **High Debt**: 5-10 applications, 40% approval rate
- **Declining**: 3-6 applications, 30% approval rate (seeking credit)
- **Fraud**: 4-8 applications, 20% approval rate (many rejections)
- **High Growth**: 2-5 applications, 80% approval rate

#### E. ONDC Orders (`ProfileAwareONDCGenerator`)
- **High Growth**: 20-40 orders
- **Declining**: 5-15 orders
- **Fraud**: 15-30 orders
- **Others**: 10-25 orders

### 3. Fraud Detection Implementation

#### Added fraud_indicators to GST records:
```json
"fraud_indicators": {
  "itc_ratio_high": true,  // ITC > 95% of output tax
  "late_filing": true,      // Filed >30 days late
  "turnover_mismatch": true // Mismatch with bank statements
}
```

#### Updated `analytics/generate_summaries.py` to detect fraud:
- Scans GST records for `fraud_indicators` field
- Aggregates fraud indicators across all returns
- Generates fraud severity (HIGH if >5 indicators, else MEDIUM)
- Outputs fraud summary in GST summary and anomalies report

#### Fraud Detection Results for CUST_MSM_00006:
```json
{
  "fraud_detected": true,
  "fraud_severity": "HIGH",
  "fraud_indicators": [
    "High ITC ratio in 2022-12",
    "Turnover mismatch in 2022-12",
    "High ITC ratio in 2023-01",
    // ... 50 more indicators
  ],
  "fraud_summary": {
    "total_indicators": 53,
    "affected_periods": 31,
    "description": "Detected 53 fraud indicators across 31 GST returns"
  }
}
```

---

## Results After Implementation

### Data Generation Output:
```
Total GST returns: 360 (36 per customer)
Total mutual fund portfolios: 37
Total insurance policies: 32
Total OCEN applications: 36
Total ONDC orders: 186
```

### Per-Customer Analytics (Sample):

#### CUST_MSM_00001 (Baseline):
- Transactions: 17,409
- GST Returns: 36
- Mutual Funds: 2
- Insurance: 2
- OCEN Apps: 2
- ONDC Orders: 13
- Anomalies: 1

#### CUST_MSM_00004 (High Growth):
- Transactions: 643
- GST Returns: 36 (showing 8× growth)
- Mutual Funds: 6
- Insurance: 4
- OCEN Apps: 2
- ONDC Orders: 31
- Anomalies: 1

#### CUST_MSM_00006 (Fraud):
- Transactions: 632
- GST Returns: 36 (**53 fraud indicators**)
- Mutual Funds: 5
- Insurance: 4
- OCEN Apps: 8
- ONDC Orders: 24
- Anomalies: 2 (including gst_fraud_indicators)

#### CUST_MSM_00007 (Declining):
- Transactions: 584
- GST Returns: 36 (showing 6× decline)
- Mutual Funds: 1
- Insurance: 2
- OCEN Apps: 6 (seeking credit)
- ONDC Orders: 7
- Anomalies: 1

### ✅ All Customers Now Have:
- **Non-zero counts** for all major datasets (no more zeros)
- **Profile-consistent patterns** in GST turnover, mutual funds, insurance, OCEN, ONDC
- **Realistic data volumes** matching their business profile

---

## Technical Changes Made

### Files Created:
1. **`data_lake/generate_profile_aware_data.py`**
   - ProfileAwareGSTGenerator
   - ProfileAwareMutualFundGenerator
   - ProfileAwareInsuranceGenerator
   - ProfileAwareOCENGenerator
   - ProfileAwareONDCGenerator

2. **`data_lake/regenerate_all_analytics.bat`**
   - Batch script to regenerate analytics for all 10 customers

### Files Modified:
1. **`data_lake/analytics/generate_summaries.py`**
   - Added fraud detection in `analyze_gst()` function
   - Updated `create_anomalies_with_transactions()` to include GST fraud
   - Pass `gst_summary` to anomalies report for fraud aggregation

### Raw Data Files Regenerated:
1. `data_lake/raw/raw_gst.ndjson` (360 records with customer_id)
2. `data_lake/raw/raw_mutual_funds.ndjson` (37 portfolios with customer_id)
3. `data_lake/raw/raw_policies.ndjson` (32 policies with customer_id)
4. `data_lake/raw/raw_ocen_applications.ndjson` (36 apps with customer_id)
5. `data_lake/raw/raw_ondc_orders.ndjson` (186 orders with customer_id)

### Analytics Files Regenerated:
All 10 customers × 10 analytics files = 100 analytics JSON files:
- `CUST_MSM_0000X_transaction_summary.json`
- `CUST_MSM_0000X_gst_summary.json`
- `CUST_MSM_0000X_credit_summary.json`
- `CUST_MSM_0000X_mutual_funds_summary.json`
- `CUST_MSM_0000X_insurance_summary.json`
- `CUST_MSM_0000X_ocen_summary.json`
- `CUST_MSM_0000X_ondc_summary.json`
- `CUST_MSM_0000X_earnings_spendings.json`
- `CUST_MSM_0000X_overall_summary.json`
- `CUST_MSM_0000X_anomalies_report.json`

---

## Key Improvements

### 1. **Consistency**
✅ All datasets now reflect the customer's assigned profile  
✅ GST turnover matches transaction patterns (growth/decline/seasonality)  
✅ Mutual funds/insurance levels match business sophistication

### 2. **Realism**
✅ No more customers with zero mutual funds, insurance, OCEN, or ONDC  
✅ Data volumes realistic for MSME businesses  
✅ Profile-appropriate investment and loan-seeking behavior

### 3. **Fraud Detection** (⭐ NEW)
✅ CUST_MSM_00006 demonstrates fraud caught by our analytics  
✅ GST fraud indicators: high ITC ratio, late filings, turnover mismatch  
✅ Fraud severity classification (HIGH/MEDIUM)  
✅ Anomalies report flags fraud for investigation

### 4. **Maintainability**
✅ Single script (`generate_profile_aware_data.py`) to regenerate all data  
✅ Batch script (`regenerate_all_analytics.bat`) for quick analytics refresh  
✅ Clear profile → data mapping in code comments

---

## How to Use

### Regenerate All Raw Data:
```bash
cd data_lake
python generate_profile_aware_data.py
```

### Regenerate All Analytics:
```bash
cd data_lake
.\regenerate_all_analytics.bat
```

### Generate Analytics for Single Customer:
```bash
cd data_lake
python analytics\generate_summaries.py --customer-id CUST_MSM_00001
```

---

## Verification Examples

### High Growth (CUST_MSM_00004):
```
GST Turnover Growth:
Dec 2022: ₹94,993
Nov 2025: ₹759,946
Growth Factor: 8×
```

### Declining (CUST_MSM_00007):
```
GST Turnover Decline:
Dec 2022: ₹1,061,939
Nov 2025: ₹173,509
Decline Factor: 6×
```

### Fraud (CUST_MSM_00006):
```
Fraud Indicators: 53
Affected Periods: 31/36 GST returns
Severity: HIGH
Key Issues:
- ITC ratio >95% in multiple periods
- 10 late filings
- 15 turnover mismatches with bank statements
```

---

## Next Steps (Future Enhancements)

1. **Frontend Integration**: Update UI to display fraud alerts for CUST_MSM_00006
2. **More Fraud Patterns**: Add invoice cycling, round-tripping detection
3. **Profile Evolution**: Allow customers to transition between profiles over time
4. **Real-time Alerts**: Trigger notifications when fraud indicators exceed threshold
5. **Benchmark Comparisons**: Show how each customer compares to industry benchmarks

---

## Summary

✅ **All customers (00001-00010) now have consistent, profile-aware data**  
✅ **No more zero counts for mutual funds, insurance, OCEN, ONDC**  
✅ **Fraud detection implemented and working (CUST_MSM_00006)**  
✅ **GST turnover patterns match assigned profiles (growth/decline/seasonality)**  
✅ **Easy regeneration via single script**  
✅ **Maintainable, well-documented codebase**

The system now accurately reflects each customer's financial profile across all data sources, making analytics reliable and demonstrating the power of comprehensive data analysis for MSME lending decisions.
