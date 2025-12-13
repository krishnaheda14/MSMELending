import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import PipelineMonitor from './components/PipelineMonitor';
import APIConsole from './components/APIConsole';
import DatasetViewer from './components/DatasetViewer';
import LogsViewer from './components/LogsViewer';
import FileManager from './components/FileManager';
import AnalyticsInsights from './components/AnalyticsInsights';
import EarningsVsSpendings from './components/EarningsVsSpendings';
import FinancialSummary from './components/FinancialSummary';
import CreditMethodology from './components/CreditMethodology';
import CreditCalculations from './components/CreditCalculations';
import Sidebar from './components/Sidebar';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
        
        <div className={`flex-1 flex flex-col overflow-hidden transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-0'}`}>
          <header className="bg-white shadow-sm z-10">
            <div className="px-6 py-4 flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setSidebarOpen(!sidebarOpen)}
                  className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent">
                  Indian Financial Data Lake
                </h1>
              </div>
              <div className="flex items-center space-x-2">
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                  ● Connected
                </span>
              </div>
            </div>
          </header>

          <main className="flex-1 overflow-auto p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/pipeline" element={<PipelineMonitor />} />
              <Route path="/analytics" element={<AnalyticsInsights />} />
              <Route path="/financial-summary" element={<FinancialSummary />} />
              <Route path="/detailed-metrics" element={<EarningsVsSpendings />} />
              <Route path="/methodology" element={<CreditMethodology />} />
              <Route path="/methodology/calculations" element={<CreditCalculations />} />
              <Route path="/api-console" element={<APIConsole />} />
              <Route path="/datasets" element={<DatasetViewer />} />
              <Route path="/logs" element={<LogsViewer />} />
              <Route path="/files" element={<FileManager />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
