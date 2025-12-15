"""
Generate specialized customer profiles with specific characteristics.
Keeps random base data but modifies specific fields to create desired behaviors.
"""
import json
import os
import sys
import random
import statistics
from datetime import datetime, timedelta


def _parse_month_from_date(date_str):
    """Return YYYY-MM for a variety of input date formats."""
    if not date_str:
        return None
    # Common ISO format
    try:
        if isinstance(date_str, str) and len(date_str) >= 7 and date_str[0:4].isdigit() and date_str[4] == '-':
            return date_str[:7]
    except Exception:
        pass

    # Try common formats
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d', '%d-%m-%y', '%d/%m/%y'):
        try:
            dt = datetime.strptime(date_str, fmt)
            return f"{dt.year:04d}-{dt.month:02d}"
        except Exception:
            continue

    # Fallback: try splitting slashes
    if '/' in date_str:
        parts = date_str.split('/')
        if len(parts) >= 3:
            d, m, y = parts[0], parts[1], parts[2]
            try:
                y = int(y)
                if y < 100:
                    y += 2000
                return f"{y:04d}-{int(m):02d}"
            except Exception:
                return None

    return None

def modify_transactions_for_high_seasonality(transactions):
    """Modify transactions to create high seasonal variation."""
    # Group by month and amplify differences
    months = {}
    for txn in transactions:
        date = txn.get('date', '')
        month = _parse_month_from_date(date) or '2025-01'
        if month not in months:
            months[month] = []
        months[month].append(txn)
    
    # Create extreme seasonality: some months very high, some very low
    month_list = sorted(months.keys())
    for i, month in enumerate(month_list):
        if i % 3 == 0:  # Every 3rd month is peak
            multiplier = random.uniform(3.0, 5.0)
        elif i % 3 == 1:  # Every other month is medium
            multiplier = random.uniform(0.8, 1.2)
        else:  # Remaining months are low
            multiplier = random.uniform(0.2, 0.4)
        
        for txn in months[month]:
            txn_type = txn.get('type', '')
            if txn_type and str(txn_type).upper() in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
                try:
                    txn['amount'] = float(txn['amount']) * multiplier
                except (ValueError, TypeError):
                    pass
    
    return transactions

def modify_transactions_for_high_debt(transactions):
    """Add many loan repayment transactions (high debt)."""
    if not transactions:
        return transactions
    
    # Get customer_id from existing transactions
    customer_id = transactions[0].get('customer_id', 'UNKNOWN')
    
    # Increase DEBIT transactions, especially loan-related
    new_transactions = []
    base_date = datetime(2024, 1, 1)
    
    # Add 40 loan EMI transactions to push DSR >40%
    for i in range(40):
        txn_date = base_date + timedelta(days=random.randint(0, 365))
        new_transactions.append({
            'transaction_id': f'TXN_LOAN_{customer_id}_{i:06d}',
            'customer_id': customer_id,
            'date': txn_date.strftime('%Y-%m-%d'),
            'type': 'DEBIT',
            'amount': random.uniform(35000, 75000),  # Very high EMI amounts
            'description': random.choice([
                'LOAN EMI PAYMENT',
                'BUSINESS LOAN REPAYMENT',
                'TERM LOAN EMI',
                'WORKING CAPITAL LOAN',
                'E.M.I DEBIT',
                'LOAN INSTALLMENT',
                'EMI PAYMENT TO HDFC',
                'BUSINESS LOAN EMI ICICI'
            ]),
            'category': 'LOAN_REPAYMENT',
            'balance': random.uniform(50000, 500000)
        })
    
    print(f"  Added {len(new_transactions)} high-value loan EMI transactions")
    return transactions + new_transactions

