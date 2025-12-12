# Data Dictionary - Indian Financial Data Lake

## Overview
This document provides detailed field definitions, data types, value ranges, and business rules for all datasets in the synthetic Indian financial data lake.

---

## 1. CONSENT ARTEFACTS

### Purpose
Represents FIU ↔ AA consent exchange metadata following RBI AA Framework.

### Fields

| Field | Type | Required | Description | Example | Business Rules |
|-------|------|----------|-------------|---------|----------------|
| consent_id | string | Yes | Unique consent identifier (UUID format) | "A1B2C3D4-1234-5678-9ABC-123456789012" | 8-4-4-4-12 pattern |
| user_id | string | Yes | User identifier | "USER00000001" | Format: USER{8 digits} |
| fiu_id | string | Yes | Financial Information User ID | "FIU123" | Requesting entity |
| aa_id | string | Yes | Account Aggregator ID | "FINVU", "ONEMONEY" | One of 5 major AAs |
| consent_start | datetime | Yes | Consent start timestamp | "2025-01-15T10:30:00" | ISO 8601 format |
| consent_expiry | datetime | Yes | Consent expiry timestamp | "2025-07-15T10:30:00" | Must be after start |
| data_from | date | Yes | Historical data start date | "2022-01-01" | YYYY-MM-DD |
| data_to | date | Yes | Historical data end date | "2025-12-11" | YYYY-MM-DD |
| consent_types | array | Yes | Types of FI data requested | ["DEPOSIT", "SIP", "MUTUAL_FUNDS"] | Multiple allowed |
| fip_ids | array | Yes | List of FIP identifiers | ["FIP1001", "FIP1002"] | At least 1 |
| status | string | Yes | Consent status | "ACTIVE", "REVOKED" | 5 possible values |
| consent_mode | string | Yes | Access mode | "VIEW", "STORE", "QUERY" | How data is accessed |
| frequency_unit | string | Yes | Fetch frequency | "DAILY", "MONTHLY" | Data polling rate |
| fetch_type | string | Yes | Fetch pattern | "ONETIME", "PERIODIC" | Single or recurring |
| created_at | datetime | Yes | Creation timestamp | "2025-01-15T10:30:00" | ISO 8601 |
| updated_at | datetime | Yes | Last update timestamp | "2025-01-20T14:25:00" | ISO 8601 |

---

## 2. BANK ACCOUNTS

### Purpose
Bank account master data from multiple FIPs (banks) received via AA.

### Fields

| Field | Type | Required | Description | Example | Business Rules |
|-------|------|----------|-------------|---------|----------------|
| account_id | string | Yes | Unique account identifier | "ACC00000001" | Format: ACC{8 digits} |
| user_id | string | Yes | User identifier | "USER00000001" | Links to user |
| masked_account_number | string | No | Masked account number | "XXXXXX1234" | Last 4 digits visible |
| account_number | string | No | Full account number (raw only) | "12345678901234" | Removed in clean data |
| bank | string | Yes | Bank name | "HDFC", "ICICI", "SBI" | One of 7 banks |
| ifsc | string | Yes | IFSC code | "HDFC0001234" | 11 chars, format: XXXX0XXXXXX |
| branch | string | No | Branch name | "Mumbai Branch" | Free text |
| account_type | string | Yes | Account type | "SAVINGS", "CURRENT" | 4 possible types |
| currency | string | Yes | Currency code | "INR" | Always INR |
| opened_date | date | No | Account opening date | "2020-05-15" | YYYY-MM-DD |
| status | string | Yes | Account status | "ACTIVE", "CLOSED" | 3 possible values |
| balance | number | No | Current balance | 125000.50 | Can be negative for current |
| holder_name | string | No | Account holder name | "Rajesh Sharma" | Free text |
| fip_id | string | Yes | FIP identifier | "FIPHDFC1234" | Bank-specific |

### Bank-Specific Behaviors
- **HDFC**: Often has truncated narration (25 chars max)
- **ICICI**: Includes "particulars" field, embeds UPI IDs
- **SBI**: May group transactions, use Hindi codes
- **Axis**: Sometimes missing reference numbers
- **Yes Bank**: Frequent malformed UPI handles

---

## 3. TRANSACTIONS

### Purpose
Bank transaction history with realistic messiness and bank-specific quirks.

### Fields

