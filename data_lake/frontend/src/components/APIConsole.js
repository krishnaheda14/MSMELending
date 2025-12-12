import React, { useState } from 'react';
import axios from 'axios';
import { Send, Copy, Check, RefreshCw } from 'lucide-react';

const APIConsole = () => {
  const [selectedEndpoint, setSelectedEndpoint] = useState('');
  const [method, setMethod] = useState('GET');
  const [requestBody, setRequestBody] = useState('');
  const [queryParams, setQueryParams] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const endpoints = [
    { method: 'GET', path: '/api/stats', description: 'Get overall statistics' },
    { method: 'GET', path: '/api/data/:dataset', description: 'Get dataset data (transactions, accounts, gst, etc.)' },
    { method: 'GET', path: '/api/logs/:logType', description: 'Get transformation logs (parsing, cleaning, validation)' },
    { method: 'POST', path: '/api/pipeline/generate', description: 'Start data generation' },
    { method: 'POST', path: '/api/pipeline/clean', description: 'Start data cleaning' },
    { method: 'POST', path: '/api/pipeline/analytics', description: 'Generate analytics' },
    { method: 'POST', path: '/api/pipeline/stop', description: 'Stop running pipeline' },
    { method: 'DELETE', path: '/api/files/:folder', description: 'Delete files (raw, clean, logs, analytics)' },
    { method: 'GET', path: '/api/files/status', description: 'Get file status and counts' },
  ];

  const executeRequest = async () => {
    setLoading(true);
    setResponse(null);

    try {
      let url = selectedEndpoint;
      if (queryParams) {
        url += `?${queryParams}`;
      }

      const config = {
        method: method,
        url: url,
        headers: {
          'Content-Type': 'application/json',
        },
      };

      if (method !== 'GET' && requestBody) {
        config.data = JSON.parse(requestBody);
      }

      const startTime = Date.now();
      const res = await axios(config);
      const endTime = Date.now();

      setResponse({
        status: res.status,
        statusText: res.statusText,
        headers: res.headers,
        data: res.data,
        time: endTime - startTime,
      });
    } catch (error) {
      setResponse({
        status: error.response?.status || 500,
        statusText: error.response?.statusText || 'Error',
        headers: error.response?.headers || {},
        data: error.response?.data || { error: error.message },
        time: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(JSON.stringify(response?.data, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-800">API Debug Console</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Request Panel */}
        <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
          <h3 className="text-xl font-bold text-gray-800">Request</h3>

          {/* Available Endpoints */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quick Select Endpoint
            </label>
            <select
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
              value={selectedEndpoint}
              onChange={(e) => {
                const endpoint = endpoints.find(ep => ep.path === e.target.value);
                setSelectedEndpoint(e.target.value);
                setMethod(endpoint?.method || 'GET');
              }}
            >
              <option value="">Select an endpoint...</option>
              {endpoints.map((endpoint, idx) => (
                <option key={idx} value={endpoint.path}>
                  {endpoint.method} {endpoint.path} - {endpoint.description}
                </option>
              ))}
            </select>
          </div>

          {/* Method and URL */}
          <div className="flex space-x-2">
            <select
              className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
              value={method}
              onChange={(e) => setMethod(e.target.value)}
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="DELETE">DELETE</option>
              <option value="PUT">PUT</option>
            </select>
            <input
              type="text"
              className="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
              placeholder="/api/endpoint"
              value={selectedEndpoint}
              onChange={(e) => setSelectedEndpoint(e.target.value)}
            />
          </div>

          {/* Query Params */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Query Parameters (e.g., type=raw&limit=10)
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
              placeholder="key1=value1&key2=value2"
              value={queryParams}
              onChange={(e) => setQueryParams(e.target.value)}
            />
          </div>

          {/* Request Body */}
          {method !== 'GET' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Request Body (JSON)
              </label>
              <textarea
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none font-mono text-sm"
                rows="6"
                placeholder='{"key": "value"}'
                value={requestBody}
                onChange={(e) => setRequestBody(e.target.value)}
              />
            </div>
          )}

          {/* Send Button */}
          <button
            onClick={executeRequest}
            disabled={loading || !selectedEndpoint}
            className="w-full px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                <span>Loading...</span>
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span>Send Request</span>
              </>
            )}
          </button>
        </div>

        {/* Response Panel */}
        <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-gray-800">Response</h3>
            {response && (
              <button
                onClick={copyToClipboard}
                className="flex items-center space-x-1 px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
              >
                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                <span>{copied ? 'Copied!' : 'Copy'}</span>
              </button>
            )}
          </div>

          {!response ? (
            <div className="flex items-center justify-center h-64 text-gray-500">
              Send a request to see the response
            </div>
          ) : (
            <>
              {/* Response Status */}
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-4">
                  <span className={`px-3 py-1 rounded font-semibold ${
                    response.status >= 200 && response.status < 300
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {response.status}
                  </span>
                  <span className="text-gray-700">{response.statusText}</span>
                </div>
                <span className="text-sm text-gray-600">{response.time}ms</span>
              </div>

              {/* Response Body */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Response Body
                </label>
                <div className="bg-gray-900 rounded-lg p-4 overflow-auto max-h-96">
                  <pre className="text-sm text-green-400 font-mono">
                    {JSON.stringify(response.data, null, 2)}
                  </pre>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* API Documentation */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Available Endpoints</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Method</th>
                <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Endpoint</th>
                <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {endpoints.map((endpoint, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 text-xs font-semibold rounded ${
                      endpoint.method === 'GET' ? 'bg-blue-100 text-blue-800' :
                      endpoint.method === 'POST' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {endpoint.method}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-sm">{endpoint.path}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{endpoint.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default APIConsole;
