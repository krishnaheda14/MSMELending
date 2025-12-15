"""
Regenerate ALL customer profiles with FOCUSED characteristics.
Each customer should have ONE primary issue that stands out prominently.
Other metrics should remain normal/reasonable.
"""
import json
import os
import random
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict

# Profile definitions - each customer gets ONE focused issue
CUSTOMER_PROFILES = {
    'CUST_MSM_00001': {
        'profile': 'baseline',
        'description': 'Normal healthy business - all metrics reasonable',
        'modifications': {}
    },
    'CUST_MSM_00002': {
        'profile': 'high_seasonality',
        'description': 'High seasonal variation in income (>100% seasonality index)',
        'focus_metric': 'Seasonality Index',
        'modifications': {
            'seasonality_multipliers': [4.5, 1.0, 0.3, 5.0, 1.2, 0.25, 4.0, 1.0, 0.4, 5.5, 1.5, 0.2]
        }
    },
    'CUST_MSM_00003': {
        'profile': 'high_debt',
        'description': 'High debt service ratio (DSR > 40%)',
        'focus_metric': 'Debt Service Ratio',
        'modifications': {
            'add_loan_emis': True,
            'emi_count': 25,  # Add 25 EMI transactions per month
            'emi_amount_range': (18000, 45000)
        }
    },
    'CUST_MSM_00004': {
        'profile': 'high_growth',
        'description': 'Strong revenue growth trend (50-100%+ growth)',
        'focus_metric': 'Credit Growth Rate',
        'modifications': {
            'growth_trend': 'exponential',
            'growth_rate': 2.5  # 2.5x growth over period
        }
    },
    'CUST_MSM_00005': {
        'profile': 'stable_income',
        'description': 'Very stable, predictable income (CV < 15%)',
        'focus_metric': 'Income Stability',
        'modifications': {
            'stabilize_credits': True,
            'variance_limit': 0.08  # ±8% variation max
        }
    },
    'CUST_MSM_00006': {
        'profile': 'fraud',  # High bounce rate
        'description': 'High bounce rate (5-8% transaction failure)',
        'focus_metric': 'Bounce Count',
        'modifications': {
            'add_bounces': True,
            'bounce_rate': 0.065,  # 6.5% of debits fail
            'bounce_keywords': ['BOUNCE', 'FAILED', 'INSUFFICIENT FUNDS', 'DISHONOURED']
        }
    },
    'CUST_MSM_00007': {
        'profile': 'declining',
        'description': 'Declining business trend (-30% to -80%)',
        'focus_metric': 'Declining Revenue',
        'modifications': {
            'decline_trend': True,
            'decline_rate': 0.4  # Decline to 40% of original
        }
    },
    'CUST_MSM_00008': {
        'profile': 'customer_concentration',
        'description': 'High customer concentration (top customer >65%)',
        'focus_metric': 'Customer Concentration',
        'modifications': {
            'concentrate_customers': True,
            'top_1_concentration': 0.70,  # 70% from top customer
            'top_3_concentration': 0.85  # 85% from top 3
        }
    },
    'CUST_MSM_00009': {
        'profile': 'high_growth',
        'description': 'Another high growth example (moderate growth)',
        'focus_metric': 'Credit Growth Rate',
        'modifications': {
            'growth_trend': 'linear',
            'growth_rate': 1.8  # 1.8x growth
        }
    },
    'CUST_MSM_00010': {
        'profile': 'high_seasonality',
        'description': 'Another seasonality example (retail business pattern)',
        'focus_metric': 'Seasonality Index',
        'modifications': {
            'seasonality_multipliers': [0.5, 0.6, 1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 2.0, 1.5, 3.5, 4.0]
        }
    }
}

def load_customer_transactions(customer_id):
    """Load transactions for a specific customer."""
    txn_file = 'raw/raw_transactions_with_customer_id.ndjson'
    if not os.path.exists(txn_file):
        print(f"  ❌ Transaction file not found: {txn_file}")
        return []
    
    transactions = []
    with open(txn_file, 'r') as f:
        for line in f:
            if line.strip():
                txn = json.loads(line)
                if txn.get('customer_id') == customer_id:
                    transactions.append(txn)
    
    return transactions

def save_all_transactions(all_transactions):
    """Save all customer transactions back to file."""
    txn_file = 'raw/raw_transactions_with_customer_id.ndjson'
    with open(txn_file, 'w') as f:
        for txn in all_transactions:
            f.write(json.dumps(txn) + '\n')

