#!/usr/bin/env python
"""Comprehensive analytics generator (per-customer).

Generates detailed analytics including transactions, GST, credit, mutual funds,
insurance, OCEN, ONDC data with proper formatting for visualization.
"""
import argparse
import json
import os
import sys
import random
import math
from datetime import datetime
from collections import defaultdict
from financial_metrics import (
    compute_cashflow_metrics,
    compute_expense_composition,
    compute_credit_behavior,
    compute_business_health_metrics
)
import math


def now_ts():
    return datetime.utcnow().isoformat() + "Z"


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def load_ndjson(filepath, max_records=None):
    """Load NDJSON file. Optionally stop after `max_records` to reduce memory/CPU.

    Args:
        filepath: path to ndjson file
        max_records: if set, stop after reading this many records (first N lines)
    """
    data = []
    if not os.path.exists(filepath):
        return data
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if max_records and i >= max_records:
                    break
                if line.strip():
                    try:
                        data.append(json.loads(line))
                    except Exception:
                        data.append({'raw': line.strip()})
    except Exception as e:
        print(f"[WARN] Error loading {filepath}: {e}")
    return data


def analyze_transactions(transactions, customer_id):
    """Analyze transaction data with proper breakdown by type."""
    if not transactions:
        return {
            "customer_id": customer_id,
            "total_transactions": 0,
            "total_amount": 0,
            "monthly_cashflow": []
        }
    
    # Group by type
    by_type = defaultdict(lambda: {"count": 0, "total_amount": 0})
    total_amount = 0
    unknown_txns = []
    unknown_type_counts = defaultdict(int)
    
    for txn in transactions:
        txn_type = (txn.get('type') or txn.get('transaction_type') or 'UNKNOWN').upper()
        try:
            amount = float(str(txn.get('amount', 0) or 0).replace(',', ''))
        except (ValueError, AttributeError):
            amount = 0
        
        by_type[txn_type]["count"] += 1
        by_type[txn_type]["total_amount"] += amount
        if txn_type == 'UNKNOWN':
            # capture lightweight sample info for UI "show more" behavior
            unknown_type = (txn.get('category') or txn.get('merchant_category') or txn.get('narration') or txn.get('description') or 'UNKNOWN').strip()
            unknown_type_counts[unknown_type] += 1
            if len(unknown_txns) < 10:
                unknown_txns.append({
                    'date': txn.get('date') or txn.get('transaction_date') or txn.get('txn_date'),
                    'amount': round(amount, 2),
                    'merchant': txn.get('merchant_name') or txn.get('counterparty') or txn.get('description') or '',
                    'narration': txn.get('narration') or txn.get('description') or ''
                })
        total_amount += abs(amount)

    transactions_with_amount = sum(1 for t in transactions if t and (t.get('amount') or t.get('value') or t.get('amt')))
    
    # Monthly cashflow simulation
    monthly_cashflow = [
        {"month": "2025-07", "income": 850000, "expense": 620000},
        {"month": "2025-08", "income": 900000, "expense": 630000},
        {"month": "2025-09", "income": 880000, "expense": 600000},
        {"month": "2025-10", "income": 920000, "expense": 650000},
        {"month": "2025-11", "income": 950000, "expense": 670000},
        {"month": "2025-12", "income": 980000, "expense": 690000},
    ]
    
    # prepare amounts list for stability computation
    amounts_list = []
    for t in transactions:
        try:
            a = abs(float(str(t.get('amount', 0) or 0).replace(',', '')))
            if a > 0:
                amounts_list.append(a)
        except Exception:
            pass

    # compute basic stats on amounts_list
    amounts_stats = {}
    try:
        if amounts_list:
            mean_amt = sum(amounts_list) / len(amounts_list)
            var = sum((x - mean_amt) ** 2 for x in amounts_list) / len(amounts_list)
            std = math.sqrt(var)
            cv = (std / mean_amt) if mean_amt else None
            amounts_stats = {'count': len(amounts_list), 'mean': mean_amt, 'std': std, 'cv': cv}
        else:
            amounts_stats = {'count': 0, 'mean': 0, 'std': 0, 'cv': None}
    except Exception:
        amounts_stats = {'count': len(amounts_list)}

    return {
        "customer_id": customer_id,
        "generated_at": now_ts(),
        "total_transactions": len(transactions),
        "total_amount": total_amount,
        "average_transaction": total_amount / len(transactions) if transactions else 0,
        "by_type": dict(by_type),
        "unknown_type_breakdown": dict(sorted(unknown_type_counts.items(), key=lambda x: x[1], reverse=True)),
        "unknown_samples": unknown_txns,
        "monthly_cashflow": monthly_cashflow
        ,
        "amounts_stats": amounts_stats,
        "calculation": {
            "transactions_counted": len(transactions),
            "transactions_with_amount": transactions_with_amount,
            "total_amount_sum": total_amount,
            "average_formula": "total_amount / total_transactions",
            "explanation": f"Processed {len(transactions)} transactions; {transactions_with_amount} had explicit amount fields. Total amount summed to {total_amount:.2f}.",
            "amounts_sample_count": len(amounts_list)
        }
    }


