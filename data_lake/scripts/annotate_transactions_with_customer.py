#!/usr/bin/env python3
import json
from collections import Counter

RAW_TXN='f:/MSMELending/data_lake/raw/raw_transactions.ndjson'
RAW_ACC='f:/MSMELending/data_lake/raw/raw_accounts.ndjson'
OUT_TXN='f:/MSMELending/data_lake/raw/raw_transactions_with_customer_id.ndjson'
OUT_ACC='f:/MSMELending/data_lake/raw/raw_accounts_with_customer_id.ndjson'

NUM_CUSTOMERS=10
ACCOUNTS_PER_CUSTOMER=20

def account_to_customer(account_id):
    # account_id format ACC00000001
    try:
        n = int(account_id.replace('ACC',''))
    except Exception:
        return None
    idx = (n-1)//ACCOUNTS_PER_CUSTOMER + 1
    if idx > NUM_CUSTOMERS:
        idx = NUM_CUSTOMERS
    return f"CUST_MSM_{idx:05d}"

def annotate_accounts():
    with open(RAW_ACC,'r',encoding='utf-8') as fin, open(OUT_ACC,'w',encoding='utf-8') as fout:
        for ln in fin:
            if not ln.strip():
                continue
            try:
                o = json.loads(ln)
            except Exception:
                continue
            cust = account_to_customer(o.get('account_id',''))
            if cust:
                o['customer_id'] = cust
            fout.write(json.dumps(o,ensure_ascii=False)+"\n")

def annotate_transactions_and_count():
    counts = Counter()
    with open(RAW_TXN,'r',encoding='utf-8') as fin, open(OUT_TXN,'w',encoding='utf-8') as fout:
        for ln in fin:
            if not ln.strip():
                continue
            try:
                t = json.loads(ln)
            except Exception:
                continue
            acc = t.get('account_id')
            cust = account_to_customer(acc) if acc else None
            if cust:
                t['customer_id'] = cust
                counts[cust] += 1
            else:
                counts['UNKNOWN'] += 1
            fout.write(json.dumps(t,ensure_ascii=False)+"\n")
    return counts

if __name__=='__main__':
    print('Annotating accounts ->', OUT_ACC)
    annotate_accounts()
    print('Annotating transactions ->', OUT_TXN)
    counts = annotate_transactions_and_count()
    print('\nPer-customer transaction counts:')
    for k in sorted(counts.keys()):
        print(f"{k}: {counts[k]}")
