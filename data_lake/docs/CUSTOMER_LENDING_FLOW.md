# MSME Lending Solution - Customer Journey Flow

## Overview: One Borrower → One Consent → One Dataset → One Analytics Package

This document explains the **complete end-to-end flow** for evaluating a single MSME borrower for a loan, following **RBI Account Aggregator (AA) Framework** and **Digital Personal Data Protection Act (DPDP) 2023** guidelines.

---

## 🎯 Solution Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MSME LENDING DECISION ENGINE                         │
│                                                                         │
│  INPUT: One Customer → OUTPUT: Creditworthiness Score + Recommendation │
└─────────────────────────────────────────────────────────────────────────┘

STEP 1: CONSENT           →  STEP 2: DATA FETCH      →  STEP 3: CLEAN & VALIDATE
Customer grants AA             Pull multi-source         Standardize & validate
consent via digital            financial data via        raw data, detect errors
consent artefact               secure AA rails           and anomalies

STEP 4: ANALYTICS         →  STEP 5: RISK SCORING    →  STEP 6: DECISION
Generate cashflow,             Custom ML risk models     Loan approval/rejection
income, expense insights       (not bureau score)        with recommended terms
```

---

## 📋 Step-by-Step Flow

### **STEP 1: Customer Consent Collection**

**What Happens:**
- Borrower (MSME owner) visits lender's platform
- Lender requests financial data consent via Account Aggregator (AA)
- Customer digitally signs consent artefact specifying:
  - Which data sources (bank accounts, GST, mutual funds, insurance, etc.)
  - Time period (e.g., last 12 months)
  - Validity duration (e.g., 6 months)
  - Access mode (VIEW/STORE/QUERY)

**Data Collected:**
```json
{
  "consent_id": "A1B2C3D4-1234-5678-9ABC-123456789012",
  "user_id": "CUST_MSM_00001",
  "fiu_id": "LENDER_BANK_XYZ",
  "aa_id": "FINVU",
  "consent_types": [
    "DEPOSIT",           // Savings/Current accounts
    "TERM_DEPOSIT",      // Fixed deposits
    "MUTUAL_FUNDS",      // Investment history
    "INSURANCE_POLICIES",// Insurance premiums
    "GOVT_SECURITIES"    // Govt bonds, etc.
  ],
  "consent_start": "2025-12-12T10:00:00Z",
  "consent_expiry": "2026-06-12T10:00:00Z",
  "data_from": "2024-01-01",
  "data_to": "2025-12-11",
  "status": "ACTIVE"
}
```

**Regulatory Compliance:**
- ✅ **RBI AA Framework**: Consent must be granular, revocable, time-bound
- ✅ **DPDP Act 2023**: Customer has right to withdraw consent anytime
- ✅ **Data Minimization**: Only request necessary data for lending decision

**System Action:**
```bash
# Consent stored in system
POST /api/consent/create
{
  "customer_id": "CUST_MSM_00001",
  "consent_artefact": {...}
}
```

---

### **STEP 2: Multi-Source Data Fetch via AA**

**What Happens:**
- Once consent is ACTIVE, lender initiates data fetch via AA
- AA securely pulls encrypted data from multiple Financial Information Providers (FIPs):
  - **Banks** (HDFC, ICICI, SBI, Axis, Kotak, etc.)
  - **GSTN** (GST return data via Sandbox)
  - **Credit Bureaus** (CIBIL, Experian, Equifax, CRIF)
  - **Insurance Providers** (LIC, HDFC Life, etc.)
  - **Mutual Fund RTAs** (CAMS, Karvy)
  - **ONDC Network** (e-commerce order history)
  - **OCEN Network** (previous loan applications)

**Data Sources & Purpose:**

| Data Source | What We Get | Why We Need It |
|------------|------------|---------------|
| **Bank Accounts** | Transactions, balances, account history | Cashflow analysis, income detection, expense patterns |
| **GST Returns** | GSTR-1, GSTR-3B filings | Business turnover, tax compliance, B2B revenue |
| **Credit Bureau** | Credit score, existing loans, repayment history | Credit risk, existing obligations |
| **Insurance** | Premiums paid, policy values | Financial discipline, asset ownership |
| **Mutual Funds** | SIP investments, redemptions | Savings behavior, liquidity |
| **ONDC Orders** | E-commerce purchase/sales history | Business activity (for online sellers) |
| **OCEN Applications** | Previous loan applications | Loan stacking detection, credit hunger |

**Raw Data Structure (Per Customer):**
```
raw/
├── raw_consent.ndjson              # 1 record (consent artefact)
├── raw_accounts.ndjson             # 2-5 records (bank accounts)
├── raw_transactions.ndjson         # 500-5000 records (6-12 months)
├── raw_gst.ndjson                  # 12-24 records (monthly returns)
├── raw_credit_reports.ndjson       # 1-4 records (bureau reports)
├── raw_policies.ndjson             # 0-3 records (insurance policies)
├── raw_mutual_funds.ndjson         # 0-10 records (MF holdings)
├── raw_ondc_orders.ndjson          # 0-100 records (e-commerce)
└── raw_ocen_applications.ndjson    # 0-5 records (loan history)
```

**System Action:**
```bash
# Generate customer-specific dataset
POST /api/pipeline/generate
{
  "customer_id": "CUST_MSM_00001"
}

