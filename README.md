# MSME Lending Solution - Indian Financial Data Lake

## Overview

This is a **complete MSME lending decision engine** that simulates the **Account Aggregator (AA) Framework** for credit underwriting. It demonstrates:

**One Borrower → One Consent → One Dataset → One Analytics Package**

The system generates synthetic data and provides **per-customer analytics** for loan decisioning, following:
- 🏛️ **RBI Account Aggregator Framework**
- 🔒 **Digital Personal Data Protection Act (DPDP) 2023**
- 📊 **Multi-source financial data aggregation** (Bank, GST, Bureau, Insurance, MF, ONDC, OCEN)

---

## 🎯 Solution Architecture

```
Step 1: Customer Consent (AA Framework) → 
Step 2: Data Fetch (Banking, GST, Bureau) → 
Step 3: Clean & Validate → 
Step 4: Analytics & Insights → 
Step 5: Credit Scoring → 
Step 6: Loan Decision
```

**The Lending Journey**:
1. **Customer Consent**: Borrower grants consent via AA app to access financial data
2. **Data Fetch**: System fetches data from multiple FIPs (Financial Information Providers)
3. **Clean & Validate**: Raw data is standardized and validated for quality
4. **Analytics**: Generate cashflow, turnover, spending patterns, and anomaly detection
5. **Credit Scoring**: Calculate custom risk scores (not bureau score)
6. **Loan Decision**: Review analytics and scores to approve/reject loan application

**Key Principle**: All operations are **per-customer only**. Bulk data operations are prohibited (DPDP compliance).

For complete flow documentation, see: [CUSTOMER_LENDING_FLOW.md](docs/CUSTOMER_LENDING_FLOW.md)

---

## 📊 Data Sources (Per Customer)

### 1. **Consent Artefacts** (RBI AA Framework)
Digital consent for financial data sharing
- Schema: `schemas/consent_schema.json`
- Per customer: 1 consent record

### 2. **Banking Data** (Account Aggregator)
Multi-bank transactions from HDFC, ICICI, SBI, Axis, Kotak, etc.
- **Accounts**: 2-5 per customer
- **Transactions**: 500-5000 per customer (6-12 months)
- Schemas: `schemas/account_schema.json`, `schemas/transaction_schema.json`
- **Analytics**: Cashflow, income detection, expense patterns

### 3. **GST Returns** (GSTN Integration)
GSTR-1, GSTR-3B filings with invoice details
- **Returns**: 12-24 per customer (monthly)
- Schema: `schemas/gst_schema.json`
- **Analytics**: Business turnover, tax compliance, revenue trends

### 4. **Credit Bureau Reports**
CIBIL/Experian-style reports with DPD grids
- **Reports**: 1-4 per customer
- Schema: `schemas/credit_report_schema.json`
- **Analytics**: Credit score, existing debt, repayment history

### 5. **Insurance Policies**
Life, Health, Vehicle, Term policies
- **Policies**: 0-3 per customer
- Schema: `schemas/insurance_schema.json`
- **Analytics**: Financial discipline, asset ownership

### 6. **Mutual Funds**
AMC holdings, SIP investments
- **Holdings**: 0-10 per customer
- Schema: `schemas/mutual_fund_schema.json`
- **Analytics**: Savings behavior, liquidity

### 7. **ONDC Orders** (E-commerce)
Beckn protocol orders (for online sellers)
- **Orders**: 0-100 per customer
- Schema: `schemas/ondc_schema.json`
- **Analytics**: Business activity for merchants

### 8. **OCEN Loan Applications**
Previous loan applications
- **Applications**: 0-5 per customer
- Schema: `schemas/ocen_schema.json`
- **Analytics**: Loan stacking detection

---

## 🔧 Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 16+ (for React frontend)
- 4GB+ RAM
- 5GB+ disk space

