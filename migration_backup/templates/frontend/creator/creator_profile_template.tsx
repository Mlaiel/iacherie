/**
 * 🎭 Creator Profile Template - Enterprise Component
 * =================================================
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 * 
 * @author Fahed Mlaiel
 * @role Lead Dev IA + Backend Senior + ML Engineer + Creator Economy Expert
 * @description Enterprise creator profile template with multi-format content, 
 *              analytics dashboard, collaboration tools, and monetization features
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import styled, { ThemeProvider, keyframes } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

// ===========================
// 🎨 STYLED COMPONENTS & ANIMATIONS
// ===========================

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;

const ProfileContainer = styled(motion.div)`
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  overflow-x: hidden;
`;

const ProfileHeader = styled.div`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 24px;
  align-items: center;
`;

const AvatarSection = styled.div`
  position: relative;
`;

const Avatar = styled.img`
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #667eea;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
`;

const OnlineIndicator = styled.div`
  position: absolute;
  bottom: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  background: #4ade80;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
`;

const ProfileInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const CreatorName = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const CreatorBio = styled.p`
  font-size: 16px;
  color: #64748b;
  margin: 0;
  line-height: 1.6;
`;

const CreatorStats = styled.div`
  display: flex;
  gap: 32px;
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 16px;
  }
`;

const StatItem = styled.div`
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
`;

const StatLabel = styled.div`
  font-size: 14px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 16px;
  
  @media (max-width: 768px) {
    flex-direction: column;
    width: 100%;
  }
`;

const Button = styled(motion.button)<{ variant?: 'primary' | 'secondary' }>`
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  
  ${props => props.variant === 'primary' ? `
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
  ` : `
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
    border: 2px solid #667eea;
    &:hover {
      background: #667eea;
      color: white;
    }
  `}
`;

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const ContentSection = styled.div`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
`;

const SectionTitle = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 24px 0;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const ContentTabs = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 1px solid #e2e8f0;
`;

const Tab = styled.button<{ active?: boolean }>`
  padding: 12px 20px;
  border: none;
  background: none;
  color: ${props => props.active ? '#667eea' : '#64748b'};
  font-weight: ${props => props.active ? '600' : '400'};
  border-bottom: 2px solid ${props => props.active ? '#667eea' : 'transparent'};
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    color: #667eea;
  }
`;

const ContentGrid2 = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
`;

const ContentCard = styled(motion.div)`
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
  }
`;

const ContentPreview = styled.div`
  height: 200px;
  background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-size: 18px;
`;

const ContentMeta = styled.div`
  padding: 16px;
`;

const ContentTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
`;

const ContentStats = styled.div`
  display: flex;
  justify-content: space-between;
  color: #64748b;
  font-size: 14px;
`;

const Sidebar = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const SidebarSection = styled.div`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
`;

const AnalyticsChart = styled.div`
  height: 200px;
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  margin-bottom: 16px;
`;

const MetricsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const MetricItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 8px;
`;

const MetricLabel = styled.span`
  color: #64748b;
  font-size: 14px;
`;

const MetricValue = styled.span`
  font-weight: 600;
  color: #667eea;
`;

// ===========================
// 🎯 INTERFACES & TYPES
// ===========================

interface CreatorProfile {
  id: string;
  name: string;
  username: string;
  bio: string;
  avatar: string;
  coverImage?: string;
  isOnline: boolean;
  stats: {
    followers: number;
    following: number;
    content: number;
    revenue: number;
  };
  content: ContentItem[];
  analytics: AnalyticsData;
  collaborations: Collaboration[];
}

interface ContentItem {
  id: string;
  title: string;
  type: 'video' | 'audio' | 'image' | 'text' | 'live';
  thumbnail?: string;
  views: number;
  likes: number;
  comments: number;
  revenue: number;
  createdAt: Date;
}

interface AnalyticsData {
  totalViews: number;
  totalRevenue: number;
  engagementRate: number;
  growthRate: number;
  topContent: ContentItem[];
}

interface Collaboration {
  id: string;
  title: string;
  partner: string;
  status: 'active' | 'pending' | 'completed';
  revenue: number;
}

interface CreatorProfileTemplateProps {
  profile: CreatorProfile;
  isOwnProfile?: boolean;
  onFollow?: () => void;
  onMessage?: () => void;
  onCollaborate?: () => void;
  onContentSelect?: (content: ContentItem) => void;
  theme?: any;
}

// ===========================
// 🚀 MAIN COMPONENT
// ===========================

export const CreatorProfileTemplate: React.FC<CreatorProfileTemplateProps> = ({
  profile,
  isOwnProfile = false,
  onFollow,
  onMessage,
  onCollaborate,
  onContentSelect,
  theme = defaultTheme
}) => {
  const [activeTab, setActiveTab] = useState<'content' | 'analytics' | 'collaborations'>('content');
  const [isFollowing, setIsFollowing] = useState(false);

  // Format numbers for display
  const formatNumber = useCallback((num: number): string => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  }, []);

  // Handle follow action
  const handleFollow = useCallback(() => {
    setIsFollowing(!isFollowing);
    onFollow?.();
  }, [isFollowing, onFollow]);

  // Filter content by type
  const contentByType = useMemo(() => {
    return profile.content.reduce((acc, item) => {
      if (!acc[item.type]) acc[item.type] = [];
      acc[item.type].push(item);
      return acc;
    }, {} as Record<string, ContentItem[]>);
  }, [profile.content]);

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 100
      }
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <ProfileContainer
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Profile Header */}
        <motion.div variants={itemVariants}>
          <ProfileHeader>
            <AvatarSection>
              <Avatar src={profile.avatar} alt={profile.name} />
              {profile.isOnline && <OnlineIndicator />}
            </AvatarSection>
            
            <ProfileInfo>
              <CreatorName>{profile.name}</CreatorName>
              <CreatorBio>{profile.bio}</CreatorBio>
              <CreatorStats>
                <StatItem>
                  <StatValue>{formatNumber(profile.stats.followers)}</StatValue>
                  <StatLabel>Followers</StatLabel>
                </StatItem>
                <StatItem>
                  <StatValue>{formatNumber(profile.stats.following)}</StatValue>
                  <StatLabel>Following</StatLabel>
                </StatItem>
                <StatItem>
                  <StatValue>{formatNumber(profile.stats.content)}</StatValue>
                  <StatLabel>Content</StatLabel>
                </StatItem>
                <StatItem>
                  <StatValue>${formatNumber(profile.stats.revenue)}</StatValue>
                  <StatLabel>Revenue</StatLabel>
                </StatItem>
              </CreatorStats>
            </ProfileInfo>
            
            {!isOwnProfile && (
              <ActionButtons>
                <Button
                  variant="primary"
                  onClick={handleFollow}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {isFollowing ? 'Following' : 'Follow'}
                </Button>
                <Button
                  variant="secondary"
                  onClick={onMessage}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Message
                </Button>
                <Button
                  variant="secondary"
                  onClick={onCollaborate}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Collaborate
                </Button>
              </ActionButtons>
            )}
          </ProfileHeader>
        </motion.div>

        {/* Main Content Grid */}
        <ContentGrid>
          {/* Content Section */}
          <motion.div variants={itemVariants}>
            <ContentSection>
              <SectionTitle>
                🎨 Creator Content
              </SectionTitle>
              
              <ContentTabs>
                <Tab
                  active={activeTab === 'content'}
                  onClick={() => setActiveTab('content')}
                >
                  All Content
                </Tab>
                <Tab
                  active={activeTab === 'analytics'}
                  onClick={() => setActiveTab('analytics')}
                >
                  Analytics
                </Tab>
                <Tab
                  active={activeTab === 'collaborations'}
                  onClick={() => setActiveTab('collaborations')}
                >
                  Collaborations
                </Tab>
              </ContentTabs>

              <AnimatePresence mode="wait">
                {activeTab === 'content' && (
                  <motion.div
                    key="content"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                  >
                    <ContentGrid2>
                      {profile.content.map((item, index) => (
                        <ContentCard
                          key={item.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.1 }}
                          whileHover={{ y: -4 }}
                          onClick={() => onContentSelect?.(item)}
                        >
                          <ContentPreview>
                            {item.thumbnail ? (
                              <img src={item.thumbnail} alt={item.title} />
                            ) : (
                              `${item.type.toUpperCase()} Content`
                            )}
                          </ContentPreview>
                          <ContentMeta>
                            <ContentTitle>{item.title}</ContentTitle>
                            <ContentStats>
                              <span>{formatNumber(item.views)} views</span>
                              <span>${formatNumber(item.revenue)}</span>
                            </ContentStats>
                          </ContentMeta>
                        </ContentCard>
                      ))}
                    </ContentGrid2>
                  </motion.div>
                )}
              </AnimatePresence>
            </ContentSection>
          </motion.div>

          {/* Sidebar */}
          <motion.div variants={itemVariants}>
            <Sidebar>
              {/* Analytics Overview */}
              <SidebarSection>
                <SectionTitle>📊 Analytics</SectionTitle>
                <AnalyticsChart>
                  📈 Revenue Growth Chart
                </AnalyticsChart>
                <MetricsList>
                  <MetricItem>
                    <MetricLabel>Total Views</MetricLabel>
                    <MetricValue>{formatNumber(profile.analytics.totalViews)}</MetricValue>
                  </MetricItem>
                  <MetricItem>
                    <MetricLabel>Engagement Rate</MetricLabel>
                    <MetricValue>{profile.analytics.engagementRate}%</MetricValue>
                  </MetricItem>
                  <MetricItem>
                    <MetricLabel>Growth Rate</MetricLabel>
                    <MetricValue>+{profile.analytics.growthRate}%</MetricValue>
                  </MetricItem>
                </MetricsList>
              </SidebarSection>

              {/* Recent Collaborations */}
              <SidebarSection>
                <SectionTitle>🤝 Collaborations</SectionTitle>
                <MetricsList>
                  {profile.collaborations.slice(0, 3).map((collab) => (
                    <MetricItem key={collab.id}>
                      <div>
                        <MetricLabel>{collab.title}</MetricLabel>
                        <div style={{ fontSize: '12px', color: '#64748b' }}>
                          with {collab.partner}
                        </div>
                      </div>
                      <MetricValue>${formatNumber(collab.revenue)}</MetricValue>
                    </MetricItem>
                  ))}
                </MetricsList>
              </SidebarSection>
            </Sidebar>
          </motion.div>
        </ContentGrid>
      </ProfileContainer>
    </ThemeProvider>
  );
};

