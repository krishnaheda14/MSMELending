"""
Utility module for generating realistic Indian financial data patterns.
"""
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import re

# Indian bank IFSCs (samples)
BANK_IFSC_PREFIXES = {
    "HDFC": ["HDFC0", "HDFC1", "HDFC2"],
    "ICICI": ["ICIC0", "ICIC1"],
    "SBI": ["SBIN0", "SBIN1"],
    "AXIS": ["UTIB0", "UTIB1"],
    "KOTAK": ["KKBK0"],
    "IDFC_FIRST": ["IDFB0"],
    "YES_BANK": ["YESB0"]
}

# Indian cities for addresses
INDIAN_CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata",
    "Pune", "Ahmedabad", "Jaipur", "Surat", "Lucknow", "Kanpur",
    "Nagpur", "Indore", "Thane", "Bhopal", "Visakhapatnam", "Patna",
    "Vadodara", "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad",
    "Meerut", "Rajkot", "Varanasi", "Srinagar", "Amritsar", "Coimbatore"
]

# Indian first names
INDIAN_FIRST_NAMES = [
    "Rajesh", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Rahul", "Pooja",
    "Suresh", "Deepika", "Arjun", "Kavita", "Rohan", "Neha", "Sanjay", "Ritu",
    "Karthik", "Divya", "Anil", "Meera", "Manoj", "Shruti", "Aditya", "Preeti",
    "Vivek", "Swati", "Nikhil", "Anita", "Ashok", "Sunita", "Ramesh", "Lakshmi",
    "Varun", "Nisha", "Prakash", "Shilpa", "Gaurav", "Pallavi", "Harish", "Rekha"
]

INDIAN_LAST_NAMES = [
    "Sharma", "Kumar", "Singh", "Patel", "Desai", "Reddy", "Nair", "Iyer",
    "Verma", "Gupta", "Joshi", "Rao", "Menon", "Kulkarni", "Agarwal", "Mehta",
    "Shah", "Malhotra", "Chopra", "Kapoor", "Pandey", "Mishra", "Banerjee", "Das",
    "Ghosh", "Chatterjee", "Saxena", "Sinha", "Khan", "Ali", "Ahmed", "Hussain"
]

# Merchant names for transactions
MERCHANT_NAMES = [
    "Amazon", "Flipkart", "Swiggy", "Zomato", "BigBasket", "Reliance Digital",
    "DMart", "More Supermarket", "Spencer's", "Big Bazaar", "Myntra", "Ajio",
    "BookMyShow", "PVR Cinemas", "INOX", "OLA", "Uber", "Rapido",
    "Apollo Pharmacy", "MedPlus", "Tanishq", "PC Jeweller", "Decathlon",
    "Croma", "Vijay Sales", "Blinkit", "Dunzo", "UrbanClap", "Lenskart",
    "FirstCry", "Nykaa", "Pharmeasy", "1mg", "MakeMyTrip", "Goibibo",
    "RedBus", "IRCTC", "Paytm Mall", "JioMart"
]


def generate_pan() -> str:
    """Generate a valid PAN number format."""
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    category = random.choice(['P', 'C', 'H', 'F', 'A', 'T', 'B', 'L', 'J', 'G'])
    letter = random.choice(string.ascii_uppercase)
    digits = ''.join(random.choices(string.digits, k=4))
    check = random.choice(string.ascii_uppercase)
    return f"{letters}{category}{letter}{digits}{check}"


def mask_pan(pan: str) -> str:
    """Mask middle digits of PAN."""
    if len(pan) != 10:
        return pan
    return f"{pan[:5]}XXXX{pan[9]}"


def generate_gstin(state_code: int = None) -> str:
    """Generate a valid GSTIN format."""
    if state_code is None:
        state_code = random.randint(1, 37)
    
    state = f"{state_code:02d}"
    pan = generate_pan()
    entity = random.choice(['1', '2', '3', '4', '5'])
    zone = 'Z'
    checksum = random.choice(string.ascii_uppercase + string.digits)
    
    return f"{state}{pan}{entity}{zone}{checksum}"


def generate_ifsc(bank: str = None) -> str:
    """Generate a valid IFSC code."""
    if bank is None:
        bank = random.choice(list(BANK_IFSC_PREFIXES.keys()))
    
    prefix = random.choice(BANK_IFSC_PREFIXES[bank])
    suffix = ''.join(random.choices(string.digits + string.ascii_uppercase, k=6))
    return f"{prefix}{suffix}"


def generate_account_number(bank: str) -> str:
    """Generate realistic account number based on bank."""
    if bank == "SBI":
        return ''.join(random.choices(string.digits, k=11))
    elif bank == "HDFC":
        return ''.join(random.choices(string.digits, k=14))
    elif bank == "ICICI":
        return ''.join(random.choices(string.digits, k=12))
    elif bank == "AXIS":
        return ''.join(random.choices(string.digits, k=16))
    else:
        return ''.join(random.choices(string.digits, k=random.choice([10, 11, 12, 14, 16])))