### Backend Setup
```bash
cd data_lake

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

---

## 🚀 Quick Start

### Prerequisites Setup

**One-Time Data Generation** (Run once to create the dataset):
```bash
cd data_lake
venv\Scripts\activate
python generate_all.py
```
This creates all raw data files in `raw/` directory. You only need to do this once.

---

### Daily Usage: Process Customer Applications

1. **Start Backend**:
```bash
cd data_lake
venv\Scripts\activate
python api_panel\app.py
```
Backend runs at: http://localhost:5000

2. **Start Frontend** (new terminal):
```bash
cd data_lake\frontend
npm start
```
Frontend runs at: http://localhost:3000

3. **Process Loan Applications** (The Real Flow):
   - **Step 1**: Enter Customer ID (e.g., CUST_MSM_00001)
   - **Step 2**: Click "Validate Consent & Fetch Data" - System simulates fetching data from AA
   - **Step 3**: Click "Clean & Validate Data" - System standardizes raw banking/GST/bureau data
   - **Step 4**: Click "Generate Analytics & Credit Score" - System analyzes cashflow, turnover, anomalies
   - **Step 5**: Review credit score and risk assessment
   - **Step 6**: Make lending decision (approve/reject) based on insights

---

### The Complete AA-Based Lending Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: Customer Consent (AA App)                                  │
│ - Borrower opens AA app and grants consent                        │
│ - Consent covers: Bank, GST, Credit Bureau, Insurance             │
│ - Valid for: 6 months                                              │
└─────────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: Data Fetch from Multiple Sources                           │
│ - Banking: Last 12 months transactions from all accounts          │
│ - GST: Last 24 months GSTR-1 and GSTR-3B filings                 │
│ - Bureau: Latest credit report with existing loans                │
│ - Insurance: Active policies                                       │
└─────────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: Clean & Validate (Your Action)                            │
│ - Standardize dates: "4 Nov 25" → "2025-11-04"                   │
│ - Parse amounts: "₹1,250.00 Dr" → -1250.0                        │
│ - Categorize transactions: UPI/Amazon → SHOPPING                  │
│ - Flag missing/duplicate data                                      │
└─────────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: Generate Analytics & Insights (Your Action)                │
│ - Transaction Analytics: Income, expenses, cashflow trends         │
│ - GST Analytics: Turnover, tax compliance, filing status          │
│ - Credit Analytics: Existing debt, DTI ratio, repayment history   │
│ - Anomaly Detection: Unusual spikes, fraud indicators             │
└─────────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: Calculate Custom Credit Score (Automatic)                  │
│ - Cashflow Stability Score (0-100)                                │
│ - Business Health Score (0-100)                                   │
│ - Debt Capacity Score (0-100)                                     │
│ - Overall Risk Score (0-100)                                      │
└─────────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 6: Loan Decision (Review & Decide)                           │
│ - Review all analytics and scores                                 │
│ - Check for red flags (anomalies, poor compliance, high debt)    │
│ - Make decision: APPROVE or REJECT                                │
│ - If approved: Set loan amount, tenure, interest rate             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔒 Data Privacy & DPDP Compliance

### Per-Customer Enforcement

All APIs require `customer_id`:

```bash
# ❌ REJECTED: Bulk data request
GET /api/data/transactions?type=raw

# ✅ ALLOWED: Per-customer request
GET /api/data/transactions?customer_id=CUST_MSM_00001&type=raw
```

### Data Retention Policy
- **Active Consent**: Data accessible for lending decision
- **Loan Approved**: Retain 90 days (regulatory)
- **Loan Rejected**: Delete within 30 days
- **Consent Revoked**: Delete within 24 hours

---

## 📊 Analytics Generated (Per Customer)

### Transaction Analytics
- Monthly income/expenses
- Cashflow trends
- Spending patterns by category
- Top merchants
- Payment mode distribution

### GST Analytics
- Business turnover (monthly/annual)
- Tax compliance rate
- Filing status (on-time/late)
- Revenue growth trends

### Credit Analytics
- Bureau score
- Existing debt obligations
- Debt service ratio (DTI)
- Repayment history
- Account age & mix

### Anomaly Detection
- High-value transactions
- Spending spikes
- Income irregularities
- Fraud indicators

### Custom Risk Scores
- **Cashflow Stability Score** (0-100)
- **Business Health Score** (0-100)
- **Debt Capacity Score** (0-100)
- **Overall Credit Risk Score** (0-100)

See [CUSTOMER_LENDING_FLOW.md](docs/CUSTOMER_LENDING_FLOW.md) for detailed scoring methodology.

---

## 🔍 API Endpoints

### Pipeline Control (Per Customer)
```bash
POST /api/pipeline/generate
{
  "customer_id": "CUST_MSM_00001"
}

