# Profile Parameters — Exact Modifiers Applied Per Customer

This document lists the exact code-level parameters and values applied to each customer profile (via `apply_profile.py`) that produce behaviors such as High Growth, High Debt, High Seasonality, Declining, etc.

Notes:
- Values below are taken directly from `data_lake/apply_profile.py` (modification functions) and the regeneration mapping in `COMPLETE_DATA_FIX_SUMMARY.md`.
- Randomized ranges use `random.uniform(a, b)` unless otherwise stated; where iteration-based factors are used the exact formulas are shown.

---

## Per-Customer Profile Assignments
(From regeneration script mapping)

- CUST_MSM_00001: Baseline (no modification)
- CUST_MSM_00002: `high_seasonality`
- CUST_MSM_00003: `high_debt`
- CUST_MSM_00004: `high_growth`
- CUST_MSM_00005: `stable_income`
- CUST_MSM_00006: `high_bounce`
- CUST_MSM_00007: `declining`
- CUST_MSM_00008: `customer_concentration`
- CUST_MSM_00009: `high_growth` (second instance)
- CUST_MSM_00010: `high_seasonality` (second instance)

---

## Exact Parameter Details (function-level)
All function names below are in `data_lake/apply_profile.py`.

### `modify_transactions_for_high_seasonality(transactions)`
- Groups transactions by month (key: `txn['date'][:7]`), sorts months.
- For each month index `i`:
  - If `i % 3 == 0` (peak months): `multiplier = random.uniform(3.0, 5.0)`
  - If `i % 3 == 1` (medium months): `multiplier = random.uniform(0.8, 1.2)`
  - Else (low months): `multiplier = random.uniform(0.2, 0.4)`
- Applies multiplier only to credit-type transactions (types matched: `'CREDIT','CR','C','DEPOSIT'`).

Impact: peak months see 3–5× credits; troughs 0.2–0.4× — produces high seasonality index and high income CV.


### `modify_transactions_for_high_debt(transactions)`
- Creates new debt transactions equal to `len(transactions) // 10` (10% more debt txns).
- For each new debt txn:
  - `amount = random.uniform(15000, 50000)`
  - `type = 'DEBIT'`, `category = 'LOAN_REPAYMENT'`
  - `description` and `narration` randomly chosen from loan-related strings
  - `balance = random.uniform(50000, 500000)`
- Appends these transactions to the customer's list.

Impact: increases number and volume of repayments; raises Debt Servicing Ratio and loan-related metrics.


### `modify_transactions_for_high_growth(transactions)`
- Parses transaction dates (using `dateutil.parser.parse`) and sorts transactions by actual date.
- For sorted credits (same credit-type matching as above), computes:
  - `length = max(1, len(sorted_txns))`
  - `growth_factor = 0.3 + ((i / length) * 2.7)` where `i` is index in sorted list.
    - This yields approximate multipliers from ~0.3 (earliest) to ~3.0 (latest).
- Replaces `txn['amount'] = original_amount * growth_factor` for credits.

Impact: produces a strong upward revenue trend (roughly 10× spread early→late), used to compute CAGR and TTM growth.


### `modify_transactions_for_stable_income(transactions)`
- Computes per-month average credit (mean credit per month).
- `avg_credit` = overall mean of monthly averages (fallback `50000` if none).
- For each credit txn: `txn['amount'] = avg_credit * random.uniform(0.95, 1.05)` (±5% noise).

Impact: very low CV (income stability CV < ~15%), low seasonality.


### `modify_transactions_for_high_bounce(transactions)`
- For each debit-type txn, with probability `0.07` (7%) mark it as failed:
  - `txn['status'] = 'FAILED'`
  - `txn['failure_reason']` set from a shortlist (`INSUFFICIENT_FUNDS`, `PAYMENT_DECLINED`, `ACCOUNT_BLOCKED`)
  - Append ` - BOUNCE` to `narration` / `description`.

Impact: produces ~7% failed debits; increases `bounce_count` and lowers EMI consistency.


### `modify_transactions_for_declining_business(transactions)`
- Parses dates and sorts by date (like growth modifier).
- For sorted credits, computes:
  - `length = max(1, len(sorted_txns))`
  - `decline_factor = 1.5 - (i / length) * 1.3` (intent: 1.5 → ~0.2 across timeline)
  - Applies `txn['amount'] = original_amount * max(0.2, decline_factor)`

Notes: `max(0.2, decline_factor)` prevents negative/zero multipliers; effective multiplier range: 0.2 — 1.5.

