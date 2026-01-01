# 🔄 INDIAN FINANCIAL DATA LAKE - COMPLETE FLOW DOCUMENTATION

## 📋 TABLE OF CONTENTS
1. [System Overview](#system-overview)
2. [Architecture Flow](#architecture-flow)
3. [Data Generation Flow](#data-generation-flow)
4. [Data Processing Flow](#data-processing-flow)
5. [API Debug Panel Flow](#api-debug-panel-flow)
6. [Complete End-to-End Flow](#complete-end-to-end-flow)

---

## 🏗️ SYSTEM OVERVIEW

### Purpose
Generate realistic synthetic Indian financial data matching production patterns from:
- **Account Aggregators** (Finarkein, Setu, Perfios)
- **GST Network** (GSTN)
- **Credit Bureaus** (CIBIL, Experian, Equifax, CRIF)
- **Insurance Providers**
- **Mutual Fund AMCs**
- **ONDC Network** (Open Network for Digital Commerce)
- **OCEN Protocol** (Open Credit Enablement Network)

### Key Features
✅ **9 Distinct Datasets** - Each with Indian-specific patterns  
✅ **Realistic Messiness** - Mimics production data quality issues  
✅ **Complete Pipeline** - Raw → Clean → Analytics  
✅ **Web Debug Panel** - Visual exploration tool  
✅ **Configurable Scale** - From 1K to 50K+ users  
✅ **Consent-based Access & Smart Collect** - Consent enforcement and a consent-driven micro-collection module

---

## 🏛️ ARCHITECTURE FLOW

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INPUT                                   │
│                  (config.json configuration)                         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STEP 1: DATA GENERATION                           │
│                     (generate_all.py)                                │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Banking Module  │  │   GST & Bureau   │  │  Insurance & MF  │  │
│  │                  │  │     Module       │  │     Module       │  │
│  │  • Consents      │  │  • GST Returns   │  │  • Policies      │  │
│  │  • Accounts      │  │  • Credit        │  │  • Mutual Funds  │  │
│  │  • Transactions  │  │    Reports       │  │                  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                      │
│  ┌──────────────────┐                                               │
│  │ ONDC & OCEN Mod  │                                               │
│  │  • ONDC Orders   │                                               │
│  │  • OCEN Loans    │                                               │
│  └──────────────────┘                                               │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      RAW DATA STORAGE                                │
│                       (raw/*.ndjson)                                 │
├─────────────────────────────────────────────────────────────────────┤
│  raw_consent.ndjson          | raw_policies.ndjson                  │
│  raw_accounts.ndjson         | raw_mutual_funds.ndjson              │
│  raw_transactions.ndjson     | raw_ondc_orders.ndjson               │
│  raw_gst.ndjson              | raw_ocen_applications.ndjson         │
│  raw_credit_reports.ndjson   |                                      │
│  raw_smart_collect.ndjson    |                                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 STEP 2: DATA PROCESSING PIPELINE                     │
│                    (pipeline/clean_data.py)                          │
├─────────────────────────────────────────────────────────────────────┤
│  Phase 1: PARSING          → Parse dates, amounts, formats          │
│  Phase 2: CLEANING         → Remove noise, fix formatting           │
│  Phase 3: NORMALIZATION    → Standardize codes (PAN, GSTIN, IFSC)   │
│  Phase 4: STANDARDIZATION  → Enum mapping, type coercion            │
│  Phase 5: DEDUPLICATION    → Remove duplicates                      │
│  Phase 6: VALIDATION       → JSONSchema validation                  │
│  Consent Enforcement       → Apply consent filters (consent artefacts)│
└────────────────────────────┬────────────────────────────────────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
                 ▼                       ▼
┌─────────────────────────────┐  ┌──────────────────────────────────┐
│    CLEAN DATA STORAGE       │  │    TRANSFORMATION LOGS           │
│   (clean/*.ndjson)          │  │      (logs/*.json)               │
├─────────────────────────────┤  ├──────────────────────────────────┤
│ transactions_clean.ndjson   │  │ transaction_parsing_log.json     │
│ accounts_clean.ndjson       │  │ transaction_cleaning_log.json    │
│ gst_clean.ndjson            │  │ transaction_validation_errors    │
│ ... (all 9 datasets)        │  │ ... (for each dataset)           │
└────────────────┬────────────┘  └──────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│               STEP 3: ANALYTICS GENERATION                           │
│              (analytics/generate_summaries.py)                       │
├─────────────────────────────────────────────────────────────────────┤
│  • Transaction summaries (mean, median, distributions)               │
│  • Account summaries (bank-wise, type-wise)                          │
│  • GST summaries (turnover, filing status)                           │
│  • Credit score distributions                                        │
│  • Anomaly detection (outliers, suspicious patterns)                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   ANALYTICS STORAGE                                  │
│                  (analytics/*.json)                                  │
├─────────────────────────────────────────────────────────────────────┤
│  transaction_summary.json   | credit_summary.json                   │
│  account_summary.json       | anomalies_report.json                 │
│  gst_summary.json           | overall_summary.json                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 STEP 4: WEB DEBUG PANEL                              │
│                   (api_panel/app.py)                                 │
├─────────────────────────────────────────────────────────────────────┤
│  Flask REST API serving:                                             │
│  • GET /              → Dashboard UI                                 │
│  • GET /api/data/{dataset}?type=raw|clean → Dataset viewer           │
│  • GET /api/logs/{logType}  → Transformation logs                    │
│  • GET /api/consent   → Consent artefacts (raw|clean)                 │
│  • POST /api/smart_collect → Trigger Smart Collect request           │
│  • GET /api/stats     → Overall statistics                           │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │   USER BROWSER     │
                    │ http://localhost:5000 │
                    └────────────────────┘
```

---

## 🔄 DATA GENERATION FLOW

### Entry Point: `generate_all.py`

```python
START
  │
  ├─► Load config.json
  │     • Read scale parameters (users, accounts, transactions)
  │     • Read messiness config
  │     • Read date ranges, bank lists
  │
  ├─► Execute Step 1: Banking Data
  │     │
  │     ├─► ConsentGenerator
  │     │     • Generate 50K consent artefacts
  │     │     • AA providers: Finarkein, Setu, Anumati, Saafe, CAMS, OneMoney
  │     │     • Consent types: PROFILE, SUMMARY, TRANSACTIONS
  │     │     • Output: raw/raw_consent.ndjson
  │     │
  │     ├─► BankAccountGenerator
  │     │     • Generate 80K bank accounts
  │     │     • Banks: HDFC, ICICI, SBI, Axis, Kotak, IDFC, Yes
  │     │     • Account types: Savings, Current, CC, OD, NRE, NRO
  │     │     • Realistic balances (₹15K-₹2L)
  │     │     • Output: raw/raw_accounts.ndjson
  │     │
  │     └─► TransactionGenerator
  │           • Generate 30M transactions
  │           • Categories: SALARY, EMI, FOOD, SHOPPING, TRAVEL, etc.
  │           • Modes: UPI, NEFT, IMPS, RTGS, CASH, CHEQUE, ATM, POS
  │           • Apply messiness:
  │           │   - Date format variations (5 formats)
  │           │   - Numeric format inconsistencies (Indian vs Western commas)
  │           │   - Missing fields (15% probability)
  │           │   - Duplicates (2% probability)
  │           │   - Bank-specific quirks (HDFC truncation, SBI Hindi, etc.)
  │           • Output: raw/raw_transactions.ndjson
  │
  ├─► Execute Step 2: GST & Bureau
  │     │
  │     ├─► GSTGenerator
  │     │     • Generate 25K GST returns
  │     │     • Return types: GSTR-1, GSTR-3B
  │     │     • Invoice details with IGST/CGST/SGST breakdown
  │     │     • Turnover distributions: Micro/Small/Medium
  │     │     • Filing behavior: Filed/Late/Pending
  │     │     • Output: raw/raw_gst.ndjson
  │     │
  │     └─► CreditBureauGenerator
  │           • Generate 30K credit reports
  │           • Bureau types: CIBIL, Experian, Equifax, CRIF
  │           • Credit scores: 300-900 (realistic distribution)
  │           • 24-month DPD grids (000, 030, 060, 090, XXX, STD)
  │           • Multiple account types: Auto, Home, Personal, CC, Gold
  │           • Enquiry history
  │           • Output: raw/raw_credit_reports.ndjson
  │
  ├─► Execute Step 3: Insurance & MF
  │     │
  │     ├─► InsuranceGenerator
  │     │     • Generate 40K insurance policies
  │     │     • Types: Life, Health, Term, ULIP, Vehicle, Home, Travel
  │     │     • Realistic premiums (₹5K-₹50K)
  │     │     • Claim history
  │     │     • Output: raw/raw_policies.ndjson
  │     │
  │     └─► MutualFundGenerator
  │           • Generate 20K MF portfolios
  │           • AMCs: HDFC, ICICI Pru, SBI, Aditya Birla, etc.
  │           • Scheme types: Equity, Debt, Hybrid, Liquid
  │           • NAV history (12 months)
  │           • SIP details
  │           • Output: raw/raw_mutual_funds.ndjson
  │
  └─► Execute Step 4: ONDC & OCEN
        │
        ├─► ONDCGenerator
        │     • Generate 100K ONDC orders
        │     • Beckn protocol format
        │     • Providers: Amazon, Flipkart, Swiggy, Zomato, BigBasket
        │     • Fulfillment states
        │     • Output: raw/raw_ondc_orders.ndjson
        │
        └─► OCENGenerator
              • Generate 15K loan applications
              • Loan purposes: Working Capital, Term Loan, Invoice Discounting
              • Business details
              • Scoring features
              • Document checklist
              • Output: raw/raw_ocen_applications.ndjson
END
```

---

## 🧹 DATA PROCESSING FLOW

### Entry Point: `pipeline/clean_data.py`

```python
START
  │
  ├─► Initialize Cleaners
  │     • TransactionCleaner (inherits from DataCleaner)
  │     • AccountCleaner
  │     • GSTCleaner
  │     • Generic DataCleaner for others
  │
  ├─► Process Transactions (30M records)
  │     │
  │     ├─► PHASE 1: PARSING
  │     │     • parse_date() - Handle 5 different date formats
  │     │     │   - %Y-%m-%d, %d/%m/%Y, %d-%m-%Y, %Y%m%d, %d.%m.%Y
  │     │     │   - Extract ISO 8601 format
  │     │     • parse_amount() - Handle numeric variations
  │     │     │   - Remove commas (both Indian and Western)
  │     │     │   - Strip ₹, Rs., INR symbols
  │     │     │   - Convert to float
  │     │     • Log parsing issues
  │     │
  │     ├─► PHASE 2: CLEANING
  │     │     • Trim whitespace
  │     │     • Remove special characters
  │     │     • Fix encoding issues
  │     │     • Normalize merchant names
  │     │     │   - "Amazon.in" → "Amazon"
  │     │     │   - "flipkart   " → "Flipkart"
  │     │     • Log cleaning transformations
  │     │
  │     ├─► PHASE 3: NORMALIZATION
  │     │     • normalize_ifsc() - Uppercase IFSC codes
  │     │     • normalize_pan() - Validate & uppercase PAN
  │     │     • normalize_upi() - Standardize UPI handles
  │     │     • normalize_account_number() - Remove dashes/spaces
  │     │
  │     ├─► PHASE 4: STANDARDIZATION
  │     │     • Standardize transaction types
  │     │     │   - "Dr", "DR", "debit" → "DEBIT"
  │     │     │   - "Cr", "CR", "credit" → "CREDIT"
  │     │     • Standardize payment modes
  │     │     │   - "upi", "UPI ", "Upi" → "UPI"
  │     │     │   - Map all variations to canonical forms
  │     │     • Standardize categories
  │     │     │   - Use predefined enum values
  │     │
  │     ├─► PHASE 5: DEDUPLICATION
  │     │     • Create hash of (account_number, date, amount, narration)
  │     │     • Keep first occurrence
  │     │     • Log duplicate count
  │     │
  │     └─► PHASE 6: VALIDATION
  │           • Load schemas/transaction_schema.json
  │           • Validate each record against JSONSchema
  │           • Log validation errors with details
  │           • Output clean records to clean/transactions_clean.ndjson
  │
  ├─► Process Accounts (80K records)
  │     • Similar 6-phase pipeline
  │     • Special handling for IFSC normalization
  │     • Account number validation
  │     • Output: clean/accounts_clean.ndjson
  │
  ├─► Process GST Returns (25K records)
  │     • GSTIN validation (regex pattern)
  │     • Invoice-level cleaning
  │     • Tax amount validation (IGST + CGST + SGST = Total)
  │     • Output: clean/gst_clean.ndjson
  │
  ├─► Process Credit Reports (30K records)
  │     • Credit score range validation (300-900)
  │     • DPD string validation
  │     • Account type normalization
  │     • Output: clean/credit_reports_clean.ndjson
  │
  └─► Process Remaining Datasets
        • Insurance policies
        • Mutual funds
        • ONDC orders
        • OCEN applications
        • Consent artefacts
        • Output: clean/*_clean.ndjson
END
```

---

## 🌐 API DEBUG PANEL FLOW

### Entry Point: `api_panel/app.py`

```python
START Flask Server
  │
  ├─► Initialize
  │     • Set up Flask app
  │     • Enable CORS
  │     • Define base paths (raw/, clean/, logs/, analytics/)
  │
  ├─► Route: GET /
  │     │
  │     └─► Render dashboard (templates/index.html)
  │           • Beautiful gradient UI
  │           • 9 dataset cards with icons
  │           • Statistics summary (users, accounts, transactions)
  │           • Interactive buttons for each dataset
  │
  ├─► Route: GET /api/data/<dataset>?type=raw|clean&limit=100
  │     │
  │     ├─► Parse parameters
  │     │     • dataset: transactions, accounts, gst, etc.
  │     │     • type: raw or clean
  │     │     • limit: number of records (default 100)
  │     │
  │     ├─► Load NDJSON file
  │     │     • If type=raw: load from raw/raw_{dataset}.ndjson
  │     │     • If type=clean: load from clean/{dataset}_clean.ndjson
  │     │     • Read line-by-line up to limit
  │     │
  │     └─► Return JSON response
  │           {
  │             "dataset": "transactions",
  │             "type": "raw",
  │             "count": 100,
  │             "data": [...]
  │           }
  │
  ├─► Route: GET /api/logs/<logType>
  │     │
  │     ├─► Parse log type
  │     │     • parsing → transaction_parsing_log.json
  │     │     • cleaning → transaction_cleaning_log.json
  │     │     • validation → transaction_validation_errors.json
  │     │
  │     └─► Return JSON response
  │           • First 100 log entries
  │
  └─► Route: GET /api/stats
        │
        ├─► Count records in all datasets
        │     • raw_transactions.ndjson → 30M lines
        │     • raw_accounts.ndjson → 80K lines
        │     • ... (all 9 datasets)
        │
        └─► Return JSON response
              {
                "total_raw_records": 30M+,
                "total_clean_records": 29M+ (after dedup),
                "datasets": {
                  "transactions": {"raw": 30M, "clean": 29M},
                  ...
                }
              }

User Browser Interaction:
  │
  ├─► User opens http://localhost:5000
  │     • Dashboard loads
  │     • Stats auto-fetch via JavaScript
  │
  ├─► User clicks "View Raw" on Transactions
  │     • JavaScript: fetch('/api/data/transactions?type=raw&limit=100')
  │     • Display JSON in viewer panel
  │     • Syntax highlighting
  │
  ├─► User clicks "View Clean" on Transactions
  │     • JavaScript: fetch('/api/data/transactions?type=clean&limit=100')
  │     • Display cleaned JSON
  │     • User can compare raw vs clean side-by-side
  │
  └─► User clicks "Transformation Logs"
        • JavaScript: fetch('/api/logs/parsing')
        • Display parsing transformations
        • Shows date format fixes, amount parsing, etc.
```

---

## 🔄 COMPLETE END-TO-END FLOW

### Quick Start Flow (5 Minutes)

```
1. SETUP (1 min)
   ├─► Run: setup_venv.bat
   │     • Creates Python virtual environment
   │     • Activates venv
   │     • Installs requirements.txt
   │     • Takes ~1 minute
   └─► Success! venv/ folder created

2. GENERATE DATA (60-90 min for full scale, 5 min for test)
   ├─► Edit config.json for quick test:
   │     {
   │       "scale": {
   │         "users": 1000,           // Reduce from 50000
   │         "bank_accounts": 1500,   // Reduce from 80000
   │         "transactions": 50000    // Reduce from 30000000
   │       }
   │     }
   ├─► Activate venv: venv\Scripts\activate
   ├─► Run: python generate_all.py
   │     │
   │     ├─► Step 1: Banking Data (2 min)
   │     │     [DEBUG] Generating 1000 consents...
   │     │     [✓] Generated 1000 consents
   │     │     [DEBUG] Generating 1500 accounts...
   │     │     [✓] Generated 1500 accounts
   │     │     [DEBUG] Generating 50000 transactions...
   │     │     [✓] Generated 50000 transactions
   │     │
   │     ├─► Step 2: GST & Bureau (1 min)
   │     │     [DEBUG] Generating GST returns...
   │     │     [✓] Generated GST returns
   │     │     [DEBUG] Generating credit reports...
   │     │     [✓] Generated credit reports
   │     │
   │     ├─► Step 3: Insurance & MF (1 min)
   │     │     [DEBUG] Generating insurance policies...
   │     │     [✓] Generated policies
   │     │     [DEBUG] Generating mutual funds...
   │     │     [✓] Generated mutual funds
   │     │
   │     └─► Step 4: ONDC & OCEN (1 min)
   │           [DEBUG] Generating ONDC orders...
   │           [✓] Generated ONDC orders
   │           [DEBUG] Generating OCEN applications...
   │           [✓] Generated OCEN applications
   │
   └─► Success! 9 raw NDJSON files in raw/ folder

3. CLEAN DATA (5-10 min)
   ├─► Run: python pipeline\clean_data.py
   │     │
   │     ├─► Processing transactions...
   │     │     [DEBUG] Loading raw_transactions.ndjson...
   │     │     [DEBUG] Loaded 50000 records
   │     │     [1/6] PARSING - Parsing dates and amounts...
   │     │     [2/6] CLEANING - Removing noise...
   │     │     [3/6] NORMALIZATION - Standardizing codes...
   │     │     [4/6] STANDARDIZATION - Mapping enums...
   │     │     [5/6] DEDUPLICATION - Removing duplicates...
   │     │     [6/6] VALIDATION - JSONSchema validation...
   │     │     [✓] Cleaned 49500 transactions (500 duplicates removed)
   │     │
   │     ├─► Processing accounts...
   │     │     [✓] Cleaned 1500 accounts
   │     │
   │     └─► Processing GST, credit, insurance, MF, ONDC, OCEN, consent...
   │           [✓] All datasets cleaned
   │
   └─► Success! 9 clean NDJSON files in clean/ folder
                Logs in logs/ folder

4. GENERATE ANALYTICS (1 min)
   ├─► Run: python analytics\generate_summaries.py
   │     │
   │     ├─► [1/5] Analyzing transactions...
   │     │     • Mean amount: ₹12,450
   │     │     • Median amount: ₹3,200
   │     │     • Top category: SALARY (15%)
   │     │     • Top mode: UPI (45%)
   │     │     [✓] Generated transaction_summary.json
   │     │
   │     ├─► [2/5] Analyzing accounts...
   │     │     • Top bank: HDFC (25%)
   │     │     • Most common type: Savings (60%)
   │     │     [✓] Generated account_summary.json
   │     │
   │     ├─► [3/5] Analyzing GST...
   │     │     [✓] Generated gst_summary.json
   │     │
   │     ├─► [4/5] Analyzing credit reports...
   │     │     • Mean credit score: 720
   │     │     [✓] Generated credit_summary.json
   │     │
   │     └─► [5/5] Detecting anomalies...
   │           • Found 50 high-value outliers
   │           [✓] Generated anomalies_report.json
   │
   └─► Success! 6 analytics files in analytics/ folder

5. LAUNCH DEBUG PANEL (Instant)
   ├─► Run: python api_panel\app.py
   │     │
   │     ├─► [✓] Flask app initialized
   │     ├─► [✓] CORS enabled
   │     ├─► [✓] Base directory: f:\MSMELending\data_lake
   │     ├─► [✓] Raw data: f:\MSMELending\data_lake\raw
   │     └─► [✓] Clean data: f:\MSMELending\data_lake\clean
   │
   │     🌐 Server running at http://localhost:5000
   │     ⌨️  Press Ctrl+C to stop
   │
   └─► Open browser to http://localhost:5000
         • Beautiful dashboard loads
         • Click any dataset to view raw/clean data
         • Explore transformation logs
```

### Automated Flow (One Command)

```
Run: run_complete_pipeline.bat
  │
  ├─► Activates venv
  ├─► Runs generate_all.py
  ├─► Runs clean_data.py
  ├─► Runs generate_summaries.py
  └─► Launches app.py
```

---

## 📊 DATA FLOW DIAGRAM

```
CONFIG.JSON
    │
    ▼
┌───────────────────┐
│  GENERATORS       │
│  • Banking        │
│  • GST/Bureau     │
│  • Insurance/MF   │
│  • ONDC/OCEN      │
└─────────┬─────────┘
          │
          ▼
     RAW DATA (9 files, ~30M+ records)
     ┌──────────────────────────────┐
     │ • Messy dates (5 formats)    │
     │ • Inconsistent numbers       │
     │ • Missing fields (15%)       │
     │ • Duplicates (2%)            │
     │ • Bank quirks                │
     └─────────┬────────────────────┘
               │
               ▼
     CLEANING PIPELINE (6 phases)
     ┌──────────────────────────────┐
     │ 1. Parse → 2. Clean          │
     │ 3. Normalize → 4. Standardize│
     │ 5. Deduplicate → 6. Validate │
     └─────────┬────────────────────┘
               │
          ┌────┴────┐
          ▼         ▼
     CLEAN DATA   LOGS
     9 files      Parsing, Cleaning, Validation
          │
          ▼
     ANALYTICS
     Summaries, Stats, Anomalies
          │
          ▼
     WEB PANEL (Flask)
     Visual Exploration
```

---

## 🎯 KEY DEBUGGING POINTS

### During Generation
- **[DEBUG]** messages show current operation
- **[✓]** shows successful completion
- **[ERROR]** shows failures with stack trace
- Watch for record counts matching config

### During Cleaning
- Check **logs/*.json** for transformation details
- Validation errors indicate schema mismatches
- Duplicate counts show data quality

### In Debug Panel
- **View Raw** shows original messy data
- **View Clean** shows processed data
- **Compare** them to see transformations
- **Logs** show exact changes made

---

## 📦 FILE OUTPUTS

```
f:\MSMELending\data_lake\
│
├── raw/                           # Raw messy data (9 files)
│   ├── raw_consent.ndjson         # 50K records
│   ├── raw_accounts.ndjson        # 80K records
│   ├── raw_transactions.ndjson    # 30M records
│   ├── raw_gst.ndjson             # 25K records
│   ├── raw_credit_reports.ndjson  # 30K records
│   ├── raw_policies.ndjson        # 40K records
│   ├── raw_mutual_funds.ndjson    # 20K records
│   ├── raw_ondc_orders.ndjson     # 100K records
│   └── raw_ocen_applications.ndjson # 15K records
│
├── clean/                         # Cleaned standardized data (9 files)
│   ├── transactions_clean.ndjson
│   ├── accounts_clean.ndjson
│   └── ... (all 9 datasets)
│
├── logs/                          # Transformation logs
│   ├── transaction_parsing_log.json
│   ├── transaction_cleaning_log.json
│   ├── transaction_validation_errors.json
│   └── ... (for each dataset)
│
└── analytics/                     # Analytics & summaries
    ├── transaction_summary.json
    ├── account_summary.json
    ├── gst_summary.json
    ├── credit_summary.json
    ├── anomalies_report.json
    └── overall_summary.json
```

---

## 🚀 NEXT STEPS AFTER GENERATION

1. **Explore Data** → Use debug panel at http://localhost:5000
2. **Integrate** → Load NDJSON files into your application
3. **Analyze** → Use analytics/*.json for insights
4. **Customize** → Edit config.json to change scale/patterns
5. **Extend** → Add new datasets or messiness patterns

---

## 💡 PRO TIPS

✅ **Start Small** - Use 1K users for testing before full 50K scale  
✅ **Monitor Memory** - Large datasets (30M txns) need 4GB+ RAM  
✅ **Use SSD** - Faster I/O for NDJSON processing  
✅ **Parallel Processing** - Consider batch processing for huge scales  
✅ **Incremental Gen** - Generate datasets separately if needed  

---

**End of Flow Documentation** 🎉
