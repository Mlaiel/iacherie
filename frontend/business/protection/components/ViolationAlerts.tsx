/**
 * Violation Alerts - Copyright violation alerts and management
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  EyeIcon,
  ShieldExclamationIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';

interface ViolationAlert {
  id: string;
  contentTitle: string;
  platform: string;
  violationType: 'copyright' | 'trademark' | 'privacy' | 'other';
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'new' | 'investigating' | 'resolved' | 'dismissed';
  detectedAt: string;
  url: string;
  evidence: string[];
}

const ViolationAlerts: React.FC = () => {
  const [alerts, setAlerts] = React.useState<ViolationAlert[]>([
    {
      id: '1',
      contentTitle: 'My Original Video Tutorial',
      platform: 'YouTube',
      violationType: 'copyright',
      severity: 'high',
      status: 'new',
      detectedAt: '2025-01-09T10:30:00Z',
      url: 'https://youtube.com/watch?v=example1',
      evidence: ['Video fingerprint match: 95%', 'Audio match: 87%']
    },
    {
      id: '2',
      contentTitle: 'Photography Portfolio',
      platform: 'Instagram',
      violationType: 'copyright',
      severity: 'medium',
      status: 'investigating',
      detectedAt: '2025-01-08T15:45:00Z',
      url: 'https://instagram.com/post/example2',
      evidence: ['Image similarity: 92%', 'Metadata match']
    },
    {
      id: '3',
      contentTitle: 'Brand Logo Design',
      platform: 'Pinterest',
      violationType: 'trademark',
      severity: 'critical',
      status: 'resolved',
      detectedAt: '2025-01-07T09:20:00Z',
      url: 'https://pinterest.com/pin/example3',
      evidence: ['Logo match: 98%', 'Commercial use detected']
    }
  ]);

  const [filter, setFilter] = React.useState<string>('all');

  const getSeverityColor = (severity: ViolationAlert['severity']) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: ViolationAlert['status']) => {
    switch (status) {
      case 'new':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      case 'investigating':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />;
      case 'resolved':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'dismissed':
        return <EyeIcon className="h-5 w-5 text-gray-500" />;
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getViolationTypeIcon = (type: ViolationAlert['violationType']) => {
    switch (type) {
      case 'copyright':
        return <ShieldExclamationIcon className="h-5 w-5 text-red-500" />;
      case 'trademark':
        return <ShieldExclamationIcon className="h-5 w-5 text-orange-500" />;
      default:
        return <ShieldExclamationIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredAlerts = alerts.filter(alert => 
    filter === 'all' || alert.status === filter
  );

  const handleTakeAction = (alertId: string, action: string) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId 
        ? { ...alert, status: action as ViolationAlert['status'] }
        : alert
    ));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Violation Alerts</h2>
          <p className="text-gray-600">Monitor and manage copyright violations</p>
        </div>
        <div className="flex items-center space-x-3">
          <span className="text-sm text-gray-500">Filter by status:</span>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Alerts</option>
            <option value="new">New</option>
            <option value="investigating">Investigating</option>
            <option value="resolved">Resolved</option>
            <option value="dismissed">Dismissed</option>
          </select>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-8 w-8 text-red-500 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {alerts.filter(a => a.status === 'new').length}
              </p>
              <p className="text-sm text-gray-600">New Alerts</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center">
            <ClockIcon className="h-8 w-8 text-yellow-500 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {alerts.filter(a => a.status === 'investigating').length}
              </p>
              <p className="text-sm text-gray-600">Investigating</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center">
            <CheckCircleIcon className="h-8 w-8 text-green-500 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">
                {alerts.filter(a => a.status === 'resolved').length}
              </p>
              <p className="text-sm text-gray-600">Resolved</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center">
            <ShieldExclamationIcon className="h-8 w-8 text-blue-500 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">{alerts.length}</p>
              <p className="text-sm text-gray-600">Total Alerts</p>
            </div>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Recent Violations</h3>
        </div>
        
        <div className="divide-y divide-gray-200">
          {filteredAlerts.map(alert => (
            <div key={alert.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(alert.status)}
                    {getViolationTypeIcon(alert.violationType)}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="font-medium text-gray-900">{alert.contentTitle}</h4>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getSeverityColor(alert.severity)}`}>
                        {alert.severity.toUpperCase()}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-4 text-sm text-gray-600 mb-2">
                      <div className="flex items-center space-x-1">
                        <GlobeAltIcon className="h-4 w-4" />
                        <span>{alert.platform}</span>
                      </div>
                      <span>•</span>
                      <span>{formatDate(alert.detectedAt)}</span>
                      <span>•</span>
                      <span className="capitalize">{alert.violationType} violation</span>
                    </div>
                    
                    <div className="text-sm text-gray-600 mb-3">
                      <p className="font-medium mb-1">Evidence:</p>
                      <ul className="list-disc list-inside space-y-1">
                        {alert.evidence.map((evidence, index) => (
                          <li key={index}>{evidence}</li>
                        ))}
                      </ul>
                    </div>
                    
                    <a
                      href={alert.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                    >
                      View Violation →
                    </a>
                  </div>
                </div>
                
                <div className="flex space-x-2 ml-4">
                  {alert.status === 'new' && (
                    <>
                      <button
                        onClick={() => handleTakeAction(alert.id, 'investigating')}
                        className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-md text-sm font-medium hover:bg-yellow-200 transition-colors"
                      >
                        Investigate
                      </button>
                      <button
                        onClick={() => handleTakeAction(alert.id, 'dismissed')}
                        className="px-3 py-1 bg-gray-100 text-gray-800 rounded-md text-sm font-medium hover:bg-gray-200 transition-colors"
                      >
                        Dismiss
                      </button>
                    </>
                  )}
                  
                  {alert.status === 'investigating' && (
                    <button
                      onClick={() => handleTakeAction(alert.id, 'resolved')}
                      className="px-3 py-1 bg-green-100 text-green-800 rounded-md text-sm font-medium hover:bg-green-200 transition-colors"
                    >
                      Mark Resolved
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ViolationAlerts;