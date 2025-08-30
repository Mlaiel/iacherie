/**
 * Social Competitions - Ultra-Advanced Enterprise System
 * 
 * This component provides comprehensive social competition management with
 * real-time tournament brackets and competitive matchmaking.
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
  Competition,
  Reward,
  ApiResponse,
  PaginatedResponse 
} from './types';
import { gamificationStyles } from './gamification.styles';
import { 
  TrophyIcon,
  UsersIcon,
  ClockIcon,
  CurrencyDollarIcon,
  FireIcon,
  PlayIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  CalendarIcon,
  StarIcon
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface SocialCompetitionsProps {
  userId: string;
  className?: string;
  onCompetitionJoin?: (competitionId: string) => Promise<boolean>;
  onCompetitionDetails?: (competition: Competition) => void;
  showCompleted?: boolean;
}

interface Participant {
  userId: string;
  username: string;
  avatar?: string;
  score: number;
  rank: number;
  isCurrentUser: boolean;
}

interface CompetitionDetails extends Competition {
  leaderboard: Participant[];
  userRank?: number;
  timeRemaining: string;
  isParticipating: boolean;
  canJoin: boolean;
  joinReason?: string;
}

const SocialCompetitions: React.FC<SocialCompetitionsProps> = ({
  userId,
  className,
  onCompetitionJoin,
  onCompetitionDetails,
  showCompleted = false
}) => {
  const [competitions, setCompetitions] = useState<CompetitionDetails[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [joiningId, setJoiningId] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<'all' | 'upcoming' | 'active' | 'completed'>('active');
  const [filterCategory, setFilterCategory] = useState<string>('');
  const [sortBy, setSortBy] = useState<'startDate' | 'prizePool' | 'participants'>('startDate');

  const fetchCompetitions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const queryParams = new URLSearchParams({
        userId,
        status: filterStatus === 'all' ? '' : filterStatus,
        category: filterCategory,
        sort: sortBy,
        includeCompleted: showCompleted.toString()
      });

      const response = await fetch(`/api/gamification/competitions?${queryParams}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch competitions: ${response.statusText}`);
      }

      const result: ApiResponse<PaginatedResponse<CompetitionDetails>> = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch competitions');
      }

      setCompetitions(result.data!.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
      console.error('Competitions fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [userId, filterStatus, filterCategory, sortBy, showCompleted]);

  useEffect(() => {
    fetchCompetitions();
  }, [fetchCompetitions]);

  const handleJoinCompetition = async (competition: CompetitionDetails) => {
    if (!onCompetitionJoin || joiningId || !competition.canJoin) return;

    try {
      setJoiningId(competition.id);
      const success = await onCompetitionJoin(competition.id);
      
      if (success) {
        // Update local state
        setCompetitions(prev => prev.map(c => 
          c.id === competition.id 
            ? { 
                ...c, 
                participants: [...c.participants, userId],
                isParticipating: true,
                canJoin: false
              }
            : c
        ));
      }
    } catch (err) {
      console.error('Failed to join competition:', err);
    } finally {
      setJoiningId(null);
    }
  };

  const getStatusColor = (status: Competition['status']) => {
    switch (status) {
      case 'upcoming':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300';
      case 'active':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      case 'completed':
        return 'bg-slate-100 text-slate-800 dark:bg-slate-900/30 dark:text-slate-300';
      case 'cancelled':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
      default:
        return 'bg-slate-100 text-slate-800';
    }
  };

  const getStatusIcon = (status: Competition['status']) => {
    switch (status) {
      case 'upcoming':
        return <CalendarIcon className="w-4 h-4" />;
      case 'active':
        return <FireIcon className="w-4 h-4" />;
      case 'completed':
        return <CheckCircleIcon className="w-4 h-4" />;
      case 'cancelled':
        return <ExclamationTriangleIcon className="w-4 h-4" />;
      default:
        return <ClockIcon className="w-4 h-4" />;
    }
  };

  const formatTimeRemaining = (competition: CompetitionDetails): string => {
    const now = new Date();
    const startDate = new Date(competition.startDate);
    const endDate = new Date(competition.endDate);

    if (competition.status === 'upcoming') {
      const diff = startDate.getTime() - now.getTime();
      if (diff <= 0) return 'Starting soon';
      
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      
      if (days > 0) return `Starts in ${days}d ${hours}h`;
      return `Starts in ${hours}h`;
    }

    if (competition.status === 'active') {
      const diff = endDate.getTime() - now.getTime();
      if (diff <= 0) return 'Ending soon';
      
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      
      if (days > 0) return `${days}d ${hours}h remaining`;
      return `${hours}h remaining`;
    }

    return competition.timeRemaining;
  };

  const categories = [...new Set(competitions.map(c => c.category))];

  if (loading) {
    return (
      <div className={clsx(gamificationStyles.container.main, className)}>
        <div className="max-w-6xl mx-auto p-6">
          <div className={gamificationStyles.loading.skeleton + " h-8 w-64 mb-6"} />
          <div className={gamificationStyles.grid.cols2}>
            {Array.from({ length: 4 }).map((_, i) => (
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

  if (error) {
    return (
      <div className={clsx(gamificationStyles.container.main, className)}>
        <div className="max-w-6xl mx-auto p-6">
          <div className={gamificationStyles.container.section}>
            <div className="text-center py-12">
              <div className="text-red-500 text-6xl mb-4">⚠️</div>
              <h3 className={gamificationStyles.typography.heading.secondary}>
                Failed to Load Competitions
              </h3>
              <p className={gamificationStyles.typography.body.regular}>
                {error}
              </p>
              <button
                onClick={fetchCompetitions}
                className={clsx(gamificationStyles.buttons.primary, "mt-4")}
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={clsx(gamificationStyles.container.main, className)}>
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className={clsx(gamificationStyles.typography.heading.primary, "flex items-center")}>
            <TrophyIcon className="w-8 h-8 mr-3 text-yellow-500" />
            Social Competitions
          </h1>
          <p className={gamificationStyles.typography.body.regular}>
            Compete with creators worldwide in exciting tournaments and events
          </p>
        </div>

        {/* Filters */}
        <div className={clsx(gamificationStyles.container.section, "mb-6")}>
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex gap-3">
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as any)}
                className={gamificationStyles.forms.select}
              >
                <option value="all">All Competitions</option>
                <option value="upcoming">Upcoming</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
              </select>

              {categories.length > 0 && (
                <select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  className={gamificationStyles.forms.select}
                >
                  <option value="">All Categories</option>
                  {categories.map(category => (
                    <option key={category} value={category}>
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </option>
                  ))}
                </select>
              )}

              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className={gamificationStyles.forms.select}
              >
                <option value="startDate">Sort by Date</option>
                <option value="prizePool">Sort by Prize Pool</option>
                <option value="participants">Sort by Participants</option>
              </select>
            </div>
          </div>
        </div>

        {/* Competitions Grid */}
        <div className={gamificationStyles.grid.cols2}>
          {competitions.map((competition) => (
            <div
              key={competition.id}
              className={clsx(
                gamificationStyles.container.card,
                "cursor-pointer transition-all duration-300 hover:shadow-lg",
                competition.isParticipating && "ring-2 ring-blue-500"
              )}
              onClick={() => onCompetitionDetails?.(competition)}
            >
              {/* Header */}
              <div className={gamificationStyles.utils.flexBetween + " mb-3"}>
                <div className={clsx(
                  "inline-flex items-center px-3 py-1 rounded-full text-sm font-medium",
                  getStatusColor(competition.status)
                )}>
                  {getStatusIcon(competition.status)}
                  <span className="ml-1 capitalize">{competition.status}</span>
                </div>
                {competition.isParticipating && (
                  <div className={gamificationStyles.badges.featured}>
                    Participating
                  </div>
                )}
              </div>

              {/* Competition Info */}
              <h3 className={clsx(gamificationStyles.typography.body.large, "font-semibold mb-2")}>
                {competition.title}
              </h3>
              <p className={clsx(gamificationStyles.typography.body.small, "mb-4")}>
                {competition.description}
              </p>

              {/* Metadata */}
              <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-500 flex items-center">
                    <UsersIcon className="w-4 h-4 mr-1" />
                    Participants:
                  </span>
                  <span className="font-medium">
                    {competition.participants.length}
                    {competition.maxParticipants && `/${competition.maxParticipants}`}
                  </span>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-500 flex items-center">
                    <CurrencyDollarIcon className="w-4 h-4 mr-1" />
                    Prize Pool:
                  </span>
                  <span className="font-bold text-green-600">
                    ${competition.prizePool.toLocaleString()}
                  </span>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-500 flex items-center">
                    <ClockIcon className="w-4 h-4 mr-1" />
                    Time:
                  </span>
                  <span className="font-medium">
                    {formatTimeRemaining(competition)}
                  </span>
                </div>

                {competition.userRank && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-500">Your Rank:</span>
                    <span className="font-bold text-blue-600">
                      #{competition.userRank}
                    </span>
                  </div>
                )}
              </div>

              {/* Top Participants Preview */}
              {competition.leaderboard.length > 0 && (
                <div className="mb-4 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <div className={clsx(gamificationStyles.typography.body.small, "font-medium mb-2")}>
                    Top Participants
                  </div>
                  <div className="space-y-1">
                    {competition.leaderboard.slice(0, 3).map((participant, index) => (
                      <div key={participant.userId} className="flex items-center justify-between">
                        <div className="flex items-center">
                          <span className={clsx(
                            "text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center mr-2",
                            index === 0 && "bg-yellow-100 text-yellow-800",
                            index === 1 && "bg-slate-100 text-slate-800",
                            index === 2 && "bg-orange-100 text-orange-800",
                            index > 2 && "bg-slate-100 text-slate-600"
                          )}>
                            {index + 1}
                          </span>
                          <span className={clsx(
                            gamificationStyles.typography.body.small,
                            participant.isCurrentUser && "font-bold text-blue-600"
                          )}>
                            {participant.username}
                            {participant.isCurrentUser && " (You)"}
                          </span>
                        </div>
                        <span className={gamificationStyles.typography.body.small}>
                          {participant.score.toLocaleString()}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Prizes Preview */}
              {competition.prizes.length > 0 && (
                <div className="mb-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                  <div className={clsx(gamificationStyles.typography.body.small, "font-medium mb-2 flex items-center")}>
                    <StarIcon className="w-4 h-4 mr-1 text-yellow-600" />
                    Prize Rewards
                  </div>
                  <div className="space-y-1">
                    {competition.prizes.slice(0, 3).map((prize, index) => (
                      <div key={prize.id} className="flex items-center text-xs">
                        <span className="mr-2">
                          {index === 0 && "🥇"}
                          {index === 1 && "🥈"}
                          {index === 2 && "🥉"}
                          {index > 2 && `#${index + 1}`}
                        </span>
                        <span>{prize.title}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Entry Fee */}
              {competition.entryFee && competition.entryFee > 0 && (
                <div className="mb-4 p-2 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                  <div className={clsx(gamificationStyles.typography.body.small, "text-orange-800 dark:text-orange-300")}>
                    Entry Fee: {competition.entryFee} points
                  </div>
                </div>
              )}

              {/* Action Button */}
              <div className="mt-auto">
                {competition.status === 'completed' ? (
                  <button
                    disabled
                    className={clsx(gamificationStyles.buttons.secondary, "w-full cursor-not-allowed opacity-60")}
                  >
                    <CheckCircleIcon className="w-4 h-4 mr-2" />
                    Completed
                  </button>
                ) : competition.status === 'cancelled' ? (
                  <button
                    disabled
                    className={clsx(gamificationStyles.buttons.danger, "w-full cursor-not-allowed opacity-60")}
                  >
                    <ExclamationTriangleIcon className="w-4 h-4 mr-2" />
                    Cancelled
                  </button>
                ) : competition.isParticipating ? (
                  <button
                    disabled
                    className={clsx(gamificationStyles.buttons.success, "w-full cursor-not-allowed")}
                  >
                    <CheckCircleIcon className="w-4 h-4 mr-2" />
                    Participating
                  </button>
                ) : competition.canJoin ? (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleJoinCompetition(competition);
                    }}
                    disabled={joiningId === competition.id}
                    className={clsx(gamificationStyles.buttons.primary, "w-full")}
                  >
                    {joiningId === competition.id ? (
                      <>
                        <div className={gamificationStyles.loading.spinner + " mr-2"} />
                        Joining...
                      </>
                    ) : (
                      <>
                        <PlayIcon className="w-4 h-4 mr-2" />
                        Join Competition
                      </>
                    )}
                  </button>
                ) : (
                  <button
                    disabled
                    className={clsx(gamificationStyles.buttons.secondary, "w-full cursor-not-allowed opacity-60")}
                    title={competition.joinReason}
                  >
                    {competition.joinReason || "Cannot Join"}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* No Results */}
        {!loading && competitions.length === 0 && (
          <div className={gamificationStyles.container.section}>
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🏆</div>
              <h3 className={gamificationStyles.typography.heading.secondary}>
                No Competitions Found
              </h3>
              <p className={gamificationStyles.typography.body.regular}>
                No competitions match your current criteria. Try adjusting your filters or check back later for new competitions.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SocialCompetitions;