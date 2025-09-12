/**
 * AIProtection - AI-powered content protection interface
 * 
 * Advanced protection interface with AI monitoring, threat detection,
 * and automated response capabilities
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState, useEffect } from 'react';
import {
  ShieldCheckIcon,
  ShieldExclamationIcon,
  EyeIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XMarkIcon,
  Cog6ToothIcon,
  BoltIcon,
  ChartBarIcon,
  ClockIcon,
  DocumentMagnifyingGlassIcon,
  GlobeAltIcon,
  LockClosedIcon,
  BeakerIcon
} from '@heroicons/react/24/outline';

export interface ProtectionStatus {
  id: string;
  contentId: string;
  contentName: string;
  protectionLevel: 'essential' | 'professional' | 'premium';
  status: 'active' | 'monitoring' | 'violation_detected' | 'action_taken' | 'disabled';
  aiConfidence: number;
  threatsDetected: number;
  lastScan: Date;
  fingerprints: string[];
  platforms: string[];
}

export interface ThreatAlert {
  id: string;
  type: 'copyright_violation' | 'unauthorized_use' | 'deepfake_detection' | 'content_modification';
  severity: 'low' | 'medium' | 'high' | 'critical';
  platform: string;
  url: string;
  description: string;
  confidence: number;
  detectedAt: Date;
  status: 'pending' | 'investigating' | 'action_taken' | 'false_positive';
}

export interface AIProtectionProps {
  contentItems?: ProtectionStatus[];
  alerts?: ThreatAlert[];
  onEnableProtection?: (contentId: string, level: string) => void;
  onDisableProtection?: (contentId: string) => void;
  onHandleAlert?: (alertId: string, action: string) => void;
  onConfigureSettings?: () => void;
  className?: string;
}

const protectionLevels = {
  essential: {
    name: 'Essential Protection',
    features: ['Content fingerprinting', 'Standard monitoring', 'Email alerts'],
    color: 'blue'
  },
  professional: {
    name: 'Professional Protection',
    features: ['AI-powered detection', 'Real-time monitoring', 'Automated takedowns', 'Analytics'],
    color: 'purple'
  },
  premium: {
    name: 'Premium Protection',
    features: ['Deep AI analysis', 'Cross-platform monitoring', 'Legal assistance', 'Priority support'],
    color: 'gold'
  }
};

const threatTypes = {
  copyright_violation: { name: 'Copyright Violation', icon: LockClosedIcon, color: 'red' },
  unauthorized_use: { name: 'Unauthorized Use', icon: ExclamationTriangleIcon, color: 'orange' },
  deepfake_detection: { name: 'Deepfake Detection', icon: BeakerIcon, color: 'purple' },
  content_modification: { name: 'Content Modification', icon: DocumentMagnifyingGlassIcon, color: 'yellow' }
};

const formatTimeAgo = (date: Date): string => {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
};

export const AIProtection: React.FC<AIProtectionProps> = ({
  contentItems = [],
  alerts = [],
  onEnableProtection,
  onDisableProtection,
  onHandleAlert,
  onConfigureSettings,
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'content' | 'alerts' | 'settings'>('overview');
  const [selectedLevel, setSelectedLevel] = useState<string>('professional');
  const [aiScanProgress, setAiScanProgress] = useState(0);
  const [isScanning, setIsScanning] = useState(false);

  // Simulate AI scanning progress
  useEffect(() => {
    if (isScanning) {
      const interval = setInterval(() => {
        setAiScanProgress(prev => {
          if (prev >= 100) {
            setIsScanning(false);
            return 0;
          }
          return prev + Math.random() * 15;
        });
      }, 300);
      return () => clearInterval(interval);
    }
  }, [isScanning]);

  const stats = {
    totalProtected: contentItems.length,
    activeMonitoring: contentItems.filter(item => item.status === 'active' || item.status === 'monitoring').length,
    threatsDetected: alerts.filter(alert => alert.status === 'pending').length,
    actionsLast24h: alerts.filter(alert => {
      const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
      return alert.detectedAt > dayAgo;
    }).length
  };

  const criticalAlerts = alerts.filter(alert => alert.severity === 'critical').slice(0, 3);
  const recentProtected = contentItems.filter(item => item.status === 'active').slice(0, 5);

  const startAIScan = () => {
    setIsScanning(true);
    setAiScanProgress(0);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <ShieldCheckIcon className="w-5 h-5 text-green-500" />;
      case 'monitoring': return <EyeIcon className="w-5 h-5 text-blue-500" />;
      case 'violation_detected': return <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />;
      case 'action_taken': return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'disabled': return <XMarkIcon className="w-5 h-5 text-gray-500" />;
      default: return <ShieldExclamationIcon className="w-5 h-5 text-gray-500" />;
    }
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md border p-6 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <ShieldCheckIcon className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AI Protection Center</h1>
              <p className="text-gray-600">Advanced AI-powered content protection and monitoring</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={startAIScan}
              disabled={isScanning}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
            >
              <BoltIcon className="w-4 h-4" />
              <span>{isScanning ? 'Scanning...' : 'AI Scan'}</span>
            </button>
            <button
              onClick={onConfigureSettings}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center space-x-2"
            >
              <Cog6ToothIcon className="w-4 h-4" />
              <span>Settings</span>
            </button>
          </div>
        </div>

        {/* AI Scan Progress */}
        {isScanning && (
          <div className="mt-4">
            <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
              <span>AI scanning in progress...</span>
              <span>{Math.round(aiScanProgress)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${aiScanProgress}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow-md border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Protected</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalProtected}</p>
            </div>
            <ShieldCheckIcon className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Monitoring</p>
              <p className="text-2xl font-bold text-blue-900">{stats.activeMonitoring}</p>
            </div>
            <EyeIcon className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Threats Detected</p>
              <p className="text-2xl font-bold text-red-900">{stats.threatsDetected}</p>
            </div>
            <ExclamationTriangleIcon className="w-8 h-8 text-red-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Actions (24h)</p>
              <p className="text-2xl font-bold text-purple-900">{stats.actionsLast24h}</p>
            </div>
            <BoltIcon className="w-8 h-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-md border">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'overview', name: 'Overview', icon: ChartBarIcon },
              { id: 'content', name: 'Protected Content', icon: ShieldCheckIcon },
              { id: 'alerts', name: 'Threat Alerts', icon: ExclamationTriangleIcon },
              { id: 'settings', name: 'Settings', icon: Cog6ToothIcon }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`
                  flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm
                  ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <tab.icon className="w-5 h-5" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Critical Alerts */}
              {criticalAlerts.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Critical Alerts</h3>
                  <div className="space-y-3">
                    {criticalAlerts.map((alert) => {
                      const ThreatIcon = threatTypes[alert.type]?.icon || ExclamationTriangleIcon;
                      return (
                        <div key={alert.id} className="flex items-center justify-between p-4 bg-red-50 border border-red-200 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <ThreatIcon className="w-5 h-5 text-red-500" />
                            <div>
                              <p className="font-medium text-red-900">{threatTypes[alert.type]?.name}</p>
                              <p className="text-sm text-red-700">{alert.description}</p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className="text-xs text-red-600">{formatTimeAgo(alert.detectedAt)}</span>
                            <button
                              onClick={() => onHandleAlert?.(alert.id, 'investigate')}
                              className="px-3 py-1 bg-red-600 text-white text-xs rounded-md hover:bg-red-700"
                            >
                              Investigate
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Recently Protected Content */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recently Protected Content</h3>
                <div className="space-y-3">
                  {recentProtected.map((item) => (
                    <div key={item.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(item.status)}
                        <div>
                          <p className="font-medium text-gray-900">{item.contentName}</p>
                          <p className="text-sm text-gray-500">
                            {protectionLevels[item.protectionLevel]?.name} • {item.platforms.length} platforms
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">{item.aiConfidence}% confidence</p>
                        <p className="text-xs text-gray-500">Last scan: {formatTimeAgo(item.lastScan)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Content Tab */}
          {activeTab === 'content' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Protected Content</h3>
                <div className="flex items-center space-x-2">
                  <select
                    value={selectedLevel}
                    onChange={(e) => setSelectedLevel(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm"
                  >
                    <option value="">All Levels</option>
                    <option value="essential">Essential</option>
                    <option value="professional">Professional</option>
                    <option value="premium">Premium</option>
                  </select>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Content
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Protection Level
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        AI Confidence
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {contentItems
                      .filter(item => !selectedLevel || item.protectionLevel === selectedLevel)
                      .map((item) => (
                        <tr key={item.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div>
                                <div className="text-sm font-medium text-gray-900">{item.contentName}</div>
                                <div className="text-sm text-gray-500">{item.platforms.join(', ')}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full
                              ${item.protectionLevel === 'essential' ? 'bg-blue-100 text-blue-800' :
                                item.protectionLevel === 'professional' ? 'bg-purple-100 text-purple-800' :
                                'bg-yellow-100 text-yellow-800'}`}>
                              {protectionLevels[item.protectionLevel]?.name}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center space-x-2">
                              {getStatusIcon(item.status)}
                              <span className="text-sm text-gray-900 capitalize">{item.status.replace('_', ' ')}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.aiConfidence}%
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button
                              onClick={() => onDisableProtection?.(item.contentId)}
                              className="text-red-600 hover:text-red-900 mr-3"
                            >
                              Disable
                            </button>
                            <button className="text-blue-600 hover:text-blue-900">
                              Configure
                            </button>
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Alerts Tab */}
          {activeTab === 'alerts' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Threat Alerts</h3>
              <div className="space-y-3">
                {alerts.map((alert) => {
                  const ThreatIcon = threatTypes[alert.type]?.icon || ExclamationTriangleIcon;
                  return (
                    <div key={alert.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3">
                          <ThreatIcon className="w-5 h-5 text-gray-500 mt-0.5" />
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <p className="font-medium text-gray-900">{threatTypes[alert.type]?.name}</p>
                              <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getSeverityColor(alert.severity)}`}>
                                {alert.severity.toUpperCase()}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 mb-2">{alert.description}</p>
                            <div className="flex items-center space-x-4 text-xs text-gray-500">
                              <span className="flex items-center space-x-1">
                                <GlobeAltIcon className="w-4 h-4" />
                                <span>{alert.platform}</span>
                              </span>
                              <span className="flex items-center space-x-1">
                                <ClockIcon className="w-4 h-4" />
                                <span>{formatTimeAgo(alert.detectedAt)}</span>
                              </span>
                              <span>Confidence: {alert.confidence}%</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => onHandleAlert?.(alert.id, 'takedown')}
                            className="px-3 py-1 bg-red-600 text-white text-xs rounded-md hover:bg-red-700"
                          >
                            Takedown
                          </button>
                          <button
                            onClick={() => onHandleAlert?.(alert.id, 'false_positive')}
                            className="px-3 py-1 bg-gray-600 text-white text-xs rounded-md hover:bg-gray-700"
                          >
                            False Positive
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Settings Tab */}
          {activeTab === 'settings' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">Protection Settings</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {Object.entries(protectionLevels).map(([key, level]) => (
                  <div key={key} className="border border-gray-200 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-lg font-semibold text-gray-900">{level.name}</h4>
                      <ShieldCheckIcon className={`w-6 h-6 text-${level.color}-500`} />
                    </div>
                    <ul className="space-y-2 mb-4">
                      {level.features.map((feature, index) => (
                        <li key={index} className="flex items-center space-x-2 text-sm text-gray-600">
                          <CheckCircleIcon className="w-4 h-4 text-green-500" />
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                    <button
                      onClick={() => onEnableProtection?.('', key)}
                      className={`w-full px-4 py-2 rounded-lg text-white font-medium
                        ${key === 'essential' ? 'bg-blue-600 hover:bg-blue-700' :
                          key === 'professional' ? 'bg-purple-600 hover:bg-purple-700' :
                          'bg-yellow-600 hover:bg-yellow-700'}`}
                    >
                      Select {level.name}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIProtection;