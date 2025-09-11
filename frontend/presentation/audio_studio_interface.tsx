/**
 * 🎵 Audio Studio Professional - Advanced Audio Processing Interface
 * 
 * @fileoverview Professional audio editing and processing studio interface
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

'use client';

import React, { useState, useRef, useEffect, useCallback, createContext, useContext } from 'react';
import {
  PlayIcon,
  PauseIcon,
  StopIcon,
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
  AdjustmentsHorizontalIcon,
  ArrowUpTrayIcon,
  ArrowDownTrayIcon,
  ScissorsIcon,
  DocumentDuplicateIcon,
  TrashIcon
} from '@heroicons/react/24/outline';

// === AUDIO TYPES ===

export interface AudioTrack {
  id: string;
  name: string;
  url: string;
  duration: number;
  sampleRate: number;
  channels: number;
  bitRate: number;
  format: 'mp3' | 'wav' | 'aac' | 'flac' | 'ogg';
  volume: number;
  muted: boolean;
  solo: boolean;
  effects: AudioEffect[];
  waveformData?: Float32Array[];
  markers: AudioMarker[];
  regions: AudioRegion[];
  createdAt: number;
  updatedAt: number;
}

export interface AudioEffect {
  id: string;
  type: 'reverb' | 'delay' | 'chorus' | 'distortion' | 'equalizer' | 'compressor' | 'limiter' | 'noise_gate' | 'filter';
  name: string;
  enabled: boolean;
  parameters: Record<string, number>;
  presets: EffectPreset[];
  order: number;
}

export interface EffectPreset {
  id: string;
  name: string;
  parameters: Record<string, number>;
  description?: string;
}

export interface AudioMarker {
  id: string;
  time: number;
  label: string;
  color?: string;
  type: 'marker' | 'cue' | 'chapter' | 'bookmark';
}

export interface AudioRegion {
  id: string;
  startTime: number;
  endTime: number;
  label?: string;
  color?: string;
  fadeIn?: number;
  fadeOut?: number;
  loop?: boolean;
}

export interface AudioProject {
  id: string;
  name: string;
  description?: string;
  tempo: number;
  sampleRate: number;
  tracks: AudioTrack[];
  masterVolume: number;
  masterEffects: AudioEffect[];
  length: number;
  createdAt: number;
  updatedAt: number;
  metadata?: {
    artist?: string;
    album?: string;
    genre?: string;
    year?: number;
    artwork?: string;
  };
}

export interface PlaybackState {
  isPlaying: boolean;
  isPaused: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  playbackRate: number;
  loopEnabled: boolean;
  loopStart?: number;
  loopEnd?: number;
}

export interface AudioAnalysis {
  rms: number;
  peak: number;
  frequency: number[];
  spectralCentroid: number;
  zeroCrossings: number;
  mfcc: number[];
  tempo?: number;
  key?: string;
  loudness: number;
}

// === AUDIO ENGINE ===

export class AudioEngine {
  private audioContext: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private analyser: AnalyserNode | null = null;
  private tracks: Map<string, AudioTrackNode> = new Map();
  private isInitialized = false;

  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    this.masterGain = this.audioContext.createGain();
    this.analyser = this.audioContext.createAnalyser();
    
    this.masterGain.connect(this.analyser);
    this.analyser.connect(this.audioContext.destination);
    
    this.analyser.fftSize = 2048;
    this.isInitialized = true;
  }

  async loadTrack(track: AudioTrack): Promise<AudioTrackNode> {
    if (!this.audioContext || !this.masterGain) {
      throw new Error('AudioEngine not initialized');
    }

    const response = await fetch(track.url);
    const arrayBuffer = await response.arrayBuffer();
    const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);

    const source = this.audioContext.createBufferSource();
    const gainNode = this.audioContext.createGain();
    const panNode = this.audioContext.createStereoPanner();

    source.buffer = audioBuffer;
    source.connect(gainNode);
    gainNode.connect(panNode);
    panNode.connect(this.masterGain);

    const trackNode: AudioTrackNode = {
      id: track.id,
      source,
      gainNode,
      panNode,
      audioBuffer,
      effects: [],
      isPlaying: false,
      startTime: 0
    };

    this.tracks.set(track.id, trackNode);
    return trackNode;
  }

  async playTrack(trackId: string, when: number = 0, offset: number = 0): Promise<void> {
    const trackNode = this.tracks.get(trackId);
    if (!trackNode || !this.audioContext) return;

    if (trackNode.isPlaying) {
      this.stopTrack(trackId);
    }

    // Create new source (required after each play)
    const newSource = this.audioContext.createBufferSource();
    newSource.buffer = trackNode.audioBuffer;
    newSource.connect(trackNode.gainNode);

    newSource.start(when, offset);
    trackNode.source = newSource;
    trackNode.isPlaying = true;
    trackNode.startTime = this.audioContext.currentTime - offset;
  }

  stopTrack(trackId: string): void {
    const trackNode = this.tracks.get(trackId);
    if (!trackNode) return;

    try {
      trackNode.source.stop();
    } catch (error) {
      // Source might already be stopped
    }
    
    trackNode.isPlaying = false;
  }

  setTrackVolume(trackId: string, volume: number): void {
    const trackNode = this.tracks.get(trackId);
    if (!trackNode) return;

    trackNode.gainNode.gain.value = volume;
  }

  setTrackPan(trackId: string, pan: number): void {
    const trackNode = this.tracks.get(trackId);
    if (!trackNode) return;

    trackNode.panNode.pan.value = Math.max(-1, Math.min(1, pan));
  }

  setMasterVolume(volume: number): void {
    if (this.masterGain) {
      this.masterGain.gain.value = volume;
    }
  }

  getAnalysisData(): AudioAnalysis {
    if (!this.analyser) {
      return {
        rms: 0,
        peak: 0,
        frequency: [],
        spectralCentroid: 0,
        zeroCrossings: 0,
        mfcc: [],
        loudness: 0
      };
    }

    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    this.analyser.getByteFrequencyData(dataArray);

    const rms = Math.sqrt(dataArray.reduce((sum, value) => sum + value * value, 0) / bufferLength) / 255;
    const peak = Math.max(...dataArray) / 255;
    const frequency = Array.from(dataArray).map(v => v / 255);

    return {
      rms,
      peak,
      frequency,
      spectralCentroid: this.calculateSpectralCentroid(dataArray),
      zeroCrossings: 0, // Would need time domain data
      mfcc: [], // Complex calculation
      loudness: this.calculateLoudness(dataArray)
    };
  }

  private calculateSpectralCentroid(frequencyData: Uint8Array): number {
    let numerator = 0;
    let denominator = 0;

    for (let i = 0; i < frequencyData.length; i++) {
      numerator += i * frequencyData[i];
      denominator += frequencyData[i];
    }

    return denominator > 0 ? numerator / denominator : 0;
  }

  private calculateLoudness(frequencyData: Uint8Array): number {
    const sum = frequencyData.reduce((acc, val) => acc + val, 0);
    return 20 * Math.log10((sum / frequencyData.length) / 255 + 0.0001);
  }

  dispose(): void {
    this.tracks.forEach(track => this.stopTrack(track.id));
    this.tracks.clear();
    
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    
    this.isInitialized = false;
  }
}

interface AudioTrackNode {
  id: string;
  source: AudioBufferSourceNode;
  gainNode: GainNode;
  panNode: StereoPannerNode;
  audioBuffer: AudioBuffer;
  effects: AudioNode[];
  isPlaying: boolean;
  startTime: number;
}

// === AUDIO CONTEXT ===

interface AudioStudioContextValue {
  project: AudioProject | null;
  playbackState: PlaybackState;
  selectedTrack: string | null;
  audioEngine: AudioEngine;
  isRecording: boolean;
  createProject: (name: string) => void;
  loadProject: (projectData: AudioProject) => void;
  addTrack: (file: File) => Promise<void>;
  removeTrack: (trackId: string) => void;
  selectTrack: (trackId: string) => void;
  play: () => void;
  pause: () => void;
  stop: () => void;
  seek: (time: number) => void;
  setVolume: (trackId: string, volume: number) => void;
  setMasterVolume: (volume: number) => void;
  addEffect: (trackId: string, effect: AudioEffect) => void;
  removeEffect: (trackId: string, effectId: string) => void;
  exportProject: (format: 'wav' | 'mp3') => Promise<Blob>;
}

const AudioStudioContext = createContext<AudioStudioContextValue | null>(null);

export const useAudioStudio = () => {
  const context = useContext(AudioStudioContext);
  if (!context) {
    throw new Error('useAudioStudio must be used within an AudioStudioProvider');
  }
  return context;
};

// === AUDIO STUDIO PROVIDER ===

interface AudioStudioProviderProps {
  children: React.ReactNode;
}

export const AudioStudioProvider: React.FC<AudioStudioProviderProps> = ({ children }) => {
  const [project, setProject] = useState<AudioProject | null>(null);
  const [playbackState, setPlaybackState] = useState<PlaybackState>({
    isPlaying: false,
    isPaused: false,
    currentTime: 0,
    duration: 0,
    volume: 1,
    playbackRate: 1,
    loopEnabled: false
  });
  const [selectedTrack, setSelectedTrack] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);

  const audioEngineRef = useRef(new AudioEngine());
  const animationFrameRef = useRef<number>();

  useEffect(() => {
    audioEngineRef.current.initialize();
    
    return () => {
      audioEngineRef.current.dispose();
    };
  }, []);

  const updatePlaybackTime = useCallback(() => {
    if (playbackState.isPlaying) {
      setPlaybackState(prev => ({
        ...prev,
        currentTime: prev.currentTime + 0.1
      }));
      animationFrameRef.current = requestAnimationFrame(updatePlaybackTime);
    }
  }, [playbackState.isPlaying]);

  useEffect(() => {
    if (playbackState.isPlaying) {
      animationFrameRef.current = requestAnimationFrame(updatePlaybackTime);
    } else {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [playbackState.isPlaying, updatePlaybackTime]);

  const createProject = useCallback((name: string) => {
    const newProject: AudioProject = {
      id: `project_${Date.now()}`,
      name,
      tempo: 120,
      sampleRate: 44100,
      tracks: [],
      masterVolume: 1,
      masterEffects: [],
      length: 0,
      createdAt: Date.now(),
      updatedAt: Date.now()
    };

    setProject(newProject);
  }, []);

  const loadProject = useCallback((projectData: AudioProject) => {
    setProject(projectData);
  }, []);

  const addTrack = useCallback(async (file: File) => {
    if (!project) return;

    const url = URL.createObjectURL(file);
    const audio = new Audio(url);
    
    await new Promise((resolve) => {
      audio.onloadedmetadata = resolve;
    });

    const newTrack: AudioTrack = {
      id: `track_${Date.now()}`,
      name: file.name,
      url,
      duration: audio.duration,
      sampleRate: 44100,
      channels: 2,
      bitRate: 320,
      format: file.name.split('.').pop() as any || 'mp3',
      volume: 1,
      muted: false,
      solo: false,
      effects: [],
      markers: [],
      regions: [],
      createdAt: Date.now(),
      updatedAt: Date.now()
    };

    setProject(prev => prev ? {
      ...prev,
      tracks: [...prev.tracks, newTrack],
      length: Math.max(prev.length, newTrack.duration),
      updatedAt: Date.now()
    } : null);

    // Load track into audio engine
    await audioEngineRef.current.loadTrack(newTrack);
  }, [project]);

  const removeTrack = useCallback((trackId: string) => {
    if (!project) return;

    audioEngineRef.current.stopTrack(trackId);
    
    setProject(prev => prev ? {
      ...prev,
      tracks: prev.tracks.filter(t => t.id !== trackId),
      updatedAt: Date.now()
    } : null);

    if (selectedTrack === trackId) {
      setSelectedTrack(null);
    }
  }, [project, selectedTrack]);

  const selectTrack = useCallback((trackId: string) => {
    setSelectedTrack(trackId);
  }, []);

  const play = useCallback(() => {
    if (!project) return;

    project.tracks.forEach(track => {
      audioEngineRef.current.playTrack(track.id, 0, playbackState.currentTime);
    });

    setPlaybackState(prev => ({
      ...prev,
      isPlaying: true,
      isPaused: false
    }));
  }, [project, playbackState.currentTime]);

  const pause = useCallback(() => {
    if (!project) return;

    project.tracks.forEach(track => {
      audioEngineRef.current.stopTrack(track.id);
    });

    setPlaybackState(prev => ({
      ...prev,
      isPlaying: false,
      isPaused: true
    }));
  }, [project]);

  const stop = useCallback(() => {
    if (!project) return;

    project.tracks.forEach(track => {
      audioEngineRef.current.stopTrack(track.id);
    });

    setPlaybackState(prev => ({
      ...prev,
      isPlaying: false,
      isPaused: false,
      currentTime: 0
    }));
  }, [project]);

  const seek = useCallback((time: number) => {
    setPlaybackState(prev => ({
      ...prev,
      currentTime: time
    }));

    if (playbackState.isPlaying && project) {
      // Restart playback from new position
      project.tracks.forEach(track => {
        audioEngineRef.current.stopTrack(track.id);
        audioEngineRef.current.playTrack(track.id, 0, time);
      });
    }
  }, [playbackState.isPlaying, project]);

  const setVolume = useCallback((trackId: string, volume: number) => {
    audioEngineRef.current.setTrackVolume(trackId, volume);
    
    if (project) {
      setProject(prev => prev ? {
        ...prev,
        tracks: prev.tracks.map(t => 
          t.id === trackId ? { ...t, volume } : t
        )
      } : null);
    }
  }, [project]);

  const setMasterVolume = useCallback((volume: number) => {
    audioEngineRef.current.setMasterVolume(volume);
    
    if (project) {
      setProject(prev => prev ? {
        ...prev,
        masterVolume: volume
      } : null);
    }
  }, [project]);

  const addEffect = useCallback((trackId: string, effect: AudioEffect) => {
    if (!project) return;

    setProject(prev => prev ? {
      ...prev,
      tracks: prev.tracks.map(t => 
        t.id === trackId 
          ? { ...t, effects: [...t.effects, effect] }
          : t
      )
    } : null);
  }, [project]);

  const removeEffect = useCallback((trackId: string, effectId: string) => {
    if (!project) return;

    setProject(prev => prev ? {
      ...prev,
      tracks: prev.tracks.map(t => 
        t.id === trackId 
          ? { ...t, effects: t.effects.filter(e => e.id !== effectId) }
          : t
      )
    } : null);
  }, [project]);

  const exportProject = useCallback(async (format: 'wav' | 'mp3'): Promise<Blob> => {
    // This would implement actual audio rendering and export
    // For now, return empty blob
    return new Blob([], { type: `audio/${format}` });
  }, []);

  const contextValue: AudioStudioContextValue = {
    project,
    playbackState,
    selectedTrack,
    audioEngine: audioEngineRef.current,
    isRecording,
    createProject,
    loadProject,
    addTrack,
    removeTrack,
    selectTrack,
    play,
    pause,
    stop,
    seek,
    setVolume,
    setMasterVolume,
    addEffect,
    removeEffect,
    exportProject
  };

  return (
    <AudioStudioContext.Provider value={contextValue}>
      {children}
    </AudioStudioContext.Provider>
  );
};

// === AUDIO STUDIO COMPONENTS ===

interface AudioStudioInterfaceProps {
  className?: string;
}

export const AudioStudioInterface: React.FC<AudioStudioInterfaceProps> = ({ className }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  return (
    <AudioStudioProvider>
      <div className={`h-screen bg-gray-900 text-white flex flex-col ${className}`}>
        <AudioStudioHeader />
        <div className="flex-1 flex">
          <AudioStudioSidebar />
          <div className="flex-1 flex flex-col">
            <AudioStudioTimeline />
            <AudioStudioTracks />
          </div>
        </div>
        <AudioStudioControls />
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          multiple
          className="hidden"
        />
      </div>
    </AudioStudioProvider>
  );
};

const AudioStudioHeader: React.FC = () => {
  const { project, createProject } = useAudioStudio();
  
  return (
    <div className="h-16 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-6">
      <div className="flex items-center space-x-4">
        <h1 className="text-xl font-bold">Audio Studio Pro</h1>
        {project && (
          <span className="text-gray-400">• {project.name}</span>
        )}
      </div>
      
      <div className="flex items-center space-x-2">
        <button
          onClick={() => createProject('New Project')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          New Project
        </button>
        <button className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
          Save
        </button>
        <button className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
          Export
        </button>
      </div>
    </div>
  );
};

const AudioStudioSidebar: React.FC = () => {
  const { addTrack } = useAudioStudio();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      Array.from(files).forEach(file => addTrack(file));
    }
  };

  return (
    <div className="w-64 bg-gray-800 border-r border-gray-700 p-4">
      <div className="space-y-4">
        <button
          onClick={() => fileInputRef.current?.click()}
          className="w-full flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          <ArrowUpTrayIcon className="w-5 h-5 mr-2" />
          Import Audio
        </button>
        
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-gray-400 uppercase">Effects</h3>
          <div className="space-y-1">
            {['Reverb', 'Delay', 'Chorus', 'Distortion', 'EQ', 'Compressor'].map(effect => (
              <div
                key={effect}
                className="p-2 bg-gray-700 rounded text-sm cursor-pointer hover:bg-gray-600"
              >
                {effect}
              </div>
            ))}
          </div>
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          multiple
          onChange={handleFileUpload}
          className="hidden"
        />
      </div>
    </div>
  );
};

const AudioStudioTimeline: React.FC = () => {
  const { playbackState, seek } = useAudioStudio();
  
  const handleTimelineClick = (event: React.MouseEvent<HTMLDivElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const percentage = x / rect.width;
    const newTime = percentage * playbackState.duration;
    seek(newTime);
  };

  return (
    <div className="h-16 bg-gray-700 border-b border-gray-600 flex items-center px-4">
      <div className="flex-1 relative">
        <div
          className="h-8 bg-gray-600 rounded cursor-pointer"
          onClick={handleTimelineClick}
        >
          <div
            className="h-full bg-blue-500 rounded"
            style={{
              width: `${playbackState.duration > 0 ? (playbackState.currentTime / playbackState.duration) * 100 : 0}%`
            }}
          />
        </div>
        <div className="absolute top-0 left-0 right-0 flex justify-between text-xs text-gray-400 mt-10">
          <span>{formatTime(playbackState.currentTime)}</span>
          <span>{formatTime(playbackState.duration)}</span>
        </div>
      </div>
    </div>
  );
};

const AudioStudioTracks: React.FC = () => {
  const { project, selectedTrack, selectTrack, removeTrack, setVolume } = useAudioStudio();
  
  if (!project || project.tracks.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center text-gray-400">
          <p className="text-lg">No tracks loaded</p>
          <p className="text-sm">Import audio files to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      {project.tracks.map(track => (
        <div
          key={track.id}
          className={`h-24 border-b border-gray-600 flex items-center p-4 ${
            selectedTrack === track.id ? 'bg-gray-700' : 'bg-gray-800'
          }`}
          onClick={() => selectTrack(track.id)}
        >
          <div className="w-48 pr-4">
            <div className="font-medium truncate">{track.name}</div>
            <div className="text-sm text-gray-400">
              {formatTime(track.duration)} • {track.format.toUpperCase()}
            </div>
          </div>
          
          <div className="flex-1 h-16 bg-gray-600 rounded relative overflow-hidden">
            {/* Waveform visualization would go here */}
            <div className="h-full bg-gradient-to-r from-blue-500 to-purple-500 opacity-30" />
          </div>
          
          <div className="w-32 pl-4 flex items-center space-x-2">
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={track.volume}
              onChange={(e) => setVolume(track.id, parseFloat(e.target.value))}
              className="flex-1"
            />
            <button
              onClick={(e) => {
                e.stopPropagation();
                removeTrack(track.id);
              }}
              className="p-1 text-gray-400 hover:text-red-400"
            >
              <TrashIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