# Backend runs:
python generate_all.py --customer-id CUST_MSM_00001
```

**Security Notes:**
- 🔒 Data is encrypted in transit (TLS 1.3)
- 🔒 Customer PII is masked (account numbers → XXXXXX1234)
- 🔒 Data stored temporarily only for analysis (auto-delete after 90 days)

---

### **STEP 3: Data Cleaning & Validation**

**What Happens:**
- Raw data from multiple FIPs has inconsistencies:
  - Different date formats (`DD/MM/YYYY`, `YYYY-MM-DD`, `DD-MMM-YY`)
  - Numeric formats (`1,25,000.00`, `125000`, `1.25L`)
  - Missing fields, duplicate records, encoding errors
- Cleaning pipeline standardizes everything

**Cleaning Operations:**

1. **Date Standardization**: All dates → `YYYY-MM-DD` format
2. **Numeric Normalization**: All amounts → `float` without commas
3. **Deduplication**: Remove duplicate transactions/records
4. **Schema Validation**: Check against JSON schemas
5. **Missing Field Handling**: Flag critical missing data
6. **Categorization**: Auto-categorize transactions (SALARY, EMI, FOOD, etc.)
7. **PII Masking**: Mask account numbers, PAN (keep last 4 digits)

**Before vs After (Example Transaction):**
```json
// RAW (messy)
{
  "date": "04/11/2025",
  "amount": "1,250.00 Dr",
  "narration": "UPI/Amazon/amazonpay@ybl/1234567890",
  "balance": "₹ 45,320.50"
}

// CLEAN (standardized)
{
  "transaction_id": "TXN000001",
  "account_id": "ACC00001",
  "date": "2025-11-04",
  "type": "DEBIT",
  "amount": 1250.00,
  "mode": "UPI",
  "merchant_name": "Amazon",
  "category": "SHOPPING",
  "balance_after": 45320.50,
  "upi_id": "amazonpay@ybl"
}
```

**Validation Logs:**
```
logs/
├── account_validation_errors.json     # Missing IFSC codes, invalid banks
├── transaction_validation_errors.json # Invalid amounts, future dates
├── gst_validation_errors.json         # Invalid GSTIN, missing returns
└── transaction_cleaning_log.json      # Transformation audit trail
```

**System Action:**
```bash
# Clean customer data
POST /api/pipeline/clean
{
  "customer_id": "CUST_MSM_00001"
}

