"""
Generate specialized customer profiles with specific characteristics.
Keeps random base data but modifies specific fields to create desired behaviors.
"""
import json
import os
import sys
import random
from datetime import datetime, timedelta

def modify_transactions_for_high_seasonality(transactions):
    """Modify transactions to create high seasonal variation."""
    # Group by month and amplify differences
    months = {}
    for txn in transactions:
        date = txn.get('date', '')
        month = date[:7] if date else '2025-01'
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
            if txn.get('type', '').upper() in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
                txn['amount'] = float(txn['amount']) * multiplier
    
    return transactions

def modify_transactions_for_high_debt(transactions):
    """Add many loan repayment transactions (high debt)."""
    # Increase DEBIT transactions, especially loan-related
    new_transactions = []
    base_date = datetime(2024, 1, 1)
    
    for i in range(len(transactions) // 10):  # Add 10% more debt transactions
        txn_date = base_date + timedelta(days=random.randint(0, 365))
        new_transactions.append({
            'transaction_id': f'TXN_DEBT_{i:06d}',
            'date': txn_date.strftime('%Y-%m-%d'),
            'type': 'DEBIT',
            'amount': random.uniform(15000, 50000),  # High EMI amounts
            'description': random.choice([
                'LOAN EMI PAYMENT',
                'BUSINESS LOAN REPAYMENT',
                'TERM LOAN EMI',
                'WORKING CAPITAL LOAN'
            ]),
            'category': 'LOAN_REPAYMENT',
            'balance': random.uniform(50000, 500000)
        })
    
    return transactions + new_transactions

def modify_transactions_for_high_growth(transactions):
    """Create strong growth trend - increasing credits over time."""
    sorted_txns = sorted(transactions, key=lambda x: x.get('date', ''))
    
    for i, txn in enumerate(sorted_txns):
        if txn.get('type', '').upper() in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
            # Growth multiplier based on position in time
            growth_factor = 1.0 + (i / len(sorted_txns)) * 2.0  # 1x to 3x growth
            txn['amount'] = float(txn['amount']) * growth_factor
    
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
    
    # Calculate average credit per month
    monthly_credits = {}
    for month, txns in months.items():
        credits = [float(t['amount']) for t in txns if t.get('type', '').upper() in ['CREDIT', 'CR', 'C', 'DEPOSIT']]
        if credits:
            monthly_credits[month] = sum(credits) / len(credits)
    
    avg_credit = sum(monthly_credits.values()) / len(monthly_credits) if monthly_credits else 50000
    
    # Normalize all credit transactions to be close to average
    for txn in transactions:
        if txn.get('type', '').upper() in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
            # Keep within ±10% of average
            txn['amount'] = avg_credit * random.uniform(0.95, 1.05)
    
    return transactions

def modify_transactions_for_high_bounce(transactions):
    """Add failed transactions (bounced payments)."""
    failed_count = 0
    for txn in transactions:
        # Mark 5-8% of DEBIT transactions as failed
        if txn.get('type', '').upper() in ['DEBIT', 'DR', 'D', 'WITHDRAWAL']:
            if random.random() < 0.07:  # 7% failure rate
                txn['status'] = 'FAILED'
                txn['failure_reason'] = random.choice([
                    'INSUFFICIENT_FUNDS',
                    'PAYMENT_DECLINED',
                    'ACCOUNT_BLOCKED',
                    'TECHNICAL_ERROR'
                ])
                failed_count += 1
    
    print(f"  Added {failed_count} failed transactions")
    return transactions

def modify_transactions_for_declining_business(transactions):
    """Create declining revenue trend."""
    sorted_txns = sorted(transactions, key=lambda x: x.get('date', ''))
    
    for i, txn in enumerate(sorted_txns):
        if txn.get('type', '').upper() in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
            # Declining multiplier
            decline_factor = 1.5 - (i / len(sorted_txns)) * 1.3  # 1.5x to 0.2x (declining)
            txn['amount'] = float(txn['amount']) * max(0.2, decline_factor)
    
    return sorted_txns

def modify_transactions_for_high_customer_concentration(transactions):
    """Concentrate most income from 2-3 customers."""
    credit_txns = [t for t in transactions if t.get('type', '').upper() in ['CREDIT', 'CR', 'C', 'DEPOSIT']]
    
    # Pick 3 major customers
    major_customers = [f'MajorClient-{i:03d}' for i in range(1, 4)]
    
    # 70% of credit transactions go to these 3 customers
    major_customer_txns = random.sample(credit_txns, k=int(len(credit_txns) * 0.7))
    
    for txn in major_customer_txns:
        txn['counterparty_account'] = random.choice(major_customers)
        txn['merchant_name'] = random.choice(major_customers)
        # Increase amounts for concentration
        txn['amount'] = float(txn['amount']) * random.uniform(1.5, 3.0)
    
    return transactions

def apply_customer_profile(customer_id, profile_type):
    """Apply specific characteristics to a customer's data."""
    print(f"\n{'='*80}")
    print(f"  Applying profile: {profile_type} to {customer_id}")
    print(f"{'='*80}")
    
    # Load raw transactions
    txn_file = f'raw/raw_transactions.ndjson'
    if not os.path.exists(txn_file):
        print(f"  ❌ Transactions file not found: {txn_file}")
        return False
    
    transactions = []
    with open(txn_file, 'r') as f:
        for line in f:
            if line.strip():
                transactions.append(json.loads(line))
    
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
    elif profile_type == 'customer_concentration':
        transactions = modify_transactions_for_high_customer_concentration(transactions)
    
    # Save modified transactions
    with open(txn_file, 'w') as f:
        for txn in transactions:
            f.write(json.dumps(txn) + '\n')
    
    print(f"  ✅ Modified {len(transactions)} transactions")
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
    print("  ✅ ALL SPECIALIZED PROFILES GENERATED")
    print("="*80)

if __name__ == '__main__':
    main()