POST /api/pipeline/clean
{
  "customer_id": "CUST_MSM_00001"
}

POST /api/pipeline/analytics
{
  "customer_id": "CUST_MSM_00001"
}
```

### Data Access (Per Customer)
```bash
GET /api/data/transactions?customer_id=CUST_MSM_00001&type=raw&limit=100
GET /api/data/gst?customer_id=CUST_MSM_00001&type=clean
```

### Analytics Retrieval
```bash
GET /api/analytics?customer_id=CUST_MSM_00001
```

### System Stats
```bash
GET /api/stats  # Dataset counts (anonymized)

---

## 📁 Project Structure

```
data_lake/
├── config.json                      # Data generation configuration
├── requirements.txt                 # Python dependencies
├── generate_all.py                  # Master data generator (per-customer)
│
├── generators/                      # Data generation modules
│   ├── indian_data_utils.py        # Utility functions
│   ├── generate_banking_data.py    # Bank accounts + transactions
│   ├── generate_additional_data.py # GST + Credit bureau
│   ├── generate_insurance_mf.py    # Insurance + Mutual funds
│   └── generate_ondc_ocen.py       # ONDC + OCEN
│
├── pipeline/                        # Data processing
│   └── clean_data.py               # Cleaning & standardization (per-customer)
│
├── analytics/                       # Analytics generation
│   └── generate_summaries.py       # Summaries & insights (per-customer)
│
├── schemas/                         # JSON Schema definitions
│   ├── consent_schema.json
│   ├── account_schema.json
│   ├── transaction_schema.json
│   ├── gst_schema.json
│   ├── credit_report_schema.json
│   ├── insurance_schema.json
│   ├── mutual_fund_schema.json
│   ├── ondc_schema.json
│   └── ocen_schema.json
│
├── raw/                            # Raw data (per-customer, temporary)
│   └── raw_*.ndjson               # Auto-deleted after processing
│
├── clean/                          # Cleaned data (per-customer)
│   └── *_clean.ndjson
│
├── logs/                           # Validation & transformation logs
│   └── *_log.json
│
├── analytics/                      # Analytics outputs (per-customer)
│   ├── transaction_summary.json
│   ├── gst_summary.json
│   ├── credit_summary.json
│   └── anomalies_report.json
│
├── api_panel/                      # Flask backend
│   ├── app.py                     # API server + WebSocket
│   └── templates/
│       └── index.html
│
├── frontend/                       # React UI
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.js
│   │   │   ├── PipelineMonitor.js  # Customer ID input + pipeline control
│   │   │   ├── DatasetViewer.js    # Per-customer data viewer
│   │   │   ├── AnalyticsInsights.js # Charts & insights
│   │   │   ├── LogsViewer.js
│   │   │   └── FileManager.js
│   │   └── App.js
│   ├── package.json
│   └── tailwind.config.js
│
└── docs/                           # Documentation
    ├── CUSTOMER_LENDING_FLOW.md   # Complete lending journey
    ├── data_dictionary.md          # Field definitions
    └── TESTING_GUIDE.md           # Testing instructions
```

---

## 🎯 Use Cases

### 1. MSME Lending (Primary)
- Fetch AA data + GST + Bureau for loan applicant
- Generate cashflow analytics
- Calculate custom risk scores
- Make approve/reject decision

### 2. Credit Underwriting Training
- Train underwriters on real-world data patterns
- Demonstrate messy data challenges
- Practice data quality assessment