def generate_upi_id(name: str, bank: str = None) -> str:
    """Generate UPI ID."""
    name_part = name.lower().replace(' ', '.')
    
    upi_handles = {
        "HDFC": "@hdfcbank",
        "ICICI": "@icici",
        "SBI": "@sbi",
        "AXIS": "@axisbank",
        "KOTAK": "@kotak",
        "IDFC_FIRST": "@idfcbank",
        "YES_BANK": "@yesbank",
        "PAYTM": "@paytm",
        "PHONEPE": "@ybl",
        "GPAY": "@okaxis"
    }
    
    if bank and bank in upi_handles:
        handle = upi_handles[bank]
    else:
        handle = random.choice(list(upi_handles.values()))
    
    # Sometimes add numbers
    if random.random() < 0.3:
        name_part += str(random.randint(1, 999))
    
    return f"{name_part}{handle}"


def generate_indian_name() -> str:
    """Generate a random Indian name."""
    first = random.choice(INDIAN_FIRST_NAMES)
    last = random.choice(INDIAN_LAST_NAMES)
    return f"{first} {last}"


def generate_indian_address() -> Dict[str, str]:
    """Generate a random Indian address."""
    house_no = f"{random.randint(1, 999)}/{random.randint(1, 50)}"
    street = random.choice([
        "MG Road", "Nehru Street", "Gandhi Road", "Park Street", "Main Road",
        "Station Road", "Civil Lines", "Model Town", "Sector " + str(random.randint(1, 100)),
        "Koramangala", "Indiranagar", "Jayanagar", "Bandra", "Andheri"
    ])
    city = random.choice(INDIAN_CITIES)
    state = random.choice([
        "Maharashtra", "Karnataka", "Tamil Nadu", "Delhi", "West Bengal",
        "Gujarat", "Rajasthan", "Uttar Pradesh", "Madhya Pradesh", "Punjab",
        "Haryana", "Bihar", "Odisha", "Kerala", "Telangana", "Andhra Pradesh"
    ])
    pincode = ''.join(random.choices(string.digits, k=6))
    
    return {
        "line1": f"{house_no}, {street}",
        "city": city,
        "state": state,
        "pincode": pincode,
        "country": "India"
    }


def generate_mobile_number() -> str:
    """Generate Indian mobile number."""
    prefix = random.choice(['98', '97', '96', '95', '94', '93', '92', '91', '90',
                           '89', '88', '87', '86', '85', '84', '83', '82', '81', '80',
                           '79', '78', '77', '76', '75', '74', '73', '72', '70'])
    number = ''.join(random.choices(string.digits, k=8))
    return f"+91{prefix}{number}"


def generate_email(name: str) -> str:
    """Generate email address."""
    name_part = name.lower().replace(' ', '.')
    domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'rediffmail.com']
    
    if random.random() < 0.3:
        name_part += str(random.randint(1, 999))
    
    return f"{name_part}@{random.choice(domains)}"


def apply_messy_date_format(date_obj: datetime) -> str:
    """Apply various messy date formats."""
    format_choice = random.random()
    
    if format_choice < 0.4:
        return date_obj.strftime("%Y-%m-%d")
    elif format_choice < 0.6:
        return date_obj.strftime("%d/%m/%Y")
    elif format_choice < 0.75:
        # Use platform-safe day formatting (no leading zero)
        # Windows' strftime doesn't support %-d, so build manually
        return f"{date_obj.day} {date_obj.strftime('%b %y')}"  # "4 Nov 25"
    elif format_choice < 0.9:
        return date_obj.strftime("%Y/%m/%d %H:%M:%S")
    else:
        return date_obj.strftime("%d-%m-%Y")


def apply_messy_amount_format(amount: float) -> str:
    """Apply various messy numeric formats."""
    format_choice = random.random()
    
    if format_choice < 0.3:
        # Indian comma style
        return indian_number_format(amount)
    elif format_choice < 0.5:
        # No decimals
        return str(int(amount))
    elif format_choice < 0.7:
        # One decimal
        return f"{amount:.1f}"
    else:
        # Two decimals
        return f"{amount:.2f}"


def indian_number_format(amount: float) -> str:
    """Format number in Indian style with lakhs/crores."""
    s = f"{amount:.2f}"
    if '.' in s:
        integer_part, decimal_part = s.split('.')
    else:
        integer_part, decimal_part = s, "00"
    
    # Reverse and add commas
    integer_part = integer_part[::-1]
    result = []
    
    for i, char in enumerate(integer_part):
        if i == 3 or (i > 3 and (i - 3) % 2 == 0):
            result.append(',')
        result.append(char)
    
    formatted = ''.join(result[::-1])
    return f"{formatted}.{decimal_part}" if decimal_part else formatted


def generate_merchant_name_variants(merchant: str) -> str:
    """Generate merchant name with realistic variations."""
    variants = random.random()
    
    if variants < 0.6:
        return merchant
    elif variants < 0.75:
        return merchant.upper()
    elif variants < 0.85:
        return merchant.lower()
    elif variants < 0.92:
        return f"{merchant} India" if random.random() < 0.5 else f"{merchant}.in"
    else:
        # Add suffixes like PAY, WALLET, etc.
        suffixes = [" PAY", " WALLET", " APP", " ONLINE", " STORE"]
        return merchant + random.choice(suffixes)


