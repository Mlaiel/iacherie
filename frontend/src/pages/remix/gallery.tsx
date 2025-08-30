/**
 * Remix Gallery Page - Ultra-Advanced Enterprise Content Discovery Platform
 * 
 * This page provides an advanced gallery interface for discovering,
 * filtering, and showcasing community remixes and AI-generated content.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️  CRITICAL LEGAL NOTICE:
 * This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
 * Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
 * Contact: mlaiel@live.de for licensing inquiries.
 * 
 * 🏆 Expert Development Team Specialties:
 * - Lead AI Developer: Advanced machine learning and AI systems
 * - Backend Senior Engineer: Enterprise Python/FastAPI architecture
 * - ML Engineer: TensorFlow/PyTorch and neural networks
 * - Database Administrator: PostgreSQL and vector databases
 * - Security Specialist: Enterprise security protocols
 * - Microservices Architect: Scalable distributed systems
 * - Audio Engineer: Professional audio processing
 * - DevOps Engineer: CI/CD and cloud infrastructure
 * - AI Prompt Engineer: Advanced prompt engineering
 */

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import studioStyles from '@/components/remix_studio/remix_studio.styles';
import { 
  PlayIcon,
  PauseIcon,
  HeartIcon,
  ShareIcon,
  DownloadIcon,
  EyeIcon,
  ChatBubbleLeftIcon,
  StarIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  Squares2X2Icon,
  ListBulletIcon,
  ClockIcon,
  MusicalNoteIcon,
  TrophyIcon,
  SparklesIcon,
  ArrowLeftIcon,
  AdjustmentsHorizontalIcon,
  UserIcon,
  CalendarIcon,
  TagIcon,
  FireIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartIconSolid } from '@heroicons/react/24/solid';
import clsx from 'clsx';

interface GalleryPageProps {
  params?: { [key: string]: string };
}

interface RemixItem {
  id: string;
  title: string;
  description: string;
  artist: {
    id: string;
    name: string;
    username: string;
    avatar: string;
    verified: boolean;
    followers: number;
  };
  thumbnail: string;
  waveform: number[];
  duration: number;
  bpm: number;
  key: string;
  genre: string;
  tags: string[];
  createdAt: Date;
  plays: number;
  likes: number;
  comments: number;
  downloads: number;
  isLiked: boolean;
  isPremium: boolean;
  isAIGenerated: boolean;
  originalTrack?: {
    title: string;
    artist: string;
  };
  collaborators?: string[];
  license: 'free' | 'premium' | 'exclusive';
  price?: number;
  rating: number;
}

interface FilterOptions {
  genre: string;
  duration: string;
  license: string;
  sortBy: string;
  dateRange: string;
  aiGenerated: boolean | null;
  hasCollaborators: boolean | null;
}