def analyze_gst(gst_records, customer_id):
    """Analyze GST data with state distribution and fraud detection."""
    if not gst_records:
        return {
            "customer_id": customer_id,
            "returns_count": 0,
            "annual_turnover": 0
        }
    # Compute real aggregates from provided records
    # Treat each record as one GST return; aggregate turnover by MONTH to avoid cumulative inflation
    returns_count = len(gst_records)
    monthly_turnover = defaultdict(float)
    by_state = defaultdict(lambda: {"returns": 0, "turnover": 0})
    
    # Fraud detection tracking
    fraud_indicators_found = []
    fraud_records = []

    # mapping of GST state codes (first two digits) to state short names
    gst_state_map = {
        '01': 'JAMMU & KASHMIR','02': 'HIMACHAL PRADESH','03': 'PUNJAB','04': 'CHANDIGARH','05': 'UTTARAKHAND',
        '06': 'HARYANA','07': 'DELHI','08': 'RAJASTHAN','09': 'UTTAR PRADESH','10': 'BIHAR',
        '11': 'SIKKIM','12': 'ARUNACHAL PRADESH','13': 'NAGALAND','14': 'MANIPUR','15': 'MIZORAM',
        '16': 'TRIPURA','17': 'MEGHALAYA','18': 'ASSAM','19': 'WEST BENGAL','20': 'JHARKHAND',
        '21': 'ODISHA','22': 'CHATTISGARH','23': 'MADHYA PRADESH','24': 'GUJARAT','25': 'DAMAN & DIU',
        '26': 'DADRA & NAGAR HAVELI','27': 'MAHARASHTRA','28': 'ANDHRA PRADESH','29': 'KARNATAKA','30': 'GOA',
        '31': 'LAKSHADWEEP','32': 'KERALA','33': 'TAMIL NADU','34': 'PUDUCHERRY','35': 'ANDAMAN & NICOBAR',
        '36': 'TELANGANA','37': 'ANDHRA PRADESH (NEW)'
    }

    mapping_debug = []

    for rec in gst_records:
        # Try multiple fields for turnover
        turnover = 0
        try:
            turnover = float(str(rec.get('total_taxable_value') or rec.get('turnover') or 0).replace(',', ''))
        except:
            turnover = 0
        
        # Check for fraud indicators
        fraud_data = rec.get('fraud_indicators')
        if fraud_data:
            fraud_found = False
            if fraud_data.get('itc_ratio_high'):
                fraud_found = True
                fraud_indicators_found.append(f"High ITC ratio in {rec.get('return_period')}")
            if fraud_data.get('late_filing'):
                fraud_found = True
                fraud_indicators_found.append(f"Late filing in {rec.get('return_period')}")
            if fraud_data.get('turnover_mismatch'):
                fraud_found = True
                fraud_indicators_found.append(f"Turnover mismatch in {rec.get('return_period')}")
            if fraud_found:
                fraud_records.append(rec)

        # Aggregate by month (return_period format: "YYYY-MM")
        period = rec.get('return_period', '')
        if period:
            monthly_turnover[period] += turnover
        
        # Determine state: prefer explicit place_of_supply/state, else infer from GSTIN prefix
        raw_state = rec.get('place_of_supply') or rec.get('state')
        gstin = (rec.get('gstin') or '')
        mapped_state = None
        if raw_state and isinstance(raw_state, str) and raw_state.strip():
            mapped_state = raw_state.strip()
        else:
            # infer from gstin first two digits if possible
            if isinstance(gstin, str) and len(gstin) >= 2 and gstin[:2].isdigit():
                code = gstin[:2]
                mapped_state = gst_state_map.get(code, f'CODE_{code}')
        if not mapped_state:
            mapped_state = 'UNKNOWN'

        by_state[mapped_state]['returns'] += 1
        by_state[mapped_state]['turnover'] += turnover

        # record a small debug sample showing original vs mapped
        if len(mapping_debug) < 20:
            mapping_debug.append({
                'gstin': gstin,
                'raw_state': raw_state,
                'mapped_state': mapped_state,
                'turnover': turnover,
                'period': period
            })

    # Use MONTHLY AGGREGATED turnover instead of raw cumulative total
    # This prevents the issue where 5000 returns × ₹10M = ₹50B
    total_turnover = sum(monthly_turnover.values())
    total_businesses = len({(r.get('gstin') or r.get('trade_name') or i) for i, r in enumerate(gst_records)})
    average_revenue = (total_turnover / total_businesses) if total_businesses else 0

    result = {
        "customer_id": customer_id,
        "generated_at": now_ts(),
        "returns_count": returns_count,
        "monthly_periods": len(monthly_turnover),
        "annual_turnover": total_turnover,
        "total_businesses": total_businesses,
        "total_revenue": total_turnover,
        "average_revenue": average_revenue,
        "monthly_gst_turnover": dict(sorted(monthly_turnover.items())),
        "by_state": dict(by_state),
        "mapping_debug": mapping_debug,
        "compliance_score": random.randint(70, 95),
        "calculation": {
            "returns_count_computed_from": "len(gst_records)",
            "monthly_periods_found": len(monthly_turnover),
            "turnover_fields_used": ["total_taxable_value", "turnover"],
            "total_businesses_counted_by_unique_gstin_or_name": total_businesses,
            "note": "Turnover is sum of monthly aggregated values to avoid double-counting multiple returns per month"
        }
    }
    
    # Add fraud detection results if any found
    if fraud_indicators_found:
        result["fraud_detected"] = True
        result["fraud_indicators"] = fraud_indicators_found
        result["fraud_severity"] = "HIGH" if len(fraud_indicators_found) > 5 else "MEDIUM"
        result["fraud_records_count"] = len(fraud_records)
        result["fraud_summary"] = {
            "total_indicators": len(fraud_indicators_found),
            "affected_periods": len(set(r.get('return_period') for r in fraud_records)),
            "description": f"Detected {len(fraud_indicators_found)} fraud indicators across {len(fraud_records)} GST returns"
        }
    else:
        result["fraud_detected"] = False
    
    return result


def analyze_credit(credit_reports, customer_id):
    """Analyze credit bureau data."""
    # Provide summary with lightweight calculation metadata
    bureau_score = random.randint(650, 800)
    open_loans = random.randint(1, 3)
    total_outstanding = random.randint(100000, 500000)
    credit_utilization = round(random.uniform(30, 70), 2)
    payment_history = "Good" if random.random() > 0.3 else "Fair"

    return {
        "customer_id": customer_id,
        "generated_at": now_ts(),
        "bureau_score": bureau_score,
        "open_loans": open_loans,
        "total_outstanding": total_outstanding,
        "credit_utilization": credit_utilization,
        "payment_history": payment_history,
        "calculation": {
            "reports_counted": len(credit_reports),
            "bureau_score_source": "simulated_random_for_demo",
            "total_outstanding_estimate": total_outstanding,
            "explanation": f"Aggregated {len(credit_reports)} credit report entries; bureau score (simulated)={bureau_score}, total outstanding approx {total_outstanding}."
        }
    }


def analyze_mutual_funds(mf_records, customer_id):
    """Analyze mutual fund investments."""
    if not mf_records:
        return {
            "customer_id": customer_id,
            "total_portfolios": 0,
            "total_investment": 0
        }
    
    customer_mfs = [mf for mf in mf_records if mf.get('user_id') == customer_id or (mf.get('portfolio_id') or '').startswith('MF')]

    total_value = 0
    total_invested = 0
    scheme_types = defaultdict(int)

    for mf in customer_mfs:
        try:
            current_val = float(str(mf.get('current_value', 0) or 0).replace(',', ''))
            invested = float(str(mf.get('invested_amount', 0) or 0).replace(',', ''))
            total_value += current_val
            total_invested += invested
            scheme_types[mf.get('scheme_type') or 'UNKNOWN'] += 1
        except:
            pass

    returns_val = total_value - total_invested if total_invested else 0

    return {
        "customer_id": customer_id,
        "generated_at": now_ts(),
        "total_portfolios": len(customer_mfs),
        "total_investment": total_invested,
        "current_value": total_value,
        "returns": returns_val,
        "by_scheme_type": dict(scheme_types),
        "calculation": {
            "portfolios_counted": len(customer_mfs),
            "total_current_value_sum": total_value,
            "total_invested_sum": total_invested
        }
    }


def analyze_insurance(policies, customer_id):
    """Analyze insurance policies."""
    if not policies:
        return {
            "customer_id": customer_id,
            "total_policies": 0,
            "total_coverage": 0
        }
    
    customer_policies = [p for p in policies if p.get('user_id') == customer_id or (p.get('policy_id') or '').startswith('POL')]

    total_coverage = 0
    total_premium = 0
    by_type = defaultdict(int)

    for policy in customer_policies:
        try:
            coverage = float(str(policy.get('sum_assured', 0) or 0).replace(',', ''))
            premium = float(str(policy.get('premium_amount', 0) or 0).replace(',', ''))
            total_coverage += coverage
            total_premium += premium
            by_type[policy.get('policy_type') or 'UNKNOWN'] += 1
        except:
            pass

    active_policies = len([p for p in customer_policies if p.get('status') == 'ACTIVE'])

    # Sanity check: extremely high policy counts are suspicious in demo data
    suspicious_policy_count = True if len(customer_policies) > 200 else False

    return {
        "customer_id": customer_id,
        "generated_at": now_ts(),
        "total_policies": len(customer_policies),
        "total_coverage": total_coverage,
        "annual_premium": total_premium,
        "by_type": dict(by_type),
        "active_policies": active_policies,
        "suspicious_policy_count": suspicious_policy_count,
        "calculation": {
            "policies_counted": len(customer_policies),
            "total_coverage_sum": total_coverage,
            "total_annual_premium": total_premium,
            "note": "If total_policies is very large (>>100), the dataset may include synthetic or duplicated policies; inspect raw policy records."
        }
    }


