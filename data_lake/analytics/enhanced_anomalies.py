"""
Enhanced Anomaly Detection
Isolation Forest and change-point detection for transaction anomalies.
"""
import json
import os
from typing import Dict, List
from datetime import datetime
import numpy as np
from sklearn.ensemble import IsolationForest
from collections import defaultdict


def detect_anomalies_ml(customer_id: str, analytics_dir: str = None) -> Dict:
    """
    Enhanced anomaly detection using Isolation Forest.
    
    Args:
        customer_id: Customer ID
        analytics_dir: Path to analytics directory
    
    Returns:
        Dictionary with ML-detected anomalies and change points
    """
    if analytics_dir is None:
        analytics_dir = os.path.dirname(__file__)
    
    print(f"\n[INFO] Running enhanced anomaly detection for {customer_id}")
    
    # Load existing anomaly report
    anomaly_file = os.path.join(analytics_dir, f'{customer_id}_anomalies_report.json')
    earnings_file = os.path.join(analytics_dir, f'{customer_id}_earnings_spendings.json')
    
    try:
        with open(anomaly_file, 'r') as f:
            existing_anomalies = json.load(f)
        with open(earnings_file, 'r') as f:
            earnings_data = json.load(f)
    except FileNotFoundError as e:
        print(f"[ERROR] Required file not found: {e}")
        return {}
    
    # Extract transaction features for ML model
    high_value_txns = existing_anomalies.get('high_value_transactions', [])
    
    if not high_value_txns or len(high_value_txns) < 10:
        print("[WARN] Insufficient transaction data for ML anomaly detection")
        return {}
    
    # Prepare features: amount, day_of_month, description_length
    features = []
    txn_records = []
    
    for txn in high_value_txns:
        amount = txn.get('amount', 0)
        date_str = txn.get('date', '')
        description = txn.get('description', '') or txn.get('narration', '')
        
        # Extract day of month
        day = 15  # default
        try:
            if '-' in date_str:
                day = int(date_str.split('-')[2][:2])
        except:
            pass
        
        desc_len = len(description) if description else 0
        
        features.append([amount, day, desc_len])
        txn_records.append(txn)
    
    features = np.array(features)
    
    # Run Isolation Forest
    iso_forest = IsolationForest(
        contamination=0.1,  # Expect 10% anomalies
        random_state=42,
        n_estimators=100
    )
    predictions = iso_forest.fit_predict(features)
    anomaly_scores = iso_forest.score_samples(features)
    
    # Extract anomalies (prediction = -1)
    ml_anomalies = []
    for i, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
        if pred == -1:
            txn = txn_records[i].copy()
            txn['anomaly_score'] = round(float(score), 4)
            txn['anomaly_type'] = 'ML_DETECTED'
            ml_anomalies.append(txn)
    
    # Change-point detection on monthly cashflow
    monthly_inflow = earnings_data.get('cashflow_metrics', {}).get('monthly_inflow', {})
    monthly_outflow = earnings_data.get('cashflow_metrics', {}).get('monthly_outflow', {})
    
    # Sort months and compute changes
    months = sorted(set(monthly_inflow.keys()) | set(monthly_outflow.keys()))
    inflow_series = [monthly_inflow.get(m, 0) for m in months]
    outflow_series = [monthly_outflow.get(m, 0) for m in months]
    
    # Simple change-point detection: look for jumps > 2 std deviations
    change_points = []
    
    if len(inflow_series) > 3:
        inflow_mean = np.mean(inflow_series)
        inflow_std = np.std(inflow_series)
        
        for i in range(1, len(inflow_series)):
            diff = abs(inflow_series[i] - inflow_series[i-1])
            if diff > 2 * inflow_std:
                change_points.append({
                    'month': months[i],
                    'type': 'INFLOW_JUMP',
                    'previous_value': round(inflow_series[i-1], 2),
                    'current_value': round(inflow_series[i], 2),
                    'change': round(diff, 2),
                    'change_pct': round((diff / inflow_series[i-1] * 100) if inflow_series[i-1] > 0 else 0, 2)
                })
    
    if len(outflow_series) > 3:
        outflow_mean = np.mean(outflow_series)
        outflow_std = np.std(outflow_series)
        
        for i in range(1, len(outflow_series)):
            diff = abs(outflow_series[i] - outflow_series[i-1])
            if diff > 2 * outflow_std:
                change_points.append({
                    'month': months[i],
                    'type': 'OUTFLOW_JUMP',
                    'previous_value': round(outflow_series[i-1], 2),
                    'current_value': round(outflow_series[i], 2),
                    'change': round(diff, 2),
                    'change_pct': round((diff / outflow_series[i-1] * 100) if outflow_series[i-1] > 0 else 0, 2)
                })
    
    # Compile result
    result = {
        'customer_id': customer_id,
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'ml_anomalies': {
            'total_detected': len(ml_anomalies),
            'transactions': ml_anomalies[:20],  # Top 20
            'detection_method': 'Isolation Forest',
            'contamination_rate': 0.1
        },
        'change_points': {
            'total_detected': len(change_points),
            'points': change_points,
            'detection_method': 'Statistical threshold (2σ)'
        },
        'combined_summary': {
            'total_anomalies': len(ml_anomalies) + len(change_points),
            'ml_transaction_anomalies': len(ml_anomalies),
            'cashflow_change_points': len(change_points)
        },
        'risk_assessment': {
            'risk_level': 'High' if len(ml_anomalies) + len(change_points) > 10 else 'Medium' if len(ml_anomalies) + len(change_points) > 5 else 'Low',
            'risk_explanation': f'Detected {len(ml_anomalies)} ML anomalies and {len(change_points)} change points'
        }
    }
    
    # Save result
    output_file = os.path.join(analytics_dir, f'{customer_id}_enhanced_anomalies.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"[✓] Enhanced anomalies saved to {output_file}")
    print(f"\n{'='*60}")
    print(f"ENHANCED ANOMALY DETECTION")
    print(f"{'='*60}")
    print(f"ML-Detected Anomalies: {len(ml_anomalies)}")
    print(f"Change Points: {len(change_points)}")
    print(f"Risk Level: {result['risk_assessment']['risk_level']}")
    print(f"{'='*60}\n")
    
    return result


if __name__ == '__main__':
    import sys
    
    customer_id = sys.argv[1] if len(sys.argv) > 1 else 'CUST_MSM_00001'
    analytics_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(__file__)
    
    detect_anomalies_ml(customer_id, analytics_dir)