# Backend runs:
python pipeline/clean_data.py
```

**Output:**
```
clean/
├── accounts_clean.ndjson          # Validated accounts
├── transactions_clean.ndjson      # Standardized transactions
├── gst_clean.ndjson              # Validated GST returns
└── ... (other cleaned datasets)
```

---

### **STEP 4: Analytics & Insight Generation**

**What Happens:**
- Cleaned data is analyzed to extract **actionable business intelligence**
- System generates 6 types of analytics outputs

#### **4.1 Transaction Analytics**

**Generated Insights:**
```json
{
  "total_transactions": 1247,
  "amount_statistics": {
    "mean": 8450.32,
    "median": 2100.00,
    "std_dev": 15234.67,
    "min": 10.00,
    "max": 125000.00,
    "total": 10537349.84
  },
  "category_distribution": {
    "SALARY": 12,           // Monthly income credits
    "EMI": 12,              // Loan repayments
    "UTILITIES": 45,        // Electricity, water, etc.
    "FOOD": 89,             // Dining expenses
    "SHOPPING": 156,        // Retail purchases
    "TRANSFER": 234,        // Fund transfers
    "INVESTMENT": 24        // SIP/investment
  },
  "mode_distribution": {
    "UPI": 678,
    "NEFT": 145,
    "IMPS": 89,
    "CHEQUE": 12,
    "CASH": 23
  },
  "top_merchants": {
    "Amazon": 45,
    "Swiggy": 34,
    "Zomato": 28,
    "BigBazaar": 12
  }
}
```

**Key Metrics Derived:**
- ✅ **Average Monthly Income**: Detect salary credits (₹45K/month)
- ✅ **Average Monthly Expenses**: Sum all debits (₹38K/month)
- ✅ **Net Cashflow**: Income - Expenses = ₹7K/month surplus
- ✅ **Expense Stability**: Low std_dev = predictable spending
- ✅ **Payment Behavior**: UPI dominance = digitally active customer

#### **4.2 GST Analytics**

**Generated Insights:**
```json
{
  "total_returns": 24,
  "turnover_statistics": {
    "mean": 1250000.00,      // ₹12.5L average monthly turnover
    "median": 1100000.00,
    "min": 450000.00,
    "max": 2800000.00,
    "total": 30000000.00     // ₹3Cr annual turnover
  },
  "filing_status_distribution": {
    "FILED": 22,             // 22/24 returns filed on time
    "LATE_FILED": 2,         // 2 returns late
    "NOT_FILED": 0           // No missing returns
  },
  "return_type_distribution": {
    "GSTR3B": 12,
    "GSTR1": 12
  }
}
```

**Key Metrics Derived:**
- ✅ **Business Turnover**: ₹3Cr annually (qualifies for MSME loan)
- ✅ **Tax Compliance**: 91.7% on-time filing (good)
- ✅ **Revenue Trend**: Growing 5-10% MoM (healthy business)
- ✅ **GST Fraud Risk**: No missing returns = low risk

#### **4.3 Credit Bureau Analytics**

**Generated Insights:**
```json
{
  "total_reports": 1,
  "credit_score_statistics": {
    "mean": 745,
    "median": 745,
    "min": 745,
    "max": 745
  },
  "score_distribution": {
    "300-550": 0,
    "550-650": 0,
    "650-750": 1,           // Good credit score range
    "750-900": 0
  },
  "average_accounts": 4,    // 4 credit accounts
  "total_debt": 850000,     // ₹8.5L existing loans
  "monthly_obligations": 45000  // ₹45K EMI/month
}
```

**Key Metrics Derived:**
- ✅ **Credit Score**: 745 (Good - eligible for prime lending)
- ✅ **Existing Debt**: ₹8.5L (manageable)
- ✅ **Debt Service Ratio**: EMI/Income = 45K/45K = 100% (HIGH RISK)
- ⚠️ **Red Flag**: Customer already at debt capacity

#### **4.4 Account Analytics**

**Generated Insights:**
```json
{
  "total_accounts": 3,
  "bank_distribution": {
    "HDFC": 1,
    "ICICI": 1,
    "SBI": 1
  },
  "account_type_distribution": {
    "SAVINGS": 2,
    "CURRENT": 1            // Has business current account
  },
  "balance_statistics": {
    "mean": 125000.00,
    "median": 85000.00,
    "total": 375000.00      // ₹3.75L total liquid cash
  }
}
```

**Key Metrics Derived:**
- ✅ **Banking Relationship**: Multi-bank customer (good)
- ✅ **Business Account**: Has current account (business entity)
- ✅ **Liquidity**: ₹3.75L available (3 months buffer)

#### **4.5 Anomaly Detection**

**Generated Insights:**
```json
[
  {
    "transaction_id": "TXN00045623",
    "amount": 250000.00,
    "threshold": 75000.00,
    "deviation": 8.5,        // 8.5 std deviations above mean
    "type": "high_value_transaction",
    "description": "Unusually large debit (₹2.5L) - may indicate loan prepayment or emergency"
  },
  {
    "transaction_id": "TXN00056789",
    "amount": 150000.00,
    "threshold": 75000.00,
    "deviation": 5.2,
    "type": "high_value_transaction",
    "description": "Large credit (₹1.5L) - possible loan disbursement or asset sale"
  }
]
```

**Key Metrics Derived:**
- ⚠️ **Spending Spikes**: 2 anomalies detected (needs manual review)
- ✅ **Fraud Indicator**: No suspicious patterns

#### **4.6 Overall Summary**

**Combined Customer Profile:**
```json
{
  "customer_id": "CUST_MSM_00001",
  "generated_at": "2025-12-12T10:30:00Z",
  "data_period": {
    "from": "2024-01-01",
    "to": "2025-12-11"
  },
  "datasets_analyzed": {
    "transactions": 1247,
    "accounts": 3,
    "gst_returns": 24,
    "credit_reports": 1
  },
  "business_profile": {
    "business_name": "ABC Trading Co.",
    "gstin": "27AABCU9603R1ZX",
    "annual_turnover": 30000000,      // ₹3Cr
    "business_vintage": 5             // 5 years old
  },
  "financial_health": {
    "monthly_income": 45000,
    "monthly_expenses": 38000,
    "net_cashflow": 7000,
    "liquid_assets": 375000,
    "existing_debt": 850000,
    "credit_score": 745
  }
}
```

**System Action:**
```bash
# Generate analytics
POST /api/pipeline/analytics
{
  "customer_id": "CUST_MSM_00001"
}

