"""
Proportional Financial Data Generator
Generates OCEN, ONDC, insurance, and mutual funds data proportional to customer's income, GST, and spending.

Rules:
- OCEN loan applications: < 30% of annual GST turnover
- Insurance premium: < 10% of annual income
- ONDC orders: 10-15% of monthly spending
- Mutual funds: < 50% of annual savings (income - spending)
"""

import json
import os
import random
from datetime import datetime, timedelta
import numpy as np


class ProportionalFinancialDataGenerator:
    """Generate realistic financial product data proportional to customer profile."""
    
    def __init__(self, customer_id, analytics_dir='analytics'):
        """Initialize generator with customer data."""
        self.customer_id = customer_id
        self.analytics_dir = analytics_dir
        
        # Load customer data
        self.earnings_data = self.load_json(f'{customer_id}_earnings_spendings.json')
        self.gst_data = self.load_json(f'{customer_id}_gst_summary.json')
        self.transactions_data = self.load_json(f'{customer_id}_transaction_summary.json')
        
        # Calculate key metrics
        self.calculate_profile()
    
    def load_json(self, filename):
        """Load JSON file."""
        filepath = os.path.join(self.analytics_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}
    
    def save_json(self, data, filename):
        """Save JSON file."""
        filepath = os.path.join(self.analytics_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def calculate_profile(self):
        """Calculate customer financial profile."""
        # Income and spending
        cashflow = self.earnings_data.get('cashflow_metrics', {})
        self.total_inflow = cashflow.get('total_inflow', 0)
        self.total_outflow = cashflow.get('total_outflow', 0)
        self.net_surplus = cashflow.get('net_surplus', 0)
        
        # Get number of months from monthly_inflow
        monthly_inflow = cashflow.get('monthly_inflow', {})
        self.num_months = len(monthly_inflow) if monthly_inflow else 36
        
        # Calculate averages
        self.avg_monthly_income = self.total_inflow / self.num_months if self.num_months > 0 else 0
        self.avg_monthly_spending = self.total_outflow / self.num_months if self.num_months > 0 else 0
        self.avg_monthly_savings = self.net_surplus / self.num_months if self.num_months > 0 else 0
        
        # Annual calculations
        self.annual_income = self.avg_monthly_income * 12
        self.annual_spending = self.avg_monthly_spending * 12
        self.annual_savings = self.avg_monthly_savings * 12
        
        # GST turnover
        self.annual_gst_turnover = self.gst_data.get('annual_turnover', 0)
        
        # Transaction data
        self.total_transactions = self.transactions_data.get('total_transactions', 0)
        
        # Calculate proportional limits
        self.max_ocen_loan = min(self.annual_gst_turnover * 0.3, self.annual_income * 2) if self.annual_gst_turnover > 0 else self.annual_income * 0.5
        self.max_insurance_premium = self.annual_income * 0.10
        self.max_ondc_monthly = self.avg_monthly_spending * 0.15
        self.max_mutual_funds = self.annual_savings * 0.50 if self.annual_savings > 0 else self.annual_income * 0.05
    
    def generate_ocen_data(self):
        """Generate OCEN loan application data."""
        # Decide number of applications (0-3 based on profile)
        if self.annual_gst_turnover < 1000000:  # < 10L turnover
            num_applications = random.choice([0, 0, 1])  # 67% chance of 0
        elif self.annual_gst_turnover < 5000000:  # < 50L turnover
            num_applications = random.choice([0, 1, 1, 2])  # More likely to have 1-2
        else:  # > 50L turnover
            num_applications = random.choice([1, 2, 2, 3])  # More likely to have 2-3
        
        applications = []
        total_amount = 0
        
        for i in range(num_applications):
            # Loan amount: 5-25% of max limit
            loan_amount = random.uniform(0.05, 0.25) * self.max_ocen_loan
            loan_amount = round(loan_amount / 10000) * 10000  # Round to nearest 10K
            
            # Tenure: 3-36 months
            tenure_months = random.choice([3, 6, 9, 12, 18, 24, 36])
            
            # Interest rate: 9-18%
            interest_rate = round(random.uniform(9.0, 18.0), 2)
            
            # Status
            status = random.choice(['APPROVED', 'APPROVED', 'APPROVED', 'PENDING', 'REJECTED'])
            
            # Application date (last 2 years)
            days_ago = random.randint(30, 730)
            app_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            application = {
                'application_id': f'OCEN_{self.customer_id}_{i+1:03d}',
                'loan_amount': loan_amount,
                'tenure_months': tenure_months,
                'interest_rate': interest_rate,
                'status': status,
                'application_date': app_date,
                'lender': random.choice(['FinTech Lender A', 'Digital Bank B', 'MSME Finance Corp', 'Quick Loan Ltd'])
            }
            applications.append(application)
            
            if status == 'APPROVED':
                total_amount += loan_amount
        
        # Calculate summary
        approved_apps = [a for a in applications if a['status'] == 'APPROVED']
        
        ocen_summary = {
            'customer_id': self.customer_id,
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'total_applications': num_applications,
            'approved_applications': len(approved_apps),
            'total_approved_amount': total_amount,
            'average_loan_amount': total_amount / len(approved_apps) if approved_apps else 0,
            'applications': applications,
            'profile_constraints': {
                'annual_gst_turnover': self.annual_gst_turnover,
                'max_loan_limit': self.max_ocen_loan,
                'total_approved_percentage_of_limit': (total_amount / self.max_ocen_loan * 100) if self.max_ocen_loan > 0 else 0
            }
        }
        
        return ocen_summary
    
    def generate_ondc_data(self):
        """Generate ONDC order data."""
        # Monthly orders: 5-20 based on spending
        if self.avg_monthly_spending < 100000:  # < 1L spending/month
            orders_per_month = random.randint(3, 8)
        elif self.avg_monthly_spending < 500000:  # < 5L spending/month
            orders_per_month = random.randint(5, 15)
        else:
            orders_per_month = random.randint(10, 20)
        
        # Generate 3 months of orders
        num_orders = orders_per_month * 3
        orders = []
        total_value = 0
        
        providers = ['Swiggy', 'Zomato', 'Dunzo', 'BigBasket', 'Blinkit', 'Zepto']
        categories = ['Food & Beverage', 'Groceries', 'Supplies', 'Electronics', 'Stationery']
        states = ['Delhi', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'Gujarat', 'Telangana']
        
        for i in range(num_orders):
            # Order value: Distribute total max ONDC budget across orders
            order_value = random.uniform(0.3, 2.5) * (self.max_ondc_monthly / orders_per_month)
            order_value = round(order_value, 2)
            
            # Order date (last 3 months)
            days_ago = random.randint(1, 90)
            order_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            order = {
                'order_id': f'ONDC_{self.customer_id}_{i+1:04d}',
                'order_date': order_date,
                'order_value': order_value,
                'provider': random.choice(providers),
                'category': random.choice(categories),
                'delivery_state': random.choice(states),
                'status': random.choice(['DELIVERED', 'DELIVERED', 'DELIVERED', 'IN_TRANSIT', 'PENDING'])
            }
            orders.append(order)
            total_value += order_value
        
        # Calculate summary by provider and state
        by_provider = {}
        by_state = {}
        for order in orders:
            provider = order['provider']
            state = order['delivery_state']
            
            by_provider[provider] = by_provider.get(provider, 0) + 1
            by_state[state] = by_state.get(state, 0) + 1
        
        top_providers = sorted(by_provider.keys(), key=lambda x: by_provider[x], reverse=True)[:5]
        
        ondc_summary = {
            'customer_id': self.customer_id,
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'total_orders': num_orders,
            'total_value': round(total_value, 2),
            'average_order_value': round(total_value / num_orders, 2) if num_orders > 0 else 0,
            'by_state': by_state,
            'by_provider': by_provider,
            'provider_diversity': len(by_provider),
            'top_providers': top_providers,
            'orders': orders[:50],  # Store only recent 50
            'profile_constraints': {
                'avg_monthly_spending': self.avg_monthly_spending,
                'max_ondc_monthly': self.max_ondc_monthly,
                'ondc_percentage_of_spending': (total_value / (self.avg_monthly_spending * 3) * 100) if self.avg_monthly_spending > 0 else 0
            }
        }
        
        return ondc_summary
    
    def generate_insurance_data(self):
        """Generate insurance policy data."""
        policies = []
        total_premium = 0
        total_coverage = 0
        
        # Business insurance (if GST turnover > 5L)
        if self.annual_gst_turnover > 500000:
            coverage = random.uniform(0.5, 2.0) * self.annual_gst_turnover
            coverage = round(coverage / 100000) * 100000  # Round to nearest 1L
            premium = coverage * random.uniform(0.005, 0.015)  # 0.5-1.5% of coverage
            
            policies.append({
                'policy_id': f'BUS_{self.customer_id}_001',
                'type': 'Business',
                'coverage': coverage,
                'annual_premium': round(premium, 2),
                'start_date': (datetime.now() - timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d'),
                'status': 'Active',
                'insurer': random.choice(['HDFC Ergo', 'ICICI Lombard', 'Bajaj Allianz', 'Tata AIG'])
            })
            total_premium += premium
            total_coverage += coverage
        
        # Health insurance (always have one)
        health_coverage = random.uniform(300000, 1000000)
        if self.annual_income > 1000000:
            health_coverage = random.uniform(500000, 2000000)
        health_coverage = round(health_coverage / 100000) * 100000
        health_premium = health_coverage * random.uniform(0.015, 0.025)
        
        policies.append({
            'policy_id': f'HEA_{self.customer_id}_001',
            'type': 'Health',
            'coverage': health_coverage,
            'annual_premium': round(health_premium, 2),
            'start_date': (datetime.now() - timedelta(days=random.randint(30, 1095))).strftime('%Y-%m-%d'),
            'status': 'Active',
            'insurer': random.choice(['Star Health', 'Max Bupa', 'Care Health', 'Niva Bupa'])
        })
        total_premium += health_premium
        total_coverage += health_coverage
        
        # Term life insurance (if income > 5L/year)
        if self.annual_income > 500000:
            term_coverage = random.uniform(10, 25) * self.annual_income
            term_coverage = round(term_coverage / 100000) * 100000
            term_premium = term_coverage * random.uniform(0.0005, 0.0015)
            
            policies.append({
                'policy_id': f'TRM_{self.customer_id}_001',
                'type': 'Term Life',
                'coverage': term_coverage,
                'annual_premium': round(term_premium, 2),
                'start_date': (datetime.now() - timedelta(days=random.randint(365, 1825))).strftime('%Y-%m-%d'),
                'status': 'Active',
                'insurer': random.choice(['LIC', 'HDFC Life', 'SBI Life', 'ICICI Prudential'])
            })
            total_premium += term_premium
            total_coverage += term_coverage
        
        # Validate: total premium should be < 10% of annual income
        if total_premium > self.max_insurance_premium:
            scale_factor = self.max_insurance_premium / total_premium
            for policy in policies:
                policy['annual_premium'] = round(policy['annual_premium'] * scale_factor, 2)
            total_premium = sum(p['annual_premium'] for p in policies)
        
        by_type = {}
        for policy in policies:
            policy_type = policy['type']
            by_type[policy_type] = by_type.get(policy_type, 0) + 1
        
        insurance_summary = {
            'customer_id': self.customer_id,
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'total_policies': len(policies),
            'total_coverage': round(total_coverage, 2),
            'annual_premium': round(total_premium, 2),
            'by_type': by_type,
            'active_policies': len([p for p in policies if p['status'] == 'Active']),
            'policies': policies,
            'profile_constraints': {
                'annual_income': self.annual_income,
                'max_premium_limit': self.max_insurance_premium,
                'premium_percentage_of_income': (total_premium / self.annual_income * 100) if self.annual_income > 0 else 0
            }
        }
        
        return insurance_summary
    
    def generate_mutual_funds_data(self):
        """Generate mutual funds investment data."""
        portfolios = []
        total_investment = 0
        total_current_value = 0
        
        # Number of funds: 1-5 based on savings capacity
        if self.annual_savings < 100000:
            num_funds = random.randint(0, 2)
        elif self.annual_savings < 500000:
            num_funds = random.randint(1, 3)
        else:
            num_funds = random.randint(2, 5)
        
        fund_types = ['Equity', 'Debt', 'Hybrid', 'Index', 'Liquid']
        fund_houses = ['HDFC MF', 'ICICI Prudential', 'SBI MF', 'Axis MF', 'Kotak MF', 'UTI MF']
        
        for i in range(num_funds):
            # Investment amount
            investment = random.uniform(0.1, 0.4) * self.max_mutual_funds / num_funds if num_funds > 0 else 0
            investment = round(investment, 2)
            
            # Returns: -5% to +25%
            return_pct = random.uniform(-5, 25)
            current_value = investment * (1 + return_pct / 100)
            current_value = round(current_value, 2)
            
            # Start date (6 months to 5 years ago)
            days_ago = random.randint(180, 1825)
            start_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            # SIP or lumpsum
            is_sip = random.choice([True, True, True, False])  # 75% SIP
            
            portfolio = {
                'portfolio_id': f'MF_{self.customer_id}_{i+1:03d}',
                'fund_name': f'{random.choice(fund_houses)} {random.choice(fund_types)} Fund',
                'scheme_type': random.choice(fund_types),
                'investment_type': 'SIP' if is_sip else 'Lumpsum',
                'invested_amount': investment,
                'current_value': current_value,
                'returns': round(current_value - investment, 2),
                'returns_percentage': round(return_pct, 2),
                'start_date': start_date,
                'status': random.choice(['Active', 'Active', 'Active', 'Redeemed'])
            }
            
            portfolios.append(portfolio)
            total_investment += investment
            total_current_value += current_value
        
        by_scheme_type = {}
        for portfolio in portfolios:
            scheme = portfolio['scheme_type']
            by_scheme_type[scheme] = by_scheme_type.get(scheme, 0) + 1
        
        mutual_funds_summary = {
            'customer_id': self.customer_id,
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'total_portfolios': len(portfolios),
            'total_investment': round(total_investment, 2),
            'current_value': round(total_current_value, 2),
            'returns': round(total_current_value - total_investment, 2),
            'returns_percentage': round((total_current_value - total_investment) / total_investment * 100, 2) if total_investment > 0 else 0,
            'by_scheme_type': by_scheme_type,
            'portfolios': portfolios,
            'profile_constraints': {
                'annual_savings': self.annual_savings,
                'max_investment_limit': self.max_mutual_funds,
                'investment_percentage_of_savings': (total_investment / self.annual_savings * 100) if self.annual_savings > 0 else 0
            }
        }
        
        return mutual_funds_summary
    
    def generate_all(self):
        """Generate all financial product data."""
        print(f"\n📊 Generating proportional financial data for {self.customer_id}")
        print(f"   Profile: Income ₹{self.annual_income:,.0f}/yr, GST ₹{self.annual_gst_turnover:,.0f}/yr, Savings ₹{self.annual_savings:,.0f}/yr")
        
        # Generate OCEN
        ocen_data = self.generate_ocen_data()
        self.save_json(ocen_data, f'{self.customer_id}_ocen_summary.json')
        print(f"   ✓ OCEN: {ocen_data['total_applications']} applications, "
              f"₹{ocen_data['total_approved_amount']:,.0f} approved "
              f"({ocen_data['profile_constraints']['total_approved_percentage_of_limit']:.1f}% of limit)")
        
        # Generate ONDC
        ondc_data = self.generate_ondc_data()
        self.save_json(ondc_data, f'{self.customer_id}_ondc_summary.json')
        print(f"   ✓ ONDC: {ondc_data['total_orders']} orders, "
              f"₹{ondc_data['total_value']:,.2f} "
              f"({ondc_data['profile_constraints']['ondc_percentage_of_spending']:.1f}% of spending)")
        
        # Generate Insurance
        insurance_data = self.generate_insurance_data()
        self.save_json(insurance_data, f'{self.customer_id}_insurance_summary.json')
        print(f"   ✓ Insurance: {insurance_data['total_policies']} policies, "
              f"₹{insurance_data['total_coverage']:,.0f} coverage, "
              f"₹{insurance_data['annual_premium']:,.0f} premium "
              f"({insurance_data['profile_constraints']['premium_percentage_of_income']:.1f}% of income)")
        
        # Generate Mutual Funds
        mf_data = self.generate_mutual_funds_data()
        self.save_json(mf_data, f'{self.customer_id}_mutual_funds_summary.json')
        print(f"   ✓ Mutual Funds: {mf_data['total_portfolios']} funds, "
              f"₹{mf_data['total_investment']:,.2f} invested, "
              f"₹{mf_data['current_value']:,.2f} current "
              f"({mf_data['returns_percentage']:+.1f}% returns)")


def main():
    """Generate proportional data for all customers."""
    import glob
    
    analytics_dir = 'analytics'
    earnings_files = glob.glob(os.path.join(analytics_dir, '*_earnings_spendings.json'))
    
    print(f"🏦 Generating proportional financial product data for {len(earnings_files)} customers...")
    
    for earnings_file in sorted(earnings_files):
        customer_id = os.path.basename(earnings_file).replace('_earnings_spendings.json', '')
        
        try:
            generator = ProportionalFinancialDataGenerator(customer_id, analytics_dir)
            generator.generate_all()
        except Exception as e:
            print(f"❌ Error processing {customer_id}: {e}")
    
    print(f"\n✅ Completed proportional financial data generation for all customers")


if __name__ == '__main__':
    main()
