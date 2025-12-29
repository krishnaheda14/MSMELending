# Advanced Features - Implementation Guide

This document describes the new advanced features added to the MSME Lending Platform.

## New Features Overview

### 1. Customer Profile Tab ✓
**Location**: Frontend (`/customer-profile`)  
**API Endpoint**: `GET /api/customer-profile?customer_id=CUST_MSM_00001`

A comprehensive view of all customer data aggregated from multiple sources:
- Overview with key metrics and credit scores
- Transaction details and patterns
- GST returns and turnover
- Credit summary and bureau scores
- Earnings & spendings breakdown
- Anomaly detection results
- Mutual funds portfolio
- Insurance policies
- OCEN loan applications
- ONDC marketplace orders

**Usage**:
1. Navigate to "Customer Profile" in the sidebar
2. Enter customer ID or use the default
3. Press Enter or click "Load Profile"
4. Browse through tabs to see detailed data

---

### 2. Explainable Risk Model 🤖
**File**: `analytics/risk_model.py`  
**Output**: `{customer_id}_risk_model.json`

ML-based risk scoring using Random Forest with feature attributions for transparency.

**Features**:
- 31 input features from all data sources
- Binary risk classification (High Risk / Low Risk)
- Per-feature contribution scores (SHAP-style)
- Top risk drivers identification
- Risk score (0-100) with category labels

**Run**:
```bash
cd data_lake/analytics
python risk_model.py CUST_MSM_00001
```

**Output includes**:
- Risk score and probability
- Top 10 risk drivers with impact direction
- All feature contributions
- Human-readable explanation

---

### 3. Cashflow Forecasting 📈
**File**: `analytics/forecasting.py`  
**Output**: `{customer_id}_cashflow_forecast.json`

Short-term cashflow prediction using Holt-Winters exponential smoothing.

**Features**:
- Forecasts inflow, outflow, and surplus for 30-180 days
- Seasonal pattern detection (12-month cycle)
- Scenario analysis (base, optimistic, pessimistic)
- Runway calculation (months until cash runs out)
- Risk assessment with actionable recommendations

**Run**:
```bash
cd data_lake/analytics
python forecasting.py CUST_MSM_00001 . 90  # 90-day forecast
```

**Scenarios**:
- **Base Case**: Current trend continuation
- **Optimistic**: +10% inflow, -5% outflow
- **Pessimistic**: -10% inflow, +10% outflow

---

### 4. GST/Bank/ONDC Reconciliation 🔗
**File**: `analytics/reconciliation.py`  
**Output**: `{customer_id}_reconciliation.json`

Fuzzy matching to link GST invoices, bank credits, and ONDC orders.

**Features**:
- Month-based and amount-based matching
- Reconciliation rate calculation
- Unmatched item identification
- Discrepancy percentage analysis
- Risk flags for low reconciliation rates

**Run**:
```bash
cd data_lake/analytics
python reconciliation.py CUST_MSM_00001
```

**Match Score Components**:
- Month similarity: 40% weight
- Amount similarity: 60% weight
- Match threshold: 50%

---

### 5. Enhanced Anomaly Detection 🚨
**File**: `analytics/enhanced_anomalies.py`  
**Output**: `{customer_id}_enhanced_anomalies.json`

ML-powered anomaly detection using Isolation Forest + statistical change-point detection.

**Features**:
- Transaction-level anomalies (10% contamination rate)
- Change-point detection in monthly cashflow
- Anomaly scores for each flagged transaction
- Risk level assessment

**Run**:
```bash
cd data_lake/analytics
python enhanced_anomalies.py CUST_MSM_00001
```

**Detection Methods**:
- **Isolation Forest**: Detects outlier transactions
- **Statistical Threshold**: Identifies jumps > 2σ in monthly patterns

---

### 6. Credit Product Recommendations 💳
**File**: `analytics/recommendations.py`  
**Output**: `{customer_id}_recommendations.json`

Personalized loan product suggestions based on customer risk profile and financial metrics.

**Products Offered**:
1. **Working Capital Loan** - For day-to-day operations
2. **Invoice Discounting** - Quick liquidity against invoices
3. **Business Expansion Loan** - Long-term growth financing
4. **Overdraft Facility** - Revolving credit line
5. **Equipment Financing** - Asset-backed loans
6. **MSME Emergency Credit** - Fast-track short-term loans

**Run**:
```bash
cd data_lake/analytics
python recommendations.py CUST_MSM_00001
```

**Recommendation Logic**:
- Risk Score ≥75: STRONGLY APPROVE (multiple products)
- Risk Score 60-74: APPROVE (standard terms)
- Risk Score 45-59: CONDITIONAL APPROVAL (additional security)
- Risk Score <45: REFER TO UNDERWRITER (manual review)

---

## Comprehensive Test Suite

**File**: `analytics/test_advanced_features.py`

Tests all advanced features in one go with detailed reporting.

**Run**:
```bash
cd data_lake/analytics
python test_advanced_features.py CUST_MSM_00001
```

**Test Output**:
- Module-wise success/failure status
- Key insights from each module
- Error summary
- Comprehensive test report JSON

**Prerequisites**:
```bash
pip install scikit-learn numpy python-dateutil joblib
```

---

## Installation & Setup

### 1. Install Dependencies
```bash
cd F:\MSMELending\data_lake
pip install -r requirements.txt
```

New dependencies added:
- `scikit-learn==1.3.2` (ML models)
- `joblib==1.3.2` (model persistence)

