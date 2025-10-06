'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Trophy, Award, TrendingUp, Target, Zap, Crown, Star, Users, Medal, Loader2 } from 'lucide-react';

interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  rarity: 'COMMON' | 'UNCOMMON' | 'RARE' | 'EPIC' | 'LEGENDARY';
  points_value: number;
  category: string;
  unlocked: boolean;
  unlocked_at?: string;
}

interface Achievement {
  id: string;
  name: string;
  description: string;
  achievement_type: string;
  points_value: number;
  rarity: string;
  progress: number;
  completed: boolean;
}

interface LeaderboardEntry {
  rank: number;
  user_id: string;
  username: string;
  avatar: string;
  score: number;
  achievements_count: number;
  badges_count: number;
}

interface UserStats {
  total_points: number;
  level: number;
  achievements_unlocked: number;
  badges_earned: number;
  rank: number;
  next_level_points: number;
}

export default function GamificationPage() {
  const [badges, setBadges] = useState<Badge[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState<'badges' | 'achievements' | 'leaderboard'>('badges');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);

      // Fetch user stats
      const statsResponse = await fetch('http://localhost:8000/gamification/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (statsResponse.ok) {
        const data = await statsResponse.json();
        setUserStats(data.stats);
      }

      // Fetch badges
      const badgesResponse = await fetch('http://localhost:8000/gamification/badges', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (badgesResponse.ok) {
        const data = await badgesResponse.json();
        setBadges(data.badges || []);
      }

      // Fetch achievements
      const achievementsResponse = await fetch('http://localhost:8000/gamification/achievements', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (achievementsResponse.ok) {
        const data = await achievementsResponse.json();
        setAchievements(data.achievements || []);
      }

      // Fetch leaderboard
      const leaderboardResponse = await fetch('http://localhost:8000/gamification/leaderboard');
      if (leaderboardResponse.ok) {
        const data = await leaderboardResponse.json();
        setLeaderboard(data.leaderboard || []);
      }
    } catch (error) {
      console.error('Error fetching gamification data:', error);
    } finally {
      setLoading(false);
    }
  };

  const rarityColors = {
    COMMON: { bg: 'bg-gray-100', text: 'text-gray-700', border: 'border-gray-300' },
    UNCOMMON: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-300' },
    RARE: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-300' },
    EPIC: { bg: 'bg-purple-100', text: 'text-purple-700', border: 'border-purple-300' },
    LEGENDARY: { bg: 'bg-yellow-100', text: 'text-yellow-700', border: 'border-yellow-300' },
  };

  const categories = ['all', 'content', 'collaboration', 'social', 'skill', 'milestone'];

  const filteredBadges = selectedCategory === 'all'
    ? badges
    : badges.filter(b => b.category === selectedCategory);

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-white to-yellow-50">
      {/* Header */}
      <div className="bg-white shadow-md border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-600 hover:text-amber-600 transition">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <Trophy className="h-8 w-8 text-amber-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Gamification Hub</h1>
                <p className="text-sm text-gray-500">Badges • Achievements • Leaderboards • Challenges</p>
              </div>
            </div>
            {userStats && (
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <div className="text-sm font-semibold text-gray-700">Level {userStats.level}</div>
                  <div className="text-xs text-gray-500">{userStats.total_points} points</div>
                </div>
                <div className="w-12 h-12 bg-gradient-to-br from-amber-400 to-yellow-500 rounded-full flex items-center justify-center text-white font-bold text-xl">
                  {userStats.level}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* User Stats Cards */}
        {userStats && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <Star className="h-8 w-8 text-yellow-600" />
                  <span className="text-xs text-gray-500">Total</span>
                </div>
                <div className="text-2xl font-bold text-gray-900">{userStats.total_points.toLocaleString()}</div>
                <div className="text-sm text-gray-600">Experience Points</div>
              </div>

              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <Trophy className="h-8 w-8 text-amber-600" />
                  <span className="text-xs text-gray-500">Unlocked</span>
                </div>
                <div className="text-2xl font-bold text-gray-900">{userStats.achievements_unlocked}</div>
                <div className="text-sm text-gray-600">Achievements</div>
              </div>

              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <Award className="h-8 w-8 text-blue-600" />
                  <span className="text-xs text-gray-500">Earned</span>
                </div>
                <div className="text-2xl font-bold text-gray-900">{userStats.badges_earned}</div>
                <div className="text-sm text-gray-600">Badges</div>
              </div>

              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <Crown className="h-8 w-8 text-purple-600" />
                  <span className="text-xs text-gray-500">Rank</span>
                </div>
                <div className="text-2xl font-bold text-gray-900">#{userStats.rank}</div>
                <div className="text-sm text-gray-600">Global Ranking</div>
              </div>
            </div>

            {/* Level Progress */}
            <div className="bg-gradient-to-r from-amber-500 to-yellow-500 rounded-xl shadow-lg p-6 mb-8 text-white">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <div className="text-sm opacity-90">Level {userStats.level}</div>
                  <div className="text-2xl font-bold">Progress to Level {userStats.level + 1}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm opacity-90">
                    {userStats.total_points % 1000} / {userStats.next_level_points}
                  </div>
                  <div className="text-xs opacity-75">points needed</div>
                </div>
              </div>
              <div className="w-full bg-white bg-opacity-30 rounded-full h-4">
                <div
                  className="bg-white h-4 rounded-full transition-all"
                  style={{ width: `${((userStats.total_points % 1000) / userStats.next_level_points) * 100}%` }}
                />
              </div>
            </div>
          </>
        )}

        {/* Tabs */}
        <div className="flex space-x-2 mb-8">
          <button
            onClick={() => setSelectedTab('badges')}
            className={`flex-1 py-4 px-6 rounded-xl font-semibold transition ${
              selectedTab === 'badges'
                ? 'bg-white shadow-lg text-amber-600'
                : 'bg-white/50 text-gray-600 hover:bg-white/80'
            }`}
          >
            <Award className="h-5 w-5 inline-block mr-2" />
            Badges
          </button>
          <button
            onClick={() => setSelectedTab('achievements')}
            className={`flex-1 py-4 px-6 rounded-xl font-semibold transition ${
              selectedTab === 'achievements'
                ? 'bg-white shadow-lg text-amber-600'
                : 'bg-white/50 text-gray-600 hover:bg-white/80'
            }`}
          >
            <Trophy className="h-5 w-5 inline-block mr-2" />
            Achievements
          </button>
          <button
            onClick={() => setSelectedTab('leaderboard')}
            className={`flex-1 py-4 px-6 rounded-xl font-semibold transition ${
              selectedTab === 'leaderboard'
                ? 'bg-white shadow-lg text-amber-600'
                : 'bg-white/50 text-gray-600 hover:bg-white/80'
            }`}
          >
            <Users className="h-5 w-5 inline-block mr-2" />
            Leaderboard
          </button>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-12 w-12 animate-spin text-amber-600" />
          </div>
        ) : (
          <>
            {/* Badges Tab */}
            {selectedTab === 'badges' && (
              <div>
                {/* Category Filter */}
                <div className="flex space-x-2 mb-6 overflow-x-auto">
                  {categories.map((cat) => (
                    <button
                      key={cat}
                      onClick={() => setSelectedCategory(cat)}
                      className={`px-4 py-2 rounded-lg font-semibold whitespace-nowrap transition ${
                        selectedCategory === cat
                          ? 'bg-amber-600 text-white'
                          : 'bg-white text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      {cat.charAt(0).toUpperCase() + cat.slice(1)}
                    </button>
                  ))}
                </div>

                {/* Badges Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                  {filteredBadges.map((badge) => {
                    const rarityStyle = rarityColors[badge.rarity];
                    return (
                      <div
                        key={badge.id}
                        className={`bg-white rounded-xl shadow-lg p-4 border-2 ${rarityStyle.border} ${
                          badge.unlocked ? '' : 'opacity-40 grayscale'
                        } hover:scale-105 transition-transform cursor-pointer`}
                      >
                        <div className="text-4xl text-center mb-2">{badge.icon}</div>
                        <div className={`text-xs px-2 py-0.5 rounded-full text-center mb-2 ${rarityStyle.bg} ${rarityStyle.text} font-semibold`}>
                          {badge.rarity}
                        </div>
                        <div className="text-sm font-bold text-gray-900 text-center mb-1">{badge.name}</div>
                        <div className="text-xs text-gray-600 text-center mb-2">{badge.description}</div>
                        <div className="text-center">
                          <span className="text-xs font-semibold text-amber-600">{badge.points_value} pts</span>
                        </div>
                        {badge.unlocked && badge.unlocked_at && (
                          <div className="text-xs text-green-600 text-center mt-2">
                            ✓ Unlocked
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Achievements Tab */}
            {selectedTab === 'achievements' && (
              <div className="space-y-4">
                {achievements.map((achievement) => (
                  <div key={achievement.id} className="bg-white rounded-xl shadow-lg p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="text-lg font-bold text-gray-900">{achievement.name}</h3>
                          {achievement.completed && (
                            <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full font-semibold">
                              Completed ✓
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mb-3">{achievement.description}</p>
                        <div className="flex items-center space-x-4 text-sm">
                          <span className="text-amber-600 font-semibold">{achievement.points_value} points</span>
                          <span className="text-gray-500">•</span>
                          <span className="text-gray-600">{achievement.achievement_type}</span>
                          <span className="text-gray-500">•</span>
                          <span className={`${rarityColors[achievement.rarity as keyof typeof rarityColors].text} font-semibold`}>
                            {achievement.rarity}
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-amber-600">{achievement.progress}%</div>
                        <div className="text-xs text-gray-500">Progress</div>
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-amber-600 to-yellow-500 h-2 rounded-full transition-all"
                        style={{ width: `${achievement.progress}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Leaderboard Tab */}
            {selectedTab === 'leaderboard' && (
              <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gradient-to-r from-amber-500 to-yellow-500 text-white">
                      <tr>
                        <th className="px-6 py-4 text-left font-semibold">Rank</th>
                        <th className="px-6 py-4 text-left font-semibold">Player</th>
                        <th className="px-6 py-4 text-center font-semibold">Score</th>
                        <th className="px-6 py-4 text-center font-semibold">Achievements</th>
                        <th className="px-6 py-4 text-center font-semibold">Badges</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {leaderboard.map((entry) => (
                        <tr key={entry.user_id} className={`hover:bg-amber-50 transition ${
                          entry.rank <= 3 ? 'bg-amber-50/50' : ''
                        }`}>
                          <td className="px-6 py-4">
                            <div className="flex items-center space-x-2">
                              {entry.rank === 1 && <Crown className="h-5 w-5 text-yellow-500" />}
                              {entry.rank === 2 && <Medal className="h-5 w-5 text-gray-400" />}
                              {entry.rank === 3 && <Medal className="h-5 w-5 text-amber-600" />}
                              <span className="font-bold text-lg">{entry.rank}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center space-x-3">
                              <div className="w-10 h-10 bg-gradient-to-br from-amber-400 to-yellow-500 rounded-full flex items-center justify-center text-white font-bold">
                                {entry.username.charAt(0).toUpperCase()}
                              </div>
                              <div>
                                <div className="font-semibold text-gray-900">{entry.username}</div>
                                <div className="text-xs text-gray-500">ID: {entry.user_id.substring(0, 8)}...</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <div className="text-lg font-bold text-amber-600">{entry.score.toLocaleString()}</div>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <div className="font-semibold text-gray-900">{entry.achievements_count}</div>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <div className="font-semibold text-gray-900">{entry.badges_count}</div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
