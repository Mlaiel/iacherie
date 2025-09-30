/**
 * DMCA Tools - DMCA takedown request management
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  DocumentTextIcon,
  PaperAirplaneIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  PlusIcon,
  EyeIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline';

interface DMCARequest {
  id: string;
  contentTitle: string;
  infringingUrl: string;
  platform: string;
  status: 'draft' | 'sent' | 'acknowledged' | 'complied' | 'rejected' | 'expired';
  submittedDate?: string;
  responseDate?: string;
  requestType: 'takedown' | 'counter_notice' | 'repeat_infringer';
  priority: 'low' | 'medium' | 'high' | 'urgent';
}

const DMCATools: React.FC = () => {
  const [requests] = React.useState<DMCARequest[]>([
    {
      id: '1',
      contentTitle: 'My Original Video Tutorial',
      infringingUrl: 'https://youtube.com/watch?v=example1',
      platform: 'YouTube',
      status: 'complied',
      submittedDate: '2025-01-05',
      responseDate: '2025-01-08',
      requestType: 'takedown',
      priority: 'high'
    },
    {
      id: '2',
      contentTitle: 'Photography Portfolio',
      infringingUrl: 'https://instagram.com/post/example2',
      platform: 'Instagram',
      status: 'acknowledged',
      submittedDate: '2025-01-07',
      requestType: 'takedown',
      priority: 'medium'
    },
    {
      id: '3',
      contentTitle: 'Music Track - "Digital Dreams"',
      infringingUrl: 'https://soundcloud.com/track/example3',
      platform: 'SoundCloud',
      status: 'sent',
      submittedDate: '2025-01-09',
      requestType: 'takedown',
      priority: 'high'
    }
  ]);

  const [showNewRequest, setShowNewRequest] = React.useState(false);
  const [filter, setFilter] = React.useState<string>('all');

  const getStatusColor = (status: DMCARequest['status']) => {
    switch (status) {
      case 'complied': return 'bg-green-100 text-green-800 border-green-200';
      case 'acknowledged': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'sent': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'rejected': return 'bg-red-100 text-red-800 border-red-200';
      case 'expired': return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'draft': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: DMCARequest['status']) => {
    switch (status) {
      case 'complied':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'acknowledged':
      case 'sent':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />;
      case 'rejected':
      case 'expired':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <DocumentTextIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getPriorityColor = (priority: DMCARequest['priority']) => {
    switch (priority) {
      case 'urgent': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
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

  const filteredRequests = requests.filter(request => 
    filter === 'all' || request.status === filter
  );

  const stats = {
    total: requests.length,
    sent: requests.filter(r => r.status === 'sent' || r.status === 'acknowledged').length,
    complied: requests.filter(r => r.status === 'complied').length,
    pending: requests.filter(r => r.status === 'draft' || r.status === 'sent').length
  };

  const generateDMCA = (requestId: string) => {
    // Simulate DMCA document generation
    console.log(`Generating DMCA document for request ${requestId}`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">DMCA Tools</h2>
          <p className="text-gray-600">Manage DMCA takedown requests and copyright enforcement</p>
        </div>
        <button
          onClick={() => setShowNewRequest(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <PlusIcon className="h-4 w-4" />
          <span>New DMCA Request</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center">
            <DocumentTextIcon className="h-8 w-8 text-blue-500 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              <p className="text-sm text-gray-600">Total Requests</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center">
            <PaperAirplaneIcon className="h-8 w-8 text-yellow-500 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.sent}</p>
              <p className="text-sm text-gray-600">Sent</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center">
            <CheckCircleIcon className="h-8 w-8 text-green-500 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.complied}</p>
              <p className="text-sm text-gray-600">Complied</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center">
            <ClockIcon className="h-8 w-8 text-orange-500 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.pending}</p>
              <p className="text-sm text-gray-600">Pending</p>
            </div>
          </div>
        </div>
      </div>

      {/* DMCA Request Templates */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Templates</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Standard Takedown</h4>
            <p className="text-sm text-gray-600 mb-3">For essential copyright infringement cases</p>
            <button className="w-full bg-blue-100 text-blue-800 py-2 px-3 rounded-md text-sm font-medium hover:bg-blue-200 transition-colors">
              Use Template
            </button>
          </div>
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Counter Notice</h4>
            <p className="text-sm text-gray-600 mb-3">For responding to false claims</p>
            <button className="w-full bg-green-100 text-green-800 py-2 px-3 rounded-md text-sm font-medium hover:bg-green-200 transition-colors">
              Use Template
            </button>
          </div>
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Repeat Infringer</h4>
            <p className="text-sm text-gray-600 mb-3">For habitual copyright violators</p>
            <button className="w-full bg-red-100 text-red-800 py-2 px-3 rounded-md text-sm font-medium hover:bg-red-200 transition-colors">
              Use Template
            </button>
          </div>
        </div>
      </div>

      {/* DMCA Requests List */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">DMCA Requests</h3>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Requests</option>
              <option value="draft">Draft</option>
              <option value="sent">Sent</option>
              <option value="acknowledged">Acknowledged</option>
              <option value="complied">Complied</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
        </div>
        
        <div className="divide-y divide-gray-200">
          {filteredRequests.map(request => (
            <div key={request.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(request.status)}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="font-medium text-gray-900">{request.contentTitle}</h4>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(request.status)}`}>
                        {request.status.replace('_', ' ').toUpperCase()}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(request.priority)}`}>
                        {request.priority.toUpperCase()}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600 mb-3">
                      <div>
                        <p className="font-medium text-gray-700">Platform</p>
                        <p>{request.platform}</p>
                      </div>
                      <div>
                        <p className="font-medium text-gray-700">Request Type</p>
                        <p className="capitalize">{request.requestType.replace('_', ' ')}</p>
                      </div>
                      <div>
                        <p className="font-medium text-gray-700">Submitted</p>
                        <p>{request.submittedDate ? formatDate(request.submittedDate) : 'Not submitted'}</p>
                      </div>
                    </div>
                    
                    <a
                      href={request.infringingUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                    >
                      View Infringing Content →
                    </a>
                  </div>
                </div>
                
                <div className="flex space-x-2 ml-4">
                  <button
                    onClick={() => generateDMCA(request.id)}
                    className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                    title="Download DMCA Document"
                  >
                    <ArrowDownTrayIcon className="h-4 w-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                    <EyeIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* New Request Modal (placeholder) */}
      {showNewRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">New DMCA Request</h3>
            <p className="text-gray-600 mb-4">DMCA request form would be implemented here.</p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowNewRequest(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowNewRequest(false)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Create Request
              </button>
            </div>
          </div>
        </div>
      )}

      {/* DMCA Information */}
      <div className="bg-yellow-50 rounded-lg p-6">
        <h4 className="font-medium text-yellow-900 mb-3">DMCA Process Information</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-yellow-700">
          <div>
            <h5 className="font-medium mb-2">Before Filing:</h5>
            <ul className="space-y-1">
              <li>• Ensure you own the copyright</li>
              <li>• Document the infringement</li>
              <li>• Gather evidence</li>
              <li>• Identify the infringing party</li>
            </ul>
          </div>
          <div>
            <h5 className="font-medium mb-2">After Filing:</h5>
            <ul className="space-y-1">
              <li>• Platform has 14 days to respond</li>
              <li>• Content may be removed</li>
              <li>• Infringer can file counter-notice</li>
              <li>• Monitor for compliance</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DMCATools;