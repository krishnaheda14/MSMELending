"""
GST, Credit Bureau, Insurance, Mutual Fund, ONDC, and OCEN data generators.
"""
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generators.indian_data_utils import *


class GSTGenerator:
    """Generate GST returns."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.return_types = ["GSTR1", "GSTR3B"]
    
    def generate(self, num_profiles: int) -> List[Dict]:
        """Generate GST returns."""
        gst_returns = []
        
        for profile_id in range(1, num_profiles + 1):
            gstin = generate_gstin()
            trade_name = f"{random.choice(['M/s', 'Shri', ''])} {generate_indian_name()} {random.choice(['Traders', 'Enterprises', 'Industries', 'Services', 'Solutions', 'Pvt Ltd'])}"
            
            # Generate returns for last 24 months
            end_date = datetime.now()
            start_date = end_date - timedelta(days=730)
            
            current_date = start_date
            while current_date < end_date:
                for return_type in self.return_types:
                    gst_return = self._generate_return(
                        f"GSTR{profile_id:06d}_{current_date.strftime('%m%Y')}_{return_type}",
                        gstin,
                        trade_name,
                        current_date,
                        return_type
                    )
                    gst_returns.append(gst_return)
                
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        
        return gst_returns
    
    def _generate_return(self, return_id: str, gstin: str, trade_name: str,
                        period_date: datetime, return_type: str) -> Dict:
        """Generate a single GST return."""
        return_period = period_date.strftime("%m-%Y")
        
        # Determine filing status
        filing_status_weights = [0.70, 0.15, 0.10, 0.05]
        status = random.choices(["FILED", "NOT_FILED", "LATE_FILED", "REVISED"],
                               weights=filing_status_weights)[0]
        
        # Filing date
        if status in ["FILED", "REVISED"]:
            # Normal filing within 20 days of next month
            filing_date = period_date + timedelta(days=random.randint(35, 50))
        elif status == "LATE_FILED":
            filing_date = period_date + timedelta(days=random.randint(60, 180))
        else:
            filing_date = None
        
        # Determine business size
        business_type = random.choices(
            ["micro", "small", "medium"],
            weights=[0.50, 0.35, 0.15]
        )[0]
        
        turnover_range = self.config['distributions']['gst_turnover'][business_type]
        monthly_turnover = random.uniform(*turnover_range)
        
        # Add seasonality
        month = period_date.month
        if month in [10, 11, 12]:  # Festive season
            monthly_turnover *= random.uniform(1.1, 1.4)
        elif month in [6, 7]:  # Mid-year
            monthly_turnover *= random.uniform(0.8, 0.95)
        
        # Generate invoices
        num_invoices = max(1, int(monthly_turnover / random.uniform(10000, 50000)))
        num_invoices = min(num_invoices, 200)  # Cap for performance
        
        invoices = []
        total_taxable = 0
        total_igst = 0
        total_cgst = 0
        total_sgst = 0
        
        for inv_num in range(1, num_invoices + 1):
            invoice = self._generate_invoice(
                f"INV/{period_date.strftime('%Y%m')}/{inv_num:04d}",
                period_date,
                gstin
            )
            invoices.append(invoice)
            
            # Sum up values
            try:
                taxable = float(str(invoice['taxable_value']).replace(',', ''))
                total_taxable += taxable
                total_igst += float(str(invoice.get('igst', 0)).replace(',', ''))
                total_cgst += float(str(invoice.get('cgst', 0)).replace(',', ''))
                total_sgst += float(str(invoice.get('sgst', 0)).replace(',', ''))
            except:
                pass
        
        # Apply messy formats
        if self.config['messiness_config']['numeric_format_inconsistency']:
            total_taxable_str = apply_messy_amount_format(total_taxable)
            total_igst_str = apply_messy_amount_format(total_igst)
            total_cgst_str = apply_messy_amount_format(total_cgst)
            total_sgst_str = apply_messy_amount_format(total_sgst)
        else:
            total_taxable_str = total_taxable
            total_igst_str = total_igst
            total_cgst_str = total_cgst
            total_sgst_str = total_sgst
        
        filing_date_str = None
        if filing_date:
            if self.config['messiness_config']['date_format_variation']:
                filing_date_str = apply_messy_date_format(filing_date)
            else:
                filing_date_str = filing_date.strftime("%Y-%m-%d")
        
        itc_claimed = total_igst * random.uniform(0.05, 0.15)
        net_tax = (total_igst + total_cgst + total_sgst) - itc_claimed
        
        gst_return = {
            "return_id": return_id,
            "gstin": gstin,
            "trade_name": trade_name,
            "legal_name": trade_name,
            "return_period": return_period,
            "return_type": return_type,
            "filing_date": filing_date_str,
            "status": status,
            "total_taxable_value": total_taxable_str,
            "total_igst": total_igst_str,
            "total_cgst": total_cgst_str,
            "total_sgst": total_sgst_str,
            "total_cess": 0,
            "invoices": invoices if return_type == "GSTR1" else [],
            "itc_claimed": apply_messy_amount_format(itc_claimed) if random.random() < 0.7 else None,
            "itc_reversed": 0,
            "net_tax_liability": apply_messy_amount_format(net_tax) if random.random() < 0.7 else None
        }
        
        # Introduce missing fields
        if self.config['messiness_config']['missing_field_probability'] > 0:
            gst_return = introduce_missing_fields(
                gst_return,
                self.config['messiness_config']['missing_field_probability']
            )
        
        return gst_return
    
    def _generate_invoice(self, invoice_number: str, period_date: datetime,
                         seller_gstin: str) -> Dict:
        """Generate a single invoice."""
        invoice_date = period_date + timedelta(days=random.randint(1, 28))
        
        # Invoice value
        invoice_value = random.uniform(5000, 500000)
        
        # Determine inter/intra state
        is_interstate = random.random() < 0.3
        
        hsn_code = generate_hsn_code()
        gst_rate = generate_gst_rate()
        
        taxable_value = invoice_value / (1 + gst_rate / 100)
        
        if is_interstate:
            igst = taxable_value * gst_rate / 100
            cgst = 0
            sgst = 0
        else:
            igst = 0
            cgst = taxable_value * gst_rate / 200
            sgst = taxable_value * gst_rate / 200
        
        # Buyer GSTIN (sometimes missing)
        buyer_gstin = generate_gstin() if random.random() < 0.7 else None
        
        # Apply messy formats
        if self.config['messiness_config']['date_format_variation']:
            invoice_date_str = apply_messy_date_format(invoice_date)
        else:
            invoice_date_str = invoice_date.strftime("%Y-%m-%d")
        
        if self.config['messiness_config']['numeric_format_inconsistency']:
            invoice_value_str = apply_messy_amount_format(invoice_value)
            taxable_value_str = apply_messy_amount_format(taxable_value)
            igst_str = apply_messy_amount_format(igst)
            cgst_str = apply_messy_amount_format(cgst)
            sgst_str = apply_messy_amount_format(sgst)
        else:
            invoice_value_str = invoice_value
            taxable_value_str = taxable_value
            igst_str = igst
            cgst_str = cgst
            sgst_str = sgst
        
        # HSN code sometimes missing or malformed
        if random.random() < 0.2:
            hsn_code = None
        
        invoice = {
            "invoice_number": invoice_number,
            "invoice_date": invoice_date_str,
            "invoice_value": invoice_value_str,
            "taxable_value": taxable_value_str,
            "igst": igst_str,
            "cgst": cgst_str,
            "sgst": sgst_str,
            "buyer_gstin": buyer_gstin,
            "buyer_name": generate_indian_name() + " " + random.choice(["Traders", "Enterprises", "Services"]) if buyer_gstin else None,
            "place_of_supply": random.choice(INDIAN_CITIES),
            "reverse_charge": "N",
            "hsn_code": hsn_code,
            "gst_rate": gst_rate
        }
        
        return invoice


class CreditBureauGenerator:
    """Generate credit bureau reports."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.bureaus = ["CIBIL", "EXPERIAN", "EQUIFAX", "CRIF"]
        self.account_types = ["PERSONAL_LOAN", "HOME_LOAN", "AUTO_LOAN", "CREDIT_CARD", 
                             "OVERDRAFT", "LOAN_AGAINST_PROPERTY", "GOLD_LOAN", 
                             "EDUCATION_LOAN", "TWO_WHEELER_LOAN", "BUSINESS_LOAN"]
    
    def generate(self, user_ids: List[str]) -> List[Dict]:
        """Generate credit bureau reports for users."""
        reports = []
        
        for user_id in user_ids:
            # Each user gets 1 report
            if random.random() < 0.85:  # 85% of users have credit history
                report = self._generate_report(user_id)
                reports.append(report)
        
        return reports
    
    def _generate_report(self, user_id: str) -> Dict:
        """Generate a single credit bureau report."""
        report_id = f"CBR{user_id[4:]}"
        
        report_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        # Generate credit score
        credit_score = generate_credit_score(self.config['distributions']['credit_score'])
        
        name = generate_indian_name()
        pan = mask_pan(generate_pan()) if random.random() < 0.7 else None
        
        # Generate accounts based on credit score
        if credit_score >= 750:
            num_accounts = random.randint(3, 8)
        elif credit_score >= 650:
            num_accounts = random.randint(2, 6)
        elif credit_score >= 550:
            num_accounts = random.randint(1, 4)
        else:
            num_accounts = random.randint(0, 3)
        
        accounts = []
        total_credit_limit = 0
        total_outstanding = 0
        total_overdue = 0
        active_count = 0
        
        for _ in range(num_accounts):
            account = self._generate_credit_account(credit_score)
            accounts.append(account)
            
            if account['status'] == 'ACTIVE':
                active_count += 1
            
            try:
                if account.get('credit_limit'):
                    total_credit_limit += float(str(account['credit_limit']).replace(',', ''))
                if account.get('current_balance'):
                    total_outstanding += float(str(account['current_balance']).replace(',', ''))
                if account.get('amount_overdue'):
                    total_overdue += float(str(account['amount_overdue']).replace(',', ''))
            except:
                pass
        
        # Generate enquiries
        num_enquiries = random.randint(0, 15)
        enquiries = []
        for _ in range(num_enquiries):
            enquiry = self._generate_enquiry()
            enquiries.append(enquiry)
        
        enquiries_30 = len([e for e in enquiries if 
                           (datetime.now() - datetime.fromisoformat(e['enquiry_date'])).days <= 30])
        enquiries_90 = len([e for e in enquiries if 
                           (datetime.now() - datetime.fromisoformat(e['enquiry_date'])).days <= 90])
        
        # Apply messy date format
        if self.config['messiness_config']['date_format_variation']:
            report_date_str = apply_messy_date_format(report_date)
        else:
            report_date_str = report_date.strftime("%Y-%m-%d")
        
        dob = datetime.now() - timedelta(days=random.randint(18*365, 65*365))
        dob_str = apply_messy_date_format(dob) if random.random() < 0.5 else dob.strftime("%Y-%m-%d")
        
        report = {
            "report_id": report_id,
            "user_id": user_id,
            "bureau_type": random.choice(self.bureaus),
            "report_date": report_date_str,
            "credit_score": credit_score,
            "pan": pan,
            "name": name,
            "dob": dob_str,
            "gender": random.choice(["M", "F"]),
            "address": generate_indian_address(),
            "accounts": accounts,
            "enquiries": enquiries,
            "total_accounts": len(accounts),
            "active_accounts": active_count,
            "total_credit_limit": total_credit_limit if random.random() < 0.8 else None,
            "total_outstanding": total_outstanding if random.random() < 0.8 else None,
            "total_overdue": total_overdue if total_overdue > 0 and random.random() < 0.8 else None,
            "enquiries_last_30_days": enquiries_30,
            "enquiries_last_90_days": enquiries_90
        }
        
        # Introduce missing fields
        if self.config['messiness_config']['missing_field_probability'] > 0:
            report = introduce_missing_fields(
                report,
                self.config['messiness_config']['missing_field_probability'] * 0.5  # Less aggressive for critical data
            )
        
        return report
    
    def _generate_credit_account(self, credit_score: int) -> Dict:
        """Generate a credit account."""
        account_type = random.choice(self.account_types)
        
        # Determine credit limit based on account type
        if account_type == "CREDIT_CARD":
            credit_limit = random.uniform(20000, 500000)
            current_balance = credit_limit * random.uniform(0, 0.8)
        elif account_type == "PERSONAL_LOAN":
            credit_limit = random.uniform(50000, 1000000)
            current_balance = credit_limit * random.uniform(0.1, 0.9)
        elif account_type == "HOME_LOAN":
            credit_limit = random.uniform(500000, 10000000)
            current_balance = credit_limit * random.uniform(0.3, 0.95)
        elif account_type == "AUTO_LOAN":
            credit_limit = random.uniform(200000, 2000000)
            current_balance = credit_limit * random.uniform(0.2, 0.85)
        else:
            credit_limit = random.uniform(50000, 500000)
            current_balance = credit_limit * random.uniform(0.1, 0.8)
        
        opened_date = datetime.now() - timedelta(days=random.randint(180, 3650))
        
        # Determine status
        if credit_score >= 700:
            status = random.choices(["ACTIVE", "CLOSED"], weights=[0.8, 0.2])[0]
        else:
            status = random.choices(["ACTIVE", "CLOSED", "WRITTEN_OFF", "SETTLED"], 
                                   weights=[0.6, 0.25, 0.10, 0.05])[0]
        
        # Generate DPD string
        dpd_string = generate_dpd_string()
        
        # Determine overdue
        if status == "ACTIVE" and credit_score < 650:
            amount_overdue = current_balance * random.uniform(0, 0.3)
        else:
            amount_overdue = 0
        
        closed_date = None
        if status in ["CLOSED", "WRITTEN_OFF", "SETTLED"]:
            closed_date = opened_date + timedelta(days=random.randint(180, 1825))
        
        # Apply messy formats
        if self.config['messiness_config']['date_format_variation']:
            opened_date_str = apply_messy_date_format(opened_date)
            closed_date_str = apply_messy_date_format(closed_date) if closed_date else None
        else:
            opened_date_str = opened_date.strftime("%Y-%m-%d")
            closed_date_str = closed_date.strftime("%Y-%m-%d") if closed_date else None
        
        account = {
            "account_number": f"XXXX{random.randint(1000, 9999)}",
            "account_type": account_type,
            "ownership": random.choice(["INDIVIDUAL", "JOINT", "GUARANTOR"]),
            "date_opened": opened_date_str,
            "date_closed": closed_date_str,
            "credit_limit": credit_limit,
            "current_balance": current_balance if status == "ACTIVE" else 0,
            "amount_overdue": amount_overdue,
            "dpd_string": dpd_string,
            "write_off_amount": current_balance if status == "WRITTEN_OFF" else None,
            "settlement_amount": current_balance * 0.6 if status == "SETTLED" else None,
            "status": status,
            "lender_name": random.choice(["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank", 
                                         "Kotak Mahindra", "Bajaj Finance", "Tata Capital"])
        }
        
        return account
    
    def _generate_enquiry(self) -> Dict:
        """Generate a credit enquiry."""
        enquiry_date = datetime.now() - timedelta(days=random.randint(0, 730))
        
        purposes = ["Personal Loan", "Credit Card", "Home Loan", "Auto Loan", 
                   "Business Loan", "Two Wheeler Loan"]
        
        enquiry = {
            "enquiry_date": enquiry_date.strftime("%Y-%m-%d"),
            "enquiry_purpose": random.choice(purposes),
            "lender_name": random.choice(["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank", 
                                         "Kotak Mahindra", "Bajaj Finance"]),
            "amount": random.uniform(50000, 1000000) if random.random() < 0.7 else None
        }
        
        return enquiry


def save_ndjson(data: List[Dict], filepath: str):
    """Save data in NDJSON format."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for record in data:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')


def main():
    """Generate additional datasets."""
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    print("Generating additional datasets...")
    
    # Generate user IDs
    user_ids = [f"USER{i:08d}" for i in range(1, config['scale']['users'] + 1)]
    
    # Generate GST data
    print("[1/3] Generating GST returns...")
    gst_gen = GSTGenerator(config)
    gst_returns = gst_gen.generate(config['scale']['gst_profiles'])
    save_ndjson(gst_returns, 'raw/raw_gst.ndjson')
    print(f"  Generated {len(gst_returns)} GST returns")
    
    # Generate Credit Bureau reports
    print("[2/3] Generating credit bureau reports...")
    bureau_gen = CreditBureauGenerator(config)
    reports = bureau_gen.generate(user_ids)
    save_ndjson(reports, 'raw/raw_credit_reports.ndjson')
    print(f"  Generated {len(reports)} credit reports")
    
    print("\nAdditional data generation completed!")


if __name__ == "__main__":
    main()
