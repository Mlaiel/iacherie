/**
 * Mobile Analytics - Advanced Analytics Dashboard
 * 
 * Comprehensive mobile analytics interface providing insights into
 * content performance, user engagement, and revenue metrics.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️  CRITICAL LEGAL NOTICE:
 * This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
 * Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
 * Contact: mlaiel@live.de for licensing inquiries.
 */

import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import LinearGradient from 'react-native-linear-gradient';
import { AnalyticsProps, MobileAnalyticsData } from './types';

const { width } = Dimensions.get('window');

const MobileAnalytics: React.FC<AnalyticsProps> = ({
  data,
  timeframe,
  onTimeframeChange,
  onExportData,
  style,
  testID,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<'usage' | 'performance' | 'engagement' | 'revenue'>('usage');

  const formatNumber = useCallback((num: number) => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  }, []);

  const formatBytes = useCallback((bytes: number) => {
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
  }, []);

  const formatCurrency = useCallback((amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
    }).format(amount);
  }, []);

  const renderTimeframeSelector = () => (
    <View style={styles.timeframeContainer}>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.timeframeScroll}
      >
        {(['24h', '7d', '30d', '90d'] as const).map((period) => (
          <TouchableOpacity
            key={period}
            style={[
              styles.timeframeButton,
              timeframe === period && styles.activeTimeframeButton,
            ]}
            onPress={() => onTimeframeChange(period)}
          >
            <Text
              style={[
                styles.timeframeText,
                timeframe === period && styles.activeTimeframeText,
              ]}
            >
              {period}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );

  const renderCategorySelector = () => (
    <View style={styles.categoryContainer}>
      {(['usage', 'performance', 'engagement', 'revenue'] as const).map((category) => (
        <TouchableOpacity
          key={category}
          style={[
            styles.categoryButton,
            selectedCategory === category && styles.activeCategoryButton,
          ]}
          onPress={() => setSelectedCategory(category)}
        >
          <Icon
            name={
              category === 'usage'
                ? 'chart-line'
                : category === 'performance'
                ? 'speedometer'
                : category === 'engagement'
                ? 'heart'
                : 'currency-eur'
            }
            size={16}
            color={selectedCategory === category ? '#ffffff' : '#94a3b8'}
          />
          <Text
            style={[
              styles.categoryText,
              selectedCategory === category && styles.activeCategoryText,
            ]}
          >
            {category.charAt(0).toUpperCase() + category.slice(1)}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  const renderMetricCard = (
    title: string,
    value: string | number,
    subtitle: string,
    icon: string,
    color: string,
    trend?: 'up' | 'down' | 'stable'
  ) => (
    <View style={styles.metricCard}>
      <LinearGradient
        colors={[color, `${color}80`]}
        style={styles.metricGradient}
      >
        <View style={styles.metricHeader}>
          <Icon name={icon} size={20} color="#ffffff" />
          {trend && (
            <Icon
              name={
                trend === 'up'
                  ? 'trending-up'
                  : trend === 'down'
                  ? 'trending-down'
                  : 'trending-neutral'
              }
              size={16}
              color={
                trend === 'up'
                  ? '#10b981'
                  : trend === 'down'
                  ? '#ef4444'
                  : '#6b7280'
              }
            />
          )}
        </View>
        <Text style={styles.metricValue}>{value}</Text>
        <Text style={styles.metricTitle}>{title}</Text>
        <Text style={styles.metricSubtitle}>{subtitle}</Text>
      </LinearGradient>
    </View>
  );

  const renderUsageMetrics = () => (
    <View style={styles.metricsGrid}>
      {renderMetricCard(
        'Active Time',
        `${Math.round(data.usage.dailyActiveTime / 60)}m`,
        'Average daily usage',
        'clock',
        '#3b82f6',
        'up'
      )}
      {renderMetricCard(
        'Screen Views',
        formatNumber(Object.values(data.usage.screenViews).reduce((a, b) => a + b, 0)),
        'Total views',
        'eye',
        '#10b981',
        'up'
      )}
      {renderMetricCard(
        'Features Used',
        data.usage.featuresUsed.length.toString(),
        'Unique features',
        'application',
        '#8b5cf6',
        'stable'
      )}
      {renderMetricCard(
        'App Stability',
        `${((1 - data.usage.crashes / 100) * 100).toFixed(1)}%`,
        `${data.usage.crashes} crashes`,
        'shield-check',
        data.usage.crashes > 5 ? '#ef4444' : '#10b981',
        data.usage.crashes > 5 ? 'down' : 'up'
      )}
    </View>
  );

  const renderPerformanceMetrics = () => (
    <View style={styles.metricsGrid}>
      {renderMetricCard(
        'Load Times',
        `${Math.round(Object.values(data.performance.loadTimes).reduce((a, b) => a + b, 0) / Object.keys(data.performance.loadTimes).length)}ms`,
        'Average load time',
        'speedometer',
        '#f59e0b',
        'down'
      )}
      {renderMetricCard(
        'Memory Usage',
        formatBytes(data.performance.memoryUsage),
        'Average memory',
        'memory',
        '#ef4444',
        'up'
      )}
      {renderMetricCard(
        'Battery Impact',
        `${data.performance.batteryImpact.toFixed(1)}%`,
        'Battery usage',
        'battery',
        data.performance.batteryImpact > 10 ? '#ef4444' : '#10b981',
        data.performance.batteryImpact > 10 ? 'up' : 'down'
      )}
      {renderMetricCard(
        'Network Usage',
        formatBytes(data.performance.networkUsage),
        'Data consumed',
        'wifi',
        '#3b82f6',
        'stable'
      )}
    </View>
  );

  const renderEngagementMetrics = () => (
    <View style={styles.metricsGrid}>
      {renderMetricCard(
        'Content Created',
        data.engagement.contentCreated.toString(),
        'Total uploads',
        'plus-circle',
        '#10b981',
        'up'
      )}
      {renderMetricCard(
        'Collaborations',
        data.engagement.collaborations.toString(),
        'Active projects',
        'account-group',
        '#8b5cf6',
        'up'
      )}
      {renderMetricCard(
        'Challenges',
        data.engagement.challengesCompleted.toString(),
        'Completed',
        'trophy',
        '#f59e0b',
        'up'
      )}
      {renderMetricCard(
        'Social Shares',
        data.engagement.socialShares.toString(),
        'Total shares',
        'share',
        '#3b82f6',
        'up'
      )}
    </View>
  );

  const renderRevenueMetrics = () => (
    <View style={styles.metricsGrid}>
      {renderMetricCard(
        'Total Earnings',
        formatCurrency(data.revenue.earnings),
        `${timeframe} revenue`,
        'currency-eur',
        '#10b981',
        'up'
      )}
      {renderMetricCard(
        'Transactions',
        data.revenue.transactions.toString(),
        'Completed sales',
        'credit-card',
        '#3b82f6',
        'up'
      )}
      {renderMetricCard(
        'Conversion Rate',
        `${(data.revenue.conversionRate * 100).toFixed(1)}%`,
        'Visitor to customer',
        'chart-line',
        data.revenue.conversionRate > 0.05 ? '#10b981' : '#f59e0b',
        data.revenue.conversionRate > 0.05 ? 'up' : 'down'
      )}
      {renderMetricCard(
        'Avg. Revenue',
        formatCurrency(data.revenue.earnings / Math.max(data.revenue.transactions, 1)),
        'Per transaction',
        'calculator',
        '#8b5cf6',
        'stable'
      )}
    </View>
  );

  const renderTopScreens = () => {
    const topScreens = Object.entries(data.usage.screenViews)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5);

    return (
      <View style={styles.listContainer}>
        <Text style={styles.listTitle}>Top Screens</Text>
        {topScreens.map(([screen, views], index) => (
          <View key={screen} style={styles.listItem}>
            <View style={styles.listRank}>
              <Text style={styles.listRankText}>#{index + 1}</Text>
            </View>
            <Text style={styles.listItemText}>{screen}</Text>
            <Text style={styles.listItemValue}>{formatNumber(views)} views</Text>
          </View>
        ))}
      </View>
    );
  };

  const renderTopFeatures = () => (
    <View style={styles.listContainer}>
      <Text style={styles.listTitle}>Most Used Features</Text>
      {data.usage.featuresUsed.slice(0, 5).map((feature, index) => (
        <View key={feature} style={styles.listItem}>
          <View style={styles.listRank}>
            <Text style={styles.listRankText}>#{index + 1}</Text>
          </View>
          <Text style={styles.listItemText}>{feature}</Text>
          <Icon name="check-circle" size={16} color="#10b981" />
        </View>
      ))}
    </View>
  );

  const renderCategoryContent = () => {
    switch (selectedCategory) {
      case 'usage':
        return (
          <>
            {renderUsageMetrics()}
            {renderTopScreens()}
            {renderTopFeatures()}
          </>
        );
      case 'performance':
        return renderPerformanceMetrics();
      case 'engagement':
        return renderEngagementMetrics();
      case 'revenue':
        return renderRevenueMetrics();
      default:
        return renderUsageMetrics();
    }
  };

  return (
    <SafeAreaView style={[styles.container, style]} testID={testID}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Analytics</Text>
        <TouchableOpacity
          style={styles.exportButton}
          onPress={() => {
            if (onExportData) {
              onExportData();
            } else {
              Alert.alert('Export', 'Analytics data export feature coming soon!');
            }
          }}
        >
          <Icon name="download" size={20} color="#ffffff" />
        </TouchableOpacity>
      </View>

      {/* Timeframe Selector */}
      {renderTimeframeSelector()}

      {/* Category Selector */}
      {renderCategorySelector()}

      {/* Content */}
      <ScrollView
        style={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {renderCategoryContent()}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#1e293b',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  exportButton: {
    padding: 8,
  },
  timeframeContainer: {
    paddingVertical: 8,
  },
  timeframeScroll: {
    paddingHorizontal: 16,
  },
  timeframeButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#1e293b',
    borderRadius: 20,
    marginRight: 8,
  },
  activeTimeframeButton: {
    backgroundColor: '#3b82f6',
  },
  timeframeText: {
    fontSize: 14,
    color: '#94a3b8',
    fontWeight: '600',
  },
  activeTimeframeText: {
    color: '#ffffff',
  },
  categoryContainer: {
    flexDirection: 'row',
    backgroundColor: '#1e293b',
    marginHorizontal: 16,
    marginVertical: 8,
    borderRadius: 12,
    padding: 4,
  },
  categoryButton: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 8,
    borderRadius: 8,
  },
  activeCategoryButton: {
    backgroundColor: '#3b82f6',
  },
  categoryText: {
    fontSize: 12,
    color: '#94a3b8',
    marginLeft: 4,
    fontWeight: '600',
  },
  activeCategoryText: {
    color: '#ffffff',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  metricCard: {
    width: '48%',
    marginBottom: 12,
    borderRadius: 12,
    overflow: 'hidden',
  },
  metricGradient: {
    padding: 16,
  },
  metricHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  metricTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 2,
  },
  metricSubtitle: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.8)',
  },
  listContainer: {
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  listTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 12,
  },
  listItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
  },
  listRank: {
    width: 30,
    alignItems: 'center',
  },
  listRankText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#6b7280',
  },
  listItemText: {
    flex: 1,
    fontSize: 14,
    color: '#e2e8f0',
    marginLeft: 12,
  },
  listItemValue: {
    fontSize: 12,
    color: '#94a3b8',
    fontWeight: '600',
  },
});

export default MobileAnalytics;