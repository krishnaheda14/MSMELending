"""
Advanced Financial Metrics Module
Computes earnings vs spendings, cashflow stability, seasonality, and credit behavior metrics.
"""
import math
import statistics
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Tuple
from dateutil import parser as date_parser


def normalize_date_to_month(date_str):
    """Normalize inconsistent date formats to YYYY-MM format."""
    if not date_str:
        return '2025-01'
    try:
        parsed = date_parser.parse(str(date_str), dayfirst=False)
        return parsed.strftime('%Y-%m')
    except:
        # Fallback for unparseable dates
        return '2025-01'


def compute_cashflow_metrics(transactions: List[Dict]) -> Dict:
    """Compute detailed cashflow metrics including inflow/outflow, variance, seasonality."""
    # Parse transactions into credits/debits and monthly aggregates
    credits = []
    debits = []
    monthly_credits = defaultdict(float)
    monthly_debits = defaultdict(float)
    counterparty_inflows = defaultdict(float)

    for txn in transactions:
        txn_type = (txn.get('type') or txn.get('transaction_type') or '').upper()
        try:
            amount = abs(float(str(txn.get('amount', 0) or txn.get('value', 0) or 0).replace(',', '')))
        except Exception:
            amount = 0.0

        if amount == 0:
            continue

        date_str = txn.get('date') or txn.get('transaction_date') or txn.get('txn_date') or ''
        try:
            month = date_str[:7] if date_str else '2025-01'
        except Exception:
            month = '2025-01'

        if txn_type in ['CREDIT', 'CR', 'C', 'DEPOSIT']:
            credits.append(amount)
            monthly_credits[month] += amount
            counterparty = (txn.get('merchant_name') or txn.get('counterparty_account') or txn.get('description', '')[:30] or f'Customer-{len(counterparty_inflows) + 1:03d}')
            counterparty_inflows[counterparty] += amount
        else:
            debits.append(amount)
            monthly_debits[month] += amount

    total_inflow = sum(credits)
    total_outflow = sum(debits)
    net_surplus = total_inflow - total_outflow

    inflow_outflow_ratio = (total_inflow / total_outflow) if total_outflow > 0 else float('inf')
    surplus_ratio = (net_surplus / total_inflow * 100) if total_inflow > 0 else 0

    # ----- Seasonality & Income Stability (recommended formula) -----
    # Step 1: monthly averages (month-of-year across years)
    month_buckets = {m: [] for m in range(1, 13)}
    for ym, val in monthly_credits.items():
        try:
            parts = ym.split('-')
            if len(parts) == 2:
                mnum = int(parts[1])
                month_buckets[mnum].append(float(val))
        except Exception:
            continue

    avg_by_month = {}
    for m in range(1, 13):
        vals = month_buckets.get(m, [])
        avg_by_month[m] = statistics.mean(vals) if vals else 0.0

    nonzero_month_avgs = [v for v in avg_by_month.values() if v is not None]
    overall_avg_monthly_rev = statistics.mean(nonzero_month_avgs) if nonzero_month_avgs else 0.0

    # Step 2: seasonality index per month and Step 3: SV (CV of those indices)
    seasonality_index_by_month = {}
    seasonality_indices = []
    for m in range(1, 13):
        avg_m = avg_by_month.get(m, 0.0) or 0.0
        si_m = (avg_m / overall_avg_monthly_rev) if overall_avg_monthly_rev > 0 else 1.0
        seasonality_index_by_month[f"{m:02d}"] = round(si_m, 4)
        seasonality_indices.append(si_m)

    seasonality_sv = 0.0
    try:
        if len(seasonality_indices) > 1 and statistics.mean(seasonality_indices) != 0:
            seasonality_sv = statistics.pstdev(seasonality_indices) / statistics.mean(seasonality_indices) * 100.0
    except Exception:
        seasonality_sv = 0.0

    # Income stability: CV across all months (std/mean * 100)
    all_months_vals = [v for v in monthly_credits.values()]
    income_cv_overall = None
    try:
        if all_months_vals and statistics.mean(all_months_vals) != 0 and len(all_months_vals) > 1:
            income_cv_overall = statistics.pstdev(all_months_vals) / statistics.mean(all_months_vals) * 100.0
    except Exception:
        income_cv_overall = None

    # --- build monthly surplus and trends ---
    monthly_surplus = {}
    for month in set(list(monthly_credits.keys()) + list(monthly_debits.keys())):
        monthly_surplus[month] = monthly_credits.get(month, 0) - monthly_debits.get(month, 0)

    sorted_months = sorted(monthly_surplus.items())
    surplus_trend = "stable"
    if len(sorted_months) >= 3:
        mid = len(sorted_months) // 2
        first_half_avg = sum([v for _, v in sorted_months[:mid]]) / mid if mid > 0 else 0
        second_half_avg = sum([v for _, v in sorted_months[mid:]]) / (len(sorted_months) - mid) if (len(sorted_months) - mid) > 0 else 0
        if second_half_avg > first_half_avg * 1.1:
            surplus_trend = "increasing"
        elif second_half_avg < first_half_avg * 0.9:
            surplus_trend = "decreasing"

    # Variance in cashflow
    all_amounts = credits + debits
    cashflow_variance = 0
    if len(all_amounts) > 1:
        mean_amt = sum(all_amounts) / len(all_amounts)
        cashflow_variance = sum((x - mean_amt) ** 2 for x in all_amounts) / len(all_amounts)

    sorted_customers = sorted(counterparty_inflows.items(), key=lambda x: x[1], reverse=True)
    top_3_inflow = sum(v for _, v in sorted_customers[:3])
    top_customer_dependence = (top_3_inflow / total_inflow * 100) if total_inflow > 0 else 0

    # Assemble result
    result = {
        "total_inflow": total_inflow,
        "total_outflow": total_outflow,
        "net_surplus": net_surplus,
        "surplus_ratio": round(surplus_ratio, 2),
        "inflow_outflow_ratio": round(inflow_outflow_ratio, 2) if inflow_outflow_ratio != float('inf') else 999,
        "income_stability_cv": round(income_cv_overall, 2) if income_cv_overall is not None else None,
        "seasonality_index": round(seasonality_sv, 2),
        "top_customer_dependence": round(top_customer_dependence, 2),
        "top_customers": [{"name": name, "amount": round(amt, 2)} for name, amt in sorted_customers[:5]],
        "monthly_inflow": {k: round(v, 2) for k, v in sorted(monthly_credits.items())},
        "monthly_outflow": {k: round(v, 2) for k, v in sorted(monthly_debits.items())},
        "monthly_surplus": {k: round(v, 2) for k, v in sorted_months},
        "surplus_trend": surplus_trend,
        "cashflow_variance": round(cashflow_variance, 2),
        "calculation": {
            "seasonality": {
                "overall_sv_percent": round(seasonality_sv, 2),
                "by_month_index": seasonality_index_by_month,
                "rating_table": {
                    "<10": "Very Stable",
                    "10-25": "Mild Seasonality",
                    "25-50": "Moderate Seasonality",
                    ">50": "High Seasonality Risk"
                },
                "explanation": "Seasonality SV is coefficient of variation (std/mean) of monthly seasonality indices; lower is more stable."
            },
            "income_stability": {
                "cv_overall_percent": round(income_cv_overall, 2) if income_cv_overall is not None else None,
                "explanation": "Income stability computed as CV across all months (std/mean * 100). Lower values indicate more stable income month-to-month."
            },
            "inflow_outflow_ratio": {
                "formula": "Total Inflow ÷ Total Outflow",
                "breakdown": {
                    "Total Inflow (Credits)": f"₹{total_inflow:,.2f}",
                    "Total Outflow (Debits)": f"₹{total_outflow:,.2f}",
                    "Ratio": f"{inflow_outflow_ratio:.2f}" if inflow_outflow_ratio != float('inf') else "∞"
                },
                "explanation": f"This ratio of {inflow_outflow_ratio:.2f} means for every ₹1 spent, you earn ₹{inflow_outflow_ratio:.2f}. {'Healthy - income exceeds expenses' if inflow_outflow_ratio > 1.2 else 'Concerning - expenses are high relative to income' if inflow_outflow_ratio < 1.0 else 'Moderate - income slightly exceeds expenses'}. Analyzed {len(transactions)} transactions."
            },
            "cashflow_variance": {
                "formula": "Σ(amount - mean)² ÷ N",
                "breakdown": {
                    "Total Transactions": len(all_amounts),
                    "Mean Transaction Amount": f"₹{sum(all_amounts) / len(all_amounts):,.2f}" if all_amounts else "N/A",
                    "Variance": f"₹{cashflow_variance:,.2f}"
                },
                "explanation": f"Measures volatility in transaction amounts. Higher variance ({cashflow_variance:,.2f}) indicates {'irregular transaction patterns - both large and small transactions common' if cashflow_variance > 1000000 else 'consistent transaction sizes - predictable cashflow'}."
            }
        }
    }

    return result


