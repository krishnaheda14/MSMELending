# MSME Lending Solution — Indian Financial Data Lake

## 🎯 Problem Statement

**Challenge**: Traditional MSME lending in India faces critical barriers:
- **Manual, paper-heavy credit assessment** leads to weeks-long approval cycles
- **Single-source bureau scores** (CIBIL) miss 70% of the real financial picture
- **No unified view** of banking, GST, insurance, mutual funds, ONDC, OCEN data
- **DPDP Act 2023** mandates explicit per-customer consent — bulk data operations now prohibited
- **RBI Account Aggregator Framework** requires standardized multi-FIP data fetching


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
echo "DEEPSEEK_API_KEY=sk-your deepseek key here" > .env
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
