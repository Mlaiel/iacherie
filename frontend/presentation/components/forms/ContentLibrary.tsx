/**
 * Content Library - Manage uploaded content library
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  FolderIcon,
  DocumentIcon,
  MusicalNoteIcon,
  VideoCameraIcon,
  PhotoIcon,
  MagnifyingGlassIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  ShareIcon
} from '@heroicons/react/24/outline';

interface ContentItem {
  id: string;
  filename: string;
  type: 'audio' | 'video' | 'image' | 'document';
  size: number;
  uploadedAt: string;
  status: 'protected' | 'processing' | 'unprotected';
  tags: string[];
  downloads: number;
  views: number;
  thumbnail?: string;
  duration?: number;
}

interface Folder {
  id: string;
  name: string;
  itemCount: number;
  createdAt: string;
}

const ContentLibrary: React.FC = () => {
  const [content, setContent] = React.useState<ContentItem[]>([]);
  const [folders, setFolders] = React.useState<Folder[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [searchTerm, setSearchTerm] = React.useState('');
  const [filterType, setFilterType] = React.useState<'all' | 'audio' | 'video' | 'image' | 'document'>('all');
  const [filterStatus, setFilterStatus] = React.useState<'all' | 'protected' | 'processing' | 'unprotected'>('all');
  const [viewMode, setViewMode] = React.useState<'grid' | 'list'>('grid');
  const [selectedItems, setSelectedItems] = React.useState<string[]>([]);

  React.useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setFolders([
        { id: '1', name: 'Music Albums', itemCount: 24, createdAt: '2024-01-10' },
        { id: '2', name: 'Video Content', itemCount: 12, createdAt: '2024-01-08' },
        { id: '3', name: 'Artwork & Images', itemCount: 18, createdAt: '2024-01-05' },
        { id: '4', name: 'Drafts', itemCount: 6, createdAt: '2024-01-15' }
      ]);

      setContent([
        {
          id: '1',
          filename: 'Track_Master_Final.mp3',
          type: 'audio',
          size: 8547328,
          uploadedAt: '2024-01-15T10:30:00Z',
          status: 'protected',
          tags: ['master', 'final', 'album'],
          downloads: 245,
          views: 1205,
          duration: 245
        },
        {
          id: '2',
          filename: 'Music_Video_HD.mp4',
          type: 'video',
          size: 157286400,
          uploadedAt: '2024-01-14T15:45:00Z',
          status: 'protected',
          tags: ['music video', 'hd', 'promotional'],
          downloads: 89,
          views: 2340,
          duration: 180
        },
        {
          id: '3',
          filename: 'Album_Cover_Art.jpg',
          type: 'image',
          size: 2048576,
          uploadedAt: '2024-01-13T09:20:00Z',
          status: 'protected',
          tags: ['artwork', 'cover', 'album'],
          downloads: 56,
          views: 890
        },
        {
          id: '4',
          filename: 'Demo_Recording.wav',
          type: 'audio',
          size: 45678912,
          uploadedAt: '2024-01-12T14:30:00Z',
          status: 'processing',
          tags: ['demo', 'raw', 'unmastered'],
          downloads: 12,
          views: 234,
          duration: 320
        },
        {
          id: '5',
          filename: 'Behind_Scenes.mp4',
          type: 'video',
          size: 89234567,
          uploadedAt: '2024-01-11T11:15:00Z',
          status: 'unprotected',
          tags: ['bts', 'documentary'],
          downloads: 23,
          views: 567,
          duration: 420
        }
      ]);

      setLoading(false);
    }, 1000);
  }, []);

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'audio': return <MusicalNoteIcon className="h-8 w-8 text-purple-500" />;
      case 'video': return <VideoCameraIcon className="h-8 w-8 text-red-500" />;
      case 'image': return <PhotoIcon className="h-8 w-8 text-blue-500" />;
      default: return <DocumentIcon className="h-8 w-8 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'protected': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-yellow-100 text-yellow-800';
      case 'unprotected': return 'bg-red-100 text-red-800';
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

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '-';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const filteredContent = content
    .filter(item => 
      item.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    )
    .filter(item => filterType === 'all' || item.type === filterType)
    .filter(item => filterStatus === 'all' || item.status === filterStatus);

  const toggleSelection = (itemId: string) => {
    setSelectedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const selectAll = () => {
    if (selectedItems.length === filteredContent.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(filteredContent.map(item => item.id));
    }
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
            <p className="text-gray-600">Manage and organize your uploaded content</p>
          </div>
          <div className="flex space-x-3">
            <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
              Upload Content
            </button>
            <button className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors">
              Create Folder
            </button>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
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
                {content.filter(item => item.status === 'protected').length}
              </p>
            </div>
            <EyeIcon className="h-10 w-10 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Downloads</p>
              <p className="text-2xl font-bold text-gray-900">
                {content.reduce((sum, item) => sum + item.downloads, 0)}
              </p>
            </div>
            <ArrowDownTrayIcon className="h-10 w-10 text-purple-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Views</p>
              <p className="text-2xl font-bold text-gray-900">
                {content.reduce((sum, item) => sum + item.views, 0).toLocaleString()}
              </p>
            </div>
            <EyeIcon className="h-10 w-10 text-yellow-500" />
          </div>
        </div>
      </div>

      {/* Folders */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Folders</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {folders.map((folder) => (
            <div key={folder.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors cursor-pointer">
              <div className="flex items-center mb-2">
                <FolderIcon className="h-8 w-8 text-blue-500 mr-3" />
                <div>
                  <h4 className="font-medium text-gray-900">{folder.name}</h4>
                  <p className="text-sm text-gray-500">{folder.itemCount} items</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex flex-col md:flex-row md:items-center space-y-4 md:space-y-0 md:space-x-4">
          {/* Search */}
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search files and tags..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Filters */}
          <div className="flex space-x-3">
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value as 'all' | 'audio' | 'video' | 'image' | 'document')}
              className="border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="all">All Types</option>
              <option value="audio">Audio</option>
              <option value="video">Video</option>
              <option value="image">Images</option>
              <option value="document">Documents</option>
            </select>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as 'all' | 'protected' | 'processing' | 'unprotected')}
              className="border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="all">All Status</option>
              <option value="protected">Protected</option>
              <option value="processing">Processing</option>
              <option value="unprotected">Unprotected</option>
            </select>

            <button
              onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
              className="border border-gray-300 rounded-md px-3 py-2 hover:bg-gray-50"
            >
              {viewMode === 'grid' ? 'List View' : 'Grid View'}
            </button>
          </div>
        </div>
      </div>

      {/* Bulk Actions */}
      {selectedItems.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <span className="font-medium text-blue-900">
                {selectedItems.length} items selected
              </span>
              <button
                onClick={selectAll}
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                {selectedItems.length === filteredContent.length ? 'Deselect All' : 'Select All'}
              </button>
            </div>
            <div className="flex space-x-2">
              <button className="bg-green-600 text-white px-3 py-1 rounded-md hover:bg-green-700 text-sm">
                Protect
              </button>
              <button className="bg-blue-600 text-white px-3 py-1 rounded-md hover:bg-blue-700 text-sm">
                Move to Folder
              </button>
              <button className="bg-red-600 text-white px-3 py-1 rounded-md hover:bg-red-700 text-sm">
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Content Grid/List */}
      <div className="bg-white rounded-lg shadow-md p-6">
        {viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredContent.map((item) => (
              <div
                key={item.id}
                className={`border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer ${
                  selectedItems.includes(item.id) ? 'border-blue-500 bg-blue-50' : ''
                }`}
                onClick={() => toggleSelection(item.id)}
              >
                <div className="flex items-center justify-between mb-3">
                  {getFileIcon(item.type)}
                  <input
                    type="checkbox"
                    checked={selectedItems.includes(item.id)}
                    onChange={() => toggleSelection(item.id)}
                    className="rounded"
                  />
                </div>

                <h4 className="font-medium text-gray-900 mb-2 truncate" title={item.filename}>
                  {item.filename}
                </h4>

                <div className="space-y-2 text-sm text-gray-500">
                  <div className="flex justify-between">
                    <span>Size:</span>
                    <span>{formatFileSize(item.size)}</span>
                  </div>
                  {item.duration && (
                    <div className="flex justify-between">
                      <span>Duration:</span>
                      <span>{formatDuration(item.duration)}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span>Views:</span>
                    <span>{item.views}</span>
                  </div>
                </div>

                <div className="mt-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                    {item.status.toUpperCase()}
                  </span>
                </div>

                <div className="mt-3 flex flex-wrap gap-1">
                  {item.tags.slice(0, 2).map((tag, index) => (
                    <span key={index} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
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
          <div className="space-y-2">
            {filteredContent.map((item) => (
              <div
                key={item.id}
                className={`border rounded-lg p-4 hover:bg-gray-50 transition-colors ${
                  selectedItems.includes(item.id) ? 'border-blue-500 bg-blue-50' : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <input
                      type="checkbox"
                      checked={selectedItems.includes(item.id)}
                      onChange={() => toggleSelection(item.id)}
                      className="rounded"
                    />
                    {getFileIcon(item.type)}
                    <div>
                      <h4 className="font-medium text-gray-900">{item.filename}</h4>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span>{formatFileSize(item.size)}</span>
                        {item.duration && <span>{formatDuration(item.duration)}</span>}
                        <span>{item.views} views</span>
                        <span>{item.downloads} downloads</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                      {item.status.toUpperCase()}
                    </span>
                    <div className="flex space-x-1">
                      <button className="text-gray-400 hover:text-blue-600">
                        <EyeIcon className="h-5 w-5" />
                      </button>
                      <button className="text-gray-400 hover:text-green-600">
                        <PencilIcon className="h-5 w-5" />
                      </button>
                      <button className="text-gray-400 hover:text-purple-600">
                        <ShareIcon className="h-5 w-5" />
                      </button>
                      <button className="text-gray-400 hover:text-red-600">
                        <TrashIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {filteredContent.length === 0 && (
          <div className="text-center py-12">
            <FolderIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No content found</h3>
            <p className="text-gray-600">No files match your search criteria.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ContentLibrary;