const AudioStudioControls: React.FC = () => {
  const { playbackState, play, pause, stop, setMasterVolume } = useAudioStudio();
  
  return (
    <div className="h-20 bg-gray-800 border-t border-gray-700 flex items-center justify-between px-6">
      <div className="flex items-center space-x-4">
        <button
          onClick={playbackState.isPlaying ? pause : play}
          className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center hover:bg-blue-700"
        >
          {playbackState.isPlaying ? (
            <PauseIcon className="w-6 h-6" />
          ) : (
            <PlayIcon className="w-6 h-6 ml-1" />
          )}
        </button>
        
        <button
          onClick={stop}
          className="w-10 h-10 bg-gray-600 rounded-full flex items-center justify-center hover:bg-gray-700"
        >
          <StopIcon className="w-5 h-5" />
        </button>
      </div>
      
      <div className="flex items-center space-x-4">
        <span className="text-sm text-gray-400">Master</span>
        <div className="flex items-center space-x-2">
          <SpeakerWaveIcon className="w-5 h-5 text-gray-400" />
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={playbackState.volume}
            onChange={(e) => setMasterVolume(parseFloat(e.target.value))}
            className="w-24"
          />
        </div>
      </div>
    </div>
  );
};

// === UTILITY FUNCTIONS ===

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export default AudioStudioInterface;