Impact: creates reducing credit amounts over time — negative TTM/QoQ growth, 'decreasing' surplus trend.


### `modify_transactions_for_customer_concentration(transactions)`
- Collects credit txns and selects ~70% (`major_count = int(len(credit_txns) * 0.7)`) to be from 3 major customers.
- For selected txns:
  - Set `counterparty_account` / `merchant_name` to `MajorClient-0XX` (one of three)
  - Multiply `amount` by `random.uniform(1.5, 3.0)`

Impact: top-customer dependence >70%; increases customer concentration metrics.


---

## Additional System/Generator Changes That Affect Outcomes
These are not per-customer modifiers, but global code changes that affect how the behavior appears in analytics:

1. `apply_profile()` isolation fix (critical)
   - Prior behavior: `apply_profile` modifications overwrote the whole `raw_transactions.ndjson` dataset, affecting all customers.
   - New behavior (exact): load all transactions, split into `customer_transactions = [t for t in all_transactions if t.get('customer_id') == customer_id]` and `other_transactions = [...]`, apply modifications only to `customer_transactions`, then save `other_transactions + customer_transactions` back. This isolates effects to the single customer.

2. `generate_summaries.py` dataset filtering (note: we patched this during investigation)
   - Original helper filtered only on exact matches of `customer_id`/`user_id`/`account_customer_id`.
   - Patch adds substring-matching for `user_id`/`account_customer_id` variants (e.g. `USER_CUST_MSM_00010`) and prints debug counts. This increases robustness when `user_id` contains the customer id.

3. `generate_summaries.py` GST sampling
   - By default, GST file is loaded with `max_records = GST_SAMPLE_LIMIT` (default 5000). If the dataset contains no per-record `customer_id`/`user_id` keys, generator considers the dataset *not customer-scoped* and uses the full file (leading to inflated counts if raw_gst isn't per-customer).

---

## Why `CUST_MSM_00007` Appears "Declining" in Labels but Shows Strong Revenue Numbers in the Financial Summary (diagnosis)

Short answer: inconsistent data sources — `transactions` vs `GST` — and the generator's filtering rules.

Detailed reason:
- `apply_profile` applied the `declining` modifier to `CUST_MSM_00007`'s transactions (this reduces credit amounts over time via `decline_factor`). The transaction-derived analytics (e.g., `earnings_spendings`, `transaction_summary`) therefore reflect declining or modest transaction volumes.
- However, `generate_summaries.py` also ingests GST returns from `raw_gst.ndjson` with `GST_SAMPLE_LIMIT=5000` (default); the GST NDJSON file in this demo does not contain a per-record `customer_id` (it represents many GST returns across many businesses).
- The generator's filtering helper historically returns the full GST dataset if records don't contain customer_id/user_id keys (i.e., it assumes dataset is not customer-scoped). Therefore `CUST_MSM_00007`'s `gst_summary` shows 5,000 returns and ₹40,515,976,984 annual turnover — the full file — which massively inflates the `business_health` score.
- The UI/decision logic combines `cashflow_stability`, `business_health`, and `debt_capacity` to produce composite labels (`business_health` had high weight). Because `business_health` is computed using the unfiltered GST dataset, it reports high revenue scale and thus may show conflicting messaging.

Practical implication: the Financial Summary cards you attached (revenue, net profit, CAGR) are driven by transaction-based metrics (which are correct for the single customer after `apply_profile`), but the high `GST` figures in `overall_summary` (and the derived `business_health` 55/100) come from the unfiltered GST file — creating a mismatch.

---

## Recommended Fixes (short)
1. Map GST returns to customers where possible (add `customer_id` during generation), or
2. Change `generate_summaries.py` to conservatively treat large shared datasets (like GST) as not applicable per-customer and either:
   - skip including them in `business_health` when no per-record customer id exists, or
   - apply a separate matching heuristic (e.g., match GSTIN → customer mapping) before attributing turnover.
3. Re-run analytics for affected customers after the above fix to remove inflated GST contributions.

---

## References
- `data_lake/apply_profile.py` — exact modifiers and ranges
- `COMPLETE_DATA_FIX_SUMMARY.md` — per-customer mapping used during regeneration
- `data_lake/analytics/generate_summaries.py` — dataset filtering and GST sampling logic

---

If you'd like, I can:
- Implement the conservative GST-handling change in `generate_summaries.py` so GST is not attributed unless per-record customer keys exist, and then re-run analytics for `CUST_MSM_00007` and others.
- Or try to map GSTIN -> customer_id if there's a deterministic mapping in the dataset.

Which do you prefer? 