def analyze_ocen(ocen_apps, customer_id):
    """Analyze OCEN loan applications."""
    if not ocen_apps:
        return {
            "customer_id": customer_id,
            "total_applications": 0
        }
    
    customer_apps = [app for app in ocen_apps if app.get('user_id') == customer_id or (app.get('application_id') or '').startswith('OCEN') or app.get('customer_id') == customer_id or app.get('account_customer_id') == customer_id]

    by_status = defaultdict(int)
    total_requested = 0
    total_approved = 0

    for app in customer_apps:
        try:
            # Support multiple possible field names from different generators
            requested = float(str(app.get('requested_amount') or app.get('loan_amount') or app.get('amount') or 0).replace(',', ''))
            # If a disbursed/approved field exists, use it; otherwise infer from status
            if app.get('approved_amount') is not None:
                approved = float(str(app.get('approved_amount') or 0).replace(',', ''))
            elif (app.get('status') or '').upper() in ['APPROVED', 'DISBURSED']:
                approved = requested
            else:
                approved = 0.0
            total_requested += requested
            total_approved += approved
            by_status[app.get('status') or 'UNKNOWN'] += 1
        except:
            pass

    approval_rate = (total_approved / total_requested * 100) if total_requested else 0

    return {
        "customer_id": customer_id,
        "generated_at": now_ts(),
        "total_applications": len(customer_apps),
        "total_requested": total_requested,
        "total_approved": total_approved,
        "approval_rate": approval_rate,
        "by_status": dict(by_status),
        "calculation": {
            "applications_counted": len(customer_apps),
            "total_requested_sum": total_requested,
            "total_approved_sum": total_approved,
            "approval_rate_formula": "total_approved / total_requested * 100"
        }
    }


def analyze_ondc(ondc_orders, customer_id):
    """Analyze ONDC order history."""
    if not ondc_orders:
        return {
            "customer_id": customer_id,
            "total_orders": 0,
            "total_value": 0
        }
    
    customer_orders = [o for o in ondc_orders if o.get('user_id') == customer_id or (o.get('order_id') or '').startswith('ONDC')]

    total_value = 0
    by_state = defaultdict(int)
    by_provider = defaultdict(int)
    provider_values = defaultdict(float)
    state_values = defaultdict(float)
    orders_processed = 0
    orders_with_price = 0

    for order in customer_orders:
        orders_processed += 1
        try:
            # support different raw schemas
            price = 0
            if isinstance(order.get('quote'), dict):
                price = float(order.get('quote', {}).get('price', 0) or 0)
            else:
                # Support generator field `total_amount` and older `total_value`/`order_value`
                price = float(order.get('order_value') or order.get('total_value') or order.get('total_amount') or 0)
            
            if price > 0:
                orders_with_price += 1
                total_value += price
            
            # Extract state from fulfillment or fallback
            state = 'UNKNOWN'
            if isinstance(order.get('fulfillment'), dict):
                state = order.get('fulfillment').get('state') or state
            elif order.get('state'):
                state = order.get('state')
            
            # Extract provider name from common fields produced by generators
            provider = 'UNKNOWN'
            # Common generator fields: 'provider_name', 'provider', 'seller', 'merchant'
            if order.get('provider_name') and isinstance(order.get('provider_name'), str) and order.get('provider_name').strip():
                provider = order.get('provider_name').strip()
            elif isinstance(order.get('provider'), dict):
                provider = order.get('provider').get('name') or provider
            elif isinstance(order.get('provider'), str) and order.get('provider').strip():
                provider = order.get('provider')
            elif order.get('seller') and isinstance(order.get('seller'), str):
                provider = order.get('seller')
            elif order.get('merchant') and isinstance(order.get('merchant'), str):
                provider = order.get('merchant')
            
            by_state[state] += 1
            by_provider[provider] += 1
            state_values[state] += price
            provider_values[provider] += price
        except Exception as e:
            # Log parse error but continue
            pass

    total_orders = len(customer_orders)
    average_order_value = (total_value / total_orders) if total_orders else 0
    unique_providers = len([p for p in by_provider.keys() if p != 'UNKNOWN'])
    unique_states = len([s for s in by_state.keys() if s != 'UNKNOWN'])
    # Top providers by total value (exclude UNKNOWN)
    sorted_providers = sorted(((p, v) for p, v in provider_values.items() if p != 'UNKNOWN'), key=lambda x: x[1], reverse=True)
    top_providers = [p for p, _ in sorted_providers[:10]]

    return {
        "customer_id": customer_id,
        "generated_at": now_ts(),
        "total_orders": total_orders,
        "total_value": total_value,
        "average_order_value": average_order_value,
        "by_state": dict(by_state),
        "by_provider": dict(by_provider),
        "provider_diversity": unique_providers,
        "top_providers": top_providers,
        "calculation": {
            "orders_counted": total_orders,
            "orders_processed": orders_processed,
            "orders_with_price": orders_with_price,
            "total_value_sum": total_value,
            "average_formula": "total_value / total_orders",
            "unique_providers": unique_providers,
            "unique_states": unique_states,
            "provider_distribution": dict(by_provider),
            "state_distribution": dict(by_state),
            "explanation": f"Processed {orders_processed} orders for customer {customer_id}. Found {unique_providers} unique providers and {unique_states} delivery states. Average order value computed as total_value ({total_value:.2f}) / total_orders ({total_orders})."
        }
    }


def create_anomalies_with_transactions(transactions, customer_id, gst_summary=None):
    """Create comprehensive anomalies report including fraud detection."""
    anomalies = []
    
    # Check for GST fraud indicators
    if gst_summary and gst_summary.get('fraud_detected'):
        fraud_details = gst_summary.get('fraud_summary', {})
        anomalies.append({
            "type": "gst_fraud_indicators",
            "count": fraud_details.get('total_indicators', 0),
            "severity": gst_summary.get('fraud_severity', 'HIGH'),
            "description": fraud_details.get('description', 'Fraud indicators detected in GST returns'),
            "indicators": gst_summary.get('fraud_indicators', [])[:10],  # Top 10
            "affected_periods": fraud_details.get('affected_periods', 0)
        })
    
    # Find high-value transactions
    high_value_txns = []
    for txn in transactions:
        try:
            amount = abs(float(str(txn.get('amount', 0) or txn.get('value', 0) or 0).replace(',', '')))
        except (ValueError, AttributeError):
            amount = 0
        # annotate txn with numeric amount for sorting
        txn_amount = amount
        if txn_amount > 0:
            txn['_numeric_amount'] = txn_amount
        if txn_amount > 100000:
            high_value_txns.append(txn)

    # sort descending by annotated amount and prepare top lists
    high_value_txns_sorted = sorted(high_value_txns, key=lambda t: t.get('_numeric_amount', 0), reverse=True)
    top_5 = []
    for t in high_value_txns_sorted[:5]:
        # produce a compact representation for UI
        top_5.append({
            'date': t.get('date') or t.get('transaction_date') or t.get('txn_date'),
            'type': t.get('type') or t.get('transaction_type') or 'N/A',
            'amount': t.get('_numeric_amount', 0),
            'description': t.get('description') or t.get('narration') or t.get('remark') or '' ,
            'raw': t
        })

    if high_value_txns:
        anomalies.append({
            "type": "high_value_transactions",
            "count": len(high_value_txns),
            "severity": "medium",
            "top_transactions": top_5,
            "transactions": high_value_txns_sorted[:10]  # include top 10 full objects sorted
        })
    
    # Simulate other anomaly types
    if random.random() > 0.7:
        anomalies.append({
            "type": "irregular_pattern",
            "count": 1,
            "severity": "low",
            "description": "Unusual transaction timing detected",
            "transactions": [transactions[0]] if transactions else []
        })
    
    return {
        "customer_id": customer_id,
        "generated_at": now_ts(),
        "total_anomalies": len(anomalies),
        "anomalies": anomalies,
        "fraud_detected": any(a.get('type') == 'gst_fraud_indicators' for a in anomalies)
    }


