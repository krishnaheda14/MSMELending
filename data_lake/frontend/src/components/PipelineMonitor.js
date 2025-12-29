import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Play, Square, RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react';
import io from 'socket.io-client';

const PipelineMonitor = () => {
  const [customerId, setCustomerId] = useState('CUST_MSM_00001'); // Customer ID input
  const [consentGranted, setConsentGranted] = useState(false);
  const [consentToken, setConsentToken] = useState(null);
  const [dataFetched, setDataFetched] = useState(false);
  const [debugMinimized, setDebugMinimized] = useState(false);
  const [currentExecution, setCurrentExecution] = useState({ step: null, command: null, status: 'idle' });
  const [pipeline, setPipeline] = useState({
    status: 'idle', // idle, running, completed, failed
    currentStep: null,
    steps: [
      { id: 0, name: 'Validate Consent & Fetch Data', status: 'pending', progress: 0 },
      { id: 1, name: 'Clean & Validate Data', status: 'pending', progress: 0 },
      { id: 2, name: 'Generate Analytics & Insights', status: 'pending', progress: 0 },
      { id: 3, name: 'Calculate Credit Score', status: 'pending', progress: 0 },
    ],
    logs: [],
  });

  const [socket, setSocket] = useState(null);

  useEffect(() => {
    // Load saved customer id from localStorage (so other components share the same selection)
    try {
      const stored = localStorage.getItem('msme_customer_id');
      if (stored) setCustomerId(stored);
    } catch (e) {
      // ignore
    }

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

  // When customerId changes, fetch server-side pipeline state/cache
  useEffect(() => {
    if (!customerId) return;
    try {
      axios.get('/api/pipeline/state', { params: { customer_id: customerId } })
        .then(resp => {
          const { cache, raw_present } = resp.data || {};
          if (cache) {
            // apply cached logs
            setPipeline(prev => ({ ...prev, logs: cache.logs || prev.logs }));
            // apply steps states
            if (cache.steps) {
              setPipeline(prev => ({
                ...prev,
                steps: prev.steps.map(s => {
                  const cs = cache.steps[String(s.id)];
                  if (cs) return { ...s, status: cs.status || s.status, progress: cs.progress || s.progress };
                  return s;
                }),
                status: cache.pipelineStatus || prev.status
              }));
            }
          }
          if (raw_present) {
            setDataFetched(true);
            // raw data presence implies consent & fetch (step 0) already completed
            setPipeline(prev => ({
              ...prev,
              steps: prev.steps.map(s => s.id === 0 ? { ...s, status: 'completed', progress: 100 } : s)
            }));
            setConsentGranted(true);
          }
        })
        .catch(err => {
          console.warn('Failed to load pipeline state', err.message || err);
        });
    } catch (e) {
      // ignore
    }
  }, [customerId]);

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
    if (data.status === 'completed' || data.status === 'failed') {
      setCurrentExecution(prev => ({ ...prev, status: data.status }));
    }
  };

  const applyCustomerId = () => {
    if (!customerId || customerId.trim() === '') {
      addLog('Error: Customer ID is required', 'error');
      return;
    }
    
    const trimmedId = customerId.trim();
    setCustomerId(trimmedId);
    try {
      localStorage.setItem('msme_customer_id', trimmedId);
    } catch (e) {
      // ignore
    }
    
    addLog(`Customer ID ${trimmedId} applied. Ready to process.`, 'success');
    addLog('Step 0: Validate consent and fetch data from Account Aggregator', 'info');
  };

  const handleConsentAndFetch = () => {
    if (!customerId || customerId.trim() === '') {
      addLog('Error: Customer ID is required', 'error');
      return;
    }

    setCurrentExecution({ step: 'Validate Consent & Fetch Data', command: `Simulating AA consent for ${customerId}`, status: 'running' });
    addLog(`Starting consent validation for customer ${customerId}...`, 'info');
    setPipeline(prev => ({
      ...prev,
      status: 'running',
      steps: prev.steps.map(step => 
        step.id === 0 ? { ...step, status: 'running', progress: 10 } : step
      )
    }));

    // Simulate consent validation
    setTimeout(() => {
      addLog(`✓ Consent validated for customer ${customerId}`, 'success');
      addLog(`  - Consent ID: AA-${customerId}-${Date.now()}`, 'info');
      addLog(`  - Valid until: ${new Date(Date.now() + 180*24*60*60*1000).toLocaleDateString()}`, 'info');
      addLog(`  - Data sources authorized: Banking, GST, Credit Bureau, Insurance, MF, ONDC, OCEN`, 'info');
      
      setPipeline(prev => ({
        ...prev,
        steps: prev.steps.map(step => 
          step.id === 0 ? { ...step, progress: 30 } : step
        )
      }));

      setConsentGranted(true);
      
      // Simulate AA data fetch
      setTimeout(() => {
        addLog(`Fetching data from Account Aggregator...`, 'info');
        addLog(`  - Connecting to FIPs (Banks, GSTN, Credit Bureaus)...`, 'info');
        
        setPipeline(prev => ({
          ...prev,
          steps: prev.steps.map(step => 
            step.id === 0 ? { ...step, progress: 50 } : step
          )
        }));

        setTimeout(() => {
          addLog(`  - Fetched banking data: Found pre-loaded transactions`, 'success');
          addLog(`  - Fetched GST data: Found pre-loaded returns`, 'success');
          addLog(`  - Fetched credit reports: Found pre-loaded bureau data`, 'success');
          addLog(`  - Fetched insurance & MF: Found pre-loaded policies`, 'success');
          addLog(`  - Fetched ONDC & OCEN: Found pre-loaded applications`, 'success');
          
          setPipeline(prev => ({
            ...prev,
            status: 'idle',
            steps: prev.steps.map(step => 
              step.id === 0 ? { ...step, status: 'completed', progress: 100 } : step
            )
          }));

          setDataFetched(true);
          addLog(`✓ Data fetch complete for customer ${customerId}`, 'success');
          addLog(`Ready to clean and analyze data`, 'info');
          setCurrentExecution({ step: null, command: null, status: 'idle' });
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
      'clean': 1,
      'analytics': 2,
      'calculate_score': 3
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
      
      // Include token for analytics if available
      const payload = { customer_id: customerId };
      if (stepName === 'analytics' && consentToken) {
        payload.token = consentToken;
        addLog(`Using consent token: ${consentToken}`, 'info');
      }
      
      const response = await axios.post(`/api/pipeline/${stepName}`, payload);
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

      {/* Current Execution Debug Panel */}
      {currentExecution.status === 'running' && (
        <div className="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <RefreshCw className="w-5 h-5 text-yellow-600 animate-spin" />
              <h3 className="text-lg font-bold text-gray-800">Currently Executing</h3>
            </div>
            <span className="px-3 py-1 bg-yellow-600 text-white text-xs rounded-full animate-pulse">RUNNING</span>
          </div>
          <div className="bg-white rounded-lg p-3 border border-yellow-200">
            <p className="text-sm text-gray-600 mb-1"><strong>Step:</strong> {currentExecution.step}</p>
            <p className="text-xs font-mono text-gray-700 bg-gray-50 p-2 rounded">{currentExecution.command}</p>
          </div>
        </div>
      )}

      {/* Customer ID Input - Pre-loaded Demo Datasets */}
      <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-6">
        <div className="flex items-center space-x-2 mb-3">
          <span className="text-2xl">👤</span>
          <h3 className="text-lg font-bold text-gray-800">Customer Selection - Pre-loaded Demo Datasets</h3>
          <span className="px-2 py-1 bg-blue-600 text-white text-xs rounded-full">Required</span>
        </div>
        <p className="text-sm text-gray-600 mb-4">
          10 pre-loaded customer datasets are available (CUST_MSM_00001 through CUST_MSM_00010). Each has randomly generated data with natural variation. Enter customer ID and click Apply to process their loan application.
        </p>
        <div className="flex items-center space-x-3 mb-3">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Customer ID <span className="text-red-500">*</span>
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                value={customerId}
                onChange={(e) => setCustomerId(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && applyCustomerId()}
                placeholder="e.g., CUST_MSM_00001"
                className="flex-1 px-4 py-2 border-2 border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono"
              />
              <button
                onClick={applyCustomerId}
                disabled={!customerId || customerId.trim() === ''}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold whitespace-nowrap"
              >
                Apply Customer ID
              </button>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg p-3 border border-blue-200">
          <p className="text-xs font-semibold text-gray-700 mb-2">📋 Available Demo Customers (specialized profiles):</p>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div><span className="font-mono bg-blue-50 px-2 py-1 rounded">CUST_MSM_00001</span> - Baseline</div>
            <div><span className="font-mono bg-orange-50 px-2 py-1 rounded">CUST_MSM_00002</span> - High Seasonality</div>
            <div><span className="font-mono bg-red-50 px-2 py-1 rounded">CUST_MSM_00003</span> - High Debt</div>
            <div><span className="font-mono bg-green-50 px-2 py-1 rounded">CUST_MSM_00004</span> - High Growth (126% CAGR)</div>
            <div><span className="font-mono bg-green-50 px-2 py-1 rounded">CUST_MSM_00005</span> - Stable Income ⭐</div>
            <div><span className="font-mono bg-red-50 px-2 py-1 rounded">CUST_MSM_00006</span> - High Bounce Rate</div>
            <div><span className="font-mono bg-red-50 px-2 py-1 rounded">CUST_MSM_00007</span> - Declining</div>
            <div><span className="font-mono bg-yellow-50 px-2 py-1 rounded">CUST_MSM_00008</span> - Customer Concentration</div>
            <div><span className="font-mono bg-green-50 px-2 py-1 rounded">CUST_MSM_00009</span> - High Growth #2</div>
            <div><span className="font-mono bg-orange-50 px-2 py-1 rounded">CUST_MSM_00010</span> - High Seasonality #2</div>
          </div>
          <p className="text-xs text-gray-500 mt-2 italic">⚠️ Run generate_all_specialized.bat to create all specialized profiles with distinct characteristics</p>
        </div>
      </div>

      {/* Lending Flow Visualization */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl shadow-md p-6 mb-6">
        <h3 className="text-xl font-bold text-gray-800 mb-6 text-center">AA-Based Lending Pipeline - Customer: {customerId}</h3>
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          {/* Step 0: Consent */}
          <div className="flex flex-col items-center text-center">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-2 ${
              pipeline.steps[0]?.status === 'completed' ? 'bg-green-500' :
              pipeline.steps[0]?.status === 'running' ? 'bg-blue-500 animate-pulse' :
              'bg-gray-300'
            }`}>
              <span className="text-white text-2xl">{pipeline.steps[0]?.status === 'completed' ? '✓' : '0'}</span>
            </div>
            <div className="text-xs font-semibold text-gray-700">STEP 0</div>
            <div className="text-sm font-bold text-gray-800 mt-1">Consent & Fetch</div>
            <div className="text-xs text-gray-500 mt-1">AA Framework</div>
          </div>
          <div className="text-2xl text-gray-400 mx-2">→</div>
          
          {/* Step 1: Clean */}
          <div className="flex flex-col items-center text-center">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-2 ${
              pipeline.steps[1]?.status === 'completed' ? 'bg-green-500' :
              pipeline.steps[1]?.status === 'running' ? 'bg-blue-500 animate-pulse' :
              'bg-gray-300'
            }`}>
              <span className="text-white text-2xl">{pipeline.steps[1]?.status === 'completed' ? '✓' : '1'}</span>
            </div>
            <div className="text-xs font-semibold text-gray-700">STEP 1</div>
            <div className="text-sm font-bold text-gray-800 mt-1">Clean & Validate</div>
            <div className="text-xs text-gray-500 mt-1">Standardize Data</div>
          </div>
          <div className="text-2xl text-gray-400 mx-2">→</div>
          
          {/* Step 2: Analytics */}
          <div className="flex flex-col items-center text-center">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-2 ${
              pipeline.steps[2]?.status === 'completed' ? 'bg-green-500' :
              pipeline.steps[2]?.status === 'running' ? 'bg-blue-500 animate-pulse' :
              'bg-gray-300'
            }`}>
              <span className="text-white text-2xl">{pipeline.steps[2]?.status === 'completed' ? '✓' : '2'}</span>
            </div>
            <div className="text-xs font-semibold text-gray-700">STEP 2</div>
            <div className="text-sm font-bold text-gray-800 mt-1">Analytics</div>
            <div className="text-xs text-gray-500 mt-1">Generate Insights</div>
          </div>
          <div className="text-2xl text-gray-400 mx-2">→</div>
          
          {/* Step 3: Score */}
          <div className="flex flex-col items-center text-center">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-2 ${
              pipeline.steps[3]?.status === 'completed' ? 'bg-green-500' :
              pipeline.steps[3]?.status === 'running' ? 'bg-blue-500 animate-pulse' :
              'bg-gray-300'
            }`}>
              <span className="text-white text-2xl">{pipeline.steps[3]?.status === 'completed' ? '✓' : '3'}</span>
            </div>
            <div className="text-xs font-semibold text-gray-700">STEP 3</div>
            <div className="text-sm font-bold text-gray-800 mt-1">Credit Score</div>
            <div className="text-xs text-gray-500 mt-1">Risk Model</div>
          </div>
          <div className="text-2xl text-gray-400 mx-2">→</div>
          
          {/* Step 4: Decision */}
          <div className="flex flex-col items-center text-center">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-2 ${
              pipeline.steps[3]?.status === 'completed' ? 'bg-green-500' : 'bg-gray-300'
            }`}>
              <span className="text-white text-2xl">{pipeline.steps[3]?.status === 'completed' ? '✓' : '4'}</span>
            </div>
            <div className="text-xs font-semibold text-gray-700">STEP 4</div>
            <div className="text-sm font-bold text-gray-800 mt-1">Loan Decision</div>
            <div className="text-xs text-gray-500 mt-1">Approve/Reject</div>
          </div>
        </div>
      </div>

      {/* Pipeline Controls */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Process Customer Loan Application</h3>
        <p className="text-sm text-gray-600 mb-4">
          {!consentGranted ? 'Start by validating customer consent and fetching data from Account Aggregator (simulated)' :
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
            <span>{consentGranted ? '✓ Consent Validated & Data Fetched' : 'Step 0: Validate Consent & Fetch Data (Simulated)'}</span>
          </button>
          {consentToken && (
            <div className="w-full px-4 py-2 bg-green-50 border border-green-300 text-green-800 rounded-lg flex items-center gap-2 text-sm">
              <CheckCircle className="w-4 h-4 flex-shrink-0" />
              <div className="flex-1 overflow-hidden">
                <span className="font-semibold">Consent Token:</span>
                <span className="ml-2 font-mono text-xs break-all">{consentToken}</span>
              </div>
            </div>
          )}
          <button
            onClick={() => startPipeline('clean')}
            disabled={pipeline.status === 'running' || !customerId || !dataFetched || pipeline.steps[1].status === 'completed'}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 text-lg font-semibold"
          >
            <Play className="w-5 h-5" />
            <span>{pipeline.steps[1].status === 'completed' ? '✓ Data Cleaned' : 'Step 1: Clean & Validate Data'}</span>
          </button>
          <button
            onClick={() => startPipeline('analytics')}
            disabled={
              pipeline.status === 'running' ||
              !customerId ||
              // enforce strict step-by-step: require step 0 and step 1 completed
              pipeline.steps[0].status !== 'completed' ||
              pipeline.steps[1].status !== 'completed' ||
              pipeline.steps[2].status === 'completed'
            }
            className="w-full px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 text-lg font-semibold"
          >
            <Play className="w-5 h-5" />
            <span>{pipeline.steps[2].status === 'completed' ? '✓ Analytics Generated' : 'Step 2: Generate Analytics & Insights'}</span>
          </button>
          <button
            onClick={() => startPipeline('calculate_score')}
            disabled={pipeline.status === 'running' || !customerId || pipeline.steps[2].status !== 'completed'}
            className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 text-lg font-semibold"
          >
            <Play className="w-5 h-5" />
            <span>{pipeline.steps[3].status === 'completed' ? '✓ Credit Score Calculated' : 'Step 3: Calculate Credit Score'}</span>
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
          <h3 className="text-xl font-bold text-gray-800">Live Logs & Debugging</h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setDebugMinimized(!debugMinimized)}
              className="px-3 py-1 text-sm bg-gray-200 hover:bg-gray-300 rounded flex items-center space-x-1"
            >
              <span>{debugMinimized ? '🔍 Show Debug Info' : '➖ Hide Debug Info'}</span>
            </button>
            <button
              onClick={() => setPipeline(prev => ({ ...prev, logs: [] }))}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 flex items-center space-x-2"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Clear Logs</span>
            </button>
          </div>
        </div>
        {!debugMinimized && (
          <div className="mb-4 bg-gray-50 border border-gray-300 rounded-lg p-4">
            <p className="text-xs font-semibold text-gray-600 mb-2">Debug Information:</p>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <span className="font-semibold">Pipeline Status:</span> <span className="px-2 py-0.5 rounded bg-gray-200">{pipeline.status}</span>
              </div>
              <div>
                <span className="font-semibold">Current Step:</span> <span className="px-2 py-0.5 rounded bg-gray-200">{pipeline.currentStep || 'None'}</span>
              </div>
              <div>
                <span className="font-semibold">Customer ID:</span> <span className="px-2 py-0.5 rounded bg-blue-100 font-mono">{customerId}</span>
              </div>
              <div>
                <span className="font-semibold">Steps Completed:</span> <span className="px-2 py-0.5 rounded bg-green-100">{pipeline.steps.filter(s => s.status === 'completed').length}/{pipeline.steps.length}</span>
              </div>
            </div>
            {currentExecution.status === 'running' && (
              <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded">
                <p className="text-xs font-semibold text-yellow-800">Active Execution:</p>
                <p className="text-xs font-mono text-gray-700 mt-1">{currentExecution.command}</p>
              </div>
            )}
          </div>
        )}
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
