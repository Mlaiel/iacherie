/**
 * Remix Studio Components Index
 * 
 * Central export point for all Creative Studio Interface components.
 * Provides clean imports for the complete remix studio ecosystem.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Project: IA-Influencer Agent + Content Protection Platform
 * Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps
 * 
 * WARNING: This code is the intellectual property of Fahed Mlaiel.
 * Any unauthorized use, reproduction, or distribution without explicit written permission
 * is strictly prohibited and will be prosecuted to the full extent of the law.
 * 
 * Contact: mlaiel@live.de for licensing inquiries.
 */

// Main Studio Component
export { default as RemixStudioMain } from './RemixStudioMain';

// Collaboration Components
export { default as CollaborativeWorkspace } from '../remix_studio_effects/CollaborativeWorkspace';

// AI-Powered Components
export { default as AIAssistantInterface } from '../remix_studio_effects/AIAssistantInterface';
// Temporarily disabled while implementing core system
// export { default as StyleTransferPanel } from '../remix_studio_effects/StyleTransferPanel';
// export { default as QualityEnhancer } from '../remix_studio_effects/QualityEnhancer';

// Timeline and Editing Components
export { default as TimelineEditor } from './TimelineEditor';
export { default as LoopManager } from './LoopManager';

// Audio Processing Components
export { default as EffectsPanel } from '../remix_studio_effects/EffectsPanel';
export { default as TrackMixer } from '../remix_studio_audio/TrackMixer';
// Temporarily disabled while implementing core system
// export { default as VocalProcessor } from '../remix_studio_audio/VocalProcessor';

// Instrument and MIDI Components
export { default as InstrumentSelector } from '../remix_studio_effects/InstrumentSelector';
export { default as TempoController } from './TempoController';
// Temporarily disabled while implementing core system
// export { default as KeyTransposer } from '../remix_studio_effects/KeyTransposer';

// Visualization Components
export { default as WaveformVisualizer } from '../remix_studio_audio/WaveformVisualizer';
export { default as SpectrogramAnalyzer } from '../remix_studio_audio/SpectrogramAnalyzer';

// Export and Management Components
export { default as ExportManager } from '../remix_studio_effects/ExportManager';

// Styling System
export * from './remix_studio.styles';
export { default as studioStyles } from './remix_studio.styles';

// Type Definitions
export type RemixStudioComponent = 
  | 'timeline'
  | 'mixer'
  | 'effects'
  | 'instruments'
  | 'collaboration'
  | 'ai-assistant'
  | 'waveform'
  | 'spectrogram'
  | 'export';

export interface StudioComponentProps {
  className?: string;
  isVisible?: boolean;
  onToggleVisibility?: () => void;
}

export interface AudioTrack {
  id: string;
  name: string;
  type: 'audio' | 'midi' | 'instrument' | 'vocal' | 'drums' | 'bass';
  color: string;
  volume: number;
  pan: number;
  muted: boolean;
  solo: boolean;
  armed: boolean;
  audioUrl?: string;
  startTime: number;
  duration: number;
  length: number; // Track length in samples or beats
  effects: AudioEffect[];
}

export interface AudioEffect {
  id: string;
  type: 'reverb' | 'delay' | 'compressor' | 'eq' | 'distortion' | 'chorus' | 'filter';
  name: string;
  enabled: boolean;
  parameters: Record<string, number>;
  presetName?: string;
}

export interface StudioState {
  currentTime: number;
  isPlaying: boolean;
  isRecording: boolean;
  tempo: number;
  timeSignature: [number, number];
  key: string;
  tracks: AudioTrack[];
  selectedTracks: string[];
  zoomLevel: number;
  snapGrid: number;
  loopEnabled: boolean;
  loopStart: number;
  loopEnd: number;
}

export interface CollaborationUser {
  id: string;
  name: string;
  email: string;
  avatar: string;
  role: 'owner' | 'collaborator' | 'viewer';
  isOnline: boolean;
  cursor?: {
    x: number;
    y: number;
    timestamp: number;
  };
  selection?: {
    trackId: string;
    startTime: number;
    endTime: number;
  };
}

export interface AIAssistantSuggestion {
  id: string;
  type: 'harmony' | 'rhythm' | 'structure' | 'effects' | 'mixing' | 'mastering';
  title: string;
  description: string;
  confidence: number;
  parameters: Record<string, any>;
  previewUrl?: string;
  canApply: boolean;
}

export interface ExportSettings {
  format: 'wav' | 'mp3' | 'flac' | 'aac' | 'ogg';
  quality: 'low' | 'medium' | 'high' | 'lossless';
  sampleRate: 44100 | 48000 | 96000 | 192000;
  bitDepth: 16 | 24 | 32;
  channels: 'mono' | 'stereo';
  normalize: boolean;
  fadeIn: number;
  fadeOut: number;
  trimSilence: boolean;
}

// Hook Types
export type UseStudioHook = () => {
  state: StudioState;
  actions: {
    play: () => void;
    pause: () => void;
    stop: () => void;
    record: () => void;
    seek: (time: number) => void;
    setTempo: (tempo: number) => void;
    addTrack: (track: Omit<AudioTrack, 'id'>) => void;
    removeTrack: (trackId: string) => void;
    updateTrack: (trackId: string, updates: Partial<AudioTrack>) => void;
    selectTrack: (trackId: string, multiSelect?: boolean) => void;
    deselectAllTracks: () => void;
  };
};

export type UseCollaborationHook = () => {
  users: CollaborationUser[];
  currentUser: CollaborationUser | null;
  isConnected: boolean;
  sendMessage: (message: string) => void;
  shareSelection: (selection: CollaborationUser['selection']) => void;
  requestControl: (trackId: string) => void;
  releaseControl: (trackId: string) => void;
};

export type UseAIAssistantHook = () => {
  suggestions: AIAssistantSuggestion[];
  isAnalyzing: boolean;
  generateSuggestions: (context: Partial<StudioState>) => Promise<void>;
  applySuggestion: (suggestionId: string) => Promise<void>;
  dismissSuggestion: (suggestionId: string) => void;
  setFeedback: (suggestionId: string, helpful: boolean) => void;
};