"""
Cashflow Forecasting Module
Provides short-term cashflow forecasts (30-180 days) using exponential smoothing or Holt-Winters.
"""
import json
import os
from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from dateutil import parser as date_parser


def parse_month(month_str):
    """Parse various month formats to YYYY-MM."""
    if not month_str:
        return None
    try:
        # Try standard formats
        for fmt in ['%Y-%m', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y']:
            try:
                dt = datetime.strptime(str(month_str), fmt)
                return dt.strftime('%Y-%m')
            except:
                continue
        
        # Try dateutil parser
        dt = date_parser.parse(str(month_str))
        return dt.strftime('%Y-%m')
    except:
        return None


def exponential_smoothing_forecast(values: List[float], alpha: float = 0.3, periods: int = 6) -> List[float]:
    """
    Simple exponential smoothing for time series forecasting.
    
    Args:
        values: Historical values
        alpha: Smoothing factor (0 < alpha < 1)
        periods: Number of periods to forecast
    
    Returns:
        List of forecasted values
    """
    if not values or len(values) < 2:
        return [values[-1] if values else 0] * periods
    
    # Initialize with first value
    smoothed = [values[0]]
    
    # Smooth historical data
    for i in range(1, len(values)):
        s = alpha * values[i] + (1 - alpha) * smoothed[-1]
        smoothed.append(s)
    
    # Forecast future periods
    forecast = []
    last_smoothed = smoothed[-1]
    
    for _ in range(periods):
        forecast.append(last_smoothed)
    
    return forecast


def holt_winters_forecast(values: List[float], alpha: float = 0.3, beta: float = 0.1, 
                          periods: int = 6, seasonal: bool = True, 
                          seasonal_periods: int = 12) -> List[float]:
    """
    Holt-Winters exponential smoothing with trend and optional seasonality.
    
    Args:
        values: Historical values
        alpha: Level smoothing factor
        beta: Trend smoothing factor
        periods: Number of periods to forecast
        seasonal: Whether to include seasonality
        seasonal_periods: Length of seasonal cycle (e.g., 12 for monthly data)
    
    Returns:
        List of forecasted values
    """
    if not values or len(values) < 2:
        return [values[-1] if values else 0] * periods
    
    n = len(values)
    
    # Initialize level and trend
    level = values[0]
    trend = (values[1] - values[0]) if n > 1 else 0
    
    # Initialize seasonal components if applicable
    seasonal_components = None
    if seasonal and n >= seasonal_periods:
        seasonal_components = []
        for i in range(seasonal_periods):
            indices = [j for j in range(i, n, seasonal_periods)]
            if indices:
                avg = np.mean([values[j] for j in indices])
                overall_avg = np.mean(values[:min(n, seasonal_periods)])
                seasonal_components.append(avg - overall_avg if overall_avg != 0 else 0)
            else:
                seasonal_components.append(0)
    
    # Smooth historical data
    for i in range(1, n):
        last_level = level
        
        if seasonal and seasonal_components:
            s_idx = i % seasonal_periods
            level = alpha * (values[i] - seasonal_components[s_idx]) + (1 - alpha) * (last_level + trend)
        else:
            level = alpha * values[i] + (1 - alpha) * (last_level + trend)
        
        trend = beta * (level - last_level) + (1 - beta) * trend
    
    # Forecast future periods
    forecast = []
    for i in range(periods):
        if seasonal and seasonal_components:
            s_idx = (n + i) % seasonal_periods
            forecast_val = level + (i + 1) * trend + seasonal_components[s_idx]
        else:
            forecast_val = level + (i + 1) * trend
        
        forecast.append(max(0, forecast_val))  # Ensure non-negative
    
    return forecast


def compute_cashflow_forecast(customer_id: str, analytics_dir: str = None, 
                              forecast_days: int = 90) -> Dict:
    """
    Generate cashflow forecast for specified period.
    
    Args:
        customer_id: Customer ID
        analytics_dir: Path to analytics directory
        forecast_days: Number of days to forecast (30, 90, 180)
    
    Returns:
        Dictionary with forecast data and scenarios
    """
    if analytics_dir is None:
        analytics_dir = os.path.join(os.path.dirname(__file__))
    
    print(f"\n[INFO] Generating {forecast_days}-day cashflow forecast for {customer_id}")
    
    # Load earnings_spendings data
    earnings_file = os.path.join(analytics_dir, f'{customer_id}_earnings_spendings.json')
    try:
        with open(earnings_file, 'r', encoding='utf-8') as f:
            earnings_data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Earnings file not found: {earnings_file}")
        return {}
    
    cashflow = earnings_data.get('cashflow_metrics', {})
    monthly_inflow = cashflow.get('monthly_inflow', {})
    monthly_outflow = cashflow.get('monthly_outflow', {})
    
    # Parse and sort months
    inflow_series = []
    outflow_series = []
    months_ordered = []
    
    # Combine all months
    all_months = set(monthly_inflow.keys()) | set(monthly_outflow.keys())
    
    for month_key in all_months:
        parsed = parse_month(month_key)
        if parsed:
            months_ordered.append(parsed)
    
    months_ordered = sorted(list(set(months_ordered)))
    
    # Aggregate by parsed month
    monthly_agg_inflow = defaultdict(float)
    monthly_agg_outflow = defaultdict(float)
    
    for month_key, value in monthly_inflow.items():
        parsed = parse_month(month_key)
        if parsed:
            monthly_agg_inflow[parsed] += value
    
    for month_key, value in monthly_outflow.items():
        parsed = parse_month(month_key)
        if parsed:
            monthly_agg_outflow[parsed] += value
    
    # Build time series
    for month in months_ordered[-24:]:  # Last 24 months
        inflow_series.append(monthly_agg_inflow.get(month, 0))
        outflow_series.append(monthly_agg_outflow.get(month, 0))
    
    if not inflow_series or not outflow_series:
        print("[WARN] No valid cashflow data found")
        return {}
    
    # Calculate forecast periods (months)
    forecast_months = max(1, forecast_days // 30)
    
    # Generate forecasts using both methods
    print(f"  [INFO] Forecasting {forecast_months} months ahead using historical data from {len(inflow_series)} months")
    
    # Exponential smoothing
    inflow_forecast_exp = exponential_smoothing_forecast(inflow_series, alpha=0.3, periods=forecast_months)
    outflow_forecast_exp = exponential_smoothing_forecast(outflow_series, alpha=0.3, periods=forecast_months)
    
    # Holt-Winters with seasonality
    inflow_forecast_hw = holt_winters_forecast(
        inflow_series, alpha=0.3, beta=0.1, periods=forecast_months,
        seasonal=True, seasonal_periods=12
    )
    outflow_forecast_hw = holt_winters_forecast(
        outflow_series, alpha=0.3, beta=0.1, periods=forecast_months,
        seasonal=True, seasonal_periods=12
    )
    
    # Use Holt-Winters as primary forecast (better for seasonal data)
    inflow_forecast = inflow_forecast_hw
    outflow_forecast = outflow_forecast_hw
    
    # Generate forecast months
    last_month = datetime.strptime(months_ordered[-1], '%Y-%m')
    forecast_month_labels = []
    for i in range(1, forecast_months + 1):
        next_month = last_month + timedelta(days=30 * i)
        forecast_month_labels.append(next_month.strftime('%Y-%m'))
    
    # Calculate net surplus forecast
    surplus_forecast = [inf - out for inf, out in zip(inflow_forecast, outflow_forecast)]
    
    # Scenario analysis
    scenarios = {
        'base_case': {
            'inflow': inflow_forecast,
            'outflow': outflow_forecast,
            'surplus': surplus_forecast,
            'cumulative_surplus': [sum(surplus_forecast[:i+1]) for i in range(len(surplus_forecast))]
        },
        'optimistic': {
            'description': 'Inflow +10%, Outflow -5%',
            'inflow': [x * 1.1 for x in inflow_forecast],
            'outflow': [x * 0.95 for x in outflow_forecast],
        },
        'pessimistic': {
            'description': 'Inflow -10%, Outflow +10%',
            'inflow': [x * 0.9 for x in inflow_forecast],
            'outflow': [x * 1.1 for x in outflow_forecast],
        }
    }
    
    # Calculate surplus for scenarios
    for scenario_name, scenario_data in scenarios.items():
        if scenario_name != 'base_case':
            scenario_data['surplus'] = [
                inf - out for inf, out in zip(scenario_data['inflow'], scenario_data['outflow'])
            ]
            scenario_data['cumulative_surplus'] = [
                sum(scenario_data['surplus'][:i+1]) for i in range(len(scenario_data['surplus']))
            ]
    
    # Calculate runway (months until surplus becomes negative)
    current_surplus = cashflow.get('net_surplus', 0)
    runway_months = 0
    cumulative = current_surplus
    
    for monthly_surplus in surplus_forecast:
        cumulative += monthly_surplus
        if cumulative < 0:
            break
        runway_months += 1
    
    # Risk assessment
    risk_flags = []
    if any(s < 0 for s in surplus_forecast):
        risk_flags.append('Negative surplus expected in forecast period')
    if runway_months < 3 and current_surplus < np.mean(outflow_series[-3:]) * 2:
        risk_flags.append('Insufficient cash buffer (< 2 months of expenses)')
    if np.std(inflow_series[-6:]) / np.mean(inflow_series[-6:]) > 0.5:
        risk_flags.append('High income volatility detected')
    
    # Recommendations
    recommendations = []
    if runway_months < 6:
        recommendations.append(f'Build cash reserves: Current runway is only {runway_months} months')
    if any(s < 0 for s in scenarios['pessimistic']['surplus']):
        recommendations.append('Consider contingency planning for downside scenarios')
    if np.mean(outflow_series[-3:]) > np.mean(inflow_series[-3:]) * 0.8:
        recommendations.append('High expense ratio: Consider cost optimization')
    
    # Compile result
    result = {
        'customer_id': customer_id,
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'forecast_period': {
            'days': forecast_days,
            'months': forecast_months,
            'forecast_labels': forecast_month_labels
        },
        'historical_summary': {
            'avg_monthly_inflow': round(np.mean(inflow_series), 2),
            'avg_monthly_outflow': round(np.mean(outflow_series), 2),
            'avg_monthly_surplus': round(np.mean(inflow_series) - np.mean(outflow_series), 2),
            'inflow_volatility_cv': round(np.std(inflow_series) / np.mean(inflow_series) * 100, 2) if np.mean(inflow_series) > 0 else 0,
            'months_analyzed': len(inflow_series)
        },
        'forecast': {
            'monthly_inflow': [round(x, 2) for x in inflow_forecast],
            'monthly_outflow': [round(x, 2) for x in outflow_forecast],
            'monthly_surplus': [round(x, 2) for x in surplus_forecast],
            'cumulative_surplus': [round(x, 2) for x in scenarios['base_case']['cumulative_surplus']],
            'total_expected_inflow': round(sum(inflow_forecast), 2),
            'total_expected_outflow': round(sum(outflow_forecast), 2),
            'total_expected_surplus': round(sum(surplus_forecast), 2)
        },
        'scenarios': {
            scenario_name: {
                'description': scenario_data.get('description', 'Base case'),
                'total_inflow': round(sum(scenario_data['inflow']), 2),
                'total_outflow': round(sum(scenario_data['outflow']), 2),
                'total_surplus': round(sum(scenario_data['surplus']), 2),
                'final_cumulative': round(scenario_data['cumulative_surplus'][-1], 2) if scenario_data['cumulative_surplus'] else 0
            }
            for scenario_name, scenario_data in scenarios.items()
        },
        'risk_assessment': {
            'runway_months': runway_months,
            'runway_days': runway_months * 30,
            'current_surplus': round(current_surplus, 2),
            'risk_flags': risk_flags,
            'risk_level': 'High' if len(risk_flags) >= 2 else 'Medium' if risk_flags else 'Low'
        },
        'recommendations': recommendations,
        'methodology': {
            'primary_method': 'Holt-Winters Exponential Smoothing',
            'seasonal': True,
            'seasonal_periods': 12,
            'alpha': 0.3,
            'beta': 0.1,
            'fallback_method': 'Simple Exponential Smoothing'
        }
    }
    
    # Save to file
    output_file = os.path.join(analytics_dir, f'{customer_id}_cashflow_forecast.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"[✓] Forecast saved to {output_file}")
    print(f"\n{'='*60}")
    print(f"CASHFLOW FORECAST SUMMARY ({forecast_days} days)")
    print(f"{'='*60}")
    print(f"Expected Total Inflow:  ₹{result['forecast']['total_expected_inflow']:,.2f}")
    print(f"Expected Total Outflow: ₹{result['forecast']['total_expected_outflow']:,.2f}")
    print(f"Expected Net Surplus:   ₹{result['forecast']['total_expected_surplus']:,.2f}")
    print(f"\nRunway: {runway_months} months ({runway_months * 30} days)")
    print(f"Risk Level: {result['risk_assessment']['risk_level']}")
    
    if risk_flags:
        print(f"\n⚠️  Risk Flags:")
        for flag in risk_flags:
            print(f"  • {flag}")
    
    if recommendations:
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"  • {rec}")
    
    print(f"{'='*60}\n")
    
    return result


if __name__ == '__main__':
    import sys
    
    customer_id = sys.argv[1] if len(sys.argv) > 1 else 'CUST_MSM_00001'
    analytics_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(__file__)
    forecast_days = int(sys.argv[3]) if len(sys.argv) > 3 else 90
    
    compute_cashflow_forecast(customer_id, analytics_dir, forecast_days)
