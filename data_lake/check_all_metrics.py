#!/usr/bin/env python3
"""
Extract key metrics from all customer analytics files.
"""
import json
import os

CUSTOMERS = [f'CUST_MSM_{i:05d}' for i in range(1, 11)]

def get_metrics(customer_id):
    """Extract key metrics for a customer."""
    try:
        with open(f'analytics/{customer_id}_earnings_spendings.json', 'r') as f:
            data = json.load(f)
        
        cashflow = data.get('cashflow_metrics', {})
        credit = data.get('credit_behavior', {})
        expense = data.get('expense_composition', {})
        health = data.get('business_health', {})
        
        return {
            'seasonality': cashflow.get('seasonality_index', 0),
            'debt_ratio': expense.get('debt_servicing_ratio', 0),
            'loan_payments': credit.get('total_loan_payments', 0),
            'bounce_count': credit.get('bounce_count', 0),
            'growth': health.get('credit_growth_rate', 0),
            'concentration': cashflow.get('top_customer_dependence', 0),
            'income_cv': cashflow.get('income_stability_cv', 0)
        }
    except Exception as e:
        print(f"Error reading {customer_id}: {e}")
        return None

def main():
    print("=" * 80)
    print("CUSTOMER ANALYTICS - KEY METRICS SUMMARY")
    print("=" * 80)
    print()
    
    profiles = [
        ("CUST_MSM_00001", "Baseline", "Normal metrics"),
        ("CUST_MSM_00002", "High Seasonality", ">100% seasonality"),
        ("CUST_MSM_00003", "High Debt", "DSR >40%"),
        ("CUST_MSM_00004", "High Growth", ">50% growth"),
        ("CUST_MSM_00005", "Stable Income", "CV <15%"),
        ("CUST_MSM_00006", "High Bounce", ">10 bounces"),
        ("CUST_MSM_00007", "Declining", "Negative growth"),
        ("CUST_MSM_00008", "Concentration", "Top 1 >70%"),
        ("CUST_MSM_00009", "High Growth", ">50% growth"),
        ("CUST_MSM_00010", "High Seasonality", ">100% seasonality"),
    ]
    
    for cust_id, profile, expected in profiles:
        print(f"\n{cust_id} - {profile}")
        print(f"  Expected: {expected}")
        
        metrics = get_metrics(cust_id)
        if metrics:
            print(f"  Seasonality:    {metrics['seasonality']:>8.2f}%")
            print(f"  Debt Ratio:     {metrics['debt_ratio']:>8.2f}%")
            print(f"  Loan Payments:  Rs{metrics['loan_payments']:>12,.0f}")
            print(f"  Bounce Count:   {metrics['bounce_count']:>8}")
            print(f"  Growth Rate:    {metrics['growth']:>8.2f}%")
            print(f"  Concentration:  {metrics['concentration']:>8.2f}%")
            print(f"  Income CV:      {metrics['income_cv']:>8.2f}%")
            
            # Highlight focus metric
            if "Seasonality" in profile and metrics['seasonality'] > 80:
                print(f"  → PRIMARY ISSUE PRESENT: High Seasonality")
            elif "Debt" in profile and metrics['debt_ratio'] > 30:
                print(f"  → PRIMARY ISSUE PRESENT: High Debt")
            elif "Bounce" in profile and metrics['bounce_count'] > 5:
                print(f"  → PRIMARY ISSUE PRESENT: High Bounce Rate")
            elif "Growth" in profile and metrics['growth'] > 40:
                print(f"  → PRIMARY ISSUE PRESENT: High Growth")
            elif "Concentration" in profile and metrics['concentration'] > 60:
                print(f"  → PRIMARY ISSUE PRESENT: High Concentration")
            elif "Declining" in profile and metrics['growth'] < -10:
                print(f"  → PRIMARY ISSUE PRESENT: Declining Business")
            elif "Stable" in profile and metrics['income_cv'] < 20:
                print(f"  → PRIMARY ISSUE PRESENT: Stable Income")
            else:
                print(f"  ⚠ PRIMARY ISSUE NOT YET PROMINENT")
        else:
            print(f"  ✗ No analytics found")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