def compute_expense_composition(transactions: List[Dict]) -> Dict:
    """Compute expense composition: essential vs non-essential spending."""
    
    essential_categories = ['UTILITIES', 'RENT', 'SALARY', 'LOAN_REPAYMENT', 'INSURANCE', 'TAX']
    non_essential_categories = ['ENTERTAINMENT', 'DINING', 'SHOPPING', 'TRAVEL']
    
    essential_spend = 0
    non_essential_spend = 0
    debt_servicing = 0
    total_expenses = 0
    # collect sample transactions for explainability
    essential_txns = []
    non_essential_txns = []
    debt_txns = []
    
    for txn in transactions:
        txn_type = (txn.get('type') or '').upper()
        if txn_type not in ['DEBIT', 'DR', 'D', 'WITHDRAWAL']:
            continue
        
        try:
            amount = abs(float(str(txn.get('amount', 0) or 0).replace(',', '')))
        except:
            amount = 0
        
        if amount == 0:
            continue
        
        total_expenses += amount
        category = (txn.get('category') or txn.get('merchant_category') or '').upper()
        narration = (txn.get('narration') or '').upper()
        
        # Categorize
        if category in essential_categories or any(key in narration for key in ['SALARY', 'RENT', 'UTILITY', 'BILL']):
            essential_spend += amount
            if len(essential_txns) < 20:
                essential_txns.append({
                    'date': txn.get('date') or txn.get('transaction_date') or '',
                    'merchant': txn.get('merchant_name') or txn.get('counterparty') or txn.get('description') or '',
                    'amount': round(amount, 2),
                    'narration': txn.get('narration') or txn.get('description') or ''
                })
        elif category in non_essential_categories:
            non_essential_spend += amount
            if len(non_essential_txns) < 20:
                non_essential_txns.append({
                    'date': txn.get('date') or txn.get('transaction_date') or '',
                    'merchant': txn.get('merchant_name') or txn.get('counterparty') or txn.get('description') or '',
                    'amount': round(amount, 2),
                    'narration': txn.get('narration') or txn.get('description') or ''
                })
        
        # Debt servicing (EMI, loan payments)
        if 'EMI' in narration or 'LOAN' in narration or category == 'LOAN_REPAYMENT':
            debt_servicing += amount
            if len(debt_txns) < 20:
                debt_txns.append({
                    'date': txn.get('date') or txn.get('transaction_date') or '',
                    'merchant': txn.get('merchant_name') or txn.get('counterparty') or txn.get('description') or '',
                    'amount': round(amount, 2),
                    'narration': txn.get('narration') or txn.get('description') or ''
                })
    
    # Calculate ratios
    essential_ratio = (essential_spend / total_expenses * 100) if total_expenses > 0 else 0
    non_essential_ratio = (non_essential_spend / total_expenses * 100) if total_expenses > 0 else 0
    dsr = (debt_servicing / total_expenses * 100) if total_expenses > 0 else 0
    
    return {
        "total_expenses": round(total_expenses, 2),
        "essential_spend": round(essential_spend, 2),
        "non_essential_spend": round(non_essential_spend, 2),
        "other_spend": round(total_expenses - essential_spend - non_essential_spend, 2),
        "essential_ratio": round(essential_ratio, 2),
        "non_essential_ratio": round(non_essential_ratio, 2),
        "debt_servicing": round(debt_servicing, 2),
        "debt_servicing_ratio": round(dsr, 2),
        "sample_transactions": {
            "essential": essential_txns,
            "non_essential": non_essential_txns,
            "debt_servicing": debt_txns
        },
        "calculation": {
            "total_expenses": {
                "formula": "Sum of all DEBIT transactions",
                "breakdown": {
                    "Total Expense Transactions": f"₹{total_expenses:,.2f}",
                    "Essential Spending": f"₹{essential_spend:,.2f} ({essential_ratio:.1f}%)",
                    "Non-Essential Spending": f"₹{non_essential_spend:,.2f} ({non_essential_ratio:.1f}%)",
                    "Other Spending": f"₹{total_expenses - essential_spend - non_essential_spend:,.2f}"
                },
                "explanation": f"Total expenses of ₹{total_expenses:,.2f} across all DEBIT transactions. Essential expenses include rent, utilities, salary, loan repayments."
            },
            "essential_ratio": {
                "formula": "(Essential Spend ÷ Total Expenses) × 100",
                "breakdown": {
                    "Essential Spend": f"₹{essential_spend:,.2f}",
                    "Total Expenses": f"₹{total_expenses:,.2f}",
                    "Essential Ratio": f"{essential_ratio:.2f}%"
                },
                "explanation": f"Essential expenses are {essential_ratio:.2f}% of total spending. {'Good - majority spent on necessary items' if essential_ratio > 60 else 'Concerning - high discretionary spending'}. Essential categories: utilities, rent, salary, loan repayment, insurance, tax."
            },
            "debt_servicing_ratio": {
                "formula": "(Debt Servicing ÷ Total Expenses) × 100",
                "breakdown": {
                    "Debt Servicing (EMI + Loans)": f"₹{debt_servicing:,.2f}",
                    "Total Expenses": f"₹{total_expenses:,.2f}",
                    "DSR": f"{dsr:.2f}%"
                },
                "explanation": f"Debt servicing is {dsr:.2f}% of total expenses. {'Healthy - sustainable debt levels' if dsr < 40 else 'High - debt burden may strain cashflow' if dsr < 60 else 'Critical - debt obligations are very high'}. Includes all EMI and loan repayment transactions."
            }
        }
    }


