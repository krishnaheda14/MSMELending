import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Play, Square, RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react';
import io from 'socket.io-client';

const PipelineMonitor = () => {
  const [customerId, setCustomerId] = useState('CUST_MSM_00001'); // Customer ID input
  const [consentGranted, setConsentGranted] = useState(false);
  const [dataFetched, setDataFetched] = useState(false);
  const [pipeline, setPipeline] = useState({
    status: 'idle', // idle, running, completed, failed
    currentStep: null,
    steps: [
      { id: 1, name: 'Validate Consent & Fetch Data', status: 'pending', progress: 0 },
      { id: 2, name: 'Clean & Validate Data', status: 'pending', progress: 0 },
      { id: 3, name: 'Generate Analytics & Insights', status: 'pending', progress: 0 },
      { id: 4, name: 'Calculate Credit Score', status: 'pending', progress: 0 },
    ],
    logs: [],
  });

  const [socket, setSocket] = useState(null);

  useEffect(() => {
    // Connect to WebSocket for real-time updates
    const newSocket = io('http://localhost:5000', {
      transports: ['websocket', 'polling']
    });

    newSocket.on('connect', () => {
      console.log('WebSocket connected');
      addLog('Connected to server');
    });

    newSocket.on('pipeline_progress', (data) => {
      console.log('Progress update:', data);
      handleProgressUpdate(data);
    });

    newSocket.on('pipeline_log', (data) => {
      addLog(data.message, data.level);
    });

    newSocket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      addLog('Disconnected from server', 'warning');
    });

    setSocket(newSocket);

    return () => {
      if (newSocket) newSocket.disconnect();
    };
  }, []);

  const addLog = (message, level = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setPipeline(prev => ({
      ...prev,
      logs: [...prev.logs, { timestamp, message, level }].slice(-100) // Keep last 100 logs
    }));
  };

  const handleProgressUpdate = (data) => {
    setPipeline(prev => ({
      ...prev,
      currentStep: data.step,
      steps: prev.steps.map(step =>
        step.id === data.stepId
          ? { ...step, status: data.status, progress: data.progress }
          : step
      ),
      status: data.pipelineStatus || prev.status,
    }));
  };

  const handleConsentAndFetch = () => {
    if (!customerId || customerId.trim() === '') {
      addLog('Error: Customer ID is required', 'error');
      return;
    }

    addLog(`Starting consent validation for customer ${customerId}...`, 'info');
    setPipeline(prev => ({
      ...prev,
      status: 'running',
      steps: prev.steps.map(step => 
        step.id === 1 ? { ...step, status: 'running', progress: 10 } : step
      )
    }));

    // Simulate consent validation
    setTimeout(() => {
      addLog(`✓ Consent validated for customer ${customerId}`, 'success');
      addLog(`  - Consent ID: AA-${customerId}-${Date.now()}`, 'info');
      addLog(`  - Valid until: ${new Date(Date.now() + 180*24*60*60*1000).toLocaleDateString()}`, 'info');
      addLog(`  - Data sources: Bank, GST, Credit Bureau, Insurance`, 'info');
      
      setPipeline(prev => ({
        ...prev,
        steps: prev.steps.map(step => 
          step.id === 1 ? { ...step, progress: 30 } : step
        )
      }));

      setConsentGranted(true);
      
      // Simulate AA data fetch
      setTimeout(() => {
        addLog(`Fetching data from Account Aggregator...`, 'info');
        addLog(`  - Connecting to FIPs (Banks, GSTN, Bureaus)...`, 'info');
        
        setPipeline(prev => ({
          ...prev,
          steps: prev.steps.map(step => 
            step.id === 1 ? { ...step, progress: 50 } : step
          )
        }));

        setTimeout(() => {
          addLog(`  - Fetched banking data: 3 accounts, 1,247 transactions`, 'success');
          addLog(`  - Fetched GST data: 24 returns`, 'success');
          addLog(`  - Fetched credit report: CIBIL score available`, 'success');
          addLog(`  - Fetched insurance: 2 policies`, 'success');
          
          setPipeline(prev => ({
            ...prev,
            status: 'idle',
            steps: prev.steps.map(step => 
              step.id === 1 ? { ...step, status: 'completed', progress: 100 } : step
            )
          }));

          setDataFetched(true);
          addLog(`✓ Data fetch complete for customer ${customerId}`, 'success');
          addLog(`Ready to clean and analyze data`, 'info');
        }, 2000);
      }, 1500);
    }, 1000);
  };

  const startPipeline = async (stepName) => {
    if (!customerId || customerId.trim() === '') {
      addLog('Error: Customer ID is required', 'error');
      return;
    }
    
    // Determine which step this corresponds to
    const stepMap = {
      'clean': 2,
      'analytics': 3,
      'calculate_score': 4
    };
    const stepIndex = stepMap[stepName];
    
    try {
      // Update UI to show running state
      if (stepIndex !== undefined) {
        setPipeline(prev => ({
          ...prev,
          status: 'running',
          steps: prev.steps.map(step => 
            step.id === stepIndex ? { ...step, status: 'running', progress: 10 } : step
          )
        }));
      }
      
      addLog(`Starting ${stepName} for customer ${customerId}...`, 'info');
      const response = await axios.post(`/api/pipeline/${stepName}`, { customer_id: customerId });
      addLog(response.data.message || `✓ ${stepName} completed successfully`, 'success');
      
      // Update to completed
      if (stepIndex !== undefined) {
        setPipeline(prev => ({
          ...prev,
          status: 'idle',
          steps: prev.steps.map(step => 
            step.id === stepIndex ? { ...step, status: 'completed', progress: 100 } : step
          )
        }));
      }
    } catch (error) {
      addLog(`Error: ${error.response?.data?.error || error.message}`, 'error');
      
      // Update to failed
      if (stepIndex !== undefined) {
        setPipeline(prev => ({
          ...prev,
          status: 'idle',
          steps: prev.steps.map(step => 
            step.id === stepIndex ? { ...step, status: 'failed', progress: 0 } : step
          )
        }));
      }
    }
  };

  const stopPipeline = async () => {
    try {
      const response = await axios.post('/api/pipeline/stop');
      addLog(response.data.message, 'warning');
      setPipeline(prev => ({ ...prev, status: 'idle' }));
    } catch (error) {
      addLog(`Error: ${error.message}`, 'error');
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'running':
        return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getLogColor = (level) => {
    switch (level) {
      case 'error':
        return 'text-red-400';
      case 'warning':
        return 'text-yellow-400';
      case 'success':
        return 'text-green-400';
      default:
        return 'text-gray-300';
    }
  };

  const getProgressBarColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'running':
        return 'bg-blue-500 animate-pulse';
      case 'failed':
        return 'bg-red-500';
      default:
        return 'bg-gray-300';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-800">MSME Lending Pipeline</h2>
          <p className="text-gray-600 mt-1">Process customer loan application through the complete AA lending flow</p>
        </div>
      </div>

      {/* Customer ID Input - DPDP Compliance: Per-customer operations only */}
      <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-6">
        <div className="flex items-center space-x-2 mb-3">
          <span className="text-2xl">👤</span>
          <h3 className="text-lg font-bold text-gray-800">Customer Selection</h3>
          <span className="px-2 py-1 bg-blue-600 text-white text-xs rounded-full">Required</span>
        </div>
        <p className="text-sm text-gray-600 mb-4">
          Per RBI AA Framework & DPDP Act: All operations must be customer-specific. Enter customer ID to proceed.
        </p>
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
              className="w-full px-4 py-2 border-2 border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono"
            />
          </div>
          <div className="text-sm text-gray-600 pt-6">
            {customerId ? (
              <span className="text-green-600 font-semibold">✓ Customer ID set</span>
            ) : (
              <span className="text-red-600 font-semibold">⚠ Required</span>
            )}
          </div>
        </div>
      </div>

      {/* Lending Flow Visualization */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl shadow-md p-6 mb-6">
        <h3 className="text-xl font-bold text-gray-800 mb-6 text-center">AA-Based Lending Flow - Customer: {customerId}</h3>
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          {/* Step 1: Consent */}
          <div className="flex flex-col items-center text-center">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-2 ${
              pipeline.steps[0]?.status === 'completed' ? 'bg-green-500' :
              pipeline.steps[0]?.status === 'running' ? 'bg-blue-500 animate-pulse' :
              'bg-gray-300'
            }`}>
              <span className="text-white text-2xl">{pipeline.steps[0]?.status === 'completed' ? '✓' : '1'}</span>
            </div>
            <div className="text-xs font-semibold text-gray-700">STEP 1</div>
            <div className="text-sm font-bold text-gray-800 mt-1">Consent & Fetch</div>
            <div className="text-xs text-gray-500 mt-1">AA Framework</div>
          </div>
          <div className="text-2xl text-gray-400 mx-2">→</div>
          
          {/* Step 2: Clean */}
          <div className="flex flex-col items-center text-center">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-2 ${
              pipeline.steps[1]?.status === 'completed' ? 'bg-green-500' :
              pipeline.steps[1]?.status === 'running' ? 'bg-blue-500 animate-pulse' :
              'bg-gray-300'
            }`}>
              <span className="text-white text-2xl">{pipeline.steps[1]?.status === 'completed' ? '✓' : '2'}</span>
            </div>
            <div className="text-xs font-semibold text-gray-700">STEP 2</div>
            <div className="text-sm font-bold text-gray-800 mt-1">Clean & Validate</div>
            <div className="text-xs text-gray-500 mt-1">Standardize</div>
          </div>
          <div className="text-2xl text-gray-400 mx-2">→</div>
          
          {/* Step 3: Analytics */}
          <div className="flex flex-col items-center text-center">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-2 ${
              pipeline.steps[2]?.status === 'completed' ? 'bg-green-500' :
              pipeline.steps[2]?.status === 'running' ? 'bg-blue-500 animate-pulse' :
              'bg-gray-300'
            }`}>
              <span className="text-white text-2xl">{pipeline.steps[2]?.status === 'completed' ? '✓' : '3'}</span>
            </div>
            <div className="text-xs font-semibold text-gray-700">STEP 3</div>
            <div className="text-sm font-bold text-gray-800 mt-1">Analytics</div>
            <div className="text-xs text-gray-500 mt-1">Insights</div>
          </div>
          <div className="text-2xl text-gray-400 mx-2">→</div>
          
          {/* Step 4: Score */}
          <div className="flex flex-col items-center text-center">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-2 ${
              pipeline.steps[3]?.status === 'completed' ? 'bg-green-500' :
              pipeline.steps[3]?.status === 'running' ? 'bg-blue-500 animate-pulse' :
              'bg-gray-300'
            }`}>
              <span className="text-white text-2xl">{pipeline.steps[3]?.status === 'completed' ? '✓' : '4'}</span>
            </div>
            <div className="text-xs font-semibold text-gray-700">STEP 4</div>
            <div className="text-sm font-bold text-gray-800 mt-1">Credit Score</div>
            <div className="text-xs text-gray-500 mt-1">Risk Model</div>
          </div>
          <div className="text-2xl text-gray-400 mx-2">→</div>
          
          {/* Step 5: Decision */}
          <div className="flex flex-col items-center text-center">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-2 ${
              pipeline.steps[3]?.status === 'completed' ? 'bg-green-500' : 'bg-gray-300'
            }`}>
              <span className="text-white text-2xl">{pipeline.steps[3]?.status === 'completed' ? '✓' : '5'}</span>
            </div>
            <div className="text-xs font-semibold text-gray-700">STEP 5</div>
            <div className="text-sm font-bold text-gray-800 mt-1">Loan Decision</div>
            <div className="text-xs text-gray-500 mt-1">Approve/Reject</div>
          </div>
        </div>
      </div>

      {/* Pipeline Controls */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Process Customer Loan Application</h3>
        <p className="text-sm text-gray-600 mb-4">
          {!consentGranted ? 'Start by validating customer consent and fetching data from Account Aggregator' :
           !dataFetched ? 'Fetching data from AA...' :
           'Data fetched successfully. Now clean and analyze to make lending decision.'}
        </p>
        <div className="space-y-2">
          <button
            onClick={handleConsentAndFetch}
            disabled={pipeline.status === 'running' || !customerId || consentGranted}
            className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 text-lg font-semibold"
          >
            <Play className="w-5 h-5" />
            <span>{consentGranted ? '✓ Consent Validated & Data Fetched' : 'Step 1: Validate Consent & Fetch Data'}</span>
          </button>
          <button
            onClick={() => startPipeline('clean')}
            disabled={pipeline.status === 'running' || !customerId || !dataFetched || pipeline.steps[1].status === 'completed'}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 text-lg font-semibold"
          >
            <Play className="w-5 h-5" />
            <span>{pipeline.steps[1].status === 'completed' ? '✓ Data Cleaned' : 'Step 2: Clean & Validate Data'}</span>
          </button>
          <button
            onClick={() => startPipeline('analytics')}
            disabled={pipeline.status === 'running' || !customerId || pipeline.steps[1].status !== 'completed' || pipeline.steps[2].status === 'completed'}
            className="w-full px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 text-lg font-semibold"
          >
            <Play className="w-5 h-5" />
            <span>{pipeline.steps[2].status === 'completed' ? '✓ Analytics Generated' : 'Step 3: Generate Analytics & Insights'}</span>
          </button>
          <button
            onClick={() => startPipeline('calculate_score')}
            disabled={pipeline.status === 'running' || !customerId || pipeline.steps[2].status !== 'completed'}
            className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 text-lg font-semibold"
          >
            <Play className="w-5 h-5" />
            <span>{pipeline.steps[3].status === 'completed' ? '✓ Credit Score Calculated' : 'Step 4: Calculate Credit Score'}</span>
          </button>
        </div>
      </div>

      {/* Pipeline Steps */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Pipeline Steps</h3>
        <div className="space-y-4">
          {pipeline.steps.map((step) => (
            <div key={step.id} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(step.status)}
                  <span className="font-semibold text-gray-800">{step.name}</span>
                </div>
                <span className={`text-sm font-medium capitalize px-3 py-1 rounded-full ${
                  step.status === 'completed' ? 'bg-green-100 text-green-800' :
                  step.status === 'running' ? 'bg-blue-100 text-blue-800' :
                  step.status === 'failed' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-600'
                }`}>{step.status}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className={`h-3 rounded-full transition-all duration-700 ${getProgressBarColor(step.status)}`}
                  style={{ width: `${step.progress}%` }}
                />
              </div>
              <div className="mt-2 flex justify-between items-center text-xs">
                <span className="text-gray-500">Progress</span>
                <span className="font-bold text-gray-700">{step.progress}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Live Logs */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-800">Live Logs</h3>
          <button
            onClick={() => setPipeline(prev => ({ ...prev, logs: [] }))}
            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 flex items-center space-x-2"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Clear Logs</span>
          </button>
        </div>
        <div className="bg-gray-900 rounded-lg p-4 h-96 overflow-y-auto font-mono text-xs leading-relaxed">
          {pipeline.logs.length === 0 ? (
            <p className="text-gray-500">No logs yet. Start a pipeline to see real-time logs.</p>
          ) : (
            pipeline.logs.map((log, index) => (
              <div key={index} className={`mb-1 ${getLogColor(log.level)}`}>
                <span className="text-gray-400">[{log.timestamp}]</span>{' '}
                <span className="font-medium">{log.message}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default PipelineMonitor;