def main():
    parser = argparse.ArgumentParser(description="Generate comprehensive analytics summaries (per-customer)")
    parser.add_argument("--customer-id", dest="customer_id", required=True)
    # Optional raw file paths (allow pointing to annotated versions)
    parser.add_argument("--raw-transactions", dest="raw_transactions", required=False,
                        help="Path to raw transactions NDJSON (overrides default raw/raw_transactions.ndjson)")
    parser.add_argument("--raw-gst", dest="raw_gst", required=False,
                        help="Path to raw GST NDJSON (overrides default raw/raw_gst.ndjson)")
    parser.add_argument("--raw-credit-reports", dest="raw_credit_reports", required=False,
                        help="Path to raw credit reports NDJSON")
    parser.add_argument("--raw-mutual-funds", dest="raw_mutual_funds", required=False,
                        help="Path to raw mutual funds NDJSON")
    parser.add_argument("--raw-policies", dest="raw_policies", required=False,
                        help="Path to raw policies NDJSON")
    parser.add_argument("--raw-ocen", dest="raw_ocen", required=False,
                        help="Path to raw OCEN applications NDJSON")
    parser.add_argument("--raw-ondc", dest="raw_ondc", required=False,
                        help="Path to raw ONDC orders NDJSON")
    args = parser.parse_args()

    cid = args.customer_id
    print(f"[INFO] Starting comprehensive analytics generation for customer={cid}")
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    analytics_dir = os.path.join(base_dir, 'analytics')
    raw_dir = os.path.join(base_dir, 'raw')
    os.makedirs(analytics_dir, exist_ok=True)

    # Load data
    print(f"[INFO] Loading data from {raw_dir}...")
    # Allow overriding the raw input files via CLI for annotated/debug files
    # Use annotated file with customer_id by default
    default_txn_file = os.path.join(raw_dir, 'raw_transactions_with_customer_id.ndjson')
    if not os.path.exists(default_txn_file):
        default_txn_file = os.path.join(raw_dir, 'raw_transactions.ndjson')
    transactions_path = args.raw_transactions if args.raw_transactions else default_txn_file
    print(f"[INFO] Using transactions file: {transactions_path}")
    transactions = load_ndjson(transactions_path)

    # Configure GST sampling to reduce CPU / client disconnects during heavy processing
    # Defaults: limit=5000 records unless overridden by env `GST_SAMPLE_LIMIT` or sampling rate `GST_SAMPLE_RATE`
    try:
        gst_sample_limit = int(os.environ.get('GST_SAMPLE_LIMIT', '5000') or 0)
    except Exception:
        gst_sample_limit = 5000
    try:
        gst_sample_rate = float(os.environ.get('GST_SAMPLE_RATE', '0') or 0)
    except Exception:
        gst_sample_rate = 0.0

    gst_path = args.raw_gst if args.raw_gst else os.path.join(raw_dir, 'raw_gst.ndjson')
    print(f"[INFO] Using GST file: {gst_path}")
    # If a hard limit is specified, stop after reading that many records to avoid loading the entire file.
    if gst_sample_limit and gst_sample_limit > 0:
        gst_records = load_ndjson(gst_path, max_records=gst_sample_limit)
    else:
        gst_records = load_ndjson(gst_path)

    # If a sampling rate is specified (and <1.0), apply lightweight step sampling on the loaded slice
    if gst_records and gst_sample_rate > 0 and gst_sample_rate < 1.0:
        orig_len = len(gst_records)
        step = max(1, int(1.0 / gst_sample_rate))
        gst_records = [gst_records[i] for i in range(0, orig_len, step)]
        print(f"[INFO] GST records further sampled from {orig_len} to {len(gst_records)} using rate={gst_sample_rate}")

    # Load remaining datasets
    credit_reports_path = args.raw_credit_reports if args.raw_credit_reports else os.path.join(raw_dir, 'raw_credit_reports.ndjson')
    mutual_funds_path = args.raw_mutual_funds if args.raw_mutual_funds else os.path.join(raw_dir, 'raw_mutual_funds.ndjson')
    policies_path = args.raw_policies if args.raw_policies else os.path.join(raw_dir, 'raw_policies.ndjson')
    ocen_apps_path = args.raw_ocen if args.raw_ocen else os.path.join(raw_dir, 'raw_ocen_applications.ndjson')
    ondc_orders_path = args.raw_ondc if args.raw_ondc else os.path.join(raw_dir, 'raw_ondc_orders.ndjson')

    credit_reports = load_ndjson(credit_reports_path)
    mutual_funds = load_ndjson(mutual_funds_path)
    policies = load_ndjson(policies_path)
    ocen_apps = load_ndjson(ocen_apps_path)
    
    # Filter loaded datasets to the requested customer where possible (preserve full lists if no customer_id present)
    def _filter_by_customer(records):
        if not records:
            return []
        # Robust matching: accept exact customer_id matches, and also user_id/account_customer_id
        # variants that embed the customer id (e.g. "USER_CUST_MSM_00010").
        has_keys = any(('customer_id' in r or 'user_id' in r or 'account_customer_id' in r) for r in records)
        filtered = []
        for r in records:
            try:
                if r.get('customer_id') == cid:
                    filtered.append(r)
                    continue
                uid = r.get('user_id') or ''
                if isinstance(uid, str) and cid in uid:
                    filtered.append(r)
                    continue
                acc = r.get('account_customer_id') or ''
                if isinstance(acc, str) and cid in acc:
                    filtered.append(r)
                    continue
            except Exception:
                # ignore malformed records
                continue

        # If dataset contains any customer/user keys, return the (possibly empty) filtered list.
        # Otherwise assume dataset is not customer-scoped and return the original records.
        if has_keys:
            print(f"[DEBUG] _filter_by_customer: original={len(records)} filtered={len(filtered)} for customer={cid}")
            return filtered
        return records

    transactions = _filter_by_customer(transactions)
    gst_records = _filter_by_customer(gst_records)
    credit_reports = _filter_by_customer(credit_reports)
    mutual_funds = _filter_by_customer(mutual_funds)
    policies = _filter_by_customer(policies)
    ocen_apps = _filter_by_customer(ocen_apps)
    ondc_orders = _filter_by_customer(load_ndjson(ondc_orders_path))

    if gst_records is not None:
        print(f"[INFO] GST records loaded: {len(gst_records)} (limit={gst_sample_limit}, rate={gst_sample_rate})")

    # If GST records do not contain per-record customer identifiers, they likely represent a global file
    # and should not be attributed to a single customer (to avoid inflating business health).
    if gst_records and not any(('customer_id' in r or 'user_id' in r or 'account_customer_id' in r) for r in gst_records):
        print(f"[INFO] GST file appears unscoped (no per-record customer ids). Skipping GST attribution for customer={cid}.")
        gst_records = []

    # Generate analytics
    print(f"[INFO] Generating analytics...")
    transaction_summary = analyze_transactions(transactions, cid)
    gst_summary = analyze_gst(gst_records, cid)
    credit_summary = analyze_credit(credit_reports, cid)
    mf_summary = analyze_mutual_funds(mutual_funds, cid)
    insurance_summary = analyze_insurance(policies, cid)
    ocen_summary = analyze_ocen(ocen_apps, cid)
    ondc_summary = analyze_ondc(ondc_orders, cid)
    anomalies_report = create_anomalies_with_transactions(transactions, cid, gst_summary)
    
    # Compute advanced financial metrics
    print(f"[INFO] Computing advanced financial metrics...")
    cashflow_metrics = compute_cashflow_metrics(transactions)
    expense_composition = compute_expense_composition(transactions)
    credit_behavior = compute_credit_behavior(transactions)
    business_health = compute_business_health_metrics(gst_summary, transactions, ondc_summary)
    
    # Create earnings vs spendings summary
    earnings_spendings = {
        "customer_id": cid,
        "generated_at": now_ts(),
        "cashflow_metrics": cashflow_metrics,
        "expense_composition": expense_composition,
        "credit_behavior": credit_behavior,
        "business_health": business_health
    }

    # Debt & Loan Analysis: derive a UI-friendly section combining credit and expense data
    try:
        total_loan_payments = credit_behavior.get('total_loan_payments') if credit_behavior.get('total_loan_payments') is not None else expense_composition.get('debt_servicing', 0)
    except Exception:
        total_loan_payments = expense_composition.get('debt_servicing', 0)

    debt_loan_analysis = {
        "total_loan_payments": round(float(total_loan_payments or 0), 2),
        "emi_transactions": int(credit_behavior.get('emi_count') or 0),
        "debt_servicing_ratio": round(float(expense_composition.get('debt_servicing_ratio') or 0), 2),
        "debt_to_income_ratio": round(float(credit_behavior.get('debt_to_income_ratio') or 0), 2),
        "debt_burden": "High" if float(expense_composition.get('debt_servicing_ratio') or 0) > 60 else "Moderate" if float(expense_composition.get('debt_servicing_ratio') or 0) > 40 else "Low",
        "emi_consistency_score": round(float(credit_behavior.get('emi_consistency_score') or 100), 2),
        "payment_regularity_score": round(float(credit_behavior.get('payment_regularity_score') or 100), 2)
    }

    earnings_spendings['debt_loan_analysis'] = debt_loan_analysis

    # Top 10 expenses (for UI click-to-expand)
    debit_txns = []
    for t in transactions:
        ttype = (t.get('type') or t.get('transaction_type') or '').upper()
        if ttype in ['DEBIT', 'DR', 'D', 'WITHDRAWAL']:
            try:
                amt = abs(float(str(t.get('amount', 0) or t.get('value') or 0).replace(',', '')))
            except Exception:
                amt = 0.0
            debit_txns.append({
                'date': t.get('date') or t.get('transaction_date') or '',
                'merchant': t.get('merchant_name') or t.get('counterparty') or t.get('description') or '',
                'category': t.get('category') or t.get('merchant_category') or '',
                'amount': round(amt, 2),
                'narration': t.get('narration') or t.get('description') or ''
            })

    top_10_expenses = sorted(debit_txns, key=lambda x: x['amount'], reverse=True)[:10]
    # attach to expense_composition for UI convenience
    earnings_spendings['expense_composition']['top_10_expenses'] = top_10_expenses

    # Provide a single reconciliation percent for UI display: GST–Bank Variance as % of GST Turnover
    try:
        reconciliation_pct = business_health.get('reconciliation_percent_of_gst') if isinstance(business_health, dict) else None
    except Exception:
        reconciliation_pct = None
    overall_reconciliation_pct = round(float(reconciliation_pct), 2) if reconciliation_pct is not None else None
    
    # Generate lending decision based on financial metrics
    print(f"[INFO] Generating lending decision...")
    positives = []
    negatives = []
    
    # Evaluate cashflow metrics
    if cashflow_metrics.get('net_surplus', 0) > 0:
        positives.append(f"Positive net surplus of ₹{cashflow_metrics['net_surplus']:.2f}")
    else:
        negatives.append(f"Negative net surplus of ₹{cashflow_metrics['net_surplus']:.2f}")
    
    if cashflow_metrics.get('surplus_ratio', 0) > 20:
        positives.append(f"Strong surplus ratio of {cashflow_metrics['surplus_ratio']:.1f}%")
    elif cashflow_metrics.get('surplus_ratio', 0) < 0:
        negatives.append(f"Negative surplus ratio of {cashflow_metrics['surplus_ratio']:.1f}%")
    
    if cashflow_metrics.get('inflow_outflow_ratio', 0) > 1.2:
        positives.append(f"Healthy inflow/outflow ratio of {cashflow_metrics['inflow_outflow_ratio']:.2f}")
    elif cashflow_metrics.get('inflow_outflow_ratio', 0) < 1.0:
        negatives.append(f"Poor inflow/outflow ratio of {cashflow_metrics['inflow_outflow_ratio']:.2f}")
    
    if cashflow_metrics.get('income_stability_cv', 100) < 30:
        positives.append(f"Stable income with CV of {cashflow_metrics['income_stability_cv']:.1f}%")
    elif cashflow_metrics.get('income_stability_cv', 100) > 60:
        negatives.append(f"Volatile income with CV of {cashflow_metrics['income_stability_cv']:.1f}%")
    
    if cashflow_metrics.get('seasonality_index', 100) < 50:
        positives.append(f"Low seasonality index of {cashflow_metrics['seasonality_index']:.1f}%")
    elif cashflow_metrics.get('seasonality_index', 100) > 80:
        negatives.append(f"High seasonality with index of {cashflow_metrics['seasonality_index']:.1f}%")
    
    if cashflow_metrics.get('top_customer_dependence', 100) < 50:
        positives.append(f"Diversified customer base with {cashflow_metrics['top_customer_dependence']:.1f}% top customer dependence")
    elif cashflow_metrics.get('top_customer_dependence', 100) > 70:
        negatives.append(f"High customer concentration with {cashflow_metrics['top_customer_dependence']:.1f}% dependence")
    
    surplus_trend = cashflow_metrics.get('surplus_trend', 'stable')
    if surplus_trend == 'increasing':
        positives.append("Surplus is trending upward")
    elif surplus_trend == 'decreasing':
        negatives.append("Surplus is trending downward")
    
    # Evaluate expense composition
    if expense_composition.get('essential_ratio', 0) > 60:
        positives.append(f"Majority spending on essentials: {expense_composition['essential_ratio']:.1f}%")
    elif expense_composition.get('essential_ratio', 0) < 40:
        negatives.append(f"High non-essential spending: {100 - expense_composition['essential_ratio']:.1f}%")
    
    if expense_composition.get('debt_servicing_ratio', 100) < 40:
        positives.append(f"Manageable debt servicing at {expense_composition['debt_servicing_ratio']:.1f}%")
    elif expense_composition.get('debt_servicing_ratio', 100) > 60:
        negatives.append(f"High debt burden with {expense_composition['debt_servicing_ratio']:.1f}% DSR")
    
    # Evaluate credit behavior
    if credit_behavior.get('bounce_count', 0) == 0:
        positives.append("No payment bounces or failures")
    elif credit_behavior.get('bounce_count', 0) > 3:
        negatives.append(f"Multiple payment failures: {credit_behavior['bounce_count']} bounces")
    else:
        negatives.append(f"{credit_behavior['bounce_count']} payment bounce(s) detected")
    
    if credit_behavior.get('emi_consistency_score', 0) > 80:
        positives.append(f"Excellent EMI consistency: {credit_behavior['emi_consistency_score']:.1f}%")
    elif credit_behavior.get('emi_consistency_score', 0) < 60:
        negatives.append(f"Poor EMI consistency: {credit_behavior['emi_consistency_score']:.1f}%")
    

    
    if business_health.get('working_capital_gap', 100) < 30:
        positives.append(f"Efficient working capital: {business_health['working_capital_gap']:.1f} days")
    elif business_health.get('working_capital_gap', 100) > 60:
        negatives.append(f"Long working capital cycle: {business_health['working_capital_gap']:.1f} days")
    
    if business_health.get('credit_growth_rate', -100) > 10:
        positives.append(f"Strong credit growth of {business_health['credit_growth_rate']:.1f}%")
    elif business_health.get('credit_growth_rate', -100) < -10:
        negatives.append(f"Declining credit with {business_health['credit_growth_rate']:.1f}% growth")
    
    if business_health.get('expense_growth_rate', 100) < 5:
        positives.append(f"Controlled expense growth at {business_health['expense_growth_rate']:.1f}%")
    elif business_health.get('expense_growth_rate', 100) > 20:
        negatives.append(f"Rapidly rising expenses: {business_health['expense_growth_rate']:.1f}% growth")
    
    # Make final decision
    positive_count = len(positives)
    negative_count = len(negatives)
    
    if positive_count >= negative_count * 2:
        recommendation = "APPROVE"
        reasoning = f"Strong financial profile with {positive_count} positive indicators vs {negative_count} concerns. Borrower demonstrates good creditworthiness."
    elif positive_count > negative_count:
        recommendation = "APPROVE WITH CONDITIONS"
        reasoning = f"Generally positive profile with {positive_count} strengths, though {negative_count} concerns should be monitored. Consider setting conditions on loan amount or tenure."
    elif positive_count == negative_count:
        recommendation = "MANUAL REVIEW"
        reasoning = f"Mixed financial indicators with {positive_count} positives and {negative_count} negatives. Requires detailed manual assessment."
    else:
        recommendation = "REJECT"
        reasoning = f"Significant concerns with {negative_count} negative indicators vs {positive_count} positives. High credit risk profile."
    
    earnings_spendings['decision'] = {
        "recommendation": recommendation,
        "positives": positives,
        "negatives": negatives,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "reasoning": reasoning,
        "generated_at": now_ts()
    }

    # Calculate derived credit metrics
    # Cashflow stability: derive from transaction amounts statistics (lower CV -> higher stability)
    try:
        amt_stats = transaction_summary.get('amounts_stats', {}) or {}
        txn_calc = transaction_summary.get('calculation', {})
        cnt = float(txn_calc.get('transactions_counted') or 0) or 0.0
        with_amt = float(txn_calc.get('transactions_with_amount') or 0) or 0.0
        perc_with_amount = (with_amt / cnt) if cnt else 0.0
        cv = amt_stats.get('cv') if isinstance(amt_stats.get('cv'), (int, float)) else 1.0
        # score mapping: base 50 + contribution from completeness + stability inverse of CV
        score_raw = 50.0 + (perc_with_amount * 30.0) + (max(0.0, (1.0 / (1.0 + cv))) * 20.0)
        cashflow_stability = round(max(0.0, min(100.0, score_raw)), 1)
        cv_val = amt_stats.get('cv')
        try:
            cv_str = f"{cv_val:.3f}" if cv_val is not None else 'N/A'
        except Exception:
            cv_str = str(cv_val)
        cashflow_explanation = (
            f"Computed from {int(cnt)} transactions ({int(with_amt)} with amounts). "
            f"Mean amount={amt_stats.get('mean'):.2f} std={amt_stats.get('std'):.2f} cv={cv_str}. "
            f"Formula: 50 + perc_with_amount*30 + (1/(1+cv))*20 => {cashflow_stability}"
        )
    except Exception:
        cashflow_stability = round(random.uniform(60, 90), 1)
        cashflow_explanation = "Fallback random estimate due to insufficient data"

    # Business Health: calculate from actual business metrics
    try:
        gst_count = gst_summary.get('returns_count', 0)
        gst_turnover = gst_summary.get('total_revenue', 0)
        ondc_orders = ondc_summary.get('total_orders', 0)
        ondc_providers = len(ondc_summary.get('top_providers', []))
        mf_portfolios = mf_summary.get('total_portfolios', 0)
        
        # Score components (0-100 scale)
        # GST compliance: 30 points. New expected baseline is 36 monthly returns (~3 years).
        # Scale linearly: gst_score = min(30, gst_count / EXPECTED_RETURNS * 30)
        EXPECTED_GST_RETURNS = 36
        gst_score = min(30, (gst_count / EXPECTED_GST_RETURNS) * 30) if gst_count > 0 else 0
        
        # Revenue scale: 20 points (based on turnover) — normalized to new composition
        # Score increases with turnover: 0-1Cr=4pts, 1-5Cr=8pts, 5-10Cr=12pts, 10-50Cr=16pts, >50Cr=20pts
        if gst_turnover > 500000000:  # >50Cr
            revenue_score = 20
        elif gst_turnover > 100000000:  # 10-50Cr
            revenue_score = 16
        elif gst_turnover > 50000000:  # 5-10Cr
            revenue_score = 12
        elif gst_turnover > 10000000:  # 1-5Cr
            revenue_score = 8
        elif gst_turnover > 0:  # 0-1Cr
            revenue_score = 4
        else:
            revenue_score = 0
        
        # ONDC: provider diversity (10 points) + volume relative to PAT (5 points) => total 15
        # Investment (MF) scoring: 20 points based on current value relative to PAT
        # Customer concentration: 10 points (based on top-5 share)
        # State diversification: 5 points (distinct GST states)

        # Compose final business health from the component scores we prepared above
        # Recompute lightweight inflow breakdown if not already available
        total_inflow = 0.0
        inflow_by_counterparty = {}
        for t in transactions:
            ttype = (t.get('type') or t.get('transaction_type') or '').upper()
            if ttype in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
                try:
                    amt = abs(float(str(t.get('amount', 0) or t.get('value') or 0).replace(',', '')))
                except:
                    amt = 0.0
                total_inflow += amt
                # Prefer multiple possible counterparty fields to avoid collapsing to UNKNOWN
                counter = None
                for key in ['merchant_name', 'counterparty_account', 'counterparty_name', 'beneficiary_name', 'payee', 'payer', 'description', 'narration', 'remark']:
                    val = t.get(key)
                    if isinstance(val, str) and val.strip():
                        counter = val.strip()
                        break
                if not counter:
                    counter = 'UNKNOWN'
                # normalize length to avoid huge keys
                if len(counter) > 60:
                    counter = counter[:57] + '...'
                inflow_by_counterparty[counter] = inflow_by_counterparty.get(counter, 0.0) + amt

        # PAT proxy: credits - debits; fallback to GST monthly average
        total_debits = 0.0
        for t in transactions:
            ttype = (t.get('type') or t.get('transaction_type') or '').upper()
            if ttype in ['DEBIT', 'DR', 'D']:
                try:
                    total_debits += abs(float(str(t.get('amount', 0) or 0).replace(',', '')))
                except:
                    pass

        pat_proxy = total_inflow - total_debits
        if abs(pat_proxy) < 1 and gst_turnover > 0:
            pat_proxy = gst_turnover / 12.0

        # ONDC scoring: provider diversity (10) + volume (5) based on realistic buckets
        provider_div_score = min(10, ondc_providers * 2) if ondc_providers > 0 else 0
        ondc_total_value = ondc_summary.get('total_value', 0)

        # Choose base for ONDC volume: Annual Revenue (GST) or Bank Credits
        used_revenue_base = None
        try:
            used_revenue_base = business_health.get('used_revenue_base') if isinstance(business_health, dict) else None
        except Exception:
            used_revenue_base = None

        total_inflow_for_bank = total_inflow if total_inflow > 0 else (cashflow_metrics.get('total_inflow') or 0)
        gst_base = gst_turnover if gst_turnover and gst_turnover > 0 else 0

        # compute percentages
        pct_vs_annual = (ondc_total_value / gst_base) if gst_base > 0 else 0
        pct_vs_bank = (ondc_total_value / total_inflow_for_bank) if total_inflow_for_bank > 0 else 0

        # Bucket scoring: prefer revenue base when GST is present, else bank
        if used_revenue_base == 'gst' and gst_base > 0:
            pct = pct_vs_annual
            # thresholds (annual revenue): >=5% => full 5, 2-5%=>3, 1-2%=>1.5, <1% scaled
            if pct >= 0.05:
                vol_score = 5
            elif pct >= 0.02:
                vol_score = 3
            elif pct >= 0.01:
                vol_score = 1.5
            else:
                vol_score = min(1.5, pct / 0.01 * 1.5) if pct > 0 else 0
            vol_base_label = 'annual_revenue'
        else:
            pct = pct_vs_bank
            # thresholds (bank credits): >=2% => full 5, 1-2%=>3, 0.5-1%=>1.5
            if pct >= 0.02:
                vol_score = 5
            elif pct >= 0.01:
                vol_score = 3
            elif pct >= 0.005:
                vol_score = 1.5
            else:
                vol_score = min(1.5, pct / 0.005 * 1.5) if pct > 0 else 0
            vol_base_label = 'bank_credits'

        ondc_score = round(provider_div_score + vol_score, 2)

        # MF scoring: allow MF_value ÷ Avg Monthly Obligations OR MF_value ÷ Requested Loan Amount
        mf_current_value = mf_summary.get('current_value', 0)
        avg_monthly_obligations = 0
        mf_base_used = None
        # use cashflow_metrics monthly_outflow if available to compute average obligations
        try:
            mo = cashflow_metrics.get('monthly_outflow') or {}
            if isinstance(mo, dict) and len(mo) > 0:
                avg_monthly_obligations = sum([float(v) for v in mo.values()]) / len(mo)
            else:
                avg_monthly_obligations = (cashflow_metrics.get('total_outflow') or 0) / 12.0
        except Exception:
            avg_monthly_obligations = (cashflow_metrics.get('total_outflow') or 0) / 12.0

        requested_loan = ocen_summary.get('total_requested', 0)
        if requested_loan and requested_loan > 0:
            # MF relative to requested loan amount: full if MF >= 50% of requested loan
            r = mf_current_value / requested_loan if requested_loan > 0 else 0
            mf_score = min(20, (r / 0.5) * 20) if r > 0 else 0
            mf_base_used = 'requested_loan'
        elif avg_monthly_obligations and avg_monthly_obligations > 0:
            # MF relative to monthly obligations: full if MF covers >= 6 months obligations
            r = mf_current_value / avg_monthly_obligations if avg_monthly_obligations > 0 else 0
            mf_score = min(20, (r / 6.0) * 20) if r > 0 else 0
            mf_base_used = 'avg_monthly_obligations'
        else:
            mf_score = min(20, mf_portfolios * 2)
            mf_base_used = 'portfolio_count_fallback'

        # Customer concentration: top-5 share -> lower share -> higher score (10 points)
        top5 = sorted(inflow_by_counterparty.values(), reverse=True)[:5]
        top5_share = (sum(top5) / total_inflow) if total_inflow > 0 else 0
        concentration_score = round((1.0 - min(1.0, top5_share)) * 10, 2)

        # Explain concentration result for UI: detect if collapse to UNKNOWN occurred
        unique_counterparties = len([k for k in inflow_by_counterparty.keys() if k != 'UNKNOWN'])
        if total_inflow == 0:
            concentration_explanation = "No credit inflow data available to compute concentration."
        elif unique_counterparties == 0:
            concentration_explanation = (
                "All credit inflows are uncategorized (counterparty unknown). "
                "This often indicates missing merchant/counterparty fields in transactions; improve parsing to get meaningful concentration scores."
            )
        else:
            if top5_share >= 0.95:
                concentration_explanation = (
                    f"Top-5 customers account for {top5_share*100:.1f}% of inflows — very high concentration. "
                    "Verify counterparty parsing (unknowns may be collapsing) and consider diversification actions."
                )
            else:
                concentration_explanation = f"Top-5 customers account for {top5_share*100:.1f}% of inflows. Lower is better."

        # State diversification: use GST summary's distinct mapped states (5 points max)
        unique_states = len([s for s in gst_summary.get('by_state', {}).keys() if s and s != 'UNKNOWN'])
        state_score = min(5, (unique_states / 3.0) * 5) if unique_states > 0 else 0

        # Final business health composition (sum of components):
        # gst_score (30) + revenue_score (20) + ondc_score (15) + mf_score (20) + concentration_score (10) + state_score (5)
        business_health = round(gst_score + revenue_score + ondc_score + mf_score + concentration_score + state_score, 1)
        business_health = min(100.0, business_health)

        business_explanation = (
            f"GST Compliance: {gst_score:.1f}/30 ({gst_count} returns, baseline={EXPECTED_GST_RETURNS}), "
            f"Revenue Scale: {revenue_score}/20 (₹{gst_turnover:,.0f}), "
            f"ONDC: {ondc_score:.2f}/15 ({ondc_providers} providers, value=₹{ondc_total_value:,.0f}), "
            f"Investments: {mf_score:.2f}/20 (MF value=₹{mf_current_value:,.0f}), "
            f"Cust Concentration: {concentration_score:.2f}/10 (top5_share={top5_share:.2f}), "
            f"State Diversity: {state_score:.2f}/5 (states={unique_states}) = {business_health}/100"
        )
        # Human-friendly explanation strings for UI info buttons
        debt_capacity_explanation = (
            "Debt capacity is computed from credit behavior, OCEN approvals, insurance coverage, DTI, "
            "and repayment regularity. Components: credit score-based (0-30), DTI impact (0-15), OCEN approval (0-10), "
            "insurance cover (0-10), repayment & regularity bonuses (0-10), with a base floor to reflect minimal capacity. "
            "See detailed `debt_capacity_breakdown` for numeric components."
        )
        concentration_explanation_text = concentration_explanation
    except Exception as e:
        business_health = round(random.uniform(65, 95), 1)
        business_explanation = f"Fallback estimate due to calculation error: {str(e)}"
    
    # Compute deterministic debt capacity using credit behavior, OCEN approval, insurance coverage, and DTI
    try:
        cb = credit_behavior or {}
        default_prob = float(cb.get('default_probability_score') or 50)
        debt_to_income = float(cb.get('debt_to_income_ratio') or cb.get('debt_to_income_ratio', 0) or 0)
        repayment_rate = float(cb.get('loan_repayment_rate') or 100)
        payment_regularity = float(cb.get('payment_regularity_score') or 100)

        # OCEN approval
        ocen_approval = float(ocen_summary.get('approval_rate') or 0)

        # Insurance coverage relative to annual revenue (GST) if available
        insurance_coverage = float(insurance_summary.get('total_coverage') or 0)
        revenue_for_insurance = gst_summary.get('total_revenue') or 0

        # Components
        # 1) Credit component (0-30): lower default probability => higher score
        credit_component = max(0.0, 30.0 * (1.0 - (default_prob / 100.0)))

        # small bonus for high repayment rate (0-5)
        repayment_bonus = min(5.0, (repayment_rate / 100.0) * 5.0)

        # 2) DTI component (0-15): higher DTI reduces score
        dti_component = max(0.0, 15.0 * (1.0 - min(1.0, debt_to_income / 100.0)))

        # 3) OCEN approval (0-10)
        ocen_component = min(10.0, (ocen_approval / 100.0) * 10.0)

        # 4) Insurance coverage (0-10) based on coverage vs annual revenue
        if revenue_for_insurance > 0:
            cov_ratio = insurance_coverage / revenue_for_insurance
            if cov_ratio >= 1.0:
                ins_component = 10.0
            elif cov_ratio >= 0.5:
                ins_component = 8.0
            elif cov_ratio >= 0.2:
                ins_component = 5.0
            else:
                ins_component = min(4.0, (cov_ratio / 0.1) * 4.0) if cov_ratio > 0 else 0.0
        else:
            # fallback: reward any meaningful absolute coverage (small contribution)
            ins_component = min(5.0, insurance_coverage / 100000.0)

        # 5) Payment regularity small bonus (0-5)
        regularity_bonus = min(5.0, (payment_regularity / 100.0) * 5.0)

        # Base floor to reflect minimal capacity if data exists
        base_floor = 10.0

        debt_capacity_val = base_floor + credit_component + repayment_bonus + dti_component + ocen_component + ins_component + regularity_bonus
        debt_capacity = round(max(0.0, min(100.0, debt_capacity_val)), 1)

        debt_capacity_breakdown = {
            "base_floor": base_floor,
            "credit_component": round(credit_component, 2),
            "repayment_bonus": round(repayment_bonus, 2),
            "dti_component": round(dti_component, 2),
            "ocen_component": round(ocen_component, 2),
            "insurance_component": round(ins_component, 2),
            "regularity_bonus": round(regularity_bonus, 2),
            "sum_raw": round(debt_capacity_val, 2),
            "final_debt_capacity": debt_capacity
        }
        # Build a human-friendly derivation string similar to business_explanation
        try:
            cov_ratio = (insurance_coverage / revenue_for_insurance) if revenue_for_insurance > 0 else None
            debt_derivation = (
                f"Credit Component: {debt_capacity_breakdown['credit_component']:.2f}/30 (default_prob={default_prob:.1f}%), "
                f"Repayment Bonus: {debt_capacity_breakdown['repayment_bonus']:.2f}/5 (repayment_rate={repayment_rate:.1f}%), "
                f"DTI: {debt_capacity_breakdown['dti_component']:.2f}/15 (debt_to_income={debt_to_income:.1f}%), "
                f"OCEN: {debt_capacity_breakdown['ocen_component']:.2f}/10 (approval_rate={ocen_approval:.1f}%), "
                f"Insurance: {debt_capacity_breakdown['insurance_component']:.2f}/10 (coverage=₹{insurance_coverage:,.0f}{', revenue_base=₹{:,}'.format(int(revenue_for_insurance)) if revenue_for_insurance else ''}), "
                f"Regularity Bonus: {debt_capacity_breakdown['regularity_bonus']:.2f}/5 (payment_regularity={payment_regularity:.1f}%) = {debt_capacity}/100"
            )
        except Exception:
            debt_derivation = "Credit utilization, OCEN approval rate, insurance coverage, loan-to-income ratio"
    except Exception as e:
        debt_capacity = round(random.uniform(40, 80), 1)
        debt_capacity_breakdown = {"error": str(e)}
    # Composite weighted score
    composite_credit_score = round(0.45 * cashflow_stability + 0.35 * business_health + 0.20 * debt_capacity, 2)

    overall = {
        "customer_id": cid,
        "generated_at": now_ts(),
        "total_records": len(transactions) + len(gst_records) + len(credit_reports),
        "datasets_count": 7,
        "total_accounts": random.randint(2, 5),
        "datasets": {
            "transactions": len(transactions),
            "gst_returns": len(gst_records),
            "credit_reports": len(credit_reports),
            "mutual_funds": mf_summary["total_portfolios"],
            "insurance": insurance_summary["total_policies"],
            "ocen_applications": ocen_summary["total_applications"],
            "ondc_orders": ondc_summary["total_orders"]
        },
        "scores": {
            "cashflow_stability": cashflow_stability,
            "business_health": business_health,
            "debt_capacity": debt_capacity,
            "overall_risk_score": composite_credit_score
        },
        "debt_capacity_breakdown": debt_capacity_breakdown,
        "debt_capacity_explanation": debt_capacity_explanation,
        "business_health_contributors": {
            "gst_businesses": gst_summary.get('returns_count', 0),
            "gst_turnover": gst_summary.get('total_revenue', 0),
            "ondc_provider_diversity": len(ondc_summary.get('top_providers', [])),
            "mutual_fund_portfolios": mf_summary.get('total_portfolios', 0),
            "calculation_breakdown": business_explanation
        },
        "reconciliation_pct_of_gst": overall_reconciliation_pct,
        "concentration_explanation": concentration_explanation_text,
        "score_methodology": {
            "composite_formula": "0.45*cashflow_stability + 0.35*business_health + 0.20*debt_capacity",
            "weights": {"cashflow": 0.45, "business": 0.35, "debt": 0.20},
            "cashflow_derivation": cashflow_explanation if isinstance(cashflow_explanation, str) else "Transaction volume consistency, income/expense ratio, monthly variance",
            "business_derivation": business_explanation if isinstance(business_explanation, str) else "GST compliance, ONDC order diversity, revenue trends, mutual fund investments",
            "debt_derivation": debt_derivation if 'debt_derivation' in locals() else "Credit utilization, OCEN approval rate, insurance coverage, loan-to-income ratio",
            "explanation": f"Cashflow ({cashflow_stability}) weighted 45% + Business Health ({business_health}) weighted 35% + Debt Capacity ({debt_capacity}) weighted 20% = {composite_credit_score}"
        },
        "recommendation": "approve" if composite_credit_score >= 75 else "review" if composite_credit_score >= 60 else "caution"
    }

    # Write all summaries
    print(f"[INFO] Writing analytics files to {analytics_dir}...")
    write_json(os.path.join(analytics_dir, f"{cid}_transaction_summary.json"), transaction_summary)
    write_json(os.path.join(analytics_dir, f"{cid}_gst_summary.json"), gst_summary)
    write_json(os.path.join(analytics_dir, f"{cid}_credit_summary.json"), credit_summary)
    write_json(os.path.join(analytics_dir, f"{cid}_mutual_funds_summary.json"), mf_summary)
    write_json(os.path.join(analytics_dir, f"{cid}_insurance_summary.json"), insurance_summary)
    write_json(os.path.join(analytics_dir, f"{cid}_ocen_summary.json"), ocen_summary)
    write_json(os.path.join(analytics_dir, f"{cid}_ondc_summary.json"), ondc_summary)
    write_json(os.path.join(analytics_dir, f"{cid}_anomalies_report.json"), anomalies_report)
    write_json(os.path.join(analytics_dir, f"{cid}_earnings_spendings.json"), earnings_spendings)
    write_json(os.path.join(analytics_dir, f"{cid}_overall_summary.json"), overall)

    print(f"[INFO] Analytics files written to: {analytics_dir}")
    print(f"[INFO] Completed analytics generation for customer={cid}")
    print(f"  - Transactions: {transaction_summary['total_transactions']}")
    print(f"  - GST Returns: {gst_summary['returns_count']}")
    print(f"  - Mutual Funds: {mf_summary['total_portfolios']}")
    print(f"  - Insurance: {insurance_summary['total_policies']}")
    print(f"  - OCEN Apps: {ocen_summary['total_applications']}")
    print(f"  - ONDC Orders: {ondc_summary['total_orders']}")
    print(f"  - Anomalies: {anomalies_report['total_anomalies']}")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"[ERROR] Analytics generation failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(2)
    sys.exit(0)
