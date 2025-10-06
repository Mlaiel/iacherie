/**
 * STUDIOS DASHBOARD
 * Central hub for all 7 studio types with real-time collaboration
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import { useStudiosStore } from '@/lib/store/generated';
import { useWebSocketStatus } from '@/lib/websocket';
import Link from 'next/link';
import { Music, Film, Image, FileText, Mic, Sparkles, Radio, Zap } from 'lucide-react';

const STUDIOS = [
  {
    id: 'audio',
    name: 'Audio Studio',
    description: 'Professional audio editing and production',
    icon: Music,
    path: '/audio-studio',
    color: 'from-green-500 to-emerald-500',
    count: 626,
  },
  {
    id: 'video',
    name: 'Video Studio',
    description: 'Advanced video editing and effects',
    icon: Film,
    path: '/video-studio',
    color: 'from-blue-500 to-cyan-500',
    count: 433,
  },
  {
    id: 'image',
    name: 'Image Studio',
    description: 'Image editing and AI enhancement',
    icon: Image,
    path: '/image-studio',
    color: 'from-orange-500 to-red-500',
    count: 408,
  },
  {
    id: 'text',
    name: 'Text Studio',
    description: 'Advanced text and content creation',
    icon: FileText,
    path: '/text-studio',
    color: 'from-purple-500 to-pink-500',
    count: 467,
  },
  {
    id: 'remix',
    name: 'Remix Studio',
    description: 'Multi-track audio/video remixing',
    icon: Sparkles,
    path: '/remix-studio',
    color: 'from-pink-500 to-rose-500',
    count: 358,
  },
  {
    id: 'podcast',
    name: 'Podcast Studio',
    description: 'Podcast recording and production',
    icon: Radio,
    path: '/podcast-studio',
    color: 'from-yellow-500 to-orange-500',
    count: 0, // À créer
  },
  {
    id: 'ai',
    name: 'AI Studio',
    description: 'AI-powered content generation',
    icon: Zap,
    path: '/ai-studio',
    color: 'from-indigo-500 to-purple-500',
    count: 9,
  },
];

export default function StudioPage() {
  const { items, loading } = useStudiosStore();
  const { connected } = useWebSocketStatus();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Studios</h1>
          <p className="text-gray-600">
            Professional creative tools powered by AI
          </p>
          
          {/* Status Bar */}
          <div className="mt-4 flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm">
              <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
              <span className="text-gray-600">
                {connected ? 'Real-time collaboration active' : 'Reconnecting...'}
              </span>
            </div>
            <div className="text-sm text-gray-500">
              {items.length} active projects
            </div>
          </div>
        </div>

        {/* Studios Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {STUDIOS.map((studio) => (
            <Link
              key={studio.id}
              href={studio.path}
              className="group relative bg-white rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden"
            >
              {/* Gradient Background */}
              <div className={`absolute inset-0 bg-gradient-to-br ${studio.color} opacity-0 group-hover:opacity-10 transition-opacity`}></div>
              
              <div className="relative p-6">
                {/* Icon */}
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${studio.color} flex items-center justify-center mb-4`}>
                  <studio.icon className="w-7 h-7 text-white" />
                </div>

                {/* Content */}
                <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition">
                  {studio.name}
                </h3>
                <p className="text-gray-600 text-sm mb-4">
                  {studio.description}
                </p>

                {/* Stats */}
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">
                    {studio.count > 0 ? `${studio.count} lines of code` : 'Coming soon'}
                  </span>
                  <span className="text-xs font-medium text-gray-900 group-hover:translate-x-1 transition-transform">
                    Open →
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {/* Recent Projects */}
        {items.length > 0 && (
          <div className="mt-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Recent Projects</h2>
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="space-y-3">
                {items.slice(0, 5).map((item: any) => (
                  <div key={item.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
                    <div>
                      <h4 className="font-medium text-gray-900">{item.name || 'Untitled Project'}</h4>
                      <p className="text-sm text-gray-500">{item.type || 'Unknown'} Studio</p>
                    </div>
                    <Link
                      href={`/${item.type}-studio?project=${item.id}`}
                      className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Open
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
