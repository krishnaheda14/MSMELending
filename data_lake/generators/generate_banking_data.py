"""
Main data generator orchestrator for synthetic Indian financial data lake.
"""
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generators.indian_data_utils import *


class ConsentGenerator:
    """Generate AA consent artefacts."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.aa_providers = ["FINVU", "ONEMONEY", "NADL", "CAMS", "ANUMATI"]
        self.consent_types = ["DEPOSIT", "TERM_DEPOSIT", "RECURRING_DEPOSIT", "SIP", 
                            "MUTUAL_FUNDS", "INSURANCE_POLICIES", "EQUITIES"]
    
    def generate(self, user_ids: List[str]) -> List[Dict]:
        """Generate consent artefacts for users."""
        consents = []
        
        for user_id in user_ids:
            # Each user may have 1-3 consent artefacts
            num_consents = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
            
            for _ in range(num_consents):
                consent = self._generate_consent(user_id)
                consents.append(consent)
        
        return consents
    
    def _generate_consent(self, user_id: str) -> Dict:
        """Generate a single consent artefact."""
        consent_id = f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')}" + \
                    ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=7)) + "-" + \
                    ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4)) + "-" + \
                    ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4)) + "-" + \
                    ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4)) + "-" + \
                    ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=12))
        
        start_date = datetime.now() - timedelta(days=random.randint(1, 365))
        expiry_date = start_date + timedelta(days=random.randint(90, 730))
        
        data_from = start_date - timedelta(days=random.randint(365, 1095))
        data_to = datetime.now()
        
        status_weights = [0.7, 0.05, 0.15, 0.05, 0.05]
        status = random.choices(["ACTIVE", "PAUSED", "REVOKED", "EXPIRED", "PENDING"], 
                               weights=status_weights)[0]
        
        consent = {
            "consent_id": consent_id,
            "user_id": user_id,
            "fiu_id": f"FIU{random.randint(100, 999)}",
            "aa_id": random.choice(self.aa_providers),
            "consent_start": start_date.isoformat(),
            "consent_expiry": expiry_date.isoformat(),
            "data_from": data_from.strftime("%Y-%m-%d"),
            "data_to": data_to.strftime("%Y-%m-%d"),
            "consent_types": random.sample(self.consent_types, random.randint(1, 4)),
            "fip_ids": [f"FIP{random.randint(1000, 9999)}" for _ in range(random.randint(1, 3))],
            "status": status,
            "consent_mode": random.choice(["VIEW", "STORE", "QUERY"]),
            "frequency_unit": random.choice(["DAILY", "MONTHLY", "YEARLY"]),
            "fetch_type": random.choice(["ONETIME", "PERIODIC"]),
            "created_at": start_date.isoformat(),
            "updated_at": (start_date + timedelta(days=random.randint(0, 30))).isoformat()
        }
        
        return consent


class BankAccountGenerator:
    """Generate bank accounts."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.banks = config['banks']
    
    def generate(self, user_ids: List[str], num_accounts: int) -> List[Dict]:
        """Generate bank accounts."""
        accounts = []
        account_id = 1
        
        # Ensure each user has at least one account
        for user_id in user_ids:
            bank = random.choice(self.banks)
            account = self._generate_account(f"ACC{account_id:08d}", user_id, bank)
            accounts.append(account)
            account_id += 1
        
        # Generate remaining accounts
        while len(accounts) < num_accounts:
            user_id = random.choice(user_ids)
            bank = random.choice(self.banks)
            account = self._generate_account(f"ACC{account_id:08d}", user_id, bank)
            accounts.append(account)
            account_id += 1
        
        return accounts
    
    def _generate_account(self, account_id: str, user_id: str, bank: str) -> Dict:
        """Generate a single bank account."""
        account_number = generate_account_number(bank)
        ifsc = generate_ifsc(bank)
        
        opened_date = datetime.now() - timedelta(days=random.randint(30, 3650))
        
        account_types = ["SAVINGS", "CURRENT", "OVERDRAFT", "CASH_CREDIT"]
        type_weights = [0.65, 0.25, 0.07, 0.03]
        account_type = random.choices(account_types, weights=type_weights)[0]
        
        status = random.choices(["ACTIVE", "INACTIVE", "CLOSED"], weights=[0.85, 0.10, 0.05])[0]
        
        # Generate balance
        if account_type == "SAVINGS":
            balance = random.uniform(500, 500000)
        elif account_type == "CURRENT":
            balance = random.uniform(-50000, 2000000)
        else:
            balance = random.uniform(-100000, 1000000)
        
        # Apply messy format to balance
        if random.random() < 0.3:
            balance_str = apply_messy_amount_format(balance)
        else:
            balance_str = balance
        
        # Apply messy date format
        if random.random() < 0.4:
            opened_date_str = apply_messy_date_format(opened_date)
        else:
            opened_date_str = opened_date.strftime("%Y-%m-%d")
        
        account = {
            "account_id": account_id,
            "user_id": user_id,
            "masked_account_number": f"XXXXXX{account_number[-4:]}",
            "account_number": account_number,
            "bank": bank,
            "ifsc": ifsc,
            "branch": random.choice(INDIAN_CITIES) + " Branch",
            "account_type": account_type,
            "currency": "INR",
            "opened_date": opened_date_str,
            "status": status,
            "balance": balance_str,
            "holder_name": generate_indian_name(),
            "fip_id": f"FIP{bank}{random.randint(1000, 9999)}"
        }
        
        # Introduce missing fields
        if self.config['messiness_config']['missing_field_probability'] > 0:
            account = introduce_missing_fields(
                account, 
                self.config['messiness_config']['missing_field_probability']
            )
        
        return account


