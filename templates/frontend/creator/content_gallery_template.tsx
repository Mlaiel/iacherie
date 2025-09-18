/**
 * @fileoverview Enterprise Content Gallery Template with AI Categorization
 * @version 1.0.0
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - All Rights Reserved
 * @license Proprietary - Unauthorized use prohibited
 * 
 * 🚨 INTELLECTUAL PROPERTY WARNING:
 * This code is the exclusive property of Fahed Mlaiel.
 * Unauthorized copying, modification, distribution, or commercial use
 * without explicit written permission is strictly prohibited.
 * Violation will result in immediate legal action.
 */

import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import styled, { keyframes, ThemeProvider } from 'styled-components';

// ==================== INTERFACES & TYPES ====================

interface ContentItem {
  id: string;
  title: string;
  description: string;
  type: 'audio' | 'video' | 'image' | 'document' | 'live_stream' | 'podcast';
  url: string;
  thumbnailUrl: string;
  duration?: number; // in seconds for audio/video
  fileSize: number; // in bytes
  format: string;
  createdAt: Date;
  updatedAt: Date;
  status: 'draft' | 'published' | 'private' | 'archived' | 'processing';
  visibility: 'public' | 'private' | 'unlisted' | 'premium';
  tags: string[];
  aiCategories: string[]; // AI-generated categories
  aiSentiment: 'positive' | 'neutral' | 'negative';
  aiContentScore: number; // 0-100 quality score
  performance: {
    views: number;
    likes: number;
    shares: number;
    comments: number;
    revenue: number;
    engagementRate: number;
  };
  metadata: {
    bitrate?: number;
    resolution?: string;
    fps?: number;
    channels?: number;
    colorSpace?: string;
    codec?: string;
  };
  collaborators?: string[];
  monetization: {
    isMonetized: boolean;
    price?: number;
    currency?: string;
    salesCount?: number;
  };
}

interface FilterOptions {
  type: string[];
  status: string[];
  visibility: string[];
  dateRange: {
    start?: Date;
    end?: Date;
  };
  aiCategories: string[];
  performanceRange: {
    minViews?: number;
    maxViews?: number;
    minEngagement?: number;
    maxEngagement?: number;
  };
  monetization: 'all' | 'monetized' | 'free';
}

interface SortOptions {
  field: 'createdAt' | 'updatedAt' | 'views' | 'likes' | 'revenue' | 'aiContentScore';
  direction: 'asc' | 'desc';
}

interface ContentGalleryProps {
  creatorId: string;
  className?: string;
  theme?: 'light' | 'dark' | 'auto';
  viewMode?: 'grid' | 'list' | 'masonry';
  enableBulkActions?: boolean;
  enableAIInsights?: boolean;
  onContentSelect?: (content: ContentItem) => void;
  onContentEdit?: (content: ContentItem) => void;
  onContentDelete?: (contentIds: string[]) => void;
  onBulkAction?: (action: string, contentIds: string[]) => void;
}

// ==================== STYLED COMPONENTS ====================

const fadeInUp = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;

const shimmer = keyframes`
  0% { background-position: -200px 0; }
  100% { background-position: calc(200px + 100%) 0; }
`;

const scaleIn = keyframes`
  from { transform: scale(0.9); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
`;

const GalleryContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  background: ${props => props.theme.colors.background};
  min-height: 100vh;
  animation: ${fadeInUp} 0.6s ease-out;
`;

const GalleryHeader = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  
  @media (min-width: 768px) {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
`;

const HeaderTitle = styled.h1`
  margin: 0;
  font-size: 32px;
  font-weight: 800;
  color: ${props => props.theme.colors.text};
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const StatsBar = styled.div`
  display: flex;
  gap: 24px;
  align-items: center;
  flex-wrap: wrap;
`;

const StatItem = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
`;

const StatValue = styled.div`
  font-size: 24px;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
`;

