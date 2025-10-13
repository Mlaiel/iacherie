/**
 * CRAWLERS LIST COMPONENT
 * Display list/grid of crawlers with filters and pagination
 * Supports 3,231 crawlers across 31+ platforms
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import { useEffect, useState } from 'react';
import { CrawlerCard } from './CrawlerCard';
import { useCrawlersStore } from '@/lib/store/crawlers.store';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Search, Grid, List, RefreshCw } from 'lucide-react';

type ViewMode = 'grid' | 'list';

export function CrawlersList() {
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [searchTerm, setSearchTerm] = useState('');
  
  const {
    items: crawlers,
    loading,
    error,
    filters,
    total,
    fetchItems,
    setFilters,
  } = useCrawlersStore();

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const handleSearch = (value: string) => {
    setSearchTerm(value);
    setFilters({ search: value });
  };

  const handleStatusFilter = (status: string) => {
    setFilters({ status: status === 'all' ? undefined : status });
  };

  const handlePlatformFilter = (platform: string) => {
    setFilters({ category: platform === 'all' ? undefined : platform });
  };

  // Platforms (31+ available)
  const platforms = [
    'all',
    'youtube',
    'tiktok',
    'instagram',
    'facebook',
    'twitter',
    'linkedin',
    'pinterest',
    'reddit',
    'twitch',
    'discord',
    'telegram',
    'whatsapp',
    'snapchat',
    'wechat',
    'line',
    'viber',
    'spotify',
    'soundcloud',
    'apple-music',
    'amazon-music',
    'deezer',
    'tidal',
    'github',
    'gitlab',
    'bitbucket',
    'stackoverflow',
    'medium',
    'substack',
    'patreon',
    'onlyfans',
  ];

  const statuses = ['all', 'active', 'inactive', 'pending', 'error'];

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500 mb-4">Error: {error}</p>
        <Button onClick={() => fetchItems()}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters & Search */}
      <div className="flex flex-col lg:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            type="text"
            placeholder="Search crawlers..."
            value={searchTerm}
            onChange={(e) => handleSearch(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Platform Filter */}
        <Select
          value={filters.category || 'all'}
          onValueChange={handlePlatformFilter}
        >
          <SelectTrigger className="w-full lg:w-48">
            <SelectValue placeholder="Platform" />
          </SelectTrigger>
          <SelectContent>
            {platforms.map((platform) => (
              <SelectItem key={platform} value={platform}>
                {platform === 'all' ? 'All Platforms' : platform.charAt(0).toUpperCase() + platform.slice(1)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Status Filter */}
        <Select
          value={filters.status || 'all'}
          onValueChange={handleStatusFilter}
        >
          <SelectTrigger className="w-full lg:w-48">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            {statuses.map((status) => (
              <SelectItem key={status} value={status}>
                {status === 'all' ? 'All Statuses' : status.charAt(0).toUpperCase() + status.slice(1)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* View Mode Toggle */}
        <div className="flex gap-2">
          <Button
            variant={viewMode === 'grid' ? 'default' : 'outline'}
            size="icon"
            onClick={() => setViewMode('grid')}
          >
            <Grid className="w-4 h-4" />
          </Button>
          <Button
            variant={viewMode === 'list' ? 'default' : 'outline'}
            size="icon"
            onClick={() => setViewMode('list')}
          >
            <List className="w-4 h-4" />
          </Button>
        </div>

        {/* Refresh */}
        <Button
          variant="outline"
          size="icon"
          onClick={() => fetchItems()}
          disabled={loading}
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </Button>
      </div>

      {/* Stats */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-500">
          Showing {crawlers.length} of {total.toLocaleString()} crawlers
        </p>
        {filters.search && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleSearch('')}
          >
            Clear search
          </Button>
        )}
      </div>

      {/* Crawlers Grid/List */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="h-64 bg-gray-100 rounded-lg animate-pulse"
            />
          ))}
        </div>
      ) : crawlers.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">No crawlers found</p>
          <Button onClick={() => fetchItems()}>
            Refresh
          </Button>
        </div>
      ) : (
        <div
          className={
            viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4'
              : 'space-y-4'
          }
        >
          {crawlers.map((crawler) => (
            <CrawlerCard
              key={crawler.id}
              crawler={crawler}
              onStart={(id) => console.log('Start crawler:', id)}
              onPause={(id) => console.log('Pause crawler:', id)}
              onStop={(id) => console.log('Stop crawler:', id)}
              onConfigure={(id) => console.log('Configure crawler:', id)}
              onDelete={(id) => console.log('Delete crawler:', id)}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {!loading && crawlers.length > 0 && (
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            disabled={!filters.offset || filters.offset === 0}
            onClick={() =>
              setFilters({
                offset: Math.max(0, (filters.offset || 0) - (filters.limit || 50)),
              })
            }
          >
            Previous
          </Button>
          
          <p className="text-sm text-gray-500">
            Page {Math.floor((filters.offset || 0) / (filters.limit || 50)) + 1}
          </p>
          
          <Button
            variant="outline"
            disabled={crawlers.length < (filters.limit || 50)}
            onClick={() =>
              setFilters({
                offset: (filters.offset || 0) + (filters.limit || 50),
              })
            }
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
