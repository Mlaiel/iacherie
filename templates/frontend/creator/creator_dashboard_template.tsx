/**
 * 🎨 CREATOR DASHBOARD TEMPLATE - CREATOR ECONOMY INTERFACE
 * =========================================================
 * 
 * Enterprise Creator Dashboard component with:
 * - Real-time analytics and metrics
 * - Content management interface
 * - Revenue tracking and insights
 * - Collaboration management
 * - Creator Economy specialized features
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 */

import React, { useState, useEffect, useMemo } from 'react';
import styled, { css, keyframes } from 'styled-components';

// Animation keyframes
const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
`;

const slideUp = keyframes`
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`;

const countUp = keyframes`
  from { transform: scale(0.8); }
  to { transform: scale(1); }
`;

// Types
export interface CreatorData {
  id: string;
  name: string;
  avatar?: string;
  tier: 'basic' | 'pro' | 'enterprise';
  verified: boolean;
  joinDate: Date;
  stats: {
    totalContent: number;
    totalViews: number;
    totalRevenue: number;
    subscribers: number;
    engagement: number;
    monthlyViews: number;
    monthlyRevenue: number;
  };
  recentContent: ContentItem[];
  analytics: AnalyticsData;
  collaborations: CollaborationItem[];
  notifications: NotificationItem[];
}

export interface ContentItem {
  id: string;
  title: string;
  type: 'video' | 'audio' | 'image' | 'text' | 'live';
  thumbnail?: string;
  views: number;
  likes: number;
  revenue: number;
  createdAt: Date;
  status: 'published' | 'draft' | 'scheduled' | 'processing';
}

export interface AnalyticsData {
  viewsChart: { date: string; views: number }[];
  revenueChart: { date: string; revenue: number }[];
  engagementChart: { date: string; engagement: number }[];
  topContent: ContentItem[];
  demographics: {
    age: Record<string, number>;
    location: Record<string, number>;
    devices: Record<string, number>;
  };
}

export interface CollaborationItem {
  id: string;
  collaborator: {
    id: string;
    name: string;
    avatar?: string;
  };
  type: 'active' | 'pending' | 'request';
  project: string;
  revenue: number;
  createdAt: Date;
}

export interface NotificationItem {
  id: string;
  type: 'revenue' | 'collaboration' | 'content' | 'system';
  title: string;
  message: string;
  read: boolean;
  createdAt: Date;
}

export interface CreatorDashboardProps {
  creatorData: CreatorData;
  onContentClick?: (content: ContentItem) => void;
  onCollaborationClick?: (collaboration: CollaborationItem) => void;
  onNotificationClick?: (notification: NotificationItem) => void;
  onCreateContent?: () => void;
  onInviteCollaborator?: () => void;
  loading?: boolean;
}

// Styled components
const DashboardContainer = styled.div`
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  animation: ${slideUp} 0.6s ease-out;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: between;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 1rem;
  color: white;
`;

const CreatorInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const Avatar = styled.img`
  width: 4rem;
  height: 4rem;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
`;

const CreatorDetails = styled.div`
  h1 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
  }
  
  p {
    margin: 0.25rem 0 0 0;
    opacity: 0.9;
    font-size: 0.875rem;
  }
`;

const TierBadge = styled.span<{ tier: string }>`
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  
  ${props => {
    switch (props.tier) {
      case 'enterprise':
        return css`
          background: linear-gradient(45deg, #ffd700, #ffed4e);
          color: #7c2d12;
        `;
      case 'pro':
        return css`
          background: linear-gradient(45deg, #c084fc, #a855f7);
          color: white;
        `;
      default:
        return css`
          background: linear-gradient(45deg, #60a5fa, #3b82f6);
          color: white;
        `;
    }
  }}
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const StatCard = styled.div<{ color?: string }>`
  padding: 1.5rem;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border-left: 4px solid ${props => props.color || '#3b82f6'};
  transition: transform 0.2s ease-in-out;
  
  &:hover {
    transform: translateY(-2px);
  }
`;

const StatValue = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  animation: ${countUp} 0.6s ease-out;
`;

const StatLabel = styled.div`
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
`;

const StatChange = styled.div<{ positive?: boolean }>`
  font-size: 0.75rem;
  margin-top: 0.5rem;
  color: ${props => props.positive ? '#10b981' : '#ef4444'};
  font-weight: 600;
`;

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const ContentSection = styled.div`
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
`;

const SectionHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: between;
  margin-bottom: 1rem;
  
  h2 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #1f2937;
  }
`;

const ContentList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const ContentItem = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  
  &:hover {
    border-color: #3b82f6;
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
  }
`;

const ContentThumbnail = styled.img`
  width: 3rem;
  height: 3rem;
  border-radius: 0.375rem;
  object-fit: cover;
`;

const ContentInfo = styled.div`
  flex: 1;
  
  h3 {
    margin: 0;
    font-size: 0.875rem;
    font-weight: 600;
    color: #1f2937;
  }
  
  p {
    margin: 0.25rem 0 0 0;
    font-size: 0.75rem;
    color: #6b7280;
  }
`;

const ContentStats = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
  
  span {
    font-size: 0.75rem;
    color: #6b7280;
  }
  
  strong {
    font-size: 0.875rem;
    color: #1f2937;
  }
`;

const StatusBadge = styled.span<{ status: string }>`
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  
  ${props => {
    switch (props.status) {
      case 'published':
        return css`
          background-color: #d1fae5;
          color: #065f46;
        `;
      case 'processing':
        return css`
          background-color: #fef3c7;
          color: #92400e;
        `;
      case 'scheduled':
        return css`
          background-color: #dbeafe;
          color: #1e40af;
        `;
      default:
        return css`
          background-color: #f3f4f6;
          color: #374151;
        `;
    }
  }}
`;

