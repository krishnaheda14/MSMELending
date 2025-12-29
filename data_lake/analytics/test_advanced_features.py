"""
Comprehensive Test Script for Advanced Features
Tests all new analytics modules on a single customer.
"""
import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import all advanced modules
try:
    from risk_model import analyze_risk_model
    from forecasting import compute_cashflow_forecast
    from reconciliation import reconcile_transactions
    from enhanced_anomalies import detect_anomalies_ml
    from recommendations import recommend_credit_products
except ImportError as e:
    print(f"[ERROR] Failed to import module: {e}")
    print("[INFO] Make sure all required dependencies are installed:")
    print("  pip install scikit-learn numpy python-dateutil")
    sys.exit(1)


def print_section_header(title: str):
    """Print formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_all_features(customer_id: str = 'CUST_MSM_00001'):
    """
    Run all advanced features and generate comprehensive report.
    
    Args:
        customer_id: Customer ID to test
    """
    analytics_dir = os.path.dirname(__file__)
    
    print_section_header(f"ADVANCED FEATURES TEST - {customer_id}")
    print(f"Started at: {datetime.utcnow().isoformat()}Z\n")
    
    # Check if analytics files exist
    required_files = [
        f'{customer_id}_overall_summary.json',
        f'{customer_id}_earnings_spendings.json',
        f'{customer_id}_gst_summary.json',
        f'{customer_id}_credit_summary.json',
        f'{customer_id}_anomalies_report.json'
    ]
    
    missing_files = []
    for filename in required_files:
        filepath = os.path.join(analytics_dir, filename)
        if not os.path.exists(filepath):
            missing_files.append(filename)
    
    if missing_files:
        print(f"[ERROR] Missing required analytics files:")
        for f in missing_files:
            print(f"  • {f}")
        print(f"\n[INFO] Please run the following commands first:")
        print(f"  python ../generate_all.py --customer-id {customer_id}")
        print(f"  python ../pipeline/clean_data.py --customer-id {customer_id}")
        print(f"  python generate_summaries.py --customer-id {customer_id}")
        return None
    
    results = {}
    errors = []
    
    # 1. Explainable Risk Model
    print_section_header("1. EXPLAINABLE RISK MODEL")
    try:
        risk_result = analyze_risk_model(customer_id, analytics_dir)
        results['risk_model'] = risk_result
        print("[✓] Risk model completed successfully")
    except Exception as e:
        error_msg = f"Risk Model Error: {str(e)}"
        print(f"[✗] {error_msg}")
        errors.append(error_msg)
        results['risk_model'] = None
    
    # 2. Cashflow Forecasting (90 days)
    print_section_header("2. CASHFLOW FORECASTING")
    try:
        forecast_result = compute_cashflow_forecast(customer_id, analytics_dir, forecast_days=90)
        results['cashflow_forecast'] = forecast_result
        print("[✓] Cashflow forecast completed successfully")
    except Exception as e:
        error_msg = f"Cashflow Forecast Error: {str(e)}"
        print(f"[✗] {error_msg}")
        errors.append(error_msg)
        results['cashflow_forecast'] = None
    
    # 3. GST/Bank/ONDC Reconciliation
    print_section_header("3. GST/BANK/ONDC RECONCILIATION")
    try:
        reconciliation_result = reconcile_transactions(customer_id, analytics_dir)
        results['reconciliation'] = reconciliation_result
        print("[✓] Reconciliation completed successfully")
    except Exception as e:
        error_msg = f"Reconciliation Error: {str(e)}"
        print(f"[✗] {error_msg}")
        errors.append(error_msg)
        results['reconciliation'] = None
    
    # 4. Enhanced Anomaly Detection
    print_section_header("4. ENHANCED ANOMALY DETECTION")
    try:
        anomaly_result = detect_anomalies_ml(customer_id, analytics_dir)
        results['enhanced_anomalies'] = anomaly_result
        print("[✓] Enhanced anomaly detection completed successfully")
    except Exception as e:
        error_msg = f"Enhanced Anomaly Detection Error: {str(e)}"
        print(f"[✗] {error_msg}")
        errors.append(error_msg)
        results['enhanced_anomalies'] = None
    
    # 5. Credit Product Recommendations
    print_section_header("5. CREDIT PRODUCT RECOMMENDATIONS")
    try:
        recommendations_result = recommend_credit_products(customer_id, analytics_dir)
        results['recommendations'] = recommendations_result
        print("[✓] Credit recommendations completed successfully")
    except Exception as e:
        error_msg = f"Credit Recommendations Error: {str(e)}"
        print(f"[✗] {error_msg}")
        errors.append(error_msg)
        results['recommendations'] = None
    
    # Generate comprehensive summary report
    print_section_header("COMPREHENSIVE TEST SUMMARY")
    
    successful = sum(1 for v in results.values() if v is not None)
    total = len(results)
    
    print(f"Customer ID: {customer_id}")
    print(f"Tests Completed: {successful}/{total}")
    print(f"Success Rate: {successful/total*100:.1f}%")
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z\n")
    
    # Module-wise status
    print("Module Status:")
    for module, result in results.items():
        status = "✓ PASS" if result is not None else "✗ FAIL"
        print(f"  {status}  {module.replace('_', ' ').title()}")
    
    # Error summary
    if errors:
        print(f"\n⚠️  Errors Encountered:")
        for error in errors:
            print(f"  • {error}")
    else:
        print(f"\n✅ All tests passed successfully!")
    
    # Key insights extraction
    if results.get('risk_model'):
        print(f"\n📊 Key Insights:")
        risk_data = results['risk_model']['risk_assessment']
        print(f"  Risk Score: {risk_data['risk_score']}/100 ({risk_data['risk_category']})")
        
        if results.get('cashflow_forecast'):
            forecast_data = results['cashflow_forecast']['forecast']
            print(f"  90-Day Forecast: ₹{forecast_data['total_expected_surplus']:,.2f} surplus expected")
            print(f"  Runway: {results['cashflow_forecast']['risk_assessment']['runway_months']} months")
        
        if results.get('reconciliation'):
            recon_data = results['reconciliation']['summary']
            print(f"  GST Reconciliation: {recon_data['reconciliation_rate']}%")
        
        if results.get('enhanced_anomalies'):
            anom_data = results['enhanced_anomalies']['combined_summary']
            print(f"  Anomalies Detected: {anom_data['total_anomalies']} total")
        
        if results.get('recommendations'):
            rec_data = results['recommendations']
            print(f"  Recommendation: {rec_data['overall_recommendation']}")
            print(f"  Products Available: {len(rec_data['recommended_products'])}")
    
    # Save comprehensive report
    report = {
        'customer_id': customer_id,
        'test_timestamp': datetime.utcnow().isoformat() + 'Z',
        'success_rate': f"{successful}/{total}",
        'results': {
            'risk_model': {
                'status': 'SUCCESS' if results.get('risk_model') else 'FAILED',
                'output_file': f'{customer_id}_risk_model.json' if results.get('risk_model') else None
            },
            'cashflow_forecast': {
                'status': 'SUCCESS' if results.get('cashflow_forecast') else 'FAILED',
                'output_file': f'{customer_id}_cashflow_forecast.json' if results.get('cashflow_forecast') else None
            },
            'reconciliation': {
                'status': 'SUCCESS' if results.get('reconciliation') else 'FAILED',
                'output_file': f'{customer_id}_reconciliation.json' if results.get('reconciliation') else None
            },
            'enhanced_anomalies': {
                'status': 'SUCCESS' if results.get('enhanced_anomalies') else 'FAILED',
                'output_file': f'{customer_id}_enhanced_anomalies.json' if results.get('enhanced_anomalies') else None
            },
            'recommendations': {
                'status': 'SUCCESS' if results.get('recommendations') else 'FAILED',
                'output_file': f'{customer_id}_recommendations.json' if results.get('recommendations') else None
            }
        },
        'errors': errors
    }
    
    report_file = os.path.join(analytics_dir, f'{customer_id}_advanced_features_test_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Full test report saved to: {report_file}")
    
    print_section_header("TEST COMPLETED")
    
    return report


if __name__ == '__main__':
    customer_id = sys.argv[1] if len(sys.argv) > 1 else 'CUST_MSM_00001'
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          MSME LENDING - ADVANCED FEATURES TEST SUITE             ║
╚══════════════════════════════════════════════════════════════════╝

This script tests the following advanced features:
  1. Explainable Risk Model (ML-based with feature attributions)
  2. Cashflow Forecasting (Holt-Winters, 90-day forecast)
  3. GST/Bank/ONDC Reconciliation (Fuzzy matching)
  4. Enhanced Anomaly Detection (Isolation Forest + Change Points)
  5. Credit Product Recommendations (Personalized loan products)

Required Dependencies:
  - scikit-learn
  - numpy
  - python-dateutil

""")
    
    # Check dependencies
    try:
        import sklearn
        import numpy
        import dateutil
        print("[✓] All dependencies installed\n")
    except ImportError as e:
        print(f"[✗] Missing dependency: {e}")
        print("\nInstall missing packages:")
        print("  pip install scikit-learn numpy python-dateutil\n")
        sys.exit(1)
    
    # Run tests
    test_all_features(customer_id)
