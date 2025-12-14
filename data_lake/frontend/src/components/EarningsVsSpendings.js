import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Info, TrendingUp, TrendingDown, AlertCircle, CheckCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { formatCurrency, formatNumber, formatPercent } from '../utils/formatters';

const EarningsVsSpendings = () => {
  const [customerId, setCustomerId] = useState(() => {
    try { return localStorage.getItem('msme_customer_id') || 'CUST_MSM_00001'; } catch (e) { return 'CUST_MSM_00001'; }
  });
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showCalculation, setShowCalculation] = useState(null);
  const [showExpenseTxns, setShowExpenseTxns] = useState(null);
  const [expandedCashflow, setExpandedCashflow] = useState(false);

  useEffect(() => {
    if (customerId) {
      fetchData();
    }
    const handleStorage = (e) => {
      if (e.key === 'msme_customer_id' && e.newValue) {
        setCustomerId(e.newValue);
      }
    };
    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, [customerId]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`/api/earnings-spendings?customer_id=${customerId}`);
      setData(response.data);
    } catch (error) {
      console.error('Error fetching earnings vs spendings data:', error);
      setError(error.response?.data?.error || 'Failed to load data. Have you generated analytics for this customer?');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading financial data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center bg-red-50 p-6 rounded-lg">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-700">{error}</p>
          <button
            onClick={fetchData}
            className="mt-4 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-8 text-gray-500">
        No Earnings vs Spendings data available
      </div>
    );
  }

  const CalculationModal = ({ metric, calculation, onClose }) => {
    if (!calculation) return null;

    // Extract the specific calculation for this metric
    const metricKey = metric.toLowerCase().replace(/ /g, '_').replace(/[()]/g, '');
    let calcData = calculation[metricKey] || calculation;

    // If we received the parent calculation object (no direct formula), try to locate nested metric entry
    if (calcData && !calcData.formula && typeof calculation === 'object') {
      const variants = [
        metricKey,
        metricKey.replace(/[^a-z0-9]/g, ''),
        metricKey + '_variance',
        metricKey + '_ratio',
        'reconciliation_variance',
        'reconciliation_ratio',
        'total_expenses',
        'non_essential_spend',
        'essential_spend',
        'income_stability_cv',
        'seasonality_index'
      ];
      for (const v of variants) {
        if (calculation[v]) { calcData = calculation[v]; break; }
      }
      if ((!calcData || !calcData.formula) && typeof calculation === 'object') {
        // try fuzzy match by token
        const tokens = metricKey.split('_').filter(Boolean);
        for (const k of Object.keys(calculation)) {
          if (tokens.some(t => k.includes(t))) { calcData = calculation[k]; break; }
        }
      }
    }

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
        <div className="bg-white rounded-lg p-6 max-w-2xl max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-xl font-bold text-gray-800">{metric}</h3>
            <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-2xl">×</button>
          </div>
          
          {calcData.formula && (
            <div className="mb-4">
              <h4 className="font-semibold text-gray-700 mb-2">Formula:</h4>
              <div className="bg-blue-50 p-3 rounded font-mono text-sm text-blue-900">{calcData.formula}</div>
            </div>
          )}
          
          {calcData.explanation && (
            <div className="mb-4">
              <h4 className="font-semibold text-gray-700 mb-2">Explanation:</h4>
              <p className="text-gray-600 leading-relaxed">{calcData.explanation}</p>
            </div>
          )}
          
          {calcData.breakdown && (
            <div className="mb-4">
              <h4 className="font-semibold text-gray-700 mb-2">Calculation Breakdown:</h4>
              <div className="space-y-2">
                {Object.entries(calcData.breakdown).map(([key, value]) => {
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

          {/* If calculation contains sample transactions, render link to show them */}
          {calcData && calcData.sample_transactions && (
            <div className="mb-4">
              <h4 className="font-semibold text-gray-700 mb-2">Sample Transactions</h4>
              <div className="space-y-2">
                {Object.entries(calcData.sample_transactions).map(([k, v]) => (
                  <div key={k} className="flex justify-between items-center">
                    <div className="text-sm text-gray-700">{k.replace(/_/g, ' ')}: {v.length} sample(s)</div>
                    <button className="text-blue-600" onClick={() => { onClose(); setTimeout(() => setShowExpenseTxns({ type: k, txns: v }), 100); }}>Show transactions</button>
                  </div>
                ))}
              </div>
            </div>
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

  const MetricCard = ({ title, value, unit, trend, calculation, status }) => {
    const getStatusColor = () => {
      if (status === 'positive') return 'text-green-600';
      if (status === 'negative') return 'text-red-600';
      return 'text-gray-600';
    };

    const getTrendIcon = () => {
      if (trend === 'increasing') return <TrendingUp className="w-4 h-4 text-green-600" />;
      if (trend === 'decreasing') return <TrendingDown className="w-4 h-4 text-red-600" />;
      return null;
    };

    // Format value based on unit
    const formattedValue = unit === '₹' ? formatCurrency(value).replace('₹', '') : 
                          unit === '%' ? formatNumber(value) : 
                          formatNumber(value);

    return (
      <div className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow">
        <div className="flex justify-between items-start mb-2">
          <h4 className="text-sm font-medium text-gray-600">{title}</h4>
          {calculation && (
            <button
              onClick={() => setShowCalculation({ metric: title, calculation })}
              className="text-blue-500 hover:text-blue-700"
            >
              <Info className="w-4 h-4" />
            </button>
          )}
        </div>
        <div className="flex items-end justify-between">
          <div>
            <span className={`text-2xl font-bold ${getStatusColor()}`}>
              {formattedValue}
            </span>
            {unit && <span className="text-sm text-gray-500 ml-1">{unit}</span>}
          </div>
          {getTrendIcon()}
        </div>
      </div>
    );
  };

  // Using imported formatters from utils/formatters.js

  const { cashflow_metrics, expense_composition, credit_behavior, business_health } = data;

  return (
    <div className="space-y-6 p-4">
      {showCalculation && (
        <CalculationModal
          metric={showCalculation.metric}
          calculation={showCalculation.calculation}
          onClose={() => setShowCalculation(null)}
        />
      )}

      {showExpenseTxns && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setShowExpenseTxns(null)}>
          <div className="bg-white rounded-lg p-6 max-w-3xl max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-bold text-gray-800">Transactions — {showExpenseTxns.type.replace(/_/g, ' ')}</h3>
              <button onClick={() => setShowExpenseTxns(null)} className="text-gray-500 hover:text-gray-700 text-2xl">×</button>
            </div>
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
                  {showExpenseTxns.txns && showExpenseTxns.txns.length > 0 ? showExpenseTxns.txns.map((t, i) => (
                    <tr key={i}>
                      <td className="px-4 py-2 text-sm text-gray-700">{t.date}</td>
                      <td className="px-4 py-2 text-sm text-gray-700">{t.merchant} {t.narration ? '— ' + t.narration : ''}</td>
                      <td className="px-4 py-2 text-sm text-right text-gray-700">{formatCurrency(t.amount)}</td>
                    </tr>
                  )) : (
                    <tr><td className="p-4">No sample transactions available.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Customer ID Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-4 rounded-lg shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">{customerId}</h2>
            <p className="text-blue-100 text-sm">Financial Analysis & Lending Decision</p>
          </div>
          <div className="text-right text-sm">
            <p className="text-blue-100">Generated: {new Date(data.generated_at).toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Decision Summary - Moved to Top */}
      {data.decision && (
        <div className={`p-6 rounded-lg shadow-lg ${data.decision.recommendation === 'APPROVE' ? 'bg-green-50 border-2 border-green-200' : data.decision.recommendation === 'REJECT' ? 'bg-red-50 border-2 border-red-200' : 'bg-yellow-50 border-2 border-yellow-200'}`}>
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            {data.decision.recommendation === 'APPROVE' ? (
              <CheckCircle className="w-6 h-6 text-green-600 mr-2" />
            ) : (
              <AlertCircle className="w-6 h-6 text-red-600 mr-2" />
            )}
            Lending Decision: {data.decision.recommendation}
          </h3>

          {/* Positives */}
          {data.decision.positives && data.decision.positives.length > 0 && (
            <div className="mb-4">
              <h4 className="font-semibold text-green-700 mb-2">✓ Positive Indicators ({data.decision.positive_count})</h4>
              <ul className="space-y-1">
                {data.decision.positives.map((item, idx) => (
                  <li key={idx} className="text-gray-700 flex items-start">
                    <span className="text-green-500 mr-2">•</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Negatives */}
          {data.decision.negatives && data.decision.negatives.length > 0 && (
            <div className="mb-4">
              <h4 className="font-semibold text-red-700 mb-2">✗ Negative Indicators ({data.decision.negative_count})</h4>
              <ul className="space-y-1">
                {data.decision.negatives.map((item, idx) => (
                  <li key={idx} className="text-gray-700 flex items-start">
                    <span className="text-red-500 mr-2">•</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Final Reasoning */}
          {data.decision.reasoning && (
            <div className="mt-4 p-4 bg-white rounded border-l-4 border-blue-500">
              <h4 className="font-semibold text-gray-700 mb-2">Final Assessment:</h4>
              <p className="text-gray-600">{data.decision.reasoning}</p>
            </div>
          )}
        </div>
      )}

      {/* Net Surplus Overview */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Financial Health Summary</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            title="Net Surplus / Deficit"
            value={cashflow_metrics?.net_surplus}
            unit="₹"
            status={cashflow_metrics?.net_surplus >= 0 ? 'positive' : 'negative'}
            calculation={cashflow_metrics?.calculation}
          />
          <MetricCard
            title="Surplus Ratio"
            value={cashflow_metrics?.surplus_ratio}
            unit="%"
            status={cashflow_metrics?.surplus_ratio > 20 ? 'positive' : 'negative'}
            calculation={cashflow_metrics?.calculation}
          />
          <MetricCard
            title="Inflow/Outflow Ratio"
            value={cashflow_metrics?.inflow_outflow_ratio}
            status={cashflow_metrics?.inflow_outflow_ratio > 1.2 ? 'positive' : 'negative'}
            calculation={cashflow_metrics?.calculation}
          />
        </div>
      </div>

      {/* Income Stability */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Income Stability</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            title="Income Stability (CV)"
            value={cashflow_metrics?.income_stability_cv}
            unit="%"
            status={cashflow_metrics?.income_stability_cv < 30 ? 'positive' : 'negative'}
            calculation={cashflow_metrics?.calculation}
          />
          <MetricCard
            title="Seasonality Index"
            value={cashflow_metrics?.seasonality_index}
            unit="%"
            status={cashflow_metrics?.seasonality_index < 50 ? 'positive' : 'negative'}
            calculation={cashflow_metrics?.calculation}
          />
          <MetricCard
            title="Cashflow Variance"
            value={cashflow_metrics?.cashflow_variance}
            unit="₹"
            calculation={cashflow_metrics?.calculation}
          />
        </div>

        {/* Monthly Breakdown */}
        {cashflow_metrics?.monthly_inflow && cashflow_metrics?.monthly_outflow && (
          <div className="mt-6">
            <h4 className="font-semibold text-gray-700 mb-3">Monthly Cashflow Breakdown</h4>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Month</th>
                    <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Inflow</th>
                    <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Outflow</th>
                    <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Surplus</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {Object.keys(cashflow_metrics.monthly_inflow)
                    .slice(0, expandedCashflow ? undefined : 10)
                    .map((month) => {
                      const inflow = cashflow_metrics.monthly_inflow[month];
                      const outflow = cashflow_metrics.monthly_outflow ? cashflow_metrics.monthly_outflow[month] : undefined;
                      const nIn = Number(inflow);
                      const nOut = Number(outflow);
                      const surplus = Number.isFinite(nIn) || Number.isFinite(nOut) ? ((Number.isFinite(nIn) ? nIn : 0) - (Number.isFinite(nOut) ? nOut : 0)) : null;
                      return (
                        <tr key={month}>
                          <td className="px-4 py-2 text-sm text-gray-700">{month}</td>
                          <td className="px-4 py-2 text-sm text-right text-green-600">{formatCurrency(inflow)}</td>
                          <td className="px-4 py-2 text-sm text-right text-red-600">{formatCurrency(outflow)}</td>
                          <td className={`px-4 py-2 text-sm text-right font-semibold ${surplus >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {surplus === null ? '—' : formatCurrency(surplus)}
                          </td>
                        </tr>
                      );
                    })}
                </tbody>
              </table>
            </div>
            {Object.keys(cashflow_metrics.monthly_inflow).length > 10 && (
              <button
                onClick={() => setExpandedCashflow(!expandedCashflow)}
                className="mt-3 flex items-center text-blue-600 hover:text-blue-700 font-medium"
              >
                {expandedCashflow ? (
                  <>
                    <ChevronUp className="w-4 h-4 mr-1" />
                    Show Less
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-4 h-4 mr-1" />
                    Show All ({Object.keys(cashflow_metrics.monthly_inflow).length} months)
                  </>
                )}
              </button>
            )}
          </div>
        )}

        {/* Surplus Trend */}
        {cashflow_metrics?.surplus_trend && (
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-gray-700">Surplus Trend:</span>
              <div className="flex items-center">
                {cashflow_metrics.surplus_trend === 'increasing' ? (
                  <>
                    <TrendingUp className="w-5 h-5 text-green-600 mr-2" />
                    <span className="text-green-600 font-semibold">Increasing</span>
                  </>
                ) : cashflow_metrics.surplus_trend === 'decreasing' ? (
                  <>
                    <TrendingDown className="w-5 h-5 text-red-600 mr-2" />
                    <span className="text-red-600 font-semibold">Decreasing</span>
                  </>
                ) : (
                  <span className="text-gray-600 font-semibold">Stable</span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Expense Composition */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Expense Composition</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            title="Total Expenses"
            value={expense_composition?.total_expenses}
            unit="₹"
            calculation={expense_composition?.calculation}
          />
          <MetricCard
            title="Essential vs Non-Essential Ratio"
            value={expense_composition?.essential_ratio}
            unit="%"
            status={expense_composition?.essential_ratio > 60 ? 'positive' : 'negative'}
            calculation={expense_composition?.calculation}
          />
          <MetricCard
            title="Debt Servicing Ratio (DSR)"
            value={expense_composition?.debt_servicing_ratio}
            unit="%"
            status={expense_composition?.debt_servicing_ratio < 40 ? 'positive' : 'negative'}
            calculation={expense_composition?.calculation}
          />
        </div>

        {/* Expense Breakdown */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-green-50 rounded-lg">
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-semibold text-gray-700 mb-2">Essential Spending</h4>
                <p className="text-2xl font-bold text-green-600">{formatCurrency(expense_composition?.essential_spend)}</p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => setShowCalculation({ metric: 'Essential Spending', calculation: expense_composition?.calculation || expense_composition })} className="text-blue-500 hover:text-blue-700"><Info className="w-4 h-4"/></button>
                <button onClick={() => setShowExpenseTxns({ type: 'essential', txns: expense_composition?.sample_transactions?.essential || [] })} className="text-gray-600 hover:text-gray-800">Show txns</button>
              </div>
            </div>
          </div>
          <div className="p-4 bg-orange-50 rounded-lg">
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-semibold text-gray-700 mb-2">Non-Essential Spending</h4>
                <p className="text-2xl font-bold text-orange-600">{formatCurrency(expense_composition?.non_essential_spend)}</p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => setShowCalculation({ metric: 'Non-Essential Spending', calculation: expense_composition?.calculation || expense_composition })} className="text-blue-500 hover:text-blue-700"><Info className="w-4 h-4"/></button>
                <button onClick={() => setShowExpenseTxns({ type: 'non_essential', txns: expense_composition?.sample_transactions?.non_essential || [] })} className="text-gray-600 hover:text-gray-800">Show txns</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Credit Behavior */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Credit Behavior</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            title="Bounce Count"
            value={credit_behavior?.bounce_count}
            status={credit_behavior?.bounce_count === 0 ? 'positive' : 'negative'}
            calculation={credit_behavior?.calculation}
          />
          <MetricCard
            title="EMI Consistency Score"
            value={credit_behavior?.emi_consistency_score}
            unit="%"
            status={credit_behavior?.emi_consistency_score > 80 ? 'positive' : 'negative'}
            calculation={credit_behavior?.calculation}
          />
          <MetricCard
            title="EMI Variance"
            value={credit_behavior?.emi_variance}
            unit="₹"
            calculation={credit_behavior?.calculation}
          />
        </div>

        {/* Failed Transactions */}
        {credit_behavior?.failed_transactions && credit_behavior.failed_transactions.length > 0 && (
          <div className="mt-6">
            <h4 className="font-semibold text-gray-700 mb-3 flex items-center">
              <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
              Failed Transactions
            </h4>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                    <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {credit_behavior.failed_transactions.map((txn, idx) => (
                    <tr key={idx}>
                      <td className="px-4 py-2 text-sm text-gray-700">{txn.date}</td>
                      <td className="px-4 py-2 text-sm text-gray-700">{txn.description}</td>
                      <td className="px-4 py-2 text-sm text-right text-red-600">{formatCurrency(txn.amount)}</td>
                      <td className="px-4 py-2 text-sm text-gray-600">{txn.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Business Health */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Business Health Indicators</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            title="Top Customer Dependence"
            value={cashflow_metrics?.top_customer_dependence}
            unit="%"
            status={cashflow_metrics?.top_customer_dependence < 50 ? 'positive' : 'negative'}
            calculation={cashflow_metrics?.calculation}
          />
          <MetricCard
            title="GST vs Bank Reconciliation"
            value={business_health?.reconciliation_variance}
            unit="%"
            status={Math.abs(business_health?.reconciliation_variance || 0) < 10 ? 'positive' : 'negative'}
            calculation={business_health?.calculation}
          />
          <MetricCard
            title="Working Capital Gap"
            value={business_health?.working_capital_gap}
            unit="days"
            status={business_health?.working_capital_gap < 30 ? 'positive' : 'negative'}
            calculation={business_health?.calculation}
          />
        </div>

        {/* Growth Rates */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className={`p-4 rounded-lg ${business_health?.credit_growth_rate >= 0 ? 'bg-green-50' : 'bg-red-50'}`}>
            <div className="flex justify-between items-center">
              <div>
                <h4 className="font-semibold text-gray-700">Credit Growth Rate</h4>
                {business_health?.credit_growth_years >= 2 && business_health?.credit_growth_cagr != null && (
                  <span className="text-xs text-gray-500">CAGR over {business_health.credit_growth_years} years</span>
                )}
              </div>
              <button
                onClick={() => setShowCalculation({ metric: 'Credit Growth Rate', calculation: business_health?.calculation })}
                className="text-blue-500 hover:text-blue-700"
              >
                <Info className="w-4 h-4" />
              </button>
            </div>
            <div className="flex items-center mt-2">
              {business_health?.credit_growth_rate >= 0 ? (
                <TrendingUp className="w-6 h-6 text-green-600 mr-2" />
              ) : (
                <TrendingDown className="w-6 h-6 text-red-600 mr-2" />
              )}
                <p className={`text-2xl font-bold ${business_health?.credit_growth_rate >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatNumber(business_health?.credit_growth_rate)}%
              </p>
            </div>
          </div>
          <div className={`p-4 rounded-lg ${business_health?.expense_growth_rate <= 0 ? 'bg-green-50' : 'bg-orange-50'}`}>
            <div className="flex justify-between items-center">
              <div>
                <h4 className="font-semibold text-gray-700">Expense Growth Rate</h4>
                {business_health?.expense_growth_years >= 2 && business_health?.expense_growth_cagr != null && (
                  <span className="text-xs text-gray-500">CAGR over {business_health.expense_growth_years} years</span>
                )}
              </div>
              <button
                onClick={() => setShowCalculation({ metric: 'Expense Growth Rate', calculation: business_health?.calculation })}
                className="text-blue-500 hover:text-blue-700"
              >
                <Info className="w-4 h-4" />
              </button>
            </div>
            <div className="flex items-center mt-2">
              {business_health?.expense_growth_rate >= 0 ? (
                <TrendingUp className="w-6 h-6 text-orange-600 mr-2" />
              ) : (
                <TrendingDown className="w-6 h-6 text-green-600 mr-2" />
              )}
                <p className={`text-2xl font-bold ${business_health?.expense_growth_rate <= 0 ? 'text-green-600' : 'text-orange-600'}`}>
                  {formatNumber(business_health?.expense_growth_rate)}%
              </p>
            </div>
          </div>
        </div>

        {/* Top Customers */}
        {cashflow_metrics?.top_customers && cashflow_metrics.top_customers.length > 0 && (
          <div className="mt-6">
            <h4 className="font-semibold text-gray-700 mb-3">Top 5 Customers by Inflow</h4>
            <div className="space-y-2">
              {cashflow_metrics.top_customers.map((customer, idx) => (
                  <div key={idx} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="text-gray-700">{customer.name || `Customer ${idx + 1}`}</span>
                    <span className="font-semibold text-green-600">{formatCurrency(customer.amount)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EarningsVsSpendings;
