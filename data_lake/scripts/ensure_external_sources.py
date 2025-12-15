"""
Ensure every customer present in transactions has at least one ONDC order,
one Mutual Fund record and one Insurance policy in the raw NDJSON files.

This script:
 - Scans `raw/raw_transactions_with_customer_id.ndjson` to get customer IDs
 - Scans `raw/raw_ondc_orders.ndjson`, `raw/raw_mutual_funds.ndjson`, `raw/raw_policies.ndjson`
   to find which customers already have records
 - Appends a single minimal, realistic record to any missing customer's file

Run from `data_lake`:
  python scripts/ensure_external_sources.py

It creates `.bak` copies of files it modifies.
"""
import json
import os
import random
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
RAW_DIR = os.path.join(ROOT, 'raw')

TRANSACTIONS_FILE = os.path.join(RAW_DIR, 'raw_transactions_with_customer_id.ndjson')
ONDC_FILE = os.path.join(RAW_DIR, 'raw_ondc_orders.ndjson')
MF_FILE = os.path.join(RAW_DIR, 'raw_mutual_funds.ndjson')
INS_FILE = os.path.join(RAW_DIR, 'raw_policies.ndjson')

BACKUP_SUFFIX = '.bak_before_ensure_external_sources'


def load_ndjson(filepath):
    records = []
    if not os.path.exists(filepath):
        return records
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                try:
                    # tolerate trailing commas or broken lines
                    records.append(json.loads(line.rstrip(',')))
                except Exception:
                    records.append({'raw': line})
    return records


