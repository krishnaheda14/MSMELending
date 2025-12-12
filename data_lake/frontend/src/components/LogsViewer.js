import React, { useState } from 'react';
import axios from 'axios';
import ReactJson from 'react-json-view';
import { FileText, Search } from 'lucide-react';

const LogsViewer = () => {
  const [selectedLog, setSelectedLog] = useState('parsing');
  const [logs, setLogs] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('');

  const logTypes = [
    { value: 'parsing', label: 'Parsing Logs', description: 'Date/amount parsing issues' },
    { value: 'cleaning', label: 'Cleaning Logs', description: 'Transformations applied' },
    { value: 'validation', label: 'Validation Errors', description: 'Schema validation failures' },
  ];

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`/api/logs/${selectedLog}`);
      setLogs(response.data);
    } catch (error) {
      console.error('Error fetching logs:', error);
      setLogs({ error: error.message });
    } finally {
      setLoading(false);
    }
  };

  const filteredLogs = logs && Array.isArray(logs)
    ? logs.filter(log => 
        JSON.stringify(log).toLowerCase().includes(filter.toLowerCase())
      )
    : logs;

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-800">Transformation Logs</h2>

      {/* Log Type Selection */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {logTypes.map((logType) => (
          <button
            key={logType.value}
            onClick={() => {
              setSelectedLog(logType.value);
              setLogs(null);
            }}
            className={`p-4 rounded-lg border-2 transition-all ${
              selectedLog === logType.value
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-start space-x-3">
              <FileText className="w-6 h-6 text-primary-600 flex-shrink-0" />
              <div className="text-left">
                <h3 className="font-semibold text-gray-800">{logType.label}</h3>
                <p className="text-sm text-gray-600 mt-1">{logType.description}</p>
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* Controls */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none"
              placeholder="Filter logs..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            />
          </div>
          <button
            onClick={fetchLogs}
            disabled={loading}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Load Logs'}
          </button>
        </div>
      </div>

      {/* Logs Display */}
      {filteredLogs && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-gray-800">
              {logTypes.find(lt => lt.value === selectedLog)?.label}
            </h3>
            <span className="text-sm text-gray-600">
              {Array.isArray(filteredLogs) ? filteredLogs.length : 0} entries
            </span>
          </div>

          {filteredLogs.error ? (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-yellow-800">
              {filteredLogs.error}
            </div>
          ) : (
            <div className="bg-gray-900 rounded-lg p-4 max-h-[600px] overflow-auto">
              <ReactJson
                src={filteredLogs}
                theme="monokai"
                collapsed={2}
                displayDataTypes={false}
                displayObjectSize={true}
                enableClipboard={true}
                collapseStringsAfterLength={100}
                style={{ fontSize: '13px', lineHeight: '1.6' }}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default LogsViewer;
