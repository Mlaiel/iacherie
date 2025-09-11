/**
 * 🎮 Features Interface Enterprise - Feature Management & Discovery
 * 
 * @fileoverview Advanced features interface for enterprise feature management
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

import React, { useState, useEffect } from 'react';

export interface Feature {
  id: string;
  name: string;
  description: string;
  category: 'ai' | 'content' | 'analytics' | 'monetization' | 'protection' | 'collaboration';
  status: 'available' | 'beta' | 'coming_soon' | 'premium' | 'enterprise';
  requirements: {
    plan: 'free' | 'pro' | 'enterprise';
    permissions: string[];
    dependencies: string[];
  };
  usage: {
    used: number;
    limit: number;
    period: string;
  };
  metrics: {
    popularity: number;
    userRating: number;
    lastUsed?: number;
  };
}

export interface FeatureCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  features: Feature[];
  enabled: boolean;
}

interface FeaturesInterfaceProps {
  userId?: string;
  userPlan?: string;
  onFeatureSelect?: (feature: Feature) => void;
  onFeatureToggle?: (featureId: string, enabled: boolean) => void;
}

export const FeaturesInterface: React.FC<FeaturesInterfaceProps> = ({
  userId,
  userPlan = 'free',
  onFeatureSelect,
  onFeatureToggle
}) => {
  const [categories, setCategories] = useState<FeatureCategory[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('ai');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadFeatures();
  }, [userId, userPlan]);

  const loadFeatures = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockCategories: FeatureCategory[] = [
        {
          id: 'ai',
          name: 'AI & Machine Learning',
          description: 'Advanced AI-powered features for content creation and optimization',
          icon: '🤖',
          enabled: true,
          features: [
            {
              id: 'ai-content-generation',
              name: 'AI Content Generation',
              description: 'Generate high-quality content using advanced AI models',
              category: 'ai',
              status: userPlan === 'free' ? 'premium' : 'available',
              requirements: {
                plan: 'pro',
                permissions: ['content:create'],
                dependencies: []
              },
              usage: { used: 15, limit: 100, period: 'monthly' },
              metrics: { popularity: 95, userRating: 4.8 }
            },
            {
              id: 'ai-optimization',
              name: 'AI Content Optimization',
              description: 'Optimize your content for better engagement and SEO',
              category: 'ai',
              status: 'available',
              requirements: {
                plan: 'free',
                permissions: ['content:edit'],
                dependencies: []
              },
              usage: { used: 45, limit: 50, period: 'monthly' },
              metrics: { popularity: 88, userRating: 4.6 }
            }
          ]
        },
        {
          id: 'content',
          name: 'Content Management',
          description: 'Powerful tools for managing and organizing your content',
          icon: '📝',
          enabled: true,
          features: [
            {
              id: 'multi-format-upload',
              name: 'Multi-Format Upload',
              description: 'Upload and process multiple content formats',
              category: 'content',
              status: 'available',
              requirements: {
                plan: 'free',
                permissions: ['content:upload'],
                dependencies: []
              },
              usage: { used: 89, limit: 500, period: 'monthly' },
              metrics: { popularity: 92, userRating: 4.7 }
            },
            {
              id: 'version-control',
              name: 'Content Version Control',
              description: 'Track and manage different versions of your content',
              category: 'content',
              status: userPlan === 'enterprise' ? 'available' : 'enterprise',
              requirements: {
                plan: 'enterprise',
                permissions: ['content:version'],
                dependencies: []
              },
              usage: { used: 12, limit: 1000, period: 'monthly' },
              metrics: { popularity: 78, userRating: 4.5 }
            }
          ]
        },
        {
          id: 'analytics',
          name: 'Analytics & Insights',
          description: 'Deep analytics and insights for your content performance',
          icon: '📊',
          enabled: true,
          features: [
            {
              id: 'real-time-analytics',
              name: 'Real-time Analytics',
              description: 'Monitor your content performance in real-time',
              category: 'analytics',
              status: 'available',
              requirements: {
                plan: 'free',
                permissions: ['analytics:view'],
                dependencies: []
              },
              usage: { used: 0, limit: -1, period: 'unlimited' },
              metrics: { popularity: 85, userRating: 4.4 }
            },
            {
              id: 'predictive-insights',
              name: 'Predictive Insights',
              description: 'AI-powered predictions for content performance',
              category: 'analytics',
              status: userPlan === 'free' ? 'premium' : 'available',
              requirements: {
                plan: 'pro',
                permissions: ['analytics:advanced'],
                dependencies: ['ai-content-generation']
              },
              usage: { used: 23, limit: 100, period: 'monthly' },
              metrics: { popularity: 91, userRating: 4.9 }
            }
          ]
        }
      ];

      setCategories(mockCategories);
    } catch (error) {
      console.error('Failed to load features:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredFeatures = categories
    .find(cat => cat.id === selectedCategory)?.features
    .filter(feature => 
      feature.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      feature.description.toLowerCase().includes(searchQuery.toLowerCase())
    ) || [];

  const handleFeatureClick = (feature: Feature) => {
    if (feature.status === 'available') {
      onFeatureSelect?.(feature);
    }
  };

  const getStatusColor = (status: Feature['status']) => {
    switch (status) {
      case 'available': return 'text-green-600 bg-green-100';
      case 'beta': return 'text-blue-600 bg-blue-100';
      case 'coming_soon': return 'text-gray-600 bg-gray-100';
      case 'premium': return 'text-purple-600 bg-purple-100';
      case 'enterprise': return 'text-orange-600 bg-orange-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status: Feature['status']) => {
    switch (status) {
      case 'available': return 'Available';
      case 'beta': return 'Beta';
      case 'coming_soon': return 'Coming Soon';
      case 'premium': return 'Premium';
      case 'enterprise': return 'Enterprise';
      default: return 'Unknown';
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Platform Features</h2>
        <p className="text-gray-600">Discover and manage platform features available to your account</p>
      </div>

      {/* Search */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="Search features..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div className="flex gap-6">
        {/* Categories Sidebar */}
        <div className="w-64 bg-gray-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-4">Categories</h3>
          {categories.map(category => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`w-full text-left p-3 rounded-lg mb-2 transition-colors ${
                selectedCategory === category.id
                  ? 'bg-blue-600 text-white'
                  : 'hover:bg-gray-200 text-gray-700'
              }`}
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">{category.icon}</span>
                <div>
                  <div className="font-medium">{category.name}</div>
                  <div className="text-sm opacity-75">{category.features.length} features</div>
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* Features Grid */}
        <div className="flex-1">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredFeatures.map(feature => (
              <div
                key={feature.id}
                onClick={() => handleFeatureClick(feature)}
                className={`border rounded-lg p-4 transition-all duration-200 ${
                  feature.status === 'available'
                    ? 'cursor-pointer hover:shadow-md border-gray-200 hover:border-blue-300'
                    : 'cursor-not-allowed opacity-60 border-gray-200'
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <h4 className="font-semibold text-gray-900">{feature.name}</h4>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(feature.status)}`}>
                    {getStatusText(feature.status)}
                  </span>
                </div>
                
                <p className="text-gray-600 text-sm mb-4">{feature.description}</p>
                
                {/* Usage Metrics */}
                {feature.usage.limit > 0 && (
                  <div className="mb-3">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span>Usage</span>
                      <span>{feature.usage.used}/{feature.usage.limit}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${Math.min((feature.usage.used / feature.usage.limit) * 100, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                {/* Rating */}
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <span>⭐ {feature.metrics.userRating}</span>
                  <span>•</span>
                  <span>{feature.metrics.popularity}% popularity</span>
                </div>
              </div>
            ))}
          </div>

          {filteredFeatures.length === 0 && (
            <div className="text-center py-12">
              <div className="text-gray-400 text-lg mb-2">No features found</div>
              <p className="text-gray-600">Try adjusting your search query or select a different category</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FeaturesInterface;