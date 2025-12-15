# Tabs & Pages — Feature Summary

This document lists each UI tab/page and a short description of the features available so you can attach screenshots for quick context.

Pipeline Monitor
- **Purpose:** Visualize data ingestion and generation pipelines.
- **Features:** job status (queued/running/failed), last run time, record counts, per-step logs, retry button, quick link to raw NDJSON files, CSV export, and alerts for schema or sample-rate issues.

Analytics & Insights (Customer View)
- **Purpose:** Per-customer analytics dashboard showing finance, compliance and risk.
- **Features:** overview KPI cards (Cashflow, Business Health, Debt Capacity, Risk Recommendation), time-series charts (Revenue, Expenses, TTM/CAGR), reconciliation widget (GST–Bank variance %), component breakdown with i-buttons (explain calculations), and exportable per-customer JSON.

Customer Profile / Master
- **Purpose:** Source of truth for profile attributes and scenario application.
- **Features:** profile attributes (industry, seasonality, growth/decline flags), apply-profile actions (generate isolated customer data), history of profile changes, download generated raw files.

Transactions
- **Purpose:** Raw and parsed transactions explorer.
- **Features:** filter by date/type/amount / merchant, aggregated stats (inflow/outflow), unknown-type inspector (click to show samples), top counterparty list, top-10 expenses table with export.

GST Returns
- **Purpose:** GST return summarization & compliance view.
- **Features:** returns count, monthly series, by-state distribution, fraud indicators list, compliance score, ability to view mapped GSTIN and return_period rows.

ONDC Orders
- **Purpose:** ONDC activity summary for merchant-side data.
- **Features:** total orders/value, provider diversity, top providers list, value vs revenue ratio, provider-level drilldown.

OCEN / Loan Applications
- **Purpose:** Aggregated loan request & approval signals.
- **Features:** total requested vs approved, approval rate, per-application status, inferred credit appetite signal used in debt capacity.

Mutual Funds & Insurance
- **Purpose:** Investment & protection overlays.
- **Features:** MF current value and portfolios, MF vs obligations scoring; insurance total coverage and policy counts; quick ratio metrics (coverage ÷ revenue).

Business Health & Scoring Breakdown
- **Purpose:** Explain composite business score and contributors.
- **Features:** component scores (GST, Revenue Scale, ONDC, Investments, Concentration, State Diversity), human-readable explanation text, `debt_capacity_breakdown` accessible via i-button.

Anomalies & Fraud
- **Purpose:** Highlight suspicious patterns across datasets.
- **Features:** GST fraud indicators, high-value transactions, payment bounces, irregular seasonality, downloadable anomaly reports.

Lending Decision / Recommendation
- **Purpose:** Summarize lending stance with reasoning.
- **Features:** recommendation (APPROVE / APPROVE WITH CONDITIONS / MANUAL REVIEW / REJECT), positives/negatives, score methodology snippet, link to full JSON evidence.

Admin / Settings
- **Purpose:** Configure sampling rates, GST baseline, and scoring thresholds.
- **Features:** environment toggles, regenerate dataset actions, set `GST_UNRELIABLE_THRESHOLD_PCT`, sampling limits, and metric weight adjustments.

Developer Tools
- **Purpose:** For engineers to trace pipeline and regenerate datasets.
- **Features:** run scripts, view patch notes, regenerate specific customer analytics, debug logs, and unit test runners.

Notes
- Each screen includes small i-buttons explaining formulas and verifiable inputs (which raw file and field produced that number).
- All tables and charts support CSV/JSON export for offline review.
