/**
 * 🎬 AVATAR LIVE STREAMING - Complete UI
 * ======================================
 * Interface complète pour diffuser un avatar IA en direct sur TikTok, Instagram, YouTube, Facebook
 * Avec tous les paramètres: plateforme, avatar, voix, script, durée, qualité
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Play, Square, Eye, Video, Upload, CheckCircle, Info, Tv, Clock, Users } from 'lucide-react';

// Types
interface StreamStats {
  totalStreams: number;
  totalViewers: number;
  totalDuration: number;
  platforms: Record<string, number>;
}

export default function AvatarLiveStreaming() {
  // État du streaming
  const [streamStatus, setStreamStatus] = useState<'idle' | 'preparing' | 'streaming' | 'paused' | 'stopped'>('idle');
  const [streamId, setStreamId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [viewers, setViewers] = useState(0);
  const [duration, setDuration] = useState(0);
  
  // Configuration
  const [platform, setPlatform] = useState<'youtube' | 'facebook' | 'instagram' | 'tiktok' | 'twitch'>('youtube');
  const [avatarType, setAvatarType] = useState<'photo' | 'generated'>('generated');
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPrompt, setAvatarPrompt] = useState('');
  const [voiceType, setVoiceType] = useState<'recorded' | 'tts' | 'cloned'>('tts');
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [script, setScript] = useState('');
  const [streamTitle, setStreamTitle] = useState('');
  const [streamDescription, setStreamDescription] = useState('');
  const [quality, setQuality] = useState<'720p' | '1080p' | '4k'>('1080p');
  const [enableLipSync, setEnableLipSync] = useState(true);
  const [enableAnimation, setEnableAnimation] = useState(true);
  
  // Statistiques
  const [stats, setStats] = useState<StreamStats>({
    totalStreams: 0,
    totalViewers: 0,
    totalDuration: 0,
    platforms: {}
  });

  // Charger les statistiques au montage
  useEffect(() => {
    fetchStats();
  }, []);

  // Timer pour la durée du stream
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (streamStatus === 'streaming') {
      interval = setInterval(() => {
        setDuration(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [streamStatus]);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/studios/avatar/live/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const startStream = async () => {
    // Validation
    if (!streamTitle) {
      alert('Veuillez entrer un titre pour le stream');
      return;
    }
    
    if (avatarType === 'photo' && !avatarFile) {
      alert('Veuillez upload une photo d\'avatar');
      return;
    }
    
    if (avatarType === 'generated' && !avatarPrompt) {
      alert('Veuillez décrire l\'avatar à générer');
      return;
    }

    setStreamStatus('preparing');
    setProgress(0);

    try {
      const formData = new FormData();
      formData.append('platform', platform);
      formData.append('title', streamTitle);
      formData.append('description', streamDescription);
      formData.append('quality', quality);
      formData.append('enable_lip_sync', enableLipSync.toString());
      formData.append('enable_animation', enableAnimation.toString());
      formData.append('avatar_type', avatarType);
      
      if (avatarType === 'photo' && avatarFile) {
        formData.append('avatar_image', avatarFile);
      } else if (avatarType === 'generated') {
        formData.append('avatar_prompt', avatarPrompt);
      }
      
      if (audioFile) formData.append('audio_file', audioFile);
      if (voiceType === 'tts' && script) formData.append('tts_script', script);

      const response = await fetch('/api/studios/avatar/live/start', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      
      if (data.success) {
        setStreamId(data.stream_id);
        setStreamStatus('streaming');
        
        // Simuler la progression
        simulateProgress();
        
        // Démarrer le polling pour les viewers
        startViewerPolling(data.stream_id);
      } else {
        alert('Erreur: ' + data.error);
        setStreamStatus('idle');
      }
    } catch (error) {
      console.error('Stream start error:', error);
      alert('Erreur lors du démarrage du stream');
      setStreamStatus('idle');
    }
  };

  const stopStream = async () => {
    if (!streamId) return;

    try {
      const response = await fetch(`/api/studios/avatar/live/${streamId}/stop`, {
        method: 'POST'
      });

      const data = await response.json();
      
      if (data.success) {
        setStreamStatus('stopped');
        alert(`Stream terminé!\nViewers: ${viewers}\nDurée: ${formatDuration(duration)}`);
      }
    } catch (error) {
      console.error('Stream stop error:', error);
    }
  };

  const simulateProgress = () => {
    let current = 0;
    const interval = setInterval(() => {
      current += 5;
      setProgress(current);
      if (current >= 100) {
        clearInterval(interval);
      }
    }, 200);
  };

  const startViewerPolling = (id: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/api/studios/avatar/live/${id}/status`);
        const data = await response.json();
        setViewers(data.viewers || 0);
      } catch (error) {
        console.error('Viewer polling error:', error);
      }
    }, 5000);
    
    // Cleanup on unmount
    return () => clearInterval(interval);
  };

  const formatDuration = (seconds: number): string => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Tv className="w-8 h-8" />
            Avatar Live Streaming
          </h1>
          <p className="text-gray-500 mt-1">Diffusez en direct avec un avatar IA sur les réseaux sociaux</p>
        </div>
        <span className={`px-4 py-2 rounded-full text-sm font-semibold ${
          streamStatus === 'streaming' ? 'bg-red-500 text-white' : 'bg-gray-200 text-gray-700'
        }`}>
          {streamStatus === 'streaming' && (
            <span className="inline-block w-2 h-2 bg-white rounded-full mr-2 animate-pulse" />
          )}
          {streamStatus === 'streaming' ? 'EN DIRECT' : streamStatus.toUpperCase()}
        </span>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center gap-3">
            <Tv className="w-8 h-8 text-blue-500" />
            <div>
              <p className="text-sm text-gray-500">Total Streams</p>
              <p className="text-2xl font-bold">{stats.totalStreams}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center gap-3">
            <Users className="w-8 h-8 text-green-500" />
            <div>
              <p className="text-sm text-gray-500">Total Viewers</p>
              <p className="text-2xl font-bold">{stats.totalViewers}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center gap-3">
            <Clock className="w-8 h-8 text-purple-500" />
            <div>
              <p className="text-sm text-gray-500">Durée Totale</p>
              <p className="text-2xl font-bold">{Math.floor(stats.totalDuration / 3600)}h</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center gap-3">
            <Eye className="w-8 h-8 text-orange-500" />
            <div>
              <p className="text-sm text-gray-500">Viewers Actuels</p>
              <p className="text-2xl font-bold">{viewers}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Configuration et Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Configuration</h3>
          
          <div className="space-y-4">
            {/* Plateforme */}
            <div>
              <label className="block text-sm font-medium mb-2">Plateforme</label>
              <select
                value={platform}
                onChange={(e) => setPlatform(e.target.value as any)}
                className="w-full p-2 border rounded-md"
              >
                <option value="youtube">🎥 YouTube Live</option>
                <option value="facebook">👥 Facebook Live</option>
                <option value="instagram">📸 Instagram Live</option>
                <option value="tiktok">🎵 TikTok Live</option>
                <option value="twitch">🎮 Twitch</option>
              </select>
            </div>

            {/* Titre */}
            <div>
              <label className="block text-sm font-medium mb-2">Titre du Stream</label>
              <input
                type="text"
                placeholder="Mon super live avec avatar IA"
                value={streamTitle}
                onChange={(e) => setStreamTitle(e.target.value)}
                className="w-full p-2 border rounded-md"
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium mb-2">Description</label>
              <textarea
                placeholder="Décrivez votre live..."
                value={streamDescription}
                onChange={(e) => setStreamDescription(e.target.value)}
                className="w-full min-h-[100px] p-2 border rounded-md"
              />
            </div>

            {/* Type Avatar */}
            <div>
              <label className="block text-sm font-medium mb-2">Type d'Avatar</label>
              <select
                value={avatarType}
                onChange={(e) => setAvatarType(e.target.value as any)}
                className="w-full p-2 border rounded-md"
              >
                <option value="generated">🤖 Générer par IA (prompt)</option>
                <option value="photo">📸 Upload photo</option>
              </select>
            </div>

            {/* Avatar - Génération par Prompt */}
            {avatarType === 'generated' && (
              <div>
                <label className="block text-sm font-medium mb-2">Prompt Avatar</label>
                <textarea
                  placeholder="Décrivez l'avatar souhaité (ex: 'jeune femme professionnelle, sourire, cheveux blonds, costume bleu')"
                  value={avatarPrompt}
                  onChange={(e) => setAvatarPrompt(e.target.value)}
                  className="w-full min-h-[100px] p-2 border rounded-md"
                />
                <p className="text-xs text-gray-500 mt-1">
                  🎨 L'avatar sera généré automatiquement par SDXL (portrait réaliste)
                </p>
              </div>
            )}

            {/* Avatar - Upload Photo */}
            {avatarType === 'photo' && (
              <div>
                <label className="block text-sm font-medium mb-2">Photo Avatar</label>
                <div className="border-2 border-dashed rounded-lg p-4 text-center cursor-pointer hover:bg-gray-50">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => setAvatarFile(e.target.files?.[0] || null)}
                    className="hidden"
                    id="avatar-upload"
                  />
                  <label htmlFor="avatar-upload" className="cursor-pointer">
                    <Upload className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                    <p className="text-sm text-gray-500">Cliquez pour upload une photo</p>
                  </label>
                  {avatarFile && (
                    <p className="text-sm text-green-600 mt-2 flex items-center justify-center gap-2">
                      <CheckCircle className="w-4 h-4" />
                      {avatarFile.name}
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Script TTS */}
            {voiceType === 'tts' && avatarType === 'photo' && (
              <div>
                <label className="block text-sm font-medium mb-2">Script (Text-to-Speech)</label>
                <textarea
                  placeholder="Tapez le texte que l'avatar va dire..."
                  value={script}
                  onChange={(e) => setScript(e.target.value)}
                  className="w-full min-h-[100px] p-2 border rounded-md"
                />
                <p className="text-xs text-gray-500 mt-1">
                  L'avatar parlera ce texte avec lip sync automatique
                </p>
              </div>
            )}

            {/* Audio Upload */}
            {voiceType === 'recorded' && (
              <div>
                <label className="block text-sm font-medium mb-2">Fichier Audio</label>
                <input
                  type="file"
                  accept="audio/*"
                  onChange={(e) => setAudioFile(e.target.files?.[0] || null)}
                  className="w-full p-2 border rounded-md"
                />
                <p className="text-xs text-gray-500 mt-1">
                  L'avatar sera synchronisé avec cet audio
                </p>
              </div>
            )}

            {/* Options avancées */}
            <div className="space-y-2">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <span className="text-sm font-medium">Lip Sync</span>
                <input
                  type="checkbox"
                  checked={enableLipSync}
                  onChange={(e) => setEnableLipSync(e.target.checked)}
                  className="w-5 h-5"
                />
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <span className="text-sm font-medium">Animation</span>
                <input
                  type="checkbox"
                  checked={enableAnimation}
                  onChange={(e) => setEnableAnimation(e.target.checked)}
                  className="w-5 h-5"
                />
              </div>
            </div>

            {/* Info */}
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="flex items-start gap-2">
                <Info className="w-5 h-5 text-blue-500 mt-0.5" />
                <div className="text-sm text-blue-700">
                  <p className="font-semibold mb-1">Technologie IA:</p>
                  <ul className="list-disc list-inside space-y-1">
                    <li>Wav2Lip pour le lip sync</li>
                    <li>SadTalker pour l'animation</li>
                    <li>Streaming RTMP temps réel</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Preview et Contrôles */}
        <div className="space-y-4">
          {/* Preview Video */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Eye className="w-5 h-5" />
              Preview Live
            </h3>
            <div className="relative bg-black rounded-lg overflow-hidden aspect-video">
              {streamStatus === 'streaming' ? (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center text-white">
                    <Video className="w-16 h-16 mx-auto mb-4 animate-pulse" />
                    <p className="text-xl font-bold">STREAMING EN DIRECT</p>
                    <p className="text-sm mt-2">{formatDuration(duration)}</p>
                  </div>
                </div>
              ) : (
                <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                  <div className="text-center">
                    <Video className="w-16 h-16 mx-auto mb-2" />
                    <p>Aperçu du stream</p>
                  </div>
                </div>
              )}
            </div>

            {/* Progress Bar */}
            {streamStatus === 'preparing' && (
              <div className="mt-4">
                <div className="flex justify-between text-sm mb-2">
                  <span>Préparation du stream...</span>
                  <span>{progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Contrôles */}
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="space-y-4">
              {streamStatus === 'idle' || streamStatus === 'stopped' ? (
                <button
                  onClick={startStream}
                  disabled={
                    !streamTitle || 
                    (avatarType === 'photo' && !avatarFile) ||
                    (avatarType === 'generated' && !avatarPrompt)
                  }
                  className="w-full py-3 px-4 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <Play className="w-5 h-5" />
                  Démarrer le Stream
                </button>
              ) : (
                <button
                  onClick={stopStream}
                  disabled={streamStatus === 'preparing'}
                  className="w-full py-3 px-4 bg-red-500 text-white rounded-lg font-semibold hover:bg-red-600 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <Square className="w-5 h-5" />
                  Arrêter le Stream
                </button>
              )}

              {streamStatus === 'streaming' && (
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="p-3 bg-gray-50 rounded">
                    <p className="text-gray-500">Durée</p>
                    <p className="font-bold">{formatDuration(duration)}</p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded">
                    <p className="text-gray-500">Viewers</p>
                    <p className="font-bold">{viewers}</p>
                  </div>
                </div>
              )}

              {streamStatus === 'streaming' && (
                <div className="p-4 bg-green-50 rounded-lg">
                  <div className="flex items-center gap-2 text-green-700">
                    <CheckCircle className="w-5 h-5" />
                    <span className="font-semibold">Stream actif sur {platform}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