# Backend runs:
python analytics/generate_summaries.py
```

**Output:**
```
analytics/
├── transaction_summary.json       # Cashflow insights
├── account_summary.json          # Banking behavior
├── gst_summary.json             # Business turnover & compliance
├── credit_summary.json          # Bureau data insights
├── anomalies_report.json        # Red flags
└── overall_summary.json         # Combined profile
```

---

### **STEP 5: Custom Risk Scoring (ML Models)**

**What Happens:**
- Analytics data feeds into **custom machine learning risk models**
- **NOT bureau score** - bank builds proprietary models based on:
  - Cashflow stability
  - Business growth trends
  - Tax compliance
  - Repayment capacity
  - Industry-specific risks

**Example Custom Scores:**

#### **5.1 Cashflow Stability Score (0-100)**
```python
# Formula
cashflow_score = (
    (avg_monthly_surplus / avg_monthly_income) * 30 +  # Surplus ratio
    (1 - (std_dev_expenses / mean_expenses)) * 30 +    # Expense stability
    (on_time_salary_credits / total_months) * 40       # Income regularity
)

# Customer Example
cashflow_score = (
    (7000 / 45000) * 30 +      # 15.5% surplus → 4.67 points
    (1 - (5000 / 38000)) * 30 + # Low variance → 26.3 points
    (12 / 12) * 40             # 100% regular income → 40 points
) = 71/100  # MEDIUM-HIGH stability
```

#### **5.2 Business Health Score (0-100)**
```python
# Formula
business_score = (
    (gst_filing_compliance_rate) * 25 +           # Tax discipline
    (revenue_growth_rate / 0.10) * 25 +          # Growth trajectory
    (turnover / industry_avg_turnover) * 25 +    # Market position
    (payment_to_suppliers_on_time_rate) * 25     # B2B trust
)

