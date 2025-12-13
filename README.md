# MSME Lending Solution — Indian Financial Data Lake

## Problem Statement

**Challenge**: Traditional MSME lending in India faces critical barriers:
- Manual, paper-heavy credit assessment leads to weeks-long approval cycles
- Single-source bureau scores (CIBIL) miss 70% of the real financial picture
- No unified view of banking, GST, insurance, mutual funds, ONDC, OCEN data
- DPDP Act 2023 mandates explicit per-customer consent — bulk data operations prohibited
- RBI Account Aggregator Framework requires standardized multi-FIP data fetching

**Business Impact**:
- 50+ day average loan turnaround for MSMEs
- 40% rejection rate due to incomplete financial visibility
- Manual underwriting prone to bias and errors
- Cannot scale to millions of MSME borrowers

---

## Proposed Solution

A comprehensive MSME credit decisioning platform leveraging:

### 1. Account Aggregator (AA) Framework Integration
- One Borrower → One Consent → One Dataset
- Compliant with RBI AA specs and DPDP Act 2023
- Fetch multi-source financial data: Banking, GST, Bureau, Insurance, MF, ONDC, OCEN

### 2. AI-Powered Multi-Source Analytics
- 7 data sources aggregated per customer (vs. traditional 1-2)
- Automated cashflow analysis, GST compliance scoring, anomaly detection
- Composite credit scoring combining:
  - Cashflow Stability (45% weight) — transaction patterns, income/expense ratios
  - Business Health (35% weight) — GST turnover, ONDC order diversity, MF investments
  - Debt Capacity (20% weight) — credit utilization, OCEN approval rate, insurance coverage

### 3. Explainable AI & Transparency
- Click-to-reveal calculation breakdowns for every metric
- Separate Methodology and Calculations tabs showing real numbers and formulas
- Debug panels in charts for raw data inspection
- All metrics include: Formula, Breakdown with actual values, Risk interpretation

### 4. Pre-loaded Demo Datasets for Quick Demonstration
- 10 customer profiles with varying risk levels and specialized behaviors
- Range from excellent borrowers to high-risk cases with edge scenarios
- Profiles include: High Seasonality, High Debt, Growing Business, Declining Business, etc.
- See `data_lake/docs/CUSTOMER_PROFILES.md` for detailed descriptions

---

## Implementation

### Demo Flow (Current Setup)

**Pre-loaded Datasets**: 10 customer profiles (CUST_MSM_00001 through CUST_MSM_00010) are already generated and stored in `data_lake/raw/`. Each represents different lending scenarios.

**Pipeline Flow**:
```
Customer Selection (choose from 00001-00010)
         ↓
Step 1: Consent Validation (simulated AA consent check)
         ↓
Step 2: Clean & Validate Data (remove outliers, standardize formats)
         ↓
Step 3: Generate Analytics (calculate 7-source summaries + earnings/spendings)
         ↓
Step 4: Calculate Credit Score (composite weighted score + AI insights)
         ↓
Lending Decision (Approve / Review / Reject)
```

### Architecture