def apply_seasonality_modification(transactions, multipliers):
    """Apply seasonal multipliers to credit transactions."""
    # Group by month
    months = defaultdict(list)
    for txn in transactions:
        date_str = txn.get('date', '')
        try:
            # Parse various date formats
            if isinstance(date_str, str):
                if '/' in date_str:
                    if date_str.count('/') == 2:
                        parts = date_str.split()
                        date_part = parts[0]
                        month = datetime.strptime(date_part, '%d/%m/%Y').month if date_part.count('/') == 2 else datetime.strptime(date_part, '%m/%d/%Y').month
                    else:
                        month = int(date_str.split('/')[1] if date_str.split('/')[0].isdigit() and int(date_str.split('/')[0]) <= 31 else date_str.split('/')[0])
                elif '-' in date_str:
                    month = int(date_str.split('-')[1])
                else:
                    month = 1
            else:
                month = 1
        except:
            month = 1
        
        months[month].append(txn)
    
    # Apply multipliers
    for month, txns in months.items():
        multiplier = multipliers[(month - 1) % 12]
        for txn in txns:
            if txn.get('type', '').upper() in ['CREDIT', 'CR', 'C']:
                try:
                    current_amount = float(txn.get('amount', 0) or 0)
                    txn['amount'] = current_amount * multiplier
                except:
                    pass
    
    return transactions

def add_loan_emi_transactions(transactions, customer_id, emi_count, amount_range):
    """Add loan EMI transactions for high debt profile."""
    print(f"    Adding {emi_count} EMI transactions...")
    
    # Get date range from existing transactions
    dates = []
    for txn in transactions:
        date_str = txn.get('date', '')
        try:
            if '-' in date_str:
                dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
            elif '/' in date_str:
                if ' ' in date_str:
                    date_str = date_str.split()[0]
                try:
                    dates.append(datetime.strptime(date_str, '%d/%m/%Y'))
                except:
                    dates.append(datetime.strptime(date_str, '%m/%d/%Y'))
        except:
            continue
    
    if not dates:
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
    else:
        start_date = min(dates)
        end_date = max(dates)
    
    # Generate EMI transactions spread across the period
    new_transactions = []
    days_span = (end_date - start_date).days
    
    for i in range(emi_count):
        txn_date = start_date + timedelta(days=random.randint(0, days_span))
        
        new_transactions.append({
            'transaction_id': f'TXN_EMI_{customer_id}_{i:06d}',
            'account_id': f'ACC_{customer_id}',
            'date': txn_date.strftime('%Y-%m-%d'),
            'timestamp': txn_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'type': 'DEBIT',
            'amount': random.uniform(*amount_range),
            'currency': 'INR',
            'mode': 'NEFT',
            'balance_after': None,
            'narration': random.choice([
                'BUSINESS LOAN EMI PAYMENT',
                'TERM LOAN INSTALLMENT',
                'WORKING CAPITAL LOAN EMI',
                'MACHINERY LOAN REPAYMENT',
                'ICICI BUSINESS LOAN EMI',
                'HDFC TERM LOAN EMI'
            ]),
            'reference_number': f'REF{random.randint(100000000000, 999999999999)}',
            'merchant_name': None,
            'category': 'LOAN_REPAYMENT',
            'customer_id': customer_id
        })
    
    print(f"    ✅ Added {len(new_transactions)} EMI transactions")
    return transactions + new_transactions

def add_bounce_transactions(transactions, customer_id, bounce_rate, keywords):
    """Mark transactions as bounced/failed."""
    print(f"    Adding bounces at {bounce_rate*100:.1f}% rate...")
    
    bounce_count = 0
    debit_txns = [t for t in transactions if t.get('type', '').upper() in ['DEBIT', 'DR', 'D']]
    target_bounces = int(len(debit_txns) * bounce_rate)
    
    # Randomly select transactions to mark as bounced
    bounced_txns = random.sample(debit_txns, min(target_bounces, len(debit_txns)))
    
    for txn in bounced_txns:
        txn['status'] = 'FAILED'
        keyword = random.choice(keywords)
        original_narration = txn.get('narration', '') or ''
        txn['narration'] = f'{keyword} - {original_narration}' if original_narration else keyword
        txn['failure_reason'] = random.choice([
            'INSUFFICIENT_FUNDS',
            'PAYMENT_DECLINED',
            'BOUNCED',
            'DISHONOURED'
        ])
        bounce_count += 1
    
    print(f"    ✅ Marked {bounce_count} transactions as bounced/failed")
    return transactions

