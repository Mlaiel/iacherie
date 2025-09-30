/**
 * Mobile Gamification App - Touch-Optimized Gamification Interface
 * 
 * Professional gamification system designed specifically for mobile content creators
 * with touch-optimized interfaces, real-time achievement tracking, and social engagement.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Team Specialties:
 * - Lead AI Developer + Backend Senior + ML Engineer
 * - Database Administrator + Security Expert
 * - Microservices Architect + Audio Processing Specialist
 * - DevOps Engineer + IA Prompt Engineer
 * 
 * ⚠️ STRICT COPYRIGHT NOTICE ⚠️
 * This code is proprietary and confidential to Fahed Mlaiel.
 * Any unauthorized use, copying, modification, or distribution
 * without explicit written permission is strictly prohibited.
 * Violations will result in legal action.
 * Contact: mlaiel@live.de for licensing inquiries.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Animated,
  Dimensions,
  Alert,
  RefreshControl,
  StatusBar,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { GamificationEngine } from '../../services/GamificationEngine';
import { MobileAnalyticsService } from '../../services/MobileAnalyticsService';
import { TouchOptimizedInterface } from './TouchOptimizedInterface';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

interface MobileGamificationAppProps {
  userId: string;
  onAchievementUnlocked?: (achievement: Achievement) => void;
  onLevelUp?: (newLevel: number) => void;
  onChallengeCompleted?: (challenge: Challenge) => void;
  theme?: 'light' | 'dark';
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  points: number;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  unlockedAt?: Date;
  progress: number;
  maxProgress: number;
}

interface Challenge {
  id: string;
  title: string;
  description: string;
  type: 'daily' | 'weekly' | 'monthly' | 'special';
  difficulty: 'easy' | 'medium' | 'hard' | 'expert';
  reward: Reward;
  progress: number;
  maxProgress: number;
  expiresAt: Date;
  isCompleted: boolean;
}

interface Reward {
  type: 'points' | 'badge' | 'premium' | 'feature';
  value: number | string;
  description: string;
}

interface UserStats {
  level: number;
  totalPoints: number;
  pointsToNextLevel: number;
  streak: number;
  rank: number;
  achievements: Achievement[];
  activeChallenges: Challenge[];
  completedChallenges: number;
}

const MobileGamificationApp: React.FC<MobileGamificationAppProps> = ({
  userId,
  onAchievementUnlocked,
  onLevelUp,
  onChallengeCompleted,
  theme = 'dark'
}) => {
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedTab, setSelectedTab] = useState<'overview' | 'achievements' | 'challenges'>('overview');
  const [animatedValues] = useState({
    levelProgress: new Animated.Value(0),
    pointsAnimation: new Animated.Value(0),
    achievementScale: new Animated.Value(1),
  });

  const insets = useSafeAreaInsets();
  const gamificationEngine = GamificationEngine.getInstance();
  const analytics = MobileAnalyticsService.getInstance();

  useEffect(() => {
    initializeGamification();
    
    // Track component usage
    analytics.trackEvent('MobileGamificationApp', 'Viewed', { userId });
  }, [userId]);

  const initializeGamification = async () => {
    try {
      setIsLoading(true);
      
      // Load user gamification data
      const stats = await gamificationEngine.getUserStats(userId);
      setUserStats(stats);
      
      // Animate level progress
      Animated.timing(animatedValues.levelProgress, {
        toValue: stats.pointsToNextLevel > 0 ? 
          (stats.totalPoints % 1000) / 1000 : 1,
        duration: 1000,
        useNativeDriver: false,
      }).start();
      
      // Setup real-time updates
      setupRealtimeUpdates();
      
    } catch (error) {
      console.error('Failed to initialize gamification:', error);
      Alert.alert('Error', 'Failed to load gamification data');
    } finally {
      setIsLoading(false);
    }
  };

  const setupRealtimeUpdates = () => {
    // Listen for achievement unlocks
    gamificationEngine.onAchievementUnlocked((achievement: Achievement) => {
      animateAchievementUnlock(achievement);
      onAchievementUnlocked?.(achievement);
    });

    // Listen for level ups
    gamificationEngine.onLevelUp((newLevel: number) => {
      animateLevelUp(newLevel);
      onLevelUp?.(newLevel);
    });

    // Listen for challenge completions
    gamificationEngine.onChallengeCompleted((challenge: Challenge) => {
      animateChallengeCompletion(challenge);
      onChallengeCompleted?.(challenge);
    });
  };

  const animateAchievementUnlock = (achievement: Achievement) => {
    Animated.sequence([
      Animated.timing(animatedValues.achievementScale, {
        toValue: 1.2,
        duration: 200,
        useNativeDriver: true,
      }),
      Animated.timing(animatedValues.achievementScale, {
        toValue: 1,
        duration: 200,
        useNativeDriver: true,
      }),
    ]).start();

    // Show achievement notification
    Alert.alert(
      '🏆 Achievement Unlocked!',
      `${achievement.title}\n+${achievement.points} points`,
      [{ text: 'Awesome!', style: 'default' }]
    );
  };

  const animateLevelUp = (newLevel: number) => {
    Animated.sequence([
      Animated.timing(animatedValues.pointsAnimation, {
        toValue: 1,
        duration: 500,
        useNativeDriver: true,
      }),
      Animated.timing(animatedValues.pointsAnimation, {
        toValue: 0,
        duration: 500,
        useNativeDriver: true,
      }),
    ]).start();

    Alert.alert(
      '🎉 Level Up!',
      `Congratulations! You've reached level ${newLevel}`,
      [{ text: 'Great!', style: 'default' }]
    );
  };

  const animateChallengeCompletion = (challenge: Challenge) => {
    Alert.alert(
      '✅ Challenge Completed!',
      `${challenge.title}\nReward: ${challenge.reward.description}`,
      [{ text: 'Claim Reward', style: 'default' }]
    );
  };

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    await initializeGamification();
    setIsRefreshing(false);
  }, []);

  const handleTabPress = (tab: 'overview' | 'achievements' | 'challenges') => {
    setSelectedTab(tab);
    analytics.trackEvent('MobileGamificationApp', 'TabChanged', { tab });
  };

  const handleChallengeStart = async (challengeId: string) => {
    try {
      await gamificationEngine.startChallenge(userId, challengeId);
      await initializeGamification(); // Refresh data
      analytics.trackEvent('MobileGamificationApp', 'ChallengeStarted', { challengeId });
    } catch (error) {
      Alert.alert('Error', 'Failed to start challenge');
    }
  };

  const renderOverviewTab = () => (
    <ScrollView
      style={styles.tabContent}
      refreshControl={
        <RefreshControl 
          refreshing={isRefreshing} 
          onRefresh={handleRefresh}
          tintColor={theme === 'dark' ? '#ffffff' : '#000000'}
        />
      }
    >
      {/* User Level Card */}
      <View style={[styles.card, { backgroundColor: theme === 'dark' ? '#2a2a2a' : '#ffffff' }]}>
        <LinearGradient
          colors={['#667eea', '#764ba2']}
          style={styles.levelGradient}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
        >
          <View style={styles.levelContent}>
            <Text style={styles.levelNumber}>LVL {userStats?.level}</Text>
            <Text style={styles.levelPoints}>{userStats?.totalPoints.toLocaleString()} pts</Text>
          </View>
          <View style={styles.progressContainer}>
            <Animated.View 
              style={[
                styles.progressBar,
                {
                  width: animatedValues.levelProgress.interpolate({
                    inputRange: [0, 1],
                    outputRange: ['0%', '100%'],
                  })
                }
              ]}
            />
          </View>
          <Text style={styles.progressText}>
            {userStats?.pointsToNextLevel} points to next level
          </Text>
        </LinearGradient>
      </View>

      {/* Quick Stats */}
      <View style={styles.statsRow}>
        <View style={[styles.statCard, { backgroundColor: theme === 'dark' ? '#2a2a2a' : '#ffffff' }]}>
          <Ionicons name="flame" size={24} color="#ff6b6b" />
          <Text style={[styles.statNumber, { color: theme === 'dark' ? '#ffffff' : '#333333' }]}>
            {userStats?.streak}
          </Text>
          <Text style={[styles.statLabel, { color: theme === 'dark' ? '#cccccc' : '#666666' }]}>
            Day Streak
          </Text>
        </View>
        
        <View style={[styles.statCard, { backgroundColor: theme === 'dark' ? '#2a2a2a' : '#ffffff' }]}>
          <Ionicons name="trophy" size={24} color="#ffd93d" />
          <Text style={[styles.statNumber, { color: theme === 'dark' ? '#ffffff' : '#333333' }]}>
            #{userStats?.rank}
          </Text>
          <Text style={[styles.statLabel, { color: theme === 'dark' ? '#cccccc' : '#666666' }]}>
            Rank
          </Text>
        </View>
        
        <View style={[styles.statCard, { backgroundColor: theme === 'dark' ? '#2a2a2a' : '#ffffff' }]}>
          <Ionicons name="checkmark-circle" size={24} color="#6bcf7f" />
          <Text style={[styles.statNumber, { color: theme === 'dark' ? '#ffffff' : '#333333' }]}>
            {userStats?.completedChallenges}
          </Text>
          <Text style={[styles.statLabel, { color: theme === 'dark' ? '#cccccc' : '#666666' }]}>
            Completed
          </Text>
        </View>
      </View>

      {/* Recent Achievements */}
      <View style={[styles.card, { backgroundColor: theme === 'dark' ? '#2a2a2a' : '#ffffff' }]}>
        <Text style={[styles.cardTitle, { color: theme === 'dark' ? '#ffffff' : '#333333' }]}>
          Recent Achievements
        </Text>
        {userStats?.achievements.slice(0, 3).map((achievement) => (
          <Animated.View 
            key={achievement.id}
            style={[
              styles.achievementItem,
              { transform: [{ scale: animatedValues.achievementScale }] }
            ]}
          >
            <View style={styles.achievementIcon}>
              <Text style={styles.achievementEmoji}>{achievement.icon}</Text>
            </View>
            <View style={styles.achievementContent}>
              <Text style={[styles.achievementTitle, { color: theme === 'dark' ? '#ffffff' : '#333333' }]}>
                {achievement.title}
              </Text>
              <Text style={[styles.achievementDescription, { color: theme === 'dark' ? '#cccccc' : '#666666' }]}>
                {achievement.description}
              </Text>
            </View>
            <View style={styles.achievementPoints}>
              <Text style={styles.pointsText}>+{achievement.points}</Text>
            </View>
          </Animated.View>
        ))}
      </View>

      {/* Active Challenges */}
      <View style={[styles.card, { backgroundColor: theme === 'dark' ? '#2a2a2a' : '#ffffff' }]}>
        <Text style={[styles.cardTitle, { color: theme === 'dark' ? '#ffffff' : '#333333' }]}>
          Active Challenges
        </Text>
        {userStats?.activeChallenges.slice(0, 3).map((challenge) => (
          <View key={challenge.id} style={styles.challengeItem}>
            <View style={styles.challengeContent}>
              <Text style={[styles.challengeTitle, { color: theme === 'dark' ? '#ffffff' : '#333333' }]}>
                {challenge.title}
              </Text>
              <Text style={[styles.challengeDescription, { color: theme === 'dark' ? '#cccccc' : '#666666' }]}>
                {challenge.description}
              </Text>
              <View style={styles.challengeProgress}>
                <View style={styles.challengeProgressBg}>
                  <View 
                    style={[
                      styles.challengeProgressBar,
                      { width: `${(challenge.progress / challenge.maxProgress) * 100}%` }
                    ]} 
                  />
                </View>
                <Text style={[styles.challengeProgressText, { color: theme === 'dark' ? '#cccccc' : '#666666' }]}>
                  {challenge.progress}/{challenge.maxProgress}
                </Text>
              </View>
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );

  const renderAchievementsTab = () => (
    <ScrollView style={styles.tabContent}>
      <Text style={[styles.sectionTitle, { color: theme === 'dark' ? '#ffffff' : '#333333' }]}>
        All Achievements
      </Text>
      {userStats?.achievements.map((achievement) => (
        <View key={achievement.id} style={[styles.fullAchievementItem, { backgroundColor: theme === 'dark' ? '#2a2a2a' : '#ffffff' }]}>
          <View style={styles.achievementIcon}>
            <Text style={styles.achievementEmoji}>{achievement.icon}</Text>
          </View>
          <View style={styles.achievementContent}>
            <Text style={[styles.achievementTitle, { color: theme === 'dark' ? '#ffffff' : '#333333' }]}>
              {achievement.title}
            </Text>
            <Text style={[styles.achievementDescription, { color: theme === 'dark' ? '#cccccc' : '#666666' }]}>
              {achievement.description}
            </Text>
            <View style={styles.achievementMeta}>
              <Text style={[styles.rarityText, { color: getRarityColor(achievement.rarity) }]}>
                {achievement.rarity.toUpperCase()}
              </Text>
              <Text style={styles.pointsText}>+{achievement.points} pts</Text>
            </View>
          </View>
        </View>
      ))}
    </ScrollView>
  );

  const renderChallengesTab = () => (
    <ScrollView style={styles.tabContent}>
      <Text style={[styles.sectionTitle, { color: theme === 'dark' ? '#ffffff' : '#333333' }]}>
        Available Challenges
      </Text>
      {userStats?.activeChallenges.map((challenge) => (
        <View key={challenge.id} style={[styles.fullChallengeItem, { backgroundColor: theme === 'dark' ? '#2a2a2a' : '#ffffff' }]}>
          <View style={styles.challengeHeader}>
            <Text style={[styles.challengeTitle, { color: theme === 'dark' ? '#ffffff' : '#333333' }]}>
              {challenge.title}
            </Text>
            <View style={[styles.difficultyBadge, { backgroundColor: getDifficultyColor(challenge.difficulty) }]}>
              <Text style={styles.difficultyText}>{challenge.difficulty.toUpperCase()}</Text>
            </View>
          </View>
          <Text style={[styles.challengeDescription, { color: theme === 'dark' ? '#cccccc' : '#666666' }]}>
            {challenge.description}
          </Text>
          <View style={styles.challengeProgress}>
            <View style={styles.challengeProgressBg}>
              <View 
                style={[
                  styles.challengeProgressBar,
                  { width: `${(challenge.progress / challenge.maxProgress) * 100}%` }
                ]} 
              />
            </View>
            <Text style={[styles.challengeProgressText, { color: theme === 'dark' ? '#cccccc' : '#666666' }]}>
              {challenge.progress}/{challenge.maxProgress}
            </Text>
          </View>
          <View style={styles.challengeFooter}>
            <Text style={[styles.rewardText, { color: theme === 'dark' ? '#cccccc' : '#666666' }]}>
              Reward: {challenge.reward.description}
            </Text>
            {!challenge.isCompleted && (
              <TouchableOpacity 
                style={styles.startButton}
                onPress={() => handleChallengeStart(challenge.id)}
              >
                <Text style={styles.startButtonText}>Start</Text>
              </TouchableOpacity>
            )}
          </View>
        </View>
      ))}
    </ScrollView>
  );

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common': return '#9e9e9e';
      case 'rare': return '#2196f3';
      case 'epic': return '#9c27b0';
      case 'legendary': return '#ff9800';
      default: return '#9e9e9e';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return '#4caf50';
      case 'medium': return '#ff9800';
      case 'hard': return '#f44336';
      case 'expert': return '#9c27b0';
      default: return '#9e9e9e';
    }
  };

  if (isLoading) {
    return (
      <View style={[styles.container, styles.centered, { backgroundColor: theme === 'dark' ? '#1a1a1a' : '#f5f5f5' }]}>
        <Text style={[styles.loadingText, { color: theme === 'dark' ? '#ffffff' : '#333333' }]}>
          Loading gamification...
        </Text>
      </View>
    );
  }

  return (
    <TouchOptimizedInterface>
      <View style={[styles.container, { backgroundColor: theme === 'dark' ? '#1a1a1a' : '#f5f5f5', paddingTop: insets.top }]}>
        <StatusBar barStyle={theme === 'dark' ? 'light-content' : 'dark-content'} />
        
        {/* Header */}
        <View style={[styles.header, { backgroundColor: theme === 'dark' ? '#2a2a2a' : '#ffffff' }]}>
          <Text style={[styles.headerTitle, { color: theme === 'dark' ? '#ffffff' : '#333333' }]}>
            Gamification
          </Text>
        </View>

        {/* Tab Navigation */}
        <View style={[styles.tabBar, { backgroundColor: theme === 'dark' ? '#2a2a2a' : '#ffffff' }]}>
          <TouchableOpacity 
            style={[styles.tab, selectedTab === 'overview' && styles.activeTab]}
            onPress={() => handleTabPress('overview')}
          >
            <Text style={[styles.tabText, selectedTab === 'overview' && styles.activeTabText]}>
              Overview
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.tab, selectedTab === 'achievements' && styles.activeTab]}
            onPress={() => handleTabPress('achievements')}
          >
            <Text style={[styles.tabText, selectedTab === 'achievements' && styles.activeTabText]}>
              Achievements
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.tab, selectedTab === 'challenges' && styles.activeTab]}
            onPress={() => handleTabPress('challenges')}
          >
            <Text style={[styles.tabText, selectedTab === 'challenges' && styles.activeTabText]}>
              Challenges
            </Text>
          </TouchableOpacity>
        </View>

        {/* Tab Content */}
        {selectedTab === 'overview' && renderOverviewTab()}
        {selectedTab === 'achievements' && renderAchievementsTab()}
        {selectedTab === 'challenges' && renderChallengesTab()}
      </View>
    </TouchOptimizedInterface>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  centered: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  tabBar: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  tab: {
    flex: 1,
    paddingVertical: 15,
    alignItems: 'center',
  },
  activeTab: {
    borderBottomWidth: 2,
    borderBottomColor: '#667eea',
  },
  tabText: {
    fontSize: 16,
    color: '#999999',
  },
  activeTabText: {
    color: '#667eea',
    fontWeight: '600',
  },
  tabContent: {
    flex: 1,
    padding: 20,
  },
  card: {
    borderRadius: 12,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  levelGradient: {
    padding: 20,
    borderRadius: 12,
  },
  levelContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  levelNumber: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  levelPoints: {
    fontSize: 18,
    color: '#ffffff',
    opacity: 0.9,
  },
  progressContainer: {
    height: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    borderRadius: 4,
    marginBottom: 10,
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#ffffff',
    borderRadius: 4,
  },
  progressText: {
    color: '#ffffff',
    fontSize: 14,
    opacity: 0.9,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  statCard: {
    flex: 1,
    marginHorizontal: 5,
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    marginTop: 4,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 15,
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  achievementItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  fullAchievementItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    borderRadius: 12,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  achievementIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  achievementEmoji: {
    fontSize: 24,
  },
  achievementContent: {
    flex: 1,
  },
  achievementTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  achievementDescription: {
    fontSize: 14,
  },
  achievementMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
  },
  rarityText: {
    fontSize: 12,
    fontWeight: '600',
  },
  achievementPoints: {
    marginLeft: 10,
  },
  pointsText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#667eea',
  },
  challengeItem: {
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  fullChallengeItem: {
    padding: 20,
    borderRadius: 12,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  challengeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  challengeContent: {
    flex: 1,
  },
  challengeTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
    flex: 1,
  },
  challengeDescription: {
    fontSize: 14,
    marginBottom: 12,
  },
  challengeProgress: {
    marginBottom: 10,
  },
  challengeProgressBg: {
    height: 6,
    backgroundColor: '#e0e0e0',
    borderRadius: 3,
    marginBottom: 5,
  },
  challengeProgressBar: {
    height: '100%',
    backgroundColor: '#667eea',
    borderRadius: 3,
  },
  challengeProgressText: {
    fontSize: 12,
    textAlign: 'right',
  },
  challengeFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  rewardText: {
    fontSize: 14,
    flex: 1,
  },
  difficultyBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  difficultyText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: '600',
  },
  startButton: {
    backgroundColor: '#667eea',
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 20,
  },
  startButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  loadingText: {
    fontSize: 16,
  },
});

export default MobileGamificationApp;