```
┌─────────────────┐
│  10 Pre-loaded  │  Demo Customer Datasets
│  Customer       │  (CUST_MSM_00001 - CUST_MSM_00010)
│  Profiles       │  Different risk profiles: seasonal, high-debt, growth, stable, etc.
└─────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────┐
│  Simulated AA Data (stored in data_lake/raw/)        │
│  • Banking (Accounts & Transactions)                 │
│  • GST (GSTR-1, GSTR-3B with monthly aggregation)    │
│  • Credit Bureau (CIBIL/Experian-style reports)      │
│  • Insurance (Life, Health, Vehicle policies)        │
│  • Mutual Funds (AMC holdings, SIPs)                 │
│  • ONDC (Beckn protocol orders)                      │
│  • OCEN (loan applications)                          │
└──────────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│  Data Pipeline (per-customer)                        │
│  1. Clean & Validate (schemas + error logs)          │
│  2. Generate Analytics (7 summaries + overall)       │
│  3. AI Insights (Deepseek/Gemini - lending reco)     │
│  4. Calculate Credit Score (composite weighted)      │
└──────────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│  Frontend Dashboard                                  │
│  • Lending Analytics & AI Insights (main view)       │
│  • Earnings vs Spendings (detailed financial health) │
│  • Credit Methodology (explainability doc)           │
│  • Credit Calculations (numeric examples)            │
│  • Pipeline Monitor (real-time progress)             │
│  • Dataset Viewer (raw/clean data inspection)        │
└──────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend**:
- Python 3.11+ (Flask, SocketIO)
- NDJSON for raw/clean data storage
- JSON for analytics summaries
- AI providers: Deepseek (primary), Google Gemini (fallback)

**Frontend**:
- React 18, Tailwind CSS
- Recharts for visualizations
- Axios for API calls
- WebSocket (Socket.IO client) for pipeline updates

**Data Generation**:
- Realistic Indian data patterns (PAN, GSTIN, IFSC, mobile, addresses)
- Per-customer seeding (hash of customer_id → unique deterministic data)
- Configurable messiness (date format variation, missing fields, duplicates)
- Specialized profile modifications (seasonality, debt, growth patterns)

---

## Features Implemented

### Data Sources (Per Customer)
1. **Consent Artefacts** — RBI AA Framework digital consent
2. **Banking** — 2-5 accounts, 50,000 transactions (multiple years)
3. **GST Returns** — 5,000 returns with monthly aggregation to prevent inflation
4. **Credit Bureau** — 843 credit report entries with simulated bureau scores
5. **Insurance** — 0-1,000 policies (Life, Health, Vehicle)
6. **Mutual Funds** — 0-425 portfolios (AMC, SIPs)
7. **ONDC Orders** — 100-1,903 orders (Beckn protocol, for sellers)
8. **OCEN Applications** — 10-272 loan applications

### Analytics Engine
- **Overall Summary** — composite score + methodology with business health calculation
- **Transaction Summary** — cashflow, income/expense, inflow/outflow ratios
- **Earnings vs Spendings** — comprehensive financial analysis with 30+ metrics:
  - **Cashflow Metrics**: Inflow/Outflow Ratio, Net Surplus, Surplus Ratio, Income Stability CV, Seasonality Index
  - **Growth Metrics**: Credit Growth Rate, TTM Revenue Growth, QoQ Revenue Growth, Expense Growth Rate, Profit Margin
  - **Credit Scores**: Bounce Count, EMI Consistency, Credit Utilization Ratio, Default Probability Score, Debt-to-Income Ratio, Payment Regularity Score, Loan Repayment Rate
  - **Business Health**: GST vs Bank Reconciliation, Working Capital Gap (days), Annual Operating Cashflow
  - **All metrics include**: Formula, Breakdown with actual dataset values, Risk interpretation
- **GST Summary** — turnover (monthly aggregated to prevent inflation), returns count, state distribution
- **Credit Summary** — bureau score, utilization, open loans
- **Anomaly Detection** — high-value transactions, unusual patterns
- **Mutual Funds Summary** — invested amount, returns, portfolios
- **Insurance Summary** — total coverage, premium paid, policies
- **ONDC Summary** — order volume, provider diversity, category breakdown
- **OCEN Summary** — application count, approval rates, loan amounts

### Frontend Dashboard
- **Lending Analytics & AI Insights** — main view with:
  - Prominent credit score display with click-to-expand component derivations
  - Transaction, GST, ONDC, Mutual Funds, Insurance, OCEN, Anomaly cards
  - Debug panel in GST section (collapsible raw data inspector)
  - AI-generated lending recommendation (formatted with bold/lists)
  - Enter key submit on customer ID input
- **Earnings vs Spendings** — comprehensive financial analysis page:
  - Customer ID prominently displayed at top with generation timestamp
  - Final Assessment moved to top for immediate visibility
  - Positive/Negative indicators count displayed
  - 30+ financial metrics with interactive info buttons
  - Click any ℹ️ button to see: Formula, Breakdown with actual values, Risk explanation
  - Monthly cashflow display with expand/collapse functionality (first 10 items shown)
  - All currency values formatted with thousand separators
- **Credit Methodology** — comprehensive explainability document
- **Credit Calculations** — per-customer numeric examples with simple walkthrough
- **Pipeline Monitor** — live progress bars for generate/clean/analytics/calculate steps:
  - On-demand customer generation — click to generate random customer IDs
  - Real-time execution debugging — shows current step and exact command running
  - Collapsible debug panel — displays pipeline status and steps completed
  - Live logs with timestamps — color-coded by severity (error/warning/success/info)
  - Specialized customer profile selection (High Seasonality, High Debt, Growth, etc.)
- **Dataset Viewer** — raw/clean data inspection with limits

### AI Integration
- **Deepseek API** (primary) — OpenAI-compatible endpoint
- **Google Gemini** (fallback) — robust parsing for varied response shapes
- Automatic fallback if Deepseek fails
- Token limits enforced (prompt + response configurable via env)

### Compliance & Security
- **DPDP Act 2023**: All operations require explicit `customer_id` — no bulk queries
- **RBI AA Framework**: Simulated consent flow and multi-FIP data aggregation
- `.gitignore` excludes raw data files (`data_lake/raw/*.ndjson`)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### 1. Clone Repository
```bash
git clone https://github.com/krishnaheda14/MSMELending.git
cd MSMELending/data_lake
```

### 2. Setup Backend
```bash
# Install Python dependencies
pip install -r requirements.txt

# Create .env file with API keys
echo "DEEPSEEK_API_KEY=sk-553a2062a03e4a88aec97575bd25d268" > .env
echo "GEMINI_API_KEY=your_gemini_key_here" >> .env
```

### 3. Generate Data for a Customer
```bash
# Generate raw data for CUST_MSM_00001
python generate_all.py --customer-id CUST_MSM_00001

# Clean the data
python pipeline/clean_data.py --customer-id CUST_MSM_00001

# Generate analytics
python analytics/generate_summaries.py --customer-id CUST_MSM_00001
```

### 4. Start Backend API
```bash
cd api_panel
python app.py
```
Backend runs at `http://localhost:5000`

### 5. Start Frontend
```bash
cd ../frontend
npm install
npm start
```
Frontend runs at `http://localhost:3000`

### 6. Open Dashboard
- Navigate to `http://localhost:3000`
- Enter customer ID (e.g., `CUST_MSM_00001`) and press **Enter** or click "Load Analytics"
- Click "Get AI Insights" for lending recommendation
- Explore Methodology and Calculations tabs

---

## 📖 Usage Guide

### Generate Data for Multiple Customers

**Option 1: Via Pipeline Monitor UI (Recommended)**
1. Open `http://localhost:3000` → go to **Pipeline Monitor** tab
2. Click **"Generate Random Customer ID"** button (green section at top)
3. A new random customer ID will be assigned (e.g., `CUST_MSM_47832`)
4. Click pipeline steps in order to generate data for that customer:
   - Step 1: Validate Consent & Fetch Data
   - Step 2: Clean & Validate Data
   - Step 3: Generate Analytics & Insights
   - Step 4: Calculate Credit Score
5. **Debug panel** shows real-time execution status and current command being run
6. Repeat to add more customers to your data pool

**Option 2: Via Command Line**
```bash
# Customer 1
python generate_all.py --customer-id CUST_MSM_00001
python pipeline/clean_data.py --customer-id CUST_MSM_00001
python analytics/generate_summaries.py --customer-id CUST_MSM_00001

# Customer 2 (will have different random seed → unique data)
python generate_all.py --customer-id CUST_MSM_00002
python pipeline/clean_data.py --customer-id CUST_MSM_00002
python analytics/generate_summaries.py --customer-id CUST_MSM_00002
```

**Important**: Each `customer_id` is hashed to seed the random number generator, ensuring reproducible yet distinct data per customer. You **must run the full pipeline** (generate → clean → analytics) for each new customer to get unique raw data.

### Run Full Pipeline via UI
1. Open `http://localhost:3000`
2. Go to **Pipeline Monitor** tab
3. Enter customer ID (required)
4. Click pipeline steps in order:
   - Step 1: Generate Data
   - Step 2: Clean Data
   - Step 3: Generate Analytics
   - Step 4: Calculate Credit Score

### Debug Data Issues
- Use **Show Debug** button in GST & Business Insights section to inspect raw data structure
- Check `logs/` directory for validation errors and cleaning logs
- Inspect `raw/` vs `clean/` NDJSON files in Dataset Viewer tab

---

## 🧪 Testing & Verification

### Test Credit Score Calculation
```bash
curl -X POST http://localhost:5000/api/pipeline/calculate_score \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"CUST_MSM_00001"}'
```

### Test Analytics Endpoint
```bash
curl "http://localhost:5000/api/analytics?customer_id=CUST_MSM_00001"
```

### Test AI Insights
```bash
curl -X POST http://localhost:5000/api/ai-insights \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"CUST_MSM_00001"}'
```

---

## 📂 Project Structure

```
MSMELending/
├── data_lake/
│   ├── generators/              # Synthetic data generators
│   │   ├── generate_banking_data.py
│   │   ├── generate_additional_data.py  (GST, Credit Bureau)
│   │   ├── generate_insurance_mf.py
│   │   ├── generate_ondc_ocen.py
│   │   └── indian_data_utils.py
│   ├── pipeline/
│   │   └── clean_data.py        # Data cleaning & validation
│   ├── analytics/
│   │   └── generate_summaries.py  # Analytics engine
│   ├── api_panel/
│   │   └── app.py               # Flask API + SocketIO
│   ├── frontend/
│   │   └── src/
│   │       ├── components/
│   │       │   ├── AnalyticsInsights.js  (main dashboard)
│   │       │   ├── CreditMethodology.js  (explainability doc)
│   │       │   ├── CreditCalculations.js (numeric examples)
│   │       │   ├── PipelineMonitor.js
│   │       │   ├── DatasetViewer.js
│   │       │   └── Sidebar.js
│   │       └── App.js
│   ├── schemas/                 # JSON schemas for validation
│   ├── docs/                    # Documentation
│   ├── raw/                     # Raw NDJSON data (gitignored)
│   ├── clean/                   # Cleaned NDJSON data (gitignored)
│   ├── analytics/               # Analytics JSON summaries (gitignored)
│   ├── logs/                    # Validation error logs (gitignored)
│   ├── config.json              # Generation config
│   ├── generate_all.py          # Master generator orchestrator
│   ├── requirements.txt
│   └── README.md
└── README.md                    # This file
```

---

## 🔧 Configuration

### Scale Settings (`data_lake/config.json`)
```json
{
  "scale": {
    "users": 10000,
    "bank_accounts": 15000,
    "transactions": 50000
  },
  "messiness_config": {
    "date_format_variation": true,
    "numeric_format_inconsistency": true,
    "missing_field_probability": 0.05,
    "duplicate_probability": 0.02
  }
}
```

### AI Provider Keys (`data_lake/.env`)
```bash
DEEPSEEK_API_KEY=sk-553a2062a03e4a88aec97575bd25d268
GEMINI_API_KEY=your_gemini_key_here
MAX_AI_PROMPT_TOKENS=1500
MAX_AI_RESPONSE_TOKENS=1500
```

---

## 🚧 Known Limitations & Future Enhancements

### Current Limitations
1. **Anomaly detection** is rule-based (1st-pass logic) — not ML-based
2. **GST/OCEN/MF/Insurance** analyzers have partial `calculation` metadata parity (transactions/credit/ONDC fully implemented)
3. **AI insights** subject to provider token limits (may truncate context for large datasets)
4. **Synthetic data only** — not connected to real AA/FIP providers

### Planned Enhancements
- ML-based anomaly detection (isolation forest, autoencoders)
- Richer calculation metadata across all analyzers
- Real AA integration (replace synthetic generators)
- Time-series forecasting for cashflow prediction
- Interactive risk matrix charts
- Multi-language support (Hindi, regional languages)

---

## 📚 Documentation

- **[data_lake/README.md](data_lake/README.md)** — detailed project documentation
- **[data_lake/docs/CUSTOMER_LENDING_FLOW.md](data_lake/docs/CUSTOMER_LENDING_FLOW.md)** — lending journey walkthrough
- **[data_lake/docs/data_dictionary.md](data_lake/docs/data_dictionary.md)** — field-level data documentation
- **[data_lake/FLOW.md](data_lake/FLOW.md)** — pipeline execution flow diagram

---

## 🤝 Contributing

This is a demo/prototype project. For production use:
1. Replace synthetic data generators with real AA connectors
2. Implement proper authentication & authorization
3. Add audit trails and compliance logging
4. Deploy backend/frontend with HTTPS
5. Set up database for persistent storage (currently file-based)
6. Add comprehensive test coverage

---

## 📄 License

MIT License — Free to use for educational and commercial purposes.

---

## 🙏 Acknowledgments

Built with adherence to:
- **RBI Account Aggregator Framework** (Master Directions)
- **Digital Personal Data Protection Act (DPDP) 2023**
- **GSTN API** specifications
- **ONDC Beckn Protocol** standards
- **OCEN lending protocol**

---

## 📧 Contact

- **GitHub**: [krishnaheda14/MSMELending](https://github.com/krishnaheda14/MSMELending)
- **Issues**: Open an issue on GitHub for bugs or feature requests

---

**Built for the future of MSME lending in India. 🚀**