const GalleryPage: React.FC<GalleryPageProps> = ({ params }) => {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('trending');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [isPlaying, setIsPlaying] = useState<string | null>(null);
  const [remixItems, setRemixItems] = useState<RemixItem[]>([]);
  const [filteredItems, setFilteredItems] = useState<RemixItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const [filters, setFilters] = useState<FilterOptions>({
    genre: 'all',
    duration: 'all',
    license: 'all',
    sortBy: 'trending',
    dateRange: 'all',
    aiGenerated: null,
    hasCollaborators: null
  });

  const tabs = [
    { id: 'trending', label: 'Trending', description: 'Most popular remixes this week', icon: FireIcon },
    { id: 'featured', label: 'Featured', description: 'Curated and highlighted content', icon: StarIcon },
    { id: 'recent', label: 'Recent', description: 'Latest uploads and creations', icon: ClockIcon },
    { id: 'ai-generated', label: 'AI Generated', description: 'AI-powered remixes and creations', icon: SparklesIcon },
    { id: 'competitions', label: 'Competitions', description: 'Contest entries and winners', icon: TrophyIcon }
  ];

  const genres = [
    'all', 'Electronic', 'Hip-Hop', 'Pop', 'Rock', 'Jazz', 'Classical',
    'Ambient', 'House', 'Techno', 'Dubstep', 'Trap', 'R&B', 'Country'
  ];

  const sortOptions = [
    { value: 'trending', label: 'Trending' },
    { value: 'newest', label: 'Newest First' },
    { value: 'oldest', label: 'Oldest First' },
    { value: 'most-liked', label: 'Most Liked' },
    { value: 'most-played', label: 'Most Played' },
    { value: 'highest-rated', label: 'Highest Rated' }
  ];

  useEffect(() => {
    loadRemixItems();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [remixItems, filters, searchQuery]);

  const loadRemixItems = async () => {
    try {
      setIsLoading(true);
      await new Promise(resolve => setTimeout(resolve, 1000));

      const mockItems: RemixItem[] = [
        {
          id: 'remix-1',
          title: 'Sunset Dreams (AI Remix)',
          description: 'AI-generated tropical house remix with ethereal vocals and sunset vibes',
          artist: {
            id: 'artist-1',
            name: 'AI Creator',
            username: 'ai_beats',
            avatar: '/avatars/ai-creator.jpg',
            verified: true,
            followers: 45000
          },
          thumbnail: '/remixes/sunset-dreams.jpg',
          waveform: Array.from({ length: 100 }, () => Math.random()),
          duration: 245,
          bpm: 124,
          key: 'Am',
          genre: 'Electronic',
          tags: ['tropical', 'house', 'ai', 'chill', 'sunset'],
          createdAt: new Date(Date.now() - 3600000),
          plays: 12450,
          likes: 892,
          comments: 156,
          downloads: 234,
          isLiked: false,
          isPremium: false,
          isAIGenerated: true,
          originalTrack: {
            title: 'Summer Nights',
            artist: 'Original Artist'
          },
          license: 'free',
          rating: 4.8
        },
        {
          id: 'remix-2',
          title: 'Urban Symphony Collab',
          description: 'Hip-hop meets orchestral in this groundbreaking collaboration between MC Flow and Jazz Ensemble',
          artist: {
            id: 'artist-2',
            name: 'MC Flow',
            username: 'mc_flow_official',
            avatar: '/avatars/mc-flow.jpg',
            verified: true,
            followers: 128000
          },
          thumbnail: '/remixes/urban-symphony.jpg',
          waveform: Array.from({ length: 100 }, () => Math.random()),
          duration: 198,
          bpm: 95,
          key: 'Dm',
          genre: 'Hip-Hop',
          tags: ['hip-hop', 'orchestral', 'collaboration', 'urban', 'symphony'],
          createdAt: new Date(Date.now() - 7200000),
          plays: 28750,
          likes: 2156,
          comments: 389,
          downloads: 567,
          isLiked: true,
          isPremium: true,
          isAIGenerated: false,
          collaborators: ['Jazz Ensemble', 'String Section'],
          license: 'premium',
          price: 4.99,
          rating: 4.9
        },
        {
          id: 'remix-3',
          title: 'Ambient Meditation Flow',
          description: 'Peaceful ambient soundscape designed for deep meditation and relaxation',
          artist: {
            id: 'artist-3',
            name: 'Zen Producer',
            username: 'zen_sounds',
            avatar: '/avatars/zen-producer.jpg',
            verified: false,
            followers: 15600
          },
          thumbnail: '/remixes/ambient-meditation.jpg',
          waveform: Array.from({ length: 100 }, () => Math.random() * 0.6),
          duration: 1800, // 30 minutes
          bpm: 60,
          key: 'C',
          genre: 'Ambient',
          tags: ['ambient', 'meditation', 'relaxation', 'nature', 'zen'],
          createdAt: new Date(Date.now() - 86400000),
          plays: 8950,
          likes: 445,
          comments: 67,
          downloads: 189,
          isLiked: false,
          isPremium: false,
          isAIGenerated: false,
          license: 'free',
          rating: 4.7
        },
        {
          id: 'remix-4',
          title: 'Retro Synthwave Fusion',
          description: 'AI-enhanced 80s synthwave with modern production techniques',
          artist: {
            id: 'artist-4',
            name: 'Neon Dreams',
            username: 'neon_dreams_80s',
            avatar: '/avatars/neon-dreams.jpg',
            verified: true,
            followers: 67800
          },
          thumbnail: '/remixes/retro-synthwave.jpg',
          waveform: Array.from({ length: 100 }, () => Math.random()),
          duration: 312,
          bpm: 128,
          key: 'Em',
          genre: 'Electronic',
          tags: ['synthwave', 'retro', '80s', 'neon', 'cyberpunk'],
          createdAt: new Date(Date.now() - 172800000),
          plays: 19650,
          likes: 1234,
          comments: 234,
          downloads: 345,
          isLiked: true,
          isPremium: false,
          isAIGenerated: true,
          license: 'free',
          rating: 4.6
        },
        {
          id: 'remix-5',
          title: 'Jazz Fusion Experiment',
          description: 'Modern jazz fusion with electronic elements and live instrumentation',
          artist: {
            id: 'artist-5',
            name: 'Jazz Collective',
            username: 'jazz_collective',
            avatar: '/avatars/jazz-collective.jpg',
            verified: true,
            followers: 34500
          },
          thumbnail: '/remixes/jazz-fusion.jpg',
          waveform: Array.from({ length: 100 }, () => Math.random()),
          duration: 267,
          bpm: 110,
          key: 'Bb',
          genre: 'Jazz',
          tags: ['jazz', 'fusion', 'experimental', 'live', 'improvisation'],
          createdAt: new Date(Date.now() - 259200000),
          plays: 7890,
          likes: 567,
          comments: 89,
          downloads: 123,
          isLiked: false,
          isPremium: true,
          isAIGenerated: false,
          collaborators: ['Live Band', 'Studio Musicians'],
          license: 'premium',
          price: 7.99,
          rating: 4.8
        }
      ];

      setRemixItems(mockItems);
    } catch (error) {
      console.error('Failed to load remix items:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const applyFilters = useCallback(() => {
    let filtered = [...remixItems];

    // Text search
    if (searchQuery) {
      filtered = filtered.filter(item =>
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.artist.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // Genre filter
    if (filters.genre !== 'all') {
      filtered = filtered.filter(item => item.genre === filters.genre);
    }

    // License filter
    if (filters.license !== 'all') {
      filtered = filtered.filter(item => item.license === filters.license);
    }

    // AI Generated filter
    if (filters.aiGenerated !== null) {
      filtered = filtered.filter(item => item.isAIGenerated === filters.aiGenerated);
    }

    // Collaborators filter
    if (filters.hasCollaborators !== null) {
      filtered = filtered.filter(item => 
        filters.hasCollaborators ? (item.collaborators && item.collaborators.length > 0) : !item.collaborators
      );
    }

    // Sort
    switch (filters.sortBy) {
      case 'newest':
        filtered.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
        break;
      case 'oldest':
        filtered.sort((a, b) => a.createdAt.getTime() - b.createdAt.getTime());
        break;
      case 'most-liked':
        filtered.sort((a, b) => b.likes - a.likes);
        break;
      case 'most-played':
        filtered.sort((a, b) => b.plays - a.plays);
        break;
      case 'highest-rated':
        filtered.sort((a, b) => b.rating - a.rating);
        break;
      default: // trending
        filtered.sort((a, b) => (b.plays + b.likes * 10) - (a.plays + a.likes * 10));
    }

    setFilteredItems(filtered);
  }, [remixItems, filters, searchQuery]);

  const handlePlay = (itemId: string) => {
    setIsPlaying(isPlaying === itemId ? null : itemId);
  };

  const handleLike = async (itemId: string) => {
    try {
      setRemixItems(prev => prev.map(item =>
        item.id === itemId
          ? { 
              ...item, 
              isLiked: !item.isLiked, 
              likes: item.isLiked ? item.likes - 1 : item.likes + 1 
            }
          : item
      ));
    } catch (error) {
      console.error('Failed to toggle like:', error);
    }
  };

  const handleDownload = async (itemId: string) => {
    try {
      const item = remixItems.find(i => i.id === itemId);
      if (item?.isPremium && !item.license) {
        // Handle premium purchase flow
        console.log('Purchase required for premium track');
        return;
      }
      console.log('Downloading track:', itemId);
    } catch (error) {
      console.error('Failed to download track:', error);
    }
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    return `${minutes}:${String(secs).padStart(2, '0')}`;
  };

  const renderRemixCard = (item: RemixItem) => (
    <div key={item.id} className={clsx(
      studioStyles.container.card,
      "overflow-hidden transition-all duration-200 hover:scale-105 hover:shadow-lg group"
    )}>
      {/* Thumbnail and Play Button */}
      <div className="relative aspect-square bg-gradient-to-br from-purple-500 to-blue-500 overflow-hidden">
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-200 flex items-center justify-center">
          <button
            onClick={() => handlePlay(item.id)}
            className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-4 bg-white bg-opacity-20 rounded-full backdrop-blur-sm"
          >
            {isPlaying === item.id ? (
              <PauseIcon className="h-8 w-8 text-white" />
            ) : (
              <PlayIcon className="h-8 w-8 text-white" />
            )}
          </button>
        </div>
        
        {/* Badges */}
        <div className="absolute top-3 left-3 flex flex-wrap gap-1">
          {item.isAIGenerated && (
            <span className="px-2 py-1 text-xs font-medium bg-purple-600 text-white rounded-full">
              AI
            </span>
          )}
          {item.isPremium && (
            <span className="px-2 py-1 text-xs font-medium bg-yellow-600 text-white rounded-full">
              Premium
            </span>
          )}
          {item.collaborators && (
            <span className="px-2 py-1 text-xs font-medium bg-blue-600 text-white rounded-full">
              Collab
            </span>
          )}
        </div>
        
        {/* Duration */}
        <div className="absolute bottom-3 right-3">
          <span className="px-2 py-1 text-xs font-medium bg-black bg-opacity-50 text-white rounded">
            {formatDuration(item.duration)}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Title and Artist */}
        <div className="mb-3">
          <h3 className="font-semibold text-slate-900 dark:text-white mb-1 line-clamp-1 group-hover:text-purple-600 transition-colors">
            {item.title}
          </h3>
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-green-500 to-teal-500 flex items-center justify-center text-xs font-medium text-white">
              {item.artist.name.split(' ').map(n => n[0]).join('')}
            </div>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {item.artist.name}
              {item.artist.verified && (
                <span className="ml-1 text-blue-500">✓</span>
              )}
            </p>
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1 mb-3">
          {item.tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className="px-2 py-1 text-xs bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 rounded"
            >
              #{tag}
            </span>
          ))}
        </div>

        {/* Stats */}
        <div className="flex items-center justify-between text-sm text-slate-500 dark:text-slate-400 mb-3">
          <div className="flex items-center space-x-3">
            <span className="flex items-center space-x-1">
              <PlayIcon className="h-3 w-3" />
              <span>{item.plays.toLocaleString()}</span>
            </span>
            <span className="flex items-center space-x-1">
              <HeartIcon className="h-3 w-3" />
              <span>{item.likes.toLocaleString()}</span>
            </span>
          </div>
          <div className="flex items-center space-x-1">
            <StarIcon className="h-3 w-3 text-yellow-500" />
            <span>{item.rating}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleLike(item.id)}
              className={clsx(
                "p-2 rounded-lg transition-colors",
                item.isLiked
                  ? "text-red-500 bg-red-50 dark:bg-red-900/20"
                  : "text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20"
              )}
            >
              {item.isLiked ? (
                <HeartIconSolid className="h-4 w-4" />
              ) : (
                <HeartIcon className="h-4 w-4" />
              )}
            </button>
            <button className="p-2 text-slate-400 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors">
              <ShareIcon className="h-4 w-4" />
            </button>
            <button className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 rounded-lg transition-colors">
              <ChatBubbleLeftIcon className="h-4 w-4" />
            </button>
          </div>
          <button
            onClick={() => handleDownload(item.id)}
            className={clsx(
              "px-3 py-1 text-xs font-medium rounded-lg transition-colors",
              item.license === 'free'
                ? "bg-green-600 text-white hover:bg-green-700"
                : "bg-purple-600 text-white hover:bg-purple-700"
            )}
          >
            {item.license === 'free' ? 'Free' : `$${item.price}`}
          </button>
        </div>
      </div>
    </div>
  );

  const renderListView = (item: RemixItem) => (
    <div key={item.id} className={clsx(
      studioStyles.container.card,
      "p-4 flex items-center space-x-4 hover:shadow-lg transition-all duration-200"
    )}>
      {/* Thumbnail */}
      <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center relative group cursor-pointer">
        <button onClick={() => handlePlay(item.id)}>
          {isPlaying === item.id ? (
            <PauseIcon className="h-6 w-6 text-white" />
          ) : (
            <PlayIcon className="h-6 w-6 text-white" />
          )}
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-slate-900 dark:text-white truncate">
              {item.title}
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400 truncate">
              {item.artist.name}
            </p>
            <div className="flex items-center space-x-2 mt-1">
              <span className="text-xs text-slate-500">{item.genre}</span>
              <span className="text-xs text-slate-500">•</span>
              <span className="text-xs text-slate-500">{formatDuration(item.duration)}</span>
              <span className="text-xs text-slate-500">•</span>
              <span className="text-xs text-slate-500">{item.bpm} BPM</span>
            </div>
          </div>

          {/* Stats and Actions */}
          <div className="flex items-center space-x-4 ml-4">
            <div className="flex items-center space-x-3 text-sm text-slate-500">
              <span className="flex items-center space-x-1">
                <PlayIcon className="h-3 w-3" />
                <span>{item.plays.toLocaleString()}</span>
              </span>
              <span className="flex items-center space-x-1">
                <HeartIcon className="h-3 w-3" />
                <span>{item.likes.toLocaleString()}</span>
              </span>
            </div>
            
            <div className="flex items-center space-x-1">
              <button
                onClick={() => handleLike(item.id)}
                className={clsx(
                  "p-1 rounded transition-colors",
                  item.isLiked ? "text-red-500" : "text-slate-400 hover:text-red-500"
                )}
              >
                {item.isLiked ? (
                  <HeartIconSolid className="h-4 w-4" />
                ) : (
                  <HeartIcon className="h-4 w-4" />
                )}
              </button>
              <button className="p-1 text-slate-400 hover:text-blue-500 rounded transition-colors">
                <ShareIcon className="h-4 w-4" />
              </button>
              <button
                onClick={() => handleDownload(item.id)}
                className="p-1 text-slate-400 hover:text-green-500 rounded transition-colors"
              >
                <DownloadIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
        <div className="px-6 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/remix')}
                className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
              >
                <ArrowLeftIcon className="h-5 w-5" />
              </button>
              <div>
                <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                  Remix Gallery
                </h1>
                <p className="text-slate-600 dark:text-slate-400 mt-2">
                  Discover amazing remixes and AI-generated content from creators worldwide
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* View Mode Toggle */}
              <div className="flex bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={clsx(
                    "p-2 rounded-md transition-colors",
                    viewMode === 'grid'
                      ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm"
                      : "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
                  )}
                >
                  <Squares2X2Icon className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={clsx(
                    "p-2 rounded-md transition-colors",
                    viewMode === 'list'
                      ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm"
                      : "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
                  )}
                >
                  <ListBulletIcon className="h-4 w-4" />
                </button>
              </div>

              <button
                onClick={() => setShowFilters(!showFilters)}
                className={clsx(
                  "px-4 py-2 rounded-lg border transition-colors",
                  showFilters
                    ? "bg-purple-50 border-purple-200 text-purple-700 dark:bg-purple-900/20 dark:border-purple-700 dark:text-purple-400"
                    : "border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800"
                )}
              >
                <FunnelIcon className="h-4 w-4 mr-2" />
                Filters
              </button>
            </div>
          </div>

          {/* Search Bar */}
          <div className="mt-6">
            <div className="relative max-w-md">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search remixes, artists, genres..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              />
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="px-6">
          <div className="flex space-x-8 border-b border-slate-200 dark:border-slate-700">
            {tabs.map((tab) => {
              const IconComponent = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={clsx(
                    "pb-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 flex items-center space-x-2",
                    activeTab === tab.id
                      ? "border-purple-500 text-purple-600 dark:text-purple-400"
                      : "border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
                  )}
                >
                  <IconComponent className="h-4 w-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="px-6 py-4 bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Genre
                </label>
                <select
                  value={filters.genre}
                  onChange={(e) => setFilters(prev => ({ ...prev, genre: e.target.value }))}
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                >
                  {genres.map((genre) => (
                    <option key={genre} value={genre}>
                      {genre === 'all' ? 'All Genres' : genre}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  License
                </label>
                <select
                  value={filters.license}
                  onChange={(e) => setFilters(prev => ({ ...prev, license: e.target.value }))}
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="all">All Licenses</option>
                  <option value="free">Free</option>
                  <option value="premium">Premium</option>
                  <option value="exclusive">Exclusive</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Sort By
                </label>
                <select
                  value={filters.sortBy}
                  onChange={(e) => setFilters(prev => ({ ...prev, sortBy: e.target.value }))}
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                >
                  {sortOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  AI Generated
                </label>
                <select
                  value={filters.aiGenerated === null ? 'all' : filters.aiGenerated.toString()}
                  onChange={(e) => setFilters(prev => ({ 
                    ...prev, 
                    aiGenerated: e.target.value === 'all' ? null : e.target.value === 'true' 
                  }))}
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="all">All Content</option>
                  <option value="true">AI Generated</option>
                  <option value="false">Human Created</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Collaborations
                </label>
                <select
                  value={filters.hasCollaborators === null ? 'all' : filters.hasCollaborators.toString()}
                  onChange={(e) => setFilters(prev => ({ 
                    ...prev, 
                    hasCollaborators: e.target.value === 'all' ? null : e.target.value === 'true' 
                  }))}
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="all">All Projects</option>
                  <option value="true">Collaborations</option>
                  <option value="false">Solo Projects</option>
                </select>
              </div>

              <div className="flex items-end">
                <button
                  onClick={() => setFilters({
                    genre: 'all',
                    duration: 'all',
                    license: 'all',
                    sortBy: 'trending',
                    dateRange: 'all',
                    aiGenerated: null,
                    hasCollaborators: null
                  })}
                  className="w-full px-3 py-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="px-6 py-8">
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {Array.from({ length: 8 }).map((_, index) => (
              <div key={index} className="animate-pulse">
                <div className="aspect-square bg-slate-200 dark:bg-slate-800 rounded-lg mb-3"></div>
                <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded mb-2"></div>
                <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-2/3"></div>
              </div>
            ))}
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="text-center py-12">
            <MusicalNoteIcon className="h-12 w-12 text-slate-400 mx-auto mb-4" />
            <p className="text-lg text-slate-600 dark:text-slate-400">No remixes found</p>
            <p className="text-sm text-slate-500 dark:text-slate-500 mt-2">
              Try adjusting your search or filters
            </p>
          </div>
        ) : (
          <div>
            {/* Results Summary */}
            <div className="flex items-center justify-between mb-6">
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Showing {filteredItems.length} remix{filteredItems.length !== 1 ? 'es' : ''}
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-500">
                {tabs.find(tab => tab.id === activeTab)?.description}
              </p>
            </div>

            {/* Content Grid/List */}
            {viewMode === 'grid' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {filteredItems.map(renderRemixCard)}
              </div>
            ) : (
              <div className="space-y-4">
                {filteredItems.map(renderListView)}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default GalleryPage;