class TransactionGenerator:
    """Generate bank transactions."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.date_range = (
            datetime.strptime(config['date_range']['start'], "%Y-%m-%d"),
            datetime.strptime(config['date_range']['end'], "%Y-%m-%d")
        )
    
    def generate(self, accounts: List[Dict], num_transactions: int) -> List[Dict]:
        """Generate transactions for accounts."""
        transactions = []
        txn_id = 1
        
        # Calculate average transactions per account
        active_accounts = [acc for acc in accounts if acc.get('status') == 'ACTIVE']
        
        if not active_accounts:
            return []
        
        txns_per_account = num_transactions // len(active_accounts)
        
        for account in active_accounts:
            num_txns = max(1, int(txns_per_account * random.uniform(0.5, 1.5)))
            account_txns = self._generate_account_transactions(
                account, num_txns, txn_id
            )
            transactions.extend(account_txns)
            txn_id += len(account_txns)
            
            if len(transactions) >= num_transactions:
                break
        
        # Introduce duplicates
        if self.config['messiness_config']['duplicate_probability'] > 0:
            transactions = introduce_duplicates(
                transactions,
                self.config['messiness_config']['duplicate_probability']
            )
        
        return transactions[:num_transactions]
    
    def _generate_account_transactions(self, account: Dict, num_txns: int, 
                                       start_txn_id: int) -> List[Dict]:
        """Generate transactions for a single account."""
        transactions = []
        account_id = account['account_id']
        bank = account['bank']
        
        # Parse current balance
        try:
            if isinstance(account.get('balance'), str):
                current_balance = float(account['balance'].replace(',', ''))
            else:
                current_balance = float(account.get('balance', 10000))
        except:
            current_balance = 10000
        
        # Generate transactions chronologically
        dates = sorted([
            self.date_range[0] + timedelta(
                seconds=random.randint(0, int((self.date_range[1] - self.date_range[0]).total_seconds()))
            )
            for _ in range(num_txns)
        ])
        
        for i, txn_date in enumerate(dates):
            txn = self._generate_transaction(
                f"TXN{start_txn_id + i:012d}",
                account_id,
                bank,
                txn_date,
                current_balance
            )
            transactions.append(txn)
            
            # Update balance
            try:
                amount = float(str(txn['amount']).replace(',', ''))
                if txn['type'] == 'CREDIT':
                    current_balance += amount
                else:
                    current_balance -= amount
            except:
                pass
        
        return transactions
    
    def _generate_transaction(self, txn_id: str, account_id: str, bank: str,
                             txn_date: datetime, balance: float) -> Dict:
        """Generate a single transaction."""
        # Determine transaction type
        txn_type = random.choices(["CREDIT", "DEBIT"], weights=[0.35, 0.65])[0]
        
        # Determine category and amount
        if txn_type == "CREDIT":
            category_weights = {
                "SALARY": (0.15, self.config['distributions']['salary_range']),
                "TRANSFER": (0.50, [500, 50000]),
                "INVESTMENT": (0.10, [5000, 200000]),
                "OTHER": (0.25, [100, 10000])
            }
        else:
            category_weights = {
                "SHOPPING": (0.25, [200, 15000]),
                "FOOD": (0.20, self.config['distributions']['upi_spend_range']),
                "EMI": (0.10, self.config['distributions']['emi_range']),
                "UTILITIES": (0.15, [500, 5000]),
                "CASH_WITHDRAWAL": (0.15, [500, 20000]),
                "TRANSFER": (0.10, [1000, 100000]),
                "OTHER": (0.05, [100, 5000])
            }
        
        categories = list(category_weights.keys())
        weights = [v[0] for v in category_weights.values()]
        category = random.choices(categories, weights=weights)[0]
        
        amount_range = category_weights[category][1]
        amount = random.uniform(*amount_range)
        
        # Add outliers (0.5% of transactions)
        if random.random() < 0.005:
            amount *= random.uniform(5, 15)
        
        # Determine mode
        if category in ["SHOPPING", "FOOD"]:
            mode = random.choices(["UPI", "POS", "DEBIT_CARD"], weights=[0.60, 0.25, 0.15])[0]
        elif category == "CASH_WITHDRAWAL":
            mode = "ATM"
        elif category == "EMI":
            mode = random.choice(["NACH", "NEFT"])
        elif category == "SALARY":
            mode = random.choice(["NEFT", "IMPS"])
        else:
            mode = random.choice(["UPI", "IMPS", "NEFT", "RTGS"])
        
        # Generate merchant name
        merchant_name = None
        if category in ["SHOPPING", "FOOD"] and txn_type == "DEBIT":
            merchant = random.choice(MERCHANT_NAMES)
            if self.config['messiness_config']['merchant_name_drift']:
                merchant_name = generate_merchant_name_variants(merchant)
            else:
                merchant_name = merchant
        
        # Generate narration
        narration = generate_transaction_narration(txn_type, mode, merchant_name, bank)
        
        # Calculate balance after
        if txn_type == "CREDIT":
            balance_after = balance + amount
        else:
            balance_after = balance - amount
        
        # Apply messy formats
        if self.config['messiness_config']['date_format_variation']:
            date_str = apply_messy_date_format(txn_date)
        else:
            date_str = txn_date.strftime("%Y-%m-%d")
        
        if self.config['messiness_config']['numeric_format_inconsistency']:
            amount_str = apply_messy_amount_format(amount)
            balance_str = apply_messy_amount_format(balance_after) if random.random() < 0.7 else None
        else:
            amount_str = amount
            balance_str = balance_after if random.random() < 0.7 else None
        
        transaction = {
            "transaction_id": txn_id,
            "account_id": account_id,
            "date": date_str,
            "timestamp": txn_date.isoformat(),
            "type": txn_type,
            "amount": amount_str,
            "currency": "INR",
            "mode": mode,
            "balance_after": balance_str,
            "narration": narration,
            "reference_number": f"REF{random.randint(100000000000, 999999999999)}",
            "merchant_name": merchant_name,
            "category": category
        }
        
        # Add UPI ID for UPI transactions
        if mode == "UPI" and random.random() < 0.7:
            transaction["upi_id"] = generate_upi_id("merchant", bank)
        
        # Introduce missing fields
        if self.config['messiness_config']['missing_field_probability'] > 0:
            transaction = introduce_missing_fields(
                transaction,
                self.config['messiness_config']['missing_field_probability']
            )
        
        return transaction


def save_ndjson(data: List[Dict], filepath: str):
    """Save data in NDJSON format."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for record in data:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')


