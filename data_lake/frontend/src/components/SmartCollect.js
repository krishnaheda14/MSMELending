import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Calendar,
  Clock,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
  DollarSign,
  RefreshCw,
  Zap,
  Target,
  BarChart3,
  Activity,
  FileText,
  Database
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const COLORS = {
  success: '#10B981',
  danger: '#EF4444',
  warning: '#F59E0B',
  info: '#3B82F6',
  purple: '#A855F7',
  teal: '#14B8A6'
};

const SmartCollect = () => {
  const [customerId, setCustomerId] = useState('CUST_MSM_00001');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedTab, setSelectedTab] = useState('dashboard');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadSmartCollectData();
  }, [customerId]);

  const loadSmartCollectData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('/api/smart-collect', {
        params: { customer_id: customerId }
      });
      setData(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load Smart Collect data');
    } finally {
      setLoading(false);
    }
  };

  const handleReschedule = async (collectionId, newDate) => {
    setActionLoading(true);
    try {
      await axios.post('/api/smart-collect/reschedule', {
        customer_id: customerId,
        collection_id: collectionId,
        new_date: newDate
      });
      alert('Collection rescheduled successfully!');
      loadSmartCollectData();
    } catch (err) {
      alert('Failed to reschedule: ' + (err.response?.data?.error || err.message));
    } finally {
      setActionLoading(false);
    }
  };

  const handleAttemptCollection = async (collectionId) => {
    setActionLoading(true);
    try {
      const response = await axios.post('/api/smart-collect/attempt', {
        customer_id: customerId,
        collection_id: collectionId,
        method: 'E-NACH'
      });
      alert(response.data.message);
      loadSmartCollectData();
    } catch (err) {
      alert('Collection attempt failed: ' + (err.response?.data?.error || err.message));
    } finally {
      setActionLoading(false);
    }
  };

  const formatCurrency = (value) => {
    if (value >= 10000000) return `₹${(value / 10000000).toFixed(2)}Cr`;
    if (value >= 100000) return `₹${(value / 100000).toFixed(2)}L`;
    if (value >= 1000) return `₹${(value / 1000).toFixed(2)}K`;
    return `₹${value?.toFixed(2) || 0}`;
  };

  const formatNumber = (value) => {
    if (!value) return '0';
    return value.toLocaleString('en-IN');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'OPTIMAL_WINDOW':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'SCHEDULED':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'RISKY':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'CRITICAL':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'SUCCESS':
        return 'bg-green-100 text-green-800 border-green-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'SUCCESS':
        return <CheckCircle className="w-4 h-4" />;
      case 'OPTIMAL_WINDOW':
        return <Target className="w-4 h-4" />;
      case 'CRITICAL':
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  const renderDashboard = () => {
    if (!data) return null;

    const summary = data.collection_summary || {};
    
    // Collection status distribution for pie chart
    const statusDistribution = [
      { name: 'Successful', value: summary.successful_collections || 0, fill: COLORS.success },
      { name: 'Failed', value: summary.failed_collections || 0, fill: COLORS.danger },
      { name: 'Pending', value: summary.pending_collections || 0, fill: COLORS.warning }
    ].filter(item => item.value > 0);

    // Collection history trend
    const historyTrend = (data.collection_history || []).slice(-10).map((h, idx) => ({
      attempt: `#${idx + 1}`,
      success: h.status === 'SUCCESS' ? 1 : 0,
      failed: h.status.startsWith('FAILED') ? 1 : 0
    }));

    return (
      <div className="space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg shadow-md border border-blue-200">
            <div className="flex items-center justify-between mb-2">
              <Calendar className="w-8 h-8 text-blue-600" />
              <span className="text-sm font-medium text-blue-600">Total Scheduled</span>
            </div>
            <p className="text-3xl font-bold text-blue-900">{formatNumber(summary.total_emis_scheduled)}</p>
            <p className="text-sm text-blue-700 mt-1">EMIs scheduled</p>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg shadow-md border border-green-200">
            <div className="flex items-center justify-between mb-2">
              <CheckCircle className="w-8 h-8 text-green-600" />
              <span className="text-sm font-medium text-green-600">Success Rate</span>
            </div>
            <p className="text-3xl font-bold text-green-900">{summary.collection_success_rate?.toFixed(1)}%</p>
            <p className="text-sm text-green-700 mt-1">{formatNumber(summary.successful_collections)} successful</p>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-lg shadow-md border border-purple-200">
            <div className="flex items-center justify-between mb-2">
              <DollarSign className="w-8 h-8 text-purple-600" />
              <span className="text-sm font-medium text-purple-600">Amount Collected</span>
            </div>
            <p className="text-3xl font-bold text-purple-900">{formatCurrency(summary.total_amount_collected)}</p>
            <p className="text-sm text-purple-700 mt-1">Successfully recovered</p>
          </div>

          <div className="bg-gradient-to-br from-teal-50 to-teal-100 p-6 rounded-lg shadow-md border border-teal-200">
            <div className="flex items-center justify-between mb-2">
              <Zap className="w-8 h-8 text-teal-600" />
              <span className="text-sm font-medium text-teal-600">Cost Saved</span>
            </div>
            <p className="text-3xl font-bold text-teal-900">₹{formatNumber(summary.cost_saved)}</p>
            <p className="text-sm text-teal-700 mt-1">Operational savings</p>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Status Distribution */}
          {statusDistribution.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <BarChart3 className="w-5 h-5 mr-2 text-blue-600" />
                Collection Status Distribution
              </h3>
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={statusDistribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={90}
                    dataKey="value"
                  >
                    {statusDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="grid grid-cols-3 gap-2 mt-4">
                <div className="text-center p-2 bg-green-50 rounded">
                  <p className="text-xs text-gray-600">Successful</p>
                  <p className="font-bold text-green-700">{formatNumber(summary.successful_collections)}</p>
                </div>
                <div className="text-center p-2 bg-red-50 rounded">
                  <p className="text-xs text-gray-600">Failed</p>
                  <p className="font-bold text-red-700">{formatNumber(summary.failed_collections)}</p>
                </div>
                <div className="text-center p-2 bg-yellow-50 rounded">
                  <p className="text-xs text-gray-600">Pending</p>
                  <p className="font-bold text-yellow-700">{formatNumber(summary.pending_collections)}</p>
                </div>
              </div>
            </div>
          )}

          {/* Performance Metrics */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
              Performance Metrics
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <span className="text-sm text-gray-600">Average Retry Count</span>
                <span className="font-bold text-lg">{summary.average_retry_count?.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-blue-50 rounded">
                <span className="text-sm text-gray-600">Total Amount Pending</span>
                <span className="font-bold text-lg text-blue-700">{formatCurrency(summary.total_amount_pending)}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-green-50 rounded">
                <span className="text-sm text-gray-600">Collection Efficiency</span>
                <span className="font-bold text-lg text-green-700">{summary.collection_success_rate?.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-purple-50 rounded">
                <span className="text-sm text-gray-600">Cost per Collection</span>
                <span className="font-bold text-lg text-purple-700">
                  ₹{((summary.cost_saved || 0) / (summary.successful_collections || 1)).toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderUpcomingCollections = () => {
    if (!data) return null;

    const upcoming = data.upcoming_collections || [];
    const critical = upcoming.filter(c => c.status === 'CRITICAL');
    const risky = upcoming.filter(c => c.status === 'RISKY');
    const optimal = upcoming.filter(c => c.status === 'OPTIMAL_WINDOW');

    return (
      <div className="space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <div className="flex items-center justify-between">
              <Target className="w-6 h-6 text-green-600" />
              <span className="text-2xl font-bold text-green-700">{optimal.length}</span>
            </div>
            <p className="text-sm text-gray-600 mt-2">Optimal Window</p>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <div className="flex items-center justify-between">
              <Calendar className="w-6 h-6 text-blue-600" />
              <span className="text-2xl font-bold text-blue-700">{upcoming.length - critical.length - risky.length - optimal.length}</span>
            </div>
            <p className="text-sm text-gray-600 mt-2">Scheduled</p>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
            <div className="flex items-center justify-between">
              <AlertTriangle className="w-6 h-6 text-yellow-600" />
              <span className="text-2xl font-bold text-yellow-700">{risky.length}</span>
            </div>
            <p className="text-sm text-gray-600 mt-2">Risky</p>
          </div>
          <div className="bg-red-50 p-4 rounded-lg border border-red-200">
            <div className="flex items-center justify-between">
              <XCircle className="w-6 h-6 text-red-600" />
              <span className="text-2xl font-bold text-red-700">{critical.length}</span>
            </div>
            <p className="text-sm text-gray-600 mt-2">Critical</p>
          </div>
        </div>

        {/* Upcoming Collections List */}
        <div className="bg-white rounded-lg shadow-md">
          <div className="p-4 border-b bg-gray-50">
            <h3 className="text-lg font-semibold flex items-center">
              <Calendar className="w-5 h-5 mr-2 text-blue-600" />
              Upcoming Collections ({upcoming.length})
            </h3>
          </div>
          <div className="p-4 space-y-3 max-h-[600px] overflow-y-auto">
            {upcoming.map((collection, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-lg border-2 ${getStatusColor(collection.status)}`}
              >
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <div className="flex items-center space-x-2 mb-1">
                      {getStatusIcon(collection.status)}
                      <span className="font-semibold">{collection.collection_id}</span>
                    </div>
                    <p className="text-sm text-gray-600">Loan: {collection.loan_id}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(collection.status || 'SCHEDULED')}`}>
                    {(collection.status || 'SCHEDULED').replace(/_/g, ' ')}
                  </span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                  <div>
                    <p className="text-xs text-gray-600">EMI Amount</p>
                    <p className="font-bold">{formatCurrency(collection.emi_amount)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Scheduled Date</p>
                    <p className="font-semibold">{collection.scheduled_date}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Current Balance</p>
                    <p className="font-bold">{formatCurrency(collection.current_balance)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Success Probability</p>
                    <p className="font-bold text-blue-600">{collection.collection_probability?.toFixed(1)}%</p>
                  </div>
                </div>

                {collection.optimal_collection_window && (
                  <div className="bg-white bg-opacity-60 p-3 rounded-lg mb-3">
                    <p className="text-xs font-semibold text-gray-700 mb-1">Optimal Collection Window</p>
                    <div className="flex items-center justify-between text-sm">
                      <span>{collection.optimal_collection_window.start_date} to {collection.optimal_collection_window.end_date}</span>
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        Confidence: {collection.optimal_collection_window.confidence_score?.toFixed(0)}%
                      </span>
                    </div>
                    <p className="text-xs text-gray-600 mt-1">{collection.optimal_collection_window.reason}</p>
                  </div>
                )}

                <div className="flex space-x-2">
                  <button
                    onClick={() => handleReschedule(collection.collection_id, collection.optimal_collection_window?.start_date)}
                    disabled={actionLoading}
                    className="flex-1 px-3 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center"
                  >
                    <RefreshCw className="w-4 h-4 mr-1" />
                    Reschedule to Optimal
                  </button>
                  <button
                    onClick={() => handleAttemptCollection(collection.collection_id)}
                    disabled={actionLoading}
                    className="flex-1 px-3 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 flex items-center justify-center"
                  >
                    <Zap className="w-4 h-4 mr-1" />
                    Attempt Now
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderRecommendations = () => {
    if (!data) return null;

    const recommendations = data.smart_recommendations || [];
    const riskSignals = data.risk_signals || [];

    const getPriorityColor = (priority) => {
      switch (priority) {
        case 'HIGH':
          return 'border-red-400 bg-red-50';
        case 'MEDIUM':
          return 'border-yellow-400 bg-yellow-50';
        case 'LOW':
          return 'border-blue-400 bg-blue-50';
        default:
          return 'border-gray-400 bg-gray-50';
      }
    };

    const getSeverityColor = (severity) => {
      switch (severity) {
        case 'CRITICAL':
          return 'bg-red-100 text-red-800';
        case 'HIGH':
          return 'bg-orange-100 text-orange-800';
        case 'MEDIUM':
          return 'bg-yellow-100 text-yellow-800';
        case 'LOW':
          return 'bg-blue-100 text-blue-800';
        default:
          return 'bg-gray-100 text-gray-800';
      }
    };

    return (
      <div className="space-y-6">
        {/* AI Recommendations */}
        <div className="bg-white rounded-lg shadow-md">
          <div className="p-4 border-b bg-gradient-to-r from-purple-50 to-blue-50">
            <h3 className="text-lg font-semibold flex items-center">
              <Zap className="w-5 h-5 mr-2 text-purple-600" />
              AI-Driven Recommendations ({recommendations.length})
            </h3>
          </div>
          <div className="p-4 space-y-4">
            {recommendations.map((rec, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-lg border-l-4 ${getPriorityColor(rec.priority)}`}
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-semibold text-gray-900">{(rec.recommendation_type || rec.type || 'Recommendation').replace(/_/g, ' ').toUpperCase()}</h4>
                    <span className={`inline-block px-2 py-1 rounded text-xs font-semibold mt-1 ${rec.priority === 'HIGH' ? 'bg-red-200 text-red-800' : rec.priority === 'MEDIUM' ? 'bg-yellow-200 text-yellow-800' : 'bg-blue-200 text-blue-800'}`}>
                      {rec.priority || 'MEDIUM'} PRIORITY
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-700 mb-2">{rec.reason || rec.recommendation || 'No details available'}</p>
                <div className="bg-white bg-opacity-60 p-3 rounded mt-2">
                  <p className="text-xs font-semibold text-gray-700 mb-1">Expected Impact:</p>
                  <p className="text-sm text-green-700">{rec.expected_impact}</p>
                </div>
                {rec.action_required && (
                  <div className="mt-2 p-3 bg-blue-50 rounded">
                    <p className="text-xs font-semibold text-gray-700 mb-1">Action Required:</p>
                    <p className="text-sm text-blue-900">{rec.action_required}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Risk Signals */}
        {riskSignals.length > 0 && (
          <div className="bg-white rounded-lg shadow-md">
            <div className="p-4 border-b bg-gradient-to-r from-red-50 to-orange-50">
              <h3 className="text-lg font-semibold flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2 text-red-600" />
                Risk Signals Detected ({riskSignals.length})
              </h3>
            </div>
            <div className="p-4 space-y-3">
              {riskSignals.map((signal, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-lg border-l-4 border-red-400 bg-gradient-to-r from-red-50 to-white"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-semibold text-gray-900">{(signal.signal_type || signal.type || 'Risk Signal').replace(/_/g, ' ').toUpperCase()}</h4>
                      <p className="text-xs text-gray-500 mt-1">{signal.signal || 'No details'}</p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${getSeverityColor(signal.severity || 'MEDIUM')}`}>
                      {signal.severity || 'MEDIUM'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mb-2">{signal.description || signal.signal || 'No description available'}</p>
                  {signal.mitigation && (
                    <div className="mt-2 p-3 bg-blue-50 rounded">
                      <p className="text-xs font-semibold text-gray-700 mb-1">Mitigation:</p>
                      <p className="text-sm text-blue-900">{signal.mitigation}</p>
                    </div>
                  )}
                  {signal.impact && (
                    <div className="mt-2 p-3 bg-yellow-50 rounded">
                      <p className="text-xs font-semibold text-gray-700 mb-1">Impact:</p>
                      <p className="text-sm text-yellow-900">{signal.impact}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderBehavioralInsights = () => {
    if (!data) return null;

    const insights = data.behavioral_insights || {};
    const salary = insights.salary_credit_pattern || {};
    const spending = insights.spending_pattern || {};
    const payment = insights.payment_behavior || {};

    return (
      <div className="space-y-6">
        {/* Salary Pattern */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <DollarSign className="w-5 h-5 mr-2 text-green-600" />
            Salary Credit Pattern
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Typical Credit Date</p>
              <p className="text-2xl font-bold text-green-700">Day {salary.typical_date}</p>
              <p className="text-xs text-gray-500 mt-1">of each month</p>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Typical Amount</p>
              <p className="text-2xl font-bold text-blue-700">{formatCurrency(salary.typical_amount)}</p>
              <p className="text-xs text-gray-500 mt-1">average monthly</p>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Consistency Score</p>
              <p className="text-2xl font-bold text-purple-700">{salary.consistency_score?.toFixed(1)}%</p>
              <p className="text-xs text-gray-500 mt-1">{salary.consistency_score > 80 ? 'Very Stable' : salary.consistency_score > 60 ? 'Moderate' : 'Irregular'}</p>
            </div>
          </div>
        </div>

        {/* Spending Pattern */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-blue-600" />
            Spending & Balance Pattern
          </h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-sm text-gray-700 mb-3">High Spending Periods</h4>
              <div className="space-y-2">
                {(spending.high_spending_days || []).map((day, idx) => (
                  <div key={idx} className="p-3 bg-red-50 rounded-lg border border-red-200">
                    <p className="font-semibold text-red-800">{day}</p>
                    <p className="text-xs text-gray-600">Higher outflow expected</p>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-sm text-gray-700 mb-3">Low Balance Periods</h4>
              <div className="space-y-2">
                {(spending.low_balance_days || []).map((day, idx) => (
                  <div key={idx} className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                    <p className="font-semibold text-yellow-800">{day}</p>
                    <p className="text-xs text-gray-600">Avoid collection attempts</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600">Average Daily Balance</p>
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(spending.average_daily_balance)}</p>
          </div>
        </div>

        {/* Payment Behavior */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Clock className="w-5 h-5 mr-2 text-purple-600" />
            Payment Behavior
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Preferred Time</p>
              <p className="text-lg font-bold text-purple-700">{payment.preferred_payment_time}</p>
              <p className="text-xs text-gray-500 mt-1">Optimal collection window</p>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Punctuality Score</p>
              <p className="text-2xl font-bold text-blue-700">{payment.payment_punctuality_score?.toFixed(1)}%</p>
              <p className="text-xs text-gray-500 mt-1">{payment.payment_punctuality_score > 80 ? 'Excellent' : payment.payment_punctuality_score > 60 ? 'Good' : 'Needs Attention'}</p>
            </div>
            <div className="p-4 bg-yellow-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Avg Delay</p>
              <p className="text-2xl font-bold text-yellow-700">{payment.avg_delay_days?.toFixed(1)} days</p>
              <p className="text-xs text-gray-500 mt-1">Payment delays</p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderCollectionHistory = () => {
    if (!data) return null;

    const history = data.collection_history || [];
    
    // Success rate by method
    const methodStats = {};
    history.forEach(h => {
      if (!methodStats[h.method]) {
        methodStats[h.method] = { total: 0, success: 0 };
      }
      methodStats[h.method].total++;
      if (h.status === 'SUCCESS') methodStats[h.method].success++;
    });

    const methodData = Object.entries(methodStats).map(([method, stats]) => ({
      method,
      'Success Rate': (stats.success / stats.total * 100).toFixed(1)
    }));

    return (
      <div className="space-y-6">
        {/* Method Performance */}
        {methodData.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <BarChart3 className="w-5 h-5 mr-2 text-blue-600" />
              Success Rate by Collection Method
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={methodData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="method" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="Success Rate" fill={COLORS.success} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* History Table */}
        <div className="bg-white rounded-lg shadow-md">
          <div className="p-4 border-b bg-gray-50">
            <h3 className="text-lg font-semibold flex items-center">
              <Clock className="w-5 h-5 mr-2 text-purple-600" />
              Collection History (Last 20 Attempts)
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Collection ID</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Date</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Attempt #</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Amount</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Balance</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Method</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Status</th>
                </tr>
              </thead>
              <tbody>
                {history.map((h, idx) => (
                  <tr key={idx} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm">{h.collection_id}</td>
                    <td className="px-4 py-3 text-sm">{h.attempt_date}</td>
                    <td className="px-4 py-3 text-sm">
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-semibold">
                        #{h.attempt_number}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm font-semibold">{formatCurrency(h.emi_amount)}</td>
                    <td className="px-4 py-3 text-sm">{formatCurrency(h.account_balance_at_attempt)}</td>
                    <td className="px-4 py-3 text-sm">
                      <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs">
                        {h.method}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${h.status === 'SUCCESS' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                        {h.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  const renderExplainability = () => {
    if (!data || !data.behavioral_insights) return null;

    const salaryPattern = data.behavioral_insights.salary_credit_pattern || {};
    const confidencePct = salaryPattern.confidence_percentage || 0;
    
    // Determine confidence color
    let confidenceColor = 'bg-red-100 text-red-800';
    if (confidencePct >= 70) confidenceColor = 'bg-green-100 text-green-800';
    else if (confidencePct >= 50) confidenceColor = 'bg-yellow-100 text-yellow-800';
    else if (confidencePct >= 20) confidenceColor = 'bg-orange-100 text-orange-800';

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <FileText className="w-5 h-5 mr-2 text-blue-600" />
            Salary Credit Detection Explainability
          </h3>

          {/* Confidence Score */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Detection Confidence</span>
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${confidenceColor}`}>
                {confidencePct.toFixed(2)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${
                  confidencePct >= 70 ? 'bg-green-600' :
                  confidencePct >= 50 ? 'bg-yellow-500' :
                  confidencePct >= 20 ? 'bg-orange-500' : 'bg-red-600'
                }`}
                style={{ width: `${confidencePct}%` }}
              />
            </div>
          </div>

          {/* Detection Method */}
          <div className="mb-6 p-4 border-l-4 border-blue-500 bg-blue-50">
            <h4 className="font-semibold text-blue-900 mb-2">Detection Methodology</h4>
            <p className="text-blue-800">{salaryPattern.detection_method || 'Statistical analysis of transaction patterns'}</p>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Typical Salary Day</p>
              <p className="text-2xl font-bold text-blue-600">Day {salaryPattern.typical_date || 'N/A'}</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Average Salary Amount</p>
              <p className="text-2xl font-bold text-green-600">{formatCurrency(salaryPattern.average_income || 0)}</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Median Salary Amount</p>
              <p className="text-2xl font-bold text-purple-600">{formatCurrency(salaryPattern.median_income || 0)}</p>
            </div>
          </div>

          {/* Income Variability */}
          <div className="mb-6 p-4 bg-yellow-50 border-l-4 border-yellow-500">
            <h4 className="font-semibold text-yellow-900 mb-2">Income Variability Analysis</h4>
            <p className="text-yellow-800 mb-2">
              Coefficient of Variation (CV): <span className="font-bold">{salaryPattern.income_cv?.toFixed(2) || 'N/A'}</span>
            </p>
            <p className="text-sm text-yellow-700">
              {salaryPattern.income_cv < 20 ? '✓ Excellent - Very stable income' :
               salaryPattern.income_cv < 40 ? '✓ Good - Moderately stable income' :
               salaryPattern.income_cv < 60 ? '⚠ Fair - Some income volatility' :
               salaryPattern.income_cv < 100 ? '⚠ Poor - High income volatility' :
               '⚠ Very Poor - Extremely volatile income'}
            </p>
          </div>

          {/* Sample Credits */}
          {salaryPattern.sample_credits && salaryPattern.sample_credits.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div className="bg-gray-50 px-4 py-3 border-b">
                <h4 className="font-semibold text-gray-900">Sample Salary Credits</h4>
                <p className="text-sm text-gray-600">Recent transactions identified as salary credits</p>
              </div>
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Date</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Amount</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Narration</th>
                  </tr>
                </thead>
                <tbody>
                  {salaryPattern.sample_credits.map((credit, idx) => (
                    <tr key={idx} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm">{credit.date}</td>
                      <td className="px-4 py-3 text-sm font-semibold text-green-600">{formatCurrency(credit.amount)}</td>
                      <td className="px-4 py-3 text-sm">{credit.narration}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderRawAAData = () => {
    if (!data) return null;

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Database className="w-5 h-5 mr-2 text-blue-600" />
            Raw Account Aggregator Data
          </h3>
          
          <div className="bg-gray-50 p-4 rounded-lg mb-4">
            <p className="text-sm text-gray-600 mb-2">
              This section displays the raw data retrieved from Account Aggregator used for Smart Collect analysis.
            </p>
          </div>

          {/* Account Summary */}
          {data.account_summary && (
            <div className="mb-6">
              <h4 className="font-semibold text-gray-900 mb-3">Account Summary</h4>
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <pre className="text-xs overflow-x-auto">
                  {JSON.stringify(data.account_summary, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {/* Recent Transactions */}
          {data.recent_transactions && (
            <div className="mb-6">
              <h4 className="font-semibold text-gray-900 mb-3">Recent Transactions (Last 50)</h4>
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 max-h-96 overflow-y-auto">
                <pre className="text-xs">
                  {JSON.stringify(data.recent_transactions, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {/* Behavioral Data */}
          {data.behavioral_insights && (
            <div className="mb-6">
              <h4 className="font-semibold text-gray-900 mb-3">Behavioral Insights Data</h4>
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <pre className="text-xs overflow-x-auto">
                  {JSON.stringify(data.behavioral_insights, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {/* Full Raw Data */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Complete Smart Collect Data</h4>
            <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 max-h-96 overflow-y-auto">
              <pre className="text-xs">
                {JSON.stringify(data, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-2" />
          <p className="text-gray-600">Loading Smart Collect data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <XCircle className="w-5 h-5 text-red-600 mr-2" />
          <span className="text-red-800">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
          <Zap className="w-8 h-8 mr-3 text-blue-600" />
          Smart Collect - AI-Powered Collection Optimization
        </h1>
        <p className="text-gray-600">
          Real-time account monitoring, optimal scheduling, and intelligent retry strategies
        </p>
      </div>

      {/* Customer Selector */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <div className="flex items-center space-x-4">
          <label className="font-semibold text-gray-700">Customer:</label>
          <select
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {[...Array(10)].map((_, i) => {
              const id = `CUST_MSM_${String(i + 1).padStart(5, '0')}`;
              return (
                <option key={id} value={id}>
                  {id}
                </option>
              );
            })}
          </select>
          <button
            onClick={loadSmartCollectData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-md mb-6">
        <div className="flex border-b overflow-x-auto">
          {[
            { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
            { id: 'upcoming', label: 'Upcoming Collections', icon: Calendar },
            { id: 'recommendations', label: 'AI Recommendations', icon: Zap },
            { id: 'insights', label: 'Behavioral Insights', icon: Activity },
            { id: 'history', label: 'Collection History', icon: Clock },
            { id: 'explainability', label: 'Explainability', icon: FileText },
            { id: 'rawdata', label: 'Raw AA Data', icon: Database }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedTab(tab.id)}
              className={`flex items-center px-6 py-3 font-medium transition-colors whitespace-nowrap ${
                selectedTab === tab.id
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div>
        {selectedTab === 'dashboard' && renderDashboard()}
        {selectedTab === 'upcoming' && renderUpcomingCollections()}
        {selectedTab === 'recommendations' && renderRecommendations()}
        {selectedTab === 'insights' && renderBehavioralInsights()}
        {selectedTab === 'history' && renderCollectionHistory()}
        {selectedTab === 'explainability' && renderExplainability()}
        {selectedTab === 'rawdata' && renderRawAAData()}
      </div>
    </div>
  );
};

export default SmartCollect;