// ===========================
// 🎨 DEFAULT THEME
// ===========================

const defaultTheme = {
  colors: {
    primary: '#667eea',
    secondary: '#764ba2',
    background: '#f8fafc',
    surface: '#ffffff',
    text: '#1e293b',
    textSecondary: '#64748b',
    success: '#4ade80',
    warning: '#fbbf24',
    error: '#ef4444',
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    xxl: '48px',
  },
  borderRadius: {
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    full: '50%',
  },
  shadows: {
    sm: '0 2px 8px rgba(0, 0, 0, 0.1)',
    md: '0 8px 32px rgba(0, 0, 0, 0.1)',
    lg: '0 20px 40px rgba(0, 0, 0, 0.1)',
  },
};

// ===========================
// 🧪 USAGE EXAMPLES
// ===========================

export const CreatorProfileExamples = {
  basic: {
    id: '1',
    name: 'Alex Creator',
    username: '@alexcreator',
    bio: 'Multi-format content creator specializing in tech education and entertainment',
    avatar: '/api/placeholder/120/120',
    isOnline: true,
    stats: {
      followers: 125000,
      following: 892,
      content: 1247,
      revenue: 45600
    },
    content: [
      {
        id: '1',
        title: 'Advanced React Patterns',
        type: 'video' as const,
        views: 15600,
        likes: 892,
        comments: 127,
        revenue: 2400,
        createdAt: new Date()
      }
    ],
    analytics: {
      totalViews: 2500000,
      totalRevenue: 145600,
      engagementRate: 8.5,
      growthRate: 15.2,
      topContent: []
    },
    collaborations: [
      {
        id: '1',
        title: 'Tech Education Series',
        partner: 'TechCorp',
        status: 'active' as const,
        revenue: 12000
      }
    ]
  }
};

export default CreatorProfileTemplate;