const StatLabel = styled.div`
  font-size: 12px;
  font-weight: 500;
  color: ${props => props.theme.colors.textSecondary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const FilterControls = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 20px;
  background: ${props => props.theme.colors.cardBackground};
  border-radius: 16px;
  border: 1px solid ${props => props.theme.colors.border};
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
`;

const FilterGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 150px;
`;

const FilterLabel = styled.label`
  font-size: 14px;
  font-weight: 600;
  color: ${props => props.theme.colors.textSecondary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const FilterSelect = styled.select`
  padding: 8px 12px;
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 8px;
  background: ${props => props.theme.colors.background};
  color: ${props => props.theme.colors.text};
  font-size: 14px;
  cursor: pointer;
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
`;

const SearchInput = styled.input`
  padding: 12px 16px;
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 12px;
  background: ${props => props.theme.colors.background};
  color: ${props => props.theme.colors.text};
  font-size: 16px;
  flex: 1;
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  
  &::placeholder {
    color: ${props => props.theme.colors.textSecondary};
  }
`;

const ViewModeToggle = styled.div`
  display: flex;
  background: ${props => props.theme.colors.cardBackground};
  border-radius: 12px;
  padding: 4px;
  border: 1px solid ${props => props.theme.colors.border};
`;

const ViewModeButton = styled.button<{ active?: boolean }>`
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: ${props => props.active ? props.theme.colors.primary : 'transparent'};
  color: ${props => props.active ? 'white' : props.theme.colors.textSecondary};
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: ${props => props.active ? props.theme.colors.primary : props.theme.colors.hover};
  }
`;

const ContentGrid = styled.div<{ viewMode: string }>`
  display: grid;
  gap: 24px;
  
  ${props => {
    switch (props.viewMode) {
      case 'list':
        return 'grid-template-columns: 1fr;';
      case 'masonry':
        return `
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          grid-auto-rows: masonry;
        `;
      default:
        return `
          grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
          @media (min-width: 768px) {
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          }
          @media (min-width: 1200px) {
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
          }
        `;
    }
  }}
`;

const ContentCard = styled.div<{ viewMode: string; selected?: boolean }>`
  background: ${props => props.theme.colors.cardBackground};
  border-radius: 16px;
  overflow: hidden;
  border: 2px solid ${props => props.selected ? props.theme.colors.primary : props.theme.colors.border};
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  animation: ${scaleIn} 0.3s ease-out;
  
  ${props => props.viewMode === 'list' && `
    display: flex;
    align-items: center;
    padding: 16px;
    gap: 16px;
  `}
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
  }
`;

const ContentThumbnail = styled.div<{ viewMode: string }>`
  position: relative;
  ${props => props.viewMode === 'list' ? `
    width: 120px;
    height: 80px;
    flex-shrink: 0;
  ` : `
    width: 100%;
    height: 200px;
  `}
  background: linear-gradient(90deg, #f0f0f0 0%, #e0e0e0 50%, #f0f0f0 100%);
  background-size: 200px 100%;
  animation: ${shimmer} 1.5s infinite;
  border-radius: ${props => props.viewMode === 'list' ? '8px' : '0'};
  overflow: hidden;
`;

const ThumbnailImage = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
  
  &:hover {
    transform: scale(1.05);
  }
`;

const ContentOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.7) 100%);
  display: flex;
  align-items: flex-end;
  padding: 16px;
  opacity: 0;
  transition: opacity 0.3s ease;
  
  ${ContentCard}:hover & {
    opacity: 1;
  }
`;

const PlayButton = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translate(-50%, -50%) scale(1.1);
    background: white;
  }
`;

const ContentInfo = styled.div<{ viewMode: string }>`
  padding: ${props => props.viewMode === 'list' ? '0' : '20px'};
  flex: 1;