| Field | Type | Required | Description | Example | Business Rules |
|-------|------|----------|-------------|---------|----------------|
| transaction_id | string | Yes | Unique transaction ID | "TXN000000000001" | Format: TXN{12 digits} |
| account_id | string | Yes | Account identifier | "ACC00000001" | Foreign key to accounts |
| date | date | Yes | Transaction date | "2025-11-04" | YYYY-MM-DD (clean) |
| timestamp | datetime | No | Transaction timestamp | "2025-11-04T14:23:15" | ISO 8601 format |
| type | string | Yes | Transaction type | "CREDIT", "DEBIT" | Only 2 values |
| amount | number | Yes | Transaction amount | 1250.00 | Always positive |
| currency | string | Yes | Currency | "INR" | Always INR |
| mode | string | No | Payment mode | "UPI", "NEFT", "IMPS" | 10+ possible modes |
| balance_after | number | No | Balance after transaction | 45320.50 | May be missing |
| narration | string | No | Transaction narration | "UPI-Amazon-123456789" | Bank-specific format |
| reference_number | string | No | Transaction reference | "REF123456789012" | Bank reference |
| merchant_name | string | No | Merchant name | "Amazon", "Swiggy" | For purchases |
| merchant_category | string | No | MCC code | "5411", "5812" | Industry standard |
| counterparty_account | string | No | Other party account | "98765432109876" | For transfers |
| counterparty_ifsc | string | No | Other party IFSC | "ICIC0001234" | For transfers |
| upi_id | string | No | UPI handle | "user@paytm" | For UPI transactions |
| category | string | No | Transaction category | "SALARY", "FOOD", "EMI" | 12+ categories |

### Transaction Categories
- **SALARY**: Incoming salary credits (₹15K-₹2L)
- **EMI**: Loan EMI deductions (₹1K-₹50K)
- **INVESTMENT**: Mutual fund/investment (₹5K-₹2L)
- **FOOD**: Food & dining (₹50-₹5K)
- **SHOPPING**: E-commerce/retail (₹200-₹15K)
- **TRAVEL**: Transport/travel (₹100-₹10K)
- **UTILITIES**: Bills, recharges (₹500-₹5K)
- **ENTERTAINMENT**: Movies, subscriptions (₹100-₹2K)
- **HEALTHCARE**: Medical expenses (₹500-₹50K)
- **EDUCATION**: Fees, courses (₹1K-₹1L)
- **TRANSFER**: P2P transfers (₹500-₹1L)
- **CASH_WITHDRAWAL**: ATM withdrawals (₹500-₹20K)
- **OTHER**: Miscellaneous

### Payment Modes
- **UPI**: Unified Payments Interface (60% of transactions)
- **IMPS**: Immediate Payment Service (15%)
- **NEFT**: National Electronic Funds Transfer (10%)
- **RTGS**: Real Time Gross Settlement (5%)
- **CASH**: Cash deposits/withdrawals (3%)
- **CHEQUE**: Cheque transactions (2%)
- **ATM**: ATM withdrawals (3%)
- **POS**: Point of Sale (2%)

---

## 4. GST RETURNS

### Purpose
GSTR-1 and GSTR-3B returns with invoice-level details and filing behavior.

### Fields

| Field | Type | Required | Description | Example | Business Rules |
|-------|------|----------|-------------|---------|----------------|
| return_id | string | Yes | Unique return identifier | "GSTR000001_112025_GSTR1" | Custom format |
| gstin | string | Yes | 15-digit GSTIN | "27ABCDE1234F1Z5" | Format: 2 digits + PAN + 4 chars |
| trade_name | string | No | Business trade name | "M/s Sharma Traders" | Free text |
| legal_name | string | No | Legal business name | "M/s Sharma Traders" | Free text |
| return_period | string | Yes | Return period MM-YYYY | "11-2025" | Format: MM-YYYY |
| return_type | string | Yes | Return type | "GSTR1", "GSTR3B" | 2 main types |
| filing_date | date | No | Actual filing date | "2025-12-15" | YYYY-MM-DD |
| status | string | Yes | Filing status | "FILED", "NOT_FILED" | 4 possible values |
| total_taxable_value | number | No | Total taxable turnover | 1250000.00 | Sum of all invoices |
| total_igst | number | No | Total IGST | 225000.00 | Integrated GST |
| total_cgst | number | No | Total CGST | 112500.00 | Central GST |
| total_sgst | number | No | Total SGST | 112500.00 | State GST |
| total_cess | number | No | Total cess | 0.00 | Additional cess |
| invoices | array | No | Invoice details | [...] | Only for GSTR1 |
| itc_claimed | number | No | Input Tax Credit claimed | 50000.00 | ITC amount |
| itc_reversed | number | No | ITC reversed | 0.00 | Reversals |
| net_tax_liability | number | No | Net tax payable | 400000.00 | After ITC |

