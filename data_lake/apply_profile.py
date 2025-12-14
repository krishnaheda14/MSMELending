"""
Apply specialized profile modifications to existing customer data.
"""
import json
import os
import random
from datetime import datetime, timedelta

def load_transactions(txn_file):
    """Load transactions from NDJSON file."""
    transactions = []
    with open(txn_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    transactions.append(json.loads(line))
                except:
                    pass
    return transactions

def save_transactions(txn_file, transactions):
    """Save transactions to NDJSON file."""
    with open(txn_file, 'w', encoding='utf-8') as f:
        for txn in transactions:
            f.write(json.dumps(txn, ensure_ascii=False) + '\n')

def modify_transactions_for_high_seasonality(transactions):
    """Modify transactions to create high seasonal variation."""
    months = {}
    for txn in transactions:
        date = txn.get('date', '')
        month = date[:7] if date else '2025-01'
        if month not in months:
            months[month] = []
        months[month].append(txn)
    
    month_list = sorted(months.keys())
    for i, month in enumerate(month_list):
        if i % 3 == 0:  # Peak months
            multiplier = random.uniform(3.0, 5.0)
        elif i % 3 == 1:  # Medium months
            multiplier = random.uniform(0.8, 1.2)
        else:  # Low months
            multiplier = random.uniform(0.2, 0.4)
        
        for txn in months[month]:
            txn_type = str(txn.get('type', '')).upper()
            if txn_type in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
                try:
                    txn['amount'] = float(str(txn['amount']).replace(',', '')) * multiplier
                except:
                    pass
    
    return transactions

def modify_transactions_for_high_debt(transactions):
    """Add many loan repayment transactions (high debt)."""
    new_transactions = []
    base_date = datetime(2024, 1, 1)
    
    # Add 10% more debt transactions
    for i in range(len(transactions) // 10):
        txn_date = base_date + timedelta(days=random.randint(0, 365))
        new_transactions.append({
            'transaction_id': f'TXN_DEBT_{i:06d}',
            'date': txn_date.strftime('%Y-%m-%d'),
            'type': 'DEBIT',
            'amount': random.uniform(15000, 50000),
            'description': random.choice([
                'LOAN EMI PAYMENT',
                'BUSINESS LOAN REPAYMENT',
                'TERM LOAN EMI',
                'WORKING CAPITAL LOAN'
            ]),
            'category': 'LOAN_REPAYMENT',
            'narration': random.choice(['EMI PAYMENT', 'LOAN REPAYMENT', 'BUSINESS LOAN EMI']),
            'balance': random.uniform(50000, 500000)
        })
    
    print(f"  Added {len(new_transactions)} debt transactions")
    return transactions + new_transactions

def modify_transactions_for_high_growth(transactions):
    """Create strong growth trend: revenue increases over time (1x → 3x)."""
    from dateutil import parser as date_parser
    
    # Parse and sort by actual date
    parsed_txns = []
    for txn in transactions:
        date_str = txn.get('date')
        if not date_str:
            parsed_date = datetime(2000, 1, 1)  # Default for missing dates
        else:
            try:
                parsed_date = date_parser.parse(str(date_str), dayfirst=False)
            except:
                parsed_date = datetime(2000, 1, 1)
        parsed_txns.append((parsed_date, txn))
    
    # Sort by parsed date
    parsed_txns.sort(key=lambda x: x[0])
    sorted_txns = [t[1] for t in parsed_txns]

    for i, txn in enumerate(sorted_txns):
        txn_type = str(txn.get('type', '')).upper()
        if txn_type in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
            # Create strong growth: shrink early amounts, amplify late amounts
            # This creates growth trend regardless of original data pattern
            try:
                length = max(1, len(sorted_txns))
                # Aggressive multiplier: 0.3x → 3.0x (10x growth ratio)
                growth_factor = 0.3 + ((i / length) * 2.7)  # 0.3x early → 3.0x late
                txn_amount = txn.get('amount')
                if txn_amount in (None, ''):
                    continue
                txn['amount'] = float(str(txn_amount).replace(',', '')) * growth_factor
            except Exception:
                pass

    return sorted_txns

def modify_transactions_for_stable_income(transactions):
    """Create very stable monthly income pattern."""
    months = {}
    for txn in transactions:
        date = txn.get('date', '')
        month = date[:7] if date else '2025-01'
        if month not in months:
            months[month] = []
        months[month].append(txn)
    
    # Calculate average credit
    monthly_credits = {}
    for month, txns in months.items():
        credits = []
        for t in txns:
            txn_type = str(t.get('type', '')).upper()
            if txn_type in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
                try:
                    credits.append(float(str(t['amount']).replace(',', '')))
                except:
                    pass
        if credits:
            monthly_credits[month] = sum(credits) / len(credits)
    
    avg_credit = sum(monthly_credits.values()) / len(monthly_credits) if monthly_credits else 50000
    
    # Normalize all credits
    for txn in transactions:
        txn_type = str(txn.get('type', '')).upper()
        if txn_type in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
            txn['amount'] = avg_credit * random.uniform(0.95, 1.05)
    
    return transactions

def modify_transactions_for_high_bounce(transactions):
    """Add failed transactions."""
    failed_count = 0
    for txn in transactions:
        txn_type = str(txn.get('type', '')).upper()
        if txn_type in ['DEBIT', 'DR', 'D', 'WITHDRAWAL']:
            if random.random() < 0.07:
                txn['status'] = 'FAILED'
                txn['failure_reason'] = random.choice([
                    'INSUFFICIENT_FUNDS',
                    'PAYMENT_DECLINED',
                    'ACCOUNT_BLOCKED'
                ])
                txn['narration'] = str(txn.get('narration', '')) + ' - BOUNCE'
                txn['description'] = str(txn.get('description', '')) + ' - FAILED'
                failed_count += 1
    
    print(f"  Marked {failed_count} transactions as failed")
    return transactions

def modify_transactions_for_declining_business(transactions):
    """Create declining revenue trend."""
    from dateutil import parser as date_parser
    
    # Parse and sort by actual date
    parsed_txns = []
    for txn in transactions:
        date_str = txn.get('date')
        if not date_str:
            parsed_date = datetime(2000, 1, 1)
        else:
            try:
                parsed_date = date_parser.parse(str(date_str), dayfirst=False)
            except:
                parsed_date = datetime(2000, 1, 1)
        parsed_txns.append((parsed_date, txn))
    
    # Sort by parsed date
    parsed_txns.sort(key=lambda x: x[0])
    sorted_txns = [t[1] for t in parsed_txns]

    for i, txn in enumerate(sorted_txns):
        txn_type = str(txn.get('type', '')).upper()
        if txn_type in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
            try:
                length = max(1, len(sorted_txns))
                decline_factor = 1.5 - (i / length) * 1.3  # 1.5x to ~0.2x
                txn_amount = txn.get('amount')
                if txn_amount in (None, ''):
                    continue
                txn['amount'] = float(str(txn_amount).replace(',', '')) * max(0.2, decline_factor)
            except Exception:
                pass

    return sorted_txns

def modify_transactions_for_customer_concentration(transactions):
    """Concentrate income from 2-3 major customers."""
    credit_txns = []
    for t in transactions:
        txn_type = str(t.get('type', '')).upper()
        if txn_type in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
            credit_txns.append(t)
    
    major_customers = [f'MajorClient-{i:03d}' for i in range(1, 4)]
    
    # 70% of credits from major customers
    if credit_txns:
        major_count = int(len(credit_txns) * 0.7)
        major_customer_txns = random.sample(credit_txns, k=major_count)
        
        for txn in major_customer_txns:
            customer = random.choice(major_customers)
            txn['counterparty_account'] = customer
            txn['merchant_name'] = customer
            try:
                txn['amount'] = float(str(txn['amount']).replace(',', '')) * random.uniform(1.5, 3.0)
            except:
                pass
        
        print(f"  Concentrated {major_count} transactions to top 3 customers")
    
    return transactions

def apply_profile(customer_id, profile_type):
    """Apply profile modification to customer data."""
    print(f"\n{'='*80}")
    print(f"  Applying {profile_type} profile to {customer_id}")
    print(f"{'='*80}")
    
    txn_file = 'raw/raw_transactions_with_customer_id.ndjson'
    if not os.path.exists(txn_file):
        print(f"  ❌ File not found: {txn_file}")
        return False
    
    print(f"  Loading all transactions...")
    all_transactions = load_transactions(txn_file)
    
    # CRITICAL FIX: Filter by customer_id
    customer_transactions = [t for t in all_transactions if t.get('customer_id') == customer_id]
    other_transactions = [t for t in all_transactions if t.get('customer_id') != customer_id]
    
    print(f"  Found {len(customer_transactions)} transactions for {customer_id}")
    print(f"  Keeping {len(other_transactions)} transactions for other customers")
    
    if not customer_transactions:
        print(f"  ⚠️  No transactions found for {customer_id}. Run generation first!")
        return False
    
    # Apply modification ONLY to this customer's transactions
    if profile_type == 'high_seasonality':
        customer_transactions = modify_transactions_for_high_seasonality(customer_transactions)
    elif profile_type == 'high_debt':
        customer_transactions = modify_transactions_for_high_debt(customer_transactions)
    elif profile_type == 'high_growth':
        customer_transactions = modify_transactions_for_high_growth(customer_transactions)
    elif profile_type == 'stable_income':
        customer_transactions = modify_transactions_for_stable_income(customer_transactions)
    elif profile_type == 'high_bounce':
        customer_transactions = modify_transactions_for_high_bounce(customer_transactions)
    elif profile_type == 'declining':
        customer_transactions = modify_transactions_for_declining_business(customer_transactions)
    elif profile_type == 'customer_concentration':
        customer_transactions = modify_transactions_for_customer_concentration(customer_transactions)
    
    # Merge back: keep other customers' data + modified customer data
    all_transactions = other_transactions + customer_transactions
    
    print(f"  Saving all transactions ({len(all_transactions)} total)...")
    save_transactions(txn_file, all_transactions)
    print(f"  ✅ Saved {len(customer_transactions)} modified transactions for {customer_id}")
    
    return True

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        customer_id = sys.argv[1]
        profile_type = sys.argv[2] if len(sys.argv) > 2 else 'high_seasonality'
        apply_profile(customer_id, profile_type)
    else:
        print("Usage: python apply_profile.py <customer_id> <profile_type>")
