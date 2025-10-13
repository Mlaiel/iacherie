/**
 * Badge Collection - Ultra-Advanced Enterprise System
 * 
 * This component provides comprehensive badge collection management with
 * showcase gallery and achievement tracking.
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
import { Badge, AchievementTier, ApiResponse } from '../types';
import { gamificationStyles, tierIcons } from '../gamification.styles';
import { StarIcon, LockClosedIcon, SparklesIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface BadgeCollectionProps {
  userId: string;
  className?: string;
  onBadgeClick?: (badge: Badge) => void;
  showEarnedOnly?: boolean;
}

const BadgeCollection: React.FC<BadgeCollectionProps> = ({
  userId,
  className,
  onBadgeClick,
  showEarnedOnly = false
}) => {
  const [badges, setBadges] = useState<Badge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBadges = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/gamification/badges?userId=${userId}&earnedOnly=${showEarnedOnly}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
      });
      const result: ApiResponse<Badge[]> = await response.json();
      if (result.success) setBadges(result.data!);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load badges');
    } finally {
      setLoading(false);
    }
  }, [userId, showEarnedOnly]);

  useEffect(() => {
    fetchBadges();
  }, [fetchBadges]);

  if (loading) {
    return (
      <div className={clsx(gamificationStyles.container.main, className)}>
        <div className="max-w-6xl mx-auto p-6">
          <div className={gamificationStyles.grid.cols6}>
            {Array.from({ length: 12 }).map((_, i) => (
              <div key={i} className={gamificationStyles.container.card}>
                <div className={gamificationStyles.loading.skeleton + " h-16 w-16 rounded-full mx-auto mb-3"} />
                <div className={gamificationStyles.loading.skeleton + " h-4 w-full"} />
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={clsx(gamificationStyles.container.main, className)}>
      <div className="max-w-6xl mx-auto p-6">
        <div className="mb-8">
          <h1 className={clsx(gamificationStyles.typography.heading.primary, "flex items-center")}>
            <StarIcon className="w-8 h-8 mr-3 text-yellow-500" />
            Badge Collection
          </h1>
          <p className={gamificationStyles.typography.body.regular}>
            Showcase your achievements with exclusive badges earned through your creator journey
          </p>
        </div>

        <div className={gamificationStyles.grid.cols6}>
          {badges.map((badge) => (
            <div
              key={badge.id}
              className={clsx(
                gamificationStyles.container.card,
                "text-center cursor-pointer transition-all duration-300 hover:shadow-lg",
                badge.earnedAt ? "hover:scale-105" : "opacity-50 grayscale"
              )}
              onClick={() => onBadgeClick?.(badge)}
            >
              <div className={clsx(
                "w-16 h-16 mx-auto mb-3 rounded-full flex items-center justify-center text-2xl",
                gamificationStyles.achievementTiers[badge.tier].bg
              )}>
                {badge.earnedAt ? badge.icon : <LockClosedIcon className="w-8 h-8 text-slate-400" />}
              </div>
              <h3 className={clsx(gamificationStyles.typography.body.regular, "font-medium mb-1")}>
                {badge.name}
              </h3>
              <p className={clsx(gamificationStyles.typography.body.small, "mb-2")}>
                {badge.description}
              </p>
              {badge.isRare && (
                <div className={gamificationStyles.badges.rare}>
                  <SparklesIcon className="w-3 h-3 mr-1" />
                  Rare
                </div>
              )}
              {badge.earnedAt && (
                <div className={gamificationStyles.typography.body.small}>
                  Earned: {new Date(badge.earnedAt).toLocaleDateString()}
                </div>
              )}
            </div>
          ))}
        </div>

        {badges.length === 0 && (
          <div className={gamificationStyles.container.section}>
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🏅</div>
              <h3 className={gamificationStyles.typography.heading.secondary}>No Badges Yet</h3>
              <p className={gamificationStyles.typography.body.regular}>
                Start completing achievements to earn your first badges!
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BadgeCollection;