def compute_credit_behavior(transactions: List[Dict]) -> Dict:
    """Compute credit behavior metrics: bounce count, EMI consistency, and advanced credit scores."""
    
    bounces = 0
    emi_transactions = []
    failed_transactions = []
    loan_repayments = []
    total_debits = 0
    on_time_payments = 0
    late_payments = 0
    
    for txn in transactions:
        narration = (txn.get('narration') or '').upper()
        description = (txn.get('description') or '').upper()
        txn_type = (txn.get('type') or '').upper()
        
        # Count total debits for DTI calculation
        if txn_type in ['DEBIT', 'DR', 'D']:
            try:
                amount = abs(float(str(txn.get('amount', 0) or 0).replace(',', '')))
                total_debits += amount
            except:
                pass
        
        # Detect bounces
        if any(keyword in narration or keyword in description for keyword in ['BOUNCE', 'FAILED', 'REJECT', 'INSUFFICIENT', 'RETURN']):
            bounces += 1
            failed_transactions.append(txn)
        
        # Detect EMI payments
        if 'EMI' in narration or 'EMI' in description:
            try:
                amount = abs(float(str(txn.get('amount', 0) or 0).replace(',', '')))
                date = txn.get('date') or txn.get('transaction_date', '')
                emi_transactions.append({"amount": amount, "date": date})
            except:
                pass
        
        # Detect loan repayments for repayment rate calculation
        if any(keyword in narration or keyword in description for keyword in ['LOAN', 'REPAYMENT', 'EMI', 'CREDIT CARD']):
            try:
                amount = abs(float(str(txn.get('amount', 0) or 0).replace(',', '')))
                loan_repayments.append(amount)
                # Assume on-time if not bounced
                if not any(keyword in narration or keyword in description for keyword in ['BOUNCE', 'FAILED']):
                    on_time_payments += 1
                else:
                    late_payments += 1
            except:
                pass
    
    # EMI consistency
    emi_consistency_score = 100  # Default perfect
    emi_variance = 0
    if len(emi_transactions) > 1:
        amounts = [e['amount'] for e in emi_transactions]
        mean_emi = sum(amounts) / len(amounts)
        variance = sum((x - mean_emi) ** 2 for x in amounts) / len(amounts)
        std = math.sqrt(variance)
        cv = (std / mean_emi) if mean_emi > 0 else 0
        emi_variance = round(variance, 2)
        # Lower CV = higher consistency
        emi_consistency_score = round(max(0, 100 - (cv * 100)), 2)
    
    # Advanced Credit Scores
    
    # 1. Credit Utilization Ratio (proxy: loan repayments / total income)
    total_credits = sum([
        abs(float(str(t.get('amount', 0) or 0).replace(',', '')))
        for t in transactions
        if (t.get('type') or '').upper() in ['CREDIT', 'CR', 'C']
    ])
    total_loan_payments = sum(loan_repayments)
    credit_utilization_ratio = (total_loan_payments / total_credits * 100) if total_credits > 0 else 0
    
    # 2. Default Probability Score (based on bounces, EMI consistency, payment history)
    # Score from 0-100, lower is better (0 = no default risk, 100 = high default risk)
    bounce_penalty = min(bounces * 5, 40)  # Up to 40 points for bounces
    emi_penalty = (100 - emi_consistency_score) * 0.3  # Up to 30 points for EMI inconsistency
    utilization_penalty = max(0, (credit_utilization_ratio - 30) * 0.5) if credit_utilization_ratio > 30 else 0  # Penalty if >30% utilization
    default_probability_score = min(100, bounce_penalty + emi_penalty + utilization_penalty)
    
    # 3. Debt-to-Income Ratio (loan payments / total income)
    debt_to_income_ratio = (total_loan_payments / total_credits * 100) if total_credits > 0 else 0
    
    # 4. Payment Regularity Score (0-100, higher is better)
    total_payment_attempts = on_time_payments + late_payments
    if total_payment_attempts > 0:
        payment_regularity_score = (on_time_payments / total_payment_attempts * 100)
    else:
        payment_regularity_score = 100  # No loans = perfect
    
    # 5. Loan Repayment Rate (percentage of expected payments made)
    # Assuming monthly EMIs, calculate expected vs actual
    if len(emi_transactions) > 1:
        # Expected: one payment per month
        unique_months = len(set([e['date'][:7] for e in emi_transactions if e.get('date')]))
        actual_payments = len(emi_transactions)
        loan_repayment_rate = (actual_payments / unique_months * 100) if unique_months > 0 else 100
    else:
        loan_repayment_rate = 100  # Insufficient data
    
    return {
        "bounce_count": bounces,
        "emi_count": len(emi_transactions),
        "emi_consistency_score": emi_consistency_score,
        "emi_variance": emi_variance,
        "credit_utilization_ratio": round(credit_utilization_ratio, 2),
        "default_probability_score": round(default_probability_score, 2),
        "debt_to_income_ratio": round(debt_to_income_ratio, 2),
        "payment_regularity_score": round(payment_regularity_score, 2),
        "loan_repayment_rate": round(loan_repayment_rate, 2),
        "failed_transactions": failed_transactions[:5],  # Top 5 failures
        "calculation": {
            "bounce_count": {
                "formula": "Count transactions with keywords: BOUNCE, FAILED, REJECT, INSUFFICIENT, RETURN",
                "breakdown": {
                    "Total Bounced Transactions": bounces,
                    "Failed Transaction Types": "Payment failures, insufficient funds, account issues"
                },
                "explanation": f"Detected {bounces} failed/bounced transactions. {'Excellent payment discipline' if bounces == 0 else 'Warning - payment failures indicate cashflow or account management issues' if bounces > 5 else 'Some payment issues detected'}. Each bounce negatively impacts credit score."
            },
            "emi_consistency_score": {
                "formula": "100 - (Coefficient of Variation × 100)",
                "breakdown": {
                    "Total EMI Transactions": len(emi_transactions),
                    "Mean EMI Amount": f"₹{sum([e['amount'] for e in emi_transactions]) / len(emi_transactions):,.2f}" if emi_transactions else "N/A",
                    "EMI Variance": f"₹{emi_variance:,.2f}",
                    "Consistency Score": f"{emi_consistency_score}/100"
                },
                "explanation": f"EMI consistency score is {emi_consistency_score}/100 based on {len(emi_transactions)} EMI payments. {'Excellent - very consistent EMI payments' if emi_consistency_score > 90 else 'Good - mostly regular EMI payments' if emi_consistency_score > 70 else 'Concerning - irregular EMI payment amounts'}. Higher scores indicate reliable debt servicing."
            },
            "emi_variance": {
                "formula": "Σ(EMI_amount - mean_EMI)² ÷ N",
                "breakdown": {
                    "EMI Count": len(emi_transactions),
                    "Variance": f"₹{emi_variance:,.2f}"
                },
                "explanation": f"Variance of ₹{emi_variance:,.2f} in EMI amounts. {'Low variance indicates fixed EMIs (term loans)' if emi_variance < 10000 else 'High variance suggests variable EMIs or multiple loan products'}."
            },
            "credit_utilization_ratio": {
                "formula": "(Total Loan Payments ÷ Total Income) × 100",
                "breakdown": {
                    "Total Loan Payments": f"₹{total_loan_payments:,.2f}",
                    "Total Income (Credits)": f"₹{total_credits:,.2f}",
                    "Utilization Ratio": f"{credit_utilization_ratio:.2f}%"
                },
                "explanation": f"Credit utilization of {credit_utilization_ratio:.2f}% shows {'healthy debt levels (<30%)' if credit_utilization_ratio < 30 else 'moderate debt usage (30-50%)' if credit_utilization_ratio < 50 else 'high debt burden (>50%) - concerning'}. Lower ratios indicate better debt management."
            },
            "default_probability_score": {
                "formula": "Bounce Penalty + EMI Inconsistency Penalty + Utilization Penalty",
                "breakdown": {
                    "Bounce Penalty": f"{bounce_penalty:.1f} points ({bounces} bounces)",
                    "EMI Inconsistency": f"{emi_penalty:.1f} points",
                    "High Utilization": f"{utilization_penalty:.1f} points",
                    "Total Risk Score": f"{default_probability_score:.2f}/100"
                },
                "explanation": f"Default probability score of {default_probability_score:.2f}/100 indicates {'very low default risk (<20)' if default_probability_score < 20 else 'low risk (20-40)' if default_probability_score < 40 else 'moderate risk (40-60)' if default_probability_score < 60 else 'high default risk (>60)'}. Lower scores are better. Based on payment history, bounces, and EMI consistency."
            },
            "debt_to_income_ratio": {
                "formula": "(Total Debt Payments ÷ Total Income) × 100",
                "breakdown": {
                    "Total Debt Payments": f"₹{total_loan_payments:,.2f}",
                    "Total Income": f"₹{total_credits:,.2f}",
                    "DTI Ratio": f"{debt_to_income_ratio:.2f}%"
                },
                "explanation": f"Debt-to-Income ratio of {debt_to_income_ratio:.2f}% {'is healthy (<30%)' if debt_to_income_ratio < 30 else 'is acceptable (30-40%)' if debt_to_income_ratio < 40 else 'is concerning (>40%) - high debt burden'}. Lenders prefer DTI below 36%."
            },
            "payment_regularity_score": {
                "formula": "(On-Time Payments ÷ Total Payment Attempts) × 100",
                "breakdown": {
                    "On-Time Payments": on_time_payments,
                    "Late/Failed Payments": late_payments,
                    "Regularity Score": f"{payment_regularity_score:.2f}/100"
                },
                "explanation": f"Payment regularity of {payment_regularity_score:.2f}/100 shows {'excellent payment discipline (>90)' if payment_regularity_score > 90 else 'good payment habits (70-90)' if payment_regularity_score > 70 else 'irregular payments (<70) - concerning'}. Consistent on-time payments improve creditworthiness."
            },
            "loan_repayment_rate": {
                "formula": "(Actual Payments ÷ Expected Monthly Payments) × 100",
                "breakdown": {
                    "Actual EMI Payments": len(emi_transactions),
                    "Expected (Monthly)": f"{len(set([e['date'][:7] for e in emi_transactions if e.get('date')]))} months" if emi_transactions else "N/A",
                    "Repayment Rate": f"{loan_repayment_rate:.2f}%"
                },
                "explanation": f"Loan repayment rate of {loan_repayment_rate:.2f}% indicates {'excellent - all payments made' if loan_repayment_rate >= 95 else 'good - most payments made' if loan_repayment_rate >= 80 else 'concerning - missed payments' if loan_repayment_rate >= 60 else 'poor - frequent missed payments'}. Tracks payment consistency over time."
            }
        }
    }