def main():
    """Main data generation function."""
    # Seed random with customer_id if provided (for distinct per-customer data)
    customer_id = os.environ.get('CUSTOMER_ID', 'CUST_MSM_00001')
    seed_value = hash(customer_id) % (2**32)
    random.seed(seed_value)
    print(f"  [SEED] Using seed {seed_value} from customer_id={customer_id}")

    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Use per-customer scales
    scale = config['scale']
    num_transactions = scale.get('transactions_per_customer', scale.get('transactions', 2000))
    
    print("Starting data generation...")
    print(f"Customer: {customer_id}")
    print(f"Configuration: transactions={num_transactions}")
    
    # Generate user IDs (just one user per customer for simplicity)
    print("\n[1/9] Generating user IDs...")
    user_ids = [f"USER_{customer_id}"]
    
    # Generate consents
    print("[2/9] Generating consent artefacts...")
    consent_gen = ConsentGenerator(config)
    consents = consent_gen.generate(user_ids)
    
    # Add customer_id to each consent
    for c in consents:
        c['customer_id'] = customer_id
    
    # Load existing consents or create new file
    consent_file = 'raw/raw_consent.ndjson'
    if os.path.exists(consent_file):
        with open(consent_file, 'r') as f:
            existing = [json.loads(line) for line in f if line.strip()]
        # Filter out this customer's old data
        existing = [c for c in existing if c.get('customer_id') != customer_id]
        consents = existing + consents
    
    save_ndjson(consents, consent_file)
    print(f"  Generated {len([c for c in consents if c.get('customer_id') == customer_id])} consents for {customer_id}")
    
    # Generate accounts (2-3 per customer)
    print("[3/9] Generating bank accounts...")
    account_gen = BankAccountGenerator(config)
    accounts = account_gen.generate(user_ids, random.randint(2, 3))
    
    # Add customer_id to each account
    for acc in accounts:
        acc['customer_id'] = customer_id
    
    # Load existing accounts or create new file
    accounts_file = 'raw/raw_accounts.ndjson'
    if os.path.exists(accounts_file):
        with open(accounts_file, 'r') as f:
            existing = [json.loads(line) for line in f if line.strip()]
        # Filter out this customer's old data
        existing = [a for a in existing if a.get('customer_id') != customer_id]
        accounts = existing + accounts
    
    save_ndjson(accounts, accounts_file)
    print(f"  Generated {len([a for a in accounts if a.get('customer_id') == customer_id])} accounts for {customer_id}")
    
    # Filter accounts for this customer only
    customer_accounts = [a for a in accounts if a.get('customer_id') == customer_id]
    
    # Generate transactions
    print("[4/9] Generating transactions (this may take a while)...")
    txn_gen = TransactionGenerator(config)
    
    all_transactions = txn_gen.generate(customer_accounts, num_transactions)
    
    # Add customer_id to each transaction
    for txn in all_transactions:
        txn['customer_id'] = customer_id
    
    # Load existing transactions or create new file
    txn_file = 'raw/raw_transactions.ndjson'
    if os.path.exists(txn_file):
        with open(txn_file, 'r') as f:
            existing_txns = [json.loads(line) for line in f if line.strip()]
        # Filter out this customer's old data
        existing_txns = [t for t in existing_txns if t.get('customer_id') != customer_id]
        all_transactions = existing_txns + all_transactions
    
    save_ndjson(all_transactions, txn_file)
    print(f"  Generated {len([t for t in all_transactions if t.get('customer_id') == customer_id])} transactions for {customer_id}")
    
    print("\nRaw data generation completed!")
    print(f"Files saved in 'raw/' directory")


if __name__ == "__main__":
    main()
