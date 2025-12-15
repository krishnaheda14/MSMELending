# Problem Statement, Rationale & Domain-Driven Approach

## Problem Statement
Small-business lending decisions require consolidating noisy, heterogeneous data (bank transactions, GST returns, marketplace orders, loan applications, investment and insurance records). Challenges:
- Data is unscoped and large (shared GST files, inconsistent field names). 
- Key signals (revenue, cashflow, loan repayments, investments) are represented differently across sources.
- Existing heuristics (short-window growth, raw counts) produce misleading scores when records are multi-year or unspecific.

Goal: build a reproducible analytics pipeline that generates per-customer, explainable credit signals and lending recommendations that are:
- realistic per-customer (profile-aware synthetic generation),
- robust to schema variants, and
- auditable (each score broken down to the exact fields and rules used).

## Why this solution
- Automated per-customer generation and profile isolation prevents one-customer edits from corrupting others.
- Prefer conservative attribution (skip unscoped GST returns) unless per-record customer ids exist — avoids inflating scores.
- Use domain-specific baselines (GST returns baseline, MF vs PAT/obligations, ONDC vs revenue) rather than blind percentile rules.
- Provide transparent breakdowns (component scores + numeric breakdowns) to help underwriting and manual reviewers.

## Approach Overview
1. **Profile-aware Data Generation**
   - Generate per-customer raw NDJSON for transactions, GST, ONDC, OCEN, MF, insurance using `generate_profile_aware_data.py` and `apply_profile.py` to simulate business types (declining, seasonal, high-debt).
2. **Robust Parsers & Field Normalization**
   - Parsers accept multiple field names (e.g., `total_amount`, `order_value`, `quote.price`) for ONDC; `loan_amount`, `approved_amount` for OCEN; `current_value` for MF.
   - Normalized dates to YYYY-MM for monthly aggregations and CAGR calculations.
3. **Metrics & Heuristics**
   - Cashflow: monthly credits/debits, income stability (CV), seasonality index.
   - Revenue: use GST monthly series when GST is reliable; otherwise use bank credits. Preference rule: switch if GST–Bank variance > threshold.
   - Revenue growth: use CAGR when multi-year, else 3‑month average comparisons.
   - Reconciliation: show single `GST–Bank Variance % of GST` (capped & explained).
   - Debt signals: detect EMIs/loan repayments via narration patterns, compute credit_utilization_ratio, DTI, EMI consistency, bounce count.
4. **Scoring Design**
   - Business Health is composed of: GST Compliance (30), Revenue Scale (20), ONDC (15), MF (20), Concentration (10), State Diversity (5).
   - ONDC scoring compares provider diversity and order value vs annual revenue or bank credits (bucketed thresholds).
   - MF scoring compares MF current value to avg monthly obligations or requested loan amount (bucketed), not only PAT.
   - Debt Capacity is derived deterministically from credit risk components (default probability, DTI, OCEN approvals, insurance cover, payment regularity).
5. **Explainability & UI**
   - Each metric includes `calculation` metadata: formula, breakdown, and the raw fields used.
   - i-buttons show `debt_capacity_breakdown`, `concentration_explanation`, and `reconciliation_pct_of_gst` for quick reviewer context.

## How domain knowledge shaped the design
- GST vs Bank: GST measures invoice turnover; bank credits measure cash receipts. We treat them differently and prefer bank when large variance exists.
- ONDC: marketplace orders often correlate to revenue but are partial; scoring uses provider diversity and order value relative to an annual base to avoid small-sample noise.
- Mutual Funds: MF current value is a liquidity buffer; scoring compares it to obligations (months of expenses) and requested loan amounts — practical for lending cushion assessment.
- Debt signals: EMIs and loan repayments appear in narration text; bounces and EMI variability are strong default predictors so we included them explicitly in `default_probability_score`.

## Validation & Next Steps
- Validate thresholds using historical labeled defaults (if available) or A/B experiment using controlled synthetic cohorts.
- Improve counterparty parsing (merchant normalisation, regex mapping) to refine top‑5 concentration metrics.
- Surface UI changes: wire `debt_capacity_breakdown` and `top_10_expenses` into info panels and the expandable expense table.
- Replace remaining random or fallback estimates with deterministic logic as more data arrives.

---

Files of interest: `data_lake/analytics/generate_summaries.py`, `data_lake/analytics/financial_metrics.py`, `data_lake/generate_profile_aware_data.py`, and raw NDJSON files in `data_lake/raw/`.
