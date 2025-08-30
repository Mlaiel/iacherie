/**
 * Mobile Gamification App - Enterprise-Grade Gamification System
 * 
 * Comprehensive mobile gamification interface providing challenges, achievements,
 * leaderboards, and reward systems for content creators on the Ainflue platform.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️  CRITICAL LEGAL NOTICE:
 * This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
 * Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
 * Contact: mlaiel@live.de for licensing inquiries.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  Animated,
  Alert,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import LinearGradient from 'react-native-linear-gradient';

import { GamificationProps, Challenge, LeaderboardEntry } from './types';

const { width, height } = Dimensions.get('window');

interface MobileGamificationAppProps extends GamificationProps {
  onNavigateToChallenge?: (challengeId: string) => void;
  onNavigateToLeaderboard?: () => void;
  onClaimReward?: (rewardId: string) => void;
  theme?: 'light' | 'dark';
}

const MobileGamificationApp: React.FC<MobileGamificationAppProps> = ({
  challenges,
  leaderboard,
  userStats,
  onChallengeAccept,
  onNavigateToChallenge,
  onNavigateToLeaderboard,
  onClaimReward,
  theme = 'dark',
  style,
  testID,
}) => {
  const [refreshing, setRefreshing] = useState(false);
  const [selectedTab, setSelectedTab] = useState<'overview' | 'challenges' | 'achievements'>('overview');
  const [animatedValue] = useState(new Animated.Value(0));

  useEffect(() => {
    // Animate entrance
    Animated.timing(animatedValue, {
      toValue: 1,
      duration: 800,
      useNativeDriver: true,
    }).start();
  }, [animatedValue]);

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    // Simulate refresh delay
    setTimeout(() => setRefreshing(false), 2000);
  }, []);

  const handleChallengePress = useCallback((challenge: Challenge) => {
    Alert.alert(
      challenge.title,
      challenge.description,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Accept Challenge',
          onPress: () => {
            onChallengeAccept?.(challenge.id);
            onNavigateToChallenge?.(challenge.id);
          },
        },
      ]
    );
  }, [onChallengeAccept, onNavigateToChallenge]);

  const getLevelProgress = () => {
    const currentLevelPoints = userStats.points % 1000;
    return currentLevelPoints / 1000;
  };

  const getStreakDays = () => {
    return Math.floor(Math.random() * 30) + 1; // Mock streak calculation
  };

  const renderOverview = () => (
    <ScrollView
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
      }
    >
      {/* User Stats Card */}
      <LinearGradient
        colors={theme === 'dark' ? ['#1e40af', '#3b82f6'] : ['#60a5fa', '#3b82f6']}
        style={styles.statsCard}
      >
        <View style={styles.statsHeader}>
          <View style={styles.levelContainer}>
            <Text style={styles.levelText}>Level {userStats.level}</Text>
            <Text style={styles.pointsText}>{userStats.points.toLocaleString()} XP</Text>
          </View>
          <View style={styles.rankContainer}>
            <Icon name="trophy" size={24} color="#FFD700" />
            <Text style={styles.rankText}>#{userStats.rank}</Text>
          </View>
        </View>

        <View style={styles.progressContainer}>
          <Text style={styles.progressLabel}>Progress to Level {userStats.level + 1}</Text>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                { width: `${getLevelProgress() * 100}%` },
              ]}
            />
          </View>
          <Text style={styles.progressText}>
            {Math.floor(getLevelProgress() * 100)}% Complete
          </Text>
        </View>
      </LinearGradient>

      {/* Quick Stats */}
      <View style={styles.quickStatsContainer}>
        <View style={styles.quickStatItem}>
          <Icon name="flash" size={32} color="#10b981" />
          <Text style={styles.quickStatValue}>{getStreakDays()}</Text>
          <Text style={styles.quickStatLabel}>Day Streak</Text>
        </View>
        <View style={styles.quickStatItem}>
          <Icon name="target" size={32} color="#f59e0b" />
          <Text style={styles.quickStatValue}>{userStats.completedChallenges}</Text>
          <Text style={styles.quickStatLabel}>Challenges</Text>
        </View>
        <View style={styles.quickStatItem}>
          <Icon name="star" size={32} color="#8b5cf6" />
          <Text style={styles.quickStatValue}>
            {Math.floor(userStats.points / 100)}
          </Text>
          <Text style={styles.quickStatLabel}>Achievements</Text>
        </View>
      </View>

      {/* Active Challenges Preview */}
      <View style={styles.sectionContainer}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Active Challenges</Text>
          <TouchableOpacity onPress={() => setSelectedTab('challenges')}>
            <Text style={styles.seeAllText}>See All</Text>
          </TouchableOpacity>
        </View>
        {challenges.slice(0, 3).map((challenge) => (
          <TouchableOpacity
            key={challenge.id}
            style={styles.challengePreviewCard}
            onPress={() => handleChallengePress(challenge)}
          >
            <View style={styles.challengeHeader}>
              <Text style={styles.challengeTitle}>{challenge.title}</Text>
              <View style={[styles.difficultyBadge, styles[`${challenge.difficulty}Badge`]]}>
                <Text style={styles.difficultyText}>{challenge.difficulty.toUpperCase()}</Text>
              </View>
            </View>
            <Text style={styles.challengeDescription} numberOfLines={2}>
              {challenge.description}
            </Text>
            <View style={styles.challengeProgress}>
              <View style={styles.progressBar}>
                <View
                  style={[
                    styles.progressFill,
                    { width: `${Math.min(challenge.progress, 100)}%` },
                  ]}
                />
              </View>
              <Text style={styles.progressPercentage}>
                {Math.floor(challenge.progress)}%
              </Text>
            </View>
            <View style={styles.challengeReward}>
              <Icon name="star-circle" size={16} color="#FFD700" />
              <Text style={styles.rewardText}>+{challenge.rewards.points} XP</Text>
            </View>
          </TouchableOpacity>
        ))}
      </View>

      {/* Leaderboard Preview */}
      <View style={styles.sectionContainer}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Leaderboard</Text>
          <TouchableOpacity onPress={onNavigateToLeaderboard}>
            <Text style={styles.seeAllText}>View Full</Text>
          </TouchableOpacity>
        </View>
        {leaderboard.slice(0, 5).map((entry) => (
          <View key={entry.userId} style={styles.leaderboardEntry}>
            <View style={styles.rankPosition}>
              <Text style={styles.rankNumber}>#{entry.rank}</Text>
              {entry.rank <= 3 && (
                <Icon
                  name={entry.rank === 1 ? 'trophy' : entry.rank === 2 ? 'medal' : 'trophy-outline'}
                  size={20}
                  color={entry.rank === 1 ? '#FFD700' : entry.rank === 2 ? '#C0C0C0' : '#CD7F32'}
                />
              )}
            </View>
            <Text style={styles.leaderboardName}>{entry.username}</Text>
            <Text style={styles.leaderboardScore}>
              {entry.score.toLocaleString()} XP
            </Text>
            <Icon
              name={
                entry.trend === 'up'
                  ? 'trending-up'
                  : entry.trend === 'down'
                  ? 'trending-down'
                  : 'trending-neutral'
              }
              size={16}
              color={
                entry.trend === 'up'
                  ? '#10b981'
                  : entry.trend === 'down'
                  ? '#ef4444'
                  : '#6b7280'
              }
            />
          </View>
        ))}
      </View>
    </ScrollView>
  );

  const renderTabContent = () => {
    switch (selectedTab) {
      case 'overview':
        return renderOverview();
      case 'challenges':
        return (
          <View style={styles.tabPlaceholder}>
            <Icon name="target" size={64} color="#6b7280" />
            <Text style={styles.placeholderText}>
              Challenge details will be rendered here
            </Text>
          </View>
        );
      case 'achievements':
        return (
          <View style={styles.tabPlaceholder}>
            <Icon name="trophy" size={64} color="#6b7280" />
            <Text style={styles.placeholderText}>
              Achievement details will be rendered here
            </Text>
          </View>
        );
      default:
        return renderOverview();
    }
  };

  return (
    <SafeAreaView style={[styles.container, style]} testID={testID}>
      <Animated.View
        style={[
          styles.content,
          {
            opacity: animatedValue,
            transform: [
              {
                translateY: animatedValue.interpolate({
                  inputRange: [0, 1],
                  outputRange: [50, 0],
                }),
              },
            ],
          },
        ]}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Gamification</Text>
          <TouchableOpacity style={styles.settingsButton}>
            <Icon name="cog" size={24} color={theme === 'dark' ? '#ffffff' : '#000000'} />
          </TouchableOpacity>
        </View>

        {/* Tab Navigation */}
        <View style={styles.tabContainer}>
          {(['overview', 'challenges', 'achievements'] as const).map((tab) => (
            <TouchableOpacity
              key={tab}
              style={[
                styles.tabButton,
                selectedTab === tab && styles.activeTabButton,
              ]}
              onPress={() => setSelectedTab(tab)}
            >
              <Text
                style={[
                  styles.tabText,
                  selectedTab === tab && styles.activeTabText,
                ]}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Content */}
        <View style={styles.tabContent}>{renderTabContent()}</View>
      </Animated.View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  content: {
    flex: 1,
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
  settingsButton: {
    padding: 8,
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#1e293b',
    marginHorizontal: 16,
    marginTop: 16,
    borderRadius: 12,
    padding: 4,
  },
  tabButton: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderRadius: 8,
  },
  activeTabButton: {
    backgroundColor: '#3b82f6',
  },
  tabText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#94a3b8',
  },
  activeTabText: {
    color: '#ffffff',
  },
  tabContent: {
    flex: 1,
    marginTop: 16,
  },
  statsCard: {
    marginHorizontal: 16,
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
  },
  statsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  levelContainer: {
    flex: 1,
  },
  levelText: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  pointsText: {
    fontSize: 16,
    color: '#e2e8f0',
    marginTop: 4,
  },
  rankContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  rankText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginLeft: 8,
  },
  progressContainer: {
    marginTop: 8,
  },
  progressLabel: {
    fontSize: 14,
    color: '#e2e8f0',
    marginBottom: 8,
  },
  progressBar: {
    height: 8,
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#ffffff',
    borderRadius: 4,
  },
  progressText: {
    fontSize: 12,
    color: '#e2e8f0',
    marginTop: 4,
    textAlign: 'right',
  },
  quickStatsContainer: {
    flexDirection: 'row',
    marginHorizontal: 16,
    marginBottom: 16,
  },
  quickStatItem: {
    flex: 1,
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  quickStatValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginTop: 8,
  },
  quickStatLabel: {
    fontSize: 12,
    color: '#94a3b8',
    marginTop: 4,
  },
  sectionContainer: {
    marginHorizontal: 16,
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  seeAllText: {
    fontSize: 14,
    color: '#3b82f6',
    fontWeight: '600',
  },
  challengePreviewCard: {
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  challengeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  challengeTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    flex: 1,
  },
  difficultyBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    marginLeft: 12,
  },
  easyBadge: {
    backgroundColor: '#10b981',
  },
  mediumBadge: {
    backgroundColor: '#f59e0b',
  },
  hardBadge: {
    backgroundColor: '#ef4444',
  },
  expertBadge: {
    backgroundColor: '#8b5cf6',
  },
  difficultyText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  challengeDescription: {
    fontSize: 14,
    color: '#94a3b8',
    marginBottom: 12,
  },
  challengeProgress: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  progressPercentage: {
    fontSize: 12,
    color: '#94a3b8',
    marginLeft: 8,
    minWidth: 35,
  },
  challengeReward: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  rewardText: {
    fontSize: 12,
    color: '#FFD700',
    fontWeight: '600',
    marginLeft: 4,
  },
  leaderboardEntry: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1e293b',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  rankPosition: {
    flexDirection: 'row',
    alignItems: 'center',
    width: 60,
  },
  rankNumber: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#ffffff',
    marginRight: 8,
  },
  leaderboardName: {
    flex: 1,
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
    marginLeft: 12,
  },
  leaderboardScore: {
    fontSize: 14,
    color: '#94a3b8',
    marginRight: 12,
  },
  tabPlaceholder: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  placeholderText: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    marginTop: 16,
  },
});

export default MobileGamificationApp;