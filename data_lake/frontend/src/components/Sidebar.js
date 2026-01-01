import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Activity, Terminal, Database, FileText, Trash2, BarChart3, BookOpen, Calculator, TrendingUp, DollarSign, FileSpreadsheet, User, Zap } from 'lucide-react';

const Sidebar = ({ isOpen, setIsOpen }) => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/pipeline', icon: Activity, label: 'Pipeline Monitor' },
    { path: '/analytics', icon: BarChart3, label: 'Analytics & Insights' },
    { path: '/customer-profile', icon: User, label: 'Customer Profile' },
    { path: '/smart-collect', icon: Zap, label: 'Smart Collect', badge: 'NEW' },
    { path: '/financial-summary', icon: DollarSign, label: 'Financial Summary (P&L)' },
    { path: '/detailed-metrics', icon: FileSpreadsheet, label: 'Detailed Metrics' },
    { path: '/methodology', icon: BookOpen, label: 'Credit Methodology' },
    { path: '/methodology/calculations', icon: Calculator, label: 'Credit Calculations' },
    { path: '/api-console', icon: Terminal, label: 'API Console' },
    { path: '/datasets', icon: Database, label: 'Datasets' },
    { path: '/logs', icon: FileText, label: 'Logs' },
    { path: '/files', icon: Trash2, label: 'File Manager' },
  ];

  if (!isOpen) return null;

  return (
    <aside className="fixed inset-y-0 left-0 w-64 bg-white shadow-lg z-20 transform transition-transform duration-300">
      <div className="flex flex-col h-full">
        <div className="p-6 border-b">
          <h2 className="text-lg font-bold text-gray-800">Navigation</h2>
        </div>
        
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
                  isActive
                    ? 'bg-primary-500 text-white shadow-md'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
                {item.badge && (
                  <span className="ml-auto px-2 py-1 text-xs font-bold bg-green-500 text-white rounded-full">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t">
          <div className="text-xs text-gray-500 space-y-1">
            <p>Version 1.0.0</p>
            <p>Synthetic Data Generator</p>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