`;

const ContentTitle = styled.h3`
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
  line-height: 1.3;
  
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const ContentDescription = styled.p`
  margin: 0 0 12px 0;
  font-size: 14px;
  color: ${props => props.theme.colors.textSecondary};
  line-height: 1.4;
  
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const ContentMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
`;

const MetaBadge = styled.span<{ variant?: 'type' | 'status' | 'ai' | 'performance' }>`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  
  ${props => {
    switch (props.variant) {
      case 'type':
        return `background: rgba(59, 130, 246, 0.1); color: #2563eb;`;
      case 'status':
        return `background: rgba(34, 197, 94, 0.1); color: #16a34a;`;
      case 'ai':
        return `background: rgba(139, 92, 246, 0.1); color: #7c3aed;`;
      case 'performance':
        return `background: rgba(245, 158, 11, 0.1); color: #d97706;`;
      default:
        return `background: rgba(107, 114, 128, 0.1); color: #374151;`;
    }
  }}
`;

const PerformanceStats = styled.div`
  display: flex;
  gap: 16px;
  align-items: center;
  margin-top: 12px;
`;

const PerformanceStat = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: ${props => props.theme.colors.textSecondary};
`;

const BulkActions = styled.div`
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: ${props => props.theme.colors.cardBackground};
  border-radius: 16px;
  padding: 16px 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  border: 1px solid ${props => props.theme.colors.border};
  display: flex;
  align-items: center;
  gap: 16px;
  z-index: 1000;
  animation: ${fadeInUp} 0.3s ease-out;
`;

const ActionButton = styled.button<{ variant?: 'primary' | 'secondary' | 'danger' }>`
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  
  ${props => {
    switch (props.variant) {
      case 'primary':
        return `
          background: linear-gradient(135deg, #3b82f6, #2563eb);
          color: white;
          &:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); }
        `;
      case 'danger':
        return `
          background: linear-gradient(135deg, #ef4444, #dc2626);
          color: white;
          &:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3); }
        `;
      default:
        return `
          background: ${props.theme.colors.background};
          color: ${props.theme.colors.text};
          border: 1px solid ${props.theme.colors.border};
          &:hover { background: ${props.theme.colors.hover}; }
        `;
    }
  }}
`;

// ==================== THEME ====================

const theme = {
  colors: {
    background: '#f8fafc',
    cardBackground: '#ffffff',
    text: '#1e293b',
    textSecondary: '#64748b',
    border: '#e2e8f0',
    hover: '#f1f5f9',
    primary: '#3b82f6',
    success: '#22c55e',
    error: '#ef4444',
    warning: '#f59e0b'
  }
};

// ==================== UTILITY FUNCTIONS ====================