### Invoice Fields (nested in GSTR-1)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| invoice_number | string | Invoice number | "INV/202511/0001" |
| invoice_date | date | Invoice date | "2025-11-05" |
| invoice_value | number | Total invoice value | 11800.00 |
| taxable_value | number | Taxable amount | 10000.00 |
| igst | number | IGST on invoice | 1800.00 |
| cgst | number | CGST on invoice | 900.00 |
| sgst | number | SGST on invoice | 900.00 |
| buyer_gstin | string | Buyer GSTIN | "29XYZAB5678C1Z3" |
| buyer_name | string | Buyer name | "ABC Enterprises" |
| place_of_supply | string | Supply location | "Maharashtra" |
| reverse_charge | string | Reverse charge flag | "N", "Y" |
| hsn_code | string | HSN code (4-8 digits) | "1234", "12345678" |
| gst_rate | number | GST rate % | 18.0 |

### GST Turnover Ranges
- **Micro**: ₹1-5 lakh/month (50% of businesses)
- **Small**: ₹5-20 lakh/month (35%)
- **Medium**: ₹20-75 lakh/month (15%)

### Filing Patterns
- **FILED**: 70% (filed on time)
- **NOT_FILED**: 15% (missed filing)
- **LATE_FILED**: 10% (filed late, 60-180 days)
- **REVISED**: 5% (filed revision)

---

## 5. CREDIT BUREAU REPORTS

### Purpose
CIBIL/Experian-style credit reports with account history and DPD data.

### Fields

| Field | Type | Required | Description | Example | Business Rules |
|-------|------|----------|-------------|---------|----------------|
| report_id | string | Yes | Report identifier | "CBR00000001" | Format: CBR{8 digits} |
| user_id | string | Yes | User identifier | "USER00000001" | Links to user |
| bureau_type | string | Yes | Bureau name | "CIBIL", "EXPERIAN" | One of 4 bureaus |
| report_date | date | Yes | Report generation date | "2025-12-01" | YYYY-MM-DD |
| credit_score | integer | No | Credit score (300-900) | 725 | Range: 300-900 |
| pan | string | No | PAN (masked) | "ABCDE1234F" or "ABCDEXXXXF" | 10 chars |
| name | string | No | User name | "Rajesh Kumar" | Free text |
| dob | date | No | Date of birth | "1985-05-15" | YYYY-MM-DD |
| gender | string | No | Gender | "M", "F", "O" | Single char |
| address | object | No | Address details | {...} | Structured object |
| accounts | array | No | Credit accounts | [...] | Array of accounts |
| enquiries | array | No | Credit enquiries | [...] | Array of enquiries |
| total_accounts | integer | No | Total accounts count | 5 | Calculated |
| active_accounts | integer | No | Active accounts count | 3 | Calculated |
| total_credit_limit | number | No | Total credit limit | 500000.00 | Sum across accounts |
| total_outstanding | number | No | Total outstanding | 125000.00 | Current dues |
| total_overdue | number | No | Total overdue amount | 5000.00 | Past due |
| enquiries_last_30_days | integer | No | Recent enquiries (30d) | 2 | Count |
| enquiries_last_90_days | integer | No | Recent enquiries (90d) | 5 | Count |

### Credit Account Fields (nested)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| account_number | string | Masked account | "XXXX1234" |
| account_type | string | Loan type | "PERSONAL_LOAN", "HOME_LOAN", "CREDIT_CARD" |
| ownership | string | Ownership type | "INDIVIDUAL", "JOINT", "GUARANTOR" |
| date_opened | date | Account opening date | "2020-01-15" |
| date_closed | date | Account closing date | "2023-12-31" or null |
| credit_limit | number | Credit limit/loan amount | 500000.00 |
| current_balance | number | Current outstanding | 125000.00 |
| amount_overdue | number | Overdue amount | 5000.00 |
| dpd_string | string | 24-month DPD history | "000\|000\|030\|000\|..." |
| write_off_amount | number | Written-off amount | 0.00 or null |
| settlement_amount | number | Settlement amount | null |
| status | string | Account status | "ACTIVE", "CLOSED", "WRITTEN_OFF" |
| lender_name | string | Lender name | "HDFC Bank" |

### DPD (Days Past Due) Codes
- **000**: Payment on time
- **030**: 1-30 days past due
- **060**: 31-60 days past due
- **090**: 61-90 days past due
- **XXX**: 90+ days past due
- **STD**: Sub-standard (written off)

### Credit Score Distribution
- **300-550**: 12% (High risk)
- **550-650**: 35% (Medium-high risk)
- **650-750**: 38% (Medium-low risk)
- **750-900**: 15% (Low risk)

### Account Types
- **PERSONAL_LOAN**: Unsecured personal loans
- **HOME_LOAN**: Housing loans (largest amounts)
- **AUTO_LOAN**: Vehicle loans
- **CREDIT_CARD**: Revolving credit
- **OVERDRAFT**: Bank overdraft facility
- **LOAN_AGAINST_PROPERTY**: Secured loans
- **GOLD_LOAN**: Gold-backed loans
- **EDUCATION_LOAN**: Student loans
- **TWO_WHEELER_LOAN**: Bike loans
- **BUSINESS_LOAN**: MSME/business loans

