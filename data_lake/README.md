# MSME Lending Solution — Indian Financial Data Lake

## 🎯 Problem Statement

**Challenge**: Traditional MSME lending in India faces critical barriers:
- **Manual, paper-heavy credit assessment** leads to weeks-long approval cycles
- **Single-source bureau scores** (CIBIL) miss 70% of the real financial picture
- **No unified view** of banking, GST, insurance, mutual funds, ONDC, OCEN data
- **DPDP Act 2023** mandates explicit per-customer consent — bulk data operations now prohibited
- **RBI Account Aggregator Framework** requires standardized multi-FIP data fetching

**Business Impact**:
- 50+ day average loan turnaround for MSMEs
- 40% rejection rate due to incomplete financial visibility
- Manual underwriting prone to bias and errors
- Cannot scale to millions of MSME borrowers

---

## 💡 Our Proposed Solution

A **comprehensive MSME credit decisioning platform** leveraging:

### 1. **Account Aggregator (AA) Framework Integration**
- **One Borrower → One Consent → One Dataset**
- Compliant with RBI AA specs and DPDP Act 2023
- Fetch multi-source financial data: Banking, GST, Bureau, Insurance, MF, ONDC, OCEN

### 2. **AI-Powered Multi-Source Analytics**
- **7 data sources** aggregated per customer (vs. traditional 1-2)
- **Automated cashflow analysis**, GST compliance scoring, anomaly detection
- **Composite credit scoring** combining:
  - **Cashflow Stability** (45% weight) — transaction patterns, income/expense ratios
  - **Business Health** (35% weight) — GST turnover, ONDC order diversity, MF investments
  - **Debt Capacity** (20% weight) — credit utilization, OCEN approval rate, insurance coverage

### 3. **Explainable AI & Transparency**
- Click-to-reveal calculation breakdowns for every metric
- Separate **Methodology** and **Calculations** tabs showing real numbers and formulas
- Debug panels in charts for raw data inspection

### 4. **End-to-End Pipeline Automation**
- Generate → Clean → Analytics → AI Insights → Credit Score → Decision
- Real-time WebSocket progress tracking
- Per-customer data isolation (no bulk operations)

---

## 🏗️ Implementation

### Architecture

```
┌─────────────────┐
│  Customer       │  Step 1: Grant consent via AA app
│  (MSME Borrower)│─────────────────────────────┐
└─────────────────┘                              │
                                                 ▼
┌──────────────────────────────────────────────────────┐
│  AA Aggregator (simulate with synthetic data gen)   │
│  • Banking (Accounts & Transactions)                 │
│  • GST (GSTR-1, GSTR-3B)                             │
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
│  2. Generate Analytics (7 summaries + 1 overall)     │
│  3. AI Insights (Deepseek/Gemini - lending reco)     │
│  4. Calculate Credit Score (composite weighted)      │
└──────────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│  Frontend Dashboard                                  │
│  • Lending Analytics & AI Insights (main view)       │
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
- Per-customer seeding (hash of `customer_id` → unique deterministic data)
- Configurable messiness (date format variation, missing fields, duplicates)

---

## ✨ Features Implemented

### Data Sources (Per Customer)
1. **Consent Artefacts** — RBI AA Framework digital consent
2. **Banking** — 2-5 accounts, 500-5000 transactions (6-12 months)
3. **GST Returns** — 12-24 returns (GSTR-1, GSTR-3B)
4. **Credit Bureau** — 1-4 reports (CIBIL/Experian-style, DPD grids)
5. **Insurance** — 0-3 policies (Life, Health, Vehicle)
6. **Mutual Funds** — 0-10 holdings (AMC, SIPs)
7. **ONDC Orders** — 100-2000 orders (Beckn protocol, for sellers)
8. **OCEN Applications** — 10-50 applications (loan history)

### Analytics Engine
- **Overall Summary** — composite score + methodology
- **Transaction Summary** — cashflow, income/expense, avg amounts (with `calculation` metadata)
- **GST Summary** — turnover, returns count, state distribution
- **Credit Summary** — bureau score, utilization, open loans (with `calculation` metadata)
- **Anomaly Detection** — high-value txns, unusual patterns (1st-pass logic)
- **Mutual Funds Summary** — invested amount, returns, portfolios
- **Insurance Summary** — total coverage, premium paid, policies
- **OCEN Summary** — approval rate, funded amount
- **ONDC Summary** — provider distribution, order counts, total GMV (with `calculation` metadata)

### Frontend Dashboard
- **Lending Analytics & AI Insights** — main view with:
  - Prominent credit score display with click-to-expand component derivations
  - Transaction, GST, ONDC, Mutual Funds, Insurance, OCEN, Anomaly cards
  - **Debug panel** in GST section (collapsible raw data inspector)
  - AI-generated lending recommendation (formatted with bold/lists)
  - **Enter key submit** on customer ID input
- **Credit Methodology** — comprehensive explainability document
- **Credit Calculations** — per-customer numeric examples with simple walkthrough
- **Pipeline Monitor** — live progress bars for generate/clean/analytics/calculate steps
  - **On-demand customer generation** — click to generate random customer IDs and add to data pool
  - **Real-time execution debugging** — shows current step being executed and exact command/script running
  - **Collapsible debug panel** — displays pipeline status, current step, customer ID, and steps completed
  - **Live logs with timestamps** — color-coded by severity (error/warning/success/info)
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

### 1. Clone & Setup Backend
```bash
cd F:\MSMELending\data_lake

# Install Python dependencies
pip install -r requirements.txt

# Create .env file with API keys
echo "DEEPSEEK_API_KEY=sk-553a2062a03e4a88aec97575bd25d268" > .env
echo "GEMINI_API_KEY=your_gemini_key_here" >> .env
```

### 2. Generate Data for a Customer
```bash
# Generate raw data for CUST_MSM_00001
python generate_all.py --customer-id CUST_MSM_00001

# Clean the data
python pipeline/clean_data.py --customer-id CUST_MSM_00001

# Generate analytics
python analytics/generate_summaries.py --customer-id CUST_MSM_00001
```

### 3. Start Backend API
```bash
cd api_panel
python app.py
```
Backend runs at `http://localhost:5000`

### 4. Start Frontend
```bash
cd ../frontend
npm install
npm start
```
Frontend runs at `http://localhost:3000`

### 5. Open Dashboard
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

**Note**: Each `customer_id` is hashed to seed the random number generator, ensuring reproducible yet distinct data per customer.

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

### Scale Settings (`config.json`)
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

### AI Provider Keys (`.env`)
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

### Planned Enhancements
- ML-based anomaly detection (isolation forest, autoencoders)
- Richer calculation metadata across all analyzers
- Real AA integration (currently simulated)
- Time-series forecasting for cashflow prediction
- Interactive risk matrix charts

---

## 📚 Documentation

- **[CUSTOMER_LENDING_FLOW.md](docs/CUSTOMER_LENDING_FLOW.md)** — detailed lending journey walkthrough
- **[data_dictionary.md](docs/data_dictionary.md)** — field-level data documentation
- **[FLOW.md](FLOW.md)** — pipeline execution flow diagram

---

## 🤝 Contributing

This is a demo/prototype project. For production use:
1. Replace synthetic data generators with real AA connectors
2. Implement proper authentication & authorization
3. Add audit trails and compliance logging
4. Deploy backend/frontend with HTTPS
5. Set up database for persistent storage (currently file-based)

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

---

**For questions or support**: Open an issue on GitHub or contact the maintainers.
