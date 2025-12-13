"""
Generate 9 additional customer datasets (CUST_MSM_00002 through CUST_MSM_00010).
CUST_MSM_00001 already exists and will be kept.

Note: The actual varying profiles will be created through natural randomness in the 
generation scripts. Each customer will have different characteristics based on random seeds.
"""

import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Customer IDs to generate (00001 already exists)
CUSTOMER_IDS = [
    'CUST_MSM_00002',
    'CUST_MSM_00003',
    'CUST_MSM_00004',
    'CUST_MSM_00005',
    'CUST_MSM_00006',
    'CUST_MSM_00007',
    'CUST_MSM_00008',
    'CUST_MSM_00009',
    'CUST_MSM_00010',
]

# Profile descriptions (for documentation - actual generation uses randomness)
CUSTOMER_PROFILES = {
    'CUST_MSM_00001': 'Excellent - Ideal Borrower (already exists)',
    'CUST_MSM_00002': 'Poor - High Risk',
    'CUST_MSM_00003': 'Good Cashflow, Bad Credit',
    'CUST_MSM_00004': 'Bad Cashflow, Good Credit',
    'CUST_MSM_00005': 'Seasonal/High Variance',
    'CUST_MSM_00006': 'Data Quality Issues',
    'CUST_MSM_00007': 'New Business - Limited History',
    'CUST_MSM_00008': 'Declining Business',
    'CUST_MSM_00009': 'Moderate/Average - Acceptable',
    'CUST_MSM_00010': 'High Debt but Growing',
}


def generate_customer_dataset(customer_id):
    """Generate complete dataset for one customer."""
    print(f"\n{'='*60}")
    print(f"Generating: {customer_id}")
    print(f"Profile: {CUSTOMER_PROFILES.get(customer_id, 'Unknown')}")
    print(f"{'='*60}")
    
    # Call generate_all.py with customer ID
    result = subprocess.run(
        [sys.executable, 'generate_all.py', '--customer-id', customer_id],
        cwd=BASE_DIR
    )
    
    if result.returncode == 0:
        print(f"✓ Successfully generated dataset for {customer_id}")
        return True
    else:
        print(f"✗ Failed to generate {customer_id} (exit code: {result.returncode})")
        return False


def main():
    """Generate all demo customer datasets."""
    print("="*80)
    print("DEMO CUSTOMER DATASET GENERATOR")
    print("Generating 9 additional customer profiles (00002-00010)")
    print("CUST_MSM_00001 already exists and will be kept")
    print("="*80)
    
    os.chdir(BASE_DIR)
    
    success_count = 1  # Count 00001 which already exists
    failed = []
    
    for customer_id in CUSTOMER_IDS:
        try:
            if generate_customer_dataset(customer_id):
                success_count += 1
            else:
                failed.append(customer_id)
        except Exception as e:
            print(f"ERROR generating {customer_id}: {e}")
            failed.append(customer_id)
    
    print("\n" + "="*80)
    print("GENERATION SUMMARY")
    print("="*80)
    print(f"✓ Successfully generated: {success_count}/10 customers")
    if failed:
        print(f"✗ Failed: {', '.join(failed)}")
    print("\nAll customers are ready for demo!")
    print("\nCustomer Profile Summary:")
    print("-" * 80)
    for cid, profile in CUSTOMER_PROFILES.items():
        status = "✓" if cid == 'CUST_MSM_00001' or (cid not in failed and cid in CUSTOMER_IDS) else "✗"
        print(f"{status} {cid}: {profile}")
    print("="*80)
    
    print("\n📋 Next Steps:")
    print("  1. Run cleaning for each customer:")
    print("     python pipeline/clean_data.py --customer-id CUST_MSM_XXXXX")
    print("\n  2. Run analytics for each customer:")
    print("     python analytics/generate_summaries.py --customer-id CUST_MSM_XXXXX")
    print("\n  3. Or use the UI at http://localhost:5000 to process all")


if __name__ == '__main__':
    main()