def modify_transactions_for_high_growth(transactions):
    """Create strong growth trend - increasing credits over time."""
    # Apply month-wise increasing multipliers to credit transactions
    months = {}
    for txn in transactions:
        date = txn.get('date', '')
        month = _parse_month_from_date(date)
        if not month:
            continue
        if month not in months:
            months[month] = []
        txn_type = txn.get('type', '')
        if txn_type and str(txn_type).upper() in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
            months[month].append(txn)

    if not months:
        return transactions

    month_list = sorted(months.keys())
    n = len(month_list)
    start = 1.0
    end = 3.5
    for i, month in enumerate(month_list):
        if n > 1:
            factor = start + (i / (n - 1)) * (end - start)
        else:
            factor = (start + end) / 2

        for txn in months[month]:
            try:
                txn['amount'] = float(txn.get('amount', 0)) * factor
            except (ValueError, TypeError):
                pass

    print(f"  Applied month-wise growth trend ({start:.2f}x to {end:.2f}x)")
    # Ensure last-month total is meaningfully higher than first-month total (>50% growth)
    try:
        first = month_list[0]
        last = month_list[-1]
        first_total = sum([float(t.get('amount', 0) or 0) for t in months.get(first, [])])
        last_total = sum([float(t.get('amount', 0) or 0) for t in months.get(last, [])])
        desired_last = max(last_total, first_total * 1.6)
        if last_total < desired_last:
            missing = desired_last - last_total
            # add top-up credits spread across the last 2-3 months (safer than only last month)
            customer_id = transactions[0].get('customer_id') if transactions else 'UNKNOWN'
            months_to_boost = []
            if n >= 3:
                months_to_boost = [month_list[-3], month_list[-2], month_list[-1]]
            elif n == 2:
                months_to_boost = [month_list[-2], month_list[-1]]
            else:
                months_to_boost = [last]

            parts = len(months_to_boost) * 2
            per_amt = missing / parts if parts else missing
            added = 0
            for m in months_to_boost:
                base_date = m + '-10'
                for i in range(2):
                    new_txn = {
                        'transaction_id': f'GROWTH_TOPUP_{customer_id}_{m}_{i:02d}',
                        'customer_id': customer_id,
                        'date': base_date,
                        'type': 'CREDIT',
                        'amount': per_amt * random.uniform(0.995, 1.005),
                        'description': 'INCREASED MONTH-END RECEIPT FOR GROWTH',
                        'category': 'SALES',
                        'balance': 0
                    }
                    transactions.append(new_txn)
                    months.setdefault(m, []).append(new_txn)
                    added += 1
            print(f"  Added {added} top-up credits across last months to ensure >50% growth")
    except Exception:
        pass

    return transactions

def modify_transactions_for_stable_income(transactions):
    """Create very stable monthly income pattern."""
    # Stabilize monthly credit totals (instead of individual txns) to reduce CV
    months = {}
    for txn in transactions:
        date = txn.get('date', '')
        month = _parse_month_from_date(date)
        txn_type = txn.get('type', '')
        if month and txn_type and str(txn_type).upper() in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
            months.setdefault(month, []).append(txn)

    if not months:
        return transactions

    monthly_totals = []
    for month, txns in months.items():
        total = sum([float(t.get('amount', 0) or 0) for t in txns])
        monthly_totals.append(total)

    # Use median to avoid extreme months skewing target
    target = statistics.median(monthly_totals) if monthly_totals else 0
    if target <= 0:
        return transactions

    # Ensure a continuous month range from earliest to latest month
    month_keys = sorted(months.keys())
    min_month = month_keys[0]
    max_month = month_keys[-1]

    def month_iter(start_ym, end_ym):
        y, m = map(int, start_ym.split('-'))
        ey, em = map(int, end_ym.split('-'))
        while (y, m) <= (ey, em):
            yield f"{y:04d}-{m:02d}"
            m += 1
            if m > 12:
                m = 1
                y += 1

    # For each month in the range, ensure totals ~= target and transaction-level uniformity
    customer_id = None
    if transactions:
        customer_id = transactions[0].get('customer_id')

    for month in month_iter(min_month, max_month):
        txns = months.get(month, [])
        current_total = sum([float(t.get('amount', 0) or 0) for t in txns])
        desired = target * random.uniform(0.995, 1.005)

        if current_total < desired * 0.98:
            # Add new credit transactions to reach desired total
            remaining = desired - current_total
            # Create 2-4 uniform transactions per month
            parts = max(2, min(4, int(len(txns) or 2)))
            per_amt = remaining / parts
            base_date = month + '-10'
            for i in range(parts):
                new_txn = {
                    'transaction_id': f'STABLE_ADD_{customer_id}_{month}_{i:02d}',
                    'customer_id': customer_id or 'UNKNOWN',
                    'date': base_date,
                    'type': 'CREDIT',
                    'amount': per_amt * random.uniform(0.995, 1.005),
                    'description': 'STABLE MONTHLY CREDIT',
                    'category': 'SALARY',
                    'balance': 0
                }
                transactions.append(new_txn)
                months.setdefault(month, []).append(new_txn)

        else:
            # If current_total >= desired * 0.98, smooth existing txns to uniform per-txn amounts
            if txns:
                per_txn = desired / max(1, len(txns))
                for t in txns:
                    try:
                        t['amount'] = per_txn * random.uniform(0.995, 1.005)
                    except (ValueError, TypeError):
                        pass

    print(f"  Stabilized monthly credit totals to median {target:,.0f} ±0.5% and smoothed transactions")
    return transactions


