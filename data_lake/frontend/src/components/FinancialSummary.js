import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, DollarSign, Activity, PieChart, BarChart3, ArrowUpCircle, ArrowDownCircle } from 'lucide-react';
import { formatCurrency, formatPercent, formatNumber } from '../utils/formatters';

const FinancialSummary = () => {
  const [customerId, setCustomerId] = useState(() => {
    try { return localStorage.getItem('msme_customer_id') || 'CUST_MSM_00001'; } catch (e) { return 'CUST_MSM_00001'; }
  });
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    if (!customerId) return;
    
    setLoading(true);
    setError(null);
    
    try {
        try { localStorage.setItem('msme_customer_id', customerId); } catch (e) { /* ignore */ }
        const url = `/api/earnings-spendings?customer_id=${encodeURIComponent(customerId)}`;
        const response = await fetch(url);
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || 'Failed to fetch data');
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (customerId) fetchData();
    const handleStorage = (e) => {
      if (e.key === 'msme_customer_id' && e.newValue) {
        setCustomerId(e.newValue);
      }
    };
    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, [customerId]);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      fetchData();
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading financial data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
          <p className="font-bold">Error</p>
          <p>{error}</p>
          <p className="mt-2 text-sm">Make sure analytics are generated for customer: {customerId}</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
          <p>No data available. Please generate analytics first.</p>
        </div>
      </div>
    );
  }

  const { cashflow_metrics, business_health, credit_behavior, expense_composition } = data;

  // Calculate key P&L metrics
  const totalRevenue = cashflow_metrics?.total_inflow || 0;
  const totalExpenses = cashflow_metrics?.total_outflow || 0;
  const netProfit = cashflow_metrics?.net_surplus || 0;
  const profitMargin = business_health?.profit_margin || 0;
  
  // Loan metrics
  const totalLoanPayments = (credit_behavior?.debt_to_income_ratio / 100) * totalRevenue || 0;
  const emiCount = credit_behavior?.emi_count || 0;
  
  // Growth metrics
  const creditGrowth = business_health?.credit_growth_rate || 0;
  const ttmGrowth = business_health?.ttm_revenue_growth || 0;
  const qoqGrowth = business_health?.qoq_revenue_growth || 0;
  const expenseGrowth = business_health?.expense_growth_rate || 0;
  
  // Cashflow metrics
  const annualCashflow = business_health?.annual_operating_cashflow || 0;
  const workingCapitalDays = business_health?.working_capital_gap || 0;
  
  // Expense breakdown
  const essentialSpending = expense_composition?.essential_spend || 0;
  const nonEssentialSpending = expense_composition?.non_essential_spend || 0;
  const debtServicing = expense_composition?.debt_servicing || 0;

  const StatCard = ({ title, value, subtitle, icon: Icon, trend, trendValue, color = 'blue' }) => {
    const colorClasses = {
      blue: 'bg-blue-50 border-blue-200 text-blue-800',
      green: 'bg-green-50 border-green-200 text-green-800',
      red: 'bg-red-50 border-red-200 text-red-800',
      purple: 'bg-purple-50 border-purple-200 text-purple-800',
      orange: 'bg-orange-50 border-orange-200 text-orange-800',
      gray: 'bg-gray-50 border-gray-200 text-gray-800'
    };

    return (
      <div className={`border-2 rounded-lg p-4 ${colorClasses[color]}`}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium opacity-75">{title}</p>
            <p className="text-2xl font-bold mt-1">{value}</p>
            {subtitle && <p className="text-sm opacity-75 mt-1">{subtitle}</p>}
          </div>
          {Icon && (
            <div className="ml-3">
              <Icon className="w-8 h-8 opacity-50" />
            </div>
          )}
        </div>
        {trend && (
          <div className="mt-3 flex items-center">
            {trend === 'up' ? (
              <ArrowUpCircle className="w-4 h-4 text-green-600 mr-1" />
            ) : (
              <ArrowDownCircle className="w-4 h-4 text-red-600 mr-1" />
            )}
            <span className={`text-sm font-medium ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
              {trendValue}
            </span>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="p-6 space-y-6">
      {/* Customer Selection */}
      <div className="bg-white p-4 rounded-lg shadow-md">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Customer ID
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter Customer ID"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
          >
            Load Data
          </button>
        </div>
      </div>

      {/* Customer Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-800 text-white p-6 rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold mb-2">Financial Summary & P&L Statement</h1>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xl font-semibold">{customerId}</p>
            <p className="text-purple-100 text-sm mt-1">Comprehensive Financial Overview</p>
          </div>
          <div className="text-right text-sm">
            <p className="text-purple-100">Generated: {new Date(data.generated_at).toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Income Statement Section */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
          <DollarSign className="w-6 h-6 mr-2" />
          Income Statement (P&L)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatCard
            title="Total Revenue (Inflow)"
            value={formatCurrency(totalRevenue)}
            subtitle="All income sources"
            icon={TrendingUp}
            color="green"
            trend={creditGrowth > 0 ? 'up' : 'down'}
            trendValue={`${formatPercent(Math.abs(creditGrowth))} growth`}
          />
          <StatCard
            title="Total Expenses (Outflow)"
            value={formatCurrency(totalExpenses)}
            subtitle="All operating costs"
            icon={TrendingDown}
            color="orange"
            trend={expenseGrowth > 0 ? 'up' : 'down'}
            trendValue={`${formatPercent(Math.abs(expenseGrowth))} growth`}
          />
          <StatCard
            title="Net Profit (Surplus)"
            value={formatCurrency(netProfit)}
            subtitle={`${formatPercent(profitMargin)} margin`}
            icon={Activity}
            color={netProfit > 0 ? 'green' : 'red'}
          />
        </div>
      </div>

      {/* Growth Metrics Section */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
          <BarChart3 className="w-6 h-6 mr-2" />
          Growth & Performance Metrics
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard
            title="Revenue Growth (3-Month)"
            value={formatPercent(creditGrowth)}
            subtitle="Recent trend"
            icon={TrendingUp}
            color={creditGrowth > 0 ? 'green' : 'red'}
          />
          <StatCard
            title="TTM Revenue Growth"
            value={formatPercent(ttmGrowth)}
            subtitle="Year-over-year"
            icon={TrendingUp}
            color={ttmGrowth > 0 ? 'green' : 'red'}
          />
          <StatCard
            title="QoQ Revenue Growth"
            value={formatPercent(qoqGrowth)}
            subtitle="Quarter momentum"
            icon={TrendingUp}
            color={qoqGrowth > 0 ? 'green' : 'red'}
          />
          <StatCard
            title="Profit Margin"
            value={formatPercent(profitMargin)}
            subtitle="Net profitability"
            icon={PieChart}
            color={profitMargin > 25 ? 'green' : profitMargin > 15 ? 'blue' : 'orange'}
          />
        </div>
      </div>

      {/* Cashflow & Liquidity */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
          <Activity className="w-6 h-6 mr-2" />
          Cashflow & Liquidity
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatCard
            title="Annual Operating Cashflow"
            value={formatCurrency(annualCashflow)}
            subtitle="Estimated yearly"
            icon={Activity}
            color="blue"
          />
          <StatCard
            title="Working Capital Gap"
            value={`${formatNumber(workingCapitalDays)} days`}
            subtitle={workingCapitalDays > 90 ? 'Excellent runway' : workingCapitalDays > 30 ? 'Good runway' : 'Tight cashflow'}
            color={workingCapitalDays > 90 ? 'green' : workingCapitalDays > 30 ? 'blue' : 'red'}
          />
          <StatCard
            title="Surplus Ratio"
            value={formatPercent(cashflow_metrics?.surplus_ratio || 0)}
            subtitle="Savings per ₹100 earned"
            color="purple"
          />
        </div>
      </div>

      {/* Debt & Loan Metrics */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
          <DollarSign className="w-6 h-6 mr-2" />
          Debt & Loan Analysis
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard
            title="Total Loan Payments"
            value={formatCurrency(totalLoanPayments)}
            subtitle={`${emiCount} EMI transactions`}
            icon={DollarSign}
            color="orange"
          />
          <StatCard
            title="Debt Servicing Ratio"
            value={formatPercent(expense_composition?.debt_servicing_ratio || 0)}
            subtitle="Of total expenses"
            color={expense_composition?.debt_servicing_ratio > 40 ? 'red' : 'blue'}
          />
          <StatCard
            title="Debt-to-Income Ratio"
            value={formatPercent(credit_behavior?.debt_to_income_ratio || 0)}
            subtitle="Debt burden"
            color={credit_behavior?.debt_to_income_ratio > 40 ? 'red' : credit_behavior?.debt_to_income_ratio > 30 ? 'orange' : 'green'}
          />
          <StatCard
            title="EMI Consistency Score"
            value={`${credit_behavior?.emi_consistency_score || 0}/100`}
            subtitle="Payment regularity"
            color={credit_behavior?.emi_consistency_score > 90 ? 'green' : 'orange'}
          />
        </div>
      </div>

      {/* Expense Breakdown */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
          <PieChart className="w-6 h-6 mr-2" />
          Expense Composition
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatCard
            title="Essential Spending"
            value={formatCurrency(essentialSpending)}
            subtitle={`${formatPercent(expense_composition?.essential_ratio || 0)} of expenses`}
            color="blue"
          />
          <StatCard
            title="Non-Essential Spending"
            value={formatCurrency(nonEssentialSpending)}
            subtitle="Discretionary costs"
            color="purple"
          />
          <StatCard
            title="Debt Servicing"
            value={formatCurrency(debtServicing)}
            subtitle="Loan repayments"
            color="orange"
          />
        </div>
      </div>

      {/* Key Ratios Summary */}
      <div className="bg-white p-6 rounded-lg shadow-lg border-2 border-gray-200">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Key Financial Ratios</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <p className="text-sm text-gray-600 font-medium">Profit Margin</p>
            <p className="text-3xl font-bold text-blue-600">{formatPercent(profitMargin)}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 font-medium">Inflow/Outflow Ratio</p>
            <p className="text-3xl font-bold text-blue-600">{formatNumber(cashflow_metrics?.inflow_outflow_ratio || 0)}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 font-medium">TTM Growth</p>
            <p className="text-3xl font-bold text-green-600">{formatPercent(ttmGrowth)}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 font-medium">Working Capital</p>
            <p className="text-3xl font-bold text-purple-600">{formatNumber(workingCapitalDays)}d</p>
          </div>
        </div>
      </div>

      {/* Business Health Score */}
      {data.overall_summary && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg shadow-lg border-2 border-blue-200">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Overall Business Health Score</h2>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-5xl font-bold text-blue-600">{data.overall_summary.business_health}/100</p>
              <p className="text-gray-600 mt-2">Composite business health rating</p>
            </div>
            {data.overall_summary.business_health_contributors && (
              <div className="text-right text-sm text-gray-600">
                <p>GST Businesses: {data.overall_summary.business_health_contributors.gst_businesses}</p>
                <p>GST Turnover: {formatCurrency(data.overall_summary.business_health_contributors.gst_turnover)}</p>
                <p>MF Portfolios: {data.overall_summary.business_health_contributors.mutual_fund_portfolios}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default FinancialSummary;
