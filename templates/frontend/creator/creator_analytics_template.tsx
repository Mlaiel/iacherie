/**
 * @fileoverview Enterprise Creator Analytics Dashboard Template with ML Intelligence
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

interface AnalyticsData {
  views: number;
  uniqueVisitors: number;
  engagement: number;
  shareRate: number;
  conversionRate: number;
  averageSessionDuration: number;
  bounceRate: number;
  retentionRate: number;
}

interface ContentPerformance {
  id: string;
  title: string;
  type: 'audio' | 'video' | 'image' | 'text' | 'live_stream';
  views: number;
  engagement: number;
  revenue: number;
  createdAt: Date;
  trending: boolean;
  aiScore: number; // ML-generated content quality score
  sentiment: 'positive' | 'neutral' | 'negative';
  demographics: {
    ageGroups: Record<string, number>;
    genders: Record<string, number>;
    locations: Record<string, number>;
  };
}

interface AudienceInsights {
  totalFollowers: number;
  growthRate: number;
  engagementRate: number;
  topCountries: Record<string, number>;
  ageDistribution: Record<string, number>;
  genderDistribution: Record<string, number>;
  deviceTypes: Record<string, number>;
  peakHours: Record<string, number>;
  audienceQuality: number; // ML-calculated audience authenticity score
}

interface MLPredictions {
  nextMonthViews: number;
  contentRecommendations: string[];
  optimalPostTimes: string[];
  trendingTopics: string[];
  audienceGrowthForecast: number[];
  revenueProjection: number;
  riskFactors: string[];
  opportunities: string[];
}

interface CreatorAnalyticsProps {
  creatorId: string;
  timeRange: '7d' | '30d' | '90d' | '1y';
  className?: string;
  theme?: 'light' | 'dark' | 'auto';
  showPredictions?: boolean;
  enableRealTime?: boolean;
  onInsightAction?: (action: string, data: any) => void;
}

// ==================== STYLED COMPONENTS ====================

const slideIn = keyframes`
  from { opacity: 0; transform: translateX(-20px); }
  to { opacity: 1; transform: translateX(0); }
`;

const chartAnimation = keyframes`
  from { stroke-dasharray: 0 100; }
  to { stroke-dasharray: 100 100; }
`;

const pulseEffect = keyframes`
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.05); opacity: 0.8; }
  100% { transform: scale(1); opacity: 1; }
`;

const AnalyticsDashboard = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
  padding: 24px;
  background: ${props => props.theme.colors.background};
  min-height: 100vh;
  animation: ${slideIn} 0.8s ease-out;

  @media (min-width: 768px) {
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  }

  @media (min-width: 1400px) {
    grid-template-columns: repeat(5, 1fr);
  }
`;

const AnalyticsCard = styled.div<{ featured?: boolean; fullWidth?: boolean }>`
  background: ${props => props.theme.colors.cardBackground};
  border-radius: 20px;
  padding: 28px;
  border: 1px solid ${props => props.theme.colors.border};
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  grid-column: ${props => props.fullWidth ? 'span 2' : 'span 1'};
  
  ${props => props.featured && `
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    animation: ${pulseEffect} 3s infinite;
  `}

  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.2);
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #22c55e, #3b82f6, #8b5cf6);
  }

  @media (max-width: 1400px) {
    grid-column: span 1;
  }
`;

const MetricHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
`;

const MetricIcon = styled.div<{ bgColor: string }>`
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: ${props => props.bgColor};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
`;

const MetricTitle = styled.h3`
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: ${props => props.theme.colors.textSecondary};
  text-transform: uppercase;
  letter-spacing: 0.8px;
`;

const MetricValue = styled.div<{ color?: string }>`
  font-size: 42px;
  font-weight: 800;
  color: ${props => props.color || props.theme.colors.text};
  margin-bottom: 12px;
  line-height: 1;
`;

const MetricChange = styled.div<{ positive?: boolean }>`
  font-size: 16px;
  font-weight: 600;
  color: ${props => props.positive ? props.theme.colors.success : props.theme.colors.error};
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ChartContainer = styled.div`
  width: 100%;
  height: 200px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 20px;
`;

const ProgressRing = styled.svg`
  transform: rotate(-90deg);
  
  circle {
    fill: none;
    stroke-width: 8;
    stroke-linecap: round;
    animation: ${chartAnimation} 2s ease-out;
  }
`;

const ContentList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 400px;
  overflow-y: auto;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: ${props => props.theme.colors.border};
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: ${props => props.theme.colors.textSecondary};
    border-radius: 3px;
  }
`;

const ContentItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: ${props => props.theme.colors.background};
  border-radius: 12px;
  border: 1px solid ${props => props.theme.colors.border};
  transition: all 0.3s ease;

  &:hover {
    background: ${props => props.theme.colors.hover};
    transform: translateX(4px);
  }
`;

const AIInsightBadge = styled.span<{ type: 'positive' | 'neutral' | 'warning' }>`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  
  ${props => {
    switch (props.type) {
      case 'positive':
        return `background: rgba(34, 197, 94, 0.1); color: #16a34a;`;
      case 'warning':
        return `background: rgba(245, 158, 11, 0.1); color: #d97706;`;
      default:
        return `background: rgba(59, 130, 246, 0.1); color: #2563eb;`;
    }
  }}
`;

const PredictionPanel = styled.div`
  background: linear-gradient(135deg, #1e293b, #334155);
  border-radius: 16px;
  padding: 24px;
  color: white;
  grid-column: span 2;
  
  @media (max-width: 1400px) {
    grid-column: span 1;
  }
`;

const ActionButton = styled.button<{ variant?: 'primary' | 'secondary' }>`
  ${props => props.variant === 'primary' ? `
    background: linear-gradient(135deg, #22c55e, #16a34a);
    color: white;
  ` : `
    background: transparent;
    color: ${props.theme.colors.text};
    border: 2px solid ${props.theme.colors.border};
  `}
  
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  }
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
    success: '#22c55e',
    error: '#ef4444',
    warning: '#f59e0b',
    info: '#3b82f6',
  }
};

// ==================== UTILITY FUNCTIONS ====================

const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toString();
};

const calculateCircleProgress = (percentage: number, radius: number = 90) => {
  const circumference = 2 * Math.PI * radius;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;
  return { strokeDasharray, strokeDashoffset };
};

// ==================== MAIN COMPONENT ====================

export const CreatorAnalyticsTemplate: React.FC<CreatorAnalyticsProps> = ({
  creatorId,
  timeRange,
  className,
  theme: themeMode = 'light',
  showPredictions = true,
  enableRealTime = false,
  onInsightAction
}) => {
  // ================ STATE MANAGEMENT ================
  const [analytics, setAnalytics] = useState<AnalyticsData>({
    views: 2847592,
    uniqueVisitors: 1253847,
    engagement: 78.5,
    shareRate: 12.3,
    conversionRate: 8.7,
    averageSessionDuration: 425,
    bounceRate: 23.4,
    retentionRate: 84.2
  });

  const [contentPerformance, setContentPerformance] = useState<ContentPerformance[]>([]);
  const [audienceInsights, setAudienceInsights] = useState<AudienceInsights | null>(null);
  const [mlPredictions, setMlPredictions] = useState<MLPredictions | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [realTimeMetrics, setRealTimeMetrics] = useState<any>(null);

  // ================ EFFECTS ================
  useEffect(() => {
    fetchAnalyticsData();
    
    if (enableRealTime) {
      const interval = setInterval(fetchRealTimeMetrics, 5000);
      return () => clearInterval(interval);
    }
  }, [creatorId, timeRange, enableRealTime]);

  // ================ API FUNCTIONS ================
  const fetchAnalyticsData = useCallback(async () => {
    setIsLoading(true);
    
    try {
      // Simulate API calls with ML processing
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock ML-enhanced content performance data
      setContentPerformance([
        {
          id: '1',
          title: 'Epic Music Mix 2025',
          type: 'audio',
          views: 156789,
          engagement: 92.5,
          revenue: 1247.50,
          createdAt: new Date('2025-01-10'),
          trending: true,
          aiScore: 94.2,
          sentiment: 'positive',
          demographics: {
            ageGroups: { '18-24': 35, '25-34': 40, '35-44': 20, '45+': 5 },
            genders: { 'male': 55, 'female': 43, 'other': 2 },
            locations: { 'US': 40, 'UK': 20, 'Canada': 15, 'Germany': 10, 'France': 8, 'Other': 7 }
          }
        },
        {
          id: '2',
          title: 'Behind the Scenes: Studio Tour',
          type: 'video',
          views: 89234,
          engagement: 87.1,
          revenue: 892.30,
          createdAt: new Date('2025-01-08'),
          trending: false,
          aiScore: 81.7,
          sentiment: 'positive',
          demographics: {
            ageGroups: { '18-24': 30, '25-34': 45, '35-44': 20, '45+': 5 },
            genders: { 'male': 50, 'female': 48, 'other': 2 },
            locations: { 'US': 35, 'UK': 25, 'Canada': 18, 'Germany': 12, 'Other': 10 }
          }
        }
      ]);

      // Mock audience insights with ML analysis
      setAudienceInsights({
        totalFollowers: 847263,
        growthRate: 18.7,
        engagementRate: 78.5,
        topCountries: { 'United States': 35, 'United Kingdom': 22, 'Canada': 15, 'Germany': 12, 'France': 8 },
        ageDistribution: { '18-24': 32, '25-34': 42, '35-44': 20, '45+': 6 },
        genderDistribution: { 'Male': 52, 'Female': 46, 'Other': 2 },
        deviceTypes: { 'Mobile': 68, 'Desktop': 25, 'Tablet': 7 },
        peakHours: { '9': 15, '12': 25, '18': 40, '21': 60, '22': 45 },
        audienceQuality: 89.3
      });

      // Mock ML predictions
      setMlPredictions({
        nextMonthViews: 3250000,
        contentRecommendations: [
          'Create more collaborative content - 23% higher engagement',
          'Post between 6-8 PM for 40% better reach',
          'Focus on audio content - trending in your niche',
          'Collaborate with creators in similar demographics'
        ],
        optimalPostTimes: ['18:00', '19:30', '21:00'],
        trendingTopics: ['AI Music Generation', 'Live Streaming', 'Creator Collaborations', 'NFT Audio'],
        audienceGrowthForecast: [850000, 920000, 995000, 1080000, 1175000, 1280000],
        revenueProjection: 45600,
        riskFactors: ['Seasonal content dip in summer', 'Increasing competition in music niche'],
        opportunities: ['Untapped audience in Latin America', 'Gaming content crossover potential']
      });

    } catch (error) {
      console.error('Failed to fetch analytics data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [creatorId, timeRange]);

  const fetchRealTimeMetrics = useCallback(async () => {
    if (!enableRealTime) return;
    
    // Simulate real-time metrics updates
    setRealTimeMetrics({
      liveViewers: Math.floor(Math.random() * 1000) + 500,
      recentEngagement: Math.floor(Math.random() * 50) + 70,
      newFollowers: Math.floor(Math.random() * 10) + 5
    });
  }, [enableRealTime]);

  // ================ COMPUTED VALUES ================
  const engagementProgress = useMemo(() => {
    return calculateCircleProgress(analytics.engagement);
  }, [analytics.engagement]);

  const topPerformingContent = useMemo(() => {
    return contentPerformance
      .sort((a, b) => b.aiScore - a.aiScore)
      .slice(0, 5);
  }, [contentPerformance]);

  // ================ EVENT HANDLERS ================
  const handleInsightAction = useCallback((action: string, data: any) => {
    onInsightAction?.(action, data);
  }, [onInsightAction]);

  // ================ RENDER ================
  return (
    <ThemeProvider theme={theme}>
      <AnalyticsDashboard className={className}>
        {/* Total Views */}
        <AnalyticsCard featured>
          <MetricHeader>
            <MetricIcon bgColor="rgba(34, 197, 94, 0.2)">👁️</MetricIcon>
            <MetricTitle>Total Views</MetricTitle>
          </MetricHeader>
          <MetricValue color="white">{formatNumber(analytics.views)}</MetricValue>
          <MetricChange positive={true}>
            ↗ +24.8% vs last {timeRange}
          </MetricChange>
          {realTimeMetrics && (
            <div style={{ marginTop: '12px', fontSize: '14px', opacity: 0.9 }}>
              🔴 {realTimeMetrics.liveViewers} watching now
            </div>
          )}
        </AnalyticsCard>

        {/* Engagement Rate */}
        <AnalyticsCard>
          <MetricHeader>
            <MetricIcon bgColor="rgba(59, 130, 246, 0.2)">💖</MetricIcon>
            <MetricTitle>Engagement Rate</MetricTitle>
          </MetricHeader>
          <ChartContainer>
            <ProgressRing width="120" height="120">
              <circle
                cx="60"
                cy="60"
                r="50"
                stroke="#e2e8f0"
                strokeWidth="8"
              />
              <circle
                cx="60"
                cy="60"
                r="50"
                stroke="#3b82f6"
                strokeWidth="8"
                strokeDasharray={engagementProgress.strokeDasharray}
                strokeDashoffset={engagementProgress.strokeDashoffset}
              />
            </ProgressRing>
            <div style={{ position: 'absolute', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: '800' }}>
                {analytics.engagement}%
              </div>
              <div style={{ fontSize: '12px', color: theme.colors.textSecondary }}>
                Engagement
              </div>
            </div>
          </ChartContainer>
          <MetricChange positive={true}>
            ↗ +5.2% improvement
          </MetricChange>
        </AnalyticsCard>

        {/* Unique Visitors */}
        <AnalyticsCard>
          <MetricHeader>
            <MetricIcon bgColor="rgba(139, 92, 246, 0.2)">👥</MetricIcon>
            <MetricTitle>Unique Visitors</MetricTitle>
          </MetricHeader>
          <MetricValue>{formatNumber(analytics.uniqueVisitors)}</MetricValue>
          <MetricChange positive={true}>
            ↗ +18.3% new visitors
          </MetricChange>
          <AIInsightBadge type="positive">
            🤖 High Quality Traffic
          </AIInsightBadge>
        </AnalyticsCard>

        {/* Conversion Rate */}
        <AnalyticsCard>
          <MetricHeader>
            <MetricIcon bgColor="rgba(245, 158, 11, 0.2)">💰</MetricIcon>
            <MetricTitle>Conversion Rate</MetricTitle>
          </MetricHeader>
          <MetricValue>{analytics.conversionRate}%</MetricValue>
          <MetricChange positive={false}>
            ↘ -2.1% from last period
          </MetricChange>
          <AIInsightBadge type="warning">
            🤖 Optimization Needed
          </AIInsightBadge>
        </AnalyticsCard>

        {/* Top Performing Content */}
        <AnalyticsCard fullWidth>
          <MetricHeader>
            <MetricTitle>Top Performing Content</MetricTitle>
            <ActionButton 
              variant="secondary"
              onClick={() => handleInsightAction('viewAll', { type: 'content' })}
            >
              View All
            </ActionButton>
          </MetricHeader>
          <ContentList>
            {topPerformingContent.map((content) => (
              <ContentItem key={content.id}>
                <div>
                  <div style={{ fontWeight: '600', marginBottom: '4px' }}>
                    {content.title}
                  </div>
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                    <span style={{ fontSize: '14px', color: theme.colors.textSecondary }}>
                      {formatNumber(content.views)} views
                    </span>
                    <AIInsightBadge type={content.aiScore > 90 ? 'positive' : 'neutral'}>
                      🤖 AI Score: {content.aiScore}
                    </AIInsightBadge>
                    {content.trending && (
                      <span style={{ fontSize: '12px' }}>🔥 Trending</span>
                    )}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontWeight: '700', color: theme.colors.success }}>
                    ${content.revenue}
                  </div>
                  <div style={{ fontSize: '14px', color: theme.colors.textSecondary }}>
                    {content.engagement}% engagement
                  </div>
                </div>
              </ContentItem>
            ))}
          </ContentList>
        </AnalyticsCard>

        {/* ML Predictions Panel */}
        {showPredictions && mlPredictions && (
          <PredictionPanel>
            <h3 style={{ margin: '0 0 20px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
              🤖 AI-Powered Insights & Predictions
            </h3>
            
            <div style={{ display: 'grid', gap: '16px' }}>
              <div>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', opacity: 0.8 }}>
                  NEXT MONTH FORECAST
                </h4>
                <div style={{ fontSize: '24px', fontWeight: '700' }}>
                  {formatNumber(mlPredictions.nextMonthViews)} views
                </div>
              </div>
              
              <div>
                <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', opacity: 0.8 }}>
                  AI RECOMMENDATIONS
                </h4>
                {mlPredictions.contentRecommendations.slice(0, 3).map((rec, index) => (
                  <div key={index} style={{ fontSize: '14px', marginBottom: '4px', opacity: 0.9 }}>
                    • {rec}
                  </div>
                ))}
              </div>
              
              <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
                <ActionButton 
                  variant="primary"
                  onClick={() => handleInsightAction('applyRecommendations', mlPredictions)}
                >
                  Apply AI Recommendations
                </ActionButton>
                <ActionButton 
                  onClick={() => handleInsightAction('viewFullReport', mlPredictions)}
                >
                  Full Report
                </ActionButton>
              </div>
            </div>
          </PredictionPanel>
        )}

        {/* Audience Quality Score */}
        {audienceInsights && (
          <AnalyticsCard>
            <MetricHeader>
              <MetricIcon bgColor="rgba(34, 197, 94, 0.2)">🎯</MetricIcon>
              <MetricTitle>Audience Quality</MetricTitle>
            </MetricHeader>
            <MetricValue>{audienceInsights.audienceQuality}%</MetricValue>
            <MetricChange positive={true}>
              ↗ High authenticity score
            </MetricChange>
            <AIInsightBadge type="positive">
              🤖 Premium Audience
            </AIInsightBadge>
          </AnalyticsCard>
        )}
      </AnalyticsDashboard>
    </ThemeProvider>
  );
};

// ==================== EXPORTS ====================
export default CreatorAnalyticsTemplate;

export type {
  CreatorAnalyticsProps,
  AnalyticsData,
  ContentPerformance,
  AudienceInsights,
  MLPredictions
};