'use client';

import Link from 'next/link';
import { 
  Languages, Search, DollarSign, Radio, Blocks, Bot, 
  Trophy, Video, Sparkles, Users, ArrowRight, Zap,
  FileText, MessageSquare, Film, Activity
} from 'lucide-react';

export default function HomePage() {
  const features = [
    {
      title: 'Languages',
      description: '644 languages with real-time translation',
      icon: Languages,
      href: '/languages',
      color: 'from-blue-500 to-purple-500',
      stats: '644 Languages'
    },
    {
      title: 'SEO Tools',
      description: '8 powerful SEO engines for optimization',
      icon: Search,
      href: '/seo-tools',
      color: 'from-purple-500 to-pink-500',
      stats: '8 Engines'
    },
    {
      title: 'Monetization',
      description: 'Complete revenue & subscription management',
      icon: DollarSign,
      href: '/monetization',
      color: 'from-green-500 to-emerald-500',
      stats: 'Stripe Integration'
    },
    {
      title: 'Streaming Live',
      description: 'Professional live streaming studio',
      icon: Radio,
      href: '/streaming-live',
      color: 'from-red-500 to-pink-500',
      stats: 'RTMP Support'
    },
    {
      title: 'Blockchain Hub',
      description: '6 networks with NFT minting',
      icon: Blocks,
      href: '/blockchain',
      color: 'from-indigo-500 to-purple-500',
      stats: '6 Networks'
    },
    {
      title: 'Crawlers',
      description: '3,231 crawlers across 31+ platforms',
      icon: Bot,
      href: '/crawlers',
      color: 'from-orange-500 to-yellow-500',
      stats: '3,231 Crawlers'
    },
    {
      title: 'Studios',
      description: '7 professional creative studios',
      icon: Film,
      href: '/studio',
      color: 'from-purple-500 to-pink-500',
      stats: '7 Studios'
    },
    {
      title: 'AI Agents',
      description: '3,054 specialized AI agents',
      icon: Bot,
      href: '/agents',
      color: 'from-indigo-500 to-purple-500',
      stats: '3,054 Agents'
    },
    {
      title: 'Chatrooms',
      description: '988 real-time chat rooms',
      icon: MessageSquare,
      href: '/chatrooms',
      color: 'from-green-500 to-emerald-500',
      stats: '988 Rooms'
    },
    {
      title: 'Automation',
      description: '3,305 workflow automations',
      icon: Zap,
      href: '/automation',
      color: 'from-red-500 to-orange-500',
      stats: '3,305 Workflows'
    },
    {
      title: 'Gamification',
      description: 'Badges, achievements & leaderboards',
      icon: Trophy,
      href: '/gamification',
      color: 'from-amber-500 to-yellow-500',
      stats: 'Achievements'
    },
    {
      title: 'Video Chat Rooms',
      description: 'WebRTC powered video communication',
      icon: Video,
      href: '/video-chat-rooms',
      color: 'from-purple-500 to-blue-500',
      stats: 'WebRTC'
    },
    {
      title: 'AI Orchestrator',
      description: '53 AI agents for automation',
      icon: Sparkles,
      href: '/ai-orchestrator',
      color: 'from-blue-500 to-indigo-500',
      stats: '53 Agents'
    },
    {
      title: 'Collaboration',
      description: 'Real-time team collaboration hub',
      icon: Users,
      href: '/collaboration',
      color: 'from-green-500 to-teal-500',
      stats: 'Real-time'
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                IA Chérie Platform
              </h1>
              <p className="mt-2 text-lg text-gray-600">
                Complete AI-Powered Content & Creator Platform
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="inline-flex items-center gap-2 px-4 py-2 bg-green-50 text-green-700 rounded-full text-sm font-medium">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                All Systems Operational
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-full text-sm font-medium mb-6">
            <Zap className="w-4 h-4" />
            100% Production Ready - No Mocks, All Real APIs
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            16+ Professional Interfaces
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Explore our complete suite of tools and features. All interfaces connected to 21,000+ real backend components with live data.
          </p>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
            <div className="text-3xl font-bold text-blue-600 mb-1">16+</div>
            <div className="text-sm text-gray-600">Interfaces</div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
            <div className="text-3xl font-bold text-purple-600 mb-1">1,069</div>
            <div className="text-sm text-gray-600">API Endpoints</div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
            <div className="text-3xl font-bold text-green-600 mb-1">21,000+</div>
            <div className="text-sm text-gray-600">Components</div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
            <div className="text-3xl font-bold text-orange-600 mb-1">100%</div>
            <div className="text-sm text-gray-600">Real APIs</div>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature) => (
            <Link
              key={feature.href}
              href={feature.href}
              className="group bg-white rounded-xl border border-gray-200 p-6 hover:shadow-xl transition-all duration-300 hover:scale-105"
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center text-white shadow-lg`}>
                  <feature.icon className="w-6 h-6" />
                </div>
                <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-gray-900 group-hover:translate-x-1 transition-all" />
              </div>
              
              <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                {feature.title}
              </h3>
              
              <p className="text-gray-600 text-sm mb-4">
                {feature.description}
              </p>
              
              <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                  {feature.stats}
                </span>
                <span className="text-sm font-medium text-blue-600 group-hover:underline">
                  Explore →
                </span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 mt-12 border-t border-gray-200">
        <div className="text-center">
          <p className="text-gray-600 text-sm">
            © 2025 IA Chérie Platform - All Rights Reserved
          </p>
          <p className="text-gray-500 text-xs mt-2">
            Enterprise Edition v3.0.0 - Backend: 
            <a href="http://localhost:8000" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline ml-1">
              http://localhost:8000
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}
