"""
LSTM-based anomaly detection for monthly cashflow time series.
Detects anomalies in monthly aggregate data (e.g., ₹30.9M spike in 2025-01).
Uses LSTM autoencoder with dynamic threshold based on reconstruction error.
"""

import numpy as np
import pandas as pd
import json
import os
from datetime import datetime
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Try to import tensorflow, fall back to simple threshold if not available
try:
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True
except ImportError:
    print("⚠️  TensorFlow not available. Using statistical threshold-based detection instead.")
    TENSORFLOW_AVAILABLE = False


class LSTMCashflowAnomalyDetector:
    """Detect anomalies in monthly cashflow time series using LSTM autoencoder."""
    
    def __init__(self, threshold_percentile=99.0):
        """
        Initialize detector.
        
        Args:
            threshold_percentile: Percentile for reconstruction error threshold (default 99.0)
        """
        self.threshold_percentile = threshold_percentile
        self.model = None
        self.scaler = StandardScaler()
        self.threshold = None
        
    def normalize_month_format(self, month_str):
        """Convert various month formats to YYYY-MM."""
        try:
            # Handle different formats
            if '-' in month_str and len(month_str.split('-')[0]) == 2:
                # DD-MM-Y format
                parts = month_str.split('-')
                return f"{parts[2]}-{parts[1]:0>2}"
            elif '/' in month_str:
                # MM/YYYY format
                parts = month_str.split('/')
                if len(parts[0]) == 2:
                    return f"{parts[1]}-{parts[0]}"
                else:
                    return f"{parts[0]}-{parts[1]:0>2}"
            elif month_str[0].isdigit() and len(month_str.split('-')[0]) == 4:
                # YYYY-MM format (already correct)
                return month_str
            else:
                # Try parsing as date string
                dt = pd.to_datetime(month_str, errors='coerce')
                if pd.notna(dt):
                    return dt.strftime('%Y-%m')
        except Exception:
            pass
        return month_str
        
    def prepare_time_series(self, monthly_inflow):
        """Prepare and sort time series data."""
        # Convert to dataframe
        data = []
        for month, amount in monthly_inflow.items():
            normalized_month = self.normalize_month_format(month)
            data.append({'month': normalized_month, 'amount': float(amount)})
        
        df = pd.DataFrame(data)
        
        # Sort by month
        df['month_dt'] = pd.to_datetime(df['month'], errors='coerce')
        df = df.dropna(subset=['month_dt'])
        df = df.sort_values('month_dt')
        df = df.reset_index(drop=True)
        
        return df
    
    def create_sequences(self, data, sequence_length=12):
        """Create sliding window sequences for LSTM."""
        sequences = []
        for i in range(len(data) - sequence_length):
            sequences.append(data[i:i+sequence_length])
        return np.array(sequences)
    
    def build_lstm_model(self, sequence_length):
        """Build LSTM autoencoder model."""
        model = keras.Sequential([
            # Encoder
            layers.LSTM(32, activation='relu', input_shape=(sequence_length, 1), return_sequences=True),
            layers.LSTM(16, activation='relu', return_sequences=False),
            layers.RepeatVector(sequence_length),
            # Decoder
            layers.LSTM(16, activation='relu', return_sequences=True),
            layers.LSTM(32, activation='relu', return_sequences=True),
            layers.TimeDistributed(layers.Dense(1))
        ])
        model.compile(optimizer='adam', loss='mse')
        return model
    
    def detect_with_lstm(self, df, sequence_length=12):
        """Detect anomalies using LSTM autoencoder."""
        # Scale data
        amounts = df['amount'].values.reshape(-1, 1)
        amounts_scaled = self.scaler.fit_transform(amounts)
        
        # Create sequences
        sequences = self.create_sequences(amounts_scaled, sequence_length)
        
        if len(sequences) < 20:
            print(f"⚠️  Not enough data for LSTM training (need >20, have {len(sequences)}). Using statistical method.")
            return self.detect_with_statistics(df)
        
        # Build and train model
        self.model = self.build_lstm_model(sequence_length)
        
        # Train on first 80% of data (or all if limited data)
        train_size = max(int(len(sequences) * 0.8), len(sequences) - 50)
        X_train = sequences[:train_size]
        
        self.model.fit(X_train, X_train, epochs=50, batch_size=32, verbose=0)
        
        # Calculate reconstruction errors
        reconstructions = self.model.predict(sequences, verbose=0)
        reconstruction_errors = np.mean(np.abs(sequences - reconstructions), axis=(1, 2))
        
        # Set threshold at specified percentile
        self.threshold = np.percentile(reconstruction_errors, self.threshold_percentile)
        
        # Identify anomalies
        anomalies = []
        for i, error in enumerate(reconstruction_errors):
            if error > self.threshold:
                idx = i + sequence_length
                if idx < len(df):
                    month = df.loc[idx, 'month']
                    amount = df.loc[idx, 'amount']
                    
                    # Calculate deviation from median
                    median_amount = df['amount'].median()
                    deviation_pct = ((amount - median_amount) / median_amount) * 100
                    
                    anomalies.append({
                        'month': month,
                        'amount': amount,
                        'reconstruction_error': float(error),
                        'threshold': float(self.threshold),
                        'deviation_from_median_pct': round(deviation_pct, 2),
                        'detection_method': 'LSTM Autoencoder'
                    })
        
        return anomalies
    
    def detect_with_statistics(self, df):
        """Fallback detection using statistical methods (IQR + Z-score)."""
        amounts = df['amount'].values
        
        # Calculate statistics
        median = np.median(amounts)
        q1 = np.percentile(amounts, 25)
        q3 = np.percentile(amounts, 75)
        iqr = q3 - q1
        
        # IQR-based outlier detection (more aggressive)
        lower_bound = q1 - 3.0 * iqr
        upper_bound = q3 + 3.0 * iqr
        
        # Z-score based detection
        mean = np.mean(amounts)
        std = np.std(amounts)
        
        anomalies = []
        for idx, row in df.iterrows():
            amount = row['amount']
            month = row['month']
            
            # Check if outlier by IQR or extreme Z-score
            is_iqr_outlier = amount < lower_bound or amount > upper_bound
            z_score = abs((amount - mean) / std) if std > 0 else 0
            is_zscore_outlier = z_score > 3.5
            
            if is_iqr_outlier or is_zscore_outlier:
                deviation_pct = ((amount - median) / median) * 100
                
                anomalies.append({
                    'month': month,
                    'amount': amount,
                    'z_score': round(float(z_score), 2),
                    'iqr_lower_bound': round(lower_bound, 2),
                    'iqr_upper_bound': round(upper_bound, 2),
                    'deviation_from_median_pct': round(deviation_pct, 2),
                    'detection_method': 'Statistical (IQR + Z-score)'
                })
        
        return anomalies
    
    def detect_anomalies(self, monthly_inflow, use_lstm=True):
        """
        Detect anomalies in monthly inflow data.
        
        Args:
            monthly_inflow: Dict of month -> amount
            use_lstm: Whether to use LSTM (True) or statistical method (False)
            
        Returns:
            List of anomaly dicts
        """
        df = self.prepare_time_series(monthly_inflow)
        
        if len(df) < 12:
            print(f"⚠️  Insufficient data for time series analysis ({len(df)} months < 12). Skipping.")
            return []
        
        # Use LSTM if available and requested
        if use_lstm and TENSORFLOW_AVAILABLE:
            try:
                return self.detect_with_lstm(df)
            except Exception as e:
                print(f"⚠️  LSTM detection failed: {e}. Falling back to statistical method.")
                return self.detect_with_statistics(df)
        else:
            return self.detect_with_statistics(df)


