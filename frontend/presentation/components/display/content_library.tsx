/**
 * Content Library - Content management and organization interface
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  MagnifyingGlassIcon, 
  FunnelIcon,
  EllipsisVerticalIcon,
  DocumentIcon,
  MusicalNoteIcon,
  VideoCameraIcon,
  PhotoIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  ShareIcon,
  ArrowDownTrayIcon,
  CalendarDaysIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

interface ContentItem {
  id: string;
  name: string;
  type: 'audio' | 'video' | 'image' | 'document';
  size: number;
  uploadDate: string;
  status: 'protected' | 'processing' | 'unprotected' | 'violation';
  tags: string[];
  platforms: string[];
  views: number;
  revenue: number;
  thumbnail?: string;
}

interface Filter {
  type: string[];
  status: string[];
  dateRange: string;
  tags: string[];
}

const ContentLibrary: React.FC = () => {
  const [content, setContent] = React.useState<ContentItem[]>([]);
  const [filteredContent, setFilteredContent] = React.useState<ContentItem[]>([]);
  const [searchQuery, setSearchQuery] = React.useState('');
  const [filter, setFilter] = React.useState<Filter>({
    type: [],
    status: [],
    dateRange: 'all',
    tags: []
  });
  const [viewMode, setViewMode] = React.useState<'grid' | 'list'>('grid');
  const [showFilters, setShowFilters] = React.useState(false);
  const [selectedItems, setSelectedItems] = React.useState<string[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      const mockContent: ContentItem[] = [
        {
          id: '1',
          name: 'Track_Final_Master.mp3',
          type: 'audio',
          size: 8547328,
          uploadDate: '2024-01-15T10:30:00Z',
          status: 'protected',
          tags: ['music', 'electronic', 'master'],
          platforms: ['Spotify', 'YouTube', 'SoundCloud'],
          views: 125000,
          revenue: 3200
        },
        {
          id: '2',
          name: 'Album_Intro_Video.mp4',
          type: 'video',
          size: 45231680,
          uploadDate: '2024-01-14T15:45:00Z',
          status: 'protected',
          tags: ['video', 'promo', 'album'],
          platforms: ['YouTube', 'TikTok'],
          views: 98000,
          revenue: 2800
        },
        {
          id: '3',
          name: 'Behind_Scenes.mp4',
          type: 'video',
          size: 67890432,
          uploadDate: '2024-01-13T09:20:00Z',
          status: 'processing',
          tags: ['video', 'bts', 'documentary'],
          platforms: [],
          views: 0,
          revenue: 0
        },
        {
          id: '4',
          name: 'Album_Cover_Art.jpg',
          type: 'image',
          size: 2547328,
          uploadDate: '2024-01-12T14:15:00Z',
          status: 'violation',
          tags: ['artwork', 'album', 'design'],
          platforms: ['Instagram'],
          views: 15000,
          revenue: 0
        },
        {
          id: '5',
          name: 'Acoustic_Version.mp3',
          type: 'audio',
          size: 6789012,
          uploadDate: '2024-01-11T11:30:00Z',
          status: 'protected',
          tags: ['music', 'acoustic', 'alternate'],
          platforms: ['Spotify', 'Apple Music'],
          views: 76000,
          revenue: 1900
        }
      ];
      
      setContent(mockContent);
      setFilteredContent(mockContent);
      setLoading(false);
    }, 1000);
  }, []);

  React.useEffect(() => {
    let filtered = content;

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(item => 
        item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // Type filter
    if (filter.type.length > 0) {
      filtered = filtered.filter(item => filter.type.includes(item.type));
    }

    // Status filter
    if (filter.status.length > 0) {
      filtered = filtered.filter(item => filter.status.includes(item.status));
    }

    // Date range filter
    if (filter.dateRange !== 'all') {
      const now = new Date();
      const filterDate = new Date();
      
      switch (filter.dateRange) {
        case '7days':
          filterDate.setDate(now.getDate() - 7);
          break;
        case '30days':
          filterDate.setDate(now.getDate() - 30);
          break;
        case '90days':
          filterDate.setDate(now.getDate() - 90);
          break;
      }
      
      filtered = filtered.filter(item => 
        new Date(item.uploadDate) >= filterDate
      );
    }

    setFilteredContent(filtered);
  }, [content, searchQuery, filter]);

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'audio': return <MusicalNoteIcon className="h-8 w-8 text-green-500" />;
      case 'video': return <VideoCameraIcon className="h-8 w-8 text-red-500" />;
      case 'image': return <PhotoIcon className="h-8 w-8 text-blue-500" />;
      default: return <DocumentIcon className="h-8 w-8 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'protected': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-yellow-100 text-yellow-800';
      case 'unprotected': return 'bg-gray-100 text-gray-800';
      case 'violation': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const toggleItemSelection = (itemId: string) => {
    setSelectedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const selectAllItems = () => {
    setSelectedItems(filteredContent.map(item => item.id));
  };

  const clearSelection = () => {
    setSelectedItems([]);
  };

  const handleBulkAction = (action: string) => {
    console.log(`Performing ${action} on items:`, selectedItems);
    // Implement bulk actions
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Content Library</h1>
            <p className="text-gray-600">Manage your uploaded content and track performance</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
              className="bg-gray-100 text-gray-700 px-3 py-2 rounded-md hover:bg-gray-200 transition-colors"
            >
              {viewMode === 'grid' ? 'List View' : 'Grid View'}
            </button>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
              Upload Content
            </button>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Files</p>
              <p className="text-2xl font-bold text-gray-900">{content.length}</p>
            </div>
            <DocumentIcon className="h-10 w-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Protected</p>
              <p className="text-2xl font-bold text-gray-900">
                {content.filter(c => c.status === 'protected').length}
              </p>
            </div>
            <ShieldCheckIcon className="h-10 w-10 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Views</p>
              <p className="text-2xl font-bold text-gray-900">
                {content.reduce((sum, c) => sum + c.views, 0).toLocaleString()}
              </p>
            </div>
            <EyeIcon className="h-10 w-10 text-purple-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Revenue</p>
              <p className="text-2xl font-bold text-gray-900">
                ${content.reduce((sum, c) => sum + c.revenue, 0).toLocaleString()}
              </p>
            </div>
            <CalendarDaysIcon className="h-10 w-10 text-yellow-500" />
          </div>
        </div>
      </div>

      {/* Search and Filter Bar */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex items-center space-x-4 mb-4">
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search content..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            <FunnelIcon className="h-5 w-5 mr-2" />
            Filters
          </button>
        </div>

        {showFilters && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-4 border-t">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Content Type</label>
              <div className="space-y-1">
                {['audio', 'video', 'image', 'document'].map(type => (
                  <label key={type} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filter.type.includes(type)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setFilter(prev => ({ ...prev, type: [...prev.type, type] }));
                        } else {
                          setFilter(prev => ({ ...prev, type: prev.type.filter(t => t !== type) }));
                        }
                      }}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700 capitalize">{type}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <div className="space-y-1">
                {['protected', 'processing', 'unprotected', 'violation'].map(status => (
                  <label key={status} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filter.status.includes(status)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setFilter(prev => ({ ...prev, status: [...prev.status, status] }));
                        } else {
                          setFilter(prev => ({ ...prev, status: prev.status.filter(s => s !== status) }));
                        }
                      }}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700 capitalize">{status}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
              <select
                value={filter.dateRange}
                onChange={(e) => setFilter(prev => ({ ...prev, dateRange: e.target.value }))}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              >
                <option value="all">All Time</option>
                <option value="7days">Last 7 Days</option>
                <option value="30days">Last 30 Days</option>
                <option value="90days">Last 90 Days</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={() => setFilter({ type: [], status: [], dateRange: 'all', tags: [] })}
                className="w-full bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors"
              >
                Clear Filters
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Bulk Actions */}
      {selectedItems.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-blue-800">
                {selectedItems.length} item{selectedItems.length !== 1 ? 's' : ''} selected
              </span>
              <button
                onClick={clearSelection}
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Clear selection
              </button>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => handleBulkAction('protect')}
                className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors"
              >
                Protect
              </button>
              <button
                onClick={() => handleBulkAction('delete')}
                className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Content Grid/List */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">
            {filteredContent.length} items
          </h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={selectAllItems}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              Select All
            </button>
          </div>
        </div>

        {filteredContent.length === 0 ? (
          <div className="text-center py-12">
            <DocumentIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No content found</h3>
            <p className="text-gray-600">Try adjusting your search or filter criteria</p>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredContent.map((item) => (
              <div
                key={item.id}
                className={`border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer ${
                  selectedItems.includes(item.id) ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                }`}
                onClick={() => toggleItemSelection(item.id)}
              >
                <div className="flex items-center justify-between mb-3">
                  {getFileIcon(item.type)}
                  <div className="flex items-center space-x-1">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                      {item.status}
                    </span>
                    <button className="text-gray-400 hover:text-gray-600">
                      <EllipsisVerticalIcon className="h-5 w-5" />
                    </button>
                  </div>
                </div>

                <h4 className="font-medium text-gray-900 mb-2 truncate">{item.name}</h4>
                
                <div className="text-sm text-gray-600 space-y-1">
                  <div>{formatFileSize(item.size)}</div>
                  <div>{formatDate(item.uploadDate)}</div>
                  <div>{item.views.toLocaleString()} views</div>
                  <div>${item.revenue.toLocaleString()} revenue</div>
                </div>

                <div className="mt-3 flex flex-wrap gap-1">
                  {item.tags.slice(0, 2).map(tag => (
                    <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                      {tag}
                    </span>
                  ))}
                  {item.tags.length > 2 && (
                    <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                      +{item.tags.length - 2}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium text-gray-700">
                    <input
                      type="checkbox"
                      checked={selectedItems.length === filteredContent.length}
                      onChange={selectedItems.length === filteredContent.length ? clearSelection : selectAllItems}
                      className="mr-2"
                    />
                    Name
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Type</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Status</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Size</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Views</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Revenue</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Date</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredContent.map((item) => (
                  <tr key={item.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          checked={selectedItems.includes(item.id)}
                          onChange={() => toggleItemSelection(item.id)}
                        />
                        {getFileIcon(item.type)}
                        <div>
                          <div className="font-medium text-gray-900">{item.name}</div>
                          <div className="text-sm text-gray-500">{item.tags.join(', ')}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-gray-600 capitalize">{item.type}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                        {item.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-600">{formatFileSize(item.size)}</td>
                    <td className="py-3 px-4 text-gray-600">{item.views.toLocaleString()}</td>
                    <td className="py-3 px-4 text-gray-600">${item.revenue.toLocaleString()}</td>
                    <td className="py-3 px-4 text-gray-600">{formatDate(item.uploadDate)}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <button className="text-blue-600 hover:text-blue-700">
                          <EyeIcon className="h-4 w-4" />
                        </button>
                        <button className="text-gray-600 hover:text-gray-700">
                          <PencilIcon className="h-4 w-4" />
                        </button>
                        <button className="text-gray-600 hover:text-gray-700">
                          <ShareIcon className="h-4 w-4" />
                        </button>
                        <button className="text-gray-600 hover:text-gray-700">
                          <ArrowDownTrayIcon className="h-4 w-4" />
                        </button>
                        <button className="text-red-600 hover:text-red-700">
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default ContentLibrary;