/**
 * CRAWLER CARD COMPONENT
 * Individual crawler card with status, actions, and real-time updates
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Play, 
  Pause, 
  StopCircle, 
  Settings, 
  Trash2, 
  Activity,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle
} from 'lucide-react';
import type { Crawler } from '@/lib/store/generated';

interface CrawlerCardProps {
  crawler: Crawler;
  onStart?: (id: string) => void;
  onPause?: (id: string) => void;
  onStop?: (id: string) => void;
  onConfigure?: (id: string) => void;
  onDelete?: (id: string) => void;
}

export function CrawlerCard({
  crawler,
  onStart,
  onPause,
  onStop,
  onConfigure,
  onDelete
}: CrawlerCardProps) {
  const [isLoading, setIsLoading] = useState(false);

  const getStatusIcon = () => {
    switch (crawler.status) {
      case 'active':
        return <Activity className="w-4 h-4 text-green-500 animate-pulse" />;
      case 'inactive':
        return <StopCircle className="w-4 h-4 text-gray-400" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (crawler.status) {
      case 'active':
        return 'bg-green-500/10 text-green-500 border-green-500/20';
      case 'inactive':
        return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
      case 'pending':
        return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
      case 'error':
        return 'bg-red-500/10 text-red-500 border-red-500/20';
      default:
        return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
    }
  };

  const handleAction = async (action: () => void) => {
    setIsLoading(true);
    try {
      await action();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="p-4 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-start gap-3">
          <div className="mt-1">
            {getStatusIcon()}
          </div>
          <div>
            <h3 className="font-semibold text-lg">{crawler.name}</h3>
            <p className="text-sm text-gray-500">ID: {crawler.id}</p>
          </div>
        </div>
        
        <Badge className={getStatusColor()}>
          {crawler.status}
        </Badge>
      </div>

      {/* Crawler Info */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">Platform</span>
          <span className="font-medium">{crawler.platform || 'N/A'}</span>
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">Type</span>
          <span className="font-medium">{crawler.type || 'General'}</span>
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">Last Run</span>
          <span className="font-medium">
            {crawler.last_run ? new Date(crawler.last_run).toLocaleString() : 'Never'}
          </span>
        </div>
        
        {crawler.items_crawled !== undefined && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-500">Items Crawled</span>
            <span className="font-medium">{crawler.items_crawled.toLocaleString()}</span>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        {crawler.status === 'inactive' && (
          <Button
            size="sm"
            variant="default"
            className="flex-1"
            disabled={isLoading}
            onClick={() => onStart && handleAction(() => onStart(crawler.id))}
          >
            <Play className="w-4 h-4 mr-1" />
            Start
          </Button>
        )}
        
        {crawler.status === 'active' && (
          <>
            <Button
              size="sm"
              variant="outline"
              className="flex-1"
              disabled={isLoading}
              onClick={() => onPause && handleAction(() => onPause(crawler.id))}
            >
              <Pause className="w-4 h-4 mr-1" />
              Pause
            </Button>
            
            <Button
              size="sm"
              variant="outline"
              disabled={isLoading}
              onClick={() => onStop && handleAction(() => onStop(crawler.id))}
            >
              <StopCircle className="w-4 h-4" />
            </Button>
          </>
        )}
        
        <Button
          size="sm"
          variant="outline"
          disabled={isLoading}
          onClick={() => onConfigure && onConfigure(crawler.id)}
        >
          <Settings className="w-4 h-4" />
        </Button>
        
        <Button
          size="sm"
          variant="outline"
          className="text-red-500 hover:bg-red-500/10"
          disabled={isLoading}
          onClick={() => onDelete && handleAction(() => onDelete(crawler.id))}
        >
          <Trash2 className="w-4 h-4" />
        </Button>
      </div>

      {/* Progress Bar (if active) */}
      {crawler.status === 'active' && crawler.progress !== undefined && (
        <div className="mt-4">
          <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
            <span>Progress</span>
            <span>{crawler.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${crawler.progress}%` }}
            />
          </div>
        </div>
      )}
    </Card>
  );
}
