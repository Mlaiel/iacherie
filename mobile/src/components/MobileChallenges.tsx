/**
 * Mobile Challenges - Advanced Challenge Management System
 * 
 * Interactive mobile interface for managing content creation challenges,
 * progress tracking, and reward claiming within the Ainflue ecosystem.
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
  Modal,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import LinearGradient from 'react-native-linear-gradient';

import { Challenge, BaseMobileComponentProps } from './types';

const { width } = Dimensions.get('window');

interface MobileChallengesProps extends BaseMobileComponentProps {
  challenges: Challenge[];
  userProgress: Record<string, number>;
  completedChallenges: string[];
  onChallengeAccept: (challengeId: string) => void;
  onChallengeStart: (challengeId: string) => void;
  onClaimReward: (challengeId: string) => void;
  onShareProgress: (challengeId: string) => void;
  theme?: 'light' | 'dark';
}

const MobileChallenges: React.FC<MobileChallengesProps> = ({
  challenges,
  userProgress,
  completedChallenges,
  onChallengeAccept,
  onChallengeStart,
  onClaimReward,
  onShareProgress,
  theme = 'dark',
  style,
  testID,
}) => {
  const [refreshing, setRefreshing] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'daily' | 'weekly' | 'monthly' | 'special'>('all');
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'creation' | 'engagement' | 'collaboration' | 'growth'>('all');
  const [selectedChallenge, setSelectedChallenge] = useState<Challenge | null>(null);
  const [showChallengeModal, setShowChallengeModal] = useState(false);
  const [animatedValues] = useState(
    challenges.reduce((acc, challenge) => {
      acc[challenge.id] = new Animated.Value(0);
      return acc;
    }, {} as Record<string, Animated.Value>)
  );

  useEffect(() => {
    // Animate challenge cards entrance
    challenges.forEach((challenge, index) => {
      setTimeout(() => {
        Animated.timing(animatedValues[challenge.id], {
          toValue: 1,
          duration: 600,
          useNativeDriver: true,
        }).start();
      }, index * 100);
    });
  }, [challenges, animatedValues]);

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    // Simulate refresh
    setTimeout(() => setRefreshing(false), 2000);
  }, []);

  const filteredChallenges = challenges.filter((challenge) => {
    const typeMatch = selectedFilter === 'all' || challenge.type === selectedFilter;
    const categoryMatch = selectedCategory === 'all' || challenge.category === selectedCategory;
    return typeMatch && categoryMatch;
  });

  const getChallengeProgress = (challenge: Challenge) => {
    return userProgress[challenge.id] || 0;
  };

  const isChallengeCompleted = (challengeId: string) => {
    return completedChallenges.includes(challengeId);
  };

  const getRemainingTime = (challenge: Challenge) => {
    const now = new Date();
    const remaining = challenge.endDate.getTime() - now.getTime();
    
    if (remaining <= 0) return 'Expired';
    
    const days = Math.floor(remaining / (1000 * 60 * 60 * 24));
    const hours = Math.floor((remaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h`;
    return '<1h';
  };

  const getDifficultyColor = (difficulty: Challenge['difficulty']) => {
    switch (difficulty) {
      case 'easy': return '#10b981';
      case 'medium': return '#f59e0b';
      case 'hard': return '#ef4444';
      case 'expert': return '#8b5cf6';
      default: return '#6b7280';
    }
  };

  const getCategoryIcon = (category: Challenge['category']) => {
    switch (category) {
      case 'creation': return 'palette';
      case 'engagement': return 'heart';
      case 'collaboration': return 'account-group';
      case 'growth': return 'trending-up';
      default: return 'star';
    }
  };

  const handleChallengePress = (challenge: Challenge) => {
    setSelectedChallenge(challenge);
    setShowChallengeModal(true);
  };

  const handleChallengeAction = (action: 'accept' | 'start' | 'claim', challenge: Challenge) => {
    switch (action) {
      case 'accept':
        onChallengeAccept(challenge.id);
        break;
      case 'start':
        onChallengeStart(challenge.id);
        break;
      case 'claim':
        onClaimReward(challenge.id);
        break;
    }
    setShowChallengeModal(false);
  };

  const renderChallengeCard = (challenge: Challenge) => {
    const progress = getChallengeProgress(challenge);
    const isCompleted = isChallengeCompleted(challenge.id);
    const remainingTime = getRemainingTime(challenge);
    const progressPercentage = Math.min(progress / challenge.requirements.target * 100, 100);

    return (
      <Animated.View
        key={challenge.id}
        style={[
          styles.challengeCard,
          {
            opacity: animatedValues[challenge.id],
            transform: [
              {
                translateY: animatedValues[challenge.id]?.interpolate({
                  inputRange: [0, 1],
                  outputRange: [50, 0],
                }) || 0,
              },
            ],
          },
        ]}
      >
        <TouchableOpacity onPress={() => handleChallengePress(challenge)}>
          <LinearGradient
            colors={
              isCompleted
                ? ['#10b981', '#059669']
                : ['#1e293b', '#334155']
            }
            style={styles.cardGradient}
          >
            {/* Challenge Header */}
            <View style={styles.challengeHeader}>
              <View style={styles.challengeInfo}>
                <Icon
                  name={getCategoryIcon(challenge.category)}
                  size={24}
                  color={getDifficultyColor(challenge.difficulty)}
                />
                <View style={styles.challengeTitleContainer}>
                  <Text style={styles.challengeTitle}>{challenge.title}</Text>
                  <View style={styles.challengeMeta}>
                    <View style={[styles.difficultyBadge, { backgroundColor: getDifficultyColor(challenge.difficulty) }]}>
                      <Text style={styles.difficultyText}>{challenge.difficulty.toUpperCase()}</Text>
                    </View>
                    <Text style={styles.challengeType}>{challenge.type}</Text>
                  </View>
                </View>
              </View>
              <View style={styles.challengeTime}>
                <Icon name="clock-outline" size={16} color="#94a3b8" />
                <Text style={styles.timeText}>{remainingTime}</Text>
              </View>
            </View>

            {/* Challenge Description */}
            <Text style={styles.challengeDescription} numberOfLines={3}>
              {challenge.description}
            </Text>

            {/* Progress Section */}
            <View style={styles.progressSection}>
              <View style={styles.progressHeader}>
                <Text style={styles.progressLabel}>
                  Progress: {progress}/{challenge.requirements.target} {challenge.requirements.metric}
                </Text>
                <Text style={styles.progressPercentage}>
                  {Math.floor(progressPercentage)}%
                </Text>
              </View>
              <View style={styles.progressBar}>
                <View
                  style={[
                    styles.progressFill,
                    { 
                      width: `${progressPercentage}%`,
                      backgroundColor: isCompleted ? '#ffffff' : getDifficultyColor(challenge.difficulty),
                    },
                  ]}
                />
              </View>
            </View>

            {/* Rewards Section */}
            <View style={styles.rewardsSection}>
              <Text style={styles.rewardsLabel}>Rewards:</Text>
              <View style={styles.rewardsList}>
                <View style={styles.rewardItem}>
                  <Icon name="star-circle" size={16} color="#FFD700" />
                  <Text style={styles.rewardText}>+{challenge.rewards.points} XP</Text>
                </View>
                {challenge.rewards.badges?.map((badge, index) => (
                  <View key={index} style={styles.rewardItem}>
                    <Icon name="medal" size={16} color="#C0C0C0" />
                    <Text style={styles.rewardText}>{badge}</Text>
                  </View>
                ))}
              </View>
            </View>

            {/* Action Button */}
            <TouchableOpacity
              style={[
                styles.actionButton,
                isCompleted && styles.completedButton,
              ]}
              onPress={() => {
                if (isCompleted) {
                  handleChallengeAction('claim', challenge);
                } else if (progressPercentage > 0) {
                  handleChallengeAction('start', challenge);
                } else {
                  handleChallengeAction('accept', challenge);
                }
              }}
            >
              <Text style={styles.actionButtonText}>
                {isCompleted
                  ? 'Claim Reward'
                  : progressPercentage > 0
                  ? 'Continue'
                  : 'Accept Challenge'}
              </Text>
              <Icon
                name={
                  isCompleted
                    ? 'gift'
                    : progressPercentage > 0
                    ? 'play'
                    : 'plus'
                }
                size={16}
                color="#ffffff"
              />
            </TouchableOpacity>
          </LinearGradient>
        </TouchableOpacity>
      </Animated.View>
    );
  };

  const renderChallengeModal = () => {
    if (!selectedChallenge) return null;

    const progress = getChallengeProgress(selectedChallenge);
    const isCompleted = isChallengeCompleted(selectedChallenge.id);
    const progressPercentage = Math.min(progress / selectedChallenge.requirements.target * 100, 100);

    return (
      <Modal
        visible={showChallengeModal}
        animationType="slide"
        transparent
        onRequestClose={() => setShowChallengeModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>{selectedChallenge.title}</Text>
              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setShowChallengeModal(false)}
              >
                <Icon name="close" size={24} color="#ffffff" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalBody}>
              <Text style={styles.modalDescription}>
                {selectedChallenge.description}
              </Text>

              <View style={styles.modalSection}>
                <Text style={styles.modalSectionTitle}>Requirements</Text>
                <Text style={styles.modalSectionContent}>
                  {selectedChallenge.requirements.target} {selectedChallenge.requirements.metric}
                  {selectedChallenge.requirements.timeframe > 0 &&
                    ` within ${selectedChallenge.requirements.timeframe} days`}
                </Text>
              </View>

              <View style={styles.modalSection}>
                <Text style={styles.modalSectionTitle}>Progress</Text>
                <View style={styles.progressBar}>
                  <View
                    style={[
                      styles.progressFill,
                      { width: `${progressPercentage}%` },
                    ]}
                  />
                </View>
                <Text style={styles.modalSectionContent}>
                  {progress}/{selectedChallenge.requirements.target} ({Math.floor(progressPercentage)}%)
                </Text>
              </View>

              <View style={styles.modalSection}>
                <Text style={styles.modalSectionTitle}>Rewards</Text>
                <View style={styles.modalRewardsList}>
                  <Text style={styles.modalSectionContent}>
                    • {selectedChallenge.rewards.points} Experience Points
                  </Text>
                  {selectedChallenge.rewards.badges?.map((badge, index) => (
                    <Text key={index} style={styles.modalSectionContent}>
                      • {badge} Badge
                    </Text>
                  ))}
                  {selectedChallenge.rewards.unlocks?.map((unlock, index) => (
                    <Text key={index} style={styles.modalSectionContent}>
                      • Unlock: {unlock}
                    </Text>
                  ))}
                </View>
              </View>
            </ScrollView>

            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.shareButton}
                onPress={() => {
                  onShareProgress(selectedChallenge.id);
                  setShowChallengeModal(false);
                }}
              >
                <Icon name="share" size={16} color="#3b82f6" />
                <Text style={styles.shareButtonText}>Share Progress</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[
                  styles.primaryButton,
                  isCompleted && styles.completedButton,
                ]}
                onPress={() => {
                  if (isCompleted) {
                    handleChallengeAction('claim', selectedChallenge);
                  } else if (progressPercentage > 0) {
                    handleChallengeAction('start', selectedChallenge);
                  } else {
                    handleChallengeAction('accept', selectedChallenge);
                  }
                }}
              >
                <Text style={styles.primaryButtonText}>
                  {isCompleted
                    ? 'Claim Reward'
                    : progressPercentage > 0
                    ? 'Continue Challenge'
                    : 'Accept Challenge'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    );
  };

  return (
    <SafeAreaView style={[styles.container, style]} testID={testID}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Challenges</Text>
        <View style={styles.headerStats}>
          <Text style={styles.statsText}>
            {completedChallenges.length}/{challenges.length} Completed
          </Text>
        </View>
      </View>

      {/* Filters */}
      <View style={styles.filtersContainer}>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.filterScrollView}
        >
          {(['all', 'daily', 'weekly', 'monthly', 'special'] as const).map((filter) => (
            <TouchableOpacity
              key={filter}
              style={[
                styles.filterButton,
                selectedFilter === filter && styles.activeFilterButton,
              ]}
              onPress={() => setSelectedFilter(filter)}
            >
              <Text
                style={[
                  styles.filterText,
                  selectedFilter === filter && styles.activeFilterText,
                ]}
              >
                {filter.charAt(0).toUpperCase() + filter.slice(1)}
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
          {(['all', 'creation', 'engagement', 'collaboration', 'growth'] as const).map((category) => (
            <TouchableOpacity
              key={category}
              style={[
                styles.filterButton,
                selectedCategory === category && styles.activeFilterButton,
              ]}
              onPress={() => setSelectedCategory(category)}
            >
              <Text
                style={[
                  styles.filterText,
                  selectedCategory === category && styles.activeFilterText,
                ]}
              >
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Challenges List */}
      <ScrollView
        style={styles.challengesList}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
        }
      >
        {filteredChallenges.map(renderChallengeCard)}
      </ScrollView>

      {/* Challenge Detail Modal */}
      {renderChallengeModal()}
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
  headerStats: {
    alignItems: 'flex-end',
  },
  statsText: {
    fontSize: 14,
    color: '#94a3b8',
  },
  filtersContainer: {
    paddingVertical: 8,
  },
  filterScrollView: {
    paddingHorizontal: 16,
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#1e293b',
    borderRadius: 20,
    marginRight: 8,
  },
  activeFilterButton: {
    backgroundColor: '#3b82f6',
  },
  filterText: {
    fontSize: 14,
    color: '#94a3b8',
    fontWeight: '600',
  },
  activeFilterText: {
    color: '#ffffff',
  },
  challengesList: {
    flex: 1,
    paddingHorizontal: 16,
  },
  challengeCard: {
    marginBottom: 16,
    borderRadius: 16,
    overflow: 'hidden',
  },
  cardGradient: {
    padding: 16,
  },
  challengeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  challengeInfo: {
    flexDirection: 'row',
    flex: 1,
  },
  challengeTitleContainer: {
    flex: 1,
    marginLeft: 12,
  },
  challengeTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  challengeMeta: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  difficultyBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    marginRight: 8,
  },
  difficultyText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  challengeType: {
    fontSize: 12,
    color: '#94a3b8',
    textTransform: 'capitalize',
  },
  challengeTime: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  timeText: {
    fontSize: 12,
    color: '#94a3b8',
    marginLeft: 4,
  },
  challengeDescription: {
    fontSize: 14,
    color: '#e2e8f0',
    lineHeight: 20,
    marginBottom: 16,
  },
  progressSection: {
    marginBottom: 16,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  progressLabel: {
    fontSize: 12,
    color: '#94a3b8',
  },
  progressPercentage: {
    fontSize: 12,
    color: '#ffffff',
    fontWeight: 'bold',
  },
  progressBar: {
    height: 6,
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 3,
  },
  rewardsSection: {
    marginBottom: 16,
  },
  rewardsLabel: {
    fontSize: 12,
    color: '#94a3b8',
    marginBottom: 8,
  },
  rewardsList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  rewardItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
    marginBottom: 4,
  },
  rewardText: {
    fontSize: 12,
    color: '#e2e8f0',
    marginLeft: 4,
  },
  actionButton: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#3b82f6',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  completedButton: {
    backgroundColor: '#10b981',
  },
  actionButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
    marginRight: 8,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.8)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#1e293b',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    flex: 1,
  },
  closeButton: {
    padding: 4,
  },
  modalBody: {
    padding: 16,
  },
  modalDescription: {
    fontSize: 16,
    color: '#e2e8f0',
    lineHeight: 24,
    marginBottom: 24,
  },
  modalSection: {
    marginBottom: 20,
  },
  modalSectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
  },
  modalSectionContent: {
    fontSize: 14,
    color: '#94a3b8',
    lineHeight: 20,
  },
  modalRewardsList: {
    marginTop: 4,
  },
  modalActions: {
    flexDirection: 'row',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#334155',
  },
  shareButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderWidth: 1,
    borderColor: '#3b82f6',
    borderRadius: 8,
    marginRight: 12,
  },
  shareButtonText: {
    fontSize: 14,
    color: '#3b82f6',
    marginLeft: 8,
  },
  primaryButton: {
    flex: 1,
    backgroundColor: '#3b82f6',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  primaryButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
  },
});

export default MobileChallenges;