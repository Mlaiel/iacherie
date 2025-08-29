/**
 * Predictive Insights - AI-powered analytics and predictions
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  ChartBarIcon,
  CpuChipIcon,
  ArrowTrendingUpIcon,
  LightBulbIcon,
  ClockIcon,
  CurrencyDollarIcon,
  UsersIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

interface Prediction {
  id: string;
  type: 'revenue' | 'growth' | 'engagement' | 'trend';
  title: string;
  prediction: string;
  confidence: number;
  timeframe: string;
  impact: 'high' | 'medium' | 'low';
  category: 'opportunity' | 'risk' | 'trend';
}

interface Insight {
  id: string;
  title: string;
  description: string;
  actionable: boolean;
  priority: 'high' | 'medium' | 'low';
  category: 'content' | 'timing' | 'audience' | 'monetization';
}

const PredictiveInsights: React.FC = () => {
  const [selectedTab, setSelectedTab] = React.useState<'predictions' | 'insights' | 'recommendations'>('predictions');
  
  const predictions: Prediction[] = [
    {
      id: '1',
      type: 'revenue',
      title: 'Revenue Growth Forecast',
      prediction: 'Expected 23% increase in revenue over next 3 months',
      confidence: 87,
      timeframe: '3 months',
      impact: 'high',
      category: 'opportunity'
    },
    {
      id: '2',
      type: 'engagement',
      title: 'Engagement Pattern Analysis',
      prediction: 'Video content engagement will peak on Tuesdays',
      confidence: 92,
      timeframe: 'Weekly',
      impact: 'medium',
      category: 'trend'
    },
    {
      id: '3',
      type: 'growth',
      title: 'Audience Growth Prediction',
      prediction: 'Follower growth may slow by 12% without content diversification',
      confidence: 78,
      timeframe: '2 months',
      impact: 'medium',
      category: 'risk'
    },
    {
      id: '4',
      type: 'trend',
      title: 'Content Trend Forecast',
      prediction: 'AI-related content will see 45% higher engagement',
      confidence: 85,
      timeframe: '6 months',
      impact: 'high',
      category: 'opportunity'
    }
  ];

  const insights: Insight[] = [
    {
      id: '1',
      title: 'Optimal Upload Time',
      description: 'Your audience is most active between 6-8 PM EST. Content uploaded during this window receives 34% more engagement.',
      actionable: true,
      priority: 'high',
      category: 'timing'
    },
    {
      id: '2',
      title: 'Content Length Optimization',
      description: 'Videos between 8-12 minutes show highest completion rates and revenue generation for your audience.',
      actionable: true,
      priority: 'high',
      category: 'content'
    },
    {
      id: '3',
      title: 'Audience Demographics Shift',
      description: '18-24 age group engagement increased by 28% last month, suggesting content resonates with younger audience.',
      actionable: false,
      priority: 'medium',
      category: 'audience'
    },
    {
      id: '4',
      title: 'Monetization Opportunity',
      description: 'Educational content categories show 67% higher revenue per view. Consider increasing tutorial content.',
      actionable: true,
      priority: 'high',
      category: 'monetization'
    }
  ];

  const recommendations = [
    {
      id: '1',
      title: 'Increase AI Tutorial Content',
      reason: 'AI-related content shows 45% higher engagement',
      action: 'Create 2-3 AI tutorials per week',
      expectedImpact: '+23% revenue growth',
      effort: 'Medium'
    },
    {
      id: '2',
      title: 'Optimize Upload Schedule',
      reason: 'Tuesday uploads perform 23% better',
      action: 'Schedule primary content for Tuesday 6-8 PM EST',
      expectedImpact: '+34% engagement',
      effort: 'Low'
    },
    {
      id: '3',
      title: 'Diversify Content Types',
      reason: 'Prevent audience growth slowdown',
      action: 'Add podcast and written content formats',
      expectedImpact: 'Maintain growth rate',
      effort: 'High'
    }
  ];

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 85) return 'text-green-600 bg-green-100';
    if (confidence >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'opportunity': return <ArrowTrendingUpIcon className="h-5 w-5 text-green-500" />;
      case 'risk': return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      case 'trend': return <ChartBarIcon className="h-5 w-5 text-blue-500" />;
      default: return <LightBulbIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getInsightIcon = (category: string) => {
    switch (category) {
      case 'content': return <ChartBarIcon className="h-5 w-5 text-blue-500" />;
      case 'timing': return <ClockIcon className="h-5 w-5 text-purple-500" />;
      case 'audience': return <UsersIcon className="h-5 w-5 text-green-500" />;
      case 'monetization': return <CurrencyDollarIcon className="h-5 w-5 text-yellow-500" />;
      default: return <LightBulbIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <CpuChipIcon className="h-6 w-6 mr-2" />
            Predictive Insights
          </h2>
          <p className="text-gray-600">AI-powered analytics and future predictions</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">Last updated:</span>
          <span className="text-sm font-medium text-gray-900">2 hours ago</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { key: 'predictions', label: 'Predictions', icon: ChartBarIcon },
            { key: 'insights', label: 'Insights', icon: LightBulbIcon },
            { key: 'recommendations', label: 'Recommendations', icon: CheckCircleIcon }
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setSelectedTab(tab.key as typeof selectedTab)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                selectedTab === tab.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="h-4 w-4" />
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Predictions Tab */}
      {selectedTab === 'predictions' && (
        <div className="space-y-4">
          {predictions.map(prediction => (
            <div key={prediction.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  {getCategoryIcon(prediction.category)}
                  <div>
                    <h3 className="font-semibold text-gray-900">{prediction.title}</h3>
                    <p className="text-sm text-gray-600">{prediction.timeframe}</p>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(prediction.confidence)}`}>
                    {prediction.confidence}% confidence
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(prediction.impact)}`}>
                    {prediction.impact} impact
                  </span>
                </div>
              </div>
              <p className="text-gray-700 mb-4">{prediction.prediction}</p>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${prediction.confidence}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Insights Tab */}
      {selectedTab === 'insights' && (
        <div className="space-y-4">
          {insights.map(insight => (
            <div key={insight.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  {getInsightIcon(insight.category)}
                  <div>
                    <h3 className="font-semibold text-gray-900">{insight.title}</h3>
                    <span className="text-sm text-gray-500 capitalize">{insight.category}</span>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(insight.priority)}`}>
                    {insight.priority} priority
                  </span>
                  {insight.actionable && (
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      Actionable
                    </span>
                  )}
                </div>
              </div>
              <p className="text-gray-700">{insight.description}</p>
            </div>
          ))}
        </div>
      )}

      {/* Recommendations Tab */}
      {selectedTab === 'recommendations' && (
        <div className="space-y-4">
          {recommendations.map(recommendation => (
            <div key={recommendation.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">{recommendation.title}</h3>
                  <p className="text-sm text-gray-600 mb-2">
                    <strong>Reason:</strong> {recommendation.reason}
                  </p>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  recommendation.effort === 'Low' ? 'bg-green-100 text-green-800' :
                  recommendation.effort === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {recommendation.effort} effort
                </span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-sm font-medium text-gray-700">Recommended Action</p>
                  <p className="text-gray-900">{recommendation.action}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700">Expected Impact</p>
                  <p className="text-green-600 font-medium">{recommendation.expectedImpact}</p>
                </div>
              </div>
              
              <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors">
                Implement Recommendation
              </button>
            </div>
          ))}
        </div>
      )}

      {/* AI Model Info */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h4 className="font-medium text-gray-900 mb-3 flex items-center">
          <CpuChipIcon className="h-5 w-5 mr-2" />
          AI Model Information
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
          <div>
            <h5 className="font-medium mb-1">Data Sources</h5>
            <ul className="space-y-1">
              <li>• Platform analytics</li>
              <li>• Audience behavior patterns</li>
              <li>• Industry trends</li>
              <li>• Content performance history</li>
            </ul>
          </div>
          <div>
            <h5 className="font-medium mb-1">Model Accuracy</h5>
            <ul className="space-y-1">
              <li>• Revenue predictions: 87%</li>
              <li>• Engagement forecasts: 92%</li>
              <li>• Growth predictions: 78%</li>
              <li>• Trend analysis: 85%</li>
            </ul>
          </div>
          <div>
            <h5 className="font-medium mb-1">Update Frequency</h5>
            <ul className="space-y-1">
              <li>• Real-time data ingestion</li>
              <li>• Model updates: Weekly</li>
              <li>• Predictions: Every 2 hours</li>
              <li>• Insights: Daily</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PredictiveInsights;