### 2. Ensure Analytics Data Exists
Before running advanced features, generate analytics for your customer:
```bash
python generate_all.py --customer-id CUST_MSM_00001
python pipeline/clean_data.py --customer-id CUST_MSM_00001
python analytics/generate_summaries.py --customer-id CUST_MSM_00001
```

### 3. Run Test Suite
```bash
cd analytics
python test_advanced_features.py CUST_MSM_00001
```

### 4. Start Backend API (if not running)
```bash
cd api_panel
python app.py
```

### 5. Start Frontend (if not running)
```bash
cd frontend
npm install
npm start
```

Navigate to `http://localhost:3000/customer-profile`

---

## File Structure

```
data_lake/
├── analytics/
│   ├── risk_model.py                 # Explainable ML risk model
│   ├── forecasting.py                 # Cashflow forecasting
│   ├── reconciliation.py              # GST/Bank/ONDC matching
│   ├── enhanced_anomalies.py          # ML anomaly detection
│   ├── recommendations.py             # Credit product recommendations
│   ├── test_advanced_features.py      # Comprehensive test script
│   ├── financial_metrics.py           # (existing)
│   ├── generate_summaries.py          # (existing)
│   └── {customer_id}_*.json           # Output files
├── api_panel/
│   └── app.py                         # + /api/customer-profile endpoint
├── frontend/
│   └── src/
│       ├── App.js                     # + CustomerProfile route
│       └── components/
│           ├── CustomerProfile.js     # NEW: Comprehensive profile view
│           └── Sidebar.js             # + Customer Profile nav item
└── requirements.txt                   # + scikit-learn, joblib
```

---

## API Endpoints

### New Endpoint
```
GET /api/customer-profile?customer_id=CUST_MSM_00001
```

Returns aggregated data from all 10 analytics sources:
- `data_sources.overall`
- `data_sources.transactions`
- `data_sources.gst`
- `data_sources.credit`
- `data_sources.anomalies`
- `data_sources.mutual_funds`
- `data_sources.insurance`
- `data_sources.ocen`
- `data_sources.ondc`
- `data_sources.earnings_spendings`

---

## Data Outputs

All advanced features generate JSON files in `analytics/` directory:

| Module | Output File | Description |
|--------|-------------|-------------|
| Risk Model | `{customer_id}_risk_model.json` | Risk score + feature attributions |
| Forecasting | `{customer_id}_cashflow_forecast.json` | 90-day forecast + scenarios |
| Reconciliation | `{customer_id}_reconciliation.json` | GST/Bank match results |
| Enhanced Anomalies | `{customer_id}_enhanced_anomalies.json` | ML-detected anomalies |
| Recommendations | `{customer_id}_recommendations.json` | Loan product suggestions |
| Test Report | `{customer_id}_advanced_features_test_report.json` | Test summary |

---

## Usage Examples

### Example 1: Full Pipeline for New Customer
```bash
# Generate data
python generate_all.py --customer-id CUST_MSM_00005
python pipeline/clean_data.py --customer-id CUST_MSM_00005
python analytics/generate_summaries.py --customer-id CUST_MSM_00005

# Run advanced features
cd analytics
python test_advanced_features.py CUST_MSM_00005
```

### Example 2: Individual Module Testing
```bash
cd analytics

# Test risk model only
python risk_model.py CUST_MSM_00001

# Test forecasting with 180-day horizon
python forecasting.py CUST_MSM_00001 . 180

# Test reconciliation
python reconciliation.py CUST_MSM_00001
```

### Example 3: Frontend Integration
1. Start backend: `cd api_panel && python app.py`
2. Start frontend: `cd frontend && npm start`
3. Navigate to: `http://localhost:3000/customer-profile`
4. Enter customer ID: `CUST_MSM_00001`
5. Browse all tabs

---

## Troubleshooting

### Missing Dependencies
```bash
pip install scikit-learn joblib numpy python-dateutil
```

### Missing Analytics Files
Run the full pipeline first:
```bash
python generate_all.py --customer-id CUST_MSM_00001
python pipeline/clean_data.py --customer-id CUST_MSM_00001
python analytics/generate_summaries.py --customer-id CUST_MSM_00001
```

### Model Training
Risk model auto-trains on first run (1000 synthetic samples). To retrain:
```python
from risk_model import ExplainableRiskModel
model = ExplainableRiskModel()
model.train_synthetic_model(n_samples=2000)
```

### Frontend Not Loading
1. Check backend is running: `http://localhost:5000/api/customer-profile?customer_id=CUST_MSM_00001`
2. Check CORS is enabled in `api_panel/app.py`
3. Rebuild frontend: `cd frontend && npm run build`

---

## Next Steps

1. **Production Integration**: Replace synthetic training data with real labeled outcomes
2. **API Endpoints**: Expose advanced features via REST APIs for external consumption
3. **Frontend Widgets**: Add forecast charts and risk visualizations to main dashboard
4. **Scheduled Jobs**: Automate daily/weekly forecasts and anomaly checks
5. **Alerting**: Email/SMS alerts for high-risk customers or negative forecasts

---

## Performance Notes

- Risk model training: ~5 seconds (1000 samples)
- Single prediction: <100ms
- Forecast computation: ~1 second (24 months history)
- Reconciliation: ~2 seconds (36 months GST + bank data)
- Enhanced anomalies: ~3 seconds (Isolation Forest on 10k+ transactions)
- Full test suite: ~15-20 seconds

---

## License & Credits

Part of MSME Lending Platform  
MIT License  
© 2025
