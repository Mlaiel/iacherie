/**
 * Mobile Leaderboards - Competitive Ranking System
 * 
 * Advanced mobile leaderboard interface showcasing user rankings,
 * achievements, and competitive analytics for content creators.
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
  RefreshControl,
  Image,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import LinearGradient from 'react-native-linear-gradient';

import { LeaderboardEntry, BaseMobileComponentProps } from './types';

const { width } = Dimensions.get('window');

interface MobileLeaderboardsProps extends BaseMobileComponentProps {
  leaderboard: LeaderboardEntry[];
  currentUser: LeaderboardEntry;
  timeframe: 'daily' | 'weekly' | 'monthly' | 'all-time';
  category: 'overall' | 'creation' | 'engagement' | 'collaboration';
  onTimeframeChange: (timeframe: string) => void;
  onCategoryChange: (category: string) => void;
  onUserProfile: (userId: string) => void;
  onFollowUser: (userId: string) => void;
  onChallengeUser: (userId: string) => void;
  theme?: 'light' | 'dark';
}

const MobileLeaderboards: React.FC<MobileLeaderboardsProps> = ({
  leaderboard,
  currentUser,
  timeframe,
  category,
  onTimeframeChange,
  onCategoryChange,
  onUserProfile,
  onFollowUser,
  onChallengeUser,
  theme = 'dark',
  style,
  testID,
}) => {
  const [refreshing, setRefreshing] = useState(false);
  const [animatedValues] = useState(
    leaderboard.reduce((acc, entry) => {
      acc[entry.userId] = new Animated.Value(0);
      return acc;
    }, {} as Record<string, Animated.Value>)
  );

  useEffect(() => {
    // Animate leaderboard entries
    leaderboard.forEach((entry, index) => {
      setTimeout(() => {
        Animated.spring(animatedValues[entry.userId], {
          toValue: 1,
          tension: 100,
          friction: 8,
          useNativeDriver: true,
        }).start();
      }, index * 100);
    });
  }, [leaderboard, animatedValues]);

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    // Simulate refresh
    setTimeout(() => setRefreshing(false), 2000);
  }, []);

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1: return 'trophy';
      case 2: return 'medal';
      case 3: return 'trophy-outline';
      default: return null;
    }
  };

  const getRankColor = (rank: number) => {
    switch (rank) {
      case 1: return '#FFD700';
      case 2: return '#C0C0C0';
      case 3: return '#CD7F32';
      default: return '#6b7280';
    }
  };

  const getTrendIcon = (trend: LeaderboardEntry['trend']) => {
    switch (trend) {
      case 'up': return 'trending-up';
      case 'down': return 'trending-down';
      case 'stable': return 'trending-neutral';
      default: return 'trending-neutral';
    }
  };

  const getTrendColor = (trend: LeaderboardEntry['trend']) => {
    switch (trend) {
      case 'up': return '#10b981';
      case 'down': return '#ef4444';
      case 'stable': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const handleUserAction = (userId: string, action: 'profile' | 'follow' | 'challenge') => {
    switch (action) {
      case 'profile':
        onUserProfile(userId);
        break;
      case 'follow':
        onFollowUser(userId);
        break;
      case 'challenge':
        Alert.alert(
          'Challenge User',
          'Send a friendly challenge to compete?',
          [
            { text: 'Cancel', style: 'cancel' },
            { text: 'Send Challenge', onPress: () => onChallengeUser(userId) },
          ]
        );
        break;
    }
  };

  const renderTopThree = () => {
    const topThree = leaderboard.slice(0, 3);
    
    return (
      <View style={styles.podiumContainer}>
        <LinearGradient
          colors={['#1e40af', '#3b82f6']}
          style={styles.podiumGradient}
        >
          {/* Podium Layout */}
          <View style={styles.podium}>
            {/* Second Place */}
            {topThree[1] && (
              <Animated.View
                style={[
                  styles.podiumPosition,
                  styles.secondPlace,
                  {
                    opacity: animatedValues[topThree[1].userId],
                    transform: [
                      {
                        scale: animatedValues[topThree[1].userId]?.interpolate({
                          inputRange: [0, 1],
                          outputRange: [0.8, 1],
                        }) || 1,
                      },
                    ],
                  },
                ]}
              >
                <TouchableOpacity
                  style={styles.podiumUser}
                  onPress={() => handleUserAction(topThree[1].userId, 'profile')}
                >
                  <View style={styles.podiumAvatar}>
                    {topThree[1].avatar ? (
                      <Image source={{ uri: topThree[1].avatar }} style={styles.avatarImage} />
                    ) : (
                      <Icon name="account" size={40} color="#ffffff" />
                    )}
                  </View>
                  <Text style={styles.podiumName} numberOfLines={1}>
                    {topThree[1].username}
                  </Text>
                  <Text style={styles.podiumScore}>
                    {topThree[1].score.toLocaleString()}
                  </Text>
                  <View style={[styles.podiumRank, { backgroundColor: '#C0C0C0' }]}>
                    <Icon name="medal" size={20} color="#ffffff" />
                  </View>
                </TouchableOpacity>
              </Animated.View>
            )}

            {/* First Place */}
            {topThree[0] && (
              <Animated.View
                style={[
                  styles.podiumPosition,
                  styles.firstPlace,
                  {
                    opacity: animatedValues[topThree[0].userId],
                    transform: [
                      {
                        scale: animatedValues[topThree[0].userId]?.interpolate({
                          inputRange: [0, 1],
                          outputRange: [0.8, 1],
                        }) || 1,
                      },
                    ],
                  },
                ]}
              >
                <TouchableOpacity
                  style={styles.podiumUser}
                  onPress={() => handleUserAction(topThree[0].userId, 'profile')}
                >
                  <View style={[styles.podiumAvatar, styles.winnerAvatar]}>
                    {topThree[0].avatar ? (
                      <Image source={{ uri: topThree[0].avatar }} style={styles.avatarImage} />
                    ) : (
                      <Icon name="account" size={50} color="#ffffff" />
                    )}
                    <View style={styles.crownContainer}>
                      <Icon name="crown" size={24} color="#FFD700" />
                    </View>
                  </View>
                  <Text style={[styles.podiumName, styles.winnerName]} numberOfLines={1}>
                    {topThree[0].username}
                  </Text>
                  <Text style={[styles.podiumScore, styles.winnerScore]}>
                    {topThree[0].score.toLocaleString()}
                  </Text>
                  <View style={[styles.podiumRank, { backgroundColor: '#FFD700' }]}>
                    <Icon name="trophy" size={24} color="#ffffff" />
                  </View>
                </TouchableOpacity>
              </Animated.View>
            )}

            {/* Third Place */}
            {topThree[2] && (
              <Animated.View
                style={[
                  styles.podiumPosition,
                  styles.thirdPlace,
                  {
                    opacity: animatedValues[topThree[2].userId],
                    transform: [
                      {
                        scale: animatedValues[topThree[2].userId]?.interpolate({
                          inputRange: [0, 1],
                          outputRange: [0.8, 1],
                        }) || 1,
                      },
                    ],
                  },
                ]}
              >
                <TouchableOpacity
                  style={styles.podiumUser}
                  onPress={() => handleUserAction(topThree[2].userId, 'profile')}
                >
                  <View style={styles.podiumAvatar}>
                    {topThree[2].avatar ? (
                      <Image source={{ uri: topThree[2].avatar }} style={styles.avatarImage} />
                    ) : (
                      <Icon name="account" size={40} color="#ffffff" />
                    )}
                  </View>
                  <Text style={styles.podiumName} numberOfLines={1}>
                    {topThree[2].username}
                  </Text>
                  <Text style={styles.podiumScore}>
                    {topThree[2].score.toLocaleString()}
                  </Text>
                  <View style={[styles.podiumRank, { backgroundColor: '#CD7F32' }]}>
                    <Icon name="trophy-outline" size={20} color="#ffffff" />
                  </View>
                </TouchableOpacity>
              </Animated.View>
            )}
          </View>
        </LinearGradient>
      </View>
    );
  };

  const renderCurrentUserPosition = () => {
    if (currentUser.rank <= 3) return null;

    return (
      <View style={styles.currentUserContainer}>
        <LinearGradient
          colors={['#059669', '#10b981']}
          style={styles.currentUserGradient}
        >
          <View style={styles.currentUserHeader}>
            <Text style={styles.currentUserLabel}>Your Position</Text>
            <TouchableOpacity
              style={styles.improveButton}
              onPress={() => Alert.alert('Tips', 'Complete more challenges to improve your rank!')}
            >
              <Icon name="trending-up" size={16} color="#ffffff" />
              <Text style={styles.improveButtonText}>Improve</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.currentUserRow}>
            <View style={styles.currentUserRank}>
              <Text style={styles.currentUserRankText}>#{currentUser.rank}</Text>
            </View>
            <View style={styles.currentUserInfo}>
              <Text style={styles.currentUserName}>{currentUser.username}</Text>
              <Text style={styles.currentUserScore}>
                {currentUser.score.toLocaleString()} XP
              </Text>
            </View>
            <View style={styles.currentUserTrend}>
              <Icon
                name={getTrendIcon(currentUser.trend)}
                size={20}
                color={getTrendColor(currentUser.trend)}
              />
            </View>
          </View>
        </LinearGradient>
      </View>
    );
  };

  const renderLeaderboardEntry = (entry: LeaderboardEntry, index: number) => {
    if (index < 3) return null; // Top 3 are shown in podium

    return (
      <Animated.View
        key={entry.userId}
        style={[
          styles.leaderboardEntry,
          {
            opacity: animatedValues[entry.userId] || 1,
            transform: [
              {
                translateX: animatedValues[entry.userId]?.interpolate({
                  inputRange: [0, 1],
                  outputRange: [width, 0],
                }) || 0,
              },
            ],
          },
        ]}
      >
        <TouchableOpacity
          style={styles.entryTouchable}
          onPress={() => handleUserAction(entry.userId, 'profile')}
        >
          <View style={styles.entryRank}>
            <Text style={styles.entryRankText}>#{entry.rank}</Text>
            {getRankIcon(entry.rank) && (
              <Icon
                name={getRankIcon(entry.rank)!}
                size={16}
                color={getRankColor(entry.rank)}
                style={styles.rankIcon}
              />
            )}
          </View>

          <View style={styles.entryAvatar}>
            {entry.avatar ? (
              <Image source={{ uri: entry.avatar }} style={styles.entryAvatarImage} />
            ) : (
              <Icon name="account-circle" size={40} color="#6b7280" />
            )}
          </View>

          <View style={styles.entryInfo}>
            <Text style={styles.entryName}>{entry.username}</Text>
            <View style={styles.entryMeta}>
              <Text style={styles.entryLevel}>Level {entry.level}</Text>
              <Text style={styles.entryAchievements}>
                {entry.achievements.length} achievements
              </Text>
            </View>
          </View>

          <View style={styles.entryScore}>
            <Text style={styles.entryScoreText}>
              {entry.score.toLocaleString()}
            </Text>
            <Text style={styles.entryScoreLabel}>XP</Text>
          </View>

          <View style={styles.entryTrend}>
            <Icon
              name={getTrendIcon(entry.trend)}
              size={16}
              color={getTrendColor(entry.trend)}
            />
          </View>

          <TouchableOpacity
            style={styles.entryActions}
            onPress={() => handleUserAction(entry.userId, 'challenge')}
          >
            <Icon name="sword-cross" size={16} color="#3b82f6" />
          </TouchableOpacity>
        </TouchableOpacity>
      </Animated.View>
    );
  };

  return (
    <SafeAreaView style={[styles.container, style]} testID={testID}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Leaderboards</Text>
        <TouchableOpacity style={styles.filterButton}>
          <Icon name="filter" size={20} color="#ffffff" />
        </TouchableOpacity>
      </View>

      {/* Filters */}
      <View style={styles.filtersContainer}>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.filterScrollView}
        >
          {(['daily', 'weekly', 'monthly', 'all-time'] as const).map((period) => (
            <TouchableOpacity
              key={period}
              style={[
                styles.filterChip,
                timeframe === period && styles.activeFilterChip,
              ]}
              onPress={() => onTimeframeChange(period)}
            >
              <Text
                style={[
                  styles.filterChipText,
                  timeframe === period && styles.activeFilterChipText,
                ]}
              >
                {period.charAt(0).toUpperCase() + period.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      <View style={styles.filtersContainer}>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.filterScrollView}
        >
          {(['overall', 'creation', 'engagement', 'collaboration'] as const).map((cat) => (
            <TouchableOpacity
              key={cat}
              style={[
                styles.filterChip,
                category === cat && styles.activeFilterChip,
              ]}
              onPress={() => onCategoryChange(cat)}
            >
              <Text
                style={[
                  styles.filterChipText,
                  category === cat && styles.activeFilterChipText,
                ]}
              >
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Content */}
      <ScrollView
        style={styles.content}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
        }
      >
        {/* Top 3 Podium */}
        {renderTopThree()}

        {/* Current User Position */}
        {renderCurrentUserPosition()}

        {/* Rest of Leaderboard */}
        <View style={styles.leaderboardList}>
          <Text style={styles.sectionTitle}>Full Rankings</Text>
          {leaderboard.map(renderLeaderboardEntry)}
        </View>
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
  filterButton: {
    padding: 8,
  },
  filtersContainer: {
    paddingVertical: 8,
  },
  filterScrollView: {
    paddingHorizontal: 16,
  },
  filterChip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#1e293b',
    borderRadius: 20,
    marginRight: 8,
  },
  activeFilterChip: {
    backgroundColor: '#3b82f6',
  },
  filterChipText: {
    fontSize: 14,
    color: '#94a3b8',
    fontWeight: '600',
  },
  activeFilterChipText: {
    color: '#ffffff',
  },
  content: {
    flex: 1,
  },
  podiumContainer: {
    marginHorizontal: 16,
    marginTop: 16,
    borderRadius: 16,
    overflow: 'hidden',
  },
  podiumGradient: {
    padding: 20,
  },
  podium: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    justifyContent: 'center',
    height: 200,
  },
  podiumPosition: {
    alignItems: 'center',
    marginHorizontal: 8,
  },
  firstPlace: {
    order: 2,
    height: 160,
  },
  secondPlace: {
    order: 1,
    height: 130,
  },
  thirdPlace: {
    order: 3,
    height: 110,
  },
  podiumUser: {
    alignItems: 'center',
  },
  podiumAvatar: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#334155',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
    position: 'relative',
  },
  winnerAvatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 3,
    borderColor: '#FFD700',
  },
  avatarImage: {
    width: '100%',
    height: '100%',
    borderRadius: 30,
  },
  crownContainer: {
    position: 'absolute',
    top: -12,
    right: -8,
  },
  podiumName: {
    fontSize: 12,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 4,
    textAlign: 'center',
  },
  winnerName: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  podiumScore: {
    fontSize: 10,
    color: '#e2e8f0',
    marginBottom: 8,
  },
  winnerScore: {
    fontSize: 12,
    fontWeight: '600',
  },
  podiumRank: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  currentUserContainer: {
    marginHorizontal: 16,
    marginTop: 16,
    borderRadius: 12,
    overflow: 'hidden',
  },
  currentUserGradient: {
    padding: 16,
  },
  currentUserHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  currentUserLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
  },
  improveButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 16,
  },
  improveButtonText: {
    fontSize: 12,
    color: '#ffffff',
    marginLeft: 4,
    fontWeight: '600',
  },
  currentUserRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  currentUserRank: {
    width: 50,
    alignItems: 'center',
  },
  currentUserRankText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  currentUserInfo: {
    flex: 1,
    marginLeft: 12,
  },
  currentUserName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
  currentUserScore: {
    fontSize: 14,
    color: '#e2e8f0',
  },
  currentUserTrend: {
    alignItems: 'center',
  },
  leaderboardList: {
    marginTop: 16,
    paddingHorizontal: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 16,
  },
  leaderboardEntry: {
    backgroundColor: '#1e293b',
    borderRadius: 12,
    marginBottom: 8,
    overflow: 'hidden',
  },
  entryTouchable: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
  },
  entryRank: {
    width: 50,
    alignItems: 'center',
  },
  entryRankText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  rankIcon: {
    marginTop: 2,
  },
  entryAvatar: {
    marginLeft: 8,
  },
  entryAvatarImage: {
    width: 40,
    height: 40,
    borderRadius: 20,
  },
  entryInfo: {
    flex: 1,
    marginLeft: 12,
  },
  entryName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 2,
  },
  entryMeta: {
    flexDirection: 'row',
  },
  entryLevel: {
    fontSize: 12,
    color: '#94a3b8',
    marginRight: 12,
  },
  entryAchievements: {
    fontSize: 12,
    color: '#94a3b8',
  },
  entryScore: {
    alignItems: 'flex-end',
    marginRight: 12,
  },
  entryScoreText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  entryScoreLabel: {
    fontSize: 10,
    color: '#94a3b8',
  },
  entryTrend: {
    marginRight: 12,
  },
  entryActions: {
    padding: 8,
  },
});

export default MobileLeaderboards;