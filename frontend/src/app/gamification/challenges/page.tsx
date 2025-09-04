/**
 * Challenges Page - Ultra-Advanced Enterprise System
 * 
 * This page provides comprehensive challenge management with
 * advanced filtering and participation tracking.
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

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { 
  ChallengeInterface,
  ChallengeCreator
} from '@/components/gamification';
import { Challenge, ChallengeCreatorData } from '@/components/gamification/types';
import { gamificationStyles } from '@/components/gamification/gamification.styles';
import { 
  FireIcon,
  PlusIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

const ChallengesPage: React.FC = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [userId, setUserId] = useState<string>('current-user-id');
  const [activeView, setActiveView] = useState<'browse' | 'create'>('browse');
  const [selectedChallenge, setSelectedChallenge] = useState<Challenge | null>(null);

  useEffect(() => {
    // Check for specific challenge ID in URL
    const challengeId = searchParams?.get('id');
    if (challengeId) {
      // Could fetch and display specific challenge details
      console.log('Viewing challenge:', challengeId);
    }
  }, [searchParams]);

  const handleChallengeJoin = async (challengeId: string): Promise<void> => {
    try {
      const response = await fetch(`/api/gamification/challenges/${challengeId}/join`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify({ userId })
      });

      if (!response.ok) {
        throw new Error('Failed to join challenge');
      }

      console.log('Successfully joined challenge:', challengeId);
    } catch (err) {
      console.error('Error joining challenge:', err);
      throw err;
    }
  };

  const handleChallengeLeave = async (challengeId: string): Promise<void> => {
    try {
      const response = await fetch(`/api/gamification/challenges/${challengeId}/leave`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify({ userId })
      });

      if (!response.ok) {
        throw new Error('Failed to leave challenge');
      }

      console.log('Successfully left challenge:', challengeId);
    } catch (err) {
      console.error('Error leaving challenge:', err);
      throw err;
    }
  };

  const handleChallengeDetails = (challenge: Challenge) => {
    setSelectedChallenge(challenge);
    // Could also open a modal or navigate to details page
    console.log('Viewing challenge details:', challenge);
  };

  const handleChallengeCreate = async (challengeData: ChallengeCreatorData): Promise<boolean> => {
    try {
      const response = await fetch('/api/gamification/challenges', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify({
          ...challengeData,
          creatorId: userId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create challenge');
      }

      console.log('Successfully created challenge');
      return true;
    } catch (err) {
      console.error('Error creating challenge:', err);
      return false;
    }
  };

  const handleBackToGamification = () => {
    router.push('/gamification');
  };

  return (
    <div className={gamificationStyles.container.main}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
          <div className="px-6 py-4">
            <div className={gamificationStyles.utils.flexBetween}>
              <div className="flex items-center">
                <button
                  onClick={handleBackToGamification}
                  className={clsx(gamificationStyles.buttons.ghost, "mr-4")}
                >
                  <ArrowLeftIcon className="w-4 h-4 mr-2" />
                  Back to Gamification
                </button>
                <div>
                  <h1 className={clsx(gamificationStyles.typography.heading.primary, "flex items-center mb-2")}>
                    <FireIcon className="w-8 h-8 mr-3 text-orange-500" />
                    Challenge Center
                  </h1>
                  <p className={gamificationStyles.typography.body.regular}>
                    {activeView === 'browse' 
                      ? 'Discover and participate in exciting challenges from the creator community'
                      : 'Create new challenges for the creator community to participate in'
                    }
                  </p>
                </div>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setActiveView('browse')}
                  className={clsx(
                    activeView === 'browse' ? gamificationStyles.buttons.primary : gamificationStyles.buttons.ghost
                  )}
                >
                  Browse Challenges
                </button>
                <button
                  onClick={() => setActiveView('create')}
                  className={clsx(
                    activeView === 'create' ? gamificationStyles.buttons.primary : gamificationStyles.buttons.ghost
                  )}
                >
                  <PlusIcon className="w-4 h-4 mr-2" />
                  Create Challenge
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="min-h-screen">
          {activeView === 'browse' ? (
            <ChallengeInterface
              userId={userId}
              onChallengeJoin={handleChallengeJoin}
              onChallengeLeave={handleChallengeLeave}
              onChallengeDetails={handleChallengeDetails}
            />
          ) : (
            <ChallengeCreator
              userId={userId}
              onChallengeCreate={handleChallengeCreate}
              onCancel={() => setActiveView('browse')}
            />
          )}
        </div>

        {/* Challenge Details Modal/Sidebar */}
        {selectedChallenge && (
          <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div className={clsx(
              gamificationStyles.container.section,
              "max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            )}>
              <div className={gamificationStyles.utils.flexBetween + " mb-4"}>
                <h2 className={gamificationStyles.typography.heading.secondary}>
                  {selectedChallenge.title}
                </h2>
                <button
                  onClick={() => setSelectedChallenge(null)}
                  className={gamificationStyles.buttons.ghost}
                >
                  ✕
                </button>
              </div>
              
              <div className="space-y-4">
                <p className={gamificationStyles.typography.body.regular}>
                  {selectedChallenge.description}
                </p>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className={gamificationStyles.typography.body.small + " font-medium"}>
                      Challenge Type
                    </div>
                    <div className={gamificationStyles.typography.body.regular}>
                      {selectedChallenge.type}
                    </div>
                  </div>
                  
                  <div>
                    <div className={gamificationStyles.typography.body.small + " font-medium"}>
                      Difficulty
                    </div>
                    <div className={gamificationStyles.typography.body.regular}>
                      {selectedChallenge.difficulty}/5
                    </div>
                  </div>
                  
                  <div>
                    <div className={gamificationStyles.typography.body.small + " font-medium"}>
                      Participants
                    </div>
                    <div className={gamificationStyles.typography.body.regular}>
                      {selectedChallenge.participants.length}
                      {selectedChallenge.maxParticipants && ` / ${selectedChallenge.maxParticipants}`}
                    </div>
                  </div>
                  
                  <div>
                    <div className={gamificationStyles.typography.body.small + " font-medium"}>
                      Status
                    </div>
                    <div className={clsx(
                      gamificationStyles.typography.body.regular,
                      "capitalize font-medium",
                      selectedChallenge.status === 'active' && "text-green-600",
                      selectedChallenge.status === 'completed' && "text-blue-600",
                      selectedChallenge.status === 'expired' && "text-red-600"
                    )}>
                      {selectedChallenge.status}
                    </div>
                  </div>
                </div>

                {selectedChallenge.rewards && Object.keys(selectedChallenge.rewards).length > 0 && (
                  <div>
                    <div className={gamificationStyles.typography.body.small + " font-medium mb-2"}>
                      Rewards
                    </div>
                    <div className="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded-lg">
                      <div className={gamificationStyles.typography.body.small}>
                        {selectedChallenge.rewards.xp && `${selectedChallenge.rewards.xp} Experience Points`}
                        {selectedChallenge.rewards.currency && ` • ${selectedChallenge.rewards.currency} Virtual Currency`}
                        {selectedChallenge.rewards.badge && ` • Special Badge`}
                      </div>
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
                  <div className="flex gap-3">
                    <button
                      onClick={() => {
                        if (selectedChallenge.participants.includes(userId)) {
                          handleChallengeLeave(selectedChallenge.id);
                        } else {
                          handleChallengeJoin(selectedChallenge.id);
                        }
                        setSelectedChallenge(null);
                      }}
                      className={clsx(
                        selectedChallenge.participants.includes(userId)
                          ? gamificationStyles.buttons.warning
                          : gamificationStyles.buttons.primary,
                        "flex-1"
                      )}
                    >
                      {selectedChallenge.participants.includes(userId) ? 'Leave Challenge' : 'Join Challenge'}
                    </button>
                    <button
                      onClick={() => setSelectedChallenge(null)}
                      className={clsx(gamificationStyles.buttons.ghost, "flex-1")}
                    >
                      Close
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChallengesPage;