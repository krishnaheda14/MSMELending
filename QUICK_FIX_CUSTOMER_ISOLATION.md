# Quick Fix: Add Customer ID Filtering

## Problem
All customers currently share the same data because profile modifiers overwrite `raw/raw_transactions.ndjson`.

## Solution
Add `customer_id` field to all generated data and filter by it.

## Implementation

### Step 1: Update Transaction Generator

Edit `generators/generate_transactions.py`:

```python
def generate_transaction(customer_id=None):
    """Generate a single transaction with customer_id"""
    return {
        "transaction_id": f"TXN_{uuid.uuid4().hex[:12].upper()}",
        "customer_id": customer_id or "CUST_MSM_00001",  # ADD THIS
        "account_number": f"ACC_{random.randint(10000, 99999)}",
        # ... rest of fields
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--customer-id', default='CUST_MSM_00001')
    args = parser.parse_args()
    
    # Generate with customer_id
    for _ in range(num_transactions):
        txn = generate_transaction(customer_id=args.customer_id)
        # ...
```

### Step 2: Update apply_profile.py

```python
def apply_customer_profile(customer_id, profile_type):
    """Apply specific characteristics to a customer's data."""
    
    # Load ALL transactions
    txn_file = f'raw/raw_transactions.ndjson'
    all_transactions = []
    with open(txn_file, 'r') as f:
        for line in f:
            if line.strip():
                all_transactions.append(json.loads(line))
    
    # FILTER to only this customer's transactions
    customer_transactions = [t for t in all_transactions if t.get('customer_id') == customer_id]
    other_transactions = [t for t in all_transactions if t.get('customer_id') != customer_id]
    
    print(f"  Loaded {len(customer_transactions)} transactions for {customer_id}")
    print(f"  Keeping {len(other_transactions)} transactions for other customers")
    
    # Apply modifications ONLY to customer's data
    if profile_type == 'declining':
        customer_transactions = modify_transactions_for_declining_business(customer_transactions)
    # ... etc
    
    # Merge back and save
    all_transactions = other_transactions + customer_transactions
    with open(txn_file, 'w') as f:
        for txn in all_transactions:
            f.write(json.dumps(txn) + '\n')
```

### Step 3: Update Config for Realistic Scales

Edit `config.json`:

```json
{
  "scale": {
    "customers": 10,
    "transactions_per_customer": 2000,
    "gst_returns_per_customer": 48,
    "insurance_policies_per_customer": 15,
    "mutual_funds_per_customer": 3,
    "ondc_orders_per_customer": 800,
    "ocen_applications_per_customer": 5
  }
}
```

### Step 4: Update generate_all_specialized.bat

```batch
REM Generate base data for all customers FIRST
python generate_all.py --generate-all-customers

REM Then apply profiles WITHOUT regenerating base data
python apply_profile.py CUST_MSM_00002 high_seasonality --no-regenerate
python apply_profile.py CUST_MSM_00003 high_debt --no-regenerate
python apply_profile.py CUST_MSM_00004 high_growth --no-regenerate
python apply_profile.py CUST_MSM_00007 declining --no-regenerate
```

### Step 5: Add --no-regenerate flag to apply_profile.py

```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('customer_id')
    parser.add_argument('profile_type')
    parser.add_argument('--no-regenerate', action='store_true')
    args = parser.parse_args()
    
    if not args.no_regenerate:
        # Generate base data
        os.system(f'python generate_all.py --customer-id {args.customer_id}')
    
    # Apply profile
    apply_customer_profile(args.customer_id, args.profile_type)
```

## Testing

After implementing:

```powershell
# Regenerate all data
cd f:\MSMELending\data_lake
python cleanup_old_data.py
python generate_all.py --generate-all-customers
python apply_profile.py CUST_MSM_00007 declining --no-regenerate

# Verify isolation
python analytics/generate_summaries.py --customer-id CUST_MSM_00007
python analytics/generate_summaries.py --customer-id CUST_MSM_00001

# Check metrics
$json7 = Get-Content analytics\CUST_MSM_00007_earnings_spendings.json | ConvertFrom-Json
$json1 = Get-Content analytics\CUST_MSM_00001_earnings_spendings.json | ConvertFrom-Json

Write-Host "CUST_MSM_00007 TTM Growth: $($json7.business_health.ttm_revenue_growth)%"
Write-Host "CUST_MSM_00001 TTM Growth: $($json1.business_health.ttm_revenue_growth)%"
Write-Host "Total Inflows should be DIFFERENT"
```

Expected:
- CUST_MSM_00007: **Negative growth** (-20% or less)
- CUST_MSM_00001: **Positive growth** (10-30%)
- Different Total Inflow values
