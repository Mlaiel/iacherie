'use client';

import { useState } from 'react';
import { 
  EyeIcon,
  TrashIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  CheckCircleIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import { useContent } from '@/hooks/useContent';
import { useNotifications } from '@/hooks/useNotifications';

export function ContentManagement() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');
  
  const { content, deleteContent, isLoading } = useContent();
  const { success, error } = useNotifications();

  // Filter content based on search and filters
  const filteredContent = content.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || item.status === filterStatus;
    const matchesType = filterType === 'all' || item.type === filterType;
    
    return matchesSearch && matchesStatus && matchesType;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'protected':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'processing':
        return <ClockIcon className="w-5 h-5 text-yellow-500" />;
      case 'failed':
        return <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />;
      default:
        return <ClockIcon className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'protected':
        return 'Protected';
      case 'processing':
        return 'Processing';
      case 'uploading':
        return 'Uploading';
      case 'failed':
        return 'Failed';
      default:
        return 'Unknown';
    }
  };

  const getProtectionBadge = (level: string) => {
    const colors = {
      basic: 'bg-blue-100 text-blue-800',
      advanced: 'bg-purple-100 text-purple-800',
      enterprise: 'bg-green-100 text-green-800',
    };
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[level as keyof typeof colors] || colors.basic}`}>
        {level.charAt(0).toUpperCase() + level.slice(1)}
      </span>
    );
  };

  const handleDelete = async (contentId: string, contentName: string) => {
    if (window.confirm(`Are you sure you want to delete "${contentName}"?`)) {
      try {
        await deleteContent(contentId);
        success(`Content "${contentName}" deleted successfully`);
      } catch (err) {
        error(`Failed to delete "${contentName}"`);
      }
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Content Management</h1>
        <p className="text-gray-600">
          Monitor and manage your protected content across all platforms.
        </p>
      </div>

      {/* Filters and Search */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search content..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
        
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="all">All Status</option>
          <option value="protected">Protected</option>
          <option value="processing">Processing</option>
          <option value="uploading">Uploading</option>
          <option value="failed">Failed</option>
        </select>

        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="all">All Types</option>
          <option value="audio">Audio</option>
          <option value="video">Video</option>
          <option value="image">Image</option>
          <option value="text">Text</option>
        </select>
      </div>

      {/* Content Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card text-center">
          <div className="text-2xl font-bold text-gray-900">{content.length}</div>
          <div className="text-sm text-gray-600">Total Content</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-green-600">
            {content.filter(c => c.status === 'protected').length}
          </div>
          <div className="text-sm text-gray-600">Protected</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-yellow-600">
            {content.filter(c => c.status === 'processing').length}
          </div>
          <div className="text-sm text-gray-600">Processing</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-red-600">
            {content.filter(c => c.status === 'failed').length}
          </div>
          <div className="text-sm text-gray-600">Failed</div>
        </div>
      </div>

      {/* Content Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Content
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Protection Level
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Size
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredContent.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                    {content.length === 0 ? 'No content uploaded yet.' : 'No content matches your filters.'}
                  </td>
                </tr>
              ) : (
                filteredContent.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-lg bg-gray-100 flex items-center justify-center">
                            {item.type === 'audio' && <span className="text-blue-600">🎵</span>}
                            {item.type === 'video' && <span className="text-purple-600">🎬</span>}
                            {item.type === 'image' && <span className="text-green-600">🖼️</span>}
                            {item.type === 'text' && <span className="text-orange-600">📄</span>}
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900 truncate max-w-xs">
                            {item.name}
                          </div>
                          {item.fingerprint_id && (
                            <div className="text-xs text-gray-500">
                              ID: {item.fingerprint_id}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="capitalize text-sm text-gray-900">{item.type}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getStatusIcon(item.status)}
                        <span className="ml-2 text-sm text-gray-900">
                          {getStatusText(item.status)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getProtectionBadge(item.protection_level)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatFileSize(item.size)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(item.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          className="text-indigo-600 hover:text-indigo-900 p-1"
                          title="View Details"
                        >
                          <EyeIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(item.id, item.name)}
                          className="text-red-600 hover:text-red-900 p-1"
                          title="Delete Content"
                          disabled={isLoading}
                        >
                          <TrashIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}