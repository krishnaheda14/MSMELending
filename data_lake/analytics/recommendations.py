"""
Credit Product Recommendation Engine
Suggests loan products based on customer analytics and risk profile.
"""
import json
import os
from typing import Dict, List
from datetime import datetime


def recommend_credit_products(customer_id: str, analytics_dir: str = None) -> Dict:
    """
    Generate personalized credit product recommendations.
    
    Args:
        customer_id: Customer ID
        analytics_dir: Path to analytics directory
    
    Returns:
        Dictionary with recommended products and rationale
    """
    if analytics_dir is None:
        analytics_dir = os.path.dirname(__file__)
    
    print(f"\n[INFO] Generating credit recommendations for {customer_id}")
    
    # Load analytics data
    files = {
        'overall': f'{customer_id}_overall_summary.json',
        'earnings': f'{customer_id}_earnings_spendings.json',
        'gst': f'{customer_id}_gst_summary.json',
        'credit': f'{customer_id}_credit_summary.json',
    }
    
    data = {}
    for key, filename in files.items():
        filepath = os.path.join(analytics_dir, filename)
        try:
            with open(filepath, 'r') as f:
                data[key] = json.load(f)
        except FileNotFoundError:
            print(f"[WARN] File not found: {filename}")
            data[key] = {}
    
    # Extract key metrics
    overall = data.get('overall', {})
    earnings = data.get('earnings', {})
    gst = data.get('gst', {})
    credit = data.get('credit', {})
    
    risk_score = overall.get('scores', {}).get('overall_risk_score', 50)
    cashflow_stability = overall.get('scores', {}).get('cashflow_stability', 50)
    business_health = overall.get('scores', {}).get('business_health', 50)
    debt_capacity = overall.get('scores', {}).get('debt_capacity', 50)
    
    cashflow_metrics = earnings.get('cashflow_metrics', {})
    net_surplus = cashflow_metrics.get('net_surplus', 0)
    surplus_ratio = cashflow_metrics.get('surplus_ratio', 0)
    total_inflow = cashflow_metrics.get('total_inflow', 0)
    total_outflow = cashflow_metrics.get('total_outflow', 0)
    
    annual_turnover = gst.get('annual_turnover', 0)
    bureau_score = credit.get('bureau_score', 0)
    open_loans = credit.get('open_loans', 0)
    total_outstanding = credit.get('total_outstanding', 0)
    
    credit_behavior = earnings.get('credit_behavior', {})
    dti = credit_behavior.get('debt_to_income_ratio', 0)
    bounces = credit_behavior.get('bounces', 0)
    
    # Define credit products
    products = []
    
    # 1. Working Capital Loan
    if risk_score >= 60 and surplus_ratio > 15 and annual_turnover > 1000000:
        max_amount = min(annual_turnover * 0.25, net_surplus * 12)
        products.append({
            'product_name': 'Working Capital Loan',
            'product_type': 'Term Loan',
            'recommended_amount': round(max_amount, 2),
            'tenure_months': 12,
            'estimated_interest_rate': 12.5 if risk_score >= 70 else 14.5,
            'eligibility': 'Approved',
            'rationale': f'Strong surplus ratio ({surplus_ratio:.1f}%) and healthy turnover (₹{annual_turnover:,.0f})',
            'conditions': ['Monthly EMI: ₹{:.2f}'.format(max_amount * 0.09), 'Collateral: Not required', 'Processing time: 7-10 days']
        })
    
    # 2. Invoice Discounting
    if annual_turnover > 2000000 and cashflow_stability > 60:
        max_amount = annual_turnover * 0.15
        products.append({
            'product_name': 'Invoice Discounting',
            'product_type': 'Short-term Credit',
            'recommended_amount': round(max_amount, 2),
            'tenure_months': 3,
            'estimated_interest_rate': 10.0,
            'eligibility': 'Approved',
            'rationale': f'High GST turnover (₹{annual_turnover:,.0f}) with stable cashflow (score: {cashflow_stability:.1f})',
            'conditions': ['GST invoices required', 'Advance rate: 80%', 'Processing time: 2-3 days']
        })
    
    # 3. Business Expansion Loan
    if risk_score >= 70 and business_health > 60 and dti < 40:
        max_amount = min(annual_turnover * 0.4, 5000000)
        products.append({
            'product_name': 'Business Expansion Loan',
            'product_type': 'Term Loan',
            'recommended_amount': round(max_amount, 2),
            'tenure_months': 24,
            'estimated_interest_rate': 11.0 if bureau_score > 750 else 13.0,
            'eligibility': 'Approved',
            'rationale': f'Excellent business health ({business_health:.1f}) and low DTI ({dti:.1f}%)',
            'conditions': ['Business plan required', 'Collateral may be required', 'Processing time: 15-20 days']
        })
    
    # 4. Overdraft Facility
    if risk_score >= 65 and bounces < 3:
        max_amount = total_inflow * 0.1
        products.append({
            'product_name': 'Overdraft Facility',
            'product_type': 'Revolving Credit',
            'recommended_amount': round(max_amount, 2),
            'tenure_months': 12,
            'estimated_interest_rate': 15.0,
            'eligibility': 'Approved',
            'rationale': f'Clean repayment history (bounces: {bounces}) and consistent inflows',
            'conditions': ['Draw as needed', 'Interest on utilized amount only', 'Monthly review']
        })
    
    # 5. Equipment Financing
    if risk_score >= 55 and net_surplus > 0:
        max_amount = min(annual_turnover * 0.3, 3000000)
        products.append({
            'product_name': 'Equipment Financing',
            'product_type': 'Asset-backed Loan',
            'recommended_amount': round(max_amount, 2),
            'tenure_months': 36,
            'estimated_interest_rate': 12.0,
            'eligibility': 'Under Review',
            'rationale': f'Positive surplus (₹{net_surplus:,.0f}) suitable for asset acquisition',
            'conditions': ['Equipment as collateral', 'Down payment: 15-20%', 'Processing time: 10-12 days']
        })
    
    # 6. MSME Emergency Credit
    if risk_score >= 50 and open_loans < 3:
        max_amount = min(500000, total_outflow * 0.5)
        products.append({
            'product_name': 'MSME Emergency Credit',
            'product_type': 'Short-term Loan',
            'recommended_amount': round(max_amount, 2),
            'tenure_months': 6,
            'estimated_interest_rate': 16.0,
            'eligibility': 'Approved',
            'rationale': 'Quick disbursal for urgent working capital needs',
            'conditions': ['Minimal documentation', 'Processing time: 24-48 hours', 'Higher interest for speed']
        })
    
    # Sort by recommended amount (descending)
    products.sort(key=lambda x: x['recommended_amount'], reverse=True)
    
    # Risk-based guardrails
    guardrails = []
    if risk_score < 60:
        guardrails.append('Consider requiring collateral for loans > ₹1,000,000')
    if dti > 50:
        guardrails.append('High debt-to-income ratio: Monitor repayment capacity closely')
    if bounces > 5:
        guardrails.append('⚠️ Frequent bounces detected: Recommend co-borrower or guarantor')
    if surplus_ratio < 10:
        guardrails.append('Low surplus ratio: Limit exposure to short-term products')
    
    # Overall recommendation
    if risk_score >= 75:
        overall_recommendation = 'STRONGLY APPROVE'
        recommendation_note = 'Excellent credit profile with strong fundamentals. Pre-approved for multiple products.'
    elif risk_score >= 60:
        overall_recommendation = 'APPROVE'
        recommendation_note = 'Good credit profile. Approved for standard terms with minimal conditions.'
    elif risk_score >= 45:
        overall_recommendation = 'CONDITIONAL APPROVAL'
        recommendation_note = 'Moderate risk profile. Approve with additional security or co-borrower.'
    else:
        overall_recommendation = 'REFER TO UNDERWRITER'
        recommendation_note = 'High risk profile. Requires detailed underwriting review.'
    
    result = {
        'customer_id': customer_id,
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'overall_recommendation': overall_recommendation,
        'recommendation_note': recommendation_note,
        'customer_summary': {
            'risk_score': round(risk_score, 2),
            'annual_turnover': round(annual_turnover, 2),
            'net_surplus': round(net_surplus, 2),
            'debt_to_income': round(dti, 2),
            'bureau_score': bureau_score,
            'open_loans': open_loans
        },
        'recommended_products': products,
        'risk_guardrails': guardrails,
        'next_steps': [
            'Customer can apply online or visit branch',
            'Submit required documents within 7 days',
            'Loan approval subject to final underwriting',
            'Disbursement within processing time mentioned'
        ]
    }
    
    # Save result
    output_file = os.path.join(analytics_dir, f'{customer_id}_recommendations.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"[✓] Recommendations saved to {output_file}")
    print(f"\n{'='*60}")
    print(f"CREDIT PRODUCT RECOMMENDATIONS")
    print(f"{'='*60}")
    print(f"Overall: {overall_recommendation}")
    print(f"Risk Score: {risk_score:.2f}/100")
    print(f"Products Recommended: {len(products)}")
    print(f"\nTop 3 Products:")
    for i, product in enumerate(products[:3], 1):
        print(f"  {i}. {product['product_name']} - ₹{product['recommended_amount']:,.2f} @ {product['estimated_interest_rate']}% for {product['tenure_months']} months")
    
    if guardrails:
        print(f"\n⚠️  Risk Guardrails:")
        for guardrail in guardrails:
            print(f"  • {guardrail}")
    
    print(f"{'='*60}\n")
    
    return result


if __name__ == '__main__':
    import sys
    
    customer_id = sys.argv[1] if len(sys.argv) > 1 else 'CUST_MSM_00001'
    analytics_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(__file__)
    
    recommend_credit_products(customer_id, analytics_dir)