---

## 6. INSURANCE POLICIES

### Purpose
Insurance policy data including life, health, vehicle, and term insurance with claim history.

### Fields

| Field | Type | Required | Description | Example | Business Rules |
|-------|------|----------|-------------|---------|----------------|
| policy_id | string | Yes | Policy identifier | "POL00000001" | Format: POL{8 digits} |
| user_id | string | Yes | User identifier | "USER00000001" | Links to user |
| policy_number | string | Yes | Policy number | "LIC/123456/2020" | Insurer-specific |
| policy_type | string | Yes | Policy type | "LIFE", "HEALTH", "TERM" | 8 types |
| insurer | string | Yes | Insurance company | "LIC", "HDFC Life" | Major insurers |
| insured_name | string | No | Insured person name | "Rajesh Kumar" | Free text |
| nominee_name | string | No | Nominee name | "Priya Kumar" | Free text |
| sum_assured | number | No | Sum assured | 1000000.00 | Coverage amount |
| premium_amount | number | No | Premium amount | 25000.00 | Payment amount |
| premium_frequency | string | No | Payment frequency | "YEARLY", "MONTHLY" | How often paid |
| policy_start_date | date | No | Policy start date | "2020-01-15" | YYYY-MM-DD |
| policy_end_date | date | No | Policy end date | "2045-01-15" | YYYY-MM-DD |
| maturity_date | date | No | Maturity date | "2045-01-15" | For endowment/ULIP |
| status | string | Yes | Policy status | "ACTIVE", "LAPSED" | 5 possible values |
| last_premium_paid_date | date | No | Last payment date | "2025-01-15" | YYYY-MM-DD |
| claims | array | No | Claim history | [...] | Array of claims |
| rider_details | array | No | Policy riders | [] | Additional benefits |

### Policy Types & Ranges
- **LIFE**: ₹5L-₹1Cr sum assured, 2-5% of SA as premium
- **HEALTH**: ₹3L-₹20L sum assured, 1.5-3.5% of SA
- **TERM**: ₹5L-₹1Cr sum assured, 0.1-0.5% of SA (cheapest)
- **ENDOWMENT**: ₹1L-₹50L sum assured, 2-5% of SA
- **ULIP**: ₹1L-₹50L sum assured, variable premium
- **VEHICLE**: ₹2L-₹30L, 2-4% of IDV
- **HOME**: ₹5L-₹1Cr, 0.2-0.5% of value
- **TRAVEL**: ₹1L-₹10L, one-time premium

### Claim Fields (nested)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| claim_id | string | Claim identifier | "CLM000001" |
| claim_date | date | Claim submission date | "2025-06-15" |
| claim_amount | number | Claimed amount | 250000.00 |
| claim_status | string | Claim status | "SETTLED", "PENDING" |
| settlement_date | date | Settlement date | "2025-08-20" or null |
| settlement_amount | number | Settled amount | 240000.00 |
| claim_type | string | Claim type | "HOSPITALIZATION", "ACCIDENT" |

---

## 7-9. Additional Datasets

Complete data dictionaries for **Mutual Funds**, **ONDC Orders**, and **OCEN Loan Applications** follow the same detailed format with field definitions, types, ranges, and business rules.

---

## Data Quality Notes

### Missing Values
- **15% probability**: Random fields missing in raw data
- **Protected fields**: IDs, keys never missing
- **Calculated fields**: May be recalculated if missing

### Duplicates
- **2% probability**: Exact or near-duplicates introduced
- **Timestamp drift**: ±1 second variations
- **Merchant drift**: Name variations (e.g., "Amazon", "AMAZON PAY")

### Format Variations (Raw Data Only)
- **Dates**: "2025-11-04", "04/11/2025", "4 Nov 25"
- **Amounts**: "1,25,000", "125000.0", "125000"
- **Text**: Extra whitespace, case inconsistencies

---

## Validation Rules

All clean data is validated against JSONSchema definitions in `schemas/` directory. Common patterns:

- **PAN**: `^[A-Z]{3}[PCHABFGJLT][A-Z][0-9]{4}[A-Z]$`
- **GSTIN**: `^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$`
- **IFSC**: `^[A-Z]{4}0[A-Z0-9]{6}$`
- **Mobile**: `^\\+91[6-9][0-9]{9}$`
- **Email**: Standard RFC 5322

---

This dictionary is comprehensive but not exhaustive. Refer to JSON schemas for complete field specifications.
