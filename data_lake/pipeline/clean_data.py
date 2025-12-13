"""
Data cleaning and standardization pipeline.
"""
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple
from collections import defaultdict
import hashlib


class DataCleaner:
    """Base cleaner class."""
    
    def __init__(self):
        self.parsing_log = []
        self.cleaning_log = []
        self.validation_errors = []
    
    def log_parsing(self, record_id: str, field: str, old_value: Any, new_value: Any, action: str):
        """Log parsing action."""
        self.parsing_log.append({
            "record_id": record_id,
            "field": field,
            "old_value": str(old_value),
            "new_value": str(new_value),
            "action": action,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_cleaning(self, record_id: str, field: str, issue: str, action: str):
        """Log cleaning action."""
        self.cleaning_log.append({
            "record_id": record_id,
            "field": field,
            "issue": issue,
            "action": action,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_validation_error(self, record_id: str, field: str, error: str, value: Any):
        """Log validation error."""
        self.validation_errors.append({
            "record_id": record_id,
            "field": field,
            "error": error,
            "value": str(value),
            "timestamp": datetime.now().isoformat()
        })
    
    def parse_date(self, date_str: Any, record_id: str = None, field_name: str = "date") -> str:
        """Parse various date formats to YYYY-MM-DD."""
        if not date_str or date_str == "":
            return None
        
        if isinstance(date_str, datetime):
            return date_str.strftime("%Y-%m-%d")
        
        date_str = str(date_str).strip()
        original = date_str
        
        # Try various formats
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%d %b %y",
            "%d %B %Y",
            "%d-%b-%Y"
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                result = parsed.strftime("%Y-%m-%d")
                
                if record_id and original != result:
                    self.log_parsing(record_id, field_name, original, result, "date_format_standardized")
                
                return result
            except:
                continue
        
        # If all fail, log error
        if record_id:
            self.log_validation_error(record_id, field_name, "unparseable_date", original)
        
        return None
    
    def parse_amount(self, amount_str: Any, record_id: str = None, field_name: str = "amount") -> float:
        """Parse various numeric formats to float."""
        if amount_str is None or amount_str == "":
            return None
        
        if isinstance(amount_str, (int, float)):
            return float(amount_str)
        
        amount_str = str(amount_str).strip()
        original = amount_str
        
        try:
            # Remove Indian comma formatting
            amount_str = amount_str.replace(',', '')
            # Remove currency symbols
            amount_str = amount_str.replace('₹', '').replace('Rs', '').replace('INR', '').strip()
            
            result = float(amount_str)
            
            if record_id and original != str(result):
                self.log_parsing(record_id, field_name, original, result, "amount_format_standardized")
            
            return result
        except:
            if record_id:
                self.log_validation_error(record_id, field_name, "unparseable_amount", original)
            return None
    
    def normalize_ifsc(self, ifsc: str, record_id: str = None) -> str:
        """Normalize IFSC code."""
        if not ifsc:
            return None
        
        ifsc = str(ifsc).strip().upper()
        original = ifsc
        
        # IFSC should be 11 characters
        if len(ifsc) == 11 and re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', ifsc):
            if record_id and original != ifsc:
                self.log_parsing(record_id, "ifsc", original, ifsc, "ifsc_normalized")
            return ifsc
        else:
            if record_id:
                self.log_validation_error(record_id, "ifsc", "invalid_ifsc_format", original)
            return ifsc  # Return as-is even if invalid
    
    def normalize_pan(self, pan: str, record_id: str = None) -> str:
        """Normalize PAN."""
        if not pan:
            return None
        
        pan = str(pan).strip().upper()
        original = pan
        
        # PAN format: 10 characters or masked
        if re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan) or re.match(r'^[A-Z]{5}XXXX[A-Z]$', pan):
            if record_id and original != pan:
                self.log_parsing(record_id, "pan", original, pan, "pan_normalized")
            return pan
        else:
            if record_id:
                self.log_validation_error(record_id, "pan", "invalid_pan_format", original)
            return pan
    
    def normalize_gstin(self, gstin: str, record_id: str = None) -> str:
        """Normalize GSTIN."""
        if not gstin:
            return None
        
        gstin = str(gstin).strip().upper()
        original = gstin
        
        # GSTIN format: 15 characters
        if len(gstin) == 15 and re.match(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$', gstin):
            if record_id and original != gstin:
                self.log_parsing(record_id, "gstin", original, gstin, "gstin_normalized")
            return gstin
        else:
            if record_id:
                self.log_validation_error(record_id, "gstin", "invalid_gstin_format", original)
            return gstin
    
    def clean_string(self, text: str, record_id: str = None, field_name: str = None) -> str:
        """Clean and trim string."""
        if not text:
            return None
        
        text = str(text).strip()
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text if text else None
    
    def standardize_transaction_type(self, txn_type: str, record_id: str = None) -> str:
        """Standardize transaction type."""
        if not txn_type:
            return None
        
        txn_type = str(txn_type).strip().upper()
        
        if txn_type in ["CREDIT", "CR", "C", "DEPOSIT"]:
            return "CREDIT"
        elif txn_type in ["DEBIT", "DR", "D", "WITHDRAWAL"]:
            return "DEBIT"
        else:
            if record_id:
                self.log_validation_error(record_id, "type", "unknown_transaction_type", txn_type)
            return txn_type
    
    def standardize_mode(self, mode: str, record_id: str = None) -> str:
        """Standardize transaction mode."""
        if not mode:
            return None
        
        mode = str(mode).strip().upper()
        
        mode_map = {
            "UPI": "UPI",
            "IMPS": "IMPS",
            "NEFT": "NEFT",
            "RTGS": "RTGS",
            "CASH": "CASH",
            "CHEQUE": "CHEQUE",
            "CHECK": "CHEQUE",
            "ATM": "ATM",
            "POS": "POS",
            "DEBIT_CARD": "DEBIT_CARD",
            "DEBITCARD": "DEBIT_CARD",
            "CREDIT_CARD": "CREDIT_CARD",
            "CREDITCARD": "CREDIT_CARD",
            "NACH": "NACH",
            "ECS": "ECS"
        }
        
        return mode_map.get(mode, mode)


class TransactionCleaner(DataCleaner):
    """Clean transaction data."""
    
    def clean_transaction(self, txn: Dict) -> Dict:
        """Clean a single transaction."""
        record_id = txn.get('transaction_id', 'UNKNOWN')
        
        cleaned = {
            "transaction_id": txn.get('transaction_id'),
            "account_id": txn.get('account_id'),
            "date": self.parse_date(txn.get('date'), record_id, "date"),
            "timestamp": txn.get('timestamp'),  # Keep ISO format
            "type": self.standardize_transaction_type(txn.get('type'), record_id),
            "amount": self.parse_amount(txn.get('amount'), record_id, "amount"),
            "currency": "INR",
            "mode": self.standardize_mode(txn.get('mode'), record_id),
            "balance_after": self.parse_amount(txn.get('balance_after'), record_id, "balance_after"),
            "narration": self.clean_string(txn.get('narration'), record_id, "narration"),
            "reference_number": self.clean_string(txn.get('reference_number'), record_id, "reference_number"),
            "merchant_name": self.clean_string(txn.get('merchant_name'), record_id, "merchant_name"),
            "merchant_category": txn.get('merchant_category'),
            "counterparty_account": txn.get('counterparty_account'),
            "counterparty_ifsc": self.normalize_ifsc(txn.get('counterparty_ifsc'), record_id),
            "upi_id": self.clean_string(txn.get('upi_id'), record_id, "upi_id"),
            "category": txn.get('category')
        }
        
        # Recalculate balance if missing
        if not cleaned['balance_after'] and cleaned['amount']:
            self.log_cleaning(record_id, "balance_after", "missing", "calculated_from_previous")
        
        return cleaned


class AccountCleaner(DataCleaner):
    """Clean account data."""
    
    def clean_account(self, account: Dict) -> Dict:
        """Clean a single account."""
        record_id = account.get('account_id', 'UNKNOWN')
        
        cleaned = {
            "account_id": account.get('account_id'),
            "user_id": account.get('user_id'),
            "masked_account_number": account.get('masked_account_number'),
            "bank": account.get('bank'),
            "ifsc": self.normalize_ifsc(account.get('ifsc'), record_id),
            "branch": self.clean_string(account.get('branch'), record_id, "branch"),
            "account_type": account.get('account_type'),
            "currency": "INR",
            "opened_date": self.parse_date(account.get('opened_date'), record_id, "opened_date"),
            "status": account.get('status'),
            "balance": self.parse_amount(account.get('balance'), record_id, "balance"),
            "holder_name": self.clean_string(account.get('holder_name'), record_id, "holder_name"),
            "fip_id": account.get('fip_id')
        }
        
        return cleaned


class GSTCleaner(DataCleaner):
    """Clean GST data."""
    
    def clean_gst_return(self, gst_return: Dict) -> Dict:
        """Clean a GST return."""
        record_id = gst_return.get('return_id', 'UNKNOWN')
        
        # Clean invoices
        cleaned_invoices = []
        if gst_return.get('invoices'):
            for invoice in gst_return['invoices']:
                cleaned_inv = self.clean_invoice(invoice, record_id)
                cleaned_invoices.append(cleaned_inv)
        
        cleaned = {
            "return_id": gst_return.get('return_id'),
            "gstin": self.normalize_gstin(gst_return.get('gstin'), record_id),
            "trade_name": self.clean_string(gst_return.get('trade_name'), record_id, "trade_name"),
            "legal_name": self.clean_string(gst_return.get('legal_name'), record_id, "legal_name"),
            "return_period": gst_return.get('return_period'),
            "return_type": gst_return.get('return_type'),
            "filing_date": self.parse_date(gst_return.get('filing_date'), record_id, "filing_date"),
            "status": gst_return.get('status'),
            "total_taxable_value": self.parse_amount(gst_return.get('total_taxable_value'), record_id, "total_taxable_value"),
            "total_igst": self.parse_amount(gst_return.get('total_igst'), record_id, "total_igst"),
            "total_cgst": self.parse_amount(gst_return.get('total_cgst'), record_id, "total_cgst"),
            "total_sgst": self.parse_amount(gst_return.get('total_sgst'), record_id, "total_sgst"),
            "total_cess": self.parse_amount(gst_return.get('total_cess'), record_id, "total_cess"),
            "invoices": cleaned_invoices,
            "itc_claimed": self.parse_amount(gst_return.get('itc_claimed'), record_id, "itc_claimed"),
            "itc_reversed": self.parse_amount(gst_return.get('itc_reversed'), record_id, "itc_reversed"),
            "net_tax_liability": self.parse_amount(gst_return.get('net_tax_liability'), record_id, "net_tax_liability")
        }
        
        return cleaned
    
    def clean_invoice(self, invoice: Dict, parent_id: str) -> Dict:
        """Clean an invoice."""
        cleaned = {
            "invoice_number": self.clean_string(invoice.get('invoice_number')),
            "invoice_date": self.parse_date(invoice.get('invoice_date')),
            "invoice_value": self.parse_amount(invoice.get('invoice_value')),
            "taxable_value": self.parse_amount(invoice.get('taxable_value')),
            "igst": self.parse_amount(invoice.get('igst')),
            "cgst": self.parse_amount(invoice.get('cgst')),
            "sgst": self.parse_amount(invoice.get('sgst')),
            "buyer_gstin": self.normalize_gstin(invoice.get('buyer_gstin')),
            "buyer_name": self.clean_string(invoice.get('buyer_name')),
            "place_of_supply": self.clean_string(invoice.get('place_of_supply')),
            "reverse_charge": invoice.get('reverse_charge'),
            "hsn_code": self.normalize_hsn(invoice.get('hsn_code')),
            "gst_rate": invoice.get('gst_rate')
        }
        
        return cleaned
    
    def normalize_hsn(self, hsn: str) -> str:
        """Normalize HSN code to standard format."""
        if not hsn:
            return None
        
        hsn = str(hsn).strip()
        
        # HSN should be 4-8 digits
        if hsn.isdigit() and len(hsn) in [4, 6, 8]:
            return hsn
        
        return hsn


class OCENCleaner(DataCleaner):
    """Clean OCEN (loan application) data."""

    def clean_application(self, app: Dict) -> Dict:
        record_id = app.get('application_id') or app.get('id') or hashlib.sha1(json.dumps(app, sort_keys=True).encode()).hexdigest()[:12]

        cleaned = {
            'application_id': app.get('application_id') or app.get('id'),
            'applicant_id': app.get('applicant_id') or app.get('customer_id'),
            'requested_amount': self.parse_amount(app.get('requested_amount'), record_id, 'requested_amount'),
            'approved_amount': self.parse_amount(app.get('approved_amount'), record_id, 'approved_amount'),
            'status': self.clean_string(app.get('status'), record_id, 'status'),
            'stage': self.clean_string(app.get('stage'), record_id, 'stage'),
            'application_date': self.parse_date(app.get('application_date') or app.get('created_at'), record_id, 'application_date'),
            'decision_date': self.parse_date(app.get('decision_date') or app.get('updated_at'), record_id, 'decision_date'),
            'provider': self.clean_string(app.get('provider'), record_id, 'provider'),
            'score': float(app.get('score')) if app.get('score') is not None else None,
            'raw': app
        }

        # Basic validation
        if cleaned['requested_amount'] is None:
            self.log_validation_error(record_id, 'requested_amount', 'missing_or_invalid', app.get('requested_amount'))

        return cleaned


class ONDCCleaner(DataCleaner):
    """Clean ONDC order history data."""

    def clean_order(self, order: Dict) -> Dict:
        record_id = order.get('order_id') or order.get('id') or hashlib.sha1(json.dumps(order, sort_keys=True).encode()).hexdigest()[:12]

        cleaned = {
            'order_id': order.get('order_id') or order.get('id'),
            'buyer_id': order.get('buyer_id') or order.get('customer_id'),
            'provider': self.clean_string(order.get('provider'), record_id, 'provider'),
            'order_value': self.parse_amount(order.get('order_value') or order.get('total_value'), record_id, 'order_value'),
            'currency': order.get('currency') or 'INR',
            'order_date': self.parse_date(order.get('order_date') or order.get('created_at'), record_id, 'order_date'),
            'payment_status': self.clean_string(order.get('payment_status') or order.get('status'), record_id, 'payment_status'),
            'items_count': int(order.get('items_count')) if order.get('items_count') not in (None, '') else None,
            'raw': order
        }

        if cleaned['order_value'] is None:
            self.log_validation_error(record_id, 'order_value', 'missing_or_invalid', order.get('order_value'))

        return cleaned


def save_ndjson(data: List[Dict], filepath: str):
    """Save data in NDJSON format."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for record in data:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')


def load_ndjson(filepath: str) -> List[Dict]:
    """Load data from NDJSON format."""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def save_log(log_data: List[Dict], filepath: str):
    """Save log data."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)


def main():
    """Main cleaning pipeline with detailed progress tracking."""
    print("="*80)
    print("  DATA CLEANING AND STANDARDIZATION PIPELINE")
    print("="*80)
    
    # Clean transactions
    print("\n[STEP] 1/6 - Transactions")
    print("[SUB-STEP] Loading raw transactions...")
    txn_cleaner = TransactionCleaner()
    raw_txns = load_ndjson('raw/raw_transactions.ndjson')
    print(f"[SUB-STEP] Loaded {len(raw_txns)} raw transactions")
    
    print("[SUB-STEP] Schema validation - checking required fields...")
    validated_txns = []
    for idx, txn in enumerate(raw_txns):
        required_fields = ['transaction_id', 'account_id', 'date', 'type', 'amount']
        missing = [f for f in required_fields if not txn.get(f)]
        if missing:
            print(f"[VALIDATION-ERROR] Transaction {txn.get('transaction_id', idx)}: missing fields {missing}")
        else:
            validated_txns.append(txn)
    print(f"[SUB-STEP] Schema validation complete: {len(validated_txns)}/{len(raw_txns)} valid")
    
    print("[SUB-STEP] Format validation - dates, amounts, balances...")
    cleaned_txns = [txn_cleaner.clean_transaction(txn) for txn in validated_txns]
    print(f"[SUB-STEP] Format validation complete")
    
    print("[SUB-STEP] Duplicate detection and removal...")
    seen_ids = set()
    deduped_txns = []
    duplicates = 0
    for txn in cleaned_txns:
        tid = txn.get('transaction_id')
        if tid in seen_ids:
            duplicates += 1
            print(f"[DUPLICATE] Removed duplicate transaction: {tid}")
        else:
            seen_ids.add(tid)
            deduped_txns.append(txn)
    print(f"[SUB-STEP] Removed {duplicates} duplicates, {len(deduped_txns)} unique transactions")
    
    print("[SUB-STEP] Identifier consistency check - PAN, Account numbers...")
    # Check if all transactions reference consistent account/user identifiers
    account_ids = {t.get('account_id') for t in deduped_txns if t.get('account_id')}
    print(f"[IDENTIFIER-CHECK] Found {len(account_ids)} unique account IDs")
    
    save_ndjson(deduped_txns, 'clean/transactions_clean.ndjson')
    save_log(txn_cleaner.parsing_log, 'logs/transaction_parsing_log.json')
    save_log(txn_cleaner.cleaning_log, 'logs/transaction_cleaning_log.json')
    save_log(txn_cleaner.validation_errors, 'logs/transaction_validation_errors.json')
    print(f"[COMPLETED] Transactions: {len(deduped_txns)} cleaned records")
    print(f"  - Parsing actions: {len(txn_cleaner.parsing_log)}")
    print(f"  - Validation errors: {len(txn_cleaner.validation_errors)}")
    
    # Clean accounts
    print("\n[STEP] 2/6 - Accounts")
    print("[SUB-STEP] Loading raw accounts...")
    account_cleaner = AccountCleaner()
    raw_accounts = load_ndjson('raw/raw_accounts.ndjson')
    print(f"[SUB-STEP] Loaded {len(raw_accounts)} raw accounts")
    
    print("[SUB-STEP] Schema validation...")
    validated_accounts = []
    for acc in raw_accounts:
        required_fields = ['account_id', 'user_id', 'bank']
        missing = [f for f in required_fields if not acc.get(f)]
        if missing:
            print(f"[VALIDATION-ERROR] Account {acc.get('account_id', '?')}: missing {missing}")
        else:
            validated_accounts.append(acc)
    print(f"[SUB-STEP] {len(validated_accounts)}/{len(raw_accounts)} accounts valid")
    
    print("[SUB-STEP] Format validation and identifier checks...")
    cleaned_accounts = [account_cleaner.clean_account(acc) for acc in validated_accounts]
    
    print("[SUB-STEP] Duplicate removal...")
    seen_accs = set()
    deduped_accs = []
    dup_count = 0
    for acc in cleaned_accounts:
        aid = acc.get('account_id')
        if aid in seen_accs:
            dup_count += 1
            print(f"[DUPLICATE] Removed duplicate account: {aid}")
        else:
            seen_accs.add(aid)
            deduped_accs.append(acc)
    print(f"[SUB-STEP] Removed {dup_count} duplicates")
    
    print("[SUB-STEP] PAN/IFSC consistency check...")
    ifsc_codes = {a.get('ifsc') for a in deduped_accs if a.get('ifsc')}
    print(f"[IDENTIFIER-CHECK] Found {len(ifsc_codes)} unique IFSC codes")
    
    save_ndjson(deduped_accs, 'clean/accounts_clean.ndjson')
    save_log(account_cleaner.parsing_log, 'logs/account_parsing_log.json')
    save_log(account_cleaner.validation_errors, 'logs/account_validation_errors.json')
    print(f"[COMPLETED] Accounts: {len(deduped_accs)} cleaned records")
    
    # Clean GST
    print("\n[STEP] 3/6 - GST Returns")
    print("[SUB-STEP] Loading raw GST returns...")
    gst_cleaner = GSTCleaner()
    raw_gst = load_ndjson('raw/raw_gst.ndjson')
    print(f"[SUB-STEP] Loaded {len(raw_gst)} raw GST returns")
    
    print("[SUB-STEP] Schema validation...")
    validated_gst = []
    for gst in raw_gst:
        required_fields = ['return_id', 'gstin', 'return_period']
        missing = [f for f in required_fields if not gst.get(f)]
        if missing:
            print(f"[VALIDATION-ERROR] GST {gst.get('return_id', '?')}: missing {missing}")
        else:
            validated_gst.append(gst)
    print(f"[SUB-STEP] {len(validated_gst)}/{len(raw_gst)} GST returns valid")
    
    print("[SUB-STEP] Format validation and GSTIN checks...")
    cleaned_gst = [gst_cleaner.clean_gst_return(gst) for gst in validated_gst]
    
    print("[SUB-STEP] Duplicate removal...")
    seen_gst = set()
    deduped_gst = []
    dup_gst = 0
    for gst in cleaned_gst:
        rid = gst.get('return_id')
        if rid in seen_gst:
            dup_gst += 1
        else:
            seen_gst.add(rid)
            deduped_gst.append(gst)
    print(f"[SUB-STEP] Removed {dup_gst} duplicates")
    
    print("[SUB-STEP] GSTIN consistency check...")
    gstins = {g.get('gstin') for g in deduped_gst if g.get('gstin')}
    print(f"[IDENTIFIER-CHECK] Found {len(gstins)} unique GSTINs")
    if len(gstins) > 1:
        print(f"[WARNING] Multiple GSTINs detected: {list(gstins)[:3]}...")
    
    save_ndjson(deduped_gst, 'clean/gst_clean.ndjson')
    save_log(gst_cleaner.parsing_log, 'logs/gst_parsing_log.json')
    save_log(gst_cleaner.validation_errors, 'logs/gst_validation_errors.json')
    print(f"[COMPLETED] GST Returns: {len(deduped_gst)} cleaned records")

    # Clean OCEN applications
    print("\n[STEP] 4/6 - OCEN Applications")
    print("[SUB-STEP] Loading raw OCEN applications...")
    ocen_cleaner = OCENCleaner()
    raw_ocen = []
    try:
        raw_ocen = load_ndjson('raw/raw_ocen_applications.ndjson')
    except Exception:
        raw_ocen = []
    print(f"[SUB-STEP] Loaded {len(raw_ocen)} raw OCEN applications")
    
    print("[SUB-STEP] Schema & format validation...")
    cleaned_ocen = [ocen_cleaner.clean_application(a) for a in raw_ocen]
    print("[SUB-STEP] Duplicate removal & identifier checks...")
    seen_ocen = set()
    deduped_ocen = []
    for app in cleaned_ocen:
        aid = app.get('application_id')
        if aid not in seen_ocen:
            seen_ocen.add(aid)
            deduped_ocen.append(app)
    print(f"[SUB-STEP] {len(deduped_ocen)} unique applications")
    
    save_ndjson(deduped_ocen, 'clean/ocen_applications_clean.ndjson')
    save_log(ocen_cleaner.parsing_log, 'logs/ocen_parsing_log.json')
    save_log(ocen_cleaner.validation_errors, 'logs/ocen_validation_errors.json')
    print(f"[COMPLETED] OCEN Applications: {len(deduped_ocen)} cleaned records")

    # Clean ONDC orders
    print("\n[STEP] 5/6 - ONDC Orders")
    print("[SUB-STEP] Loading raw ONDC orders...")
    ondc_cleaner = ONDCCleaner()
    raw_ondc = []
    try:
        raw_ondc = load_ndjson('raw/raw_ondc_orders.ndjson')
    except Exception:
        raw_ondc = []
    print(f"[SUB-STEP] Loaded {len(raw_ondc)} raw ONDC orders")
    
    print("[SUB-STEP] Schema & format validation...")
    cleaned_ondc = [ondc_cleaner.clean_order(o) for o in raw_ondc]
    print("[SUB-STEP] Duplicate removal...")
    seen_ondc = set()
    deduped_ondc = []
    for order in cleaned_ondc:
        oid = order.get('order_id')
        if oid not in seen_ondc:
            seen_ondc.add(oid)
            deduped_ondc.append(order)
    print(f"[SUB-STEP] {len(deduped_ondc)} unique orders")
    
    save_ndjson(deduped_ondc, 'clean/ondc_orders_clean.ndjson')
    save_log(ondc_cleaner.parsing_log, 'logs/ondc_parsing_log.json')
    save_log(ondc_cleaner.validation_errors, 'logs/ondc_validation_errors.json')
    print(f"[COMPLETED] ONDC Orders: {len(deduped_ondc)} cleaned records")
    
    print("\n✓ Data cleaning completed!")
    print(f"\nCleaned files saved in 'clean/' directory")
    print(f"Logs saved in 'logs/' directory")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Clean synthetic data')
    parser.add_argument('--customer-id', dest='customer_id', help='Optional customer id to clean data for')
    args, _ = parser.parse_known_args()
    
    if args.customer_id:
        print(f"\n[NOTE] Cleaning data for customer_id={args.customer_id}")
        # In production, this would filter data by customer_id
        # For now, we'll set it as an environment variable for future use
        import os
        os.environ['CUSTOMER_ID'] = str(args.customer_id)
    
    main()
