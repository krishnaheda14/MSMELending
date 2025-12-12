import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { TrendingUp, Database, CheckCircle, AlertCircle, BarChart3, ArrowRight } from 'lucide-react';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/stats');
      setStats(response.data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error loading stats: {error}</p>
        <button onClick={fetchStats} className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
          Retry
        </button>
      </div>
    );
  }

  const datasets = [
    { name: 'Transactions', key: 'transactions', icon: '' },
    { name: 'Accounts', key: 'accounts', icon: '' },
    { name: 'GST Returns', key: 'gst', icon: '' },
    { name: 'Credit Reports', key: 'credit_reports', icon: '' },
    { name: 'Insurance', key: 'policies', icon: '' },
    { name: 'Mutual Funds', key: 'mutual_funds', icon: '' },
    { name: 'ONDC Orders', key: 'ondc_orders', icon: '' },
    { name: 'OCEN Loans', key: 'ocen_applications', icon: '' },
    { name: 'Consent', key: 'consent', icon: '' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-800">MSME Lending Dashboard</h2>
          <p className="text-gray-600 mt-1">Account Aggregator-based Credit Underwriting System</p>
        </div>
        <Link
          to="/analytics"
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2"
        >
          <BarChart3 className="w-4 h-4" />
          <span>View Analytics</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Lending Flow Diagram */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl p-8">
        <h3 className="text-2xl font-bold mb-6 text-center">Complete MSME Lending Journey</h3>
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          {/* Step 1 */}
          <div className="flex flex-col items-center text-center">
            <div className="w-20 h-20 bg-white/20 backdrop-blur rounded-full flex items-center justify-center mb-3 border-2 border-white">
              <span className="text-3xl">📋</span>
            </div>
            <div className="text-sm font-bold">Customer Consent</div>
            <div className="text-xs text-blue-100 mt-1">RBI AA Framework</div>
            <div className="text-xs text-blue-100">Digital signature</div>
          </div>
          <div className="text-3xl text-white/60 mx-2">→</div>
          
          {/* Step 2 */}
          <div className="flex flex-col items-center text-center">
            <div className="w-20 h-20 bg-white/20 backdrop-blur rounded-full flex items-center justify-center mb-3 border-2 border-white">
              <span className="text-3xl">📡</span>
            </div>
            <div className="text-sm font-bold">Data Fetch (AA)</div>
            <div className="text-xs text-blue-100 mt-1">Bank + GST</div>
            <div className="text-xs text-blue-100">Bureau + Insurance</div>
          </div>
          <div className="text-3xl text-white/60 mx-2">→</div>
          
          {/* Step 3 */}
          <div className="flex flex-col items-center text-center">
            <div className="w-20 h-20 bg-white/20 backdrop-blur rounded-full flex items-center justify-center mb-3 border-2 border-white">
              <span className="text-3xl">🧹</span>
            </div>
            <div className="text-sm font-bold">Clean & Validate</div>
            <div className="text-xs text-blue-100 mt-1">Standardize formats</div>
            <div className="text-xs text-blue-100">Remove duplicates</div>
          </div>
          <div className="text-3xl text-white/60 mx-2">→</div>
          
          {/* Step 4 */}
          <div className="flex flex-col items-center text-center">
            <div className="w-20 h-20 bg-white/20 backdrop-blur rounded-full flex items-center justify-center mb-3 border-2 border-white">
              <span className="text-3xl">📊</span>
            </div>
            <div className="text-sm font-bold">Analytics</div>
            <div className="text-xs text-blue-100 mt-1">Cashflow analysis</div>
            <div className="text-xs text-blue-100">Turnover trends</div>
          </div>
          <div className="text-3xl text-white/60 mx-2">→</div>
          
          {/* Step 5 */}
          <div className="flex flex-col items-center text-center">
            <div className="w-20 h-20 bg-white/20 backdrop-blur rounded-full flex items-center justify-center mb-3 border-2 border-white">
              <span className="text-3xl">🎯</span>
            </div>
            <div className="text-sm font-bold">Risk Score</div>
            <div className="text-xs text-blue-100 mt-1">Custom ML models</div>
            <div className="text-xs text-blue-100">Not bureau score</div>
          </div>
          <div className="text-3xl text-white/60 mx-2">→</div>
          
          {/* Step 6 */}
          <div className="flex flex-col items-center text-center">
            <div className="w-20 h-20 bg-white/20 backdrop-blur rounded-full flex items-center justify-center mb-3 border-2 border-white">
              <span className="text-3xl">✅</span>
            </div>
            <div className="text-sm font-bold">Loan Decision</div>
            <div className="text-xs text-blue-100 mt-1">Approve/Reject</div>
            <div className="text-xs text-blue-100">Terms & conditions</div>
          </div>
        </div>
        <div className="mt-6 text-center text-blue-100 text-sm">
          <strong>Per-Customer Only:</strong> All operations are customer-specific (DPDP Act 2023 compliant)
        </div>
      </div>

      {/* Quick Action Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Link to="/pipeline" className="group">
          <div className="bg-white rounded-xl shadow-md p-6 border-2 border-transparent hover:border-blue-500 transition-all cursor-pointer">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-800">Process Application</h3>
              <ArrowRight className="w-6 h-6 text-blue-500 group-hover:translate-x-1 transition-transform" />
            </div>
            <p className="text-gray-600 mb-4">
              Clean data, generate analytics, and calculate risk scores for customer loan applications
            </p>
            <div className="flex items-center space-x-2 text-blue-600 font-semibold">
              <CheckCircle className="w-5 h-5" />
              <span>Steps 3-5: Clean → Analytics → Risk Score</span>
            </div>
          </div>
        </Link>

        <Link to="/analytics" className="group">
          <div className="bg-white rounded-xl shadow-md p-6 border-2 border-transparent hover:border-purple-500 transition-all cursor-pointer">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-800">View Analytics</h3>
              <ArrowRight className="w-6 h-6 text-purple-500 group-hover:translate-x-1 transition-transform" />
            </div>
            <p className="text-gray-600 mb-4">
              Explore cashflow insights, GST turnover, credit analysis, and custom risk scores
            </p>
            <div className="flex items-center space-x-2 text-purple-600 font-semibold">
              <BarChart3 className="w-5 h-5" />
              <span>Step 6: Review & Decide</span>
            </div>
          </div>
        </Link>
      </div>

      {/* Data Sources Overview */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Data Sources (Per Customer)</h3>
        <p className="text-sm text-gray-600 mb-6">
          Multi-source financial data aggregated via Account Aggregator framework
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {datasets.map((dataset) => {
            const datasetStats = stats?.datasets?.[dataset.key];
            const rawCount = datasetStats?.raw || 0;
            const cleanCount = datasetStats?.clean || 0;
            const quality = rawCount > 0 ? ((cleanCount / rawCount) * 100).toFixed(1) : 0;

            return (
              <div key={dataset.key} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center space-x-3 mb-3">
                  <span className="text-2xl">{dataset.icon}</span>
                  <h4 className="font-semibold text-gray-800">{dataset.name}</h4>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Raw:</span>
                    <span className="font-medium">{rawCount.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Clean:</span>
                    <span className="font-medium">{cleanCount.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Quality:</span>
                    <span className={`font-medium ${quality >= 95 ? 'text-green-600' : quality >= 80 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {quality}%
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
