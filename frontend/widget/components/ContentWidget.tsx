/**
 * Content Widget - Embeddable Content Preview Component
 * 
 * Displays content preview and basic information in embeddable format
 * Can showcase featured content on external websites
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  PlayIcon, 
  EyeIcon, 
  HeartIcon,
  ShareIcon
} from '@heroicons/react/24/outline';

interface ContentWidgetProps {
  apiKey: string;
  userId: string;
  showTitle?: boolean;
  data?: any;
}

interface ContentData {
  id: string;
  title: string;
  description: string;
  thumbnail: string;
  duration: string;
  views: number;
  likes: number;
  shares: number;
  category: string;
  createdAt: string;
}

export function ContentWidget({ apiKey, userId, showTitle = true, data }: ContentWidgetProps) {
  const [content, setContent] = useState<ContentData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchContent = async () => {
      try {
        if (data) {
          setContent(data);
          setIsLoading(false);
          return;
        }

        if (!apiKey || !userId) {
          throw new Error('API Key et User ID requis');
        }

        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock data
        setContent({
          id: '1',
          title: 'Ma dernière création musicale',
          description: 'Découvrez mon nouveau titre avec des sonorités uniques et des paroles inspirantes.',
          thumbnail: 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400&h=300&fit=crop',
          duration: '3:45',
          views: 15420,
          likes: 892,
          shares: 156,
          category: 'Musique',
          createdAt: new Date(Date.now() - 86400000).toISOString()
        });
        
        setIsLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erreur de chargement');
        setIsLoading(false);
      }
    };

    fetchContent();
  }, [apiKey, userId, data]);

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-sm text-gray-600">Chargement...</span>
        </div>
      </div>
    );
  }

  if (error || !content) {
    return (
      <div className="p-6 text-center">
        <div className="text-red-500 text-sm">
          <PlayIcon className="h-8 w-8 mx-auto mb-2 opacity-50" />
          {error || 'Aucun contenu trouvé'}
        </div>
      </div>
    );
  }

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Aujourd\'hui';
    if (diffDays === 1) return 'Hier';
    if (diffDays < 7) return `Il y a ${diffDays} jours`;
    return date.toLocaleDateString('fr-FR');
  };

  return (
    <div className="overflow-hidden">
      {showTitle && (
        <div className="flex items-center space-x-2 p-4 pb-2">
          <PlayIcon className="h-5 w-5 text-purple-600" />
          <h3 className="font-semibold text-gray-900">Contenu en vedette</h3>
        </div>
      )}

      {/* Thumbnail */}
      <div className="relative">
        <img 
          src={content.thumbnail} 
          alt={content.title}
          className="w-full h-48 object-cover"
        />
        
        {/* Play Button Overlay */}
        <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center">
          <button className="w-16 h-16 bg-white bg-opacity-90 rounded-full flex items-center justify-center hover:bg-opacity-100 transition-opacity">
            <PlayIcon className="h-8 w-8 text-gray-800 ml-1" />
          </button>
        </div>

        {/* Duration Badge */}
        <div className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded">
          {content.duration}
        </div>

        {/* Category Badge */}
        <div className="absolute top-2 left-2 bg-purple-600 text-white text-xs px-2 py-1 rounded">
          {content.category}
        </div>
      </div>

      {/* Content Info */}
      <div className="p-4">
        <h4 className="font-semibold text-gray-900 mb-2 line-clamp-2">
          {content.title}
        </h4>
        
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {content.description}
        </p>

        {/* Stats */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <EyeIcon className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">{formatNumber(content.views)}</span>
            </div>
            
            <div className="flex items-center space-x-1">
              <HeartIcon className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">{formatNumber(content.likes)}</span>
            </div>
            
            <div className="flex items-center space-x-1">
              <ShareIcon className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">{formatNumber(content.shares)}</span>
            </div>
          </div>
          
          <span className="text-xs text-gray-500">
            {formatDate(content.createdAt)}
          </span>
        </div>

        {/* Action Button */}
        <button className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:opacity-90 transition-opacity">
          Voir le contenu complet
        </button>

        {/* Powered by Ainflue */}
        <div className="text-xs text-gray-400 text-center mt-3 pt-3 border-t border-gray-100">
          <span>Powered by </span>
          <a 
            href="https://ainflue.com" 
            target="_blank" 
            rel="noopener noreferrer" 
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            Ainflue
          </a>
        </div>
      </div>
    </div>
  );
}

// CSS for line-clamp utility
export const contentWidgetStyles = `
  .line-clamp-2 {
    overflow: hidden;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
  }
`;