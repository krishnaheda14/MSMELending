import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, DollarSign, Activity, PieChart, BarChart3, ArrowUpCircle, ArrowDownCircle, Info } from 'lucide-react';
import { formatCurrency, formatPercent, formatNumber } from '../utils/formatters';

const FinancialSummary = () => {
  const [customerId, setCustomerId] = useState(() => {
    try { return localStorage.getItem('msme_customer_id') || 'CUST_MSM_00001'; } catch (e) { return 'CUST_MSM_00001'; }
  });
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showCalculation, setShowCalculation] = useState(null);
  const [showExpenseTxns, setShowExpenseTxns] = useState(null);

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

  // Calculation Modal Component
  const CalculationModal = ({ metric, onClose }) => {
    if (!metric) return null;

    const { title, calculation } = metric;
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
        <div className="bg-white rounded-lg p-6 max-w-3xl max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-xl font-bold text-gray-800">{title}</h3>
            <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-2xl">×</button>
          </div>

          {/* Buttons to open raw entries from top-level payload */}
          {data && (
            <div className="mb-4">
              <h4 className="font-semibold text-gray-700 mb-2">Raw Entries</h4>
              <div className="space-y-2">
                {/* Raw entries links removed per UI cleanup */}
              </div>
            </div>
          )}
          
          {calculation && (
            <>
              {calculation.formula && (
                <div className="mb-4">
                  <h4 className="font-semibold text-gray-700 mb-2">Formula:</h4>
                  <div className="bg-blue-50 p-3 rounded font-mono text-sm text-blue-900">{calculation.formula}</div>
                </div>
              )}
              
              {calculation.explanation && (
                <div className="mb-4">
                  <h4 className="font-semibold text-gray-700 mb-2">Explanation:</h4>
                  <p className="text-gray-600 leading-relaxed">{calculation.explanation}</p>
                </div>
              )}
              
              {calculation.breakdown && (
                <div className="mb-4">
                  <h4 className="font-semibold text-gray-700 mb-2">Calculation Breakdown:</h4>
                  <div className="space-y-2">
                    {Object.entries(calculation.breakdown).map(([key, value]) => {
                      const renderValue = (v) => {
                        if (v === null || v === undefined) return 'N/A';
                        if (Array.isArray(v)) return v.join(', ');
                        if (typeof v === 'object') {
                          return (
                            <div className="space-y-1 text-right">
                              {Object.entries(v).map(([k, val]) => (
                                <div key={k} className="text-sm">
                                  <span className="text-gray-500">{k}:</span>
                                  <span className="font-semibold text-gray-900 ml-2">{typeof val === 'number' ? formatNumber(val) : val}</span>
                                </div>
                              ))}
                            </div>
                          );
                        }
                        if (typeof v === 'number') return formatNumber(v);
                        return v;
                      };

                      return (
                        <div key={key} className="flex justify-between bg-gray-50 p-3 rounded hover:bg-gray-100">
                          <span className="text-gray-700 font-medium">{key}:</span>
                          <span className="font-semibold text-gray-900">{renderValue(value)}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </>
          )}
          
          <button
            onClick={onClose}
            className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
          >
            Close
          </button>
        </div>
      </div>
    );
  };

  // Calculate key P&L metrics
  const totalRevenue = cashflow_metrics?.total_inflow || 0;
  const totalExpenses = cashflow_metrics?.total_outflow || 0;
  const operatingProfit = cashflow_metrics?.net_surplus || 0;
  const operatingProfitMargin = business_health?.profit_margin || cashflow_metrics?.surplus_ratio || 0;
  
  // Create detailed operating profit calculation
  const operatingProfitCalculation = {
    formula: "Total Revenue (Inflow) − Total Expenses (Outflow)",
    breakdown: {
      "Total Revenue (Credits)": `₹${formatNumber(totalRevenue)}`,
      "Total Expenses (Debits)": `₹${formatNumber(totalExpenses)}`,
      "Operating Profit (Net Surplus)": `₹${formatNumber(operatingProfit)}`,
      "Operating Profit Margin": `${formatNumber(operatingProfitMargin)}%`
    },
    explanation: `Operating profit of ₹${formatNumber(operatingProfit)} calculated as Total Revenue (₹${formatNumber(totalRevenue)}) minus Total Expenses (₹${formatNumber(totalExpenses)}). Operating Profit Margin of ${formatNumber(operatingProfitMargin)}% indicates ${operatingProfitMargin > 20 ? 'strong profitability' : operatingProfitMargin > 10 ? 'healthy margins' : operatingProfitMargin > 0 ? 'positive but thin margins' : 'unprofitable operations'}. This represents the business's core operational efficiency before interest, taxes, and non-operating items.`
  };
  
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

  const StatCard = ({ title, value, subtitle, icon: Icon, trend, trendValue, color = 'blue', calculation }) => {
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
            <div className="flex items-center gap-2">
              <p className="text-sm font-medium opacity-75">{title}</p>
              {calculation && (
                <button
                  onClick={() => setShowCalculation({ title, calculation })}
                  className="text-blue-500 hover:text-blue-700"
                  title="Show calculation"
                >
                  <Info className="w-4 h-4" />
                </button>
              )}
            </div>
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
      {/* Calculation Modal */}
      {showCalculation && (
        <CalculationModal
          metric={showCalculation}
          onClose={() => setShowCalculation(null)}
        />
      )}

      {showExpenseTxns && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setShowExpenseTxns(null)}>
          <div className="bg-white rounded-lg p-6 max-w-3xl max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-bold text-gray-800">{showExpenseTxns.type === 'raw_entries' ? 'Raw Entries' : `Transactions — ${showExpenseTxns.type.replace(/_/g, ' ')}`}</h3>
              <button onClick={() => setShowExpenseTxns(null)} className="text-gray-500 hover:text-gray-700 text-2xl">×</button>
            </div>

            {showExpenseTxns.type === 'raw_entries' ? (
              <div className="space-y-6">
                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">Top 10 Expenses</h4>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Merchant / Description</th>
                          <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {(Array.isArray(showExpenseTxns.txns?.top_10) && showExpenseTxns.txns.top_10.length > 0) ? showExpenseTxns.txns.top_10.map((t, i) => (
                          <tr key={`top_${i}`}>
                            <td className="px-4 py-2 text-sm text-gray-700">{t.date || t.transaction_date || '-'}</td>
                            <td className="px-4 py-2 text-sm text-gray-700">{t.merchant || t.description || t.narration || t.counterparty || '-'}</td>
                            <td className="px-4 py-2 text-sm text-right text-gray-700">{formatCurrency(t.amount || t.value || t.order_value || t.total_amount || 0)}</td>
                          </tr>
                        )) : (
                          <tr><td colSpan="3" className="p-4 text-center text-gray-500">No top-10 expense entries available.</td></tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">Unknown / Uncategorized Samples</h4>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Source / Narration</th>
                          <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {(Array.isArray(showExpenseTxns.txns?.unknown) && showExpenseTxns.txns.unknown.length > 0) ? showExpenseTxns.txns.unknown.map((t, i) => (
                          <tr key={`unk_${i}`}>
                            <td className="px-4 py-2 text-sm text-gray-700">{t.date || t.txn_date || '-'}</td>
                            <td className="px-4 py-2 text-sm text-gray-700">{t.merchant || t.narration || t.description || t.source || '-'}</td>
                            <td className="px-4 py-2 text-sm text-right text-gray-700">{formatCurrency(t.amount || t.value || 0)}</td>
                          </tr>
                        )) : (
                          <tr><td colSpan="3" className="p-4 text-center text-gray-500">No unknown samples available.</td></tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Merchant / Narration</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {(Array.isArray(showExpenseTxns.txns) && showExpenseTxns.txns.length > 0) ? showExpenseTxns.txns.map((t, i) => (
                      <tr key={i}>
                        <td className="px-4 py-2 text-sm text-gray-700">{t.date || t.txn_date || '-'}</td>
                        <td className="px-4 py-2 text-sm text-gray-700">{t.merchant || t.description || t.narration || '-'}</td>
                        <td className="px-4 py-2 text-sm text-right text-gray-700">{formatCurrency(t.amount || t.value || 0)}</td>
                      </tr>
                    )) : (
                      <tr><td colSpan="3" className="p-4 text-center text-gray-500">No sample transactions available.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

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
        <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center justify-between">
          <DollarSign className="w-6 h-6 mr-2" />
          <span>Income Statement (P&L)</span>
          <button onClick={() => setShowExpenseTxns({ type: 'raw_entries', txns: { top_10: data.expense_composition?.top_10_expenses || [], unknown: data.unknown_samples || [] } })} className="text-sm text-blue-600 hover:text-blue-800">Show raw entries</button>
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
            calculation={operatingProfitCalculation}
          />
          <StatCard
            title="Total Expenses (Outflow)"
            value={formatCurrency(totalExpenses)}
            subtitle="All operating costs"
            icon={TrendingDown}
            color="orange"
            trend={expenseGrowth > 0 ? 'up' : 'down'}
            trendValue={business_health?.expense_growth_years >= 2 && business_health?.expense_growth_cagr != null
              ? `${formatPercent(Math.abs(expenseGrowth))} CAGR (${business_health.expense_growth_years}Y)`
              : `${formatPercent(Math.abs(expenseGrowth))} growth`}
            calculation={operatingProfitCalculation}
          />
          <StatCard
            title="Operating Profit"
            value={formatCurrency(operatingProfit)}
            subtitle={`${formatPercent(operatingProfitMargin)} margin`}
            icon={Activity}
            color={operatingProfit > 0 ? 'green' : 'red'}
            calculation={operatingProfitCalculation}
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
            title={business_health?.credit_growth_years >= 2 && business_health?.credit_growth_cagr != null 
              ? `Revenue Growth (CAGR ${business_health.credit_growth_years}Y)` 
              : "Revenue Growth (3-Month)"}
            value={formatPercent(creditGrowth)}
            subtitle={business_health?.credit_growth_years >= 2 ? "Compound annual" : "Recent trend"}
            icon={TrendingUp}
            color={creditGrowth > 0 ? 'green' : 'red'}
            calculation={business_health?.calculation?.credit_growth_rate}
          />
          <StatCard
            title="TTM Revenue Growth"
            value={formatPercent(ttmGrowth)}
            subtitle="Year-over-year"
            icon={TrendingUp}
            color={ttmGrowth > 0 ? 'green' : 'red'}
            calculation={business_health?.calculation?.ttm_revenue_growth}
          />
          <StatCard
            title="QoQ Revenue Growth"
            value={formatPercent(qoqGrowth)}
            subtitle="Quarter momentum"
            icon={TrendingUp}
            color={qoqGrowth > 0 ? 'green' : 'red'}
            calculation={business_health?.calculation?.qoq_revenue_growth}
          />
          <StatCard
            title="Operating Profit Margin"
            value={formatPercent(operatingProfitMargin)}
            subtitle="Net profitability"
            icon={PieChart}
            color={operatingProfitMargin > 25 ? 'green' : operatingProfitMargin > 15 ? 'blue' : 'orange'}
          />
        </div>
      </div>

      {/* Cashflow & Liquidity */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center justify-between">
          <Activity className="w-6 h-6 mr-2" />
          <span>Cashflow & Liquidity</span>
          <button onClick={() => setShowExpenseTxns({ type: 'raw_entries', txns: { top_10: data.expense_composition?.top_10_expenses || [], unknown: data.unknown_samples || [] } })} className="text-sm text-blue-600 hover:text-blue-800">Show raw entries</button>
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
            calculation={business_health?.calculation?.working_capital_gap}
          />
          <StatCard
            title="Operating Profit Margin (Cashflow)"
            value={formatPercent(operatingProfitMargin)}
            subtitle="Savings per ₹100 earned"
            color="purple"
          />
        </div>
      </div>

      {/* Debt & Loan Metrics */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center justify-between">
          <DollarSign className="w-6 h-6 mr-2" />
          <span>Debt & Loan Analysis</span>
          <button onClick={() => setShowExpenseTxns({ type: 'raw_entries', txns: { top_10: data.expense_composition?.top_10_expenses || [], unknown: data.unknown_samples || [] } })} className="text-sm text-blue-600 hover:text-blue-800">Show raw entries</button>
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
        <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center justify-between">
          <PieChart className="w-6 h-6 mr-2" />
          <span>Expense Composition</span>
          <button onClick={() => setShowExpenseTxns({ type: 'raw_entries', txns: { top_10: data.expense_composition?.top_10_expenses || [], unknown: data.unknown_samples || [] } })} className="text-sm text-blue-600 hover:text-blue-800">Show raw entries</button>
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
            <p className="text-sm text-gray-600 font-medium">Operating Profit Margin</p>
            <p className="text-3xl font-bold text-blue-600">{formatPercent(operatingProfitMargin)}</p>
          </div>
          <div className="col-span-2 flex items-center justify-end">
            <button onClick={() => setShowExpenseTxns({ type: 'raw_entries', txns: { top_10: data.expense_composition?.top_10_expenses || [], unknown: data.unknown_samples || [] } })} className="text-sm text-blue-600 hover:text-blue-800">Show raw entries</button>
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
