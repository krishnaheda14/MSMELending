import React, { useState, useEffect } from 'react';
import { User, TrendingUp, FileText, CreditCard, AlertTriangle, Shield, Package, ShoppingCart, DollarSign, Briefcase } from 'lucide-react';
import axios from 'axios';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const CustomerProfile = () => {
  const [customerId, setCustomerId] = useState('CUST_MSM_00001');
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    if (!customerId.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`http://localhost:5000/api/customer-profile?customer_id=${customerId}`);
      setProfileData(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load customer profile');
      console.error('Profile load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      loadProfile();
    }
  };

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return `₹${Number(value).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
  };

  const formatNumber = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return Number(value).toLocaleString('en-IN');
  };

  // Chart colors
  const COLORS = {
    primary: '#3B82F6',
    secondary: '#8B5CF6',
    success: '#10B981',
    danger: '#EF4444',
    warning: '#F59E0B',
    info: '#06B6D4',
    purple: '#A855F7',
    pink: '#EC4899',
    teal: '#14B8A6',
    emerald: '#059669'
  };

  const CHART_COLORS = ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444', '#06B6D4', '#A855F7', '#EC4899'];

  const CustomTooltip = ({ active, payload, label, formatter }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-800 mb-1">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {entry.name}: {formatter ? formatter(entry.value) : entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const renderOverview = () => {
    const overall = profileData?.data_sources?.overall;
    const transactions = profileData?.data_sources?.transactions;
    const earnings = profileData?.data_sources?.earnings_spendings;

    if (!overall && !transactions) {
      return <div className="text-gray-500">No overview data available</div>;
    }

    const cards = [
      { label: 'Total Records', value: formatNumber(overall?.total_records), icon: FileText, color: 'blue' },
      { label: 'Data Sources', value: formatNumber(overall?.datasets_count), icon: Package, color: 'purple' },
      { label: 'Total Transactions', value: formatNumber(transactions?.total_transactions), icon: TrendingUp, color: 'green' },
      { label: 'Total Inflow', value: formatCurrency(earnings?.cashflow_metrics?.total_inflow), icon: DollarSign, color: 'emerald' },
      { label: 'Total Outflow', value: formatCurrency(earnings?.cashflow_metrics?.total_outflow), icon: DollarSign, color: 'red' },
      { label: 'Net Surplus', value: formatCurrency(earnings?.cashflow_metrics?.net_surplus), icon: TrendingUp, color: 'teal' },
    ];

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cards.map((card, idx) => {
            const Icon = card.icon;
            return (
              <div key={idx} className="bg-white rounded-lg shadow p-6 border-l-4" style={{borderLeftColor: `var(--color-${card.color}-500)`}}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">{card.label}</p>
                    <p className="text-2xl font-bold text-gray-900">{card.value}</p>
                  </div>
                  <Icon className={`w-8 h-8 text-${card.color}-500`} />
                </div>
              </div>
            );
          })}
        </div>

        {overall?.scores && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <CreditCard className="w-5 h-5 mr-2 text-primary-600" />
              Credit Scores
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Cashflow Stability</p>
                <p className="text-3xl font-bold text-blue-600">{overall.scores.cashflow_stability?.toFixed(1)}</p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Business Health</p>
                <p className="text-3xl font-bold text-green-600">{overall.scores.business_health?.toFixed(1)}</p>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Debt Capacity</p>
                <p className="text-3xl font-bold text-purple-600">{overall.scores.debt_capacity?.toFixed(1)}</p>
              </div>
              <div className="text-center p-4 bg-gradient-to-br from-primary-50 to-purple-50 rounded-lg border-2 border-primary-200">
                <p className="text-sm text-gray-600 mb-1 font-semibold">Overall Risk Score</p>
                <p className="text-3xl font-bold text-primary-600">{overall.scores.overall_risk_score?.toFixed(2)}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderTransactions = () => {
    const data = profileData?.data_sources?.transactions;
    if (!data) return <div className="text-gray-500">No transaction data available</div>;

    // Prepare data for transaction type pie chart
    const typeData = data.by_type ? Object.entries(data.by_type).map(([name, info]) => ({
      name: name,
      value: info.total_amount,
      count: info.count
    })) : [];

    // Prepare data for transaction count by type
    const countData = data.by_type ? Object.entries(data.by_type).map(([name, info]) => ({
      name: name,
      count: info.count
    })) : [];

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Transaction Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Total Transactions</p>
              <p className="text-2xl font-bold">{formatNumber(data.total_transactions)}</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Total Amount</p>
              <p className="text-2xl font-bold">{formatCurrency(data.total_amount)}</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Average Transaction</p>
              <p className="text-2xl font-bold">{formatCurrency(data.average_transaction)}</p>
            </div>
          </div>

          {/* Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            {/* Transaction Amount by Type - Pie Chart */}
            {typeData.length > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3 text-center">Transaction Amount by Type</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={typeData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {typeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip formatter={formatCurrency} />} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Transaction Count by Type - Bar Chart */}
            {countData.length > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3 text-center">Transaction Count by Type</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={countData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip content={<CustomTooltip formatter={formatNumber} />} />
                    <Bar dataKey="count" fill={COLORS.primary} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {data.by_type && (
            <div className="mt-6">
              <h4 className="font-semibold mb-3">Detailed Breakdown by Type</h4>
              <div className="space-y-2">
                {Object.entries(data.by_type).map(([type, info]) => (
                  <div key={type} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <div>
                      <span className="font-medium">{type}</span>
                      <span className="text-sm text-gray-600 ml-2">({formatNumber(info.count)} transactions)</span>
                    </div>
                    <span className="font-semibold">{formatCurrency(info.total_amount)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderGST = () => {
    const data = profileData?.data_sources?.gst;
    if (!data) return <div className="text-gray-500">No GST data available</div>;

    // Prepare monthly GST data for line chart (sort by month)
    const monthlyData = data.monthly_gst_turnover 
      ? Object.entries(data.monthly_gst_turnover)
          .map(([month, amount]) => ({
            month: month,
            turnover: amount
          }))
          .slice(-12) // Last 12 months
      : [];

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">GST Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Returns Count</p>
              <p className="text-2xl font-bold">{formatNumber(data.returns_count)}</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Annual Turnover</p>
              <p className="text-2xl font-bold">{formatCurrency(data.annual_turnover)}</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Total Businesses</p>
              <p className="text-2xl font-bold">{formatNumber(data.total_businesses)}</p>
            </div>
          </div>

          {/* Monthly GST Turnover Trend - Line Chart */}
          {monthlyData.length > 0 && (
            <div className="bg-gray-50 p-4 rounded-lg mt-6">
              <h4 className="font-semibold mb-4">Monthly GST Turnover Trend (Last 12 Months)</h4>
              <ResponsiveContainer width="100%" height={350}>
                <AreaChart data={monthlyData}>
                  <defs>
                    <linearGradient id="colorTurnover" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.8}/>
                      <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="month" 
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    tick={{ fontSize: 11 }}
                  />
                  <YAxis 
                    tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}K`}
                  />
                  <Tooltip content={<CustomTooltip formatter={formatCurrency} />} />
                  <Area 
                    type="monotone" 
                    dataKey="turnover" 
                    stroke={COLORS.primary} 
                    fillOpacity={1} 
                    fill="url(#colorTurnover)" 
                    name="Turnover"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}

          {data.monthly_gst_turnover && (
            <div className="mt-6">
              <h4 className="font-semibold mb-3">Monthly GST Turnover Details</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 max-h-64 overflow-y-auto">
                {Object.entries(data.monthly_gst_turnover).slice(-12).map(([month, amount]) => (
                  <div key={month} className="p-2 bg-gray-50 rounded text-sm">
                    <div className="text-gray-600">{month}</div>
                    <div className="font-semibold">{formatCurrency(amount)}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderCredit = () => {
    const data = profileData?.data_sources?.credit;
    if (!data) return <div className="text-gray-500">No credit data available</div>;

    // Prepare loan types chart data
    const loanTypesData = data.loan_types 
      ? Object.entries(data.loan_types).map(([type, count]) => ({ 
          name: type, 
          count: count 
        }))
      : [];

    // Prepare outstanding by loan type (if available)
    const outstandingByType = data.outstanding_by_type 
      ? Object.entries(data.outstanding_by_type).map(([type, amount]) => ({ 
          name: type, 
          amount: amount 
        }))
      : [];

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Credit Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600">Bureau Score</p>
              <p className="text-2xl font-bold text-blue-700">{data.bureau_score || 'N/A'}</p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-600">Open Loans</p>
              <p className="text-2xl font-bold text-green-700">{formatNumber(data.open_loans)}</p>
            </div>
            <div className="p-4 bg-red-50 rounded-lg">
              <p className="text-sm text-gray-600">Total Outstanding</p>
              <p className="text-2xl font-bold text-red-700">{formatCurrency(data.total_outstanding)}</p>
            </div>
          </div>

          {/* Loan Types Distribution */}
          {loanTypesData.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-4 text-center">Loan Count by Type</h4>
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={loanTypesData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={90}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {loanTypesData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {outstandingByType.length > 0 && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold mb-4">Outstanding Amount by Loan Type</h4>
                  <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={outstandingByType}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" angle={-30} textAnchor="end" height={80} tick={{ fontSize: 10 }} />
                      <YAxis tickFormatter={(value) => `\u20b9${(value / 100000).toFixed(1)}L`} />
                      <Tooltip content={<CustomTooltip formatter={formatCurrency} />} />
                      <Bar dataKey="amount" fill={COLORS.danger} name="Outstanding" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          )}

          {/* Loan Types List */}
          {data.loan_types && (
            <div className="mt-6">
              <h4 className="font-semibold mb-3">Loans by Type</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {Object.entries(data.loan_types).map(([type, count]) => (
                  <div key={type} className="p-3 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg border border-gray-200">
                    <p className="text-xs text-gray-600 mb-1">{type}</p>
                    <p className="text-xl font-bold text-gray-800">{formatNumber(count)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderAnomalies = () => {
    const data = profileData?.data_sources?.anomalies;
    if (!data) return <div className="text-gray-500">No anomaly data available</div>;

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2 text-yellow-600" />
            Anomalies Report
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
              <p className="text-sm text-gray-600">High Value Transactions</p>
              <p className="text-2xl font-bold text-yellow-700">{formatNumber(data.high_value_transactions?.length || 0)}</p>
            </div>
            <div className="p-4 bg-red-50 rounded-lg border border-red-200">
              <p className="text-sm text-gray-600">Suspicious Patterns</p>
              <p className="text-2xl font-bold text-red-700">{formatNumber(data.suspicious_patterns?.length || 0)}</p>
            </div>
          </div>

          {data.high_value_transactions && data.high_value_transactions.length > 0 && (
            <div className="mt-4">
              <h4 className="font-semibold mb-3">High Value Transactions (Top 10)</h4>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {data.high_value_transactions.slice(0, 10).map((txn, idx) => (
                  <div key={idx} className="p-3 bg-gray-50 rounded border-l-4 border-yellow-500">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="font-medium text-sm">{txn.description || txn.narration || 'No description'}</p>
                        <p className="text-xs text-gray-500 mt-1">{txn.date || 'No date'}</p>
                      </div>
                      <span className="font-bold text-yellow-700">{formatCurrency(txn.amount)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderMutualFunds = () => {
    const data = profileData?.data_sources?.mutual_funds;
    if (!data) return <div className="text-gray-500">No mutual funds data available</div>;

    // Prepare AMC distribution data
    const amcData = data.by_amc 
      ? Object.entries(data.by_amc)
          .map(([amc, info]) => ({ 
            name: amc.length > 25 ? amc.substring(0, 25) + '...' : amc,
            count: info.count,
            value: info.value
          }))
          .sort((a, b) => b.value - a.value)
          .slice(0, 8)
      : [];

    // Portfolio performance comparison
    const performanceData = data.by_amc
      ? Object.entries(data.by_amc)
          .map(([amc, info]) => ({
            name: amc.length > 20 ? amc.substring(0, 20) + '...' : amc,
            invested: info.invested || 0,
            current: info.value || 0
          }))
          .slice(0, 10)
      : [];

    // Calculate returns
    const totalReturns = (data.total_current_value || 0) - (data.total_invested || 0);
    const returnPercentage = data.total_invested > 0 
      ? ((totalReturns / data.total_invested) * 100).toFixed(2)
      : 0;

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Mutual Funds Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600">Total Portfolios</p>
              <p className="text-2xl font-bold text-blue-700">{formatNumber(data.total_portfolios)}</p>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-gray-600">Invested Amount</p>
              <p className="text-2xl font-bold text-purple-700">{formatCurrency(data.total_invested)}</p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-600">Current Value</p>
              <p className="text-2xl font-bold text-green-700">{formatCurrency(data.total_current_value)}</p>
            </div>
            <div className={`p-4 rounded-lg ${totalReturns >= 0 ? 'bg-green-50' : 'bg-red-50'}`}>
              <p className="text-sm text-gray-600">Total Returns</p>
              <p className={`text-2xl font-bold ${totalReturns >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                {formatCurrency(totalReturns)} ({returnPercentage}%)
              </p>
            </div>
          </div>

          {/* AMC Distribution Pie Chart */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {amcData.length > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-4 text-center">Portfolio Distribution by AMC</h4>
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={amcData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={90}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {amcData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip formatter={formatCurrency} />} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}

            {performanceData.length > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-4">Invested vs Current Value by AMC</h4>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-30} textAnchor="end" height={80} tick={{ fontSize: 9 }} />
                    <YAxis tickFormatter={(value) => `₹${(value / 100000).toFixed(1)}L`} />
                    <Tooltip content={<CustomTooltip formatter={formatCurrency} />} />
                    <Legend />
                    <Bar dataKey="invested" fill={COLORS.warning} name="Invested" />
                    <Bar dataKey="current" fill={COLORS.success} name="Current" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {data.by_amc && (
            <div className="mt-6">
              <h4 className="font-semibold mb-3">AMC Details</h4>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {Object.entries(data.by_amc).map(([amc, info]) => (
                  <div key={amc} className="flex justify-between items-center p-3 bg-gradient-to-r from-gray-50 to-purple-50 rounded border-l-4 border-purple-400">
                    <div>
                      <span className="font-medium">{amc}</span>
                      <span className="text-sm text-gray-600 ml-2">({formatNumber(info.count)} portfolios)</span>
                    </div>
                    <span className="font-semibold text-purple-700">{formatCurrency(info.value)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderInsurance = () => {
    const data = profileData?.data_sources?.insurance;
    if (!data) return <div className="text-gray-500">No insurance data available</div>;

    // Prepare policy type distribution
    const policyTypeData = data.by_type 
      ? Object.entries(data.by_type)
          .map(([type, info]) => ({ 
            name: type,
            count: info.count,
            coverage: info.coverage
          }))
      : [];

    // Coverage distribution pie chart
    const coverageData = data.by_type
      ? Object.entries(data.by_type)
          .map(([type, info]) => ({
            name: type,
            value: info.coverage
          }))
      : [];

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Insurance Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600">Total Policies</p>
              <p className="text-2xl font-bold text-blue-700">{formatNumber(data.total_policies)}</p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-600">Total Coverage</p>
              <p className="text-2xl font-bold text-green-700">{formatCurrency(data.total_coverage)}</p>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-gray-600">Total Premium Paid</p>
              <p className="text-2xl font-bold text-purple-700">{formatCurrency(data.total_premium)}</p>
            </div>
            <div className="p-4 bg-yellow-50 rounded-lg">
              <p className="text-sm text-gray-600">Avg Premium/Policy</p>
              <p className="text-2xl font-bold text-yellow-700">
                {formatCurrency((data.total_premium || 0) / (data.total_policies || 1))}
              </p>
            </div>
          </div>

          {/* Insurance Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {coverageData.length > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-4 text-center">Coverage Distribution by Type</h4>
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={coverageData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                      outerRadius={90}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {coverageData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip formatter={formatCurrency} />} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}

            {policyTypeData.length > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-4">Coverage Amount by Policy Type</h4>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={policyTypeData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-20} textAnchor="end" height={70} tick={{ fontSize: 11 }} />
                    <YAxis tickFormatter={(value) => `₹${(value / 10000000).toFixed(1)}Cr`} />
                    <Tooltip content={<CustomTooltip formatter={formatCurrency} />} />
                    <Bar dataKey="coverage" fill={COLORS.success} name="Coverage" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {data.by_type && (
            <div className="mt-6">
              <h4 className="font-semibold mb-3">Policy Type Details</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {Object.entries(data.by_type).map(([type, info]) => (
                  <div key={type} className="p-4 bg-gradient-to-r from-gray-50 to-green-50 rounded-lg border-l-4 border-green-400">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium text-lg">{type}</span>
                      <span className="text-sm bg-green-100 text-green-800 px-2 py-1 rounded">
                        {formatNumber(info.count)} policies
                      </span>
                    </div>
                    <p className="text-2xl font-bold text-green-700">{formatCurrency(info.coverage)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderOCEN = () => {
    const data = profileData?.data_sources?.ocen;
    if (!data) return <div className="text-gray-500">No OCEN data available</div>;

    // Prepare loan purpose data for charts
    const loanPurposeData = data.by_purpose 
      ? Object.entries(data.by_purpose).map(([purpose, count]) => ({ 
          name: purpose, 
          count: count 
        }))
      : [];

    // Application status breakdown
    const statusData = [
      { name: 'Approved', value: data.approved_count || 0, fill: COLORS.success },
      { name: 'Rejected', value: (data.total_applications || 0) - (data.approved_count || 0), fill: COLORS.danger }
    ].filter(item => item.value > 0);

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">OCEN Loan Applications</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600">Total Applications</p>
              <p className="text-2xl font-bold text-blue-700">{formatNumber(data.total_applications)}</p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-600">Approved</p>
              <p className="text-2xl font-bold text-green-700">{formatNumber(data.approved_count)}</p>
            </div>
            <div className="p-4 bg-red-50 rounded-lg">
              <p className="text-sm text-gray-600">Rejected</p>
              <p className="text-2xl font-bold text-red-700">{formatNumber((data.total_applications || 0) - (data.approved_count || 0))}</p>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-gray-600">Approval Rate</p>
              <p className="text-2xl font-bold text-purple-700">{data.approval_rate?.toFixed(1)}%</p>
            </div>
          </div>

          {/* Application Status Visualization */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {statusData.length > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-4 text-center">Application Status Distribution</h4>
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={statusData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                      outerRadius={90}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {statusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}

            {loanPurposeData.length > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-4">Applications by Loan Purpose</h4>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={loanPurposeData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-30} textAnchor="end" height={80} tick={{ fontSize: 10 }} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill={COLORS.info} name="Applications" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {data.by_purpose && (
            <div className="mt-6">
              <h4 className="font-semibold mb-3">By Loan Purpose</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {Object.entries(data.by_purpose).map(([purpose, count]) => (
                  <div key={purpose} className="p-3 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border border-blue-200">
                    <p className="text-xs text-gray-600 mb-1">{purpose}</p>
                    <p className="text-xl font-bold text-blue-800">{formatNumber(count)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderONDC = () => {
    const data = profileData?.data_sources?.ondc;
    if (!data) return <div className="text-gray-500">No ONDC data available</div>;

    // Prepare category data for charts
    const categoryOrderData = data.by_category 
      ? Object.entries(data.by_category)
          .map(([category, info]) => ({ 
            name: category, 
            count: info.count,
            value: info.value
          }))
          .sort((a, b) => b.value - a.value)
          .slice(0, 10)
      : [];

    // Provider data
    const providerData = data.by_provider 
      ? Object.entries(data.by_provider)
          .map(([provider, count]) => ({ 
            name: provider.length > 20 ? provider.substring(0, 20) + '...' : provider, 
            orders: count 
          }))
          .sort((a, b) => b.orders - a.orders)
          .slice(0, 10)
      : [];

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">ONDC Orders Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600">Total Orders</p>
              <p className="text-2xl font-bold text-blue-700">{formatNumber(data.total_orders)}</p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-600">Total Order Value</p>
              <p className="text-2xl font-bold text-green-700">{formatCurrency(data.total_order_value)}</p>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-gray-600">Avg Order Value</p>
              <p className="text-2xl font-bold text-purple-700">{formatCurrency((data.total_order_value || 0) / (data.total_orders || 1))}</p>
            </div>
            <div className="p-4 bg-pink-50 rounded-lg">
              <p className="text-sm text-gray-600">Provider Diversity</p>
              <p className="text-2xl font-bold text-pink-700">{formatNumber(data.provider_diversity)}</p>
            </div>
          </div>

          {/* Category Order Value Chart */}
          {categoryOrderData.length > 0 && (
            <div className="bg-gray-50 p-4 rounded-lg mb-6">
              <h4 className="font-semibold mb-4">Top 10 Categories by Order Value</h4>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={categoryOrderData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-35} textAnchor="end" height={100} tick={{ fontSize: 10 }} />
                  <YAxis tickFormatter={(value) => `₹${(value / 100000).toFixed(1)}L`} />
                  <Tooltip content={<CustomTooltip formatter={formatCurrency} />} />
                  <Bar dataKey="value" fill={COLORS.success} name="Order Value" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Provider Distribution */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {categoryOrderData.length > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-4 text-center">Order Count by Category</h4>
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={categoryOrderData.slice(0, 6)}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={90}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {categoryOrderData.slice(0, 6).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}

            {providerData.length > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-4">Top 10 Providers by Order Count</h4>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={providerData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 9 }} />
                    <Tooltip />
                    <Bar dataKey="orders" fill={COLORS.info} name="Orders" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {data.by_category && (
            <div className="mt-6">
              <h4 className="font-semibold mb-3">Category Details</h4>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {Object.entries(data.by_category).map(([category, info]) => (
                  <div key={category} className="flex justify-between items-center p-3 bg-gradient-to-r from-gray-50 to-blue-50 rounded border-l-4 border-blue-400">
                    <div>
                      <span className="font-medium">{category}</span>
                      <span className="text-sm text-gray-600 ml-2">({formatNumber(info.count)} orders)</span>
                    </div>
                    <span className="font-semibold text-blue-700">{formatCurrency(info.value)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderEarnings = () => {
    const data = profileData?.data_sources?.earnings_spendings;
    if (!data) return <div className="text-gray-500">No earnings/spendings data available</div>;

    const cashflow = data.cashflow_metrics || {};
    const expenses = data.expense_composition || {};
    const credit = data.credit_behavior || {};

    // Prepare monthly inflow/outflow data for charts
    const monthlyInflowData = cashflow.monthly_inflow 
      ? Object.entries(cashflow.monthly_inflow)
          .map(([month, amount]) => ({ month, inflow: amount }))
          .slice(-12)
      : [];
    
    const monthlyOutflowData = cashflow.monthly_outflow 
      ? Object.entries(cashflow.monthly_outflow)
          .map(([month, amount]) => ({ month, outflow: amount }))
          .slice(-12)
      : [];

    // Combine inflow and outflow for comparison chart
    const cashflowComparisonData = monthlyInflowData.map((inflowItem, idx) => ({
      month: inflowItem.month,
      inflow: inflowItem.inflow,
      outflow: monthlyOutflowData[idx]?.outflow || 0
    }));

    // Expense composition pie chart data
    const expenseData = [
      { name: 'Essential', value: expenses.essential_spend || 0 },
      { name: 'Non-Essential', value: expenses.non_essential_spend || 0 },
      { name: 'Debt Servicing', value: expenses.debt_servicing || 0 }
    ].filter(item => item.value > 0);

    // Top customers bar chart
    const topCustomersData = cashflow.top_customers?.slice(0, 10).map(c => ({
      name: c.name?.length > 20 ? c.name.substring(0, 20) + '...' : c.name,
      amount: c.amount
    })) || [];

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Cashflow Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-600">Total Inflow</p>
              <p className="text-2xl font-bold text-green-700">{formatCurrency(cashflow.total_inflow)}</p>
            </div>
            <div className="p-4 bg-red-50 rounded-lg">
              <p className="text-sm text-gray-600">Total Outflow</p>
              <p className="text-2xl font-bold text-red-700">{formatCurrency(cashflow.total_outflow)}</p>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600">Net Surplus</p>
              <p className="text-2xl font-bold text-blue-700">{formatCurrency(cashflow.net_surplus)}</p>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-gray-600">Surplus Ratio</p>
              <p className="text-2xl font-bold text-purple-700">{cashflow.surplus_ratio}%</p>
            </div>
            <div className="p-4 bg-yellow-50 rounded-lg">
              <p className="text-sm text-gray-600">Income Stability (CV)</p>
              <p className="text-2xl font-bold text-yellow-700">{cashflow.income_stability_cv}</p>
            </div>
            <div className="p-4 bg-pink-50 rounded-lg">
              <p className="text-sm text-gray-600">Seasonality Index</p>
              <p className="text-2xl font-bold text-pink-700">{cashflow.seasonality_index}</p>
            </div>
          </div>

          {/* Monthly Inflow vs Outflow Chart */}
          {cashflowComparisonData.length > 0 && (
            <div className="bg-gray-50 p-4 rounded-lg mt-6">
              <h4 className="font-semibold mb-4">Monthly Inflow vs Outflow (Last 12 Months)</h4>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={cashflowComparisonData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="month" 
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    tick={{ fontSize: 10 }}
                  />
                  <YAxis tickFormatter={(value) => `₹${(value / 1000000).toFixed(1)}M`} />
                  <Tooltip content={<CustomTooltip formatter={formatCurrency} />} />
                  <Legend />
                  <Bar dataKey="inflow" fill={COLORS.success} name="Inflow" />
                  <Bar dataKey="outflow" fill={COLORS.danger} name="Outflow" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Top Customers Revenue */}
          {topCustomersData.length > 0 && (
            <div className="bg-gray-50 p-4 rounded-lg mt-6">
              <h4 className="font-semibold mb-4">Top 10 Customer Revenue Contribution</h4>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={topCustomersData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" tickFormatter={(value) => `₹${(value / 1000000).toFixed(1)}M`} />
                  <YAxis dataKey="name" type="category" width={150} tick={{ fontSize: 11 }} />
                  <Tooltip content={<CustomTooltip formatter={formatCurrency} />} />
                  <Bar dataKey="amount" fill={COLORS.info} name="Revenue" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {expenses && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Expense Composition</h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">Essential Spend</p>
                  <p className="text-xl font-bold">{formatCurrency(expenses.essential_spend)}</p>
                  <p className="text-sm text-gray-500">{expenses.essential_ratio}% of total</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">Non-Essential Spend</p>
                  <p className="text-xl font-bold">{formatCurrency(expenses.non_essential_spend)}</p>
                  <p className="text-sm text-gray-500">{expenses.non_essential_ratio}% of total</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">Debt Servicing</p>
                  <p className="text-xl font-bold">{formatCurrency(expenses.debt_servicing)}</p>
                  <p className="text-sm text-gray-500">{expenses.debt_servicing_ratio}% of total</p>
                </div>
              </div>
              {expenseData.length > 0 && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold mb-3 text-center">Expense Distribution</h4>
                  <ResponsiveContainer width="100%" height={280}>
                    <PieChart>
                      <Pie
                        data={expenseData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                        outerRadius={90}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {expenseData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={[COLORS.success, COLORS.warning, COLORS.danger][index]} />
                        ))}
                      </Pie>
                      <Tooltip content={<CustomTooltip formatter={formatCurrency} />} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          </div>
        )}

        {credit && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Credit Behavior</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                <p className="text-sm text-gray-600">Bounce Count</p>
                <p className="text-2xl font-bold text-red-700">{formatNumber(credit.bounces)}</p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <p className="text-sm text-gray-600">EMI Consistency</p>
                <p className="text-2xl font-bold text-green-700">{credit.emi_consistency_score}%</p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm text-gray-600">Credit Utilization</p>
                <p className="text-2xl font-bold text-blue-700">{credit.credit_utilization_ratio?.toFixed(2)}%</p>
              </div>
              <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <p className="text-sm text-gray-600">Default Probability</p>
                <p className="text-2xl font-bold text-yellow-700">{credit.default_probability_score?.toFixed(2)}</p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                <p className="text-sm text-gray-600">Debt-to-Income</p>
                <p className="text-2xl font-bold text-purple-700">{credit.debt_to_income_ratio?.toFixed(2)}%</p>
              </div>
              <div className="p-4 bg-teal-50 rounded-lg border border-teal-200">
                <p className="text-sm text-gray-600">Payment Regularity</p>
                <p className="text-2xl font-bold text-teal-700">{credit.payment_regularity_score?.toFixed(0)}</p>
              </div>
            </div>

            {/* Credit Metrics Bar Chart */}
            <div className="bg-gray-50 p-4 rounded-lg mt-6">
              <h4 className="font-semibold mb-4">Credit Health Indicators (0-100 Scale)</h4>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={[
                  { metric: 'EMI Consistency', score: credit.emi_consistency_score || 0, fill: COLORS.success },
                  { metric: 'Payment Regularity', score: credit.payment_regularity_score || 0, fill: COLORS.info },
                  { metric: 'Default Risk', score: 100 - (credit.default_probability_score || 0), fill: COLORS.warning },
                  { metric: 'DTI Health', score: Math.max(0, 100 - (credit.debt_to_income_ratio || 0)), fill: COLORS.purple },
                  { metric: 'Credit Utilization', score: Math.max(0, 100 - (credit.credit_utilization_ratio || 0)), fill: COLORS.teal }
                ]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="metric" angle={-20} textAnchor="end" height={80} tick={{ fontSize: 11 }} />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Bar dataKey="score" name="Score">
                    {[
                      { metric: 'EMI Consistency', score: credit.emi_consistency_score || 0, fill: COLORS.success },
                      { metric: 'Payment Regularity', score: credit.payment_regularity_score || 0, fill: COLORS.info },
                      { metric: 'Default Risk', score: 100 - (credit.default_probability_score || 0), fill: COLORS.warning },
                      { metric: 'DTI Health', score: Math.max(0, 100 - (credit.debt_to_income_ratio || 0)), fill: COLORS.purple },
                      { metric: 'Credit Utilization', score: Math.max(0, 100 - (credit.credit_utilization_ratio || 0)), fill: COLORS.teal }
                    ].map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    );
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: User, render: renderOverview },
    { id: 'transactions', label: 'Transactions', icon: TrendingUp, render: renderTransactions },
    { id: 'gst', label: 'GST Returns', icon: FileText, render: renderGST },
    { id: 'credit', label: 'Credit', icon: CreditCard, render: renderCredit },
    { id: 'earnings', label: 'Earnings & Spendings', icon: DollarSign, render: renderEarnings },
    { id: 'anomalies', label: 'Anomalies', icon: AlertTriangle, render: renderAnomalies },
    { id: 'mutual_funds', label: 'Mutual Funds', icon: TrendingUp, render: renderMutualFunds },
    { id: 'insurance', label: 'Insurance', icon: Shield, render: renderInsurance },
    { id: 'ocen', label: 'OCEN', icon: Briefcase, render: renderOCEN },
    { id: 'ondc', label: 'ONDC', icon: ShoppingCart, render: renderONDC },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4 flex items-center">
          <User className="w-7 h-7 mr-3 text-primary-600" />
          Customer Profile
        </h2>
        
        <div className="flex items-center space-x-4">
          <input
            type="text"
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter Customer ID (e.g., CUST_MSM_00001)"
            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <button
            onClick={loadProfile}
            disabled={loading}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:bg-gray-400"
          >
            {loading ? 'Loading...' : 'Load Profile'}
          </button>
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <p className="font-semibold">Error:</p>
            <p>{error}</p>
          </div>
        )}
      </div>

      {profileData && (
        <>
          <div className="bg-white rounded-lg shadow">
            <div className="flex border-b overflow-x-auto">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 px-6 py-4 font-medium transition-colors whitespace-nowrap ${
                      activeTab === tab.id
                        ? 'border-b-2 border-primary-600 text-primary-600'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>
            <div className="p-6">
              {tabs.find(t => t.id === activeTab)?.render()}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default CustomerProfile;
