/**
 * Professional Remix Studio Component
 * 
 * Advanced video and content remixing interface
 * Direct backend integration for remix operations
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  Video, 
  Music, 
  Image, 
  Scissors, 
  Layers, 
  Palette, 
  Wand2, 
  Download,
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Volume2,
  Settings,
  Share2,
  Save,
  Undo,
  Redo,
  ZoomIn,
  ZoomOut
} from 'lucide-react';

interface RemixProject {
  id: string;
  name: string;
  type: 'video' | 'audio' | 'image' | 'mixed';
  duration: number;
  layers: number;
  status: 'draft' | 'processing' | 'completed' | 'error';
  thumbnail: string;
  createdAt: string;
  lastModified: string;
}

interface RemixStudioData {
  projects: RemixProject[];
  activeProject: RemixProject | null;
  templates: any[];
  recentProjects: RemixProject[];
}

export default function RemixStudio() {
  const [studioData, setStudioData] = useState<RemixStudioData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('projects');
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(100);

  useEffect(() => {
    const fetchStudioData = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/remix-studio`);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        setStudioData(data);
      } catch (error) {
        console.error('Remix studio data fetch error:', error);
        // Fallback data
        setStudioData({
          projects: [
            {
              id: 'project-1',
              name: 'Product Launch Video',
              type: 'video',
              duration: 120,
              layers: 8,
              status: 'completed',
              thumbnail: '/api/placeholder/300/200',
              createdAt: new Date().toISOString(),
              lastModified: new Date().toISOString()
            },
            {
              id: 'project-2',
              name: 'Social Media Remix',
              type: 'mixed',
              duration: 30,
              layers: 5,
              status: 'processing',
              thumbnail: '/api/placeholder/300/200',
              createdAt: new Date().toISOString(),
              lastModified: new Date().toISOString()
            },
            {
              id: 'project-3',
              name: 'Podcast Intro',
              type: 'audio',
              duration: 15,
              layers: 3,
              status: 'draft',
              thumbnail: '/api/placeholder/300/200',
              createdAt: new Date().toISOString(),
              lastModified: new Date().toISOString()
            }
          ],
          activeProject: null,
          templates: [],
          recentProjects: []
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStudioData();
    const interval = setInterval(fetchStudioData, 15000);
    return () => clearInterval(interval);
  }, []);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleProjectOpen = (project: RemixProject) => {
    setStudioData(prev => prev ? { ...prev, activeProject: project } : null);
  };

  const handleNewProject = () => {
    console.log('Creating new project');
    // Implementation for new project creation
  };

  const handleSave = () => {
    console.log('Saving project');
    // Implementation for saving project
  };

  const handleExport = () => {
    console.log('Exporting project');
    // Implementation for exporting project
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'processing': return 'text-blue-600 bg-blue-100';
      case 'draft': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'video': return <Video className="h-5 w-5" />;
      case 'audio': return <Music className="h-5 w-5" />;
      case 'image': return <Image className="h-5 w-5" />;
      case 'mixed': return <Layers className="h-5 w-5" />;
      default: return <Video className="h-5 w-5" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900">Loading Remix Studio</h2>
          <p className="text-gray-600 mt-2">Initializing creative workspace...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Wand2 className="h-8 w-8 text-purple-400" />
              <div>
                <h1 className="text-2xl font-bold text-white">Remix Studio</h1>
                <p className="text-sm text-gray-400">
                  Professional content remixing and editing
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={handleNewProject}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
              >
                New Project
              </button>
              {studioData?.activeProject && (
                <>
                  <button
                    onClick={handleSave}
                    className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    Save
                  </button>
                  <button
                    onClick={handleExport}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="flex h-screen">
        {/* Sidebar */}
        <div className="w-80 bg-gray-800 border-r border-gray-700 overflow-y-auto">
          <div className="p-6">
            <div className="flex space-x-1 mb-6">
              {[
                { id: 'projects', name: 'Projects' },
                { id: 'templates', name: 'Templates' },
                { id: 'assets', name: 'Assets' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-purple-600 text-white'
                      : 'text-gray-400 hover:text-white hover:bg-gray-700'
                  }`}
                >
                  {tab.name}
                </button>
              ))}
            </div>

            {activeTab === 'projects' && (
              <div className="space-y-4">
                <h3 className="font-semibold text-white mb-4">Recent Projects</h3>
                {studioData?.projects.map((project) => (
                  <div
                    key={project.id}
                    onClick={() => handleProjectOpen(project)}
                    className="bg-gray-700 p-4 rounded-lg cursor-pointer hover:bg-gray-600 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        {getTypeIcon(project.type)}
                        <h4 className="font-medium text-white">{project.name}</h4>
                      </div>
                      <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                        {project.status}
                      </div>
                    </div>
                    <div className="text-sm text-gray-400 space-y-1">
                      <div>Duration: {project.duration}s</div>
                      <div>Layers: {project.layers}</div>
                      <div>Modified: {new Date(project.lastModified).toLocaleDateString()}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'templates' && (
              <div className="space-y-4">
                <h3 className="font-semibold text-white mb-4">Templates</h3>
                <div className="text-gray-400 text-center py-8">
                  Templates coming soon
                </div>
              </div>
            )}

            {activeTab === 'assets' && (
              <div className="space-y-4">
                <h3 className="font-semibold text-white mb-4">Media Assets</h3>
                <div className="text-gray-400 text-center py-8">
                  Asset library coming soon
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Main Editor */}
        <div className="flex-1 flex flex-col">
          {studioData?.activeProject ? (
            <>
              {/* Toolbar */}
              <div className="bg-gray-800 border-b border-gray-700 p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <h2 className="text-lg font-semibold text-white">
                      {studioData.activeProject.name}
                    </h2>
                    <div className="flex items-center space-x-2">
                      <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                        <Undo className="h-4 w-4" />
                      </button>
                      <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                        <Redo className="h-4 w-4" />
                      </button>
                      <div className="w-px h-6 bg-gray-600 mx-2" />
                      <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                        <ZoomOut className="h-4 w-4" />
                      </button>
                      <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                        <ZoomIn className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                      <Settings className="h-4 w-4" />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                      <Share2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Preview Area */}
              <div className="flex-1 bg-black flex items-center justify-center p-8">
                <div className="bg-gray-800 rounded-lg p-8 text-center">
                  <div className="w-96 h-64 bg-gray-700 rounded-lg mb-6 flex items-center justify-center">
                    {getTypeIcon(studioData.activeProject.type)}
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-2">
                    {studioData.activeProject.name}
                  </h3>
                  <p className="text-gray-400 mb-6">
                    {studioData.activeProject.type.charAt(0).toUpperCase() + studioData.activeProject.type.slice(1)} Project
                  </p>
                  <div className="text-sm text-gray-500">
                    Preview functionality coming soon
                  </div>
                </div>
              </div>

              {/* Timeline and Controls */}
              <div className="bg-gray-800 border-t border-gray-700 p-4">
                {/* Playback Controls */}
                <div className="flex items-center justify-center space-x-4 mb-4">
                  <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                    <SkipBack className="h-5 w-5" />
                  </button>
                  <button
                    onClick={handlePlayPause}
                    className="p-3 bg-purple-600 text-white rounded-full hover:bg-purple-700"
                  >
                    {isPlaying ? <Pause className="h-6 w-6" /> : <Play className="h-6 w-6" />}
                  </button>
                  <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                    <SkipForward className="h-5 w-5" />
                  </button>
                  <div className="flex items-center space-x-2 ml-8">
                    <Volume2 className="h-4 w-4 text-gray-400" />
                    <div className="w-20 h-1 bg-gray-600 rounded-full">
                      <div className="w-1/2 h-full bg-purple-500 rounded-full"></div>
                    </div>
                  </div>
                </div>

                {/* Timeline */}
                <div className="bg-gray-700 rounded-lg p-4">
                  <div className="flex items-center justify-between text-sm text-gray-400 mb-2">
                    <span>{Math.floor(currentTime / 60)}:{(currentTime % 60).toString().padStart(2, '0')}</span>
                    <span>{Math.floor(duration / 60)}:{(duration % 60).toString().padStart(2, '0')}</span>
                  </div>
                  <div className="relative h-2 bg-gray-600 rounded-full">
                    <div 
                      className="absolute h-full bg-purple-500 rounded-full transition-all duration-300"
                      style={{ width: `${(currentTime / duration) * 100}%` }}
                    />
                  </div>
                  <div className="mt-4 text-center text-gray-400 text-sm">
                    Timeline editing interface coming soon
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <Wand2 className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">Welcome to Remix Studio</h3>
                <p className="text-gray-400 mb-6">Select a project or create a new one to get started</p>
                <button
                  onClick={handleNewProject}
                  className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700"
                >
                  Create New Project
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}