### 3. ML Model Development
- Train income detection models
- Build category prediction models
- Develop fraud detection algorithms

### 4. Fintech Product Testing
- Test AA integration workflows
- Validate data transformation pipelines
- Benchmark analytics accuracy

---

## 🧪 Sample Data

### Transaction (Raw - Messy)
```json
{
  "transaction_id": "TXN000000001",
  "account_id": "ACC00000001",
  "date": "4 Nov 25",
  "amount": "1,250.00 Dr",
  "narration": "UPI/Amazon/amazonpay@ybl",
  "balance": "₹ 45,320.50"
}
```

### Transaction (Clean - Standardized)
```json
{
  "transaction_id": "TXN000000001",
  "account_id": "ACC00000001",
  "date": "2025-11-04",
  "type": "DEBIT",
  "amount": 1250.0,
  "mode": "UPI",
  "merchant_name": "Amazon",
  "category": "SHOPPING",
  "balance_after": 45320.5,
  "currency": "INR"
}
```

---

## 📈 Performance

### Generation Time (Per Customer)
- Data fetch simulation: 30-60 seconds
- Data cleaning: 10-20 seconds
- Analytics generation: 5-10 seconds
- **Total**: ~2 minutes per customer

### Scalability
- Single customer: 2 minutes
- 100 customers (parallel): ~15 minutes
- 1000 customers: ~2.5 hours

---

## 🛠️ Configuration

Edit `config.json` to customize:

```json
{
  "scale": {
    "users": 1000,              // Per test run (can simulate multiple customers)
    "bank_accounts": 1500,
    "transactions": 50000
  },
  "date_range": {
    "start": "2024-01-01",
    "end": "2025-12-11"
  },
  "messiness_config": {
    "date_format_variation": true,
    "numeric_format_inconsistency": true,
    "missing_field_probability": 0.05,
    "duplicate_probability": 0.02
  }
}
```

---

## 🔒 Security & Compliance

### DPDP Act 2023 Compliance
- ✅ Per-customer data isolation
- ✅ Consent-based access
- ✅ Data minimization
- ✅ Automatic deletion post-processing
- ✅ Audit trail for all access

### RBI AA Framework
- ✅ Consent artefact validation
- ✅ FIP-to-FIU data flow simulation
- ✅ Encrypted data transfer (simulated)
- ✅ Granular consent types

---

## 📚 Documentation

- **[CUSTOMER_LENDING_FLOW.md](docs/CUSTOMER_LENDING_FLOW.md)** - Complete lending journey (MUST READ)
- **[data_dictionary.md](docs/data_dictionary.md)** - Field definitions & business rules
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Testing instructions
- OCEN: 1-2 min

**Total**: ~60-90 minutes for full dataset

### Memory Usage
- Peak: ~3-4 GB RAM
- Disk: ~8-12 GB (depending on transaction count)

---

## 🔒 Data Privacy

**All data is 100% synthetic.**
- No real individuals
- No real account numbers
- No real PANs or GSTINs
- Fictional names, addresses, and phone numbers

Safe for testing, demos, and development.

---

## 📚 References

- [Account Aggregator Framework - RBI](https://www.rbi.org.in/)
- [ONDC - Open Network for Digital Commerce](https://ondc.org/)
- [OCEN - Open Credit Enablement Network](https://ocen.dev/)
- [GST API Documentation](https://www.gst.gov.in/)
- [Beckn Protocol Specification](https://beckn.org/)

---

## 🤝 Contributing

This is a demonstration project. Feel free to:
- Add more FIP data sources
- Enhance messiness patterns
- Improve cleaning algorithms
- Add visualization dashboards

---

## 📄 License

MIT License - Free to use for educational and commercial purposes.

---

## 📧 Support

For questions or issues, please check:
1. `docs/data_dictionary.md` for field definitions
2. `logs/` directory for error details
3. API panel at http://localhost:5000 for data exploration

---

**Generated with ❤️ for the Indian BFSI ecosystem**
