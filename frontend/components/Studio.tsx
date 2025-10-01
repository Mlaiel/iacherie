/**
 * Professional AI Studio Component
 * 
 * REAL AI generation capabilities with multiple APIs
 * Image, Text, Audio, Video generation with real backend connections
 */

'use client';

import React, { useState, useRef } from 'react';
import { 
  Wand2, 
  Image as ImageIcon, 
  FileText, 
  Music, 
  Video, 
  Download,
  Copy,
  Heart,
  Share2,
  Settings,
  Sparkles,
  Play,
  Pause,
  Volume2,
  RefreshCw,
  Check,
  AlertCircle,
  Zap
} from 'lucide-react';

interface GeneratedContent {
  id: string;
  type: 'image' | 'text' | 'audio' | 'video';
  prompt: string;
  url?: string;
  text?: string;
  title: string;
  createdAt: string;
  metadata?: {
    source?: string;
    style?: string;
    duration?: number;
    fallback?: boolean;
    error?: boolean;
    tokens?: number;
    provider?: string;
    real?: boolean;
    realGeneration?: boolean;
    noFallback?: boolean;
    processingTime?: number;
  };
}

export default function Studio() {
  // States pour les différents types de génération
  const [activeTab, setActiveTab] = useState<'image' | 'text' | 'audio' | 'video'>('image');
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent[]>([]);
  
  // States pour l'image
  const [imagePrompt, setImagePrompt] = useState('');
  const [imageStyle, setImageStyle] = useState('realistic');
  const [imageGenerating, setImageGenerating] = useState(false);
  
  // States pour le texte
  const [textPrompt, setTextPrompt] = useState('');
  const [textType, setTextType] = useState('article');
  const [textLength, setTextLength] = useState('medium');
  const [textGenerating, setTextGenerating] = useState(false);
  
  // States pour l'audio
  const [audioText, setAudioText] = useState('');
  const [audioType, setAudioType] = useState('speech');
  const [audioVoice, setAudioVoice] = useState('neutral');
  const [audioGenerating, setAudioGenerating] = useState(false);
  
  // States pour la lecture audio
  const [playingAudio, setPlayingAudio] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  // Fonction pour générer une vraie image
  const handleImageGeneration = async () => {
    if (!imagePrompt.trim()) return;
    
    setImageGenerating(true);
    try {
      console.log('🎨 REAL IMAGE GENERATION - Calling backend API');
      
      const response = await fetch('/api/generate/image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: imagePrompt,
          style: imageStyle,
          size: '1024x1024',
          quality: 'hd'
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Génération échouée');
      }
      
      console.log('✅ REAL IMAGE GENERATED:', result.provider);
      
      const newImage: GeneratedContent = {
        id: Date.now().toString(),
        type: 'image',
        prompt: imagePrompt,
        url: result.imageUrl,
        createdAt: new Date().toISOString(),
        title: `${result.provider}: ${imagePrompt.substring(0, 30)}...`,
        metadata: {
          source: result.provider,
          realGeneration: result.realGeneration,
          noFallback: result.noFallback,
          processingTime: result.processingTime
        }
      };
      
      setGeneratedContent(prev => [newImage, ...prev]);
      setImagePrompt('');
      
    } catch (error) {
      console.error('❌ REAL Image generation error:', error);
      
      // AUCUN FALLBACK - Affichage de l'erreur uniquement
      alert(`Erreur génération d'image: ${error}`);
      
    } finally {
      setImageGenerating(false);
    }
  };

  // Fonction pour générer du vrai texte
  const handleTextGeneration = async () => {
    if (!textPrompt.trim()) return;
    
    setTextGenerating(true);
    try {
      console.log('📝 REAL TEXT GENERATION - Calling backend API');
      
      const response = await fetch('/api/generate/text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: textPrompt,
          type: textType,
          length: textLength,
          tone: 'professional',
          language: 'fr'
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();
      console.log('✅ REAL TEXT GENERATED:', result.data.source);
      
      const newText: GeneratedContent = {
        id: Date.now().toString(),
        type: 'text',
        prompt: textPrompt,
        text: result.data.text,
        createdAt: new Date().toISOString(),
        title: `${result.data.source}: ${textPrompt.substring(0, 30)}...`,
        metadata: {
          source: result.data.source,
          fallback: result.data.fallback,
          tokens: result.data.tokens
        }
      };
      
      setGeneratedContent(prev => [newText, ...prev]);
      setTextPrompt('');
      
    } catch (error) {
      console.error('❌ REAL Text generation error:', error);
      
      // AUCUN FALLBACK - Affichage de l'erreur uniquement
      alert(`Erreur génération texte: ${error}`);
      
    } finally {
      setTextGenerating(false);
    }
  };

  // Fonction pour générer du vrai audio
  const handleAudioGeneration = async () => {
    if (audioType === 'speech' && !audioText.trim()) return;
    
    setAudioGenerating(true);
    try {
      console.log('🎵 REAL AUDIO GENERATION - Calling backend API');
      
      const response = await fetch('/api/generate/audio', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: audioText,
          type: audioType,
          voice: audioVoice,
          style: 'natural',
          language: 'fr'
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();
      console.log('✅ REAL AUDIO GENERATED:', result.data.source);
      
      const newAudio: GeneratedContent = {
        id: Date.now().toString(),
        type: 'audio',
        prompt: audioText || `${audioType} audio`,
        url: result.data.audioUrl,
        createdAt: new Date().toISOString(),
        title: `${result.data.source}: ${audioType === 'speech' ? audioText.substring(0, 30) : 'Generated Music'}`,
        metadata: {
          source: result.data.source,
          duration: result.data.duration,
          fallback: result.data.fallback
        }
      };
      
      setGeneratedContent(prev => [newAudio, ...prev]);
      setAudioText('');
      
    } catch (error) {
      console.error('❌ REAL Audio generation error:', error);
      
      // AUCUN FALLBACK - Affichage de l'erreur uniquement
      alert(`Erreur génération audio: ${error}`);
      
    } finally {
      setAudioGenerating(false);
    }
  };

  // Fonction pour jouer/arrêter l'audio
  const toggleAudioPlayback = (audioUrl: string, contentId: string) => {
    if (playingAudio === contentId) {
      audioRef.current?.pause();
      setPlayingAudio(null);
    } else {
      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.play();
        setPlayingAudio(contentId);
      }
    }
  };

  // Fonction pour copier le contenu
  const copyToClipboard = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  // Fonction pour télécharger le contenu
  const downloadContent = (content: GeneratedContent) => {
    if (content.type === 'text' && content.text) {
      const blob = new Blob([content.text], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${content.title}.txt`;
      a.click();
    } else if (content.url) {
      const a = document.createElement('a');
      a.href = content.url;
      a.download = `${content.title}.${content.type === 'image' ? 'jpg' : 'mp3'}`;
      a.click();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Wand2 className="h-8 w-8 text-purple-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">AI Studio</h1>
                <p className="text-sm text-gray-600">
                  Professional AI content generation with real APIs
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{generatedContent.length}</div>
                <div className="text-xs text-gray-500">Generated</div>
              </div>
              <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 flex items-center">
                <Sparkles className="h-4 w-4 mr-2" />
                New Project
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Generation Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm border p-6">
              {/* Tabs */}
              <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
                {[
                  { id: 'image', icon: ImageIcon, name: 'Image' },
                  { id: 'text', icon: FileText, name: 'Text' },
                  { id: 'audio', icon: Music, name: 'Audio' },
                  { id: 'video', icon: Video, name: 'Video' }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex-1 flex items-center justify-center py-2 px-3 rounded-md text-sm font-medium transition-colors ${
                      activeTab === tab.id
                        ? 'bg-white text-purple-700 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <tab.icon className="h-4 w-4 mr-2" />
                    {tab.name}
                  </button>
                ))}
              </div>

              {/* Image Generation */}
              {activeTab === 'image' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Image Prompt
                    </label>
                    <textarea
                      value={imagePrompt}
                      onChange={(e) => setImagePrompt(e.target.value)}
                      placeholder="Describe the image you want to generate..."
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      rows={3}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Style
                    </label>
                    <select
                      value={imageStyle}
                      onChange={(e) => setImageStyle(e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value="realistic">Realistic</option>
                      <option value="artistic">Artistic</option>
                      <option value="cartoon">Cartoon</option>
                      <option value="abstract">Abstract</option>
                    </select>
                  </div>
                  
                  <button
                    onClick={handleImageGeneration}
                    disabled={imageGenerating || !imagePrompt.trim()}
                    className="w-full bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  >
                    {imageGenerating ? (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        Generating Real Image...
                      </>
                    ) : (
                      <>
                        <ImageIcon className="h-4 w-4 mr-2" />
                        Generate Real Image
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* Text Generation */}
              {activeTab === 'text' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Text Prompt
                    </label>
                    <textarea
                      value={textPrompt}
                      onChange={(e) => setTextPrompt(e.target.value)}
                      placeholder="What content would you like to generate?"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      rows={3}
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Type
                      </label>
                      <select
                        value={textType}
                        onChange={(e) => setTextType(e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      >
                        <option value="article">Article</option>
                        <option value="story">Story</option>
                        <option value="description">Description</option>
                        <option value="script">Script</option>
                        <option value="email">Email</option>
                        <option value="social">Social Post</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Length
                      </label>
                      <select
                        value={textLength}
                        onChange={(e) => setTextLength(e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      >
                        <option value="short">Short</option>
                        <option value="medium">Medium</option>
                        <option value="long">Long</option>
                      </select>
                    </div>
                  </div>
                  
                  <button
                    onClick={handleTextGeneration}
                    disabled={textGenerating || !textPrompt.trim()}
                    className="w-full bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  >
                    {textGenerating ? (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        Generating Real Text...
                      </>
                    ) : (
                      <>
                        <FileText className="h-4 w-4 mr-2" />
                        Generate Real Text
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* Audio Generation */}
              {activeTab === 'audio' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Audio Type
                    </label>
                    <select
                      value={audioType}
                      onChange={(e) => setAudioType(e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value="speech">Text-to-Speech</option>
                      <option value="music">Music Generation</option>
                      <option value="sound_effect">Sound Effect</option>
                    </select>
                  </div>
                  
                  {audioType === 'speech' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Text to Speak
                      </label>
                      <textarea
                        value={audioText}
                        onChange={(e) => setAudioText(e.target.value)}
                        placeholder="Enter the text you want to convert to speech..."
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        rows={3}
                      />
                    </div>
                  )}
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Voice
                    </label>
                    <select
                      value={audioVoice}
                      onChange={(e) => setAudioVoice(e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value="neutral">Neutral</option>
                      <option value="female">Female</option>
                      <option value="male">Male</option>
                    </select>
                  </div>
                  
                  <button
                    onClick={handleAudioGeneration}
                    disabled={audioGenerating || (audioType === 'speech' && !audioText.trim())}
                    className="w-full bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  >
                    {audioGenerating ? (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        Generating Real Audio...
                      </>
                    ) : (
                      <>
                        <Music className="h-4 w-4 mr-2" />
                        Generate Real Audio
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* Video Generation */}
              {activeTab === 'video' && (
                <div className="space-y-4">
                  <div className="text-center py-8">
                    <Video className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Video Generation</h3>
                    <p className="text-gray-600 mb-4">Coming Soon</p>
                    <p className="text-sm text-gray-500">
                      Video generation capabilities will be available in the next update
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Generated Content */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Generated Content</h3>
              
              {generatedContent.length === 0 ? (
                <div className="text-center py-12">
                  <Sparkles className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No content generated yet</h3>
                  <p className="text-gray-600">Start creating with AI on the left panel</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {generatedContent.map((content) => (
                    <div key={content.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <div className={`p-2 rounded-lg ${
                            content.type === 'image' ? 'bg-blue-100' :
                            content.type === 'text' ? 'bg-green-100' :
                            content.type === 'audio' ? 'bg-purple-100' : 'bg-gray-100'
                          }`}>
                            {content.type === 'image' && <ImageIcon className="h-5 w-5 text-blue-600" />}
                            {content.type === 'text' && <FileText className="h-5 w-5 text-green-600" />}
                            {content.type === 'audio' && <Music className="h-5 w-5 text-purple-600" />}
                            {content.type === 'video' && <Video className="h-5 w-5 text-gray-600" />}
                          </div>
                          <div>
                            <h4 className="font-medium text-gray-900">{content.title}</h4>
                            <div className="flex items-center space-x-2 text-sm text-gray-500">
                              <span>{new Date(content.createdAt).toLocaleString()}</span>
                              {content.metadata?.source && (
                                <>
                                  <span>•</span>
                                  <span className={`flex items-center ${content.metadata.fallback ? 'text-orange-600' : 'text-green-600'}`}>
                                    {content.metadata.fallback ? <AlertCircle className="h-3 w-3 mr-1" /> : <Zap className="h-3 w-3 mr-1" />}
                                    {content.metadata.source}
                                  </span>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          {content.type === 'text' && content.text && (
                            <button
                              onClick={() => copyToClipboard(content.text!)}
                              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded"
                              title="Copy text"
                            >
                              <Copy className="h-4 w-4" />
                            </button>
                          )}
                          
                          <button
                            onClick={() => downloadContent(content)}
                            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded"
                            title="Download"
                          >
                            <Download className="h-4 w-4" />
                          </button>
                          
                          <button className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded" title="Favorite">
                            <Heart className="h-4 w-4" />
                          </button>
                          
                          <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded" title="Share">
                            <Share2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                      
                      {/* Content Display */}
                      {content.type === 'image' && content.url && (
                        <div className="relative">
                          <img
                            src={content.url}
                            alt={content.prompt}
                            className="w-full max-h-96 object-contain rounded-lg border"
                            style={{ minHeight: '200px' }}
                          />
                          <div className="absolute bottom-2 left-2 bg-black bg-opacity-75 text-white px-3 py-2 rounded-lg text-sm max-w-xs">
                            <p className="font-medium mb-1">Prompt:</p>
                            <p className="text-xs opacity-90">{content.prompt}</p>
                          </div>
                        </div>
                      )}
                      
                      {content.type === 'text' && content.text && (
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <pre className="whitespace-pre-wrap text-sm text-gray-800 font-sans">
                            {content.text}
                          </pre>
                        </div>
                      )}
                      
                      {content.type === 'audio' && content.url && (
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <button
                                onClick={() => toggleAudioPlayback(content.url!, content.id)}
                                className="p-2 bg-purple-600 text-white rounded-full hover:bg-purple-700"
                              >
                                {playingAudio === content.id ? (
                                  <Pause className="h-4 w-4" />
                                ) : (
                                  <Play className="h-4 w-4" />
                                )}
                              </button>
                              <div>
                                <div className="text-sm font-medium text-gray-900">
                                  {content.prompt || 'Generated Audio'}
                                </div>
                                {content.metadata?.duration && (
                                  <div className="text-xs text-gray-500">
                                    Duration: {content.metadata.duration}s
                                  </div>
                                )}
                              </div>
                            </div>
                            <Volume2 className="h-5 w-5 text-gray-400" />
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Hidden audio element for playback */}
      <audio
        ref={audioRef}
        onEnded={() => setPlayingAudio(null)}
        className="hidden"
      />
    </div>
  );
}