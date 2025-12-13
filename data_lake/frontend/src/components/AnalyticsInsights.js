import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, AlertTriangle, CheckCircle, DollarSign, Users, FileText, BarChart3, Brain, Sparkles } from 'lucide-react';
import {
  BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const AnalyticsInsights = () => {
  const [customerId, setCustomerId] = useState(() => {
    try { return localStorage.getItem('msme_customer_id') || 'CUST_MSM_00001'; } catch (e) { return 'CUST_MSM_00001'; }
  });
  const [analytics, setAnalytics] = useState(null);
  const [aiInsights, setAiInsights] = useState(null);
  const [creditScore, setCreditScore] = useState(null);
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [error, setError] = useState(null);
  const [calcModal, setCalcModal] = useState({ open: false, title: '', data: null });
  const [debugMinimized, setDebugMinimized] = useState(true);

  useEffect(() => {
    if (customerId) {
      fetchAnalytics();
    }
    const handleStorage = (e) => {
      if (e.key === 'msme_customer_id' && e.newValue) {
        setCustomerId(e.newValue);
      }
    };
    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, [customerId]);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`/api/analytics?customer_id=${customerId}`);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setError(error.response?.data?.error || 'Failed to load analytics. Have you generated analytics for this customer?');
    } finally {
      setLoading(false);
    }
  };

  const fetchAIInsights = async () => {
    setAiLoading(true);
    try {
      const response = await axios.post('/api/ai-insights', { customer_id: customerId });
      setAiInsights(response.data);
    } catch (error) {
      console.error('Error fetching AI insights:', error);
      setAiInsights({ error: 'AI service unavailable' });
    } finally {
      setAiLoading(false);
    }
  };

  const handleCalculateScore = async () => {
    try {
      const resp = await axios.post('/api/pipeline/calculate_score', { customer_id: customerId });
      setCreditScore(resp.data);
    } catch (err) {
      console.error('Calculate score failed:', err);
      setCreditScore({ error: err.response?.data?.error || err.message });
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82ca9d'];

  const formatCurrency = (value) => {
    if (!value) return '₹0';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatNumber = (value) => {
    if (!value) return '0';
    return new Intl.NumberFormat('en-IN').format(value);
  };

  const renderOverallInsights = () => {
    if (!analytics?.overall) return null;

    const overall = analytics.overall;

    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
          <BarChart3 className="w-6 h-6 mr-2 text-primary-600" />
          Overall Business Insights
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <FileText className="w-8 h-8 text-blue-600" />
              <DollarSign className="w-5 h-5 text-blue-400" />
            </div>
            <p className="text-sm text-gray-600 mt-2">Total Records</p>
            <p className="text-2xl font-bold text-gray-800 mt-1">{formatNumber(overall.total_records || 0)}</p>
          </div>

          <div className="bg-green-50 rounded-lg p-4 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <TrendingUp className="w-8 h-8 text-green-600" />
              <CheckCircle className="w-5 h-5 text-green-400" />
            </div>
            <p className="text-sm text-gray-600 mt-2">Datasets Generated</p>
            <p className="text-2xl font-bold text-gray-800 mt-1">{overall.datasets_count || 0}</p>
          </div>

          <div className="bg-purple-50 rounded-lg p-4 border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <Users className="w-8 h-8 text-purple-600" />
              <DollarSign className="w-5 h-5 text-purple-400" />
            </div>
            <p className="text-sm text-gray-600 mt-2">Total Accounts</p>
            <p className="text-2xl font-bold text-gray-800 mt-1">{formatNumber(overall.total_accounts || 0)}</p>
          </div>

          <div className="bg-yellow-50 rounded-lg p-4 border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <AlertTriangle className="w-8 h-8 text-yellow-600" />
              <DollarSign className="w-5 h-5 text-yellow-400" />
            </div>
            <p className="text-sm text-gray-600 mt-2">Anomalies Detected</p>
            <p className="text-2xl font-bold text-gray-800 mt-1">{analytics?.anomalies?.total_anomalies || 0}</p>
          </div>
        </div>

        {overall.datasets && (
          <div className="mt-6">
            <h4 className="text-lg font-semibold text-gray-700 mb-4">Dataset Distribution</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={Object.entries(overall.datasets).map(([name, count]) => ({ name, count }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#8884d8" name="Records" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    );
  };

  const resolvePath = (obj, path) => {
    if (!obj || !path) return undefined;
    return path.split('.').reduce((o, p) => (o ? o[p] : undefined), obj);
  };

  const showCalculation = (path, label) => {
    if (!analytics) return;
    const node = resolvePath(analytics, path);
    let data = null;

    // If the exact node has a calculation object, use it
    if (node && typeof node === 'object' && node.calculation) {
      data = node.calculation;
    } else if (node !== undefined) {
      // If node is a primitive or object without calculation, present its value and source
      data = { value: node, source: path };
    } else {
      // fallback to section-level calculation if present
      const section = path.split('.')[0];
      const secObj = analytics?.[section];
      if (secObj && secObj.calculation) data = secObj.calculation;
      else data = secObj || { note: 'No calculation metadata available for this section.' };
    }

    // Special explainability for overall score components
    if (path.startsWith('overall.scores')) {
      const compName = path.split('.').slice(-1)[0];
      const scores = analytics?.overall?.scores || {};
      const methodology = analytics?.overall?.score_methodology || {};
      const compValue = scores[compName];
      const weights = { cashflow_stability: 0.45, business_health: 0.35, debt_capacity: 0.20 };
      const contributions = {};
      Object.keys(weights).forEach((k) => {
        const v = Number(scores[k] || 0);
        contributions[k] = Number((v * weights[k]).toFixed(2));
      });
      const composite_formula = methodology.composite_formula || '0.45*cashflow_stability + 0.35*business_health + 0.20*debt_capacity';
      const composite_value = analytics?.overall?.calculated_credit_score || scores.overall_risk_score || null;
      
      // Get component-specific derivation
      const derivationMap = {
        'cashflow_stability': methodology.cashflow_derivation || 'Transaction volume consistency, income/expense ratio, monthly variance',
        'business_health': methodology.business_derivation || 'GST compliance, ONDC order diversity, revenue trends',
        'debt_capacity': methodology.debt_derivation || 'Credit utilization, OCEN approval rate, insurance coverage'
      };
      
      data = {
        component: compName,
        value: compValue,
        derivation: derivationMap[compName] || 'Calculated from underlying metrics',
        weight: weights[compName],
        contribution_to_composite: contributions[compName],
        composite: {
          formula: composite_formula,
          weights: weights,
          all_contributions: contributions,
          composite_value: composite_value,
          explanation: methodology.explanation || `Weighted sum of all three components`
        }
      };
    }

    setCalcModal({ open: true, title: `${label} — ${path}`, data });
  };

  const closeCalculation = () => setCalcModal({ open: false, title: '', data: null });

  const renderTransactionInsights = () => {
    if (!analytics?.transactions) return null;

    const txn = analytics.transactions;

    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-6">Transaction Analysis</h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div onClick={() => showCalculation('transactions', 'Total Transactions')} className="cursor-pointer bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-4">
            <p className="text-sm text-gray-600">Total Transactions</p>
            <p className="text-3xl font-bold text-blue-700 mt-1">{formatNumber(txn.total_transactions || 0)}</p>
          </div>

          <div onClick={() => showCalculation('transactions', 'Total Amount')} className="cursor-pointer bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-4">
            <p className="text-sm text-gray-600">Total Amount</p>
            <p className="text-3xl font-bold text-green-700 mt-1">{formatCurrency(txn.total_amount || 0)}</p>
          </div>

          <div onClick={() => showCalculation('transactions', 'Average Transaction')} className="cursor-pointer bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-4">
            <p className="text-sm text-gray-600">Average Transaction</p>
            <p className="text-3xl font-bold text-purple-700 mt-1">{formatCurrency(txn.average_transaction || 0)}</p>
          </div>
        </div>

        {txn.by_type && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-4">Transaction Types</h4>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={Object.entries(txn.by_type).map(([type, data]) => ({ name: type, value: data.count || 0 }))}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {Object.keys(txn.by_type).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => formatNumber(value)} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div>
              <h4 className="text-lg font-semibold text-gray-700 mb-4">Amount by Type</h4>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={Object.entries(txn.by_type).map(([type, data]) => ({ type, amount: data.total_amount || 0 }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="type" />
                  <YAxis />
                  <Tooltip formatter={(value) => formatCurrency(value)} />
                  <Bar dataKey="amount" fill="#82ca9d" name="Total Amount" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Fallback: monthly cashflow chart when by_type not available */}
        {(!txn.by_type || Object.keys(txn.by_type).length === 0) && txn.monthly_cashflow && txn.monthly_cashflow.length > 0 && (
          <div className="mt-6">
            <h4 className="text-lg font-semibold text-gray-700 mb-4">Monthly Cashflow (Income vs Expense)</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={txn.monthly_cashflow} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Legend />
                <Bar dataKey="income" fill="#00C49F" name="Income" />
                <Bar dataKey="expense" fill="#FF8042" name="Expense" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    );
  };

  const renderAccountInsights = () => {
    if (!analytics?.accounts) return null;

    const acc = analytics.accounts;

    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-6">Account Analysis</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-500">
            <p className="text-sm text-gray-600">Total Accounts</p>
            <p className="text-2xl font-bold text-gray-800 mt-1">{formatNumber(acc.total_accounts || 0)}</p>
          </div>

          <div className="bg-green-50 rounded-lg p-4 border-l-4 border-green-500">
            <p className="text-sm text-gray-600">Total Balance</p>
            <p className="text-2xl font-bold text-gray-800 mt-1">{formatCurrency(acc.total_balance || 0)}</p>
          </div>

          <div className="bg-purple-50 rounded-lg p-4 border-l-4 border-purple-500">
            <p className="text-sm text-gray-600">Average Balance</p>
            <p className="text-2xl font-bold text-gray-800 mt-1">{formatCurrency(acc.average_balance || 0)}</p>
          </div>

          <div className="bg-yellow-50 rounded-lg p-4 border-l-4 border-yellow-500">
            <p className="text-sm text-gray-600">Active Accounts</p>
            <p className="text-2xl font-bold text-gray-800 mt-1">{formatNumber(acc.active_accounts || 0)}</p>
          </div>
        </div>

        {acc.by_type && (
          <div>
            <h4 className="text-lg font-semibold text-gray-700 mb-4">Accounts by Type</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={Object.entries(acc.by_type).map(([type, data]) => ({ 
                type, 
                count: data.count || 0, 
                balance: data.total_balance || 0 
              }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="type" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="count" fill="#8884d8" name="Count" />
                <Bar yAxisId="right" dataKey="balance" fill="#82ca9d" name="Total Balance (₹)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    );
  };

  const renderGSTInsights = () => {
    if (!analytics?.gst) return null;

    const gst = analytics.gst;

    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-gray-800">GST & Business Insights</h3>
          <button
            onClick={() => setDebugMinimized(!debugMinimized)}
            className="px-3 py-1 text-sm bg-gray-200 hover:bg-gray-300 rounded flex items-center space-x-1"
          >
            <span>{debugMinimized ? '🔍 Show Debug' : '➖ Hide Debug'}</span>
          </button>
        </div>

        {!debugMinimized && (
          <div className="mb-6 bg-gray-50 border border-gray-300 rounded-lg p-4">
            <p className="text-xs font-mono text-gray-600 mb-2">GST Raw Data:</p>
            <pre className="text-xs bg-white p-3 rounded border overflow-x-auto max-h-64">
              {JSON.stringify(gst, null, 2)}
            </pre>
          </div>
        )}
        {!debugMinimized && gst.mapping_debug && gst.mapping_debug.length > 0 && (
          <div className="mb-6 bg-white border border-gray-200 rounded-lg p-3">
            <p className="text-sm font-semibold text-gray-700 mb-2">GST Mapping Debug (sample)</p>
            <div className="overflow-x-auto">
              <table className="min-w-full text-xs">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-2 py-1 text-left font-medium text-gray-500">GSTIN</th>
                    <th className="px-2 py-1 text-left font-medium text-gray-500">Raw State</th>
                    <th className="px-2 py-1 text-left font-medium text-gray-500">Mapped State</th>
                    <th className="px-2 py-1 text-right font-medium text-gray-500">Turnover</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {gst.mapping_debug.slice(0, 10).map((m, i) => (
                    <tr key={i}>
                      <td className="px-2 py-1">{m.gstin || '-'}</td>
                      <td className="px-2 py-1">{m.raw_state || '-'}</td>
                      <td className="px-2 py-1">{m.mapped_state || '-'}</td>
                      <td className="px-2 py-1 text-right">{formatCurrency(m.turnover || 0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div onClick={() => showCalculation('gst', 'Total Businesses')} className="cursor-pointer bg-indigo-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Total Businesses</p>
            <p className="text-3xl font-bold text-indigo-700 mt-1">{formatNumber(gst.total_businesses || 0)}</p>
          </div>

          <div onClick={() => showCalculation('gst', 'Total Revenue')} className="cursor-pointer bg-teal-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Total Revenue</p>
            <p className="text-3xl font-bold text-teal-700 mt-1">{formatCurrency(gst.total_revenue || 0)}</p>
          </div>

          <div onClick={() => showCalculation('gst', 'Average Revenue')} className="cursor-pointer bg-pink-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Average Revenue</p>
            <p className="text-3xl font-bold text-pink-700 mt-1">{formatCurrency(gst.average_revenue || 0)}</p>
          </div>
        </div>

        {gst.by_state && Object.keys(gst.by_state).length > 0 && (
          <div>
            <h4 className="text-lg font-semibold text-gray-700 mb-4">Business Distribution by State</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={Object.entries(gst.by_state)
                .filter(([state]) => state && state !== 'UNKNOWN')
                .map(([state, data]) => ({ state, returns: data.returns || data, turnover: data.turnover || 0 }))
                .slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="state" angle={-45} textAnchor="end" height={100} />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="returns" fill="#FF8042" name="GST Returns" />
                <Bar yAxisId="right" dataKey="turnover" fill="#00C49F" name="Turnover (₹)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    );
  };

  const renderAnomalyInsights = () => {
    if (!analytics?.anomalies) return null;

    const anomalies = analytics.anomalies;

    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
          <AlertTriangle className="w-6 h-6 mr-2 text-red-600" />
          Risk & Anomaly Detection
        </h3>

        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
          <div className="flex items-center">
            <AlertTriangle className="w-6 h-6 text-red-600 mr-3" />
            <div>
              <p className="text-sm font-medium text-red-800">Total Anomalies Detected</p>
              <p className="text-3xl font-bold text-red-900 mt-1">{formatNumber(anomalies.total_anomalies || 0)}</p>
            </div>
          </div>
        </div>

        {anomalies.anomalies && anomalies.anomalies.length > 0 && (
          <div className="space-y-4">
            {anomalies.anomalies.map((anomaly, idx) => (
              <div key={idx} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  
                  
                  
                  <h4 className="text-lg font-semibold text-gray-800 capitalize">{anomaly.type?.replace(/_/g, ' ')}</h4>
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    anomaly.severity === 'high' ? 'bg-red-100 text-red-800' :
                    anomaly.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {anomaly.severity} • {anomaly.count} detected
                  </span>
                </div>
                {anomaly.description && (
                  <p className="text-sm text-gray-600 mb-3">{anomaly.description}</p>
                )}
                {(anomaly.top_transactions && anomaly.top_transactions.length > 0) || (anomaly.transactions && anomaly.transactions.length > 0) ? (
                  <div className="mt-3">
                    <p className="text-sm font-medium text-gray-700 mb-2">Transactions:</p>
                    <div className="overflow-x-auto">
                      <table className="min-w-full text-sm">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Date</th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Type</th>
                            <th className="px-3 py-2 text-right text-xs font-medium text-gray-500">Amount</th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Description</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {(anomaly.top_transactions && anomaly.top_transactions.length > 0
                            ? anomaly.top_transactions
                            : (anomaly.transactions || []).slice(0, 5)
                          ).map((txn, tidx) => (
                            <tr key={tidx} className="hover:bg-gray-50">
                              <td className="px-3 py-2">{txn.date || txn.transaction_date || txn.raw?.date || 'N/A'}</td>
                              <td className="px-3 py-2"><span className="px-2 py-1 bg-gray-100 rounded text-xs">{txn.type || txn.transaction_type || txn.raw?.type || 'N/A'}</span></td>
                              <td className="px-3 py-2 text-right font-semibold">{formatCurrency(txn.amount || txn._numeric_amount || (txn.raw && txn.raw.amount) || 0)}</td>
                              <td className="px-3 py-2 text-gray-600 truncate max-w-xs">{txn.description || txn.narration || txn.raw?.description || '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const renderMutualFundsInsights = () => {
    if (!analytics?.mutual_funds || analytics.mutual_funds.total_portfolios === 0) return null;

    const mf = analytics.mutual_funds;

    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-6">Mutual Funds & Investments</h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div onClick={() => showCalculation('mutual_funds', 'Total Portfolios')} className="cursor-pointer bg-purple-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Total Portfolios</p>
            <p className="text-2xl font-bold text-purple-700 mt-1">{formatNumber(mf.total_portfolios || 0)}</p>
          </div>
          <div onClick={() => showCalculation('mutual_funds', 'Invested Amount')} className="cursor-pointer bg-blue-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Invested Amount</p>
            <p className="text-2xl font-bold text-blue-700 mt-1">{formatCurrency(mf.total_investment || 0)}</p>
          </div>
          <div onClick={() => showCalculation('mutual_funds', 'Current Value')} className="cursor-pointer bg-green-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Current Value</p>
            <p className="text-2xl font-bold text-green-700 mt-1">{formatCurrency(mf.current_value || 0)}</p>
          </div>
          <div onClick={() => showCalculation('mutual_funds', 'Returns')} className="cursor-pointer bg-teal-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Returns</p>
            <p className={`text-2xl font-bold mt-1 ${(mf.returns || 0) >= 0 ? 'text-green-700' : 'text-red-700'}`}>
              {formatCurrency(mf.returns || 0)}
            </p>
          </div>
        </div>

        {mf.by_scheme_type && Object.keys(mf.by_scheme_type).length > 0 && (
          <div>
            <h4 className="text-lg font-semibold text-gray-700 mb-4">Portfolio Distribution by Scheme Type</h4>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={Object.entries(mf.by_scheme_type).map(([type, count]) => ({ name: type, value: count }))}
                  cx="50%"
                  cy="50%"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {Object.keys(mf.by_scheme_type).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    );
  };

  const renderInsuranceInsights = () => {
    if (!analytics?.insurance || analytics.insurance.total_policies === 0) return null;

    const ins = analytics.insurance;

    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-6">Insurance Coverage</h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div onClick={() => showCalculation('insurance', 'Total Policies')} className="cursor-pointer bg-indigo-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Total Policies</p>
            <p className="text-2xl font-bold text-indigo-700 mt-1">{formatNumber(ins.total_policies || 0)}</p>
          </div>
          <div onClick={() => showCalculation('insurance', 'Total Coverage')} className="cursor-pointer bg-green-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Total Coverage</p>
            <p className="text-2xl font-bold text-green-700 mt-1">{formatCurrency(ins.total_coverage || 0)}</p>
          </div>
          <div onClick={() => showCalculation('insurance', 'Annual Premium')} className="cursor-pointer bg-orange-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Annual Premium</p>
            <p className="text-2xl font-bold text-orange-700 mt-1">{formatCurrency(ins.annual_premium || 0)}</p>
          </div>
        </div>

        {ins.by_type && Object.keys(ins.by_type).length > 0 && (
          <div>
            <h4 className="text-lg font-semibold text-gray-700 mb-4">Policies by Type</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(ins.by_type).map(([type, count]) => (
                <div key={type} className="bg-gray-50 rounded-lg p-3 text-center">
                  <p className="text-sm text-gray-600 capitalize">{type.toLowerCase().replace(/_/g, ' ')}</p>
                  <p className="text-xl font-bold text-gray-800 mt-1">{count}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderOCENInsights = () => {
    if (!analytics?.ocen || analytics.ocen.total_applications === 0) return null;

    const ocen = analytics.ocen;

    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-4">OCEN Loan Applications</h3>
        
        {/* Educational Info Box */}
        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6 rounded">
          <p className="text-sm text-blue-800">
            <strong>💡 Credit Insight:</strong> OCEN (Open Credit Enablement Network) data shows the borrower's history of applying for and receiving credit from digital platforms. 
            A <strong>low approval rate (&lt;30%)</strong> can indicate:
            (1) High-risk business profile, (2) Insufficient documentation, or (3) Aggressive loan requests beyond eligibility. 
            Low approval rates are a <strong className="text-red-700">RED FLAG</strong> requiring deeper investigation.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div onClick={() => showCalculation('ocen', 'Total Applications')} className="cursor-pointer bg-blue-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Total Applications</p>
            <p className="text-2xl font-bold text-blue-700 mt-1">{formatNumber(ocen.total_applications || 0)}</p>
          </div>
          <div onClick={() => showCalculation('ocen', 'Amount Requested')} className="cursor-pointer bg-purple-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Amount Requested</p>
            <p className="text-2xl font-bold text-purple-700 mt-1">{formatCurrency(ocen.total_requested || 0)}</p>
          </div>
          <div onClick={() => showCalculation('ocen', 'Amount Approved')} className="cursor-pointer bg-green-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Amount Approved</p>
            <p className="text-2xl font-bold text-green-700 mt-1">{formatCurrency(ocen.total_approved || 0)}</p>
          </div>
          <div onClick={() => showCalculation('ocen', 'Approval Rate')} className={`${ocen.approval_rate < 30 ? 'bg-red-50' : 'bg-teal-50'} cursor-pointer rounded-lg p-4`}>
            <p className="text-sm text-gray-600">Approval Rate</p>
            <p className={`text-2xl font-bold ${ocen.approval_rate < 30 ? 'text-red-700' : 'text-teal-700'} mt-1`}>
              {(ocen.approval_rate || 0).toFixed(1)}%
              {ocen.approval_rate < 30 && <span className="text-xs ml-2">⚠️</span>}
            </p>
          </div>
        </div>

        {ocen.by_status && Object.keys(ocen.by_status).length > 0 && (
          <div>
            <h4 className="text-lg font-semibold text-gray-700 mb-4">Applications by Status</h4>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={Object.entries(ocen.by_status).map(([status, count]) => ({ status, count }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="status" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#8B5CF6" name="Applications" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    );
  };

  const renderONDCInsights = () => {
    if (!analytics?.ondc || analytics.ondc.total_orders === 0) return null;

    const ondc = analytics.ondc;

    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-4">ONDC Order History</h3>
        
        {/* Educational Info Box */}
        <div className="bg-green-50 border-l-4 border-green-500 p-4 mb-6 rounded">
          <p className="text-sm text-green-800">
            <strong>💡 Credit Insight:</strong> ONDC (Open Network for Digital Commerce) order data reveals active business operations and digital adoption. 
            <strong> High order volumes</strong> with consistent average order values indicate: 
            (1) Active customer engagement, (2) Business viability &amp; revenue generation, (3) Digital payment adoption. 
            Provider diversity shows <strong className="text-green-700">multi-channel sales capability</strong> – a positive indicator of cash flow stability.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div onClick={() => showCalculation('ondc', 'Total Orders')} className="cursor-pointer bg-pink-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Total Orders</p>
            <p className="text-2xl font-bold text-pink-700 mt-1">{formatNumber(ondc.total_orders || 0)}</p>
          </div>
          <div onClick={() => showCalculation('ondc', 'Total Value')} className="cursor-pointer bg-purple-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Total Value</p>
            <p className="text-2xl font-bold text-purple-700 mt-1">{formatCurrency(ondc.total_value || 0)}</p>
          </div>
          <div onClick={() => showCalculation('ondc', 'Avg Order Value')} className="cursor-pointer bg-indigo-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Avg Order Value</p>
            <p className="text-2xl font-bold text-indigo-700 mt-1">{formatCurrency(ondc.average_order_value || 0)}</p>
          </div>
        </div>

        {ondc.by_provider && Object.keys(ondc.by_provider).length > 0 && (
          <div className="mb-6">
            <h4 className="text-lg font-semibold text-gray-700 mb-4">Orders by Provider</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(ondc.by_provider).slice(0, 8).map(([provider, count]) => (
                <div key={provider} className="bg-gray-50 rounded-lg p-3 text-center">
                  <p className="text-sm text-gray-600 truncate">{provider}</p>
                  <p className="text-xl font-bold text-gray-800 mt-1">{count}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6 rounded-lg">
        <div className="flex items-start">
          <AlertTriangle className="w-6 h-6 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
          <div>
            <h3 className="text-lg font-medium text-yellow-800">Analytics Not Available</h3>
            <p className="text-sm text-yellow-700 mt-2">{error}</p>
            <button
              onClick={fetchAnalytics}
              className="mt-4 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold text-gray-800">Lending Analytics & AI Insights</h2>
        <div className="flex space-x-2">
          <input
            type="text"
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && fetchAnalytics()}
            placeholder="Customer ID (press Enter to submit)"
            className="px-4 py-2 border border-gray-300 rounded-lg"
          />
          <button
            onClick={fetchAnalytics}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <TrendingUp className="w-4 h-4" />
            <span>Load Analytics</span>
          </button>
        </div>
      </div>

      {/* Credit Score Display - Prominent at top for decision making */}
      {analytics?.overall && (
        <div className="bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-xl shadow-lg p-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2">
              <div className="flex items-center mb-4">
                <CheckCircle className="w-10 h-10 mr-3" />
                <div>
                  <h3 className="text-2xl font-bold">Credit Score Assessment</h3>
                  <p className="text-green-100">Customer: {customerId}</p>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4 mt-4">
                <div onClick={() => showCalculation('overall.scores.cashflow_stability', 'Cashflow Stability')} className="cursor-pointer bg-white/10 rounded-lg p-3">
                  <p className="text-xs text-green-100">Cashflow Stability</p>
                  <p className="text-2xl font-bold">{analytics.overall.scores?.cashflow_stability || 0}</p>
                </div>
                <div onClick={() => showCalculation('overall.scores.business_health', 'Business Health')} className="cursor-pointer bg-white/10 rounded-lg p-3">
                  <p className="text-xs text-green-100">Business Health</p>
                  <p className="text-2xl font-bold">{analytics.overall.scores?.business_health || 0}</p>
                </div>
                <div onClick={() => showCalculation('overall.scores.debt_capacity', 'Debt Capacity')} className="cursor-pointer bg-white/10 rounded-lg p-3">
                  <p className="text-xs text-green-100">Debt Capacity</p>
                  <p className="text-2xl font-bold">{analytics.overall.scores?.debt_capacity || 0}</p>
                </div>
              </div>
            </div>
            <div className="flex flex-col items-center justify-center bg-white/10 rounded-xl p-6">
              <p className="text-sm text-green-100 mb-2">Composite Credit Score</p>
              <div className="text-7xl font-bold mb-2">
                {analytics.overall.calculated_credit_score ? 
                  Math.round(analytics.overall.calculated_credit_score) : 
                  Math.round(analytics.overall.scores?.overall_risk_score || 0)}
              </div>
              <div className="text-xs text-green-100 mb-3">out of 100</div>
              <div className={`px-4 py-2 rounded-full text-sm font-semibold ${
                (analytics.overall.calculated_credit_score || analytics.overall.scores?.overall_risk_score || 0) >= 75 ? 'bg-green-400 text-green-900' :
                (analytics.overall.calculated_credit_score || analytics.overall.scores?.overall_risk_score || 0) >= 60 ? 'bg-yellow-400 text-yellow-900' :
                'bg-red-400 text-red-900'
              }`}>
                {(analytics.overall.calculated_credit_score || analytics.overall.scores?.overall_risk_score || 0) >= 75 ? '✓ APPROVE' :
                 (analytics.overall.calculated_credit_score || analytics.overall.scores?.overall_risk_score || 0) >= 60 ? '⚠ REVIEW' :
                 '✗ HIGH RISK'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI Insights Section */}
      {analytics && !error && (
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl shadow-lg p-6 border-2 border-purple-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-2xl font-bold text-gray-800 flex items-center">
              <Brain className="w-7 h-7 mr-2 text-purple-600" />
              AI-Powered Lending Recommendation
            </h3>
            <button
              onClick={fetchAIInsights}
              disabled={aiLoading}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center space-x-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>{aiLoading ? 'Analyzing...' : 'Get AI Insights'}</span>
            </button>
          </div>
          
          {aiInsights && !aiInsights.error && (
            <div className="bg-white rounded-lg p-6 shadow-md">
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap">{aiInsights.ai_insights}</p>
              </div>
              <p className="text-xs text-gray-500 mt-4">
                Generated at: {new Date(aiInsights.generated_at).toLocaleString()} | 
                Powered by AI (OpenRouter/Gemini)
              </p>
            </div>
          )}
          {aiInsights?.error && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-yellow-800">⚠️ {aiInsights.error} {aiInsights.ai_error ? `| provider: ${aiInsights.ai_error}` : ''}</p>
            </div>
          )}
          
          {/* Credit score result */}
          {creditScore && (
            <div className="mt-4 bg-white rounded-lg p-4 shadow-sm">
              {creditScore.error ? (
                <p className="text-red-600">Error calculating score: {creditScore.error}</p>
              ) : (
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Calculated Credit Score</p>
                    <p className="text-3xl font-bold text-gray-800">{creditScore.calculated_credit_score}</p>
                    <p className="text-xs text-gray-500">Generated: {new Date(creditScore.generated_at).toLocaleString()}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Components</p>
                    <p className="text-sm text-gray-700">Cashflow: {creditScore.components?.cashflow_stability}</p>
                    <p className="text-sm text-gray-700">Business: {creditScore.components?.business_health}</p>
                    <p className="text-sm text-gray-700">Debt Capacity: {creditScore.components?.debt_capacity}</p>
                  </div>
                </div>
              )}
            </div>
          )}
          
          {!aiInsights && !aiLoading && (
            <div className="bg-white rounded-lg p-6 text-center">
              <Brain className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600">Click "Get AI Insights" to generate AI-powered lending recommendation</p>
            </div>
          )}
        </div>
      )}

      <div className="bg-gradient-to-r from-primary-500 to-primary-700 text-white rounded-xl p-6">
        <h3 className="text-2xl font-bold mb-2">Data-Driven Decision Making for Banks & NBFCs</h3>
        <p className="text-primary-100">
          Comprehensive insights to evaluate MSME creditworthiness, detect anomalies, and make informed lending decisions.
        </p>
      </div>

      {renderOverallInsights()}
      {renderTransactionInsights()}
      {renderAccountInsights()}
      {renderGSTInsights()}
      {renderAnomalyInsights()}
      {renderMutualFundsInsights()}
      {renderInsuranceInsights()}
      {renderOCENInsights()}
      {renderONDCInsights()}

      {/* Calculation modal */}
      {calcModal.open && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50" onClick={closeCalculation}>
          <div className="bg-white rounded-lg shadow-lg w-11/12 md:w-2/3 max-h-[80vh] overflow-auto p-6" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-start justify-between mb-4">
              <h4 className="text-lg font-semibold">Calculation: {calcModal.title}</h4>
              <button onClick={closeCalculation} className="text-gray-500 hover:text-gray-700">Close</button>
            </div>
            <pre className="text-sm text-gray-800 whitespace-pre-wrap">{JSON.stringify(calcModal.data, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsInsights;