const formatFileSize = (bytes: number): string => {
  if (bytes >= 1024 * 1024 * 1024) {
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  }
  if (bytes >= 1024 * 1024) {
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }
  if (bytes >= 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${bytes} B`;
};

const formatDuration = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toString();
};

// ==================== MAIN COMPONENT ====================

export const ContentGalleryTemplate: React.FC<ContentGalleryProps> = ({
  creatorId,
  className,
  theme: themeMode = 'light',
  viewMode: initialViewMode = 'grid',
  enableBulkActions = true,
  enableAIInsights = true,
  onContentSelect,
  onContentEdit,
  onContentDelete,
  onBulkAction
}) => {
  // ================ STATE MANAGEMENT ================
  const [content, setContent] = useState<ContentItem[]>([]);
  const [filteredContent, setFilteredContent] = useState<ContentItem[]>([]);
  const [selectedContent, setSelectedContent] = useState<Set<string>>(new Set());
  const [viewMode, setViewMode] = useState(initialViewMode);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<FilterOptions>({
    type: [],
    status: [],
    visibility: [],
    dateRange: {},
    aiCategories: [],
    performanceRange: {},
    monetization: 'all'
  });
  const [sortOptions, setSortOptions] = useState<SortOptions>({
    field: 'createdAt',
    direction: 'desc'
  });
  const [isLoading, setIsLoading] = useState(false);

  // ================ EFFECTS ================
  useEffect(() => {
    fetchContent();
  }, [creatorId]);

  useEffect(() => {
    filterAndSortContent();
  }, [content, searchQuery, filters, sortOptions]);

  // ================ API FUNCTIONS ================
  const fetchContent = useCallback(async () => {
    setIsLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock content data
      const mockContent: ContentItem[] = [
        {
          id: '1',
          title: 'Epic Orchestral Mix 2025',
          description: 'A powerful orchestral composition featuring epic themes and cinematic elements.',
          type: 'audio',
          url: '/content/epic-orchestral-mix-2025.mp3',
          thumbnailUrl: 'https://api.placeholder.pics/300x200',
          duration: 245,
          fileSize: 12456789,
          format: 'MP3',
          createdAt: new Date('2025-01-15'),
          updatedAt: new Date('2025-01-15'),
          status: 'published',
          visibility: 'public',
          tags: ['orchestral', 'epic', 'cinematic', 'powerful'],
          aiCategories: ['Epic Music', 'Orchestral', 'Cinematic Score'],
          aiSentiment: 'positive',
          aiContentScore: 94.5,
          performance: {
            views: 156789,
            likes: 12456,
            shares: 2345,
            comments: 856,
            revenue: 1247.50,
            engagementRate: 78.5
          },
          metadata: {
            bitrate: 320,
            channels: 2
          },
          monetization: {
            isMonetized: true,
            price: 9.99,
            currency: 'USD',
            salesCount: 125
          }
        },
        {
          id: '2',
          title: 'Behind the Scenes: Studio Session',
          description: 'Exclusive look into the creative process of making epic music.',
          type: 'video',
          url: '/content/studio-session.mp4',
          thumbnailUrl: 'https://api.placeholder.pics/300x200',
          duration: 890,
          fileSize: 234567890,
          format: 'MP4',
          createdAt: new Date('2025-01-12'),
          updatedAt: new Date('2025-01-13'),
          status: 'published',
          visibility: 'premium',
          tags: ['behind the scenes', 'studio', 'creative process'],
          aiCategories: ['Educational', 'Behind the Scenes', 'Music Production'],
          aiSentiment: 'positive',
          aiContentScore: 87.2,
          performance: {
            views: 89234,
            likes: 8765,
            shares: 1234,
            comments: 456,
            revenue: 2456.80,
            engagementRate: 82.1
          },
          metadata: {
            resolution: '1920x1080',
            fps: 30,
            codec: 'H.264'
          },
          monetization: {
            isMonetized: true,
            price: 19.99,
            currency: 'USD',
            salesCount: 123
          }
        }
      ];
      
      setContent(mockContent);
    } catch (error) {
      console.error('Failed to fetch content:', error);
    } finally {
      setIsLoading(false);
    }
  }, [creatorId]);

  // ================ FILTERING & SORTING ================
  const filterAndSortContent = useCallback(() => {
    let filtered = [...content];
    
    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(item =>
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }
    
    // Apply type filter
    if (filters.type.length > 0) {
      filtered = filtered.filter(item => filters.type.includes(item.type));
    }
    
    // Apply status filter
    if (filters.status.length > 0) {
      filtered = filtered.filter(item => filters.status.includes(item.status));
    }
    
    // Apply monetization filter
    if (filters.monetization !== 'all') {
      filtered = filtered.filter(item => 
        filters.monetization === 'monetized' ? item.monetization.isMonetized : !item.monetization.isMonetized
      );
    }
    
    // Apply sorting
    filtered.sort((a, b) => {
      const aValue = a[sortOptions.field];
      const bValue = b[sortOptions.field];
      
      if (sortOptions.direction === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });
    
    setFilteredContent(filtered);
  }, [content, searchQuery, filters, sortOptions]);

  // ================ EVENT HANDLERS ================
  const handleContentSelect = useCallback((contentId: string) => {
    const newSelected = new Set(selectedContent);
    if (newSelected.has(contentId)) {
      newSelected.delete(contentId);
    } else {
      newSelected.add(contentId);
    }
    setSelectedContent(newSelected);
  }, [selectedContent]);

  const handleSelectAll = useCallback(() => {
    if (selectedContent.size === filteredContent.length) {
      setSelectedContent(new Set());
    } else {
      setSelectedContent(new Set(filteredContent.map(item => item.id)));
    }
  }, [selectedContent.size, filteredContent]);

  const handleBulkAction = useCallback((action: string) => {
    const selectedIds = Array.from(selectedContent);
    onBulkAction?.(action, selectedIds);
    setSelectedContent(new Set());
  }, [selectedContent, onBulkAction]);

  // ================ COMPUTED VALUES ================
  const contentStats = useMemo(() => {
    return {
      total: content.length,
      published: content.filter(item => item.status === 'published').length,
      monetized: content.filter(item => item.monetization.isMonetized).length,
      totalViews: content.reduce((sum, item) => sum + item.performance.views, 0)
    };
  }, [content]);

  // ================ RENDER ================
  return (
    <ThemeProvider theme={theme}>
      <GalleryContainer className={className}>
        {/* Header */}
        <GalleryHeader>
          <div>
            <HeaderTitle>Content Gallery</HeaderTitle>
            <StatsBar>
              <StatItem>
                <StatValue>{contentStats.total}</StatValue>
                <StatLabel>Total Items</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>{contentStats.published}</StatValue>
                <StatLabel>Published</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>{contentStats.monetized}</StatValue>
                <StatLabel>Monetized</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>{formatNumber(contentStats.totalViews)}</StatValue>
                <StatLabel>Total Views</StatLabel>
              </StatItem>
            </StatsBar>
          </div>
          
          <ViewModeToggle>
            <ViewModeButton
              active={viewMode === 'grid'}
              onClick={() => setViewMode('grid')}
            >
              Grid
            </ViewModeButton>
            <ViewModeButton
              active={viewMode === 'list'}
              onClick={() => setViewMode('list')}
            >
              List
            </ViewModeButton>
            <ViewModeButton
              active={viewMode === 'masonry'}
              onClick={() => setViewMode('masonry')}
            >
              Masonry
            </ViewModeButton>
          </ViewModeToggle>
        </GalleryHeader>

        {/* Filters */}
        <FilterControls>
          <SearchInput
            type="text"
            placeholder="Search content..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          
          <FilterGroup>
            <FilterLabel>Type</FilterLabel>
            <FilterSelect
              value=""
              onChange={(e) => {
                if (e.target.value) {
                  setFilters(prev => ({
                    ...prev,
                    type: [...prev.type, e.target.value]
                  }));
                }
              }}
            >
              <option value="">All Types</option>
              <option value="audio">Audio</option>
              <option value="video">Video</option>
              <option value="image">Image</option>
              <option value="document">Document</option>
            </FilterSelect>
          </FilterGroup>
          
          <FilterGroup>
            <FilterLabel>Status</FilterLabel>
            <FilterSelect
              value=""
              onChange={(e) => {
                if (e.target.value) {
                  setFilters(prev => ({
                    ...prev,
                    status: [...prev.status, e.target.value]
                  }));
                }
              }}
            >
              <option value="">All Status</option>
              <option value="draft">Draft</option>
              <option value="published">Published</option>
              <option value="private">Private</option>
              <option value="archived">Archived</option>
            </FilterSelect>
          </FilterGroup>
          
          <FilterGroup>
            <FilterLabel>Sort By</FilterLabel>
            <FilterSelect
              value={`${sortOptions.field}-${sortOptions.direction}`}
              onChange={(e) => {
                const [field, direction] = e.target.value.split('-');
                setSortOptions({
                  field: field as SortOptions['field'],
                  direction: direction as SortOptions['direction']
                });
              }}
            >
              <option value="createdAt-desc">Newest First</option>
              <option value="createdAt-asc">Oldest First</option>
              <option value="views-desc">Most Views</option>
              <option value="likes-desc">Most Liked</option>
              <option value="revenue-desc">Highest Revenue</option>
              <option value="aiContentScore-desc">Highest AI Score</option>
            </FilterSelect>
          </FilterGroup>
          
          {enableBulkActions && (
            <ActionButton onClick={handleSelectAll}>
              {selectedContent.size === filteredContent.length ? 'Deselect All' : 'Select All'}
            </ActionButton>
          )}
        </FilterControls>

        {/* Content Grid */}
        <ContentGrid viewMode={viewMode}>
          {filteredContent.map((item) => (
            <ContentCard
              key={item.id}
              viewMode={viewMode}
              selected={selectedContent.has(item.id)}
              onClick={() => {
                if (enableBulkActions) {
                  handleContentSelect(item.id);
                } else {
                  onContentSelect?.(item);
                }
              }}
            >
              <ContentThumbnail viewMode={viewMode}>
                <ThumbnailImage
                  src={item.thumbnailUrl}
                  alt={item.title}
                  loading="lazy"
                />
                {(item.type === 'audio' || item.type === 'video') && (
                  <PlayButton>▶</PlayButton>
                )}
                <ContentOverlay>
                  <div style={{ color: 'white', fontSize: '14px', fontWeight: '600' }}>
                    {item.duration && formatDuration(item.duration)}
                  </div>
                </ContentOverlay>
              </ContentThumbnail>
              
              <ContentInfo viewMode={viewMode}>
                <ContentMeta>
                  <MetaBadge variant="type">{item.type}</MetaBadge>
                  <MetaBadge variant="status">{item.status}</MetaBadge>
                  {enableAIInsights && (
                    <MetaBadge variant="ai">
                      AI: {item.aiContentScore.toFixed(1)}
                    </MetaBadge>
                  )}
                  {item.monetization.isMonetized && (
                    <MetaBadge variant="performance">
                      ${item.monetization.price}
                    </MetaBadge>
                  )}
                </ContentMeta>
                
                <ContentTitle>{item.title}</ContentTitle>
                <ContentDescription>{item.description}</ContentDescription>
                
                <PerformanceStats>
                  <PerformanceStat>
                    👁️ {formatNumber(item.performance.views)}
                  </PerformanceStat>
                  <PerformanceStat>
                    ❤️ {formatNumber(item.performance.likes)}
                  </PerformanceStat>
                  <PerformanceStat>
                    💰 ${item.performance.revenue.toFixed(0)}
                  </PerformanceStat>
                  <PerformanceStat>
                    📊 {item.performance.engagementRate}%
                  </PerformanceStat>
                </PerformanceStats>
              </ContentInfo>
            </ContentCard>
          ))}
        </ContentGrid>

        {/* Bulk Actions */}
        {enableBulkActions && selectedContent.size > 0 && (
          <BulkActions>
            <span>{selectedContent.size} selected</span>
            <ActionButton
              variant="primary"
              onClick={() => handleBulkAction('edit')}
            >
              Edit
            </ActionButton>
            <ActionButton
              onClick={() => handleBulkAction('archive')}
            >
              Archive
            </ActionButton>
            <ActionButton
              variant="danger"
              onClick={() => handleBulkAction('delete')}
            >
              Delete
            </ActionButton>
          </BulkActions>
        )}
      </GalleryContainer>
    </ThemeProvider>
  );
};

// ==================== EXPORTS ====================
export default ContentGalleryTemplate;

export type {
  ContentGalleryProps,
  ContentItem,
  FilterOptions,
  SortOptions
};