def apply_growth_trend(transactions, growth_rate, trend_type='exponential'):
    """Apply growth trend to credit transactions."""
    print(f"    Applying {trend_type} growth trend ({growth_rate}x)...")
    
    # Sort by date
    sorted_txns = sorted(transactions, key=lambda x: x.get('date', ''))
    total = len(sorted_txns)
    
    for i, txn in enumerate(sorted_txns):
        if txn.get('type', '').upper() in ['CREDIT', 'CR', 'C']:
            progress = i / total  # 0 to 1
            
            if trend_type == 'exponential':
                multiplier = 1.0 + (growth_rate - 1.0) * (progress ** 1.5)
            else:  # linear
                multiplier = 1.0 + (growth_rate - 1.0) * progress
            
            try:
                current_amount = float(txn.get('amount', 0) or 0)
                txn['amount'] = current_amount * multiplier
            except:
                pass
    
    print(f"    ✅ Applied growth trend")
    return sorted_txns

def apply_decline_trend(transactions, decline_rate):
    """Apply declining trend to credit transactions."""
    print(f"    Applying decline trend (to {decline_rate*100:.0f}% of original)...")
    
    sorted_txns = sorted(transactions, key=lambda x: x.get('date', ''))
    total = len(sorted_txns)
    
    for i, txn in enumerate(sorted_txns):
        if txn.get('type', '').upper() in ['CREDIT', 'CR', 'C']:
            progress = i / total
            multiplier = 1.0 - (1.0 - decline_rate) * progress
            
            try:
                current_amount = float(txn.get('amount', 0) or 0)
                txn['amount'] = current_amount * multiplier
            except:
                pass
    
    print(f"    ✅ Applied decline trend")
    return sorted_txns

def stabilize_income(transactions, variance_limit):
    """Make income very stable with minimal variation."""
    print(f"    Stabilizing income (variance ±{variance_limit*100:.0f}%)...")
    
    # Calculate average credit amount
    credits = [float(t.get('amount', 0) or 0) for t in transactions 
               if t.get('type', '').upper() in ['CREDIT', 'CR', 'C']]
    
    if not credits:
        return transactions
    
    avg_credit = sum(credits) / len(credits)
    
    # Normalize all credits to be close to average
    for txn in transactions:
        if txn.get('type', '').upper() in ['CREDIT', 'CR', 'C']:
            try:
                txn['amount'] = avg_credit * random.uniform(1 - variance_limit, 1 + variance_limit)
            except:
                pass
    
    print(f"    ✅ Stabilized income around ₹{avg_credit:,.0f}")
    return transactions

def concentrate_customers(transactions, top1_pct, top3_pct):
    """Concentrate credit transactions to top customers."""
    print(f"    Concentrating customers (Top-1: {top1_pct*100:.0f}%, Top-3: {top3_pct*100:.0f}%)...")
    
    credit_txns = [t for t in transactions if t.get('type', '').upper() in ['CREDIT', 'CR', 'C']]
    
    if not credit_txns:
        return transactions
    
    # Define major customers
    top_customer = 'GlobalTech Solutions Pvt Ltd'
    second_customer = 'Infosys Technologies'
    third_customer = 'TCS Enterprise Services'
    
    # Calculate how many transactions for each
    top1_count = int(len(credit_txns) * top1_pct)
    top3_count = int(len(credit_txns) * top3_pct)
    top2_count = int((top3_count - top1_count) / 2)
    top3_remaining = top3_count - top1_count - top2_count
    
    # Randomly assign
    random.shuffle(credit_txns)
    
    # Assign to top customer and increase amounts significantly
    for i in range(min(top1_count, len(credit_txns))):
        txn = credit_txns[i]
        txn['merchant_name'] = top_customer
        txn['counterparty_account'] = 'ACC_GLOBAL_TECH_001'
        try:
            current_amount = float(txn.get('amount', 0) or 0)
            txn['amount'] = current_amount * random.uniform(2.0, 3.5)  # Significantly increase
        except:
            pass
    
    # Assign to second customer
    for i in range(top1_count, min(top1_count + top2_count, len(credit_txns))):
        txn = credit_txns[i]
        txn['merchant_name'] = second_customer
        txn['counterparty_account'] = 'ACC_INFOSYS_002'
        try:
            current_amount = float(txn.get('amount', 0) or 0)
            txn['amount'] = current_amount * random.uniform(1.5, 2.5)
        except:
            pass
    
    # Assign to third customer
    for i in range(top1_count + top2_count, min(top3_count, len(credit_txns))):
        txn = credit_txns[i]
        txn['merchant_name'] = third_customer
        txn['counterparty_account'] = 'ACC_TCS_003'
        try:
            current_amount = float(txn.get('amount', 0) or 0)
            txn['amount'] = current_amount * random.uniform(1.3, 2.0)
        except:
            pass
    
    print(f"    ✅ Concentrated to top customers")
    return transactions

