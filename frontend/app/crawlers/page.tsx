/**
 * CRAWLERS DASHBOARD PAGE
 * Complete dashboard for managing crawlers with REAL backend connection
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Bug, Plus, RefreshCw } from 'lucide-react';
import { StatusMonitor } from './components/StatusMonitor';
import { CrawlersList } from './components/CrawlersList';
import { Button } from '@/components/ui/button';
import { useCrawlersStore } from '@/lib/store/crawlers.store';

export default function CrawlersPage() {
  const { fetchItems, loading, total } = useCrawlersStore();

  useEffect(() => {
    // Fetch crawlers on mount
    fetchItems();
  }, [fetchItems]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-yellow-50">
      <div className="bg-white shadow-md border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-600 hover:text-orange-600 transition">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <Bug className="h-8 w-8 text-orange-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Crawlers Dashboard</h1>
                <p className="text-sm text-gray-500">
                  {loading ? 'Loading...' : `${total} crawlers available`}
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => fetchItems()}
                disabled={loading}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button className="bg-orange-600 hover:bg-orange-700">
                <Plus className="w-4 h-4 mr-2" />
                New Crawler
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="space-y-8">
          <StatusMonitor />
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">All Crawlers</h2>
            <CrawlersList />
          </div>
        </div>
      </div>
    </div>
  );
}
