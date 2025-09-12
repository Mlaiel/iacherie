/**
 * Copyright Manager - Copyright registration and management
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  ShieldCheckIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  PlusIcon,
  EyeIcon
} from '@heroicons/react/24/outline';

interface CopyrightRegistration {
  id: string;
  title: string;
  type: 'video' | 'audio' | 'image' | 'text' | 'software';
  status: 'pending' | 'registered' | 'expired' | 'rejected';
  registrationDate: string;
  expiryDate: string;
  registrationNumber?: string;
  protectionLevel: 'essential' | 'standard' | 'premium';
  jurisdiction: string;
}

const CopyrightManager: React.FC = () => {
  const [registrations] = React.useState<CopyrightRegistration[]>([
    {
      id: '1',
      title: 'AI Tutorial Series - Episode 1',
      type: 'video',
      status: 'registered',
      registrationDate: '2024-12-15',
      expiryDate: '2094-12-15',
      registrationNumber: 'CR-2024-001234',
      protectionLevel: 'premium',
      jurisdiction: 'US'
    },
    {
      id: '2',
      title: 'Original Music Track - "Digital Dreams"',
      type: 'audio',
      status: 'registered',
      registrationDate: '2024-11-20',
      expiryDate: '2094-11-20',
      registrationNumber: 'CR-2024-001235',
      protectionLevel: 'standard',
      jurisdiction: 'EU'
    },
    {
      id: '3',
      title: 'Photography Portfolio 2024',
      type: 'image',
      status: 'pending',
      registrationDate: '2025-01-05',
      expiryDate: '2095-01-05',
      protectionLevel: 'essential',
      jurisdiction: 'US'
    }
  ]);

  const [showNewRegistration, setShowNewRegistration] = React.useState(false);
  const [filter, setFilter] = React.useState<string>('all');

  const getStatusColor = (status: CopyrightRegistration['status']) => {
    switch (status) {
      case 'registered': return 'bg-green-100 text-green-800 border-green-200';
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'expired': return 'bg-red-100 text-red-800 border-red-200';
      case 'rejected': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: CopyrightRegistration['status']) => {
    switch (status) {
      case 'registered':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'pending':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />;
      case 'expired':
      case 'rejected':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <DocumentTextIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getProtectionLevelColor = (level: CopyrightRegistration['protectionLevel']) => {
    switch (level) {
      case 'premium': return 'bg-purple-100 text-purple-800';
      case 'standard': return 'bg-blue-100 text-blue-800';
      case 'essential': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const filteredRegistrations = registrations.filter(reg => 
    filter === 'all' || reg.status === filter
  );

  const stats = {
    total: registrations.length,
    registered: registrations.filter(r => r.status === 'registered').length,
    pending: registrations.filter(r => r.status === 'pending').length,
    expired: registrations.filter(r => r.status === 'expired').length
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Copyright Manager</h2>
          <p className="text-gray-600">Register and manage your copyright protections</p>
        </div>
        <button
          onClick={() => setShowNewRegistration(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <PlusIcon className="h-4 w-4" />
          <span>New Registration</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center">
            <DocumentTextIcon className="h-8 w-8 text-blue-500 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              <p className="text-sm text-gray-600">Total Registrations</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center">
            <CheckCircleIcon className="h-8 w-8 text-green-500 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.registered}</p>
              <p className="text-sm text-gray-600">Registered</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center">
            <ClockIcon className="h-8 w-8 text-yellow-500 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.pending}</p>
              <p className="text-sm text-gray-600">Pending</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-8 w-8 text-red-500 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.expired}</p>
              <p className="text-sm text-gray-600">Expired</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filter and Registrations List */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Copyright Registrations</h3>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Registrations</option>
              <option value="registered">Registered</option>
              <option value="pending">Pending</option>
              <option value="expired">Expired</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
        </div>
        
        <div className="divide-y divide-gray-200">
          {filteredRegistrations.map(registration => (
            <div key={registration.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(registration.status)}
                    <ShieldCheckIcon className="h-5 w-5 text-blue-500" />
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="font-medium text-gray-900">{registration.title}</h4>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(registration.status)}`}>
                        {registration.status.toUpperCase()}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getProtectionLevelColor(registration.protectionLevel)}`}>
                        {registration.protectionLevel.toUpperCase()}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-3">
                      <div>
                        <p className="font-medium text-gray-700">Type</p>
                        <p className="capitalize">{registration.type}</p>
                      </div>
                      <div>
                        <p className="font-medium text-gray-700">Jurisdiction</p>
                        <p>{registration.jurisdiction}</p>
                      </div>
                      <div>
                        <p className="font-medium text-gray-700">Registered</p>
                        <p>{formatDate(registration.registrationDate)}</p>
                      </div>
                      <div>
                        <p className="font-medium text-gray-700">Expires</p>
                        <p>{formatDate(registration.expiryDate)}</p>
                      </div>
                    </div>
                    
                    {registration.registrationNumber && (
                      <div className="text-sm">
                        <span className="font-medium text-gray-700">Registration Number: </span>
                        <span className="font-mono text-blue-600">{registration.registrationNumber}</span>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex space-x-2 ml-4">
                  <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                    <EyeIcon className="h-4 w-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                    <DocumentTextIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* New Registration Modal (placeholder) */}
      {showNewRegistration && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">New Copyright Registration</h3>
            <p className="text-gray-600 mb-4">Copyright registration form would be implemented here.</p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowNewRegistration(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowNewRegistration(false)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Create Registration
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Protection Benefits */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h4 className="font-medium text-blue-900 mb-3">Copyright Protection Benefits</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-blue-700">
          <div>
            <h5 className="font-medium mb-1">Essential Protection</h5>
            <ul className="space-y-1">
              <li>• Automatic detection</li>
              <li>• Standard legal support</li>
              <li>• 1-year coverage</li>
            </ul>
          </div>
          <div>
            <h5 className="font-medium mb-1">Standard Protection</h5>
            <ul className="space-y-1">
              <li>• Enhanced monitoring</li>
              <li>• Legal assistance</li>
              <li>• International coverage</li>
            </ul>
          </div>
          <div>
            <h5 className="font-medium mb-1">Premium Protection</h5>
            <ul className="space-y-1">
              <li>• 24/7 monitoring</li>
              <li>• Full legal support</li>
              <li>• Global enforcement</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CopyrightManager;