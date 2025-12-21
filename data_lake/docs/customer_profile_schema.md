# Customer profile — stored information

Location: `analytics/` — files named `CUST_MSM_<id>_<report>.json` (one JSON per report type per customer).

This document summarizes the exact information stored in each customer profile report file found under `analytics/`.

## Common top-level fields
- `customer_id`: string — canonical customer identifier (e.g., `CUST_MSM_00001`).
- `generated_at`: ISO timestamp when the summary was produced.

## Report types and fields

### overall_summary.json
- `total_records`: integer — raw input records processed.
- `datasets_count`: integer — number of dataset types present.
- `total_accounts`: integer — number of bank/accounts aggregated.
- `datasets`: object — counts per dataset (transactions, gst_returns, credit_reports, mutual_funds, insurance, ocen_applications, ondc_orders).
- `scores`: object — numeric scores such as `cashflow_stability`, `business_health`, `debt_capacity`, `overall_risk_score`.
- `debt_capacity_breakdown`: object — numeric components (base_floor, credit_component, repayment_bonus, dti_component, ocen_component, insurance_component, regularity_bonus, sum_raw, final_debt_capacity).
- `debt_capacity_explanation`: string — human readable explanation of debt calculation.
- `business_health_contributors`: object — contributors like `gst_businesses`, `gst_turnover`, `ondc_provider_diversity`, `mutual_fund_portfolios` and a `calculation_breakdown` string.
- `reconciliation_pct_of_gst`, `concentration_explanation`, `score_methodology` (includes `composite_formula`, `weights`, derivations), and `recommendation`.

### transaction_summary.json
- `total_transactions`, `total_amount`, `average_transaction`.
- `by_type`: map (UNKNOWN/DEBIT/CREDIT) with `count` and `total_amount` per type.
- `unknown_type_breakdown`: map of raw narration/category -> counts to show where classification failed.
- `unknown_samples`: array of sample raw transactions (date, amount, merchant, narration).
- `monthly_cashflow`: array of `{month, income, expense}` summarized per month.
- `amounts_stats`: stats for numeric amounts (`count`, `mean`, `std`, `cv`).
- `calculation`: debug fields (transactions_counted, transactions_with_amount, total_amount_sum, explanation).

### earnings_spendings.json
- `cashflow_metrics`: object containing `total_inflow`, `total_outflow`, `net_surplus`, `surplus_ratio`, `inflow_outflow_ratio`, `income_stability_cv`, `seasonality_index`, `top_customer_dependence` and `top_customers` array (`name`, `amount`).
- `monthly_inflow` (map) and other time-series used for seasonality and stability analyses.
- Additional breakdowns of inflow/outflow categories may be present.

### credit_summary.json
- `bureau_score`: numeric credit bureau score.
- `open_loans`: integer count of open credit facilities.
- `total_outstanding`: numeric sum of outstanding balances.
- `credit_utilization`: percentage.
- `payment_history`: qualitative description (e.g., `Good`).
- `calculation`: debug/source fields (reports_counted, bureau_score_source, explanation).

### gst_summary.json
- `returns_count`: integer — number of GST returns processed.
- `monthly_periods`: integer — months covered.
- `annual_turnover`, `total_businesses`, `total_revenue`, `average_revenue`.
- `monthly_gst_turnover`: map period -> turnover.
- `by_state`: breakdown by mapped state with `returns` and `turnover`.
- `mapping_debug`: array of per-return mapping entries (`gstin`, `mapped_state`, `turnover`, `period`).
- `compliance_score`, `calculation` (fields used and notes), `fraud_detected` flag.

### anomalies_report.json
- `total_anomalies`: integer.
- `anomalies`: array of anomaly objects with `type` (e.g., `high_value_transactions`), `count`, `severity`, `top_transactions` (summaries), and `transactions` (detailed items). Each transaction entry contains raw fields: `transaction_id`, `account_id`, `date`, `timestamp`, `type`, `amount`, `currency`, `mode`, `balance_after`, `narration`, `reference_number`, `merchant_name`, `category`, and `_numeric_amount`.
- `fraud_detected`: boolean.

### insurance_summary.json
- Typical fields: `policies_count`, `total_coverage_amount`, `active_policies` (array of policy summaries), `premium_summary`, and `calculation` details. (Schema may vary; check file per customer.)

### mutual_funds_summary.json
- Typical fields: `holdings_count`, `total_value`, `holdings` (array with `scheme`, `units`, `nav`, `current_value`), and simple performance snapshots.

### ocen_summary.json
- Typical fields: `applications_count`, `approved_count`, `approval_rate`, `approved_amounts`, and per-application entries (application_id, status, amount). May be empty for customers without OCEN interactions.

### ondc_summary.json
- Typical fields: `orders_count`, `orders_value`, `provider_diversity`, and sample `orders` list (order_id, date, amount, provider).

## Notes about variability
- Not every customer has every report type; `datasets` in `overall_summary.json` indicates presence counts.
- Field-level presence/shape may vary (e.g., `monthly_inflow` keys may have inconsistent date formats). Many summaries include a `calculation` or `mapping_debug` object explaining sources and heuristics.
- Numeric fields may be floats or strings in raw transaction records; summaries normalize them to numeric fields such as `_numeric_amount` where appropriate.

## Next steps (for per-customer differences)
- To produce a per-customer detailed diff of parameter values and differing fields we can:
  1. Enumerate customers and report files present.
  2. For each report type, extract canonical field sets and types.
  3. Compare field presence and key configuration values (e.g., `scores`, `weights`, `composite_formula`, `compliance_score` thresholds) across customers and surface differences.

---
Generated by analysis of `analytics/CUST_MSM_00001_*.json` files.