def write_ndjson(filepath, records):
    with open(filepath, 'w', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def append_records(filepath, new_records):
    # backup
    if os.path.exists(filepath) and not os.path.exists(filepath + BACKUP_SUFFIX):
        os.rename(filepath, filepath + BACKUP_SUFFIX)
        # restore original to write combined
        orig = load_ndjson(filepath + BACKUP_SUFFIX)
    else:
        orig = load_ndjson(filepath)
    combined = orig + new_records
    write_ndjson(filepath, combined)


def make_min_ondc(customer_id):
    ts = datetime.utcnow().isoformat() + 'Z'
    order_total = round(random.uniform(2000, 15000), 2)
    return {
        'order_id': f'ONDC-{customer_id}-{random.randint(1000,9999)}',
        'customer_id': customer_id,
        'user_id': customer_id,
        'created_at': ts,
        'provider': 'mock_provider',
        'order_total': order_total,
        'items_count': random.randint(1,5),
        'quote': {'price': order_total}
    }


def make_min_mf(customer_id):
    ts = datetime.utcnow().date().isoformat()
    invested = round(random.uniform(1000, 50000), 2)
    current = round(invested * random.uniform(1.0, 1.25), 2)
    return {
        'portfolio_id': f'MF-{customer_id}-{random.randint(1000,9999)}',
        'customer_id': customer_id,
        'user_id': customer_id,
        'scheme_name': 'Mock Growth Fund',
        'invested_amount': invested,
        'current_value': current,
        'last_transaction_date': ts
    }


def make_min_insurance(customer_id):
    ts = datetime.utcnow().date().isoformat()
    sum_assured = random.choice([50000, 100000, 200000])
    premium = round(sum_assured * 0.02, 2)
    return {
        'policy_id': f'POL-{customer_id}-{random.randint(1000,9999)}',
        'customer_id': customer_id,
        'user_id': customer_id,
        'policy_type': 'Term',
        'sum_assured': sum_assured,
        'annual_premium': premium,
        'start_date': ts
    }


def ensure_all():
    # Normalize existing policy records so analytics matching picks them up
    def normalize_policies_file():
        if not os.path.exists(INS_FILE):
            return
        recs = load_ndjson(INS_FILE)
        changed = False
        for r in recs:
            # ensure user_id present
            if not r.get('user_id') and r.get('customer_id'):
                r['user_id'] = r.get('customer_id')
                changed = True
            # normalize old INS- prefixes to POL- so analytics 'POL' matching works
            pid = r.get('policy_id') or ''
            if isinstance(pid, str) and pid.startswith('INS-'):
                r['policy_id'] = 'POL-' + pid[len('INS-'):]
                changed = True
        if changed:
            print('Normalizing insurance records and creating backup...')
            if os.path.exists(INS_FILE) and not os.path.exists(INS_FILE + BACKUP_SUFFIX):
                os.rename(INS_FILE, INS_FILE + BACKUP_SUFFIX)
            write_ndjson(INS_FILE, recs)

    normalize_policies_file()

    # Normalize mutual fund records to ensure matching by analytics
    def normalize_mf_file():
        if not os.path.exists(MF_FILE):
            return
        recs = load_ndjson(MF_FILE)
        changed = False
        for r in recs:
            # prefer 'customer_id' -> set 'user_id' if missing
            if not r.get('user_id') and r.get('customer_id'):
                r['user_id'] = r.get('customer_id')
                changed = True
            # ensure portfolio_id has MF- prefix for matching
            pid = r.get('portfolio_id') or ''
            if not pid or (isinstance(pid, str) and not pid.startswith('MF')):
                r['portfolio_id'] = f"MF-{r.get('customer_id') or r.get('user_id') or random.randint(1000,9999)}-{random.randint(1000,9999)}"
                changed = True
        if changed:
            print('Normalizing mutual fund records and creating backup...')
            if os.path.exists(MF_FILE) and not os.path.exists(MF_FILE + BACKUP_SUFFIX):
                os.rename(MF_FILE, MF_FILE + BACKUP_SUFFIX)
            write_ndjson(MF_FILE, recs)

    normalize_mf_file()

    print('Loading transactions to collect customer IDs...')
    tx = load_ndjson(TRANSACTIONS_FILE)
    customer_ids = set()
    for r in tx:
        cid = r.get('customer_id') or r.get('customer') or r.get('cust_id')
        if cid:
            customer_ids.add(cid)
    print(f'Found {len(customer_ids)} unique customers in transactions')

    print('Loading existing ONDC, MF, Insurance records...')
    ondc = load_ndjson(ONDC_FILE)
    mf = load_ndjson(MF_FILE)
    ins = load_ndjson(INS_FILE)

    ondc_customers = set([r.get('customer_id') for r in ondc if r.get('customer_id')])
    mf_customers = set([r.get('customer_id') for r in mf if r.get('customer_id')])
    ins_customers = set([r.get('customer_id') for r in ins if r.get('customer_id')])

    need_ondc = [c for c in customer_ids if c not in ondc_customers]
    need_mf = [c for c in customer_ids if c not in mf_customers]
    need_ins = [c for c in customer_ids if c not in ins_customers]

    print(f'Customers missing ONDC: {len(need_ondc)}')
    print(f'Customers missing MF:   {len(need_mf)}')
    print(f'Customers missing INS:  {len(need_ins)}')

    new_ondc = [make_min_ondc(c) for c in need_ondc]
    new_mf = [make_min_mf(c) for c in need_mf]
    new_ins = [make_min_insurance(c) for c in need_ins]

    if new_ondc:
        print(f'Appending {len(new_ondc)} ONDC records to {ONDC_FILE} (backup created)')
        append_records(ONDC_FILE, new_ondc)
    else:
        print('No ONDC records to append.')

    if new_mf:
        print(f'Appending {len(new_mf)} MF records to {MF_FILE} (backup created)')
        append_records(MF_FILE, new_mf)
    else:
        print('No MF records to append.')

    if new_ins:
        print(f'Appending {len(new_ins)} Insurance records to {INS_FILE} (backup created)')
        append_records(INS_FILE, new_ins)
    else:
        print('No Insurance records to append.')

    print('Done. Summary:')
    print(f' - ONDC now: {len(ondc) + len(new_ondc)} (approx)')
    print(f' - MF now:   {len(mf) + len(new_mf)} (approx)')
    print(f' - INS now:  {len(ins) + len(new_ins)} (approx)')


if __name__ == '__main__':
    ensure_all()
