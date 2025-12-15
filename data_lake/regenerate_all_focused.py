#!/usr/bin/env python
"""
Simple orchestrator to regenerate all customer profiles with focused characteristics.
Calls existing generate_specialized_customers.py for each customer.
"""
import subprocess
import sys
import os
import json
import time
from datetime import datetime

# Customer profiles - ONE focus per customer
CUSTOMERS = [
    ("CUST_MSM_00001", "baseline", "Healthy balanced business"),
    ("CUST_MSM_00002", "high_seasonality", "Seasonal business >100% variation"),
    ("CUST_MSM_00003", "high_debt", "Heavy loan burden DSR >40%"),
    ("CUST_MSM_00004", "high_growth", "Strong growth >50% CAGR"),
    ("CUST_MSM_00005", "stable_income", "Stable income CV <15%"),
    ("CUST_MSM_00006", "high_bounce", "Payment failures >5% bounce rate"),
    ("CUST_MSM_00007", "declining", "Revenue decline -20% to -40%"),
    ("CUST_MSM_00008", "concentration", "Top customer >70% revenue"),
    ("CUST_MSM_00009", "high_growth", "Strong growth variant 2"),
    ("CUST_MSM_00010", "high_seasonality", "Seasonal variant 2"),
]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def run_cmd(cmd, desc):
    """Run command and return success"""
    log(f"Running: {desc}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        log(f"✓ {desc} completed")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        log(f"✗ {desc} failed: {e.stderr}")
        return False, e.stderr

def read_metric(customer_id, metric_name):
    """Read specific metric from analytics"""
    try:
        with open(f"analytics/{customer_id}_earnings_spendings.json", "r") as f:
            data = json.load(f)
        
        # Map metric names to JSON paths
        if metric_name == "seasonality":
            return data.get("cashflow_metrics", {}).get("seasonality_index", 0)
        elif metric_name == "debt":
            return data.get("expense_composition", {}).get("debt_servicing_ratio", 0)
        elif metric_name == "bounce":
            return data.get("credit_behavior", {}).get("bounce_count", 0)
        elif metric_name == "growth":
            return data.get("business_health", {}).get("credit_growth_rate", 0)
        elif metric_name == "concentration":
            return data.get("cashflow_metrics", {}).get("top_customer_dependence", 0)
        elif metric_name == "loan_payments":
            return data.get("credit_behavior", {}).get("total_loan_payments", 0)
        return 0
    except:
        return 0

def main():
    log("="*80)
    log("REGENERATING ALL CUSTOMER PROFILES WITH FOCUSED CHARACTERISTICS")
    log("="*80)
    
    results = []
    
    for customer_id, profile_type, description in CUSTOMERS:
        log("")
        log(f"{'='*80}")
        log(f"{customer_id} - {description}")
        log(f"Profile: {profile_type}")
        log(f"{'='*80}")
        
        # Step 1: Generate profile-aware data
        log(f"Step 1/2: Generating focused data...")
        success, _ = run_cmd(
            f"python generate_specialized_customers.py --customer-id {customer_id}",
            f"Data generation for {customer_id}"
        )
        
        if not success:
            log(f"⚠️ Skipping analytics for {customer_id}")
            continue
        
        # Step 2: Generate analytics
        log(f"Step 2/2: Generating analytics...")
        success, _ = run_cmd(
            f"python analytics/generate_summaries.py --customer-id {customer_id}",
            f"Analytics for {customer_id}"
        )
        
        if success:
            # Read key metrics
            seasonality = read_metric(customer_id, "seasonality")
            debt = read_metric(customer_id, "debt")
            bounce = read_metric(customer_id, "bounce")
            growth = read_metric(customer_id, "growth")
            concentration = read_metric(customer_id, "concentration")
            loan_amt = read_metric(customer_id, "loan_payments")
            
            log(f"✓ Metrics Generated:")
            log(f"  • Seasonality: {seasonality:.1f}%")
            log(f"  • Debt Ratio: {debt:.1f}%")
            log(f"  • Bounce Count: {bounce}")
            log(f"  • Loan Payments: ₹{loan_amt:,.0f}")
            log(f"  • Growth: {growth:.1f}%")
            log(f"  • Concentration: {concentration:.1f}%")
            
            results.append({
                'customer_id': customer_id,
                'profile': profile_type,
                'description': description,
                'seasonality': seasonality,
                'debt': debt,
                'bounce': bounce,
                'growth': growth,
                'concentration': concentration,
                'loan_payments': loan_amt
            })
        
        time.sleep(0.5)
    
    # Generate summary report
    log("")
    log("="*80)
    log("GENERATING SUMMARY REPORT")
    log("="*80)
    
    md_lines = []
    md_lines.append("# Customer Analytics Summary\n\n")
    md_lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    md_lines.append("## Overview\n\n")
    md_lines.append("Each customer profile is focused on ONE primary lending concern.\n\n")
    md_lines.append("## Customer Profiles\n\n")
    md_lines.append("| Customer | Profile Focus | Key Metric | Value | Status |\n")
    md_lines.append("|----------|---------------|------------|-------|--------|\n")
    
    for r in results:
        cid = r['customer_id']
        prof = r['profile']
        desc = r['description']
        
        # Determine focus metric and validation
        if 'seasonality' in prof:
            metric = "Seasonality Index"
            value = f"{r['seasonality']:.1f}%"
            status = "**✓ HIGH**" if r['seasonality'] > 80 else "⚠️ Low"
        elif 'debt' in prof:
            metric = "Debt Service Ratio"
            value = f"{r['debt']:.1f}%"
            status = "**✓ HIGH**" if r['debt'] > 35 else "⚠️ Low"
            # Also check if loan payments exist
            if r['loan_payments'] > 0:
                value = f"{r['debt']:.1f}% (₹{r['loan_payments']:,.0f})"
            else:
                status = "**⚠️ NO LOANS**"
        elif 'bounce' in prof:
            metric = "Bounce Count"
            value = str(r['bounce'])
            status = "**✓ HIGH**" if r['bounce'] > 5 else "⚠️ Low"
        elif 'growth' in prof:
            metric = "Credit Growth"
            value = f"{r['growth']:.1f}%"
            status = "**✓ HIGH**" if r['growth'] > 40 else "⚠️ Low"
        elif 'concentration' in prof:
            metric = "Top Customer %"
            value = f"{r['concentration']:.1f}%"
            status = "**✓ HIGH**" if r['concentration'] > 60 else "⚠️ Low"
        elif 'declining' in prof:
            metric = "Revenue Growth"
            value = f"{r['growth']:.1f}%"
            status = "**✓ NEGATIVE**" if r['growth'] < -10 else "⚠️ Not declining"
        else:
            metric = "Seasonality"
            value = f"{r['seasonality']:.1f}%"
            status = "✓ Normal"
        
        md_lines.append(f"| {cid} | {prof.replace('_', ' ').title()} | {metric} | {value} | {status} |\n")
    
    md_lines.append("\n## Detailed Metrics\n\n")
    for r in results:
        md_lines.append(f"### {r['customer_id']} - {r['description']}\n\n")
        md_lines.append(f"**Profile Focus**: {r['profile'].replace('_', ' ').title()}\n\n")
        md_lines.append("**All Metrics**:\n\n")
        md_lines.append(f"- **Seasonality Index**: {r['seasonality']:.2f}%\n")
        md_lines.append(f"- **Debt Service Ratio**: {r['debt']:.2f}%\n")
        md_lines.append(f"- **Total Loan Payments**: ₹{r['loan_payments']:,.2f}\n")
        md_lines.append(f"- **Bounce Count**: {r['bounce']}\n")
        md_lines.append(f"- **Credit Growth Rate**: {r['growth']:.2f}%\n")
        md_lines.append(f"- **Customer Concentration**: {r['concentration']:.2f}%\n\n")
    
    # Write report
    report_path = "docs/CUSTOMER_ANALYTICS_SUMMARY.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.writelines(md_lines)
    
    log(f"✓ Summary report: {report_path}")
    log("")
    log("="*80)
    log("REGENERATION COMPLETE!")
    log("="*80)
    log(f"✓ Processed {len(results)} customers")
    log(f"✓ Report: {report_path}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n⚠️ Interrupted")
        sys.exit(1)

