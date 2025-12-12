import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Trash2, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';

const FileManager = () => {
  const [fileStatus, setFileStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [deleting, setDeleting] = useState(null);

  const folders = [
    { name: 'raw', label: 'Raw Data', description: 'Original messy datasets', icon: '', color: 'blue' },
    { name: 'clean', label: 'Clean Data', description: 'Processed & validated datasets', icon: '', color: 'green' },
    { name: 'logs', label: 'Logs', description: 'Transformation & validation logs', icon: '', color: 'yellow' },
    { name: 'analytics', label: 'Analytics', description: 'Generated summaries & reports', icon: '', color: 'purple' },
  ];

  useEffect(() => {
    fetchFileStatus();
  }, []);

  const fetchFileStatus = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/files/status');
      setFileStatus(response.data);
    } catch (error) {
      console.error('Error fetching file status:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteFolder = async (folder) => {
    if (!window.confirm(`Are you sure you want to delete all files in ${folder}? This cannot be undone.`)) {
      return;
    }

    setDeleting(folder);
    try {
      const response = await axios.delete(`/api/files/${folder}`);
      alert(response.data.message);
      fetchFileStatus();
    } catch (error) {
      alert(`Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setDeleting(null);
    }
  };

  const getColorClasses = (color) => {
    const colors = {
      blue: 'border-blue-500 bg-blue-50',
      green: 'border-green-500 bg-green-50',
      yellow: 'border-yellow-500 bg-yellow-50',
      purple: 'border-purple-500 bg-purple-50',
    };
    return colors[color] || colors.blue;
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold text-gray-800">File Manager</h2>
        <button
          onClick={fetchFileStatus}
          disabled={loading}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 flex items-center space-x-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Warning Banner */}
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg">
        <div className="flex items-start">
          <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
          <div>
            <h3 className="text-sm font-medium text-yellow-800">Caution</h3>
            <p className="text-sm text-yellow-700 mt-1">
              Deleting folders will permanently remove all files. This action cannot be undone.
              Make sure to backup important data before proceeding.
            </p>
          </div>
        </div>
      </div>

      {/* Folders Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {folders.map((folder) => {
          const status = fileStatus?.[folder.name];
          const hasFiles = status?.file_count > 0;

          return (
            <div
              key={folder.name}
              className={`bg-white rounded-xl shadow-md border-l-4 ${getColorClasses(folder.color)} p-6`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start space-x-3">
                  <span className="text-3xl">{folder.icon}</span>
                  <div>
                    <h3 className="text-xl font-bold text-gray-800">{folder.label}</h3>
                    <p className="text-sm text-gray-600 mt-1">{folder.description}</p>
                  </div>
                </div>
                <button
                  onClick={() => deleteFolder(folder.name)}
                  disabled={deleting === folder.name || !hasFiles}
                  className="p-2 text-red-600 hover:bg-red-50 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  title="Delete all files"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>

              {status ? (
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Files:</span>
                    <span className="font-semibold text-gray-800">{status.file_count}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Total Size:</span>
                    <span className="font-semibold text-gray-800">{formatBytes(status.total_size)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Status:</span>
                    <span className="flex items-center space-x-1">
                      {hasFiles ? (
                        <>
                          <CheckCircle className="w-4 h-4 text-green-600" />
                          <span className="text-green-600 font-medium">Has Data</span>
                        </>
                      ) : (
                        <>
                          <AlertCircle className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-400 font-medium">Empty</span>
                        </>
                      )}
                    </span>
                  </div>
                  {status.files && status.files.length > 0 && (
                    <div className="mt-3 pt-3 border-t">
                      <p className="text-xs text-gray-500 mb-2">Files:</p>
                      <div className="space-y-1">
                        {status.files.slice(0, 5).map((file, idx) => (
                          <div key={idx} className="text-xs text-gray-600 truncate">
                            • {file}
                          </div>
                        ))}
                        {status.files.length > 5 && (
                          <div className="text-xs text-gray-500 italic">
                            ...and {status.files.length - 5} more
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-center py-4 text-gray-500">
                  Loading...
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Clear All Button */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-gray-800">Clear All Files</h3>
            <p className="text-sm text-gray-600 mt-1">
              Delete all files from all folders (raw, clean, logs, analytics)
            </p>
          </div>
          <button
            onClick={async () => {
              if (!window.confirm('Are you sure you want to delete ALL files from ALL folders? This cannot be undone!')) {
                return;
              }
              for (const folder of folders) {
                await deleteFolder(folder.name);
              }
            }}
            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center space-x-2"
          >
            <Trash2 className="w-5 h-5" />
            <span>Clear All</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default FileManager;
