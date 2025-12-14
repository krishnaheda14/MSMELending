"""
Insurance, Mutual Fund, ONDC, and OCEN data generators.
"""
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generators.indian_data_utils import *


class InsuranceGenerator:
    """Generate insurance policies."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.policy_types = ["LIFE", "HEALTH", "TERM", "ENDOWMENT", "ULIP", "VEHICLE", "HOME", "TRAVEL"]
        self.insurers = ["LIC", "HDFC Life", "ICICI Prudential", "SBI Life", "Max Life", 
                        "Bajaj Allianz", "Star Health", "HDFC Ergo", "ICICI Lombard", 
                        "Tata AIG", "Reliance General"]
    
    def generate(self, user_ids: List[str], num_policies: int) -> List[Dict]:
        """Generate insurance policies."""
        policies = []
        
        for policy_id in range(1, num_policies + 1):
            user_id = random.choice(user_ids)
            policy = self._generate_policy(f"POL{policy_id:08d}", user_id)
            policies.append(policy)
        
        return policies
    
    def _generate_policy(self, policy_id: str, user_id: str) -> Dict:
        """Generate a single insurance policy."""
        policy_type = random.choice(self.policy_types)
        insurer = random.choice(self.insurers)
        
        policy_number = f"{insurer[:3].upper()}/{random.randint(10000, 999999)}/{random.randint(2015, 2024)}"
        
        insured_name = generate_indian_name()
        nominee_name = generate_indian_name()
        
        # Determine sum assured and premium based on policy type
        if policy_type in ["LIFE", "TERM"]:
            sum_assured = random.uniform(500000, 10000000)
            if policy_type == "TERM":
                premium = sum_assured * random.uniform(0.001, 0.005)  # Lower for term
            else:
                premium = sum_assured * random.uniform(0.02, 0.05)
        elif policy_type == "HEALTH":
            sum_assured = random.choice([300000, 500000, 1000000, 1500000, 2000000])
            premium = sum_assured * random.uniform(0.015, 0.035)
        elif policy_type in ["VEHICLE", "HOME"]:
            sum_assured = random.uniform(200000, 3000000)
            premium = sum_assured * random.uniform(0.02, 0.04)
        elif policy_type == "ULIP":
            sum_assured = random.uniform(100000, 5000000)
            premium = random.uniform(12000, 100000)
        else:
            sum_assured = random.uniform(100000, 1000000)
            premium = sum_assured * random.uniform(0.01, 0.03)
        
        premium_frequency = random.choice(["MONTHLY", "QUARTERLY", "HALF_YEARLY", "YEARLY"])
        
        start_date = datetime.now() - timedelta(days=random.randint(30, 3650))
        
        if policy_type in ["LIFE", "ENDOWMENT", "ULIP"]:
            tenure_years = random.choice([10, 15, 20, 25, 30])
        elif policy_type == "TERM":
            tenure_years = random.choice([20, 25, 30, 35])
        elif policy_type == "VEHICLE":
            tenure_years = 1
        else:
            tenure_years = random.choice([1, 2, 3, 5])
        
        end_date = start_date + timedelta(days=tenure_years * 365)
        maturity_date = end_date if policy_type in ["ENDOWMENT", "ULIP"] else None
        
        # Determine status
        if datetime.now() > end_date:
            status = random.choices(["MATURED", "CLAIMED"], weights=[0.8, 0.2])[0]
        elif random.random() < 0.85:
            status = "ACTIVE"
        else:
            status = random.choice(["LAPSED", "SURRENDERED"])
        
        last_premium_date = start_date + timedelta(days=random.randint(0, (datetime.now() - start_date).days))
        
        # Generate claims (2% probability)
        claims = []
        if random.random() < 0.02 or status == "CLAIMED":
            num_claims = random.randint(1, 3)
            for claim_num in range(1, num_claims + 1):
                claim = self._generate_claim(claim_num, start_date, sum_assured)
                claims.append(claim)
        
        # Apply messy formats
        if self.config['messiness_config']['date_format_variation']:
            start_date_str = apply_messy_date_format(start_date)
            end_date_str = apply_messy_date_format(end_date)
            maturity_date_str = apply_messy_date_format(maturity_date) if maturity_date else None
            last_premium_str = apply_messy_date_format(last_premium_date)
        else:
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            maturity_date_str = maturity_date.strftime("%Y-%m-%d") if maturity_date else None
            last_premium_str = last_premium_date.strftime("%Y-%m-%d")
        
        if self.config['messiness_config']['numeric_format_inconsistency']:
            sum_assured_str = apply_messy_amount_format(sum_assured)
            premium_str = apply_messy_amount_format(premium)
        else:
            sum_assured_str = sum_assured
            premium_str = premium
        
        policy = {
            "policy_id": policy_id,
            "user_id": user_id,
            "policy_number": policy_number,
            "policy_type": policy_type,
            "insurer": insurer,
            "insured_name": insured_name,
            "nominee_name": nominee_name,
            "sum_assured": sum_assured_str,
            "premium_amount": premium_str,
            "premium_frequency": premium_frequency,
            "policy_start_date": start_date_str,
            "policy_end_date": end_date_str,
            "maturity_date": maturity_date_str,
            "status": status,
            "last_premium_paid_date": last_premium_str,
            "claims": claims,
            "rider_details": []
        }
        
        # Introduce missing fields
        if self.config['messiness_config']['missing_field_probability'] > 0:
            policy = introduce_missing_fields(
                policy,
                self.config['messiness_config']['missing_field_probability']
            )
        
        return policy
    
    def _generate_claim(self, claim_num: int, policy_start: datetime, sum_assured: float) -> Dict:
        """Generate a claim."""
        claim_date = policy_start + timedelta(days=random.randint(180, 1825))
        claim_amount = sum_assured * random.uniform(0.1, 1.0)
        
        claim_status = random.choices(
            ["PENDING", "APPROVED", "REJECTED", "SETTLED"],
            weights=[0.15, 0.20, 0.15, 0.50]
        )[0]
        
        settlement_date = None
        settlement_amount = None
        
        if claim_status == "SETTLED":
            settlement_date = claim_date + timedelta(days=random.randint(30, 180))
            settlement_amount = claim_amount * random.uniform(0.8, 1.0)
        elif claim_status == "APPROVED":
            settlement_date = claim_date + timedelta(days=random.randint(10, 60))
            settlement_amount = claim_amount
        
        # Apply messy formats
        claim_date_str = apply_messy_date_format(claim_date)
        settlement_date_str = apply_messy_date_format(settlement_date) if settlement_date else None
        
        claim = {
            "claim_id": f"CLM{claim_num:06d}",
            "claim_date": claim_date_str,
            "claim_amount": claim_amount,
            "claim_status": claim_status,
            "settlement_date": settlement_date_str,
            "settlement_amount": settlement_amount,
            "claim_type": random.choice(["HOSPITALIZATION", "ACCIDENT", "MATURITY", "DEATH", "CRITICAL_ILLNESS"])
        }
        
        return claim


class MutualFundGenerator:
    """Generate mutual fund portfolios."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.amcs = ["SBI Mutual Fund", "HDFC Mutual Fund", "ICICI Prudential MF", 
                    "Axis Mutual Fund", "Nippon India MF", "Kotak Mahindra MF", 
                    "UTI Mutual Fund", "DSP Mutual Fund", "Franklin Templeton", 
                    "Aditya Birla Sun Life MF"]
        self.scheme_types = ["EQUITY", "DEBT", "HYBRID", "LIQUID", "INDEX", "ETF"]
    
    def generate(self, user_ids: List[str], num_portfolios: int) -> List[Dict]:
        """Generate mutual fund portfolios."""
        portfolios = []
        
        for portfolio_id in range(1, num_portfolios + 1):
            user_id = random.choice(user_ids)
            portfolio = self._generate_portfolio(f"MF{portfolio_id:08d}", user_id)
            portfolios.append(portfolio)
        
        return portfolios
    
    def _generate_portfolio(self, portfolio_id: str, user_id: str) -> Dict:
        """Generate a mutual fund portfolio."""
        amc = random.choice(self.amcs)
        scheme_type = random.choice(self.scheme_types)
        
        scheme_names = {
            "EQUITY": ["Large Cap Fund", "Mid Cap Fund", "Small Cap Fund", "Multi Cap Fund", "Flexi Cap Fund"],
            "DEBT": ["Corporate Bond Fund", "Gilt Fund", "Liquid Fund", "Short Duration Fund"],
            "HYBRID": ["Balanced Advantage Fund", "Aggressive Hybrid Fund", "Conservative Hybrid Fund"],
            "LIQUID": ["Liquid Fund", "Overnight Fund"],
            "INDEX": ["Nifty 50 Index Fund", "Sensex Index Fund", "Nifty Next 50 Index Fund"],
            "ETF": ["Nifty BeES", "Gold ETF", "Bank BeES"]
        }
        
        scheme_name = f"{amc} - {random.choice(scheme_names[scheme_type])}"
        scheme_code = f"{amc[:3].upper()}{random.randint(100, 999)}"
        
        folio_number = f"{random.randint(10000000, 99999999)}/{random.randint(10, 99)}"
        
        isin = f"INF{random.choice(string.ascii_uppercase)}{random.randint(100000000, 999999999)}"
        
        # Determine investment
        invested_amount = random.uniform(5000, 500000)
        units = random.uniform(100, 10000)
        average_nav = invested_amount / units
        
        # Generate NAV history
        nav_history_days = random.randint(180, 1095)
        nav_history = generate_random_walk_nav(average_nav, nav_history_days)
        
        current_nav = nav_history[-1][1] if nav_history else average_nav
        current_value = units * current_nav
        
        returns_abs = current_value - invested_amount
        returns_pct = (returns_abs / invested_amount) * 100
        
        # SIP details (50% have SIPs)
        sip_details = None
        if random.random() < 0.5:
            sip_details = self._generate_sip()
        
        # Generate transactions
        transactions = self._generate_mf_transactions(units, average_nav, nav_history_days)
        
        # Apply messy formats
        if self.config['messiness_config']['numeric_format_inconsistency']:
            units_str = f"{units:.4f}" if random.random() < 0.5 else f"{units:.2f}"
            current_nav_str = f"{current_nav:.4f}"
            current_value_str = apply_messy_amount_format(current_value)
            invested_str = apply_messy_amount_format(invested_amount)
        else:
            units_str = units
            current_nav_str = current_nav
            current_value_str = current_value
            invested_str = invested_amount
        
        portfolio = {
            "portfolio_id": portfolio_id,
            "user_id": user_id,
            "folio_number": folio_number,
            "amc": amc,
            "scheme_name": scheme_name,
            "scheme_code": scheme_code,
            "isin": isin,
            "scheme_type": scheme_type,
            "units": units_str,
            "current_nav": current_nav_str,
            "current_value": current_value_str,
            "invested_amount": invested_str,
            "average_nav": f"{average_nav:.4f}",
            "returns_abs": returns_abs,
            "returns_pct": returns_pct,
            "sip_details": sip_details,
            "transactions": transactions[:20],  # Limit for size
            "nav_history": nav_history[-90:]  # Last 90 days
        }
        
        # Introduce missing fields
        if self.config['messiness_config']['missing_field_probability'] > 0:
            portfolio = introduce_missing_fields(
                portfolio,
                self.config['messiness_config']['missing_field_probability']
            )
        
        return portfolio
    
    def _generate_sip(self) -> Dict:
        """Generate SIP details."""
        sip_amount = random.choice([500, 1000, 2000, 3000, 5000, 10000, 15000, 20000])
        sip_start = datetime.now() - timedelta(days=random.randint(180, 1095))
        
        # Sometimes SIP is cancelled or completed
        status_weights = [0.70, 0.10, 0.15, 0.05]
        sip_status = random.choices(["ACTIVE", "PAUSED", "CANCELLED", "COMPLETED"], 
                                   weights=status_weights)[0]
        
        if sip_status == "COMPLETED":
            sip_end = sip_start + timedelta(days=random.randint(365, 1095))
        else:
            sip_end = None
        
        sip_details = {
            "sip_id": f"SIP{random.randint(100000, 999999)}",
            "sip_amount": sip_amount,
            "sip_frequency": random.choice(["MONTHLY", "QUARTERLY"]),
            "sip_date": random.randint(1, 28),
            "sip_start_date": sip_start.strftime("%Y-%m-%d"),
            "sip_end_date": sip_end.strftime("%Y-%m-%d") if sip_end else None,
            "sip_status": sip_status
        }
        
        return sip_details
    
    def _generate_mf_transactions(self, total_units: float, avg_nav: float, 
                                  days: int) -> List[Dict]:
        """Generate mutual fund transactions."""
        transactions = []
        num_txns = random.randint(5, 30)
        
        for txn_num in range(1, num_txns + 1):
            txn_date = datetime.now() - timedelta(days=random.randint(0, days))
            txn_type = random.choice(["PURCHASE", "REDEMPTION", "SIP", "DIVIDEND"])
            
            if txn_type in ["PURCHASE", "SIP"]:
                amount = random.uniform(500, 50000)
                nav = avg_nav * random.uniform(0.9, 1.1)
                units = amount / nav
            else:
                units = total_units * random.uniform(0.1, 0.5)
                nav = avg_nav * random.uniform(0.9, 1.1)
                amount = units * nav
            
            txn = {
                "transaction_id": f"MFTXN{txn_num:08d}",
                "transaction_date": txn_date.strftime("%Y-%m-%d"),
                "transaction_type": txn_type,
                "amount": round(amount, 2),
                "units": round(units, 4),
                "nav": round(nav, 4)
            }
            
            transactions.append(txn)
        
        return sorted(transactions, key=lambda x: x['transaction_date'])


