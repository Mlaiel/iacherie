/**
 * Challenge Interface - Ultra-Advanced Enterprise System
 * 
 * This component provides comprehensive challenge management interface with
 * real-time participation tracking and intelligent challenge recommendations.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️  CRITICAL LEGAL NOTICE:
 * This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
 * Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
 * Contact: mlaiel@live.de for licensing inquiries.
 * 
 * 🏆 Expert Development Team Specialties:
 * - Lead AI Developer: Advanced machine learning and AI systems
 * - Backend Senior Engineer: Enterprise Python/FastAPI architecture
 * - ML Engineer: TensorFlow/PyTorch and neural networks
 * - Database Administrator: PostgreSQL and vector databases
 * - Security Specialist: Enterprise security protocols
 * - Microservices Architect: Scalable distributed systems
 * - Audio Engineer: Professional audio processing
 * - DevOps Engineer: CI/CD and cloud infrastructure
 * - AI Prompt Engineer: Advanced prompt engineering
 */

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Challenge, 
  ChallengeStatus, 
  ChallengeType, 
  FilterOptions,
  ApiResponse,
  PaginatedResponse
} from '../types';
import { 
  gamificationStyles, 
  challengeIcons, 
  getDifficultyLabel, 
  difficultyColors 
} from '../gamification.styles';
import { 
  FunnelIcon,
  MagnifyingGlassIcon,
  ClockIcon,
  UserGroupIcon,
  TrophyIcon,
  PlayIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface ChallengeInterfaceProps {
  userId: string;
  className?: string;
  onChallengeJoin?: (challengeId: string) => Promise<void>;
  onChallengeLeave?: (challengeId: string) => Promise<void>;
  onChallengeDetails?: (challenge: Challenge) => void;
}

const ChallengeInterface: React.FC<ChallengeInterfaceProps> = ({
  userId,
  className,
  onChallengeJoin,
  onChallengeLeave,
  onChallengeDetails
}) => {
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<FilterOptions>({});
  const [selectedChallenge, setSelectedChallenge] = useState<Challenge | null>(null);
  const [joinLoading, setJoinLoading] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const fetchChallenges = useCallback(async (pageNum: number = 1, reset: boolean = false) => {
    try {
      setLoading(pageNum === 1);
      setError(null);

      const queryParams = new URLSearchParams({
        page: pageNum.toString(),
        pageSize: '12',
        search: searchQuery,
        userId: userId,
        ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v !== undefined))
      });

      const response = await fetch(`/api/gamification/challenges?${queryParams}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch challenges: ${response.statusText}`);
      }

      const result: ApiResponse<PaginatedResponse<Challenge>> = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch challenges');
      }

      const newChallenges = result.data!.items;
      
      if (reset || pageNum === 1) {
        setChallenges(newChallenges);
      } else {
        setChallenges(prev => [...prev, ...newChallenges]);
      }
      
      setHasMore(result.data!.hasMore);
      setPage(pageNum);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
      console.error('Challenge fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, filters, userId]);

  useEffect(() => {
    fetchChallenges(1, true);
  }, [fetchChallenges]);

  const handleJoinChallenge = async (challenge: Challenge) => {
    if (!onChallengeJoin || joinLoading) return;

    try {
      setJoinLoading(challenge.id);
      await onChallengeJoin(challenge.id);
      
      // Update local state
      setChallenges(prev => prev.map(c => 
        c.id === challenge.id 
          ? { ...c, participants: [...c.participants, userId] }
          : c
      ));
    } catch (err) {
      console.error('Failed to join challenge:', err);
    } finally {
      setJoinLoading(null);
    }
  };

  const handleLeaveChallenge = async (challenge: Challenge) => {
    if (!onChallengeLeave || joinLoading) return;

    try {
      setJoinLoading(challenge.id);
      await onChallengeLeave(challenge.id);
      
      // Update local state
      setChallenges(prev => prev.map(c => 
        c.id === challenge.id 
          ? { ...c, participants: c.participants.filter(p => p !== userId) }
          : c
      ));
    } catch (err) {
      console.error('Failed to leave challenge:', err);
    } finally {
      setJoinLoading(null);
    }
  };

  const isParticipating = (challenge: Challenge) => 
    challenge.participants.includes(userId);

  const isCompleted = (challenge: Challenge) => 
    challenge.completedBy.includes(userId);

  const getTimeRemaining = (endDate: Date): string => {
    const now = new Date();
    const diff = endDate.getTime() - now.getTime();
    
    if (diff <= 0) return 'Expired';
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  const getStatusIcon = (challenge: Challenge) => {
    if (isCompleted(challenge)) return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
    if (challenge.status === ChallengeStatus.EXPIRED) return <XCircleIcon className="w-5 h-5 text-red-500" />;
    if (isParticipating(challenge)) return <PlayIcon className="w-5 h-5 text-blue-500" />;
    return <ClockIcon className="w-5 h-5 text-slate-400" />;
  };

  const filteredAndSortedChallenges = challenges.filter(challenge => {
    if (searchQuery && !challenge.title.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !challenge.description.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  });

  if (loading && challenges.length === 0) {
    return (
      <div className={clsx(gamificationStyles.container.main, className)}>
        <div className="max-w-7xl mx-auto p-6">
          <div className={gamificationStyles.loading.skeleton + " h-8 w-64 mb-6"} />
          <div className={gamificationStyles.grid.cols3}>
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className={gamificationStyles.container.card}>
                <div className={gamificationStyles.loading.skeleton + " h-6 w-32 mb-3"} />
                <div className={gamificationStyles.loading.skeleton + " h-4 w-full mb-2"} />
                <div className={gamificationStyles.loading.skeleton + " h-4 w-3/4 mb-4"} />
                <div className={gamificationStyles.loading.skeleton + " h-10 w-full"} />
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={clsx(gamificationStyles.container.main, className)}>
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className={gamificationStyles.typography.heading.primary}>
            Challenge Arena
          </h1>
          <p className={gamificationStyles.typography.body.regular}>
            Participate in challenges to earn rewards and boost your creator journey
          </p>
        </div>

        {/* Search and Filters */}
        <div className={clsx(gamificationStyles.container.section, "mb-6")}>
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search challenges..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className={clsx(gamificationStyles.forms.input, "pl-10")}
                />
              </div>
            </div>

            {/* Filters */}
            <div className="flex gap-3">
              <select
                value={filters.type || ''}
                onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value as ChallengeType || undefined }))}
                className={gamificationStyles.forms.select}
              >
                <option value="">All Types</option>
                <option value={ChallengeType.DAILY}>Daily</option>
                <option value={ChallengeType.WEEKLY}>Weekly</option>
                <option value={ChallengeType.MONTHLY}>Monthly</option>
                <option value={ChallengeType.SEASONAL}>Seasonal</option>
                <option value={ChallengeType.SPECIAL}>Special</option>
              </select>

              <select
                value={filters.difficulty || ''}
                onChange={(e) => setFilters(prev => ({ ...prev, difficulty: e.target.value ? parseInt(e.target.value) : undefined }))}
                className={gamificationStyles.forms.select}
              >
                <option value="">All Difficulties</option>
                <option value="1">Beginner</option>
                <option value="2">Intermediate</option>
                <option value="3">Advanced</option>
                <option value="4">Expert</option>
                <option value="5">Master</option>
              </select>

              <select
                value={filters.status || ''}
                onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value || undefined }))}
                className={gamificationStyles.forms.select}
              >
                <option value="">All Status</option>
                <option value={ChallengeStatus.ACTIVE}>Active</option>
                <option value={ChallengeStatus.COMPLETED}>Completed</option>
                <option value={ChallengeStatus.PENDING}>Pending</option>
              </select>
            </div>
          </div>
        </div>

        {error && (
          <div className={clsx(gamificationStyles.container.section, "mb-6 bg-red-50 border-red-200")}>
            <div className="text-red-800">
              <strong>Error:</strong> {error}
            </div>
            <button
              onClick={() => fetchChallenges(1, true)}
              className={clsx(gamificationStyles.buttons.danger, "mt-2")}
            >
              Retry
            </button>
          </div>
        )}

        {/* Challenges Grid */}
        <div className={gamificationStyles.grid.cols3}>
          {filteredAndSortedChallenges.map((challenge) => {
            const participating = isParticipating(challenge);
            const completed = isCompleted(challenge);
            const expired = challenge.status === ChallengeStatus.EXPIRED;

            return (
              <div
                key={challenge.id}
                className={clsx(
                  gamificationStyles.container.card,
                  "cursor-pointer hover:shadow-lg transition-all duration-300",
                  completed && "ring-2 ring-green-500",
                  participating && !completed && "ring-2 ring-blue-500"
                )}
                onClick={() => onChallengeDetails?.(challenge)}
              >
                {/* Header */}
                <div className={gamificationStyles.utils.flexBetween + " mb-3"}>
                  <div className="flex items-center">
                    <span className="text-2xl mr-2">
                      {challengeIcons[challenge.type]}
                    </span>
                    <div className={clsx(
                      gamificationStyles.challengeTypes[challenge.type].bg,
                      gamificationStyles.challengeTypes[challenge.type].text,
                      "px-2 py-1 rounded-full text-xs font-medium"
                    )}>
                      {challenge.type}
                    </div>
                  </div>
                  {getStatusIcon(challenge)}
                </div>

                {/* Content */}
                <h3 className={clsx(gamificationStyles.typography.body.large, "font-semibold mb-2")}>
                  {challenge.title}
                </h3>
                <p className={clsx(gamificationStyles.typography.body.small, "mb-3 line-clamp-2")}>
                  {challenge.description}
                </p>

                {/* Metadata */}
                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-500">Difficulty:</span>
                    <span className={difficultyColors[challenge.difficulty as keyof typeof difficultyColors]}>
                      {getDifficultyLabel(challenge.difficulty)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-500">Time Remaining:</span>
                    <span className={expired ? "text-red-500" : "text-slate-700"}>
                      {getTimeRemaining(challenge.endDate)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-500">Participants:</span>
                    <span className="flex items-center">
                      <UserGroupIcon className="w-4 h-4 mr-1" />
                      {challenge.participants.length}
                      {challenge.maxParticipants && `/${challenge.maxParticipants}`}
                    </span>
                  </div>
                </div>

                {/* Rewards Preview */}
                {challenge.rewards && Object.keys(challenge.rewards).length > 0 && (
                  <div className="mb-4 p-2 bg-yellow-50 rounded-lg">
                    <div className="flex items-center text-sm">
                      <TrophyIcon className="w-4 h-4 mr-1 text-yellow-600" />
                      <span className="text-yellow-800">
                        {challenge.rewards.xp && `${challenge.rewards.xp} XP`}
                        {challenge.rewards.currency && ` • ${challenge.rewards.currency} coins`}
                        {challenge.rewards.badge && ` • ${challenge.rewards.badge}`}
                      </span>
                    </div>
                  </div>
                )}

                {/* Action Button */}
                <div className="mt-auto">
                  {completed ? (
                    <button
                      disabled
                      className={clsx(gamificationStyles.buttons.success, "w-full cursor-not-allowed opacity-60")}
                    >
                      <CheckCircleIcon className="w-4 h-4 mr-2" />
                      Completed
                    </button>
                  ) : expired ? (
                    <button
                      disabled
                      className={clsx(gamificationStyles.buttons.secondary, "w-full cursor-not-allowed opacity-60")}
                    >
                      <XCircleIcon className="w-4 h-4 mr-2" />
                      Expired
                    </button>
                  ) : participating ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleLeaveChallenge(challenge);
                      }}
                      disabled={joinLoading === challenge.id}
                      className={clsx(gamificationStyles.buttons.warning, "w-full")}
                    >
                      {joinLoading === challenge.id ? (
                        <div className={gamificationStyles.loading.spinner + " mr-2"} />
                      ) : (
                        <XCircleIcon className="w-4 h-4 mr-2" />
                      )}
                      Leave Challenge
                    </button>
                  ) : (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleJoinChallenge(challenge);
                      }}
                      disabled={joinLoading === challenge.id}
                      className={clsx(gamificationStyles.buttons.primary, "w-full")}
                    >
                      {joinLoading === challenge.id ? (
                        <div className={gamificationStyles.loading.spinner + " mr-2"} />
                      ) : (
                        <PlayIcon className="w-4 h-4 mr-2" />
                      )}
                      Join Challenge
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Load More */}
        {hasMore && !loading && (
          <div className="text-center mt-8">
            <button
              onClick={() => fetchChallenges(page + 1, false)}
              className={gamificationStyles.buttons.secondary}
            >
              Load More Challenges
            </button>
          </div>
        )}

        {/* No Results */}
        {!loading && filteredAndSortedChallenges.length === 0 && (
          <div className={gamificationStyles.container.section}>
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🎯</div>
              <h3 className={gamificationStyles.typography.heading.secondary}>
                No Challenges Found
              </h3>
              <p className={gamificationStyles.typography.body.regular}>
                Try adjusting your search criteria or check back later for new challenges.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChallengeInterface;