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

## Broader context — Account Aggregator and who consumes this
The original project goal targets banks and NBFCs who receive customer-permissioned financial data via Account Aggregator (AA) flows or similar banking/aggregator extracts. In production this data is the authoritative source of transactions, balances and account metadata for an MSME. Our pipeline is designed to take that AA/bank-transaction feed (plus complementary sources such as GST returns, marketplace orders, OCEN loan apps, mutual fund and insurance data) and produce per-customer, explainable signals that underwrite lending decisions.

In short: AA / bank transactions are the primary raw source; our project normalizes and enriches those records with GST, ONDC, OCEN, MF and insurance files, computes robust, auditable metrics and exposes them (JSON + UI) so credit teams at banks/NBFCs can review and act.

## Implementation, tools & technologies used
- Language & runtime: Python 3 (data ingestion, parsers, metrics, JSON generation).
- Frontend: React (single-page front-end under `data_lake/frontend`) with Tailwind CSS, Recharts and small UI components. The frontend consumes per-customer JSON produced by analytics and offers info (i) buttons, modals and raw‑entry views for audit.
- Data format: NDJSON for raw input fixtures (`data_lake/raw/*.ndjson`) and per-customer JSON outputs (`data_lake/analytics/*_*.json`).
- Key libraries / utilities: lightweight Python scripts for parsing & aggregation, small helper modules for formatting and date-normalization. (See `requirements.txt` in `data_lake/`.)
- Orchestration: ad-hoc runner scripts (`generate_summaries.py`, `run_fullstack.bat`) to regenerate analytics per-customer; generator scripts produce deterministic, profile-aware test data.

## End-to-end flow (how we work on the solution)
1. Ingest: ingest Account Aggregator / bank transaction dumps (NDJSON) and related files (GST returns, ONDC orders, OCEN applications, mutual funds, insurance). Files live in `data_lake/raw/` in repo workflows and are parsed by tolerant parsers.
2. Normalize: normalize field names and timestamps, convert dates to YYYY-MM for monthly aggregations, and map multiple schema variants (e.g., `total_amount` | `order_value` | `quote.price`).
3. Scope: filter or attribute records to the target customer where possible; avoid over-attribution (skip unscoped GST unless clearly mapped) to prevent inflated scores.
4. Compute metrics: derive cashflow (monthly inflow/outflow, CV, seasonality), revenue base (GST or bank credits using preference rules and a GST–Bank variance threshold), growth (CAGR when multi-year, TTM, or short-window otherwise), reconciliation pct (capped at 100%), credit signals (EMI/loan detection, bounce counts, DTI, EMI consistency), ONDC/MF scoring (amount-based, bucketed), concentration and state diversity.
5. Compose scores: aggregate component-level scores into `business_health`, `debt_capacity` (deterministic composite with numeric breakdown), and `composite_credit_score` using explicit weights. All component calculations include a `calculation` metadata object with formula, breakdown and sample transactions.
6. Publish: write per-customer JSON outputs (separate files for transaction_summary, gst_summary, earnings_spendings, overall_summary, etc.) consumed by the UI and downstream APIs.
7. UI & audit: React UI loads per-customer JSON and surfaces metrics with info (i) buttons that show the formula, numeric breakdown and sample raw transactions (`top_10_expenses`, `unknown_samples`, per-metric `sample_transactions`) to help manual reviewers validate decisions.

## Functionalities implemented (concise)
- Profile-aware synthetic data generation (`generate_profile_aware_data.py`) and isolated profile applier (`apply_profile.py`) so each customer is realistic and independent.
- Robust parsers for multiple source schemas: ONDC (`total_amount`/`order_value`/`quote.price`), OCEN (`requested_amount`/`approved_amount`), MF (`current_value`), insurance policies.
- Revenue selection rules: prefer GST series when scoped and reliable; fall back to bank credits when GST–Bank variance exceeds a threshold (configurable).
- Growth metrics: use CAGR for multi-year series, TTM/CAGR fallbacks, and short-window comparisons where appropriate.
- Reconciliation: compute `reconciliation_pct_of_gst` capped at 100% and expose it with explanation strings.
- ONDC & MF scoring: bucketed, amount-based scoring relative to annual revenue or monthly obligations; provider diversity and top-providers extracted.
- Concentration & diversity: top‑5 customer share, state diversification score and human-friendly explanations.
- Debt & credit signals: deterministic `debt_capacity` with `debt_capacity_breakdown` (credit component, DTI component, OCEN approval, insurance, repayment regularity), EMI detection heuristics, `emi_consistency_score`, `debt_to_income_ratio`, and explicit `debt_capacity_explanation`.
- Explainability: every metric publishes `calculation` metadata (formula, breakdown, sample transactions). UI info buttons and the new "Show raw entries" controls show `top_10_expenses`, `unknown_samples` and raw transactions used in calculations.
- Export & integration: per-customer JSON artifacts intended for programmatic consumption by downstream services, underwriting pipelines, or auditing tools.

## How this maps to bank / NBFC needs
- Fast reviewer workflows: i-buttons and raw-entry modals give underwriting teams immediate traceability from score → formula → raw transactions.
- Deterministic decisions: debt capacity and composite scoring use deterministic, explainable formulas useful for policy and audit trails.
- Data governance: scoping rules (avoid unscoped GST attribution) reduce false positives and provide conservative defaults for initial credit decisions.

## Current limitations & recommended next steps
- Broaden EMI/loan detection: add regexes and merchant mappings to reduce false-zero loan metrics (we currently detect EMI/loans from narration keywords and may miss bank‑specific formats).
- Calibration: tune bucket thresholds and weights using labeled historical defaults or A/B synthetic cohorts.
- Integration: wire outputs to a simple API or webhook for lenders to pull per-customer JSON, and add logging for change tracking/approval.
- Productionizing: containerize the analytics runner, add automated tests, and instrument monitoring for upstream schema drift.

## Files of interest (implementation entry points)
- `data_lake/analytics/generate_summaries.py` — orchestration & aggregations; writes per-customer JSON.
- `data_lake/analytics/financial_metrics.py` — core metric calculations (CAGR, cashflow stability, profit margins, reconciliation logic).
- `data_lake/generate_profile_aware_data.py`, `data_lake/apply_profile.py` — data generation and profile isolation.
- `data_lake/frontend/` — React UI that loads artifacts and exposes calculation + raw-transaction views.
- `data_lake/raw/` — raw NDJSON fixtures used to test and demonstrate the pipeline.

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
