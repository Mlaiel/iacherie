/**
 * Analytics Screen - Mobile analytics interface
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  StatusBar,
  SafeAreaView,
  Dimensions,
} from 'react-native';

const { width } = Dimensions.get('window');

interface AnalyticsData {
  revenue: { month: string; amount: number }[];
  contentViews: { month: string; views: number }[];
  platformDistribution: { platform: string; percentage: number }[];
  topContent: { name: string; views: number; revenue: number }[];
}

export const AnalyticsScreen: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [timeframe, setTimeframe] = useState<'7d' | '30d' | '90d' | '1y'>('30d');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalyticsData();
  }, [timeframe]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setData({
        revenue: [
          { month: 'Jan', amount: 12000 },
          { month: 'Feb', amount: 15000 },
          { month: 'Mar', amount: 18000 },
          { month: 'Apr', amount: 22000 },
          { month: 'May', amount: 19000 },
          { month: 'Jun', amount: 24580 }
        ],
        contentViews: [
          { month: 'Jan', views: 125000 },
          { month: 'Feb', views: 145000 },
          { month: 'Mar', views: 162000 },
          { month: 'Apr', views: 198000 },
          { month: 'May', views: 178000 },
          { month: 'Jun', views: 215000 }
        ],
        platformDistribution: [
          { platform: 'YouTube', percentage: 45 },
          { platform: 'Spotify', percentage: 25 },
          { platform: 'SoundCloud', percentage: 15 },
          { platform: 'Apple Music', percentage: 10 },
          { platform: 'Others', percentage: 5 }
        ],
        topContent: [
          { name: 'Track_Final_Master.mp3', views: 125000, revenue: 3200 },
          { name: 'Album_Intro_Video.mp4', views: 98000, revenue: 2800 },
          { name: 'Behind_Scenes.mp4', views: 87000, revenue: 2100 },
          { name: 'Acoustic_Version.mp3', views: 76000, revenue: 1900 }
        ]
      });
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const TimeframeSelector = () => (
    <View style={styles.timeframeContainer}>
      {(['7d', '30d', '90d', '1y'] as const).map((period) => (
        <TouchableOpacity
          key={period}
          style={[
            styles.timeframeButton,
            timeframe === period && styles.timeframeButtonActive
          ]}
          onPress={() => setTimeframe(period)}
        >
          <Text style={[
            styles.timeframeText,
            timeframe === period && styles.timeframeTextActive
          ]}>
            {period}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  const RevenueChart = () => {
    if (!data) return null;
    
    const maxRevenue = Math.max(...data.revenue.map(r => r.amount));
    
    return (
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>Revenue Trend</Text>
        <View style={styles.chart}>
          {data.revenue.map((item, index) => (
            <View key={index} style={styles.chartItem}>
              <View
                style={[
                  styles.chartBar,
                  { height: (item.amount / maxRevenue) * 120 }
                ]}
              />
              <Text style={styles.chartLabel}>{item.month}</Text>
              <Text style={styles.chartValue}>${(item.amount / 1000).toFixed(1)}k</Text>
            </View>
          ))}
        </View>
      </View>
    );
  };

  const PlatformDistribution = () => {
    if (!data) return null;
    
    return (
      <View style={styles.platformContainer}>
        <Text style={styles.sectionTitle}>Platform Distribution</Text>
        {data.platformDistribution.map((platform, index) => (
          <View key={index} style={styles.platformItem}>
            <Text style={styles.platformName}>{platform.platform}</Text>
            <View style={styles.platformProgress}>
              <View
                style={[
                  styles.platformBar,
                  { width: `${platform.percentage}%` }
                ]}
              />
            </View>
            <Text style={styles.platformPercentage}>{platform.percentage}%</Text>
          </View>
        ))}
      </View>
    );
  };

  const TopContent = () => {
    if (!data) return null;
    
    return (
      <View style={styles.topContentContainer}>
        <Text style={styles.sectionTitle}>Top Performing Content</Text>
        {data.topContent.map((content, index) => (
          <View key={index} style={styles.contentItem}>
            <View style={styles.contentInfo}>
              <Text style={styles.contentName}>{content.name}</Text>
              <Text style={styles.contentStats}>
                {(content.views / 1000).toFixed(1)}k views • ${content.revenue}
              </Text>
            </View>
            <View style={styles.contentRank}>
              <Text style={styles.rankText}>#{index + 1}</Text>
            </View>
          </View>
        ))}
      </View>
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading analytics...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
      
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.title}>Analytics</Text>
          <Text style={styles.subtitle}>Track your content performance</Text>
        </View>

        <TimeframeSelector />
        <RevenueChart />
        <PlatformDistribution />
        <TopContent />
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#6B7280',
  },
  scrollView: {
    flex: 1,
    paddingHorizontal: 16,
  },
  header: {
    paddingVertical: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
  },
  timeframeContainer: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 4,
    marginBottom: 24,
  },
  timeframeButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  timeframeButtonActive: {
    backgroundColor: '#3B82F6',
  },
  timeframeText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
  },
  timeframeTextActive: {
    color: '#FFFFFF',
  },
  chartContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
  },
  chartTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 16,
  },
  chart: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    height: 160,
  },
  chartItem: {
    alignItems: 'center',
    flex: 1,
  },
  chartBar: {
    backgroundColor: '#3B82F6',
    width: 20,
    borderRadius: 4,
    marginBottom: 8,
  },
  chartLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 4,
  },
  chartValue: {
    fontSize: 11,
    color: '#374151',
    fontWeight: '600',
  },
  platformContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 16,
  },
  platformItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  platformName: {
    flex: 1,
    fontSize: 14,
    color: '#374151',
    fontWeight: '500',
  },
  platformProgress: {
    flex: 2,
    height: 8,
    backgroundColor: '#E5E7EB',
    borderRadius: 4,
    marginHorizontal: 12,
  },
  platformBar: {
    height: '100%',
    backgroundColor: '#3B82F6',
    borderRadius: 4,
  },
  platformPercentage: {
    fontSize: 14,
    color: '#6B7280',
    fontWeight: '600',
    minWidth: 35,
    textAlign: 'right',
  },
  topContentContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
  },
  contentItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  contentInfo: {
    flex: 1,
  },
  contentName: {
    fontSize: 16,
    color: '#111827',
    fontWeight: '500',
    marginBottom: 4,
  },
  contentStats: {
    fontSize: 14,
    color: '#6B7280',
  },
  contentRank: {
    backgroundColor: '#F3F4F6',
    borderRadius: 12,
    width: 24,
    height: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  rankText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#374151',
  },
});

export default AnalyticsScreen;