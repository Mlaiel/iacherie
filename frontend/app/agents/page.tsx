/**
 * AGENTS MARKETPLACE
 * Browse and interact with 3,054 AI agents across 5 categories
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import { useState, useEffect } from 'react';
import { useAgentsStore } from '@/lib/store/generated';
import { useWebSocketStatus } from '@/lib/websocket';
import { Bot, Search, Filter, Zap, TrendingUp, Shield, Briefcase, Sparkles } from 'lucide-react';

const CATEGORIES = [
  { id: 'all', name: 'All Agents', icon: Bot, count: 3054, color: 'from-blue-500 to-cyan-500' },
  { id: 'business', name: 'Business', icon: Briefcase, count: 610, color: 'from-green-500 to-emerald-500' },
  { id: 'technical', name: 'Technical', icon: Zap, count: 612, color: 'from-orange-500 to-red-500' },
  { id: 'creative', name: 'Creative', icon: Sparkles, count: 608, color: 'from-purple-500 to-pink-500' },
  { id: 'protection', name: 'Protection', icon: Shield, count: 612, color: 'from-indigo-500 to-blue-500' },
  { id: 'specialized', name: 'Specialized', icon: TrendingUp, count: 612, color: 'from-pink-500 to-rose-500' },
];

export default function AgentsPage() {
  const { items, loading, fetchItems } = useAgentsStore();
  const { connected } = useWebSocketStatus();
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchItems();
  }, []);

  const filteredAgents = items.filter(agent => {
    const matchesSearch = !searchQuery || 
      agent.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.description?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || agent.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900">AI Agents Marketplace</h1>
          </div>
          <p className="text-gray-600">
            Discover and deploy 3,054 specialized AI agents for every task
          </p>
          
          {/* Status */}
          <div className="mt-4 flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
            <span className="text-gray-600">
              {connected ? 'Real-time updates active' : 'Reconnecting...'}
            </span>
            {!loading && (
              <span className="text-gray-500 ml-4">
                {filteredAgents.length} agents available
              </span>
            )}
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <div className="flex gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search agents by name or description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            {/* Filter Button */}
            <button className="px-6 py-3 bg-gray-100 hover:bg-gray-200 rounded-lg flex items-center gap-2 font-medium transition">
              <Filter className="w-5 h-5" />
              Filters
            </button>
          </div>
        </div>

        {/* Categories */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          {CATEGORIES.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`relative bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden ${
                selectedCategory === category.id ? 'ring-2 ring-blue-500 shadow-lg' : ''
              }`}
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${category.color} ${
                selectedCategory === category.id ? 'opacity-10' : 'opacity-0'
              } transition-opacity`}></div>
              
              <div className="relative p-4 text-center">
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${category.color} flex items-center justify-center mx-auto mb-2`}>
                  <category.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-sm font-semibold text-gray-900 mb-1">{category.name}</h3>
                <p className="text-xs text-gray-500">{category.count.toLocaleString()}</p>
              </div>
            </button>
          ))}
        </div>

        {/* Agents Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        ) : filteredAgents.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 mb-2">No agents found</h3>
            <p className="text-gray-600">Try adjusting your search or filters</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAgents.slice(0, 12).map((agent) => (
              <div
                key={agent.id}
                className="bg-white rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden group cursor-pointer"
              >
                <div className="p-6">
                  {/* Icon & Category Badge */}
                  <div className="flex items-center justify-between mb-4">
                    <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${
                      CATEGORIES.find(c => c.id === agent.category)?.color || 'from-gray-500 to-gray-600'
                    } flex items-center justify-center`}>
                      <Bot className="w-6 h-6 text-white" />
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      agent.status === 'active' 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      {agent.status || 'active'}
                    </span>
                  </div>

                  {/* Content */}
                  <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition">
                    {agent.name || 'Unnamed Agent'}
                  </h3>
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                    {agent.description || 'No description available'}
                  </p>

                  {/* Stats */}
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span className="capitalize">{agent.category || 'general'}</span>
                    <span>ID: {agent.id.slice(0, 8)}</span>
                  </div>
                </div>

                {/* Action Footer */}
                <div className="bg-gray-50 px-6 py-3 flex items-center justify-between border-t border-gray-100">
                  <button className="text-sm font-medium text-blue-600 hover:text-blue-700">
                    View Details
                  </button>
                  <button className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition">
                    Deploy
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Load More */}
        {filteredAgents.length > 12 && (
          <div className="mt-8 text-center">
            <button className="px-8 py-3 bg-white hover:bg-gray-50 rounded-lg shadow-sm text-gray-900 font-medium transition">
              Load More Agents ({filteredAgents.length - 12} remaining)
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