def save_ndjson(data: List[Dict], filepath: str):
    """Save data in NDJSON format."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for record in data:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')


def main():
    """Generate insurance and mutual fund data."""    # Seed random with customer_id if provided (for distinct per-customer data)
    customer_id = os.environ.get('CUSTOMER_ID', 'CUST_MSM_00001')
    seed_value = hash(customer_id) % (2**32)
    random.seed(seed_value)
    print(f"  [SEED] Using seed {seed_value} from customer_id={customer_id}")
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    print("Generating insurance and mutual fund datasets...")
    
    # Determine per-customer counts (fallback to legacy keys)
    num_policies = config.get('scale', {}).get('insurance_policies_per_customer', config.get('scale', {}).get('insurance_policies', 15))
    num_portfolios = config.get('scale', {}).get('mutual_fund_portfolios_per_customer', config.get('scale', {}).get('mutual_fund_portfolios', 3))

    # Use a per-customer user list (single synthetic user per customer to keep linkage simple)
    user_ids = [f"USER_{customer_id}"]

    # Generate Insurance policies
    print("[1/2] Generating insurance policies...")
    insurance_gen = InsuranceGenerator(config)
    policies = insurance_gen.generate(user_ids, num_policies)
    # Attach customer_id to policies
    for p in policies:
        p['customer_id'] = customer_id
    save_ndjson(policies, 'raw/raw_policies.ndjson')
    print(f"  Generated {len(policies)} insurance policies")

    # Generate Mutual Fund portfolios
    print("[2/2] Generating mutual fund portfolios...")
    mf_gen = MutualFundGenerator(config)
    portfolios = mf_gen.generate(user_ids, num_portfolios)
    for pf in portfolios:
        pf['customer_id'] = customer_id
    save_ndjson(portfolios, 'raw/raw_mutual_funds.ndjson')
    print(f"  Generated {len(portfolios)} mutual fund portfolios")
    
    print("\nInsurance and MF data generation completed!")


if __name__ == "__main__":
    main()
