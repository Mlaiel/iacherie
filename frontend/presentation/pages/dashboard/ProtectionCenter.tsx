/**
 * Protection Center - Content protection management interface
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  ShieldCheckIcon, 
  ExclamationTriangleIcon,
  EyeIcon,
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

interface ProtectionStats {
  totalProtected: number;
  activeMonitoring: number;
  violationsDetected: number;
  violationsResolved: number;
  protectionScore: number;
}

interface Violation {
  id: string;
  content: string;
  platform: string;
  severity: 'low' | 'medium' | 'high';
  status: 'pending' | 'resolved' | 'disputed';
  detectedAt: string;
}

const ProtectionCenter: React.FC = () => {
  const [stats, setStats] = React.useState<ProtectionStats | null>(null);
  const [violations, setViolations] = React.useState<Violation[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    // Simulate API calls
    setTimeout(() => {
      setStats({
        totalProtected: 1198,
        activeMonitoring: 892,
        violationsDetected: 43,
        violationsResolved: 38,
        protectionScore: 94
      });

      setViolations([
        {
          id: '1',
          content: 'Song_Master_Final.mp3',
          platform: 'YouTube',
          severity: 'high',
          status: 'pending',
          detectedAt: '2024-01-15T10:30:00Z'
        },
        {
          id: '2',
          content: 'Video_Intro_2024.mp4',
          platform: 'TikTok',
          severity: 'medium',
          status: 'resolved',
          detectedAt: '2024-01-14T15:45:00Z'
        },
        {
          id: '3',
          content: 'Album_Cover_Art.jpg',
          platform: 'Instagram',
          severity: 'low',
          status: 'disputed',
          detectedAt: '2024-01-13T09:20:00Z'
        }
      ]);

      setLoading(false);
    }, 1000);
  }, []);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'text-orange-600 bg-orange-100';
      case 'resolved': return 'text-green-600 bg-green-100';
      case 'disputed': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Protection Center</h1>
        <p className="text-gray-600">Monitor and manage your content protection</p>
      </div>

      {/* Protection Score Card */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8 border-l-4 border-green-500">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Protection Score</h2>
            <div className="flex items-center">
              <div className="text-4xl font-bold text-green-600 mr-4">{stats?.protectionScore}%</div>
              <div className="text-sm text-gray-600">
                <p>Your content is well protected</p>
                <p className="text-green-600">+2.5% from last month</p>
              </div>
            </div>
          </div>
          <ShieldCheckIcon className="h-16 w-16 text-green-500" />
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Protected</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.totalProtected.toLocaleString()}</p>
            </div>
            <ShieldCheckIcon className="h-10 w-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Monitoring</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.activeMonitoring.toLocaleString()}</p>
            </div>
            <EyeIcon className="h-10 w-10 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Violations Detected</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.violationsDetected}</p>
            </div>
            <ExclamationTriangleIcon className="h-10 w-10 text-red-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Violations Resolved</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.violationsResolved}</p>
            </div>
            <CheckCircleIcon className="h-10 w-10 text-green-500" />
          </div>
        </div>
      </div>

      {/* Protection Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer">
          <div className="flex items-center mb-4">
            <EyeIcon className="h-8 w-8 text-blue-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">Fingerprint Status</h3>
          </div>
          <p className="text-gray-600 mb-4">Monitor fingerprinting status and accuracy.</p>
          <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors">
            View Status
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer">
          <div className="flex items-center mb-4">
            <DocumentTextIcon className="h-8 w-8 text-yellow-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">Copyright Manager</h3>
          </div>
          <p className="text-gray-600 mb-4">Manage copyright claims and legal documentation.</p>
          <button className="w-full bg-yellow-600 text-white py-2 px-4 rounded-md hover:bg-yellow-700 transition-colors">
            Manage Claims
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer">
          <div className="flex items-center mb-4">
            <ExclamationTriangleIcon className="h-8 w-8 text-red-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">DMCA Tools</h3>
          </div>
          <p className="text-gray-600 mb-4">Generate and send DMCA takedown notices.</p>
          <button className="w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 transition-colors">
            DMCA Tools
          </button>
        </div>
      </div>

      {/* Recent Violations */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Recent Violations</h3>
          <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
            View All
          </button>
        </div>

        <div className="space-y-4">
          {violations.map((violation) => (
            <div key={violation.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  <h4 className="font-medium text-gray-900">{violation.content}</h4>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(violation.severity)}`}>
                    {violation.severity.toUpperCase()}
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(violation.status)}`}>
                    {violation.status.toUpperCase()}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <ClockIcon className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-500">
                    {new Date(violation.detectedAt).toLocaleDateString()}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-600">Platform: {violation.platform}</span>
                </div>
                <div className="flex space-x-2">
                  <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                    View Details
                  </button>
                  {violation.status === 'pending' && (
                    <button className="text-green-600 hover:text-green-700 text-sm font-medium">
                      Take Action
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

export default ProtectionCenter;