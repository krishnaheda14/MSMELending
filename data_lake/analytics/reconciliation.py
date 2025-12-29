"""
GST/Bank/ONDC Reconciliation Module
Fuzzy matching to link GST invoices, bank credits, and ONDC orders.
"""
import json
import os
from typing import Dict, List, Tuple
from datetime import datetime
from difflib import SequenceMatcher
from collections import defaultdict
from dateutil import parser as date_parser


def fuzzy_match(str1: str, str2: str) -> float:
    """Calculate similarity ratio between two strings (0-1)."""
    if not str1 or not str2:
        return 0.0
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def amount_match_score(amt1: float, amt2: float, tolerance: float = 0.05) -> float:
    """
    Calculate match score for amounts with tolerance.
    Returns 1.0 for exact match, decreases with difference.
    """
    if amt1 == 0 or amt2 == 0:
        return 0.0
    
    diff_pct = abs(amt1 - amt2) / max(amt1, amt2)
    if diff_pct <= tolerance:
        return 1.0 - (diff_pct / tolerance) * 0.3  # Small penalty for near matches
    else:
        return max(0, 1.0 - diff_pct)


def parse_date_flexible(date_str):
    """Parse various date formats."""
    if not date_str:
        return None
    try:
        return date_parser.parse(str(date_str))
    except:
        return None


