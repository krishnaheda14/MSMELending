"""
ONDC and OCEN data generators.
"""
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generators.indian_data_utils import *


class ONDCGenerator:
    """Generate ONDC orders in Beckn format."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.domains = ["nic2004:52110", "nic2004:60221", "nic2004:52112"]  # Retail, Transport, F&B
        self.actions = ["search", "select", "init", "confirm", "status", "track", "cancel", "update"]
        self.providers = ["Swiggy", "Zomato", "Dunzo", "BigBasket", "DMart Ready", "Flipkart Quick"]
        self.items_catalog = [
            {"name": "Rice (5kg)", "category": "Groceries", "price": 250},
            {"name": "Dal (1kg)", "category": "Groceries", "price": 120},
            {"name": "Milk (1L)", "category": "Dairy", "price": 60},
            {"name": "Bread", "category": "Bakery", "price": 40},
            {"name": "Chicken Biryani", "category": "Food", "price": 280},
            {"name": "Paneer Butter Masala", "category": "Food", "price": 220},
            {"name": "Dosa", "category": "Food", "price": 80},
            {"name": "Coffee", "category": "Beverages", "price": 50},
            {"name": "Pizza", "category": "Food", "price": 350},
            {"name": "Burger", "category": "Food", "price": 150},
            {"name": "Vegetables Mix", "category": "Fresh Produce", "price": 180},
            {"name": "Fruits Basket", "category": "Fresh Produce", "price": 300},
            {"name": "Detergent", "category": "Household", "price": 180},
            {"name": "Shampoo", "category": "Personal Care", "price": 250},
        ]
    
    def generate(self, user_ids: List[str], num_orders: int) -> List[Dict]:
        """Generate ONDC orders."""
        orders = []
        
        for order_id in range(1, num_orders + 1):
            user_id = random.choice(user_ids)
            order = self._generate_order(f"ONDC{order_id:08d}", user_id)
            orders.append(order)
        
        return orders
    
    def _generate_order(self, order_id: str, user_id: str) -> Dict:
        """Generate a single ONDC order."""
        transaction_id = f"TXN{random.randint(10000000, 99999999)}"
        
        provider_name = random.choice(self.providers)
        provider_id = f"PROV{random.randint(1000, 9999)}"
        
        # Generate context
        context = {
            "domain": random.choice(self.domains),
            "country": "IND",
            "city": random.choice(INDIAN_CITIES[:10]),
            "action": "confirm",  # Most orders reach confirm
            "core_version": "1.0.0",
            "bap_id": f"BAP{random.randint(100, 999)}",
            "bap_uri": f"https://bap{random.randint(100, 999)}.ondc.in",
            "bpp_id": f"BPP{random.randint(100, 999)}",
            "bpp_uri": f"https://bpp{random.randint(100, 999)}.ondc.in",
            "timestamp": (datetime.now() - timedelta(days=random.randint(0, 90))).isoformat()
        }
        
        # Generate items
        num_items = random.randint(1, 6)
        items = []
        total_price = 0
        
        for _ in range(num_items):
            item_template = random.choice(self.items_catalog)
            quantity = random.randint(1, 5)
            item_price = item_template['price'] * quantity
            total_price += item_price
            
            items.append({
                "id": f"ITEM{random.randint(1000, 9999)}",
                "name": item_template['name'],
                "category": item_template['category'],
                "quantity": quantity,
                "price": item_price
            })
        
        # Delivery charges
        delivery_charge = random.uniform(0, 80)
        platform_fee = random.uniform(2, 10)
        total_price += delivery_charge + platform_fee
        
        # Billing
        user_name = generate_indian_name()
        billing = {
            "name": user_name,
            "address": generate_indian_address(),
            "phone": generate_mobile_number(),
            "email": generate_email(user_name) if random.random() < 0.6 else None
        }
        
        # Fulfillment
        fulfillment_type = random.choice(["HOME_DELIVERY", "PICKUP", "DIGITAL"])
        fulfillment_states = ["PENDING", "PACKED", "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED", "RTO"]
        fulfillment_weights = [0.05, 0.08, 0.12, 0.65, 0.08, 0.02]
        fulfillment_state = random.choices(fulfillment_states, weights=fulfillment_weights)[0]
        
        fulfillment = {
            "type": fulfillment_type,
            "state": fulfillment_state,
            "tracking": random.choice([True, False]),
            "start": {
                "location": billing['address'],
                "time": context['timestamp']
            },
            "end": {
                "location": billing['address'],
                "time": (datetime.fromisoformat(context['timestamp']) + 
                        timedelta(hours=random.randint(1, 48))).isoformat()
            }
        }
        
        # Quote with breakup
        quote = {
            "price": total_price,
            "breakup": [
                {"title": "Item Total", "price": total_price - delivery_charge - platform_fee},
                {"title": "Delivery Charges", "price": delivery_charge},
                {"title": "Platform Fee", "price": platform_fee}
            ]
        }
        
        # Payment
        payment_type = random.choices(["PRE_PAID", "POST_PAID", "COD"], weights=[0.60, 0.10, 0.30])[0]
        
        if fulfillment_state == "DELIVERED":
            payment_status = "PAID"
        elif fulfillment_state in ["CANCELLED", "RTO"]:
            payment_status = random.choice(["REFUNDED", "PAID", "NOT_PAID"])
        else:
            payment_status = "PAID" if payment_type == "PRE_PAID" else "NOT_PAID"
        
        payment = {
            "type": payment_type,
            "status": payment_status,
            "params": {
                "transaction_id": f"PAY{random.randint(100000, 999999)}",
                "amount": total_price
            }
        }
        
        # Order state
        if fulfillment_state == "DELIVERED":
            order_state = "COMPLETED"
        elif fulfillment_state in ["CANCELLED", "RTO"]:
            order_state = "CANCELLED"
        elif fulfillment_state in ["PENDING", "PACKED"]:
            order_state = "ACCEPTED"
        else:
            order_state = "IN_PROGRESS"
        
        created_at = datetime.fromisoformat(context['timestamp'])
        updated_at = created_at + timedelta(hours=random.randint(1, 72))
        
        # Apply messy date formats
        if self.config['messiness_config']['date_format_variation']:
            created_at_str = apply_messy_date_format(created_at)
            updated_at_str = apply_messy_date_format(updated_at)
        else:
            created_at_str = created_at.isoformat()
            updated_at_str = updated_at.isoformat()
        
        order = {
            "order_id": order_id,
            "transaction_id": transaction_id,
            "user_id": user_id,
            "context": context,
            "provider": {
                "id": provider_id,
                "name": provider_name,
                "descriptor": {}
            },
            "items": items,
            "billing": billing,
            "fulfillment": fulfillment,
            "quote": quote,
            "payment": payment,
            "created_at": created_at_str,
            "updated_at": updated_at_str,
            "state": order_state
        }
        
        # Introduce missing fields
        if self.config['messiness_config']['missing_field_probability'] > 0:
            order = introduce_missing_fields(
                order,
                self.config['messiness_config']['missing_field_probability'] * 0.3
            )
        
        return order


class OCENGenerator:
    """Generate OCEN loan applications."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.loan_purposes = ["WORKING_CAPITAL", "BUSINESS_EXPANSION", "EQUIPMENT_PURCHASE", 
                             "INVENTORY", "INVOICE_FINANCING", "TERM_LOAN", "OVERDRAFT"]
        self.lenders = ["HDFC Bank", "ICICI Bank", "Axis Bank", "Bajaj Finance", 
                       "Tata Capital", "L&T Finance", "Lendingkart", "Indifi", 
                       "Capital Float", "NeoGrowth"]
    
    def generate(self, user_ids: List[str], num_applications: int) -> List[Dict]:
        """Generate OCEN loan applications."""
        applications = []
        
        for app_id in range(1, num_applications + 1):
            user_id = random.choice(user_ids)
            application = self._generate_application(f"OCEN{app_id:08d}", user_id)
            applications.append(application)
        
        return applications
    
    def _generate_application(self, application_id: str, user_id: str) -> Dict:
        """Generate a single loan application."""
        lender_id = f"LDR{random.randint(1000, 9999)}"
        lsp_id = f"LSP{random.randint(100, 999)}" if random.random() < 0.7 else None
        
        loan_purpose = random.choice(self.loan_purposes)
        
        # Requested amount based on purpose
        if loan_purpose in ["WORKING_CAPITAL", "INVENTORY"]:
            requested_amount = random.uniform(50000, 2000000)
        elif loan_purpose in ["EQUIPMENT_PURCHASE", "BUSINESS_EXPANSION"]:
            requested_amount = random.uniform(200000, 5000000)
        elif loan_purpose == "INVOICE_FINANCING":
            requested_amount = random.uniform(100000, 1000000)
        else:
            requested_amount = random.uniform(100000, 3000000)
        
        application_date = datetime.now() - timedelta(days=random.randint(0, 180))
        
        # Application status
        status_weights = [0.05, 0.20, 0.10, 0.25, 0.25, 0.10, 0.05]
        status = random.choices(
            ["DRAFT", "SUBMITTED", "UNDER_REVIEW", "APPROVED", "REJECTED", "DISBURSED", "WITHDRAWN"],
            weights=status_weights
        )[0]
        
        # Approved/disbursed amounts
        approved_amount = None
        interest_rate = None
        tenure_months = None
        
        if status in ["APPROVED", "DISBURSED"]:
            approved_amount = requested_amount * random.uniform(0.7, 1.0)
            interest_rate = random.uniform(10, 24)
            tenure_months = random.choice([6, 12, 18, 24, 36, 48, 60])
        
        rejection_reason = None
        if status == "REJECTED":
            rejection_reasons = [
                "Insufficient credit score",
                "Inadequate business vintage",
                "High existing debt burden",
                "Irregular GST filing",
                "Negative banking behavior",
                "Incomplete documentation"
            ]
            rejection_reason = random.choice(rejection_reasons)
        
        # Business details
        business_name = f"{random.choice(['M/s', 'Shri', ''])} {generate_indian_name()} {random.choice(['Traders', 'Enterprises', 'Industries', 'Services', 'Solutions'])}"
        business_type = random.choice(["PROPRIETORSHIP", "PARTNERSHIP", "PRIVATE_LIMITED", "LLP"])
        
        gstin = generate_gstin() if random.random() < 0.8 else None
        pan = mask_pan(generate_pan()) if random.random() < 0.9 else None
        
        vintage_months = random.randint(6, 120)
        annual_revenue = random.uniform(500000, 50000000)
        monthly_avg_revenue = annual_revenue / 12
        
        business_details = {
            "business_name": business_name,
            "business_type": business_type,
            "gstin": gstin,
            "pan": pan,
            "vintage_months": vintage_months,
            "annual_revenue": annual_revenue,
            "monthly_avg_revenue": monthly_avg_revenue
        }
        
        # Scoring features
        if status in ["APPROVED", "REJECTED", "DISBURSED"]:
            credit_score = generate_credit_score(self.config['distributions']['credit_score'])
            gst_score = random.uniform(400, 850)
            banking_score = random.uniform(350, 900)
            bureau_score = credit_score
            
            # Calculate final score (weighted average)
            final_score = (
                credit_score * 0.35 +
                gst_score * 0.25 +
                banking_score * 0.25 +
                bureau_score * 0.15
            )
            
            if final_score >= 750:
                risk_category = "LOW"
            elif final_score >= 650:
                risk_category = "MEDIUM"
            elif final_score >= 550:
                risk_category = "HIGH"
            else:
                risk_category = "VERY_HIGH"
            
            scoring_features = {
                "credit_score": credit_score,
                "gst_score": round(gst_score, 2),
                "banking_score": round(banking_score, 2),
                "bureau_score": bureau_score,
                "final_score": round(final_score, 2),
                "risk_category": risk_category
            }
        else:
            scoring_features = None
        
        # Consent IDs
        consent_ids = [f"CONSENT{random.randint(10000, 99999)}" for _ in range(random.randint(1, 4))]
        
        # Documents
        documents = []
        doc_types = ["PAN", "GST_CERTIFICATE", "BANK_STATEMENT", "ITR", "BUSINESS_PROOF", "ADDRESS_PROOF"]
        for doc_type in random.sample(doc_types, random.randint(3, 6)):
            documents.append({
                "document_type": doc_type,
                "document_id": f"DOC{random.randint(10000, 99999)}",
                "verified": random.choice([True, False, None])
            })
        
        # Disbursement details
        disbursement_date = None
        disbursement_account = None
        
        if status == "DISBURSED":
            disbursement_date = application_date + timedelta(days=random.randint(7, 45))
            disbursement_account = generate_account_number(random.choice(self.config['banks']))
        
        # Apply messy formats
        if self.config['messiness_config']['date_format_variation']:
            app_date_str = apply_messy_date_format(application_date)
            disb_date_str = apply_messy_date_format(disbursement_date) if disbursement_date else None
        else:
            app_date_str = application_date.strftime("%Y-%m-%d")
            disb_date_str = disbursement_date.strftime("%Y-%m-%d") if disbursement_date else None
        
        if self.config['messiness_config']['numeric_format_inconsistency']:
            requested_str = apply_messy_amount_format(requested_amount)
            approved_str = apply_messy_amount_format(approved_amount) if approved_amount else None
        else:
            requested_str = requested_amount
            approved_str = approved_amount
        
        application = {
            "application_id": application_id,
            "user_id": user_id,
            "lender_id": lender_id,
            "lsp_id": lsp_id,
            "loan_purpose": loan_purpose,
            "requested_amount": requested_str,
            "approved_amount": approved_str,
            "interest_rate": round(interest_rate, 2) if interest_rate else None,
            "tenure_months": tenure_months,
            "application_date": app_date_str,
            "status": status,
            "rejection_reason": rejection_reason,
            "business_details": business_details,
            "scoring_features": scoring_features,
            "consent_ids": consent_ids,
            "documents": documents,
            "disbursement_date": disb_date_str,
            "disbursement_account": disbursement_account
        }
        
        # Introduce missing fields
        if self.config['messiness_config']['missing_field_probability'] > 0:
            application = introduce_missing_fields(
                application,
                self.config['messiness_config']['missing_field_probability'] * 0.4
            )
        
        return application


def save_ndjson(data: List[Dict], filepath: str):
    """Save data in NDJSON format."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for record in data:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')


def main():
    """Generate ONDC and OCEN data."""
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    print("Generating ONDC and OCEN datasets...")
    
    # Generate user IDs
    user_ids = [f"USER{i:08d}" for i in range(1, config['scale']['users'] + 1)]
    
    # Generate ONDC orders
    print("[1/2] Generating ONDC orders...")
    ondc_gen = ONDCGenerator(config)
    orders = ondc_gen.generate(user_ids, config['scale']['ondc_orders'])
    save_ndjson(orders, 'raw/raw_ondc_orders.ndjson')
    print(f"  Generated {len(orders)} ONDC orders")
    
    # Generate OCEN applications
    print("[2/2] Generating OCEN loan applications...")
    ocen_gen = OCENGenerator(config)
    applications = ocen_gen.generate(user_ids, config['scale']['ocen_applications'])
    save_ndjson(applications, 'raw/raw_ocen_applications.ndjson')
    print(f"  Generated {len(applications)} OCEN loan applications")
    
    print("\nONDC and OCEN data generation completed!")


if __name__ == "__main__":
    main()