def compute_business_health_metrics(gst_data: Dict, transactions: List[Dict], ondc_data: Dict) -> Dict:
    """Compute business health indicators."""
    
    # GST vs Bank reconciliation
    gst_turnover = gst_data.get('total_revenue', 0) or 0
    
    # Compute bank turnover from transactions
    bank_credits = sum([
        abs(float(str(t.get('amount', 0) or 0).replace(',', '')))
        for t in transactions
        if (t.get('type') or '').upper() in ['CREDIT', 'CR', 'C', 'DEPOSIT']
    ])
    
    reconciliation_variance = abs(gst_turnover - bank_credits)
    # Provide both normalizations instead of a single capped ratio.
    percent_of_gst = (reconciliation_variance / gst_turnover * 100) if gst_turnover > 0 else None
    percent_of_bank = (reconciliation_variance / bank_credits * 100) if bank_credits > 0 else None
    # Keep a conservative 'relative' ratio for backward compatibility (use min if available)
    base_amount = None
    if gst_turnover > 0 and bank_credits > 0:
        base_amount = min(gst_turnover, bank_credits)
    elif gst_turnover > 0:
        base_amount = gst_turnover
    else:
        base_amount = bank_credits
    reconciliation_ratio = (reconciliation_variance / base_amount * 100) if base_amount and base_amount > 0 else None
    
    # Working capital gap (simplified: current assets - current liabilities)
    # Using monthly surplus as proxy
    monthly_surplus_values = []
    monthly_credits = defaultdict(float)
    monthly_debits = defaultdict(float)
    
    for txn in transactions:
        try:
            amount = abs(float(str(txn.get('amount', 0) or 0).replace(',', '')))
            date_str = txn.get('date') or ''
            month = normalize_date_to_month(date_str)
            txn_type = (txn.get('type') or '').upper()
            
            if txn_type in ['CREDIT', 'CR', 'C']:
                monthly_credits[month] += amount
            elif txn_type in ['DEBIT', 'DR', 'D']:
                monthly_debits[month] += amount
        except:
            pass
    
    for month in monthly_credits.keys():
        surplus = monthly_credits[month] - monthly_debits.get(month, 0)
        monthly_surplus_values.append(surplus)
    
    avg_monthly_surplus = sum(monthly_surplus_values) / len(monthly_surplus_values) if monthly_surplus_values else 0
    avg_monthly_debits = sum(monthly_debits.values()) / len(monthly_debits) if monthly_debits else 1
    # Working capital gap in days = (Monthly Surplus / Daily Expenses)
    # Daily expenses = Monthly expenses / 30
    daily_expenses = avg_monthly_debits / 30 if avg_monthly_debits > 0 else 1
    working_capital_gap_days = round(avg_monthly_surplus / daily_expenses, 1) if daily_expenses > 0 else 0
    working_capital_gap = working_capital_gap_days
    
    # TTM (Trailing Twelve Months) Revenue Growth
    # Sort months and calculate growth rates
    sorted_months = sorted(monthly_credits.items())
    
    # Credit growth rate: use CAGR if multi-year data, else simple growth
    credit_growth_rate = 0
    credit_growth_cagr = None
    credit_growth_years = 0
    ttm_revenue_growth = 0
    qoq_revenue_growth = 0  # Quarter over Quarter
    
    # Determine years span
    if sorted_months:
        first_month_str = sorted_months[0][0]
        last_month_str = sorted_months[-1][0]
        try:
            first_year = int(first_month_str.split('-')[0])
            last_year = int(last_month_str.split('-')[0])
            credit_growth_years = last_year - first_year
        except Exception:
            credit_growth_years = 0
    
    # Compute CAGR if we have 2+ years
    if credit_growth_years >= 2 and len(sorted_months) >= 12:
        # Aggregate by year
        yearly_revenue = defaultdict(float)
        for month, val in sorted_months:
            try:
                year = int(month.split('-')[0])
                yearly_revenue[year] += val
            except Exception:
                pass
        
        sorted_years = sorted(yearly_revenue.items())
        if len(sorted_years) >= 2:
            first_year_rev = sorted_years[0][1]
            last_year_rev = sorted_years[-1][1]
            n_years = sorted_years[-1][0] - sorted_years[0][0]
            if first_year_rev > 0 and n_years > 0:
                # CAGR = (End/Start)^(1/years) - 1
                credit_growth_cagr = ((last_year_rev / first_year_rev) ** (1.0 / n_years) - 1) * 100
                credit_growth_rate = credit_growth_cagr  # Use CAGR as primary metric
    
    # Fallback to 3-month comparison if insufficient years
    if credit_growth_cagr is None:
        if len(sorted_months) >= 6:
            # Use average of last 3 months vs first 3 months (more stable)
            first_3_months = sum([v for _, v in sorted_months[:3]]) / 3
            last_3_months = sum([v for _, v in sorted_months[-3:]]) / 3
            if first_3_months > 0:
                credit_growth_rate = ((last_3_months - first_3_months) / first_3_months * 100)
        elif len(sorted_months) >= 2:
            first_month_credit = sorted_months[0][1]
            last_month_credit = sorted_months[-1][1]
            if last_month_credit == 0 and len(sorted_months) >= 3:
                last_month_credit = sum([v for _, v in sorted_months[-3:]]) / 3
            if first_month_credit > 0:
                credit_growth_rate = ((last_month_credit - first_month_credit) / first_month_credit * 100)
    
    # TTM and QoQ (unchanged)
    if len(sorted_months) >= 12:
        ttm_last_12 = sum([v for _, v in sorted_months[-12:]])
        if len(sorted_months) >= 24:
            ttm_prev_12 = sum([v for _, v in sorted_months[-24:-12]])
            if ttm_prev_12 > 0:
                ttm_revenue_growth = ((ttm_last_12 - ttm_prev_12) / ttm_prev_12 * 100)
        
        if len(sorted_months) >= 6:
            last_quarter = sum([v for _, v in sorted_months[-3:]])
            prev_quarter = sum([v for _, v in sorted_months[-6:-3]])
            if prev_quarter > 0:
                qoq_revenue_growth = ((last_quarter - prev_quarter) / prev_quarter * 100)
    
    # Expense growth rate: use CAGR if multi-year data
    sorted_expense_months = sorted(monthly_debits.items())
    expense_growth_rate = 0
    expense_growth_cagr = None
    expense_growth_years = 0
    qoq_expense_growth = 0
    
    if sorted_expense_months:
        first_exp_month_str = sorted_expense_months[0][0]
        last_exp_month_str = sorted_expense_months[-1][0]
        try:
            first_exp_year = int(first_exp_month_str.split('-')[0])
            last_exp_year = int(last_exp_month_str.split('-')[0])
            expense_growth_years = last_exp_year - first_exp_year
        except Exception:
            expense_growth_years = 0
    
    # Compute CAGR if we have 2+ years
    if expense_growth_years >= 2 and len(sorted_expense_months) >= 12:
        yearly_expense = defaultdict(float)
        for month, val in sorted_expense_months:
            try:
                year = int(month.split('-')[0])
                yearly_expense[year] += val
            except Exception:
                pass
        
        sorted_exp_years = sorted(yearly_expense.items())
        if len(sorted_exp_years) >= 2:
            first_year_exp = sorted_exp_years[0][1]
            last_year_exp = sorted_exp_years[-1][1]
            n_exp_years = sorted_exp_years[-1][0] - sorted_exp_years[0][0]
            if first_year_exp > 0 and n_exp_years > 0:
                expense_growth_cagr = ((last_year_exp / first_year_exp) ** (1.0 / n_exp_years) - 1) * 100
                expense_growth_rate = expense_growth_cagr
    
    # Fallback to 3-month comparison
    if expense_growth_cagr is None:
        if len(sorted_expense_months) >= 6:
            first_3_months_exp = sum([v for _, v in sorted_expense_months[:3]]) / 3
            last_3_months_exp = sum([v for _, v in sorted_expense_months[-3:]]) / 3
            if first_3_months_exp > 0:
                expense_growth_rate = ((last_3_months_exp - first_3_months_exp) / first_3_months_exp * 100)
        elif len(sorted_expense_months) >= 2:
            first_month_expense = sorted_expense_months[0][1]
            last_month_expense = sorted_expense_months[-1][1]
            if last_month_expense == 0 and len(sorted_expense_months) >= 3:
                last_month_expense = sum([v for _, v in sorted_expense_months[-3:]]) / 3
            if first_month_expense > 0:
                expense_growth_rate = ((last_month_expense - first_month_expense) / first_month_expense * 100)
    
    # QoQ expense
    if len(sorted_expense_months) >= 6:
        last_quarter_exp = sum([v for _, v in sorted_expense_months[-3:]])
        prev_quarter_exp = sum([v for _, v in sorted_expense_months[-6:-3]])
        if prev_quarter_exp > 0:
            qoq_expense_growth = ((last_quarter_exp - prev_quarter_exp) / prev_quarter_exp * 100)
    
    # Profit Margin (Net Surplus / Revenue * 100)
    total_revenue = sum(monthly_credits.values())
    total_expenses = sum(monthly_debits.values())
    net_profit = total_revenue - total_expenses
    profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Operating Cash Flow (approximation: avg monthly surplus × 12)
    annual_operating_cashflow = avg_monthly_surplus * 12
    
    return {
        "gst_turnover": round(gst_turnover, 2),
        "bank_turnover": round(bank_credits, 2),
        "reconciliation_variance": round(reconciliation_variance, 2),
        "reconciliation_ratio": round(reconciliation_ratio, 2) if reconciliation_ratio is not None else None,
        "reconciliation_percent_of_gst": round(percent_of_gst, 2) if percent_of_gst is not None else None,
        "reconciliation_percent_of_bank": round(percent_of_bank, 2) if percent_of_bank is not None else None,
        "working_capital_gap": working_capital_gap,
        "credit_growth_rate": round(credit_growth_rate, 2),
        "credit_growth_cagr": round(credit_growth_cagr, 2) if credit_growth_cagr is not None else None,
        "credit_growth_years": credit_growth_years,
        "expense_growth_rate": round(expense_growth_rate, 2),
        "expense_growth_cagr": round(expense_growth_cagr, 2) if expense_growth_cagr is not None else None,
        "expense_growth_years": expense_growth_years,
        "ttm_revenue_growth": round(ttm_revenue_growth, 2),
        "qoq_revenue_growth": round(qoq_revenue_growth, 2),
        "qoq_expense_growth": round(qoq_expense_growth, 2),
        "profit_margin": round(profit_margin, 2),
        "annual_operating_cashflow": round(annual_operating_cashflow, 2),
        "calculation": {
            "reconciliation_variance": {
                "formula": "Absolute difference and normalized ratios",
                "breakdown": {
                    "GST Reported Turnover": f"₹{gst_turnover:,.2f}",
                    "Bank Account Credits": f"₹{bank_credits:,.2f}",
                    "Absolute Variance": f"₹{reconciliation_variance:,.2f}",
                    "Relative to GST (%)": f"{percent_of_gst:.2f}%" if percent_of_gst is not None else "N/A",
                    "Relative to Bank (%)": f"{percent_of_bank:.2f}%" if percent_of_bank is not None else "N/A",
                    "Legacy Base (Min) used for one-line ratio": f"₹{base_amount:,.2f}" if base_amount is not None else "N/A",
                    "Legacy Variance Ratio": f"{reconciliation_ratio:.2f}%" if reconciliation_ratio is not None else "N/A"
                },
                "explanation": (
                    "Absolute variance shows the rupee difference between GST-reported turnover and bank credits. "
                    "Percentages normalized to GST and to Bank are provided because GST turnover and bank credits measure different concepts (invoice turnover vs cash inflow). "
                    "Large percentages typically indicate mismatches in data coverage or synthetic/demo data extremes; investigate raw GST returns and bank transaction samples before acting."
                )
            },
            "working_capital_gap": {
                "formula": "(Avg Monthly Surplus ÷ Avg Daily Expenses) = Days of runway",
                "breakdown": {
                    "Average Monthly Surplus": f"₹{avg_monthly_surplus:,.2f}",
                    "Average Monthly Expenses": f"₹{avg_monthly_debits:,.2f}",
                    "Average Daily Expenses": f"₹{daily_expenses:,.2f}",
                    "Working Capital Gap": f"{working_capital_gap:.1f} days",
                    "Months Analyzed": len(monthly_surplus_values)
                },
                "explanation": f"Working capital gap of {working_capital_gap:.1f} days means the business can {'sustain operations for ' + str(int(working_capital_gap)) + ' days with current surplus' if working_capital_gap > 0 else 'needs immediate cash injection (negative runway)'}. {'Excellent - >90 days runway' if working_capital_gap > 90 else 'Good - 30-90 days runway' if working_capital_gap > 30 else 'Concerning - <30 days runway' if working_capital_gap > 0 else 'Critical - negative working capital'}."
            },
            "credit_growth_rate": {
                "formula": "CAGR (Compound Annual Growth Rate) when ≥2 years of data; else ((Last 3-Month Avg - First 3-Month Avg) ÷ First 3-Month Avg) × 100",
                "breakdown": {
                    "Years of Data": credit_growth_years,
                    "Method Used": "CAGR (multi-year)" if credit_growth_cagr is not None else "3-month comparison",
                    "Growth Rate": f"{credit_growth_rate:.2f}%",
                    "First 3 Months Avg": f"₹{sum([v for _, v in sorted_months[:3]]) / 3:,.2f}" if len(sorted_months) >= 3 else "N/A",
                    "Last 3 Months Avg": f"₹{sum([v for _, v in sorted_months[-3:]]) / 3:,.2f}" if len(sorted_months) >= 3 else "N/A",
                    "Months Analyzed": len(sorted_months)
                },
                "explanation": (
                    f"Revenue {'grew' if credit_growth_rate > 0 else 'declined'} by {abs(credit_growth_rate):.2f}% "
                    f"({'CAGR over ' + str(credit_growth_years) + ' years' if credit_growth_cagr is not None else 'comparing recent 3-month average to first 3-month average'}). "
                    f"{'Strong growth trajectory' if credit_growth_rate > 20 else 'Moderate growth' if credit_growth_rate > 5 else 'Stable/flat revenue' if credit_growth_rate > -5 else 'Declining revenue - concerning'}. "
                    f"{'CAGR provides annualized growth rate smoothing year-to-year volatility.' if credit_growth_cagr is not None else 'Uses 3-month averaging to reduce noise.'}"
                )
            },
            "ttm_revenue_growth": {
                "formula": "((Last 12 Months Total - Previous 12 Months Total) ÷ Previous 12 Months) × 100",
                "breakdown": {
                    "TTM (Trailing Twelve Months)": f"₹{sum([v for _, v in sorted_months[-12:]]):,.2f}" if len(sorted_months) >= 12 else "N/A",
                    "Previous 12 Months": f"₹{sum([v for _, v in sorted_months[-24:-12]]):,.2f}" if len(sorted_months) >= 24 else "N/A",
                    "YoY Growth": f"{ttm_revenue_growth:.2f}%"
                },
                "explanation": f"Year-over-year revenue growth of {ttm_revenue_growth:.2f}%. {'Excellent - high growth company' if ttm_revenue_growth > 50 else 'Strong growth' if ttm_revenue_growth > 20 else 'Moderate growth' if ttm_revenue_growth > 10 else 'Stable' if ttm_revenue_growth > 0 else 'Declining' if ttm_revenue_growth > -10 else 'Significant decline'}. Similar to stock market TTM analysis."
            },
            "qoq_revenue_growth": {
                "formula": "((Last Quarter - Previous Quarter) ÷ Previous Quarter) × 100",
                "breakdown": {
                    "Last Quarter (3 months)": f"₹{sum([v for _, v in sorted_months[-3:]]):,.2f}" if len(sorted_months) >= 3 else "N/A",
                    "Previous Quarter": f"₹{sum([v for _, v in sorted_months[-6:-3]]):,.2f}" if len(sorted_months) >= 6 else "N/A",
                    "QoQ Growth": f"{qoq_revenue_growth:.2f}%"
                },
                "explanation": f"Quarter-over-quarter growth of {qoq_revenue_growth:.2f}% shows recent momentum. {'Accelerating' if qoq_revenue_growth > credit_growth_rate else 'Decelerating' if qoq_revenue_growth < credit_growth_rate else 'Steady'}. QoQ is more sensitive to recent changes than annual growth."
            },
            "profit_margin": {
                "formula": "((Total Revenue - Total Expenses) ÷ Total Revenue) × 100",
                "breakdown": {
                    "Total Revenue": f"₹{total_revenue:,.2f}",
                    "Total Expenses": f"₹{total_expenses:,.2f}",
                    "Net Profit": f"₹{net_profit:,.2f}",
                    "Profit Margin": f"{profit_margin:.2f}%"
                },
                "explanation": f"Profit margin of {profit_margin:.2f}% indicates {'excellent profitability (>25%)' if profit_margin > 25 else 'good profitability (15-25%)' if profit_margin > 15 else 'moderate profitability (5-15%)' if profit_margin > 5 else 'low profitability (<5%)' if profit_margin > 0 else 'operating at loss'}. Higher margins indicate better cost control."
            },
            "annual_operating_cashflow": {
                "formula": "Average Monthly Surplus × 12",
                "breakdown": {
                    "Monthly Surplus": f"₹{avg_monthly_surplus:,.2f}",
                    "Annualized": f"₹{annual_operating_cashflow:,.2f}"
                },
                "explanation": f"Estimated annual operating cashflow of ₹{annual_operating_cashflow:,.2f}. {'Strong cashflow generation' if annual_operating_cashflow > 1000000 else 'Moderate cashflow' if annual_operating_cashflow > 100000 else 'Weak cashflow' if annual_operating_cashflow > 0 else 'Negative cashflow - burning cash'}."
            },
            "expense_growth_rate": {
                "formula": "CAGR (Compound Annual Growth Rate) when ≥2 years of data; else ((Last 3-Month Avg Expenses - First 3-Month Avg) ÷ First 3-Month Avg) × 100",
                "breakdown": {
                    "Years of Data": expense_growth_years,
                    "Method Used": "CAGR (multi-year)" if expense_growth_cagr is not None else "3-month comparison",
                    "Growth Rate": f"{expense_growth_rate:.2f}%",
                    "First 3 Months Avg": f"₹{sum([v for _, v in sorted_expense_months[:3]]) / 3:,.2f}" if len(sorted_expense_months) >= 3 else "N/A",
                    "Last 3 Months Avg": f"₹{sum([v for _, v in sorted_expense_months[-3:]]) / 3:,.2f}" if len(sorted_expense_months) >= 3 else "N/A"
                },
                "explanation": (
                    f"Expenses {'increased' if expense_growth_rate > 0 else 'decreased'} by {abs(expense_growth_rate):.2f}% "
                    f"({'CAGR over ' + str(expense_growth_years) + ' years' if expense_growth_cagr is not None else 'comparing recent 3-month averages'}). "
                    f"{'Good - expenses under control' if expense_growth_rate < credit_growth_rate else 'Warning - expenses growing faster than revenue' if expense_growth_rate > credit_growth_rate + 10 else 'Expenses tracking with revenue'}. "
                    f"{'CAGR provides annualized expense growth smoothing volatility.' if expense_growth_cagr is not None else 'Expense control is critical for profitability.'}"
                )
            }
        }
    }
