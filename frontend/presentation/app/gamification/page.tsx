/**
 * Gamification Hub - Engaging User Experience
 * 
 * @fileoverview Gamification features for user engagement and motivation
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

'use client';

import React, { useState } from 'react';

// Simplified gamification interface - enterprise components will be added later
const GamificationHub: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('achievements');

  const mockAchievements = [
    { id: 1, title: 'First Upload', description: 'Upload your first content', completed: true, points: 100 },
    { id: 2, title: 'Content Creator', description: 'Upload 10 pieces of content', completed: false, points: 500 },
    { id: 3, title: 'Security Master', description: 'Enable advanced protection', completed: true, points: 250 }
  ];

  const mockLeaderboard = [
    { id: 1, username: 'CreatorPro', points: 2450, rank: 1 },
    { id: 2, username: 'AudioMaster', points: 2100, rank: 2 },
    { id: 3, username: 'VideoExpert', points: 1875, rank: 3 }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'achievements':
        return (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold mb-4">Your Achievements</h3>
            {mockAchievements.map((achievement) => (
              <div
                key={achievement.id}
                className={`p-4 rounded-lg border ${
                  achievement.completed
                    ? 'bg-green-50 border-green-200'
                    : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium">{achievement.title}</h4>
                    <p className="text-sm text-gray-600">{achievement.description}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-blue-600">
                      {achievement.points} pts
                    </div>
                    {achievement.completed && (
                      <div className="text-xs text-green-600">✅ Completed</div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        );
      case 'leaderboard':
        return (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold mb-4">Leaderboard</h3>
            {mockLeaderboard.map((user) => (
              <div
                key={user.id}
                className="flex items-center justify-between p-4 bg-white rounded-lg border"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-blue-600">#{user.rank}</span>
                  </div>
                  <span className="font-medium">{user.username}</span>
                </div>
                <div className="text-blue-600 font-semibold">{user.points} pts</div>
              </div>
            ))}
          </div>
        );
      case 'challenges':
        return (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold mb-4">Daily Challenges</h3>
            <div className="p-6 bg-gradient-to-r from-purple-100 to-blue-100 rounded-lg">
              <h4 className="font-semibold text-lg mb-2">Upload Challenge</h4>
              <p className="text-gray-700 mb-4">
                Upload 3 pieces of content today to earn bonus points!
              </p>
              <div className="bg-white rounded-full h-2 mb-2">
                <div className="bg-purple-500 h-2 rounded-full" style={{ width: '33%' }}></div>
              </div>
              <div className="text-sm text-gray-600">1/3 uploads completed</div>
            </div>
          </div>
        );
      default:
        return <div>Select a tab to view content</div>;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Gamification Hub</h1>
          <p className="text-gray-600">
            Track your progress, earn achievements, and compete with other creators
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 mb-6 bg-gray-200 p-1 rounded-lg w-fit">
          {[
            { id: 'achievements', label: 'Achievements' },
            { id: 'leaderboard', label: 'Leaderboard' },
            { id: 'challenges', label: 'Challenges' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-md transition-colors ${
                activeTab === tab.id
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow p-6">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default GamificationHub;