# Customer Example
business_score = (
    (22/24) * 25 +              # 91.7% compliance → 22.9 points
    (0.08 / 0.10) * 25 +        # 8% growth vs 10% industry → 20 points
    (3Cr / 2.5Cr) * 25 +        # Above industry avg → 30 points
    (0.85) * 25                 # 85% on-time payments → 21.25 points
) = 94/100  # EXCELLENT business health
```

#### **5.3 Debt Capacity Score (0-100)**
```python
# Formula
debt_capacity = (
    100 - (current_emi / monthly_income * 100) +  # DTI ratio
    (liquid_assets / (monthly_expenses * 3)) * 20 # Liquidity buffer
)

# Customer Example
debt_capacity = (
    100 - (45000 / 45000 * 100) +  # 100% DTI → 0 points (MAXED OUT)
    (375000 / (38000 * 3)) * 20    # 3.3 months buffer → 20 points
) = 20/100  # LOW capacity (already overleveraged)
```

#### **5.4 Overall Credit Risk Score**
```python
# Weighted composite
credit_risk_score = (
    cashflow_score * 0.35 +      # 35% weight
    business_score * 0.30 +      # 30% weight
    debt_capacity * 0.25 +       # 25% weight
    (credit_score / 900) * 100 * 0.10  # 10% weight (bureau score)
)

# Customer Example
credit_risk_score = (
    71 * 0.35 +       # 24.85
    94 * 0.30 +       # 28.2
    20 * 0.25 +       # 5.0
    (745/900)*100*0.10  # 8.28
) = 66.33/100  # BORDERLINE (manual review recommended)
```

**Risk Band Classification:**
- **0-30**: High Risk → Reject
- **31-60**: Medium Risk → Higher interest rate (14-18%)
- **61-75**: Borderline → Manual underwriter review
- **76-90**: Low Risk → Prime lending (10-12%)
- **91-100**: Very Low Risk → Premium rates (8-10%)

**Customer Verdict:**
```json
{
  "customer_id": "CUST_MSM_00001",
  "credit_risk_score": 66.33,
  "risk_band": "BORDERLINE",
  "recommendation": "MANUAL_REVIEW",
  "reasoning": {
    "strengths": [
      "Excellent business health (GST compliance, turnover growth)",
      "Good credit score (745)",
      "Stable cashflow (₹7K/month surplus)",
      "Multi-bank relationship"
    ],
    "weaknesses": [
      "Existing debt at 100% DTI ratio (CRITICAL)",
      "Low debt capacity (20/100 score)",
      "2 high-value anomalies requiring explanation"
    ],
    "suggested_action": "Approve with conditions",
    "conditions": [
      "Maximum loan amount: ₹5L (not ₹10L requested)",
      "Interest rate: 14% (medium risk pricing)",
      "Mandate insurance coverage",
      "Review business financials quarterly",
      "Require co-applicant or guarantor"
    ]
  }
}
```

---

### **STEP 6: Lending Decision & Loan Terms**

**What Happens:**
- Risk score + analytics feed into **loan decision engine**
- System recommends:
  - **Approve** / **Reject** / **Manual Review**
  - Loan amount (may be lower than requested)
  - Interest rate (risk-based pricing)
  - Tenure
  - Collateral requirements

**Final Output (Sent to Underwriter):**
```json
{
  "loan_application_id": "LOAN_APP_00001",
  "customer_id": "CUST_MSM_00001",
  "requested_amount": 1000000,
  "decision": "CONDITIONAL_APPROVE",
  "approved_amount": 500000,
  "interest_rate": 14.0,
  "tenure_months": 24,
  "emi": 24116,
  "processing_fee": 10000,
  "collateral": "GUARANTOR_REQUIRED",
  "rationale": {
    "credit_risk_score": 66.33,
    "key_factors": [
      "Strong business (₹3Cr turnover, 91% GST compliance)",
      "Existing debt burden at limit (100% DTI)",
      "Reduced loan amount to maintain healthy DTI"
    ]
  },
  "monitoring_requirements": [
    "Quarterly GST return review",
    "Monthly bank statement analysis",
    "Annual credit bureau refresh"
  ]
}
```

---

## 🔒 Data Privacy & Security (DPDP Compliance)

### **1. Per-Customer Data Isolation**
```bash
# ❌ WRONG: Bulk dataset fetch (violates DPDP)
GET /api/data/transactions  # Returns all customers' data

