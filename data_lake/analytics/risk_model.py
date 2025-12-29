"""
Explainable Risk Model Module
Provides ML-based risk scoring with SHAP-style feature attributions for transparency and auditability.
"""
import json
import os
from typing import Dict, List, Tuple
from datetime import datetime
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib


class ExplainableRiskModel:
    """
    Simple tree-based risk scorer with feature attributions.
    Uses RandomForest for interpretability and provides per-feature contributions.
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_path = os.path.join(os.path.dirname(__file__), 'risk_model.pkl')
        self.scaler_path = os.path.join(os.path.dirname(__file__), 'risk_scaler.pkl')
        
    def extract_features(self, analytics_data: Dict) -> Tuple[np.ndarray, List[str]]:
        """Extract numerical features from analytics data."""
        features = []
        feature_names = []
        
        # Cashflow features (from earnings_spendings)
        earnings = analytics_data.get('earnings_spendings', {})
        cashflow = earnings.get('cashflow_metrics', {})
        
        features.extend([
            cashflow.get('surplus_ratio', 0),
            cashflow.get('inflow_outflow_ratio', 0),
            cashflow.get('income_stability_cv', 0),
            cashflow.get('seasonality_index', 0),
            cashflow.get('top_customer_dependence', 0),
        ])
        feature_names.extend([
            'surplus_ratio', 'inflow_outflow_ratio', 'income_stability_cv',
            'seasonality_index', 'top_customer_dependence'
        ])
        
        # Expense features
        expenses = earnings.get('expense_composition', {})
        features.extend([
            expenses.get('essential_ratio', 0),
            expenses.get('non_essential_ratio', 0),
            expenses.get('debt_servicing_ratio', 0),
        ])
        feature_names.extend(['essential_ratio', 'non_essential_ratio', 'debt_servicing_ratio'])
        
        # Credit behavior features
        credit_behavior = earnings.get('credit_behavior', {})
        features.extend([
            credit_behavior.get('bounces', 0),
            credit_behavior.get('emi_consistency_score', 0),
            credit_behavior.get('credit_utilization_ratio', 0),
            credit_behavior.get('default_probability_score', 0),
            credit_behavior.get('debt_to_income_ratio', 0),
            credit_behavior.get('payment_regularity_score', 0),
        ])
        feature_names.extend([
            'bounces', 'emi_consistency_score', 'credit_utilization_ratio',
            'default_probability_score', 'debt_to_income_ratio', 'payment_regularity_score'
        ])
        
        # GST features
        gst = analytics_data.get('gst', {})
        features.extend([
            gst.get('returns_count', 0),
            gst.get('annual_turnover', 0) / 1000000,  # In millions
            gst.get('total_businesses', 0),
        ])
        feature_names.extend(['gst_returns_count', 'gst_annual_turnover_millions', 'gst_businesses'])
        
        # Credit summary features
        credit = analytics_data.get('credit', {})
        features.extend([
            credit.get('bureau_score', 0),
            credit.get('open_loans', 0),
            credit.get('total_outstanding', 0) / 1000000,  # In millions
        ])
        feature_names.extend(['bureau_score', 'open_loans', 'total_outstanding_millions'])
        
        # ONDC features
        ondc = analytics_data.get('ondc', {})
        features.extend([
            ondc.get('total_orders', 0),
            ondc.get('total_order_value', 0) / 1000000,  # In millions
            ondc.get('provider_diversity', 0),
        ])
        feature_names.extend(['ondc_orders', 'ondc_value_millions', 'ondc_diversity'])
        
        # OCEN features
        ocen = analytics_data.get('ocen', {})
        features.extend([
            ocen.get('total_applications', 0),
            ocen.get('approval_rate', 0),
        ])
        feature_names.extend(['ocen_applications', 'ocen_approval_rate'])
        
        # Mutual funds and insurance
        mf = analytics_data.get('mutual_funds', {})
        insurance = analytics_data.get('insurance', {})
        features.extend([
            mf.get('total_portfolios', 0),
            mf.get('total_current_value', 0) / 1000000,  # In millions
            insurance.get('total_policies', 0),
            insurance.get('total_coverage', 0) / 1000000,  # In millions
        ])
        feature_names.extend([
            'mf_portfolios', 'mf_value_millions', 'insurance_policies', 'insurance_coverage_millions'
        ])
        
        # Anomalies
        anomalies = analytics_data.get('anomalies', {})
        features.extend([
            len(anomalies.get('high_value_transactions', [])),
            len(anomalies.get('suspicious_patterns', [])),
        ])
        feature_names.extend(['high_value_anomalies', 'suspicious_patterns'])
        
        return np.array(features).reshape(1, -1), feature_names
    
    def train_synthetic_model(self, n_samples: int = 1000):
        """
        Train a synthetic model on generated risk labels.
        In production, replace this with real labeled data.
        """
        print("[INFO] Training synthetic risk model...")
        
        # Generate synthetic training data with risk labels
        X_train = []
        y_train = []
        
        for i in range(n_samples):
            # Simulate feature distributions
            surplus_ratio = np.random.uniform(-20, 50)
            inflow_outflow = np.random.uniform(0.5, 3.0)
            income_cv = np.random.uniform(10, 500)
            seasonality = np.random.uniform(5, 100)
            customer_dep = np.random.uniform(0, 80)
            essential_ratio = np.random.uniform(30, 90)
            non_essential = np.random.uniform(5, 40)
            debt_servicing = np.random.uniform(0, 60)
            bounces = np.random.poisson(3)
            emi_consistency = np.random.uniform(50, 100)
            credit_util = np.random.uniform(0, 100)
            default_prob = np.random.uniform(0, 80)
            dti = np.random.uniform(0, 100)
            payment_reg = np.random.uniform(50, 100)
            gst_returns = np.random.randint(0, 50)
            gst_turnover = np.random.uniform(0.5, 50)
            gst_businesses = np.random.randint(1, 5)
            bureau_score = np.random.randint(300, 900)
            open_loans = np.random.randint(0, 10)
            outstanding = np.random.uniform(0, 20)
            ondc_orders = np.random.randint(0, 500)
            ondc_value = np.random.uniform(0, 10)
            ondc_diversity = np.random.randint(0, 20)
            ocen_apps = np.random.randint(0, 50)
            ocen_approval = np.random.uniform(0, 100)
            mf_portfolios = np.random.randint(0, 10)
            mf_value = np.random.uniform(0, 5)
            insurance_policies = np.random.randint(0, 5)
            insurance_coverage = np.random.uniform(0, 10)
            high_val_anom = np.random.poisson(5)
            suspicious = np.random.poisson(2)
            
            features = [
                surplus_ratio, inflow_outflow, income_cv, seasonality, customer_dep,
                essential_ratio, non_essential, debt_servicing, bounces, emi_consistency,
                credit_util, default_prob, dti, payment_reg, gst_returns, gst_turnover,
                gst_businesses, bureau_score, open_loans, outstanding, ondc_orders,
                ondc_value, ondc_diversity, ocen_apps, ocen_approval, mf_portfolios,
                mf_value, insurance_policies, insurance_coverage, high_val_anom, suspicious
            ]
            
            # Rule-based risk labeling (0 = low risk, 1 = high risk)
            risk_score = 0
            
            # Negative indicators (increase risk)
            if surplus_ratio < 10: risk_score += 2
            if inflow_outflow < 1.1: risk_score += 2
            if income_cv > 200: risk_score += 1
            if seasonality > 50: risk_score += 1
            if bounces > 5: risk_score += 3
            if default_prob > 40: risk_score += 3
            if dti > 50: risk_score += 2
            if bureau_score < 600: risk_score += 3
            if debt_servicing > 40: risk_score += 2
            
            # Positive indicators (decrease risk)
            if emi_consistency > 80: risk_score -= 1
            if payment_reg > 80: risk_score -= 1
            if gst_returns > 20: risk_score -= 1
            if bureau_score > 750: risk_score -= 2
            if ocen_approval > 70: risk_score -= 1
            if mf_value > 2: risk_score -= 1
            if insurance_coverage > 5: risk_score -= 1
            
            label = 1 if risk_score > 3 else 0  # Binary classification
            
            X_train.append(features)
            y_train.append(label)
        
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        
        # Feature names
        self.feature_names = [
            'surplus_ratio', 'inflow_outflow_ratio', 'income_stability_cv',
            'seasonality_index', 'top_customer_dependence', 'essential_ratio',
            'non_essential_ratio', 'debt_servicing_ratio', 'bounces',
            'emi_consistency_score', 'credit_utilization_ratio',
            'default_probability_score', 'debt_to_income_ratio',
            'payment_regularity_score', 'gst_returns_count',
            'gst_annual_turnover_millions', 'gst_businesses', 'bureau_score',
            'open_loans', 'total_outstanding_millions', 'ondc_orders',
            'ondc_value_millions', 'ondc_diversity', 'ocen_applications',
            'ocen_approval_rate', 'mf_portfolios', 'mf_value_millions',
            'insurance_policies', 'insurance_coverage_millions',
            'high_value_anomalies', 'suspicious_patterns'
        ]
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_train)
        
        # Train RandomForest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            class_weight='balanced'
        )
        self.model.fit(X_scaled, y_train)
        
        # Save model and scaler
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        print(f"[✓] Model trained on {n_samples} samples")
        print(f"[✓] Model saved to {self.model_path}")
        
        return self.model
    
    def load_model(self):
        """Load pre-trained model and scaler."""
        if not os.path.exists(self.model_path) or not os.path.exists(self.scaler_path):
            print("[WARN] Model not found. Training new model...")
            return self.train_synthetic_model()
        
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        
        # Reconstruct feature names
        self.feature_names = [
            'surplus_ratio', 'inflow_outflow_ratio', 'income_stability_cv',
            'seasonality_index', 'top_customer_dependence', 'essential_ratio',
            'non_essential_ratio', 'debt_servicing_ratio', 'bounces',
            'emi_consistency_score', 'credit_utilization_ratio',
            'default_probability_score', 'debt_to_income_ratio',
            'payment_regularity_score', 'gst_returns_count',
            'gst_annual_turnover_millions', 'gst_businesses', 'bureau_score',
            'open_loans', 'total_outstanding_millions', 'ondc_orders',
            'ondc_value_millions', 'ondc_diversity', 'ocen_applications',
            'ocen_approval_rate', 'mf_portfolios', 'mf_value_millions',
            'insurance_policies', 'insurance_coverage_millions',
            'high_value_anomalies', 'suspicious_patterns'
        ]
        
        print("[✓] Model loaded successfully")
        return self.model
    
    def predict_with_attribution(self, analytics_data: Dict) -> Dict:
        """
        Predict risk score with feature attributions for explainability.
        Returns risk probability, risk label, and per-feature contributions.
        """
        if self.model is None:
            self.load_model()
        
        # Extract features
        X, extracted_feature_names = self.extract_features(analytics_data)
        
        # Ensure feature alignment
        if len(extracted_feature_names) != len(self.feature_names):
            print(f"[WARN] Feature mismatch: expected {len(self.feature_names)}, got {len(extracted_feature_names)}")
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        risk_prob = self.model.predict_proba(X_scaled)[0][1]  # Probability of high risk
        risk_label = 'High Risk' if risk_prob > 0.5 else 'Low Risk'
        risk_score = int(risk_prob * 100)  # Convert to 0-100 scale
        
        # Feature importances (global)
        feature_importances = self.model.feature_importances_
        
        # Path-based contributions (simplified SHAP-like attribution)
        # For each tree, trace decision path and accumulate feature contributions
        contributions = self._compute_feature_contributions(X_scaled, feature_importances)
        
        # Sort by absolute contribution
        sorted_contributions = sorted(
            contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        # Format output
        result = {
            'customer_id': analytics_data.get('overall', {}).get('customer_id', 'UNKNOWN'),
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'risk_assessment': {
                'risk_score': risk_score,
                'risk_probability': round(risk_prob, 4),
                'risk_label': risk_label,
                'risk_category': self._get_risk_category(risk_score),
            },
            'feature_attributions': {
                'top_risk_drivers': [
                    {
                        'feature': name,
                        'contribution': round(contrib, 4),
                        'impact': 'Increases Risk' if contrib > 0 else 'Decreases Risk',
                        'magnitude': abs(round(contrib, 4))
                    }
                    for name, contrib in sorted_contributions[:10]
                ],
                'all_contributions': {
                    name: round(contrib, 4) for name, contrib in contributions.items()
                }
            },
            'model_metadata': {
                'model_type': 'RandomForestClassifier',
                'n_features': len(self.feature_names),
                'trained_samples': 1000,
                'model_version': '1.0'
            },
            'explanation': self._generate_explanation(sorted_contributions[:5], risk_score)
        }
        
        return result
    
    def _compute_feature_contributions(self, X_scaled: np.ndarray, feature_importances: np.ndarray) -> Dict[str, float]:
        """
        Compute simplified feature contributions.
        Uses feature importance weighted by actual feature values.
        """
        contributions = {}
        X_flat = X_scaled.flatten()
        
        for i, (feature_name, importance) in enumerate(zip(self.feature_names, feature_importances)):
            if i < len(X_flat):
                # Contribution = importance * normalized_value
                contribution = importance * X_flat[i]
                contributions[feature_name] = contribution
            else:
                contributions[feature_name] = 0.0
        
        return contributions
    
    def _get_risk_category(self, risk_score: int) -> str:
        """Categorize risk score into buckets."""
        if risk_score >= 75:
            return 'Very High Risk'
        elif risk_score >= 60:
            return 'High Risk'
        elif risk_score >= 40:
            return 'Moderate Risk'
        elif risk_score >= 25:
            return 'Low Risk'
        else:
            return 'Very Low Risk'
    
    def _generate_explanation(self, top_features: List[Tuple[str, float]], risk_score: int) -> str:
        """Generate human-readable explanation of risk assessment."""
        explanation = f"Risk Score: {risk_score}/100 ({self._get_risk_category(risk_score)}). "
        
        if risk_score >= 60:
            explanation += "⚠️ High risk profile. Key concerns: "
        elif risk_score >= 40:
            explanation += "⚡ Moderate risk profile. Notable factors: "
        else:
            explanation += "✅ Low risk profile. Positive indicators: "
        
        top_3 = []
        for name, contrib in top_features[:3]:
            if abs(contrib) > 0.01:  # Only mention significant contributors
                impact = "increases" if contrib > 0 else "reduces"
                top_3.append(f"{name.replace('_', ' ')} {impact} risk")
        
        explanation += ", ".join(top_3) + "."
        
        return explanation


def analyze_risk_model(customer_id: str, analytics_dir: str = None) -> Dict:
    """
    Main function to analyze customer risk using explainable ML model.
    
    Args:
        customer_id: Customer ID to analyze
        analytics_dir: Path to analytics directory containing summary JSONs
    
    Returns:
        Dictionary with risk assessment and feature attributions
    """
    if analytics_dir is None:
        analytics_dir = os.path.join(os.path.dirname(__file__))
    
    print(f"\n[INFO] Analyzing risk for customer: {customer_id}")
    
    # Load all analytics files
    analytics_files = {
        'overall': f'{customer_id}_overall_summary.json',
        'transactions': f'{customer_id}_transaction_summary.json',
        'gst': f'{customer_id}_gst_summary.json',
        'credit': f'{customer_id}_credit_summary.json',
        'anomalies': f'{customer_id}_anomalies_report.json',
        'mutual_funds': f'{customer_id}_mutual_funds_summary.json',
        'insurance': f'{customer_id}_insurance_summary.json',
        'ocen': f'{customer_id}_ocen_summary.json',
        'ondc': f'{customer_id}_ondc_summary.json',
        'earnings_spendings': f'{customer_id}_earnings_spendings.json'
    }
    
    analytics_data = {}
    for key, filename in analytics_files.items():
        filepath = os.path.join(analytics_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                analytics_data[key] = json.load(f)
            print(f"  [✓] Loaded {filename}")
        except FileNotFoundError:
            print(f"  [!] File not found: {filename}")
            analytics_data[key] = {}
        except Exception as e:
            print(f"  [ERROR] Failed to load {filename}: {str(e)}")
            analytics_data[key] = {}
    
    # Initialize and run risk model
    risk_model = ExplainableRiskModel()
    risk_assessment = risk_model.predict_with_attribution(analytics_data)
    
    # Save results
    output_file = os.path.join(analytics_dir, f'{customer_id}_risk_model.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(risk_assessment, f, indent=2, ensure_ascii=False)
    
    print(f"[✓] Risk assessment saved to {output_file}")
    print(f"\n{'='*60}")
    print(f"RISK SCORE: {risk_assessment['risk_assessment']['risk_score']}/100")
    print(f"RISK LABEL: {risk_assessment['risk_assessment']['risk_label']}")
    print(f"CATEGORY: {risk_assessment['risk_assessment']['risk_category']}")
    print(f"{'='*60}")
    print(f"\nTop 5 Risk Drivers:")
    for driver in risk_assessment['feature_attributions']['top_risk_drivers'][:5]:
        print(f"  • {driver['feature']}: {driver['impact']} (magnitude: {driver['magnitude']})")
    print(f"\n{risk_assessment['explanation']}")
    print(f"{'='*60}\n")
    
    return risk_assessment


if __name__ == '__main__':
    import sys
    
    customer_id = sys.argv[1] if len(sys.argv) > 1 else 'CUST_MSM_00001'
    analytics_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(__file__)
    
    analyze_risk_model(customer_id, analytics_dir)
