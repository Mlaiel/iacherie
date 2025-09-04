/**
 * Visual Portfolio Management Component - Professional Dashboard
 * 
 * Provides visual portfolio management with filtering, organization, and display capabilities
 * Supports multiple content types with professional gallery interface
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  PhotoIcon,
  MusicalNoteIcon,
  VideoCameraIcon,
  DocumentTextIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  Squares2X2Icon,
  ListBulletIcon,
  EyeIcon,
  HeartIcon,
  ShareIcon,
  PlusIcon,
  StarIcon,
  TagIcon,
  CalendarIcon,
  AdjustmentsHorizontalIcon
} from '@heroicons/react/24/outline';

interface PortfolioItem {
  id: string;
  title: string;
  type: 'image' | 'video' | 'audio' | 'document';
  thumbnail_url: string;
  file_url: string;
  description: string;
  tags: string[];
  created_date: string;
  stats: {
    views: number;
    likes: number;
    shares: number;
    rating: number;
  };
  protection_status: 'protected' | 'processing' | 'unprotected';
  featured: boolean;
  category: string;
  metadata: {
    size: number;
    format: string;
    duration?: number;
    resolution?: string;
  };
}

interface FilterOptions {
  type: string[];
  category: string[];
  status: string[];
  featured: boolean | null;
  dateRange: string;
}

export function VisualPortfolioManagement() {
  const [portfolioItems, setPortfolioItems] = useState<PortfolioItem[]>([]);
  const [filteredItems, setFilteredItems] = useState<PortfolioItem[]>([]);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<FilterOptions>({
    type: [],
    category: [],
    status: [],
    featured: null,
    dateRange: 'all'
  });
  const [showFilters, setShowFilters] = useState(false);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);

  // Sample portfolio data
  useEffect(() => {
    setTimeout(() => {
      const sampleItems: PortfolioItem[] = [
        {
          id: '1',
          title: 'Epic Electronic Track',
          type: 'audio',
          thumbnail_url: '/api/thumbnails/audio_1.jpg',
          file_url: '/api/files/track_1.mp3',
          description: 'Professional electronic music track with modern production',
          tags: ['electronic', 'music', 'original', 'professional'],
          created_date: '2024-01-15T10:30:00Z',
          stats: { views: 2547, likes: 389, shares: 47, rating: 4.8 },
          protection_status: 'protected',
          featured: true,
          category: 'Music',
          metadata: { size: 8392847, format: 'MP3', duration: 245 }
        },
        {
          id: '2',
          title: 'Tutorial Video Series',
          type: 'video',
          thumbnail_url: '/api/thumbnails/video_2.jpg',
          file_url: '/api/files/tutorial_1.mp4',
          description: 'Professional tutorial video in high quality',
          tags: ['tutorial', 'education', 'professional', 'video'],
          created_date: '2024-01-14T14:22:00Z',
          stats: { views: 5892, likes: 743, shares: 129, rating: 4.9 },
          protection_status: 'protected',
          featured: true,
          category: 'Education',
          metadata: { size: 142857264, format: 'MP4', duration: 1847, resolution: '1920x1080' }
        },
        {
          id: '3',
          title: 'Portfolio Photography',
          type: 'image',
          thumbnail_url: '/api/thumbnails/image_3.jpg',
          file_url: '/api/files/photo_1.jpg',
          description: 'High-resolution professional photography',
          tags: ['photography', 'portfolio', 'professional', 'art'],
          created_date: '2024-01-13T09:15:00Z',
          stats: { views: 1834, likes: 267, shares: 34, rating: 4.7 },
          protection_status: 'processing',
          featured: false,
          category: 'Photography',
          metadata: { size: 2547293, format: 'JPEG', resolution: '3840x2160' }
        },
        {
          id: '4',
          title: 'Business Presentation',
          type: 'document',
          thumbnail_url: '/api/thumbnails/doc_4.jpg',
          file_url: '/api/files/presentation_1.pdf',
          description: 'Professional business presentation template',
          tags: ['business', 'presentation', 'template', 'professional'],
          created_date: '2024-01-12T16:45:00Z',
          stats: { views: 945, likes: 123, shares: 67, rating: 4.5 },
          protection_status: 'protected',
          featured: false,
          category: 'Business',
          metadata: { size: 1247563, format: 'PDF' }
        },
        {
          id: '5',
          title: 'Ambient Soundtrack',
          type: 'audio',
          thumbnail_url: '/api/thumbnails/audio_5.jpg',
          file_url: '/api/files/ambient_1.mp3',
          description: 'Relaxing ambient soundtrack for meditation',
          tags: ['ambient', 'relaxation', 'soundtrack', 'meditation'],
          created_date: '2024-01-11T11:20:00Z',
          stats: { views: 3421, likes: 567, shares: 89, rating: 4.6 },
          protection_status: 'protected',
          featured: false,
          category: 'Music',
          metadata: { size: 12847592, format: 'MP3', duration: 720 }
        },
        {
          id: '6',
          title: 'Creative Video Art',
          type: 'video',
          thumbnail_url: '/api/thumbnails/video_6.jpg',
          file_url: '/api/files/creative_1.mp4',
          description: 'Creative video art piece with visual effects',
          tags: ['creative', 'art', 'visual-effects', 'experimental'],
          created_date: '2024-01-10T08:30:00Z',
          stats: { views: 2187, likes: 298, shares: 52, rating: 4.4 },
          protection_status: 'unprotected',
          featured: false,
          category: 'Art',
          metadata: { size: 89472635, format: 'MP4', duration: 432, resolution: '1920x1080' }
        }
      ];
      
      setPortfolioItems(sampleItems);
      setFilteredItems(sampleItems);
      setLoading(false);
    }, 500);
  }, []);

  // Apply filters
  useEffect(() => {
    let filtered = [...portfolioItems];

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(item => 
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // Type filter
    if (filters.type.length > 0) {
      filtered = filtered.filter(item => filters.type.includes(item.type));
    }

    // Category filter
    if (filters.category.length > 0) {
      filtered = filtered.filter(item => filters.category.includes(item.category));
    }

    // Status filter
    if (filters.status.length > 0) {
      filtered = filtered.filter(item => filters.status.includes(item.protection_status));
    }

    // Featured filter
    if (filters.featured !== null) {
      filtered = filtered.filter(item => item.featured === filters.featured);
    }

    // Date range filter
    if (filters.dateRange !== 'all') {
      const now = new Date();
      const cutoffDate = new Date();
      
      switch (filters.dateRange) {
        case 'week':
          cutoffDate.setDate(now.getDate() - 7);
          break;
        case 'month':
          cutoffDate.setMonth(now.getMonth() - 1);
          break;
        case 'year':
          cutoffDate.setFullYear(now.getFullYear() - 1);
          break;
      }
      
      filtered = filtered.filter(item => new Date(item.created_date) >= cutoffDate);
    }

    setFilteredItems(filtered);
  }, [portfolioItems, searchQuery, filters]);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'audio': return MusicalNoteIcon;
      case 'video': return VideoCameraIcon;
      case 'image': return PhotoIcon;
      case 'document': return DocumentTextIcon;
      default: return DocumentTextIcon;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'protected': return 'bg-green-100 text-green-800 border-green-200';
      case 'processing': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'unprotected': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatFileSize = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const toggleFilter = (filterType: keyof FilterOptions, value: any) => {
    if (filterType === 'featured') {
      setFilters(prev => ({ ...prev, featured: prev.featured === value ? null : value }));
    } else if (Array.isArray(filters[filterType])) {
      setFilters(prev => ({
        ...prev,
        [filterType]: (prev[filterType] as string[]).includes(value)
          ? (prev[filterType] as string[]).filter(item => item !== value)
          : [...(prev[filterType] as string[]), value]
      }));
    } else {
      setFilters(prev => ({ ...prev, [filterType]: value }));
    }
  };

  const clearFilters = () => {
    setFilters({
      type: [],
      category: [],
      status: [],
      featured: null,
      dateRange: 'all'
    });
    setSearchQuery('');
  };

  const toggleItemSelection = (itemId: string) => {
    setSelectedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md border p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="border border-gray-200 rounded-lg p-4">
                <div className="h-40 bg-gray-200 rounded mb-3"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md border">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <PhotoIcon className="w-5 h-5 text-purple-500" />
            <h3 className="text-lg font-semibold text-gray-900">Visual Portfolio Management</h3>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              {viewMode === 'grid' ? (
                <ListBulletIcon className="w-5 h-5" />
              ) : (
                <Squares2X2Icon className="w-5 h-5" />
              )}
            </button>
            <button className="btn-primary">
              <PlusIcon className="w-4 h-4 mr-2" />
              Add Content
            </button>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-4 mb-4">
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search portfolio items..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`btn-secondary ${showFilters ? 'bg-purple-100 text-purple-700' : ''}`}
          >
            <FunnelIcon className="w-4 h-4 mr-2" />
            Filters
          </button>
          {(filters.type.length > 0 || filters.category.length > 0 || filters.status.length > 0 || 
            filters.featured !== null || filters.dateRange !== 'all' || searchQuery) && (
            <button onClick={clearFilters} className="text-sm text-purple-600 hover:text-purple-800">
              Clear All
            </button>
          )}
        </div>

        {/* Filter Options */}
        {showFilters && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-4 bg-white rounded-lg border border-gray-200">
            {/* Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Content Type</label>
              <div className="space-y-2">
                {['audio', 'video', 'image', 'document'].map(type => (
                  <label key={type} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filters.type.includes(type)}
                      onChange={() => toggleFilter('type', type)}
                      className="rounded border-gray-300 text-purple-600 shadow-sm focus:border-purple-300 focus:ring focus:ring-purple-200 focus:ring-opacity-50"
                    />
                    <span className="ml-2 text-sm text-gray-600 capitalize">{type}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Category Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
              <div className="space-y-2">
                {['Music', 'Education', 'Photography', 'Business', 'Art'].map(category => (
                  <label key={category} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filters.category.includes(category)}
                      onChange={() => toggleFilter('category', category)}
                      className="rounded border-gray-300 text-purple-600 shadow-sm focus:border-purple-300 focus:ring focus:ring-purple-200 focus:ring-opacity-50"
                    />
                    <span className="ml-2 text-sm text-gray-600">{category}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Protection Status</label>
              <div className="space-y-2">
                {['protected', 'processing', 'unprotected'].map(status => (
                  <label key={status} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filters.status.includes(status)}
                      onChange={() => toggleFilter('status', status)}
                      className="rounded border-gray-300 text-purple-600 shadow-sm focus:border-purple-300 focus:ring focus:ring-purple-200 focus:ring-opacity-50"
                    />
                    <span className="ml-2 text-sm text-gray-600 capitalize">{status}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Date Range Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
              <select
                value={filters.dateRange}
                onChange={(e) => toggleFilter('dateRange', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="all">All Time</option>
                <option value="week">Last Week</option>
                <option value="month">Last Month</option>
                <option value="year">Last Year</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Content Grid/List */}
      <div className="p-6">
        {filteredItems.length === 0 ? (
          <div className="text-center py-12">
            <PhotoIcon className="w-12 h-12 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600">No portfolio items found matching your criteria</p>
            <button className="mt-4 btn-primary">
              <PlusIcon className="w-4 h-4 mr-2" />
              Add Your First Content
            </button>
          </div>
        ) : (
          <div className={viewMode === 'grid' 
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6' 
            : 'space-y-4'
          }>
            {filteredItems.map((item) => {
              const TypeIcon = getTypeIcon(item.type);
              
              if (viewMode === 'list') {
                return (
                  <div key={item.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:shadow-md transition-shadow">
                    <div className="flex items-center space-x-4">
                      <div className="w-16 h-16 bg-gradient-to-br from-purple-100 to-blue-100 rounded-lg flex items-center justify-center">
                        <TypeIcon className="w-8 h-8 text-purple-500" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <h4 className="text-lg font-semibold text-gray-900 truncate">{item.title}</h4>
                          {item.featured && <StarIcon className="w-5 h-5 text-yellow-500" />}
                        </div>
                        <p className="text-sm text-gray-600 truncate">{item.description}</p>
                        <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                          <span className="flex items-center">
                            <EyeIcon className="w-4 h-4 mr-1" />
                            {item.stats.views.toLocaleString()}
                          </span>
                          <span className="flex items-center">
                            <HeartIcon className="w-4 h-4 mr-1" />
                            {item.stats.likes}
                          </span>
                          <span className="flex items-center">
                            <ShareIcon className="w-4 h-4 mr-1" />
                            {item.stats.shares}
                          </span>
                        </div>
                      </div>
                      <div className="flex flex-col items-end space-y-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(item.protection_status)}`}>
                          {item.protection_status}
                        </span>
                        <span className="text-xs text-gray-500">{formatFileSize(item.metadata.size)}</span>
                      </div>
                    </div>
                  </div>
                );
              }

              return (
                <div key={item.id} className="bg-gray-50 rounded-lg border border-gray-200 hover:shadow-lg transition-shadow overflow-hidden">
                  {/* Thumbnail */}
                  <div className="relative h-48 bg-gradient-to-br from-purple-100 to-blue-100">
                    <div className="absolute inset-0 flex items-center justify-center">
                      <TypeIcon className="w-12 h-12 text-purple-500" />
                    </div>
                    {item.featured && (
                      <div className="absolute top-2 right-2 p-1 bg-yellow-100 rounded-full">
                        <StarIcon className="w-4 h-4 text-yellow-500" />
                      </div>
                    )}
                    <div className="absolute top-2 left-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(item.protection_status)}`}>
                        {item.protection_status}
                      </span>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-4">
                    <h4 className="text-lg font-semibold text-gray-900 mb-2 truncate">{item.title}</h4>
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">{item.description}</p>
                    
                    {/* Tags */}
                    <div className="flex flex-wrap gap-1 mb-3">
                      {item.tags.slice(0, 3).map((tag, index) => (
                        <span key={index} className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs">
                          #{tag}
                        </span>
                      ))}
                      {item.tags.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs">
                          +{item.tags.length - 3}
                        </span>
                      )}
                    </div>

                    {/* Stats */}
                    <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                      <div className="flex items-center space-x-3">
                        <span className="flex items-center">
                          <EyeIcon className="w-4 h-4 mr-1" />
                          {item.stats.views.toLocaleString()}
                        </span>
                        <span className="flex items-center">
                          <HeartIcon className="w-4 h-4 mr-1" />
                          {item.stats.likes}
                        </span>
                      </div>
                      <span className="text-xs">{formatFileSize(item.metadata.size)}</span>
                    </div>

                    {/* Metadata */}
                    <div className="text-xs text-gray-500 space-y-1">
                      <div className="flex justify-between">
                        <span>Format:</span>
                        <span>{item.metadata.format}</span>
                      </div>
                      {item.metadata.duration && (
                        <div className="flex justify-between">
                          <span>Duration:</span>
                          <span>{Math.floor(item.metadata.duration / 60)}:{(item.metadata.duration % 60).toString().padStart(2, '0')}</span>
                        </div>
                      )}
                      {item.metadata.resolution && (
                        <div className="flex justify-between">
                          <span>Resolution:</span>
                          <span>{item.metadata.resolution}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Portfolio Stats */}
      <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>Showing {filteredItems.length} of {portfolioItems.length} items</span>
          <div className="flex items-center space-x-4">
            <span>Total Views: {portfolioItems.reduce((sum, item) => sum + item.stats.views, 0).toLocaleString()}</span>
            <span>Total Likes: {portfolioItems.reduce((sum, item) => sum + item.stats.likes, 0).toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
}