def apply_profile_modifications(customer_id, transactions, profile_config):
    """Apply all modifications for a customer profile."""
    modifications = profile_config.get('modifications', {})
    
    if not modifications:
        print("    No modifications needed (baseline profile)")
        return transactions
    
    # Apply seasonality
    if 'seasonality_multipliers' in modifications:
        transactions = apply_seasonality_modification(
            transactions, 
            modifications['seasonality_multipliers']
        )
    
    # Add loan EMIs
    if modifications.get('add_loan_emis'):
        transactions = add_loan_emi_transactions(
            transactions,
            customer_id,
            modifications['emi_count'],
            modifications['emi_amount_range']
        )
    
    # Add bounces
    if modifications.get('add_bounces'):
        transactions = add_bounce_transactions(
            transactions,
            customer_id,
            modifications['bounce_rate'],
            modifications['bounce_keywords']
        )
    
    # Apply growth trend
    if modifications.get('growth_trend'):
        transactions = apply_growth_trend(
            transactions,
            modifications['growth_rate'],
            modifications['growth_trend']
        )
    
    # Apply decline trend
    if modifications.get('decline_trend'):
        transactions = apply_decline_trend(
            transactions,
            modifications['decline_rate']
        )
    
    # Stabilize income
    if modifications.get('stabilize_credits'):
        transactions = stabilize_income(
            transactions,
            modifications['variance_limit']
        )
    
    # Concentrate customers
    if modifications.get('concentrate_customers'):
        transactions = concentrate_customers(
            transactions,
            modifications['top_1_concentration'],
            modifications['top_3_concentration']
        )
    
    return transactions

def regenerate_customer(customer_id, profile_config):
    """Regenerate a single customer with focused profile."""
    print(f"\n{'='*80}")
    print(f"  CUSTOMER: {customer_id}")
    print(f"  Profile: {profile_config['profile']}")
    print(f"  Description: {profile_config['description']}")
    if 'focus_metric' in profile_config:
        print(f"  ⭐ Focus Metric: {profile_config['focus_metric']}")
    print(f"{'='*80}")
    
    # Step 1: Load all transactions
    print("\n  [1/4] Loading transactions...")
    all_transactions = []
    with open('raw/raw_transactions_with_customer_id.ndjson', 'r') as f:
        for line in f:
            if line.strip():
                all_transactions.append(json.loads(line))
    
    print(f"    Loaded {len(all_transactions)} total transactions")
    
    # Step 2: Extract customer transactions
    print(f"\n  [2/4] Extracting {customer_id} transactions...")
    customer_txns = [t for t in all_transactions if t.get('customer_id') == customer_id]
    other_txns = [t for t in all_transactions if t.get('customer_id') != customer_id]
    
    print(f"    Found {len(customer_txns)} transactions for {customer_id}")
    
    # Step 3: Apply profile modifications
    print(f"\n  [3/4] Applying profile modifications...")
    modified_txns = apply_profile_modifications(customer_id, customer_txns, profile_config)
    
    # Step 4: Save back
    print(f"\n  [4/4] Saving modified transactions...")
    all_transactions = other_txns + modified_txns
    save_all_transactions(all_transactions)
    
    print(f"    ✅ Saved {len(all_transactions)} total transactions")
    
    # Step 5: Regenerate analytics
    print(f"\n  [5/5] Regenerating analytics...")
    try:
        result = subprocess.run(
            ['python', 'analytics/generate_summaries.py', '--customer-id', customer_id],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print(f"    ✅ Analytics generated successfully")
        else:
            print(f"    ⚠️ Analytics generation had issues")
            if result.stderr:
                print(f"    Error: {result.stderr[:200]}")
    except Exception as e:
        print(f"    ❌ Failed to generate analytics: {e}")
    
    print(f"\n  ✅ COMPLETED: {customer_id}")
    return True

def main():
    """Main execution."""
    print("="*80)
    print("  FOCUSED PROFILE REGENERATION")
    print("  Each customer gets ONE primary focused issue")
    print("="*80)
    
    # Process each customer
    for customer_id, profile_config in CUSTOMER_PROFILES.items():
        try:
            regenerate_customer(customer_id, profile_config)
        except Exception as e:
            print(f"\n  ❌ ERROR processing {customer_id}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "="*80)
    print("  ✅ ALL CUSTOMERS REGENERATED")
    print("="*80)
    print("\n  Next: Review analytics to ensure profiles are focused and clear")

if __name__ == '__main__':
    # Change to data_lake directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
