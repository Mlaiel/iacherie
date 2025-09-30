/**
 * ✨ Features Page - Platform Capabilities & AI-Powered Tools
 * 
 * @fileoverview Comprehensive showcase of platform features and capabilities
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

'use client';

import React, { useState } from 'react';
import {
  SparklesIcon,
  ShieldCheckIcon,
  CurrencyDollarIcon,
  UsersIcon,
  ChartBarIcon,
  GlobeAltIcon,
  MusicalNoteIcon,
  PhotoIcon,
  VideoCameraIcon,
  DocumentTextIcon,
  LightBulbIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

interface Feature {
  id: string;
  category: 'ai' | 'protection' | 'monetization' | 'collaboration' | 'analytics' | 'distribution';
  title: string;
  description: string;
  icon: React.ReactNode;
  highlights: string[];
  status: 'available' | 'beta' | 'coming_soon';
}

export default function FeaturesPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const features: Feature[] = [
    {
      id: 'ai-content-analysis',
      category: 'ai',
      title: 'AI Content Analysis',
      description: 'Advanced artificial intelligence analyzes your content for quality, engagement potential, and optimization opportunities.',
      icon: <SparklesIcon className="h-6 w-6" />,
      highlights: [
        'Automated quality scoring',
        'Content optimization suggestions',
        'Trend analysis and predictions',
        'Multi-format support (audio, video, image, text)'
      ],
      status: 'available'
    },
    {
      id: 'content-protection',
      category: 'protection',
      title: 'Digital Content Protection',
      description: 'Enterprise-grade protection using digital fingerprinting, watermarking, and real-time monitoring.',
      icon: <ShieldCheckIcon className="h-6 w-6" />,
      highlights: [
        'Digital fingerprinting technology',
        'Invisible watermarking',
        'Real-time piracy detection',
        'Automated DMCA takedown'
      ],
      status: 'available'
    },
    {
      id: 'smart-monetization',
      category: 'monetization',
      title: 'Smart Monetization Engine',
      description: 'AI-powered monetization strategies that adapt to market conditions and audience behavior.',
      icon: <CurrencyDollarIcon className="h-6 w-6" />,
      highlights: [
        'Dynamic pricing optimization',
        'Revenue stream diversification',
        'Audience monetization insights',
        'Platform-specific strategies'
      ],
      status: 'available'
    },
    {
      id: 'creator-collaboration',
      category: 'collaboration',
      title: 'Creator Collaboration Hub',
      description: 'Connect with other creators, manage joint projects, and share revenue fairly.',
      icon: <UsersIcon className="h-6 w-6" />,
      highlights: [
        'Intelligent creator matching',
        'Collaborative project management',
        'Fair revenue distribution',
        'Skill-based recommendations'
      ],
      status: 'beta'
    },
    {
      id: 'advanced-analytics',
      category: 'analytics',
      title: 'Advanced Analytics Suite',
      description: 'Comprehensive analytics with predictive insights and actionable recommendations.',
      icon: <ChartBarIcon className="h-6 w-6" />,
      highlights: [
        'Real-time performance tracking',
        'Predictive audience analytics',
        'ROI optimization insights',
        'Cross-platform metrics'
      ],
      status: 'available'
    },
    {
      id: 'global-distribution',
      category: 'distribution',
      title: 'Global Distribution Network',
      description: 'Distribute your content across 200+ platforms with optimized formatting and scheduling.',
      icon: <GlobeAltIcon className="h-6 w-6" />,
      highlights: [
        '200+ platform integrations',
        'Automated format optimization',
        'Smart scheduling algorithms',
        'Geo-targeted distribution'
      ],
      status: 'available'
    },
    {
      id: 'ai-music-creation',
      category: 'ai',
      title: 'AI Music Creation Studio',
      description: 'Create professional music tracks using advanced AI with full copyright ownership.',
      icon: <MusicalNoteIcon className="h-6 w-6" />,
      highlights: [
        'AI-powered composition',
        'Professional mixing & mastering',
        'Copyright-free generation',
        'Style transfer technology'
      ],
      status: 'beta'
    },
    {
      id: 'visual-content-ai',
      category: 'ai',
      title: 'Visual Content AI',
      description: 'Generate, enhance, and optimize visual content with cutting-edge AI technology.',
      icon: <PhotoIcon className="h-6 w-6" />,
      highlights: [
        'AI image generation',
        'Photo enhancement & restoration',
        'Style transfer & filters',
        'Automated alt-text generation'
      ],
      status: 'available'
    },
    {
      id: 'video-intelligence',
      category: 'ai',
      title: 'Video Intelligence Platform',
      description: 'AI-powered video editing, analysis, and optimization for maximum engagement.',
      icon: <VideoCameraIcon className="h-6 w-6" />,
      highlights: [
        'Automated video editing',
        'Scene detection & tagging',
        'Engagement optimization',
        'Multi-language subtitles'
      ],
      status: 'coming_soon'
    }
  ];

  const categories = [
    { id: 'all', name: 'All Features', icon: <LightBulbIcon className="h-5 w-5" /> },
    { id: 'ai', name: 'AI Tools', icon: <SparklesIcon className="h-5 w-5" /> },
    { id: 'protection', name: 'Protection', icon: <ShieldCheckIcon className="h-5 w-5" /> },
    { id: 'monetization', name: 'Monetization', icon: <CurrencyDollarIcon className="h-5 w-5" /> },
    { id: 'collaboration', name: 'Collaboration', icon: <UsersIcon className="h-5 w-5" /> },
    { id: 'analytics', name: 'Analytics', icon: <ChartBarIcon className="h-5 w-5" /> },
    { id: 'distribution', name: 'Distribution', icon: <GlobeAltIcon className="h-5 w-5" /> }
  ];

  const filteredFeatures = selectedCategory === 'all' 
    ? features 
    : features.filter(feature => feature.category === selectedCategory);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'available':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Available</span>;
      case 'beta':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">Beta</span>;
      case 'coming_soon':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">Coming Soon</span>;
      default:
        return null;
    }
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      ai: 'text-purple-600 bg-purple-100',
      protection: 'text-blue-600 bg-blue-100',
      monetization: 'text-green-600 bg-green-100',
      collaboration: 'text-orange-600 bg-orange-100',
      analytics: 'text-cyan-600 bg-cyan-100',
      distribution: 'text-indigo-600 bg-indigo-100'
    };
    return colors[category as keyof typeof colors] || 'text-gray-600 bg-gray-100';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Platform Features</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Discover the comprehensive suite of AI-powered tools and features designed to transform your content creation journey.
          </p>
        </div>

        {/* Category Filter */}
        <div className="flex flex-wrap justify-center gap-3 mb-8">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedCategory === category.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              {category.icon}
              <span>{category.name}</span>
            </button>
          ))}
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredFeatures.map((feature) => (
            <div key={feature.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
              <div className="p-6">
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 rounded-full ${getCategoryColor(feature.category)}`}>
                    {feature.icon}
                  </div>
                  {getStatusBadge(feature.status)}
                </div>

                {/* Content */}
                <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600 mb-4">{feature.description}</p>

                {/* Highlights */}
                <div className="space-y-2 mb-6">
                  {feature.highlights.map((highlight, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <ArrowRightIcon className="h-4 w-4 text-green-500 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{highlight}</span>
                    </div>
                  ))}
                </div>

                {/* Action Button */}
                <button 
                  className={`w-full py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
                    feature.status === 'available'
                      ? 'bg-blue-600 hover:bg-blue-700 text-white'
                      : feature.status === 'beta'
                      ? 'bg-yellow-600 hover:bg-yellow-700 text-white'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                  disabled={feature.status === 'coming_soon'}
                >
                  {feature.status === 'available' 
                    ? 'Try Now' 
                    : feature.status === 'beta' 
                    ? 'Join Beta' 
                    : 'Coming Soon'}
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* CTA Section */}
        <div className="mt-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to Transform Your Content?</h2>
          <p className="text-blue-100 text-lg mb-6 max-w-2xl mx-auto">
            Join thousands of creators who are already using our AI-powered platform to protect, monetize, and scale their content.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
              Start Free Trial
            </button>
            <button className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors">
              Schedule Demo
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}