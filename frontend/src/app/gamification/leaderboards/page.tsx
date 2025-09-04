/**
 * Leaderboards Page - Ultra-Advanced Enterprise System
 * 
 * This page provides comprehensive leaderboard visualization with
 * competitive rankings and performance analytics.
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

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { LeaderboardComponent } from '@/components/gamification';
import { gamificationStyles } from '@/components/gamification/gamification.styles';
import { 
  TrophyIcon,
  ArrowLeftIcon,
  UserIcon,
  ChartBarIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

const LeaderboardsPage: React.FC = () => {
  const router = useRouter();
  const [userId] = useState<string>('current-user-id');
  const [selectedTimeframe, setSelectedTimeframe] = useState<'daily' | 'weekly' | 'monthly' | 'all_time'>('weekly');
  const [selectedCategory, setSelectedCategory] = useState<string>('global');
  const [selectedUser, setSelectedUser] = useState<string | null>(null);

  const handleBackToGamification = () => {
    router.push('/gamification');
  };

  const handleUserSelect = (selectedUserId: string) => {
    setSelectedUser(selectedUserId);
    // Could navigate to user profile or show user details
    console.log('Selected user:', selectedUserId);
  };

  const timeframes = [
    { value: 'daily', label: 'Daily Rankings', description: 'Top performers today' },
    { value: 'weekly', label: 'Weekly Rankings', description: 'This week\'s champions' },
    { value: 'monthly', label: 'Monthly Rankings', description: 'Monthly leaderboard' },
    { value: 'all_time', label: 'All-Time Rankings', description: 'Hall of fame' }
  ];

  const categories = [
    { value: 'global', label: 'Global', icon: GlobeAltIcon, description: 'All creators worldwide' },
    { value: 'content_creators', label: 'Content Creators', icon: UserIcon, description: 'General content creators' },
    { value: 'musicians', label: 'Musicians', icon: UserIcon, description: 'Music creators' },
    { value: 'bloggers', label: 'Bloggers', icon: UserIcon, description: 'Blog writers' },
    { value: 'photographers', label: 'Photographers', icon: UserIcon, description: 'Photo creators' },
    { value: 'influencers', label: 'Influencers', icon: UserIcon, description: 'Social influencers' },
    { value: 'comedians', label: 'Comedians', icon: UserIcon, description: 'Comedy creators' }
  ];

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
                    <TrophyIcon className="w-8 h-8 mr-3 text-yellow-500" />
                    Global Leaderboards
                  </h1>
                  <p className={gamificationStyles.typography.body.regular}>
                    Compete with creators worldwide and track your ranking progress across different categories
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <ChartBarIcon className="w-6 h-6 text-blue-500" />
                <span className={gamificationStyles.typography.body.regular}>
                  Live Rankings
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Timeframe Selection */}
        <div className="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
          <div className="px-6 py-4">
            <div className="flex flex-wrap gap-2">
              {timeframes.map((timeframe) => (
                <button
                  key={timeframe.value}
                  onClick={() => setSelectedTimeframe(timeframe.value as any)}
                  className={clsx(
                    "px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200",
                    selectedTimeframe === timeframe.value
                      ? "bg-blue-600 text-white"
                      : "bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700"
                  )}
                  title={timeframe.description}
                >
                  {timeframe.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Category Selection */}
        <div className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
          <div className="px-6 py-4">
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => {
                const Icon = category.icon;
                return (
                  <button
                    key={category.value}
                    onClick={() => setSelectedCategory(category.value)}
                    className={clsx(
                      "flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200",
                      selectedCategory === category.value
                        ? "bg-purple-600 text-white"
                        : "bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-600"
                    )}
                    title={category.description}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {category.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Current Selection Info */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-b border-slate-200 dark:border-slate-700">
          <div className="px-6 py-3">
            <div className={gamificationStyles.utils.flexBetween}>
              <div>
                <h2 className={clsx(gamificationStyles.typography.body.large, "font-semibold")}>
                  {categories.find(c => c.value === selectedCategory)?.label} - {timeframes.find(t => t.value === selectedTimeframe)?.label}
                </h2>
                <p className={clsx(gamificationStyles.typography.body.small, "text-slate-600 dark:text-slate-400")}>
                  {categories.find(c => c.value === selectedCategory)?.description} • {timeframes.find(t => t.value === selectedTimeframe)?.description}
                </p>
              </div>
              <div className="text-right">
                <div className={clsx(gamificationStyles.typography.body.small, "text-slate-500")}>
                  Last updated
                </div>
                <div className={clsx(gamificationStyles.typography.body.regular, "font-medium")}>
                  {new Date().toLocaleTimeString()}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Leaderboard Content */}
        <div className="min-h-screen">
          <LeaderboardComponent
            userId={userId}
            initialTimeframe={selectedTimeframe}
            initialCategory={selectedCategory}
            onUserSelect={handleUserSelect}
            showUserHighlight={true}
            maxEntries={100}
          />
        </div>

        {/* User Profile Modal/Sidebar */}
        {selectedUser && (
          <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div className={clsx(
              gamificationStyles.container.section,
              "max-w-md w-full max-h-[80vh] overflow-y-auto"
            )}>
              <div className={gamificationStyles.utils.flexBetween + " mb-4"}>
                <h2 className={gamificationStyles.typography.heading.secondary}>
                  User Profile
                </h2>
                <button
                  onClick={() => setSelectedUser(null)}
                  className={gamificationStyles.buttons.ghost}
                >
                  ✕
                </button>
              </div>
              
              <div className="text-center mb-6">
                <div className="w-20 h-20 bg-slate-200 dark:bg-slate-700 rounded-full mx-auto mb-3 flex items-center justify-center">
                  <UserIcon className="w-10 h-10 text-slate-500" />
                </div>
                <h3 className={clsx(gamificationStyles.typography.body.large, "font-semibold mb-1")}>
                  User #{selectedUser}
                </h3>
                <div className={clsx(gamificationStyles.typography.body.small, "text-slate-500")}>
                  Creator Profile
                </div>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className={gamificationStyles.stats.card}>
                    <div className={gamificationStyles.stats.label}>Current Rank</div>
                    <div className={clsx(gamificationStyles.stats.value, "text-blue-600")}>
                      #42
                    </div>
                  </div>
                  <div className={gamificationStyles.stats.card}>
                    <div className={gamificationStyles.stats.label}>Total Score</div>
                    <div className={clsx(gamificationStyles.stats.value, "text-green-600")}>
                      8,420
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <div>
                    <div className={gamificationStyles.typography.body.small + " font-medium mb-1"}>
                      Performance Trends
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Content Quality</span>
                        <span className="font-medium">94%</span>
                      </div>
                      <div className={gamificationStyles.progress.container}>
                        <div className={gamificationStyles.progress.bar} style={{ width: '94%' }} />
                      </div>
                    </div>
                  </div>

                  <div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Engagement Score</span>
                        <span className="font-medium">87%</span>
                      </div>
                      <div className={gamificationStyles.progress.container}>
                        <div className={gamificationStyles.progress.bar} style={{ width: '87%' }} />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
                  <div className="flex gap-3">
                    <button
                      onClick={() => {
                        console.log('View full profile for user:', selectedUser);
                        setSelectedUser(null);
                      }}
                      className={clsx(gamificationStyles.buttons.primary, "flex-1")}
                    >
                      View Full Profile
                    </button>
                    <button
                      onClick={() => setSelectedUser(null)}
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

export default LeaderboardsPage;