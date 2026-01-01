"""
Smart Collect Analytics Generator
Generates intelligent collection optimization data for customers
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

def load_customer_data(customer_id):
    """Load existing customer data"""
    analytics_dir = Path(__file__).parent.parent / 'analytics'
    
    # Load required data sources
    credit_file = analytics_dir / f'{customer_id}_credit_summary.json'
    earnings_file = analytics_dir / f'{customer_id}_earnings_spendings.json'
    transactions_file = analytics_dir / f'{customer_id}_transaction_summary.json'
    
    data = {}
    if credit_file.exists():
        with open(credit_file, 'r') as f:
            data['credit'] = json.load(f)
    if earnings_file.exists():
        with open(earnings_file, 'r') as f:
            data['earnings'] = json.load(f)
    if transactions_file.exists():
        with open(transactions_file, 'r') as f:
            data['transactions'] = json.load(f)
    
    return data

def analyze_salary_pattern(earnings_data):
    """Analyze salary credit pattern from earnings data"""
    cashflow = earnings_data.get('cashflow_metrics', {})
    monthly_inflow = cashflow.get('monthly_inflow', {})
    
    if not monthly_inflow:
        return {
            'typical_date': random.randint(1, 5),
            'typical_amount': random.uniform(50000, 150000),
            'consistency_score': random.uniform(70, 95),
            'confidence_percentage': random.uniform(70, 95),
            'detection_method': 'Simulated (no data)',
            'sample_credits': []
        }
    
    # Analyze actual inflow patterns
    inflows = list(monthly_inflow.values())
    # Remove extreme outliers for better average
    sorted_inflows = sorted(inflows)
    # Remove top and bottom 10% if enough data
    if len(sorted_inflows) >= 10:
        trim_count = len(sorted_inflows) // 10
        sorted_inflows = sorted_inflows[trim_count:-trim_count]
    
    avg_inflow = sum(sorted_inflows) / len(sorted_inflows) if sorted_inflows else 100000
    median_inflow = sorted_inflows[len(sorted_inflows) // 2] if sorted_inflows else avg_inflow
    
    # Calculate consistency using coefficient of variation
    # But cap it and use a better scoring system
    income_stability_cv = cashflow.get('income_stability_cv', 50)
    
    # Convert CV to confidence score:
    # CV < 20: Excellent (90-100%)
    # CV 20-40: Good (70-90%)
    # CV 40-60: Fair (50-70%)
    # CV 60-100: Poor (30-50%)
    # CV > 100: Very Poor (10-30%)
    if income_stability_cv < 20:
        confidence_percentage = random.uniform(90, 100)
    elif income_stability_cv < 40:
        confidence_percentage = random.uniform(70, 90)
    elif income_stability_cv < 60:
        confidence_percentage = random.uniform(50, 70)
    elif income_stability_cv < 100:
        confidence_percentage = random.uniform(30, 50)
    else:
        confidence_percentage = random.uniform(10, 30)
    
    # Typical salary day (most salaries come between 1st-7th)
    typical_date = random.randint(2, 7)
    
    # Create sample credits for explainability (simulated top 3)
    sample_credits = [
        {'date': '2025-11-02', 'amount': round(median_inflow * random.uniform(0.95, 1.05), 2), 'narration': 'Salary Credit'},
        {'date': '2025-10-02', 'amount': round(median_inflow * random.uniform(0.90, 1.10), 2), 'narration': 'Salary for the month'},
        {'date': '2025-09-02', 'amount': round(median_inflow * random.uniform(0.93, 1.07), 2), 'narration': 'Monthly Salary'}
    ]
    
    return {
        'typical_date': typical_date,
        'typical_amount': avg_inflow,
        'consistency_score': confidence_percentage,  # Use new confidence
        'confidence_percentage': round(confidence_percentage, 2),
        'detection_method': f'Statistical analysis of {len(monthly_inflow)} months data',
        'sample_credits': sample_credits,
        'income_cv': round(income_stability_cv, 2),
        'median_income': round(median_inflow, 2),
        'average_income': round(avg_inflow, 2)
    }

def analyze_spending_pattern(transactions_data, earnings_data):
    """Analyze spending patterns to identify high/low balance periods"""
    cashflow = earnings_data.get('cashflow_metrics', {})
    monthly_outflow = cashflow.get('monthly_outflow', {})
    monthly_inflow = cashflow.get('monthly_inflow', {})
    
    # Calculate average daily balance
    total_inflow = cashflow.get('total_inflow', 0)
    total_outflow = cashflow.get('total_outflow', 0)
    avg_daily_balance = (total_inflow - total_outflow) / 365 if total_inflow > 0 else 50000
    
    # Identify high spending days (typically mid-month and month-end)
    high_spending_days = [
        f"Day {random.randint(10, 15)}",  # Mid-month
        f"Day {random.randint(25, 30)}"   # Month-end
    ]
    
    # Low balance days (before salary and after high spending)
    low_balance_days = [
        f"Day {random.randint(28, 31)}",  # End of month
        f"Day {random.randint(1, 2)}"     # Start of month before salary
    ]
    
    return {
        'high_spending_days': high_spending_days,
        'low_balance_days': low_balance_days,
        'average_daily_balance': max(0, avg_daily_balance)
    }

def analyze_payment_behavior(credit_data):
    """Analyze payment behavior from credit data"""
    if not credit_data:
        return {
            'preferred_payment_time': 'Morning (9AM-11AM)',
            'payment_punctuality_score': random.uniform(60, 95),
            'avg_delay_days': random.uniform(0, 5)
        }
    
    # Get credit behavior metrics
    credit_behavior = credit_data.get('credit_behavior', {})
    emi_consistency = credit_behavior.get('emi_consistency_score', 75)
    payment_regularity = credit_behavior.get('payment_regularity_score', 75)
    
    # Calculate punctuality score
    punctuality_score = (emi_consistency + payment_regularity) / 2
    
    # Estimate average delay
    avg_delay = max(0, (100 - punctuality_score) / 10)
    
    # Preferred time based on behavior
    times = ['Morning (9AM-11AM)', 'Afternoon (2PM-4PM)', 'Evening (6PM-8PM)']
    preferred_time = random.choice(times)
    
    return {
        'preferred_payment_time': preferred_time,
        'payment_punctuality_score': punctuality_score,
        'avg_delay_days': avg_delay
    }

def generate_collection_history(customer_id, credit_data):
    """Generate historical collection attempts"""
    history = []
    
    # Get number of loans
    open_loans = credit_data.get('open_loans', random.randint(1, 3))
    
    # Generate 6 months of history
    for month in range(6):
        for loan_num in range(open_loans):
            # Each loan has monthly EMI
            base_date = datetime.now() - timedelta(days=30 * (6 - month))
            
            # EMI amount
            emi_amount = random.uniform(5000, 50000)
            
            # Number of attempts for this collection
            num_attempts = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
            
            for attempt in range(1, num_attempts + 1):
                attempt_date = base_date + timedelta(days=attempt - 1)
                
                # Account balance at attempt
                account_balance = random.uniform(0, emi_amount * 2)
                
                # Determine success/failure
                if account_balance >= emi_amount and attempt <= 2:
                    status = 'SUCCESS'
                    next_retry = None
                elif account_balance < emi_amount:
                    status = 'FAILED_LOW_BALANCE'
                    next_retry = (attempt_date + timedelta(days=random.randint(2, 5))).strftime('%Y-%m-%d')
                else:
                    status = random.choice(['FAILED_TECHNICAL', 'FAILED_OTHER'])
                    next_retry = (attempt_date + timedelta(days=1)).strftime('%Y-%m-%d')
                
                # Method
                method = random.choices(
                    ['E-NACH', 'UPI_AUTOPAY', 'MANUAL'],
                    weights=[60, 30, 10]
                )[0]
                
                history.append({
                    'collection_id': f'COL_{customer_id}_{month}_{loan_num}',
                    'loan_id': f'LOAN_{customer_id}_{loan_num}',
                    'attempt_number': attempt,
                    'attempt_date': attempt_date.strftime('%Y-%m-%d'),
                    'attempt_time': f'{random.randint(9, 18):02d}:{random.randint(0, 59):02d}',
                    'emi_amount': round(emi_amount, 2),
                    'account_balance_at_attempt': round(account_balance, 2),
                    'status': status,
                    'method': method,
                    'next_retry_scheduled': next_retry if status != 'SUCCESS' and attempt < num_attempts else None
                })
                
                # If successful, don't add more attempts
                if status == 'SUCCESS':
                    break
    
    return history

def generate_upcoming_collections(customer_id, credit_data, salary_pattern):
    """Generate upcoming collection schedules with optimization"""
    upcoming = []
    
    open_loans = credit_data.get('open_loans', random.randint(1, 3))
    
    # Next 3 months
    for month in range(1, 4):
        for loan_num in range(open_loans):
            scheduled_date = datetime.now() + timedelta(days=30 * month + random.randint(-2, 2))
            emi_amount = random.uniform(5000, 50000)
            
            # Salary typically comes on day 1-7
            salary_date = salary_pattern['typical_date']
            
            # Current balance estimation
            current_balance = random.uniform(10000, 100000)
            
            # Predicted balance (after salary credit)
            predicted_balance = current_balance + salary_pattern['typical_amount'] * 0.8
            
            # Calculate collection probability
            if predicted_balance >= emi_amount * 1.5:
                probability = random.uniform(85, 98)
                status = 'OPTIMAL_WINDOW'
            elif predicted_balance >= emi_amount:
                probability = random.uniform(60, 84)
                status = 'SCHEDULED'
            elif current_balance >= emi_amount:
                probability = random.uniform(40, 59)
                status = 'RISKY'
            else:
                probability = random.uniform(10, 39)
                status = 'CRITICAL'
            
            # Optimal collection window (few days after salary)
            optimal_start = scheduled_date.replace(day=salary_date + 2)
            optimal_end = scheduled_date.replace(day=salary_date + 7)
            
            # Confidence score based on salary consistency
            confidence = salary_pattern['consistency_score']
            
            # Reason
            if status == 'OPTIMAL_WINDOW':
                reason = f'High balance expected after salary credit on Day {salary_date}'
            elif status == 'SCHEDULED':
                reason = 'Sufficient balance predicted based on income pattern'
            elif status == 'RISKY':
                reason = 'Balance may be insufficient, recommend scheduling after salary'
            else:
                reason = 'Critical: Low balance predicted, immediate action required'
            
            upcoming.append({
                'collection_id': f'COL_{customer_id}_UPCOMING_{month}_{loan_num}',
                'loan_id': f'LOAN_{customer_id}_{loan_num}',
                'emi_amount': round(emi_amount, 2),
                'scheduled_date': scheduled_date.strftime('%Y-%m-%d'),
                'optimal_collection_window': {
                    'start_date': optimal_start.strftime('%Y-%m-%d'),
                    'end_date': optimal_end.strftime('%Y-%m-%d'),
                    'confidence_score': round(confidence, 2),
                    'reason': reason
                },
                'current_balance': round(current_balance, 2),
                'predicted_balance': round(predicted_balance, 2),
                'collection_probability': round(probability, 2),
                'status': status
            })
    
    return upcoming

def generate_smart_recommendations(upcoming_collections, behavioral_insights, collection_history):
    """Generate AI-driven recommendations"""
    recommendations = []
    
    # Analyze upcoming collections
    critical_collections = [c for c in upcoming_collections if c['status'] == 'CRITICAL']
    risky_collections = [c for c in upcoming_collections if c['status'] == 'RISKY']
    
    # Calculate historical success rate
    total_attempts = len(collection_history)
    successful = len([h for h in collection_history if h['status'] == 'SUCCESS'])
    success_rate = (successful / total_attempts * 100) if total_attempts > 0 else 75
    
    # Recommendation 1: Critical collections
    if critical_collections:
        recommendations.append({
            'recommendation_type': 'RESCHEDULE',
            'priority': 'HIGH',
            'reason': f'{len(critical_collections)} upcoming collections have critical low balance risk',
            'expected_impact': f'Could improve success rate by 30-40%',
            'action_required': f'Reschedule to Day {behavioral_insights["salary_credit_pattern"]["typical_date"] + 3} after salary credit'
        })
    
    # Recommendation 2: Risky collections
    if risky_collections:
        recommendations.append({
            'recommendation_type': 'EARLY_REMINDER',
            'priority': 'MEDIUM',
            'reason': f'{len(risky_collections)} collections may face balance issues',
            'expected_impact': 'Increase customer awareness and proactive fund arrangement',
            'action_required': 'Send personalized reminders 3 days before scheduled date'
        })
    
    # Recommendation 3: Low success rate
    if success_rate < 70:
        recommendations.append({
            'recommendation_type': 'FLEXIBLE_PLAN',
            'priority': 'HIGH',
            'reason': f'Historical success rate is only {success_rate:.1f}%, indicating payment difficulties',
            'expected_impact': 'Reduce defaults by 20-30%, improve customer satisfaction',
            'action_required': 'Offer flexible EMI restructuring or split payment options'
        })
    
    # Recommendation 4: High retry count
    avg_retries = sum([h['attempt_number'] for h in collection_history]) / len(collection_history) if collection_history else 1
    if avg_retries > 2:
        recommendations.append({
            'recommendation_type': 'INCREASE_FREQUENCY',
            'priority': 'MEDIUM',
            'reason': f'Average {avg_retries:.1f} retries per collection indicates timing issues',
            'expected_impact': 'Reduce operational costs by 15-25%',
            'action_required': 'Implement more frequent balance monitoring (every 2 days) during collection window'
        })
    
    # Recommendation 5: Optimal window opportunities
    optimal_collections = [c for c in upcoming_collections if c['status'] == 'OPTIMAL_WINDOW']
    if len(optimal_collections) >= 2:
        recommendations.append({
            'recommendation_type': 'SKIP_ATTEMPT',
            'priority': 'LOW',
            'reason': f'{len(optimal_collections)} collections are in optimal windows with high success probability',
            'expected_impact': 'Save manual intervention costs, maintain high success rate',
            'action_required': 'Auto-process these collections without manual review'
        })
    
    return recommendations

def detect_risk_signals(customer_data, behavioral_insights, collection_history):
    """Detect risk signals from financial behavior"""
    signals = []
    
    # Signal 1: Declining balance trend
    spending_pattern = behavioral_insights.get('spending_pattern', {})
    avg_balance = spending_pattern.get('average_daily_balance', 50000)
    
    if avg_balance < 10000:
        signals.append({
            'signal_type': 'LOW_AVERAGE_BALANCE',
            'severity': 'HIGH',
            'description': f'Average daily balance is only ₹{avg_balance:.2f}, indicating financial stress',
            'detected_date': datetime.now().strftime('%Y-%m-%d')
        })
    
    # Signal 2: Multiple failed attempts
    recent_failures = [h for h in collection_history[-10:] if h['status'].startswith('FAILED')]
    if len(recent_failures) >= 5:
        signals.append({
            'signal_type': 'REPEATED_COLLECTION_FAILURES',
            'severity': 'CRITICAL',
            'description': f'{len(recent_failures)} failed attempts in last 10 collections',
            'detected_date': datetime.now().strftime('%Y-%m-%d')
        })
    
    # Signal 3: Inconsistent salary
    salary_pattern = behavioral_insights.get('salary_credit_pattern', {})
    consistency = salary_pattern.get('consistency_score', 80)
    
    if consistency < 50:
        signals.append({
            'signal_type': 'IRREGULAR_INCOME',
            'severity': 'MEDIUM',
            'description': f'Income consistency score is {consistency:.1f}%, suggesting unstable income',
            'detected_date': datetime.now().strftime('%Y-%m-%d')
        })
    
    # Signal 4: High spending on low balance days
    low_balance_days = spending_pattern.get('low_balance_days', [])
    if len(low_balance_days) > 5:
        signals.append({
            'signal_type': 'POOR_CASH_MANAGEMENT',
            'severity': 'MEDIUM',
            'description': 'Frequent low balance periods indicate poor cash flow management',
            'detected_date': datetime.now().strftime('%Y-%m-%d')
        })
    
    # Signal 5: Payment punctuality issues
    payment_behavior = behavioral_insights.get('payment_behavior', {})
    punctuality = payment_behavior.get('payment_punctuality_score', 75)
    avg_delay = payment_behavior.get('avg_delay_days', 0)
    
    if punctuality < 60 or avg_delay > 5:
        signals.append({
            'signal_type': 'PAYMENT_DELAYS',
            'severity': 'HIGH',
            'description': f'Payment punctuality is {punctuality:.1f}% with average delay of {avg_delay:.1f} days',
            'detected_date': datetime.now().strftime('%Y-%m-%d')
        })
    
    return signals

def calculate_cost_savings(collection_history):
    """Calculate operational cost savings from smart scheduling"""
    total_attempts = len(collection_history)
    successful_first_attempt = len([h for h in collection_history if h['attempt_number'] == 1 and h['status'] == 'SUCCESS'])
    
    # Traditional system: assume 30% first attempt success
    traditional_first_success_rate = 0.30
    traditional_first_success = int(total_attempts * traditional_first_success_rate)
    
    # Smart collect improvement
    additional_first_success = successful_first_attempt - traditional_first_success
    
    # Cost per retry: ₹50 (transaction fees, manual intervention, etc.)
    cost_per_retry = 50
    cost_saved = max(0, additional_first_success * cost_per_retry)
    
    return cost_saved

def generate_smart_collect_analytics(customer_id):
    """Generate complete smart collect analytics for a customer"""
    print(f'Generating Smart Collect analytics for {customer_id}...')
    
    # Load customer data
    customer_data = load_customer_data(customer_id)
    
    if not customer_data:
        print(f'  ⚠ No customer data found for {customer_id}')
        return None
    
    credit_data = customer_data.get('credit', {})
    earnings_data = customer_data.get('earnings', {})
    transactions_data = customer_data.get('transactions', {})
    
    # Analyze behavioral patterns
    salary_pattern = analyze_salary_pattern(earnings_data)
    spending_pattern = analyze_spending_pattern(transactions_data, earnings_data)
    payment_behavior = analyze_payment_behavior(credit_data)
    
    behavioral_insights = {
        'salary_credit_pattern': salary_pattern,
        'spending_pattern': spending_pattern,
        'payment_behavior': payment_behavior
    }
    
    # Generate collection history
    collection_history = generate_collection_history(customer_id, credit_data)
    
    # Generate upcoming collections
    upcoming_collections = generate_upcoming_collections(customer_id, credit_data, salary_pattern)
    
    # Calculate summary metrics
    total_scheduled = len(collection_history) + len(upcoming_collections)
    successful = len([h for h in collection_history if h['status'] == 'SUCCESS'])
    failed = len([h for h in collection_history if h['status'].startswith('FAILED')])
    pending = len(upcoming_collections)
    
    success_rate = (successful / len(collection_history) * 100) if collection_history else 75
    
    total_collected = sum([h['emi_amount'] for h in collection_history if h['status'] == 'SUCCESS'])
    total_pending = sum([u['emi_amount'] for u in upcoming_collections])
    
    avg_retries = sum([h['attempt_number'] for h in collection_history]) / len(collection_history) if collection_history else 1.5
    
    cost_saved = calculate_cost_savings(collection_history)
    
    # Generate recommendations
    recommendations = generate_smart_recommendations(upcoming_collections, behavioral_insights, collection_history)
    
    # Detect risk signals
    risk_signals = detect_risk_signals(customer_data, behavioral_insights, collection_history)
    
    # Compile final analytics
    analytics = {
        'customer_id': customer_id,
        'generated_at': datetime.now().isoformat(),
        'collection_summary': {
            'total_emis_scheduled': total_scheduled,
            'successful_collections': successful,
            'failed_collections': failed,
            'pending_collections': pending,
            'collection_success_rate': round(success_rate, 2),
            'total_amount_collected': round(total_collected, 2),
            'total_amount_pending': round(total_pending, 2),
            'average_retry_count': round(avg_retries, 2),
            'cost_saved': round(cost_saved, 2)
        },
        'upcoming_collections': upcoming_collections,
        'collection_history': collection_history[-20:],  # Last 20 attempts
        'smart_recommendations': recommendations,
        'behavioral_insights': behavioral_insights,
        'risk_signals': risk_signals
    }
    
    return analytics

def save_analytics(customer_id, analytics):
    """Save analytics to file"""
    if not analytics:
        return False
    
    output_dir = Path(__file__).parent.parent / 'analytics'
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f'{customer_id}_smart_collect.json'
    
    with open(output_file, 'w') as f:
        json.dump(analytics, f, indent=2)
    
    print(f'  ✓ Smart Collect analytics saved to {output_file.name}')
    return True

def main():
    """Generate smart collect analytics for all customers"""
    analytics_dir = Path(__file__).parent.parent / 'analytics'
    
    if not analytics_dir.exists():
        print('Analytics directory not found!')
        return
    
    # Find all customer IDs
    customer_files = list(analytics_dir.glob('CUST_MSM_*_credit_summary.json'))
    customer_ids = [f.name.replace('_credit_summary.json', '') for f in customer_files]
    
    print(f'\n📊 Generating Smart Collect Analytics for {len(customer_ids)} customers...\n')
    
    success_count = 0
    for customer_id in customer_ids:
        analytics = generate_smart_collect_analytics(customer_id)
        if save_analytics(customer_id, analytics):
            success_count += 1
    
    print(f'\n✅ Successfully generated Smart Collect analytics for {success_count}/{len(customer_ids)} customers\n')

if __name__ == '__main__':
    main()
