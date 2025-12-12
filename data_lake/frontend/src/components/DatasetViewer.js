import React, { useState } from 'react';
import axios from 'axios';
import ReactJson from 'react-json-view';
import { Eye, Download } from 'lucide-react';

const DatasetViewer = () => {
  const [customerId, setCustomerId] = useState('CUST_MSM_00001');
  const [selectedDataset, setSelectedDataset] = useState('transactions');
  const [dataType, setDataType] = useState('raw');
  const [limit, setLimit] = useState(10);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const datasets = [
    { value: 'transactions', label: '💳 Transactions' },
    { value: 'accounts', label: '🏦 Accounts' },
    { value: 'gst', label: '📊 GST Returns' },
    { value: 'credit_reports', label: '📈 Credit Reports' },
    { value: 'policies', label: '🛡️ Insurance Policies' },
    { value: 'mutual_funds', label: '📊 Mutual Funds' },
    { value: 'ondc_orders', label: '🛒 ONDC Orders' },
    { value: 'ocen_applications', label: '💼 OCEN Loans' },
    { value: 'consent', label: '✅ Consent Artefacts' },
  ];

  const fetchData = async () => {
    if (!customerId || customerId.trim() === '') {
      setData({ error: 'Customer ID is required for data access (DPDP compliance)' });
      return;
    }
    setLoading(true);
    try {
      const response = await axios.get(`/api/data/${selectedDataset}?type=${dataType}&limit=${limit}&customer_id=${customerId}`);
      setData(response.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      setData({ error: error.response?.data?.error || error.message });
    } finally {
      setLoading(false);
    }
  };

  const downloadData = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedDataset}_${dataType}_${Date.now()}.json`;
    a.click();
  };

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-800">Dataset Viewer</h2>

      {/* Customer ID Input */}
      <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Customer ID <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={customerId}
              onChange={(e) => setCustomerId(e.target.value)}
              placeholder="e.g., CUST_MSM_00001"
              className="w-full px-4 py-2 border-2 border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono"
            />
          </div>
          <div className="text-sm pt-6">
            {customerId ? (
              <span className="text-green-600 font-semibold">✓ Valid</span>
            ) : (
              <span className="text-red-600 font-semibold">⚠ Required</span>
            )}
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Dataset</label>
            <select
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
              value={selectedDataset}
              onChange={(e) => setSelectedDataset(e.target.value)}
            >
              {datasets.map((ds) => (
                <option key={ds.value} value={ds.value}>
                  {ds.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
            <select
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
              value={dataType}
              onChange={(e) => setDataType(e.target.value)}
            >
              <option value="raw">Raw (Messy)</option>
              <option value="clean">Clean (Processed)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Limit</label>
            <input
              type="number"
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
              value={limit}
              onChange={(e) => setLimit(e.target.value)}
              min="1"
              max="1000"
            />
          </div>

          <div className="flex items-end space-x-2">
            <button
              onClick={fetchData}
              disabled={loading || !customerId}
              className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              <Eye className="w-4 h-4" />
              <span>{loading ? 'Loading...' : 'View'}</span>
            </button>
            {data && (
              <button
                onClick={downloadData}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center space-x-2"
              >
                <Download className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Data Display */}
      {data && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-gray-800">
              {selectedDataset} ({dataType}) - {data.count || 0} records
            </h3>
          </div>

          {data.error ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
              Error: {data.error}
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg p-4 max-h-[600px] overflow-auto">
              <ReactJson
                src={data}
                theme="monokai"
                collapsed={2}
                displayDataTypes={false}
                displayObjectSize={true}
                enableClipboard={true}
                style={{ fontSize: '13px' }}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DatasetViewer;
