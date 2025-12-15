"""
Profile-aware data generator for GST, Mutual Funds, Insurance, OCEN, and ONDC.
Generates data matching the specific profile of each customer (high_growth, declining, etc.)
"""
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import sys
import os
from dateutil import parser

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from generators.indian_data_utils import *


# Customer profile assignments
CUSTOMER_PROFILES = {
    "CUST_MSM_00001": "baseline",
    "CUST_MSM_00002": "high_seasonality",
    "CUST_MSM_00003": "high_debt",
    "CUST_MSM_00004": "high_growth",
    "CUST_MSM_00005": "stable_income",
    "CUST_MSM_00006": "fraud",  # Changed from high_bounce to fraud
    "CUST_MSM_00007": "declining",
    "CUST_MSM_00008": "customer_concentration",
    "CUST_MSM_00009": "high_growth",
    "CUST_MSM_00010": "high_seasonality"
}


class ProfileAwareGSTGenerator:
    """Generate GST returns matching customer profile."""
    
    def __init__(self):
        self.gstin_prefix = ["27", "29", "24", "07", "33"]  # State codes
        
    def generate_gstin(self, customer_id: str) -> str:
        """Generate GSTIN for customer."""
        state = random.choice(self.gstin_prefix)
        pan_part = f"{customer_id[-5:]}{random.randint(100, 999)}"
        entity = random.choice(["Z", "C", "F"])
        check = random.randint(1, 9)
        return f"{state}{pan_part}{entity}{check}"
    
    def generate_for_customer(self, customer_id: str, profile: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Generate GST returns for a customer matching their profile."""
        gstin = self.generate_gstin(customer_id)
        trade_name = f"Business_{customer_id[-5:]}"
        
        returns = []
        current_date = start_date
        
        # Base monthly turnover based on profile
        base_turnover = self._get_base_turnover(profile)
        
        month_count = 0
        while current_date < end_date:
            month_count += 1
            period = current_date.strftime("%Y-%m")
            
            # Apply profile-specific modifications
            turnover = self._apply_profile_modifier(base_turnover, profile, month_count, current_date)
            
            # CGST and SGST (typically 9% each on taxable value)
            taxable_value = turnover / 1.18  # Reverse calculate excluding GST
            cgst = taxable_value * 0.09
            sgst = taxable_value * 0.09
            igst = 0 if random.random() < 0.7 else taxable_value * 0.18
            
            # Input tax credit (typically 60-80% of output tax)
            itc_percentage = random.uniform(0.6, 0.8)
            if profile == "fraud":
                # Fraud: inflated ITC (claiming more than actual)
                itc_percentage = random.uniform(0.9, 1.15)
            
            total_tax = cgst + sgst + igst
            itc_availed = total_tax * itc_percentage
            
            # Filing status
            filing_status = "FILED"
            filing_date = current_date + timedelta(days=random.randint(10, 20))
            
            if profile == "fraud" and random.random() < 0.3:
                # Fraud: some late/missing filings
                filing_status = random.choice(["FILED_LATE", "NOT_FILED"])
                filing_date = current_date + timedelta(days=random.randint(30, 90))
            elif profile == "declining" and random.random() < 0.15:
                filing_status = "FILED_LATE"
                filing_date = current_date + timedelta(days=random.randint(25, 45))
            
            gst_return = {
                "return_id": f"GST{customer_id[-5:]}{month_count:04d}",
                "gstin": gstin,
                "trade_name": trade_name,
                "customer_id": customer_id,
                "return_period": period,
                "return_type": "GSTR3B",
                "filing_date": filing_date.strftime("%Y-%m-%d"),
                "filing_status": filing_status,
                "turnover": round(turnover, 2),
                "taxable_value": round(taxable_value, 2),
                "output_tax": {
                    "cgst": round(cgst, 2),
                    "sgst": round(sgst, 2),
                    "igst": round(igst, 2),
                    "total": round(total_tax, 2)
                },
                "itc_availed": round(itc_availed, 2),
                "tax_payable": round(max(0, total_tax - itc_availed), 2),
                "late_fee": 0 if filing_status == "FILED" else random.randint(100, 500)
            }
            
            # Fraud indicators
            if profile == "fraud":
                gst_return["fraud_indicators"] = {
                    "itc_ratio_high": itc_availed / total_tax > 0.95 if total_tax > 0 else False,
                    "late_filing": filing_status in ["FILED_LATE", "NOT_FILED"],
                    "turnover_mismatch": random.random() < 0.4  # Mismatch with bank statements
                }
            
            returns.append(gst_return)
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return returns
    
    def _get_base_turnover(self, profile: str) -> float:
        """Get base monthly turnover based on profile."""
        if profile == "high_growth":
            return random.uniform(200000, 400000)
        elif profile == "declining":
            return random.uniform(500000, 800000)  # Starts high, will decline
        elif profile == "stable_income":
            return random.uniform(300000, 500000)
        elif profile == "high_debt":
            return random.uniform(400000, 600000)
        elif profile == "fraud":
            return random.uniform(600000, 1000000)  # High reported turnover
        elif profile == "baseline":
            return random.uniform(250000, 450000)
        else:
            return random.uniform(300000, 600000)
    
    def _apply_profile_modifier(self, base: float, profile: str, month_num: int, date: datetime) -> float:
        """Apply profile-specific growth/decline patterns."""
        if profile == "high_growth":
            # Growth factor increases over time (30% -> 300%)
            growth_factor = 0.3 + (month_num / 36) * 2.7
            return base * growth_factor
        
        elif profile == "declining":
            # Decline factor (150% -> 20%)
            decline_factor = max(0.2, 1.5 - (month_num / 36) * 1.3)
            return base * decline_factor
        
        elif profile == "high_seasonality":
            # Strong seasonal pattern
            month = date.month
            if month in [10, 11, 12]:  # Festival season
                return base * random.uniform(3.0, 5.0)
            elif month in [1, 2, 3]:  # Quarter end
                return base * random.uniform(1.5, 2.5)
            elif month in [4, 5, 6]:
                return base * random.uniform(0.8, 1.2)
            else:
                return base * random.uniform(0.2, 0.5)
        
        elif profile == "stable_income":
            # Very stable, ±5%
            return base * random.uniform(0.95, 1.05)
        
        elif profile == "fraud":
            # Inflated reported turnover vs actual
            return base * random.uniform(1.5, 2.5)
        
        else:
            # Baseline: normal variation
            return base * random.uniform(0.85, 1.15)


class ProfileAwareMutualFundGenerator:
    """Generate mutual fund portfolios matching customer profile."""
    
    def __init__(self):
        self.schemes = [
            {"amc": "HDFC MF", "name": "HDFC Equity Fund", "type": "EQUITY"},
            {"amc": "ICICI Prudential MF", "name": "ICICI Bluechip Fund", "type": "EQUITY"},
            {"amc": "SBI MF", "name": "SBI Large & Midcap Fund", "type": "EQUITY"},
            {"amc": "UTI MF", "name": "UTI Nifty Index Fund", "type": "EQUITY"},
            {"amc": "Axis MF", "name": "Axis Long Term Equity Fund", "type": "EQUITY"},
            {"amc": "HDFC MF", "name": "HDFC Liquid Fund", "type": "LIQUID"},
            {"amc": "ICICI Prudential MF", "name": "ICICI Overnight Fund", "type": "LIQUID"},
            {"amc": "Axis MF", "name": "Axis Hybrid Fund", "type": "HYBRID"},
            {"amc": "SBI MF", "name": "SBI Debt Fund", "type": "DEBT"},
        ]
    
    def generate_for_customer(self, customer_id: str, profile: str) -> List[Dict]:
        """Generate mutual fund portfolios for customer."""
        user_id = f"USER_{customer_id}"
        
        # Number of portfolios based on profile
        if profile in ["high_growth", "stable_income"]:
            num_portfolios = random.randint(3, 6)
        elif profile == "declining":
            num_portfolios = random.randint(1, 3)  # Fewer investments
        elif profile == "fraud":
            num_portfolios = random.randint(4, 7)  # Many for appearance
        else:
            num_portfolios = random.randint(2, 4)
        
        portfolios = []
        for i in range(num_portfolios):
            scheme = random.choice(self.schemes)
            portfolio = self._generate_portfolio(customer_id, user_id, scheme, profile, i+1)
            portfolios.append(portfolio)
        
        return portfolios
    
    def _generate_portfolio(self, customer_id: str, user_id: str, scheme: Dict, profile: str, idx: int) -> Dict:
        """Generate a single mutual fund portfolio."""
        folio_number = f"{random.randint(10000000, 99999999)}/{random.randint(10, 99)}"
        
        # Investment amount based on profile
        if profile == "high_growth":
            invested = random.uniform(50000, 500000)
            returns_pct = random.uniform(15, 45)  # High returns
        elif profile == "stable_income":
            invested = random.uniform(100000, 400000)
            returns_pct = random.uniform(8, 15)  # Stable returns
        elif profile == "declining":
            invested = random.uniform(20000, 150000)
            returns_pct = random.uniform(-10, 5)  # Poor/negative returns
        elif profile == "fraud":
            invested = random.uniform(200000, 800000)
            returns_pct = random.uniform(-20, -5)  # Losses (poor decisions)
        else:
            invested = random.uniform(50000, 300000)
            returns_pct = random.uniform(5, 18)
        
        current_value = invested * (1 + returns_pct/100)
        returns_abs = current_value - invested
        
        units = random.uniform(100, 10000)
        current_nav = current_value / units if units > 0 else 100
        average_nav = invested / units if units > 0 else 90
        
        # Generate transactions
        num_txns = random.randint(5, 20)
        transactions = []
        for txn_idx in range(num_txns):
            txn_date = datetime.now() - timedelta(days=random.randint(30, 730))
            transactions.append({
                "transaction_id": f"MFTXN{customer_id[-5:]}{idx:03d}{txn_idx:02d}",
                "transaction_date": txn_date.strftime("%Y-%m-%d"),
                "transaction_type": random.choice(["PURCHASE", "SIP", "DIVIDEND", "REDEMPTION"]),
                "amount": round(random.uniform(1000, 50000), 2),
                "units": round(random.uniform(10, 500), 4),
                "nav": round(random.uniform(80, 200), 4)
            })
        
        return {
            "portfolio_id": f"MF{customer_id[-5:]}{idx:04d}",
            "user_id": user_id,
            "customer_id": customer_id,
            "folio_number": folio_number,
            "amc": scheme["amc"],
            "scheme_name": scheme["name"],
            "scheme_code": f"{scheme['amc'][:3].upper()}{random.randint(100,999)}",
            "scheme_type": scheme["type"],
            "units": round(units, 2),
            "current_nav": round(current_nav, 4),
            "current_value": round(current_value, 2),
            "invested_amount": round(invested, 2),
            "average_nav": round(average_nav, 4),
            "returns_abs": round(returns_abs, 2),
            "returns_pct": round(returns_pct, 2),
            "transactions": transactions
        }


class ProfileAwareInsuranceGenerator:
    """Generate insurance policies matching customer profile."""
    
    def __init__(self):
        self.policy_types = ["LIFE", "HEALTH", "TERM", "VEHICLE", "HOME"]
        self.insurers = ["LIC", "HDFC Life", "ICICI Prudential", "SBI Life", "Bajaj Allianz"]
    
    def generate_for_customer(self, customer_id: str, profile: str) -> List[Dict]:
        """Generate insurance policies for customer."""
        user_id = f"USER_{customer_id}"
        
        # Number of policies based on profile
        if profile in ["high_growth", "stable_income"]:
            num_policies = random.randint(3, 5)
        elif profile == "declining":
            num_policies = random.randint(1, 2)
        elif profile == "fraud":
            num_policies = random.randint(2, 4)
        else:
            num_policies = random.randint(2, 4)
        
        policies = []
        for i in range(num_policies):
            policy = self._generate_policy(customer_id, user_id, profile, i+1)
            policies.append(policy)
        
        return policies
    
    def _generate_policy(self, customer_id: str, user_id: str, profile: str, idx: int) -> Dict:
        """Generate a single insurance policy."""
        policy_type = random.choice(self.policy_types)
        insurer = random.choice(self.insurers)
        
        policy_number = f"{insurer[:3].upper()}/{random.randint(100000, 999999)}/{random.randint(2018, 2024)}"
        
        # Sum assured based on profile
        if profile == "high_growth":
            sum_assured = random.uniform(1000000, 5000000)
        elif profile == "stable_income":
            sum_assured = random.uniform(500000, 2000000)
        elif profile == "declining":
            sum_assured = random.uniform(200000, 800000)
        elif profile == "fraud":
            sum_assured = random.uniform(3000000, 10000000)  # Over-insured
        else:
            sum_assured = random.uniform(300000, 1500000)
        
        premium = sum_assured * random.uniform(0.02, 0.05)
        
        start_date = datetime.now() - timedelta(days=random.randint(365, 1825))
        end_date = start_date + timedelta(days=random.randint(365, 3650))
        
        status = "ACTIVE" if datetime.now() < end_date else "MATURED"
        
        if profile == "fraud" and random.random() < 0.3:
            # Fraud: some lapsed policies (non-payment)
            status = "LAPSED"
        
        return {
            "policy_id": f"POL{customer_id[-5:]}{idx:04d}",
            "user_id": user_id,
            "customer_id": customer_id,
            "policy_number": policy_number,
            "policy_type": policy_type,
            "insurer": insurer,
            "insured_name": generate_indian_name(),
            "nominee_name": generate_indian_name(),
            "sum_assured": f"{sum_assured:,.2f}",
            "premium_amount": f"{premium:.2f}",
            "premium_frequency": random.choice(["MONTHLY", "QUARTERLY", "YEARLY"]),
            "policy_start_date": start_date.strftime("%Y-%m-%d"),
            "policy_end_date": end_date.strftime("%Y-%m-%d"),
            "status": status,
            "last_premium_paid_date": (start_date + timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
            "claims": [],
            "rider_details": []
        }


class ProfileAwareOCENGenerator:
    """Generate OCEN loan applications matching customer profile."""
    
    def generate_for_customer(self, customer_id: str, profile: str) -> List[Dict]:
        """Generate OCEN applications for customer."""
        user_id = f"USER_{customer_id}"
        
        # Number of applications based on profile
        if profile == "high_debt":
            num_apps = random.randint(5, 10)  # Many loan applications
        elif profile == "declining":
            num_apps = random.randint(3, 6)  # Seeking credit
        elif profile == "fraud":
            num_apps = random.randint(4, 8)  # Many applications
        elif profile == "high_growth":
            num_apps = random.randint(2, 5)  # Growing business
        else:
            num_apps = random.randint(1, 3)
        
        applications = []
        for i in range(num_apps):
            app = self._generate_application(customer_id, user_id, profile, i+1)
            applications.append(app)
        
        return applications
    
    def _generate_application(self, customer_id: str, user_id: str, profile: str, idx: int) -> Dict:
        """Generate a single OCEN loan application."""
        # Loan amount based on profile
        if profile == "high_debt":
            loan_amount = random.uniform(200000, 1000000)
            approval_rate = 0.4  # Lower approval rate
        elif profile == "declining":
            loan_amount = random.uniform(100000, 500000)
            approval_rate = 0.3  # Struggling to get credit
        elif profile == "fraud":
            loan_amount = random.uniform(500000, 2000000)
            approval_rate = 0.2  # Many rejections
        elif profile == "high_growth":
            loan_amount = random.uniform(300000, 1500000)
            approval_rate = 0.8  # High approval
        else:
            loan_amount = random.uniform(100000, 500000)
            approval_rate = 0.6
        
        application_date = datetime.now() - timedelta(days=random.randint(30, 730))
        
        status = random.choices(
            ["APPROVED", "REJECTED", "PENDING", "DISBURSED"],
            weights=[approval_rate*0.6, 1-approval_rate, 0.1, approval_rate*0.4]
        )[0]
        
        interest_rate = random.uniform(12, 24)
        if profile == "fraud":
            interest_rate = random.uniform(20, 36)  # High risk = high rate
        
        return {
            "application_id": f"OCEN{customer_id[-5:]}{idx:04d}",
            "user_id": user_id,
            "customer_id": customer_id,
            "account_customer_id": customer_id,
            "lender_id": f"LENDER{random.randint(100, 999)}",
            "lender_name": random.choice(["HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Mahindra", "IndusInd Bank"]),
            "application_date": application_date.strftime("%Y-%m-%d"),
            "loan_amount": round(loan_amount, 2),
            "loan_purpose": random.choice(["Working Capital", "Business Expansion", "Equipment Purchase", "Inventory"]),
            "tenure_months": random.choice([12, 24, 36, 48, 60]),
            "interest_rate": round(interest_rate, 2),
            "status": status,
            "rejection_reason": random.choice(["Low Credit Score", "Insufficient Documentation", "High Debt Burden"]) if status == "REJECTED" else None
        }


class ProfileAwareONDCGenerator:
    """Generate ONDC orders matching customer profile."""
    
    def __init__(self):
        self.providers = ["Swiggy", "Zomato", "BigBasket", "DMart Ready", "Dunzo"]
        self.items = [
            {"name": "Rice (5kg)", "price": 250},
            {"name": "Office Supplies", "price": 1500},
            {"name": "Stationery", "price": 800},
            {"name": "Snacks Bulk", "price": 3000},
            {"name": "Beverages", "price": 2000},
        ]
    
    def generate_for_customer(self, customer_id: str, profile: str) -> List[Dict]:
        """Generate ONDC orders for customer."""
        user_id = f"USER_{customer_id}"
        
        # Number of orders based on profile
        if profile == "high_growth":
            num_orders = random.randint(20, 40)
        elif profile == "declining":
            num_orders = random.randint(5, 15)
        elif profile == "fraud":
            num_orders = random.randint(15, 30)
        else:
            num_orders = random.randint(10, 25)
        
        orders = []
        for i in range(num_orders):
            order = self._generate_order(customer_id, user_id, profile, i+1)
            orders.append(order)
        
        return orders
    
    def _generate_order(self, customer_id: str, user_id: str, profile: str, idx: int) -> Dict:
        """Generate a single ONDC order."""
        order_date = datetime.now() - timedelta(days=random.randint(1, 365))
        
        num_items = random.randint(1, 5)
        total_price = 0
        items = []
        
        for _ in range(num_items):
            item = random.choice(self.items)
            qty = random.randint(1, 10)
            price = item["price"] * qty
            total_price += price
            items.append({
                "name": item["name"],
                "quantity": qty,
                "price": price
            })
        
        return {
            "order_id": f"ONDC{customer_id[-5:]}{idx:06d}",
            "user_id": user_id,
            "customer_id": customer_id,
            "transaction_id": f"TXN{random.randint(10000000, 99999999)}",
            "provider_name": random.choice(self.providers),
            "order_date": order_date.strftime("%Y-%m-%d"),
            "order_status": random.choice(["COMPLETED", "PENDING", "CANCELLED"]),
            "items": items,
            "total_amount": round(total_price, 2)
        }


def main():
    """Generate all profile-aware data for customers 00001-00010."""
    print("=== Generating Profile-Aware Data for Customers ===\n")
    
    # Date range: last 3 years
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*3)
    
    gst_gen = ProfileAwareGSTGenerator()
    mf_gen = ProfileAwareMutualFundGenerator()
    insurance_gen = ProfileAwareInsuranceGenerator()
    ocen_gen = ProfileAwareOCENGenerator()
    ondc_gen = ProfileAwareONDCGenerator()
    
    all_gst = []
    all_mf = []
    all_insurance = []
    all_ocen = []
    all_ondc = []
    
    for customer_id, profile in CUSTOMER_PROFILES.items():
        print(f"Generating data for {customer_id} ({profile})...")
        
        # GST
        gst_data = gst_gen.generate_for_customer(customer_id, profile, start_date, end_date)
        all_gst.extend(gst_data)
        print(f"  - GST returns: {len(gst_data)}")
        
        # Mutual Funds
        mf_data = mf_gen.generate_for_customer(customer_id, profile)
        all_mf.extend(mf_data)
        print(f"  - Mutual fund portfolios: {len(mf_data)}")
        
        # Insurance
        insurance_data = insurance_gen.generate_for_customer(customer_id, profile)
        all_insurance.extend(insurance_data)
        print(f"  - Insurance policies: {len(insurance_data)}")
        
        # OCEN
        ocen_data = ocen_gen.generate_for_customer(customer_id, profile)
        all_ocen.extend(ocen_data)
        print(f"  - OCEN applications: {len(ocen_data)}")
        
        # ONDC
        ondc_data = ondc_gen.generate_for_customer(customer_id, profile)
        all_ondc.extend(ondc_data)
        print(f"  - ONDC orders: {len(ondc_data)}")
        print()
    
    # Write to files
    output_dir = "raw"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\nWriting data files...")
    
    # GST
    with open(f"{output_dir}/raw_gst.ndjson", "w") as f:
        for record in all_gst:
            f.write(json.dumps(record) + "\n")
    print(f"✓ Written {len(all_gst)} GST returns to raw_gst.ndjson")
    
    # Mutual Funds
    with open(f"{output_dir}/raw_mutual_funds.ndjson", "w") as f:
        for record in all_mf:
            f.write(json.dumps(record) + "\n")
    print(f"✓ Written {len(all_mf)} mutual fund portfolios to raw_mutual_funds.ndjson")
    
    # Insurance
    with open(f"{output_dir}/raw_policies.ndjson", "w") as f:
        for record in all_insurance:
            f.write(json.dumps(record) + "\n")
    print(f"✓ Written {len(all_insurance)} insurance policies to raw_policies.ndjson")
    
    # OCEN
    with open(f"{output_dir}/raw_ocen_applications.ndjson", "w") as f:
        for record in all_ocen:
            f.write(json.dumps(record) + "\n")
    print(f"✓ Written {len(all_ocen)} OCEN applications to raw_ocen_applications.ndjson")
    
    # ONDC
    with open(f"{output_dir}/raw_ondc_orders.ndjson", "w") as f:
        for record in all_ondc:
            f.write(json.dumps(record) + "\n")
    print(f"✓ Written {len(all_ondc)} ONDC orders to raw_ondc_orders.ndjson")
    
    print("\n✅ All profile-aware data generated successfully!")
    print("\n=== Summary ===")
    print(f"Total GST returns: {len(all_gst)}")
    print(f"Total mutual fund portfolios: {len(all_mf)}")
    print(f"Total insurance policies: {len(all_insurance)}")
    print(f"Total OCEN applications: {len(all_ocen)}")
    print(f"Total ONDC orders: {len(all_ondc)}")


if __name__ == "__main__":
    main()