def generate_transaction_narration(txn_type: str, mode: str, merchant: str = None, 
                                   bank: str = None) -> str:
    """Generate realistic transaction narration with bank-specific quirks."""
    if txn_type == "CREDIT":
        templates = [
            f"IMPS-{random.randint(100000000000, 999999999999)}-Salary Credit",
            f"NEFT-{random.randint(100000000000, 999999999999)}-Payment Received",
            f"UPI-{random.randint(100000000000, 999999999999)}-Payment from",
            "Salary for the month",
            "Interest Credit",
            "Refund"
        ]
        narration = random.choice(templates)
    else:  # DEBIT
        if merchant:
            ref = ''.join(random.choices(string.digits, k=12))
            templates = [
                f"UPI-{merchant}-{ref}",
                f"POS {merchant}",
                f"{merchant} Purchase",
                f"IMPS-{ref}-{merchant}",
                f"NEFT-{ref}-Payment to {merchant}"
            ]
            narration = random.choice(templates)
        else:
            narration = f"ATM Withdrawal-{random.randint(1000, 999999)}"
    
    # Apply bank-specific quirks
    if bank == "HDFC":
        # Truncate narration
        if random.random() < 0.3:
            narration = narration[:25] + "..."
    elif bank == "SBI":
        # Sometimes add Hindi/short codes
        if random.random() < 0.15:
            narration += " DBT"
    elif bank == "ICICI":
        # Add UPI ID
        if "UPI" in narration and random.random() < 0.5:
            upi_id = generate_upi_id("user", bank)
            narration += f"-{upi_id}"
    
    return narration


def generate_hsn_code() -> str:
    """Generate HSN code with variations in length."""
    base = random.randint(1000, 9999)
    if random.random() < 0.5:
        return str(base)
    elif random.random() < 0.7:
        return f"{base}{random.randint(10, 99)}"
    else:
        return f"{base}{random.randint(1000, 9999)}"


def generate_gst_rate() -> float:
    """Generate GST rate."""
    rates = [0, 0.25, 3, 5, 12, 18, 28]
    return random.choice(rates)


def calculate_gst_checksum(gstin: str) -> str:
    """Calculate checksum for GSTIN (simplified)."""
    # This is a simplified version
    return random.choice(string.ascii_uppercase + string.digits)


def generate_credit_score(distribution: Dict[str, float]) -> int:
    """Generate credit score based on distribution."""
    rand = random.random()
    cumulative = 0
    
    for range_str, prob in distribution.items():
        cumulative += prob
        if rand <= cumulative:
            min_score, max_score = map(int, range_str.split('-'))
            return random.randint(min_score, max_score)
    
    return 650  # Default


def generate_dpd_string() -> str:
    """Generate DPD (Days Past Due) string for 24 months."""
    dpd_values = ['000', '030', '060', '090', 'XXX', 'STD']
    
    dpd_list = []
    for _ in range(24):
        if random.random() < 0.85:  # 85% on-time
            dpd_list.append('000')
        elif random.random() < 0.9:  # Some 30 DPD
            dpd_list.append('030')
        elif random.random() < 0.95:  # Rare 60 DPD
            dpd_list.append('060')
        else:
            dpd_list.append(random.choice(['090', 'XXX']))
    
    return '|'.join(dpd_list)


def generate_random_walk_nav(base_nav: float, days: int) -> List[Tuple[str, float]]:
    """Generate NAV history using random walk."""
    result = []
    current_nav = base_nav
    current_date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        # Skip weekends
        if current_date.weekday() < 5:
            # Random walk with slight upward bias
            change_percent = random.gauss(0.05, 1.5) / 100
            current_nav *= (1 + change_percent)
            result.append((current_date.strftime("%Y-%m-%d"), round(current_nav, 4)))
        
        current_date += timedelta(days=1)
    
    return result


def introduce_duplicates(records: List[Dict], probability: float = 0.02) -> List[Dict]:
    """Introduce duplicate records."""
    duplicated = records.copy()
    
    for record in records:
        if random.random() < probability:
            # Create duplicate with slight variation
            dup = record.copy()
            
            # Sometimes change timestamp by ±1 second
            if 'timestamp' in dup and random.random() < 0.5:
                try:
                    dt = datetime.fromisoformat(dup['timestamp'])
                    dt += timedelta(seconds=random.choice([-1, 0, 1]))
                    dup['timestamp'] = dt.isoformat()
                except:
                    pass
            
            duplicated.append(dup)
    
    return duplicated


def introduce_missing_fields(record: Dict, probability: float = 0.15) -> Dict:
    """Randomly remove fields from a record."""
    result = record.copy()
    
    # Don't remove critical ID fields
    protected_fields = ['id', 'user_id', 'account_id', 'transaction_id', 
                       'gstin', 'pan', 'policy_id']
    
    for key in list(result.keys()):
        if key not in protected_fields and random.random() < probability:
            result[key] = None
    
    return result