const ActionButton = styled.button<{ variant?: 'primary' | 'secondary' }>`
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  
  ${props => {
    if (props.variant === 'secondary') {
      return css`
        background-color: #f3f4f6;
        color: #374151;
        
        &:hover {
          background-color: #e5e7eb;
        }
      `;
    }
    
    return css`
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      
      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
      }
    `;
  }}
`;

const LoadingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
`;

const LoadingSpinner = styled.div`
  width: 2rem;
  height: 2rem;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

// Utility functions
const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toString();
};

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount);
};

const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric'
  }).format(date);
};

// Creator Dashboard component
export const CreatorDashboard: React.FC<CreatorDashboardProps> = ({
  creatorData,
  onContentClick,
  onCollaborationClick,
  onNotificationClick,
  onCreateContent,
  onInviteCollaborator,
  loading = false
}) => {
  const [selectedPeriod, setSelectedPeriod] = useState<'7d' | '30d' | '90d'>('30d');

  const stats = useMemo(() => [
    {
      label: 'Total Revenue',
      value: formatCurrency(creatorData.stats.totalRevenue),
      change: '+12.5%',
      positive: true,
      color: '#10b981'
    },
    {
      label: 'Subscribers',
      value: formatNumber(creatorData.stats.subscribers),
      change: '+8.2%',
      positive: true,
      color: '#3b82f6'
    },
    {
      label: 'Total Views',
      value: formatNumber(creatorData.stats.totalViews),
      change: '+15.3%',
      positive: true,
      color: '#8b5cf6'
    },
    {
      label: 'Engagement Rate',
      value: `${creatorData.stats.engagement}%`,
      change: '+2.1%',
      positive: true,
      color: '#f59e0b'
    }
  ], [creatorData.stats]);

  return (
    <DashboardContainer data-testid="creator-dashboard">
      {loading && (
        <LoadingOverlay>
          <LoadingSpinner />
        </LoadingOverlay>
      )}
      
      {/* Header */}
      <Header>
        <CreatorInfo>
          <Avatar
            src={creatorData.avatar || '/default-avatar.png'}
            alt={creatorData.name}
          />
          <CreatorDetails>
            <h1>
              {creatorData.name}
              {creatorData.verified && ' ✓'}
            </h1>
            <p>
              <TierBadge tier={creatorData.tier}>
                {creatorData.tier}
              </TierBadge>
              {' '}Creator since {formatDate(creatorData.joinDate)}
            </p>
          </CreatorDetails>
        </CreatorInfo>
        
        <div style={{ display: 'flex', gap: '1rem' }}>
          <ActionButton onClick={onCreateContent}>
            Create Content
          </ActionButton>
          <ActionButton variant="secondary" onClick={onInviteCollaborator}>
            Invite Collaborator
          </ActionButton>
        </div>
      </Header>

      {/* Stats Grid */}
      <StatsGrid>
        {stats.map((stat, index) => (
          <StatCard key={index} color={stat.color}>
            <StatValue>{stat.value}</StatValue>
            <StatLabel>{stat.label}</StatLabel>
            <StatChange positive={stat.positive}>
              {stat.change}
            </StatChange>
          </StatCard>
        ))}
      </StatsGrid>

      {/* Content Grid */}
      <ContentGrid>
        {/* Recent Content */}
        <ContentSection>
          <SectionHeader>
            <h2>Recent Content</h2>
            <ActionButton onClick={onCreateContent}>
              + New Content
            </ActionButton>
          </SectionHeader>
          
          <ContentList>
            {creatorData.recentContent.slice(0, 5).map(content => (
              <ContentItem
                key={content.id}
                onClick={() => onContentClick?.(content)}
              >
                <ContentThumbnail
                  src={content.thumbnail || '/default-thumbnail.png'}
                  alt={content.title}
                />
                <ContentInfo>
                  <h3>{content.title}</h3>
                  <p>
                    {content.type} • {formatDate(content.createdAt)}
                  </p>
                </ContentInfo>
                <ContentStats>
                  <strong>{formatNumber(content.views)} views</strong>
                  <span>{formatCurrency(content.revenue)} revenue</span>
                  <StatusBadge status={content.status}>
                    {content.status}
                  </StatusBadge>
                </ContentStats>
              </ContentItem>
            ))}
          </ContentList>
        </ContentSection>

        {/* Collaborations */}
        <ContentSection>
          <SectionHeader>
            <h2>Active Collaborations</h2>
            <ActionButton variant="secondary" onClick={onInviteCollaborator}>
              + Invite
            </ActionButton>
          </SectionHeader>
          
          <ContentList>
            {creatorData.collaborations
              .filter(c => c.type === 'active')
              .slice(0, 3)
              .map(collaboration => (
                <ContentItem
                  key={collaboration.id}
                  onClick={() => onCollaborationClick?.(collaboration)}
                >
                  <Avatar
                    src={collaboration.collaborator.avatar || '/default-avatar.png'}
                    alt={collaboration.collaborator.name}
                    style={{ width: '2.5rem', height: '2.5rem' }}
                  />
                  <ContentInfo>
                    <h3>{collaboration.collaborator.name}</h3>
                    <p>{collaboration.project}</p>
                  </ContentInfo>
                  <ContentStats>
                    <strong>{formatCurrency(collaboration.revenue)}</strong>
                    <span>Revenue</span>
                  </ContentStats>
                </ContentItem>
              ))}
          </ContentList>
        </ContentSection>
      </ContentGrid>
    </DashboardContainer>
  );
};

export default CreatorDashboard;