# ✅ CORRECT: Customer-specific fetch
GET /api/data/transactions?customer_id=CUST_MSM_00001&consent_id=ABC123
```

### **2. Consent-Based Access**
- ✅ Every data fetch must validate active consent
- ✅ Data older than consent period is auto-purged
- ✅ Customer can revoke consent anytime (data deleted within 24 hours)

### **3. Data Retention Policy**
```
Consent Lifecycle:
├── Active Consent → Data fetched & analyzed (real-time)
├── Loan Approved → Keep data for 90 days (regulatory requirement)
├── Loan Rejected → Delete data within 30 days
└── Consent Revoked → Immediate deletion (within 24 hours)
```

### **4. Audit Trail**
```json
{
  "access_log_id": "LOG_00001",
  "customer_id": "CUST_MSM_00001",
  "consent_id": "ABC123",
  "accessed_at": "2025-12-12T10:30:00Z",
  "accessed_by": "underwriter@lenderbank.com",
  "data_accessed": ["transactions", "gst", "credit_report"],
  "purpose": "Loan application review",
  "ip_address": "203.192.xxx.xxx"
}
```

---

## 📊 Complete Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         CUSTOMER (MSME Borrower)                         │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
                                │ ① Requests loan on lender platform
                                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        LENDER (FIU - Bank/NBFC)                          │
│  - Initiates consent request via AA                                     │
│  - Specifies data needed: Bank, GST, Bureau, etc.                       │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
                                │ ② Redirects to AA for consent
                                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                   ACCOUNT AGGREGATOR (Finvu/OneMoney)                    │
│  - Shows customer which data will be shared                             │
│  - Customer digitally signs consent                                     │
│  - Generates consent artefact with expiry                               │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
                                │ ③ Returns signed consent to lender
                                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        LENDER BACKEND (This System)                      │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  STEP 1: CONSENT VALIDATION                                │         │
│  │  - Verify consent is active & not expired                  │         │
│  │  - Extract customer_id, FIP list, date range              │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                │                                         │
│                                │ ④ Trigger data fetch                   │
│                                ▼                                         │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  STEP 2: DATA GENERATION (per customer)                    │         │
│  │  python generate_all.py --customer-id CUST_MSM_00001       │         │
│  │                                                             │         │
│  │  Parallel API calls to:                                    │         │
│  │  ├── Bank APIs (via AA) → Accounts + Transactions          │         │
│  │  ├── GSTN Sandbox → GST returns                            │         │
│  │  ├── Credit Bureau → CIBIL/Experian report                 │         │
│  │  ├── Insurance APIs → Policy data                          │         │
│  │  ├── MF RTAs → Mutual fund holdings                        │         │
│  │  └── ONDC/OCEN → Order/loan history                        │         │
│  │                                                             │         │
│  │  Output: raw/raw_*.ndjson (messy, per-customer)            │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                │                                         │
│                                │ ⑤ Data ready for cleaning              │
│                                ▼                                         │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  STEP 3: DATA CLEANING                                     │         │
│  │  python pipeline/clean_data.py                             │         │
│  │                                                             │         │
│  │  Operations:                                                │         │
│  │  ✓ Standardize dates (all → YYYY-MM-DD)                    │         │
│  │  ✓ Normalize numbers (remove commas, convert to float)     │         │
│  │  ✓ Deduplicate records                                     │         │
│  │  ✓ Validate schemas (account numbers, GSTIN, PAN)          │         │
│  │  ✓ Categorize transactions (ML-based)                      │         │
│  │  ✓ Mask PII (account numbers, addresses)                   │         │
│  │                                                             │         │
│  │  Output: clean/*_clean.ndjson + logs/*.json                │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                │                                         │
│                                │ ⑥ Clean data ready for analytics       │
│                                ▼                                         │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  STEP 4: ANALYTICS GENERATION                              │         │
│  │  python analytics/generate_summaries.py                    │         │
│  │                                                             │         │
│  │  Modules:                                                   │         │
│  │  ├─ Transaction Analytics                                  │         │
│  │  │  └─ Income, Expenses, Cashflow, Stability               │         │
│  │  ├─ GST Analytics                                           │         │
│  │  │  └─ Turnover, Compliance, Growth trends                 │         │
│  │  ├─ Credit Bureau Analytics                                │         │
│  │  │  └─ Score, Existing debt, Payment history               │         │
│  │  ├─ Account Analytics                                      │         │
│  │  │  └─ Banking behavior, Liquidity, Multi-bank usage       │         │
│  │  └─ Anomaly Detection                                      │         │
│  │     └─ Fraud indicators, Spending spikes                   │         │
│  │                                                             │         │
│  │  Output: analytics/*.json (insights per customer)          │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                │                                         │
│                                │ ⑦ Feed into ML models                  │
│                                ▼                                         │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  STEP 5: CUSTOM RISK SCORING                               │         │
│  │                                                             │         │
│  │  Models:                                                    │         │
│  │  ├─ Cashflow Stability Model (71/100)                      │         │
│  │  ├─ Business Health Model (94/100)                         │         │
│  │  ├─ Debt Capacity Model (20/100) ⚠️                        │         │
│  │  └─ Composite Credit Risk Score (66.33/100)                │         │
│  │                                                             │         │
│  │  Output: Risk band + Recommendation                        │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                │                                         │
│                                │ ⑧ Generate decision report             │
│                                ▼                                         │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  STEP 6: LENDING DECISION                                  │         │
│  │                                                             │         │
│  │  Decision: CONDITIONAL_APPROVE                             │         │
│  │  Approved Amount: ₹5L (reduced from ₹10L request)          │         │
│  │  Interest Rate: 14% (medium risk)                          │         │
│  │  Tenure: 24 months                                         │         │
│  │  EMI: ₹24,116/month                                        │         │
│  │  Conditions: Guarantor required, quarterly monitoring      │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                                                          │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
                                │ ⑨ Send decision to underwriter
                                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                    UNDERWRITER (Human Review)                            │
│  - Reviews system recommendation                                        │
│  - Validates anomalies manually                                         │
│  - Final approve/reject decision                                        │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
                                │ ⑩ Inform customer
                                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         CUSTOMER (Receives Decision)                     │
│  - Loan approved: ₹5L @ 14% for 24 months                              │
│  - Terms: EMI ₹24,116, Guarantor needed                                │
│  - Disbursement in 3-5 days                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 API Flow (How to Use This System)

### **Complete API Sequence for One Customer:**

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 1: CONSENT COLLECTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 1. Create consent artefact (in production, this comes from AA)
POST /api/consent/create
{
  "customer_id": "CUST_MSM_00001",
  "consent_artefact": {
    "consent_id": "ABC123",
    "status": "ACTIVE",
    "data_from": "2024-01-01",
    "data_to": "2025-12-11"
  }
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 2: DATA GENERATION (Per Customer)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 2. Generate customer-specific raw data
POST /api/pipeline/generate
{
  "customer_id": "CUST_MSM_00001"
}

# Response:
{
  "status": "started",
  "message": "Generating data for customer CUST_MSM_00001",
  "estimated_time": "2-3 minutes"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 3: DATA CLEANING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 3. Clean raw data
POST /api/pipeline/clean
{
  "customer_id": "CUST_MSM_00001"
}

# Response:
{
  "status": "started",
  "message": "Cleaning data for customer CUST_MSM_00001",
  "estimated_time": "1-2 minutes"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 4: ANALYTICS GENERATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 4. Generate analytics insights
POST /api/pipeline/analytics
{
  "customer_id": "CUST_MSM_00001"
}

# Response:
{
  "status": "started",
  "message": "Generating analytics for customer CUST_MSM_00001",
  "estimated_time": "30 seconds"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 5: RETRIEVE ANALYTICS (For Underwriter Review)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 5. Get transaction analytics
GET /api/analytics?customer_id=CUST_MSM_00001

# Response:
{
  "overall": { ... },
  "transactions": { ... },
  "accounts": { ... },
  "gst": { ... },
  "anomalies": [ ... ]
}

# 6. Get specific dataset (with consent validation)
GET /api/data/transactions?customer_id=CUST_MSM_00001&consent_id=ABC123&limit=100

# Response:
{
  "dataset": "transactions",
  "count": 100,
  "data": [ ... ]
}

# 7. Get validation logs (check data quality)
GET /api/logs/validation?customer_id=CUST_MSM_00001

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 6: RISK SCORING (Future: ML API)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 8. Get custom credit risk score
POST /api/risk/score
{
  "customer_id": "CUST_MSM_00001"
}

# Response:
{
  "customer_id": "CUST_MSM_00001",
  "credit_risk_score": 66.33,
  "risk_band": "BORDERLINE",
  "recommendation": "MANUAL_REVIEW",
  "factors": { ... }
}
```