def reconcile_transactions(customer_id: str, analytics_dir: str = None) -> Dict:
    """
    Perform fuzzy reconciliation between GST, Bank, and ONDC data.
    
    Returns:
        Dictionary with matched triplets and unmatched items
    """
    if analytics_dir is None:
        analytics_dir = os.path.dirname(__file__)
    
    print(f"\n[INFO] Reconciling transactions for {customer_id}")
    
    # Load data sources
    gst_file = os.path.join(analytics_dir, f'{customer_id}_gst_summary.json')
    transactions_file = os.path.join(analytics_dir, f'{customer_id}_transaction_summary.json')
    ondc_file = os.path.join(analytics_dir, f'{customer_id}_ondc_summary.json')
    earnings_file = os.path.join(analytics_dir, f'{customer_id}_earnings_spendings.json')
    
    try:
        with open(gst_file, 'r') as f:
            gst_data = json.load(f)
        with open(transactions_file, 'r') as f:
            txn_data = json.load(f)
        with open(ondc_file, 'r') as f:
            ondc_data = json.load(f)
        with open(earnings_file, 'r') as f:
            earnings_data = json.load(f)
    except FileNotFoundError as e:
        print(f"[ERROR] Required file not found: {e}")
        return {}
    
    # Extract GST monthly turnover
    gst_turnover = gst_data.get('monthly_gst_turnover', {})
    gst_entries = [{'month': k, 'amount': v, 'source': 'GST'} for k, v in gst_turnover.items()]
    
    # Extract bank credits by month
    monthly_inflow = earnings_data.get('cashflow_metrics', {}).get('monthly_inflow', {})
    bank_entries = [{'month': k, 'amount': v, 'source': 'BANK'} for k, v in monthly_inflow.items()]
    
    # Extract ONDC monthly orders
    ondc_monthly = defaultdict(float)
    # Note: ONDC data might not have monthly breakdown, so we use total_order_value
    ondc_total = ondc_data.get('total_order_value', 0)
    ondc_orders = ondc_data.get('total_orders', 0)
    ondc_entries = [{'total_value': ondc_total, 'total_orders': ondc_orders, 'source': 'ONDC'}]
    
    # Reconciliation matches
    matches = []
    unmatched_gst = []
    unmatched_bank = []
    
    # Match GST to Bank by month and amount
    for gst_entry in gst_entries:
        gst_month = gst_entry['month']
        gst_amount = gst_entry['amount']
        
        best_match = None
        best_score = 0.0
        
        for bank_entry in bank_entries:
            bank_month = bank_entry['month']
            bank_amount = bank_entry['amount']
            
            # Month similarity
            month_score = fuzzy_match(str(gst_month), str(bank_month))
            
            # Amount similarity
            amount_score = amount_match_score(gst_amount, bank_amount, tolerance=0.1)
            
            # Combined score (weighted)
            total_score = 0.4 * month_score + 0.6 * amount_score
            
            if total_score > best_score and total_score > 0.5:  # Minimum threshold
                best_score = total_score
                best_match = {
                    'gst': gst_entry,
                    'bank': bank_entry,
                    'match_score': round(total_score, 4),
                    'month_score': round(month_score, 4),
                    'amount_score': round(amount_score, 4),
                    'reconciliation_pct': round((gst_amount / bank_amount * 100) if bank_amount > 0 else 0, 2),
                    'difference': round(abs(gst_amount - bank_amount), 2)
                }
        
        if best_match:
            matches.append(best_match)
        else:
            unmatched_gst.append(gst_entry)
    
    # Find unmatched bank entries
    matched_bank_months = {m['bank']['month'] for m in matches}
    for bank_entry in bank_entries:
        if bank_entry['month'] not in matched_bank_months:
            unmatched_bank.append(bank_entry)
    
    # Summary statistics
    total_gst = sum(e['amount'] for e in gst_entries)
    total_bank = sum(e['amount'] for e in bank_entries)
    matched_gst = sum(m['gst']['amount'] for m in matches)
    matched_bank = sum(m['bank']['amount'] for m in matches)
    
    reconciliation_rate = (matched_gst / total_gst * 100) if total_gst > 0 else 0
    discrepancy_pct = abs(total_gst - total_bank) / max(total_gst, total_bank) * 100 if max(total_gst, total_bank) > 0 else 0
    
    # Risk assessment
    risk_flags = []
    if reconciliation_rate < 70:
        risk_flags.append('Low GST-to-Bank reconciliation rate (< 70%)')
    if discrepancy_pct > 20:
        risk_flags.append(f'High overall discrepancy: {discrepancy_pct:.1f}%')
    if len(unmatched_gst) > len(gst_entries) * 0.3:
        risk_flags.append('High number of unmatched GST entries')
    
    result = {
        'customer_id': customer_id,
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'summary': {
            'total_gst_entries': len(gst_entries),
            'total_bank_entries': len(bank_entries),
            'matches_found': len(matches),
            'unmatched_gst': len(unmatched_gst),
            'unmatched_bank': len(unmatched_bank),
            'reconciliation_rate': round(reconciliation_rate, 2),
            'discrepancy_pct': round(discrepancy_pct, 2)
        },
        'totals': {
            'total_gst_turnover': round(total_gst, 2),
            'total_bank_inflow': round(total_bank, 2),
            'matched_gst_amount': round(matched_gst, 2),
            'matched_bank_amount': round(matched_bank, 2),
            'difference': round(total_bank - total_gst, 2)
        },
        'matches': matches[:50],  # Top 50 matches
        'unmatched': {
            'gst': unmatched_gst[:20],
            'bank': unmatched_bank[:20]
        },
        'ondc_data': ondc_entries,
        'risk_assessment': {
            'risk_flags': risk_flags,
            'risk_level': 'High' if len(risk_flags) >= 2 else 'Medium' if risk_flags else 'Low'
        },
        'methodology': {
            'matching_algorithm': 'Fuzzy string matching + amount tolerance',
            'month_weight': 0.4,
            'amount_weight': 0.6,
            'match_threshold': 0.5,
            'amount_tolerance': '10%'
        }
    }
    
    # Save result
    output_file = os.path.join(analytics_dir, f'{customer_id}_reconciliation.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"[✓] Reconciliation saved to {output_file}")
    print(f"\n{'='*60}")
    print(f"RECONCILIATION SUMMARY")
    print(f"{'='*60}")
    print(f"GST Entries: {len(gst_entries)}")
    print(f"Bank Entries: {len(bank_entries)}")
    print(f"Matches Found: {len(matches)}")
    print(f"Reconciliation Rate: {reconciliation_rate:.2f}%")
    print(f"Total Discrepancy: {discrepancy_pct:.2f}%")
    print(f"\nRisk Level: {result['risk_assessment']['risk_level']}")
    if risk_flags:
        print(f"⚠️  Risk Flags:")
        for flag in risk_flags:
            print(f"  • {flag}")
    print(f"{'='*60}\n")
    
    return result


if __name__ == '__main__':
    import sys
    
    customer_id = sys.argv[1] if len(sys.argv) > 1 else 'CUST_MSM_00001'
    analytics_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(__file__)
    
    reconcile_transactions(customer_id, analytics_dir)
