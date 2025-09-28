'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { ArrowLeft, Play, Pause, Upload, Download, AudioWaveform, Settings, Layers, Volume2, Save, Share2, Sparkles } from 'lucide-react';

interface RemixProject {
  id: string;
  name: string;
  originalTrack: string;
  status: 'processing' | 'completed' | 'draft';
  progress: number;
  duration: number;
  bpm: number;
  key: string;
  genre: string;
  effects: string[];
  waveformData: number[];
  audioUrl?: string;
  createdAt: string;
}

interface AISuggestion {
  id: string;
  type: 'tempo' | 'key' | 'effects' | 'structure';
  suggestion: string;
  confidence: number;
}

export default function RemixStudioPage() {
  const [projects, setProjects] = useState<RemixProject[]>([]);
  const [currentProject, setCurrentProject] = useState<RemixProject | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState<AISuggestion[]>([]);
  const [remixParams, setRemixParams] = useState({
    tempo: 128,
    key: 'C',
    effects: [] as string[],
    volume: 75,
    reverb: 20,
    compression: 40
  });

  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Projets simulés
  const mockProjects: RemixProject[] = [
    {
      id: '1',
      name: 'Summer Vibes Remix',
      originalTrack: 'Original Track - Artist Name',
      status: 'completed',
      progress: 100,
      duration: 185,
      bpm: 128,
      key: 'Am',
      genre: 'Deep House',
      effects: ['Reverb', 'Delay', 'Chorus'],
      waveformData: [45, 78, 23, 89, 34, 67, 91, 12, 56, 83, 29, 74, 38, 95, 47],
      audioUrl: '/audio/summer-vibes-remix.mp3',
      createdAt: '2025-09-25T10:30:00Z'
    },
    {
      id: '2', 
      name: 'Electronic Fusion V2',
      originalTrack: 'Base Track - Producer X',
      status: 'processing',
      progress: 67,
      duration: 210,
      bpm: 140,
      key: 'Gm',
      genre: 'Techno',
      effects: ['Distortion', 'Filter', 'Phaser'],
      waveformData: [67, 34, 89, 12, 78, 45, 23, 91, 56, 38, 74, 29, 95, 47, 83],
      createdAt: '2025-09-25T14:15:00Z'
    }
  ];

  // Suggestions IA simulées
  const mockAISuggestions: AISuggestion[] = [
    {
      id: '1',
      type: 'tempo',
      suggestion: 'Augmenter le tempo à 132 BPM pour plus d\'énergie',
      confidence: 87
    },
    {
      id: '2',
      type: 'effects',
      suggestion: 'Ajouter un filtre passe-bas sur le drop',
      confidence: 93
    },
    {
      id: '3',
      type: 'key',
      suggestion: 'Transposer en Dm pour une ambiance plus sombre',
      confidence: 76
    }
  ];

  useEffect(() => {
    // Charger les projets
    setTimeout(() => {
      setProjects(mockProjects);
      if (mockProjects.length > 0) {
        setCurrentProject(mockProjects[0]);
      }
    }, 1000);

    // Charger suggestions IA
    setTimeout(() => {
      setAiSuggestions(mockAISuggestions);
    }, 1500);
  }, []);

  const togglePlayback = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const processRemixWithAI = async () => {
    if (!currentProject) return;

    setIsProcessing(true);
    
    for (let i = 0; i <= 100; i += 20) {
      await new Promise(resolve => setTimeout(resolve, 800));
      
      const updatedProject = {
        ...currentProject,
        progress: i,
        status: i === 100 ? 'completed' as const : 'processing' as const
      };
      
      setCurrentProject(updatedProject);
      setProjects(projects.map(p => p.id === currentProject.id ? updatedProject : p));
    }

    setIsProcessing(false);
  };

  const applyAISuggestion = (suggestion: AISuggestion) => {
    switch (suggestion.type) {
      case 'tempo':
        setRemixParams(prev => ({ ...prev, tempo: 132 }));
        break;
      case 'effects':
        setRemixParams(prev => ({ ...prev, effects: [...prev.effects, 'Low Pass Filter'] }));
        break;
      case 'key':
        if (currentProject) {
          setCurrentProject({ ...currentProject, key: 'Dm' });
        }
        break;
    }
    
    setAiSuggestions(aiSuggestions.filter(s => s.id !== suggestion.id));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 to-purple-100">
      {/* Header */}
      <div className="bg-white shadow-lg border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="flex items-center text-gray-600 hover:text-pink-600">
                <ArrowLeft className="h-5 w-5 mr-2" />
                Retour
              </Link>
              <div className="h-6 w-px bg-gray-300"></div>
              <div className="flex items-center space-x-3">
                <AudioWaveform className="h-8 w-8 text-pink-600" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Remix Studio Pro</h1>
                  <p className="text-sm text-gray-600">Studio de remix collaboratif avec IA créative</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Panneau Principal */}
          <div className="lg:col-span-2 space-y-6">
            {/* Projet Actuel */}
            {currentProject && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{currentProject.name}</h2>
                    <p className="text-gray-600">Basé sur: {currentProject.originalTrack}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      currentProject.status === 'completed' ? 'bg-green-100 text-green-800' :
                      currentProject.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {currentProject.status === 'completed' ? '✅ Terminé' :
                       currentProject.status === 'processing' ? '⚡ En cours' : '📝 Brouillon'}
                    </span>
                  </div>
                </div>

                {/* Contrôles Audio */}
                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-4">
                      <button
                        onClick={togglePlayback}
                        className="bg-pink-600 text-white p-3 rounded-full hover:bg-pink-700 transition-colors"
                      >
                        {isPlaying ? <Pause className="h-6 w-6" /> : <Play className="h-6 w-6" />}
                      </button>
                      <div className="text-sm text-gray-600">
                        <div className="font-medium">{Math.floor(currentProject.duration / 60)}:{(currentProject.duration % 60).toString().padStart(2, '0')}</div>
                        <div>{currentProject.bpm} BPM • {currentProject.key}</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button className="p-2 text-gray-600 hover:text-pink-600">
                        <Volume2 className="h-5 w-5" />
                      </button>
                      <button className="p-2 text-gray-600 hover:text-pink-600">
                        <Settings className="h-5 w-5" />
                      </button>
                    </div>
                  </div>

                  {/* Forme d'onde */}
                  <div className="h-20 bg-white rounded-lg p-3 mb-4">
                    <div className="flex items-end justify-center space-x-1 h-full">
                      {currentProject.waveformData.map((value, index) => (
                        <div
                          key={index}
                          className="bg-gradient-to-t from-pink-500 to-purple-500 rounded-sm flex-1"
                          style={{ height: `${(value / 100) * 100}%`, minHeight: '2px' }}
                        ></div>
                      ))}
                    </div>
                  </div>

                  {/* Barre de progression */}
                  {currentProject.status === 'processing' && (
                    <div className="mb-4">
                      <div className="flex justify-between text-sm text-gray-600 mb-1">
                        <span>Traitement IA en cours...</span>
                        <span>{currentProject.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-pink-500 to-purple-500 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${currentProject.progress}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={processRemixWithAI}
                    disabled={isProcessing || currentProject.status === 'processing'}
                    className="bg-gradient-to-r from-pink-600 to-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:from-pink-700 hover:to-purple-700 transition-all disabled:opacity-50 flex items-center space-x-2"
                  >
                    <Sparkles className="h-5 w-5" />
                    <span>{isProcessing ? 'Traitement IA...' : '🤖 Traiter avec IA'}</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Panneau Latéral */}
          <div className="space-y-6">
            {/* Suggestions IA */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Sparkles className="h-5 w-5 text-purple-600 mr-2" />
                Suggestions IA
              </h3>
              
              {aiSuggestions.length > 0 ? (
                <div className="space-y-3">
                  {aiSuggestions.map((suggestion) => (
                    <div key={suggestion.id} className="border border-purple-200 rounded-lg p-4 bg-purple-50">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-purple-600 uppercase">
                          {suggestion.type}
                        </span>
                        <span className="text-xs text-gray-600">
                          {suggestion.confidence}% confiance
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 mb-3">{suggestion.suggestion}</p>
                      <button
                        onClick={() => applyAISuggestion(suggestion)}
                        className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg text-sm hover:bg-purple-700 transition-colors"
                      >
                        ✨ Appliquer
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">Aucune suggestion pour le moment. Commencez un remix pour obtenir des recommandations IA!</p>
              )}
            </div>

            {/* Projets */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-4">🎵 Mes Projets ({projects.length})</h3>
              
              <div className="space-y-3">
                {projects.map((project) => (
                  <div
                    key={project.id}
                    onClick={() => setCurrentProject(project)}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      currentProject?.id === project.id 
                        ? 'bg-pink-100 border-2 border-pink-300' 
                        : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-sm">{project.name}</h4>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        project.status === 'completed' ? 'bg-green-100 text-green-800' :
                        project.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {project.status}
                      </span>
                    </div>
                    <p className="text-xs text-gray-600">{project.originalTrack}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Audio Element */}
      <audio ref={audioRef} />
    </div>
  );
}