def add_cashflow_anomalies_to_report(customer_id, analytics_dir='analytics'):
    """
    Add cashflow anomalies to existing anomaly report.
    
    Args:
        customer_id: Customer ID (e.g., 'CUST_MSM_00001')
        analytics_dir: Directory containing analytics files
    """
    # Load earnings data
    earnings_file = os.path.join(analytics_dir, f'{customer_id}_earnings_spendings.json')
    if not os.path.exists(earnings_file):
        print(f"❌ Earnings file not found: {earnings_file}")
        return
    
    with open(earnings_file, 'r') as f:
        earnings_data = json.load(f)
    
    monthly_inflow = earnings_data.get('cashflow_metrics', {}).get('monthly_inflow', {})
    if not monthly_inflow:
        print(f"⚠️  No monthly inflow data for {customer_id}")
        return
    
    # Detect anomalies
    detector = LSTMCashflowAnomalyDetector(threshold_percentile=99.0)
    cashflow_anomalies = detector.detect_anomalies(monthly_inflow, use_lstm=TENSORFLOW_AVAILABLE)
    
    if not cashflow_anomalies:
        print(f"✓ No cashflow anomalies detected for {customer_id}")
        return
    
    print(f"🔍 Found {len(cashflow_anomalies)} cashflow anomalies for {customer_id}")
    
    # Load existing anomaly report
    anomaly_file = os.path.join(analytics_dir, f'{customer_id}_anomalies_report.json')
    if os.path.exists(anomaly_file):
        with open(anomaly_file, 'r') as f:
            anomaly_report = json.load(f)
    else:
        anomaly_report = {
            'customer_id': customer_id,
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'anomalies': []
        }
    
    # Add cashflow anomalies section
    anomaly_report['monthly_cashflow_anomalies'] = {
        'total_anomalies': len(cashflow_anomalies),
        'detection_method': cashflow_anomalies[0]['detection_method'] if cashflow_anomalies else 'N/A',
        'anomalies': cashflow_anomalies
    }
    anomaly_report['generated_at'] = datetime.utcnow().isoformat() + 'Z'
    
    # Save updated report
    with open(anomaly_file, 'w') as f:
        json.dump(anomaly_report, f, indent=2)
    
    print(f"✅ Updated anomaly report: {anomaly_file}")
    
    # Print summary
    for anomaly in cashflow_anomalies[:5]:  # Show first 5
        print(f"   • {anomaly['month']}: ₹{anomaly['amount']:,.2f} "
              f"({anomaly['deviation_from_median_pct']:+.1f}% from median)")


def main():
    """Process all customers."""
    import glob
    
    analytics_dir = 'analytics'
    earnings_files = glob.glob(os.path.join(analytics_dir, '*_earnings_spendings.json'))
    
    print(f"📊 Processing cashflow anomaly detection for {len(earnings_files)} customers...")
    print(f"   Using: {'LSTM Autoencoder' if TENSORFLOW_AVAILABLE else 'Statistical Methods (IQR + Z-score)'}\n")
    
    for earnings_file in sorted(earnings_files):
        customer_id = os.path.basename(earnings_file).replace('_earnings_spendings.json', '')
        add_cashflow_anomalies_to_report(customer_id, analytics_dir)
    
    print(f"\n✅ Completed cashflow anomaly detection for all customers")


if __name__ == '__main__':
    main()
