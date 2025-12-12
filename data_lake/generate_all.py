"""
Master data generator - orchestrates all dataset generation.
"""
import json
import os
import sys
from datetime import datetime

# Ensure stdout/stderr use UTF-8 to avoid Windows console encoding errors
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    else:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
except Exception:
    # If reconfiguration fails, continue without crashing; prints may still error elsewhere
    pass

# Change to data_lake directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def run_step(step_name: str, script_path: str):
    """Run a generation step."""
    print(f"\n{'='*80}")
    print(f"  📦 {step_name}")
    print(f"{'='*80}")
    print(f"  [DEBUG] Script path: {script_path}")
    
    step_start = datetime.now()
    
    try:
        print(f"  [DEBUG] Reading script...")
        with open(script_path, 'r') as f:
            code = f.read()
        
        print(f"  [DEBUG] Executing script...")
        exec(code, {'__name__': '__main__', '__file__': script_path})
        
        step_end = datetime.now()
        duration = (step_end - step_start).total_seconds()
        
        print(f"\n  ✅ {step_name} completed successfully in {duration:.2f} seconds")
        return True
    except Exception as e:
        step_end = datetime.now()
        duration = (step_end - step_start).total_seconds()
        
        print(f"\n  ❌ {step_name} failed after {duration:.2f} seconds")
        print(f"  [ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main orchestrator."""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║          🏦 INDIAN FINANCIAL DATA LAKE - SYNTHETIC DATA GENERATOR          ║
║                                                                            ║
║   Simulating AA/FIP, GST, Bureau, Insurance, Mutual Funds, ONDC, OCEN     ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    start_time = datetime.now()
    print(f"[START TIME] {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # CLI: accept optional --customer-id to scope generation to a single customer
    import argparse
    parser = argparse.ArgumentParser(description='Generate synthetic data')
    parser.add_argument('--customer-id', dest='customer_id', help='Optional customer id to generate data for')
    args, _ = parser.parse_known_args()
    customer_id = args.customer_id
    if customer_id:
        print(f"\n[NOTE] Running generation for customer_id={customer_id}")
        # expose to scripts via environment variable
        os.environ['CUSTOMER_ID'] = str(customer_id)
    
    # Load configuration
    print("\n[STEP 0] Loading configuration...")
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Safely extract scale and optional values
    scale = config.get('scale', {})
    users = scale.get('users', 0)
    bank_accounts = scale.get('bank_accounts', 0)
    transactions = scale.get('transactions', 0)

    # date_range may be at top level or inside scale depending on config
    date_range = config.get('date_range') or scale.get('date_range')
    if date_range and isinstance(date_range, dict):
        dr_start = date_range.get('start', 'N/A')
        dr_end = date_range.get('end', 'N/A')
        date_range_text = f"{dr_start} to {dr_end}"
    else:
        date_range_text = "Not specified"

    banks = config.get('banks', []) or []

    print("\n📊 Configuration:")
    print(f"  • Users: {users:,}")
    print(f"  • Bank Accounts: {bank_accounts:,}")
    print(f"  • Transactions: {transactions:,}")
    print(f"  • Date Range: {date_range_text}")
    if banks:
        print(f"  • Banks: {', '.join(banks[:3])}... ({len(banks)} total)")
    else:
        print("  • Banks: Not specified")

    print("\n🔧 Messiness Configuration:")
    messiness = config.get('messiness_config', {})
    print(f"  • Date format variation: {messiness.get('date_format_variation', False)}")
    print(f"  • Numeric inconsistency: {messiness.get('numeric_format_inconsistency', False)}")
    print(f"  • Missing fields: {messiness.get('missing_field_probability', 0)}")
    print(f"  • Duplicates: {messiness.get('duplicate_probability', 0)}")

    # TEST_MODE: If set, override heavy scales for safe quick testing
    test_mode = os.environ.get('TEST_MODE') == '1'
    if test_mode:
        print("\n[TEST MODE] Detected TEST_MODE=1 — overriding scale for safe testing")
        users = 1000
        bank_accounts = 1500
        transactions = 50000
        # reflect overrides in config variables used below
        scale['users'] = users
        scale['bank_accounts'] = bank_accounts
        scale['transactions'] = transactions
    
    print("\n📋 Generation Plan:")
    
    # Generation steps
    steps = [
        ("Step 1: Banking Data (Consents, Accounts, Transactions)", 
         "generators/generate_banking_data.py"),
        ("Step 2: GST & Credit Bureau Data", 
         "generators/generate_additional_data.py"),
        ("Step 3: Insurance & Mutual Fund Data", 
         "generators/generate_insurance_mf.py"),
        ("Step 4: ONDC & OCEN Data", 
         "generators/generate_ondc_ocen.py"),
    ]
    
    print(f"  Total steps to execute: {len(steps)}")
    for i, (name, path) in enumerate(steps, 1):
        print(f"    {i}. {name}")
    
    print("\n" + "="*80)
    print("  🚀 STARTING DATA GENERATION")
    print("="*80)
    
    results = []

    if test_mode:
        print("\n[TEST MODE] Skipping execution of generator scripts (simulating success).")
        for step_name, _ in steps:
            print(f"  [TEST] Simulating: {step_name}")
            results.append((step_name, True))
    else:
        for step_name, script_path in steps:
            success = run_step(step_name, script_path)
            results.append((step_name, success))
    
    # Summary
    print("\n" + "="*80)
    print("  📊 GENERATION SUMMARY")
    print("="*80)
    
    print("\n📈 Results:")
    for i, (step_name, success) in enumerate(results, 1):
        status_icon = "✅" if success else "❌"
        status_text = "SUCCESS" if success else "FAILED"
        print(f"  {status_icon} Step {i}: {status_text:8} | {step_name}")
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "="*80)
    print(f"  ⏱️  Total time: {duration}")
    print(f"  [END TIME] {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    success_count = sum(1 for _, s in results if s)
    print(f"\n  📊 {success_count}/{len(results)} steps completed successfully")
    
    if success_count == len(results):
        print("\n  🎉 ALL RAW DATA GENERATED SUCCESSFULLY!")
        print("\n  📋 Next steps:")
        print("    1. Run: python pipeline\\clean_data.py")
        print("       → Clean and standardize raw data")
        print()
        print("    2. Run: python analytics\\generate_summaries.py")
        print("       → Generate statistics and analytics")
        print()
        print("    3. Run: python api_panel\\app.py")
        print("       → Launch web debug panel at http://localhost:5000")
    else:
        print("\n  ⚠️  Some steps failed. Please check the errors above.")
        print("  💡 Tip: Check that all required packages are installed")


if __name__ == "__main__":
    main()