---

## 📁 File Structure (Per Customer)

```
data_lake/
│
├── raw/                                # Raw data (per customer, temporary)
│   ├── CUST_MSM_00001_consent.ndjson
│   ├── CUST_MSM_00001_accounts.ndjson
│   ├── CUST_MSM_00001_transactions.ndjson
│   ├── CUST_MSM_00001_gst.ndjson
│   └── ... (auto-deleted after 90 days)
│
├── clean/                              # Cleaned data (per customer)
│   ├── CUST_MSM_00001_accounts_clean.ndjson
│   ├── CUST_MSM_00001_transactions_clean.ndjson
│   └── ...
│
├── analytics/                          # Analytics outputs (per customer)
│   ├── CUST_MSM_00001_transaction_summary.json
│   ├── CUST_MSM_00001_gst_summary.json
│   ├── CUST_MSM_00001_credit_summary.json
│   ├── CUST_MSM_00001_anomalies.json
│   └── CUST_MSM_00001_overall_summary.json
│
└── logs/                               # Validation/audit logs
    ├── CUST_MSM_00001_validation_errors.json
    └── CUST_MSM_00001_access_log.json
```

---

## 🎯 Key Differentiators of This Solution

| Feature | Traditional Lending | This AA-Based Solution |
|---------|-------------------|----------------------|
| **Data Collection** | Manual documents (bank statements PDFs) | Automated via AA (encrypted, structured) |
| **Turnaround Time** | 7-15 days | 1-2 hours (real-time) |
| **Data Accuracy** | Prone to forgery, OCR errors | Direct from source (tamper-proof) |
| **Credit Assessment** | Bureau score only | Bureau + Cashflow + GST + Custom ML |
| **Customer Effort** | Upload 10+ documents | One-click consent |
| **Data Freshness** | 30-90 days old | Real-time (today's data) |
| **Fraud Detection** | Manual verification | Automated anomaly detection |
| **Compliance** | Manual DPDP compliance | Built-in consent & data purging |

---

## 📝 Summary: One Borrower Journey

1. **Customer**: "I need a ₹10L business loan"
2. **Lender**: "Grant us consent to fetch your financial data via AA"
3. **Customer**: *Signs consent on AA app (Finvu/OneMoney)*
4. **System**: Fetches Bank + GST + Bureau + Insurance data
5. **System**: Cleans & validates data (standardizes formats)
6. **System**: Generates analytics (cashflow, income, turnover, anomalies)
7. **System**: Runs ML risk models → Credit risk score: **66.33/100**
8. **System**: Recommends "Approve ₹5L @ 14% with guarantor"
9. **Underwriter**: Reviews, validates anomalies, approves
10. **Customer**: Receives loan offer in 2 hours (vs 7 days traditional)

---

## 🔮 Future Enhancements

- [ ] **Real-time ML scoring API** (train models on historical data)
- [ ] **Alternative data sources** (utility bills, telecom, e-commerce)
- [ ] **Fraud detection models** (synthetic data detection, ID verification)
- [ ] **Dynamic interest rate pricing** (real-time risk-based rates)
- [ ] **Predictive analytics** (forecast next 3 months cashflow)
- [ ] **Industry benchmarking** (compare customer vs peer group)

---

**Last Updated**: December 12, 2025
**Document Owner**: MSME Lending Team