def _get_monthly_target_from_transactions(transactions):
    """Compute median monthly credit total for given transactions."""
    months = {}
    for txn in transactions:
        date = txn.get('date', '')
        month = _parse_month_from_date(date)
        txn_type = txn.get('type', '')
        if month and txn_type and str(txn_type).upper() in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
            months.setdefault(month, []).append(txn)

    if not months:
        return 0

    monthly_totals = [sum([float(t.get('amount', 0) or 0) for t in txns]) for txns in months.values()]
    return statistics.median(monthly_totals) if monthly_totals else 0


def _adjust_gst_for_target(customer_id, target_monthly):
    """Scale or add GST returns for `customer_id` so monthly turnover approximates `target_monthly`.
    This is a light-touch adjustment: scales existing 'turnover' and 'taxable_value' fields proportionally.
    """
    gst_path = os.path.join('raw', 'raw_gst.ndjson')
    if not os.path.exists(gst_path):
        print(f"  [WARN] GST file not found: {gst_path}")
        return

    updated = []
    changed = 0
    with open(gst_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except Exception:
                updated.append(line)
                continue

            if rec.get('customer_id') == customer_id:
                # Prefer 'turnover' or 'total_taxable_value'
                if 'turnover' in rec and isinstance(rec['turnover'], (int, float)):
                    # scale turnover to target_monthly with small random smoothing
                    rec['turnover'] = target_monthly * random.uniform(0.98, 1.02)
                elif 'total_taxable_value' in rec:
                    try:
                        # keep as string if original file used strings
                        rec['total_taxable_value'] = str(int(target_monthly * random.uniform(0.95, 1.05)))
                    except Exception:
                        rec['total_taxable_value'] = rec.get('total_taxable_value')

                if 'taxable_value' in rec and isinstance(rec['taxable_value'], (int, float)):
                    rec['taxable_value'] = target_monthly * random.uniform(0.9, 1.05)

                changed += 1

            updated.append(json.dumps(rec))

    # Write back
    with open(gst_path, 'w', encoding='utf-8') as f:
        for r in updated:
            if isinstance(r, str):
                f.write(r + '\n')
            else:
                f.write(json.dumps(r) + '\n')

    print(f"  Adjusted {changed} GST records for {customer_id} to align with target monthly {target_monthly:,.0f}")


def _adjust_ondc_for_target(customer_id, target_monthly):
    """Adjust ONDC orders for `customer_id` so total order value across recent months approximates target_monthly.
    Scales numeric amount fields found in ONDC orders (e.g., 'total_amount', 'order_value', 'quote').
    """
    ondc_path = os.path.join('raw', 'raw_ondc_orders.ndjson')
    if not os.path.exists(ondc_path):
        print(f"  [WARN] ONDC file not found: {ondc_path}")
        return

    updated = []
    changed = 0
    with open(ondc_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except Exception:
                updated.append(line)
                continue

            if rec.get('user_id') == customer_id or rec.get('customer_id') == customer_id or (rec.get('order_id') or '').find(customer_id[-5:]) != -1:
                # Try common fields
                scaled = False
                for fld in ('total_amount', 'order_value', 'amount', 'price'):
                    if fld in rec and isinstance(rec[fld], (int, float)):
                        # make ONDC per-order values a fraction of monthly target
                        rec[fld] = target_monthly * random.uniform(0.05, 0.2)
                        scaled = True

                # Try nested quote.price
                if not scaled and isinstance(rec.get('quote'), dict):
                    q = rec['quote']
                    if 'price' in q and isinstance(q['price'], (int, float)):
                        q['price'] = target_monthly * random.uniform(0.05, 0.2)
                        rec['quote'] = q

                changed += 1

            updated.append(json.dumps(rec))

    with open(ondc_path, 'w', encoding='utf-8') as f:
        for r in updated:
            if isinstance(r, str):
                f.write(r + '\n')
            else:
                f.write(json.dumps(r) + '\n')

    print(f"  Adjusted {changed} ONDC records for {customer_id} to align with target monthly {target_monthly:,.0f}")

def modify_transactions_for_high_bounce(transactions):
    """Add failed/bounced transactions."""
    if not transactions:
        return transactions
    
    customer_id = transactions[0].get('customer_id', 'UNKNOWN')
    base_date = datetime(2024, 1, 1)
    
    # Add 15 explicit bounce transactions
    bounce_txns = []
    for i in range(15):
        txn_date = base_date + timedelta(days=random.randint(0, 365))
        bounce_txns.append({
            'transaction_id': f'TXN_BOUNCE_{customer_id}_{i:06d}',
            'customer_id': customer_id,
            'date': txn_date.strftime('%Y-%m-%d'),
            'type': 'DEBIT',
            'amount': random.uniform(5000, 25000),
            'description': random.choice([
                'PAYMENT BOUNCED INSUFFICIENT FUNDS',
                'CHEQUE DISHONOURED',
                'PAYMENT FAILED - INSUFFICIENT BALANCE',
                'TRANSACTION REJECTED',
                'BOUNCED PAYMENT',
                'CHEQUE RETURN - INSUFFICIENT FUNDS',
                'PAYMENT DISHONOUR CHARGES',
                'FAILED TRANSACTION'
            ]),
            'status': 'FAILED',
            'category': 'BOUNCE',
            'balance': random.uniform(0, 5000)
        })
    
    print(f"  Added {len(bounce_txns)} bounced/failed transactions")
    return transactions + bounce_txns

def modify_transactions_for_declining_business(transactions):
    """Create declining revenue trend."""
    # Apply month-wise declining multipliers to credit transactions to ensure clear negative trend
    months = {}
    for txn in transactions:
        date = txn.get('date', '')
        month = _parse_month_from_date(date)
        if not month:
            continue
        txn_type = txn.get('type', '')
        if txn_type and str(txn_type).upper() in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
            months.setdefault(month, []).append(txn)

    if not months:
        return transactions

    month_list = sorted(months.keys())
    n = len(month_list)
    start = 3.5
    end = 0.25
    for i, month in enumerate(month_list):
        if n > 1:
            factor = start - (i / (n - 1)) * (start - end)
        else:
            factor = (start + end) / 2

        for txn in months[month]:
            try:
                txn['amount'] = float(txn.get('amount', 0)) * factor
            except (ValueError, TypeError):
                pass

    print(f"  Applied month-wise declining trend ({start:.2f}x to {end:.2f}x)")
    return transactions

def modify_transactions_for_high_customer_concentration(transactions):
    """Concentrate revenue into a single major customer (75%+)."""
    # Identify credit transactions
    credit_txns = []
    for txn in transactions:
        txn_type = txn.get('type', '')
        if txn_type and str(txn_type).upper() in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
            credit_txns.append(txn)
    
    if not credit_txns:
        return transactions
    
    # Assign 80% of transactions to one major customer
    major_customer = 'MegaCorp Industries Ltd'
    major_customer_txns = random.sample(credit_txns, k=min(int(len(credit_txns) * 0.8), len(credit_txns)))
    
    for txn in major_customer_txns:
        txn['counterparty_account'] = major_customer
        txn['merchant_name'] = major_customer
        # Increase amounts significantly for concentration
        try:
            txn['amount'] = float(txn['amount']) * random.uniform(3.0, 5.0)
        except (ValueError, TypeError):
            pass
    
    print(f"  Concentrated {len(major_customer_txns)} transactions to {major_customer}")
    return transactions

def apply_customer_profile(customer_id, profile_type):
    """Apply specific characteristics to a customer's data."""
    print(f"\n{'='*80}")
    print(f"  Applying profile: {profile_type} to {customer_id}")
    print(f"{'='*80}")
    
    # Load raw transactions (use the customer_id version)
    txn_file = 'raw/raw_transactions_with_customer_id.ndjson'
    if not os.path.exists(txn_file):
        print(f"  [ERROR] Transactions file not found: {txn_file}")
        return False
    
    transactions = []
    with open(txn_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    txn = json.loads(line)
                    # Validate transaction is a proper dict and belongs to this customer
                    if txn and isinstance(txn, dict) and txn.get('customer_id') == customer_id:
                        transactions.append(txn)
                except (json.JSONDecodeError, TypeError):
                    continue  # Skip invalid lines
    
    print(f"  Loaded {len(transactions)} transactions")
    
    # Apply modifications based on profile
    if profile_type == 'high_seasonality':
        transactions = modify_transactions_for_high_seasonality(transactions)
    elif profile_type == 'high_debt':
        transactions = modify_transactions_for_high_debt(transactions)
    elif profile_type == 'high_growth':
        transactions = modify_transactions_for_high_growth(transactions)
    elif profile_type == 'stable_income':
        transactions = modify_transactions_for_stable_income(transactions)
    elif profile_type == 'high_bounce':
        transactions = modify_transactions_for_high_bounce(transactions)
    elif profile_type == 'declining':
        transactions = modify_transactions_for_declining_business(transactions)
    elif profile_type in ['customer_concentration', 'concentration']:
        transactions = modify_transactions_for_high_customer_concentration(transactions)
    else:
        print(f"  [INFO] No profile modification for {profile_type}, using baseline data")

    # Cross-source normalization: for stable income and growth, adjust GST/ONDC files too
    try:
        if profile_type == 'stable_income':
            target = _get_monthly_target_from_transactions(transactions)
            if target and target > 0:
                _adjust_gst_for_target(customer_id, target)
                _adjust_ondc_for_target(customer_id, target)

        if profile_type == 'high_growth':
            # Ensure ONDC/GST reflect increased recent receipts as well
            target = _get_monthly_target_from_transactions(transactions)
            # use a boosted target so ONDC/GST reflect growth signal
            if target and target > 0:
                boosted = target * 1.4
                _adjust_gst_for_target(customer_id, boosted)
                _adjust_ondc_for_target(customer_id, boosted)
    except Exception:
        print("  [WARN] Cross-source normalization failed; continuing with transactions only")
    
    # Ensure new transactions have customer_id
    for txn in transactions:
        if 'customer_id' not in txn:
            txn['customer_id'] = customer_id
    
    # Read ALL transactions, replace this customer's, and write back
    all_transactions = []
    with open(txn_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    txn = json.loads(line)
                    # Keep transactions from OTHER customers
                    if txn.get('customer_id') != customer_id:
                        all_transactions.append(txn)
                except (json.JSONDecodeError, TypeError):
                    continue
    
    # Add this customer's modified transactions
    all_transactions.extend(transactions)
    
    # Write back all transactions
    with open(txn_file, 'w', encoding='utf-8') as f:
        for txn in all_transactions:
            f.write(json.dumps(txn) + '\n')
    
    print(f"  [OK] Modified {len(transactions)} transactions for {customer_id}")
    return True

def main():
    """Generate all specialized customer profiles."""
    
    # Profile mapping
    profiles = {
        'CUST_MSM_00002': 'high_seasonality',
        'CUST_MSM_00003': 'high_debt', 
        'CUST_MSM_00004': 'high_growth',
        'CUST_MSM_00005': 'stable_income',
        'CUST_MSM_00006': 'high_bounce',
        'CUST_MSM_00007': 'declining',
        'CUST_MSM_00008': 'customer_concentration',
        'CUST_MSM_00009': 'high_growth',  # Another growth example
        'CUST_MSM_00010': 'high_seasonality',  # Another seasonal example
    }
    
    print("="*80)
    print("  SPECIALIZED CUSTOMER PROFILE GENERATOR")
    print("="*80)
    print(f"  Generating {len(profiles)} specialized customer profiles")
    print("="*80)
    
    for customer_id, profile_type in profiles.items():
        # First, generate base random data
        print(f"\n[1/2] Generating base data for {customer_id}...")
        os.system(f'python generate_all.py --customer-id {customer_id}')
        
        # Then, apply specialized modifications
        print(f"\n[2/2] Applying {profile_type} profile...")
        os.environ['CUSTOMER_ID'] = customer_id
        apply_customer_profile(customer_id, profile_type)
        
        # Regenerate analytics with modified data
        print(f"\n[3/3] Regenerating analytics...")
        os.system(f'python analytics/generate_summaries.py --customer-id {customer_id}')
    
    print("\n" + "="*80)
    print("  [OK] ALL SPECIALIZED PROFILES GENERATED")
    print("="*80)

if __name__ == '__main__':
    main()
