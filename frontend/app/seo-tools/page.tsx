'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Search, TrendingUp, BarChart3, Target, Zap, Globe, Award, Loader2, ExternalLink } from 'lucide-react';

interface SEOEngine {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'idle' | 'processing';
  category: string;
  capabilities: string[];
}

interface KeywordSuggestion {
  keyword: string;
  volume: number;
  difficulty: number;
  cpc: number;
  trend: 'up' | 'down' | 'stable';
}

interface SEOAnalysis {
  score: number;
  title_score: number;
  meta_description_score: number;
  keyword_density: number;
  readability_score: number;
  suggestions: string[];
}

export default function SEOToolsPage() {
  const [engines, setEngines] = useState<SEOEngine[]>([]);
  const [selectedEngine, setSelectedEngine] = useState<string>('content');
  const [loading, setLoading] = useState(false);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  
  // SEO Analysis
  const [urlToAnalyze, setUrlToAnalyze] = useState('');
  const [analysisResult, setAnalysisResult] = useState<SEOAnalysis | null>(null);
  
  // Keyword Research
  const [keyword, setKeyword] = useState('');
  const [keywords, setKeywords] = useState<KeywordSuggestion[]>([]);
  
  // Content Optimization
  const [contentText, setContentText] = useState('');
  const [optimizedContent, setOptimizedContent] = useState('');

  useEffect(() => {
    fetchSEOEngines();
  }, []);

  const fetchSEOEngines = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/seo/engines');
      
      if (response.ok) {
        const data = await response.json();
        setEngines(data.engines || []);
      }
    } catch (error) {
      console.error('Error fetching SEO engines:', error);
    } finally {
      setLoading(false);
    }
  };

  const analyzeSEO = async () => {
    if (!urlToAnalyze.trim()) return;

    try {
      setAnalysisLoading(true);
      setAnalysisResult(null);

      const response = await fetch('http://localhost:8000/seo/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: urlToAnalyze,
          engine: selectedEngine,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setAnalysisResult(result.analysis);
      } else {
        console.error('SEO analysis failed');
      }
    } catch (error) {
      console.error('Error analyzing SEO:', error);
    } finally {
      setAnalysisLoading(false);
    }
  };

  const researchKeywords = async () => {
    if (!keyword.trim()) return;

    try {
      setLoading(true);
      setKeywords([]);

      const response = await fetch('http://localhost:8000/seo/keywords/research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          keyword: keyword,
          language: 'en',
          country: 'US',
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setKeywords(result.keywords || []);
      }
    } catch (error) {
      console.error('Error researching keywords:', error);
    } finally {
      setLoading(false);
    }
  };

  const optimizeContent = async () => {
    if (!contentText.trim()) return;

    try {
      setLoading(true);
      setOptimizedContent('');

      const response = await fetch('http://localhost:8000/seo/content/optimize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: contentText,
          target_keywords: keyword.split(',').map(k => k.trim()),
          engine: selectedEngine,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setOptimizedContent(result.optimized_content);
      }
    } catch (error) {
      console.error('Error optimizing content:', error);
    } finally {
      setLoading(false);
    }
  };

  const engineCategories = {
    content: { name: 'Content SEO', icon: '📝', color: 'blue' },
    platform: { name: 'Platform SEO', icon: '🌐', color: 'green' },
    analytics: { name: 'SEO Analytics', icon: '📊', color: 'purple' },
    business: { name: 'Business SEO', icon: '💼', color: 'orange' },
    collaboration: { name: 'Collaboration SEO', icon: '🤝', color: 'pink' },
    protection: { name: 'Protection SEO', icon: '🛡️', color: 'red' },
    performance: { name: 'Performance SEO', icon: '⚡', color: 'yellow' },
    automation: { name: 'SEO Automation', icon: '🤖', color: 'indigo' },
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-md border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-600 hover:text-purple-600 transition">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <Search className="h-8 w-8 text-purple-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">SEO Intelligence Hub</h1>
                <p className="text-sm text-gray-500">8 Engines • Real-time Analysis • AI-Powered Optimization</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-sm font-semibold text-gray-700">{engines.length} Engines</div>
                <div className="text-xs text-green-600">● All Active</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* SEO Engines Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {Object.entries(engineCategories).map(([key, cat]) => (
            <button
              key={key}
              onClick={() => setSelectedEngine(key)}
              className={`p-4 rounded-xl border-2 transition-all transform hover:scale-105 ${
                selectedEngine === key
                  ? `border-${cat.color}-500 bg-${cat.color}-50 shadow-lg`
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <div className="text-3xl mb-2">{cat.icon}</div>
              <div className="font-semibold text-sm text-gray-900">{cat.name}</div>
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Tools */}
          <div className="lg:col-span-2 space-y-6">
            {/* URL Analysis */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center space-x-3 mb-6">
                <BarChart3 className="h-6 w-6 text-purple-600" />
                <h2 className="text-xl font-bold text-gray-900">SEO Analysis</h2>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    URL to Analyze
                  </label>
                  <div className="flex space-x-2">
                    <input
                      type="url"
                      value={urlToAnalyze}
                      onChange={(e) => setUrlToAnalyze(e.target.value)}
                      placeholder="https://example.com"
                      className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                    <button
                      onClick={analyzeSEO}
                      disabled={!urlToAnalyze || analysisLoading}
                      className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition flex items-center space-x-2"
                    >
                      {analysisLoading ? (
                        <Loader2 className="h-5 w-5 animate-spin" />
                      ) : (
                        <Search className="h-5 w-5" />
                      )}
                      <span>Analyze</span>
                    </button>
                  </div>
                </div>

                {analysisResult && (
                  <div className="mt-6 space-y-4">
                    {/* SEO Score */}
                    <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold">SEO Score</h3>
                        <div className="text-4xl font-bold text-purple-600">
                          {analysisResult.score}/100
                        </div>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                          className="bg-gradient-to-r from-purple-600 to-blue-600 h-3 rounded-full transition-all"
                          style={{ width: `${analysisResult.score}%` }}
                        />
                      </div>
                    </div>

                    {/* Detailed Scores */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-white border border-gray-200 rounded-lg p-4">
                        <div className="text-sm text-gray-600">Title Score</div>
                        <div className="text-2xl font-bold text-blue-600">{analysisResult.title_score}/100</div>
                      </div>
                      <div className="bg-white border border-gray-200 rounded-lg p-4">
                        <div className="text-sm text-gray-600">Meta Description</div>
                        <div className="text-2xl font-bold text-green-600">{analysisResult.meta_description_score}/100</div>
                      </div>
                      <div className="bg-white border border-gray-200 rounded-lg p-4">
                        <div className="text-sm text-gray-600">Keyword Density</div>
                        <div className="text-2xl font-bold text-purple-600">{analysisResult.keyword_density}%</div>
                      </div>
                      <div className="bg-white border border-gray-200 rounded-lg p-4">
                        <div className="text-sm text-gray-600">Readability</div>
                        <div className="text-2xl font-bold text-orange-600">{analysisResult.readability_score}/100</div>
                      </div>
                    </div>

                    {/* Suggestions */}
                    {analysisResult.suggestions.length > 0 && (
                      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <h4 className="font-semibold text-yellow-900 mb-3">💡 Optimization Suggestions</h4>
                        <ul className="space-y-2">
                          {analysisResult.suggestions.map((suggestion, idx) => (
                            <li key={idx} className="text-sm text-yellow-800 flex items-start">
                              <span className="mr-2">•</span>
                              <span>{suggestion}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Keyword Research */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center space-x-3 mb-6">
                <Target className="h-6 w-6 text-blue-600" />
                <h2 className="text-xl font-bold text-gray-900">Keyword Research</h2>
              </div>

              <div className="space-y-4">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    placeholder="Enter seed keyword..."
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    onClick={researchKeywords}
                    disabled={!keyword || loading}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
                  >
                    {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : 'Research'}
                  </button>
                </div>

                {keywords.length > 0 && (
                  <div className="mt-4 space-y-2 max-h-96 overflow-y-auto">
                    {keywords.map((kw, idx) => (
                      <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition">
                        <div className="flex items-center justify-between mb-2">
                          <div className="font-semibold text-gray-900">{kw.keyword}</div>
                          <div className={`flex items-center space-x-1 text-sm ${
                            kw.trend === 'up' ? 'text-green-600' : kw.trend === 'down' ? 'text-red-600' : 'text-gray-600'
                          }`}>
                            <TrendingUp className="h-4 w-4" />
                            <span>{kw.trend}</span>
                          </div>
                        </div>
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <div className="text-gray-500">Volume</div>
                            <div className="font-semibold">{kw.volume.toLocaleString()}</div>
                          </div>
                          <div>
                            <div className="text-gray-500">Difficulty</div>
                            <div className={`font-semibold ${kw.difficulty > 70 ? 'text-red-600' : kw.difficulty > 40 ? 'text-yellow-600' : 'text-green-600'}`}>
                              {kw.difficulty}/100
                            </div>
                          </div>
                          <div>
                            <div className="text-gray-500">CPC</div>
                            <div className="font-semibold">${kw.cpc.toFixed(2)}</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Content Optimization */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center space-x-3 mb-6">
                <Zap className="h-6 w-6 text-orange-600" />
                <h2 className="text-xl font-bold text-gray-900">Content Optimization</h2>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Original Content
                  </label>
                  <textarea
                    value={contentText}
                    onChange={(e) => setContentText(e.target.value)}
                    placeholder="Paste your content here..."
                    className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none"
                  />
                </div>

                <button
                  onClick={optimizeContent}
                  disabled={!contentText || loading}
                  className="w-full bg-gradient-to-r from-orange-600 to-red-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-orange-700 hover:to-red-700 disabled:opacity-50 transition"
                >
                  {loading ? 'Optimizing...' : 'Optimize Content'}
                </button>

                {optimizedContent && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <h4 className="font-semibold text-green-900 mb-3">✨ Optimized Content</h4>
                    <div className="text-sm text-green-800 whitespace-pre-wrap">
                      {optimizedContent}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Engines Status */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-24">
              <h3 className="text-lg font-bold text-gray-900 mb-4">SEO Engines Status</h3>
              
              {loading && engines.length === 0 ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-purple-600" />
                </div>
              ) : (
                <div className="space-y-3 max-h-[700px] overflow-y-auto">
                  {engines.map((engine) => (
                    <div key={engine.id} className="border border-gray-200 rounded-lg p-4 hover:border-purple-300 transition">
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-semibold text-sm text-gray-900">{engine.name}</div>
                        <div className={`px-2 py-1 rounded text-xs font-medium ${
                          engine.status === 'active' ? 'bg-green-100 text-green-700' :
                          engine.status === 'processing' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {engine.status}
                        </div>
                      </div>
                      <div className="text-xs text-gray-600 mb-2">{engine.description}</div>
                      <div className="flex flex-wrap gap-1">
                        {engine.capabilities?.slice(0, 3).map((cap, idx) => (
                          <span key={idx} className="px-2 py-0.5 bg-purple-50 text-purple-700 rounded text-xs">
                            {cap}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
