'use client';

/**
 * Remix Studio Main Interface
 * 
 * Central orchestrator for the Creative Studio Interface.
 * Manages layout, state coordination, and component integration.
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

import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { 
  PlayIcon, 
  PauseIcon, 
  StopIcon, 
  MicrophoneIcon,
  Cog6ToothIcon,
  ShareIcon,
  DocumentArrowDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { useAppContext } from '@/app/providers';
import { useNotifications } from '@/hooks/useNotifications';
import TimelineEditor from '../remix_studio/TimelineEditor';
import TrackMixer from '../remix_studio_audio/TrackMixer';
import EffectsPanel from '../remix_studio_effects/EffectsPanel';
import InstrumentSelector from '../remix_studio_effects/InstrumentSelector';
import AIAssistantInterface from '../remix_studio_effects/AIAssistantInterface';
import CollaborativeWorkspace from '../remix_studio_effects/CollaborativeWorkspace';
import WaveformVisualizer from '../remix_studio_audio/WaveformVisualizer';
import SpectrogramAnalyzer from '../remix_studio_audio/SpectrogramAnalyzer';
import ExportManager from '../remix_studio_effects/ExportManager';
import { studioColors, studioUtils } from '../remix_studio/remix_studio.styles';
import type { StudioState, AudioTrack, RemixStudioComponent } from '../remix_studio/index';

interface RemixStudioMainProps {
  projectId?: string;
  className?: string;
  onSave?: (projectData: any) => void;
  onExport?: (exportData: any) => void;
}

const RemixStudioMain: React.FC<RemixStudioMainProps> = ({
  projectId,
  className = '',
  onSave,
  onExport
}) => {
  const { state } = useAppContext();
  const { success, error, info } = useNotifications();

  // Studio State Management
  const [studioState, setStudioState] = useState<StudioState>({
    currentTime: 0,
    isPlaying: false,
    isRecording: false,
    tempo: 120,
    timeSignature: [4, 4],
    key: 'C',
    tracks: [
      {
        id: 'track-1',
        name: 'Main Vocal',
        color: studioUtils.getTrackColor(0),
        volume: 0.8,
        pan: 0,
        muted: false,
        solo: false,
        armed: false,
        startTime: 0,
        duration: 180000,
        effects: []
      },
      {
        id: 'track-2', 
        name: 'Instrumental',
        color: studioUtils.getTrackColor(1),
        volume: 0.7,
        pan: 0,
        muted: false,
        solo: false,
        armed: false,
        startTime: 0,
        duration: 180000,
        effects: []
      }
    ],
    selectedTracks: [],
    zoomLevel: 1,
    snapGrid: 0.25,
    loopEnabled: false,
    loopStart: 0,
    loopEnd: 60000
  });

  // UI State Management
  const [activeComponents, setActiveComponents] = useState<Set<RemixStudioComponent>>(
    new Set(['timeline', 'mixer', 'waveform'] as RemixStudioComponent[])
  );
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Transport Controls
  const handlePlay = useCallback(() => {
    if (studioState.isPlaying) {
      setStudioState(prev => ({ ...prev, isPlaying: false }));
      info('Playback paused');
    } else {
      setStudioState(prev => ({ ...prev, isPlaying: true, isRecording: false }));
      success('Playback started');
    }
  }, [studioState.isPlaying, info, success]);

  const handleStop = useCallback(() => {
    setStudioState(prev => ({ 
      ...prev, 
      isPlaying: false, 
      isRecording: false,
      currentTime: 0 
    }));
    info('Playback stopped');
  }, [info]);

  const handleRecord = useCallback(() => {
    if (studioState.isRecording) {
      setStudioState(prev => ({ ...prev, isRecording: false }));
      info('Recording stopped');
    } else {
      setStudioState(prev => ({ 
        ...prev, 
        isRecording: true, 
        isPlaying: true 
      }));
      success('Recording started');
    }
  }, [studioState.isRecording, info, success]);

  // Track Management
  const addTrack = useCallback((track: Omit<AudioTrack, 'id'>) => {
    const newTrack: AudioTrack = {
      ...track,
      id: `track-${Date.now()}`,
      color: studioUtils.getTrackColor(studioState.tracks.length)
    };
    
    setStudioState(prev => ({
      ...prev,
      tracks: [...prev.tracks, newTrack]
    }));
    
    success(`Track "${newTrack.name}" added`);
  }, [studioState.tracks.length, success]);

  const updateTrack = useCallback((trackId: string, updates: Partial<AudioTrack>) => {
    setStudioState(prev => ({
      ...prev,
      tracks: prev.tracks.map(track => 
        track.id === trackId ? { ...track, ...updates } : track
      )
    }));
  }, []);

  const removeTrack = useCallback((trackId: string) => {
    const track = studioState.tracks.find(t => t.id === trackId);
    if (track) {
      setStudioState(prev => ({
        ...prev,
        tracks: prev.tracks.filter(t => t.id !== trackId),
        selectedTracks: prev.selectedTracks.filter(id => id !== trackId)
      }));
      info(`Track "${track.name}" removed`);
    }
  }, [studioState.tracks, info]);

  // Component Toggle Management
  const toggleComponent = useCallback((component: RemixStudioComponent) => {
    setActiveComponents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(component)) {
        newSet.delete(component);
      } else {
        newSet.add(component);
      }
      return newSet;
    });
  }, []);

  // Project Management
  const handleSave = useCallback(async () => {
    try {
      const projectData = {
        id: projectId,
        state: studioState,
        timestamp: new Date().toISOString(),
        version: '1.0.0'
      };
      
      if (onSave) {
        await onSave(projectData);
      }
      
      success('Project saved successfully');
    } catch (err) {
      error('Failed to save project');
    }
  }, [projectId, studioState, onSave, success, error]);

  // Keyboard Shortcuts
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (event.code) {
        case 'Space':
          event.preventDefault();
          handlePlay();
          break;
        case 'KeyS':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            handleSave();
          }
          break;
        case 'KeyR':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            handleRecord();
          }
          break;
        case 'Escape':
          handleStop();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [handlePlay, handleSave, handleRecord, handleStop]);

  // Memoized component visibility checks
  const showTimeline = activeComponents.has('timeline');
  const showMixer = activeComponents.has('mixer');
  const showEffects = activeComponents.has('effects');
  const showInstruments = activeComponents.has('instruments');
  const showAI = activeComponents.has('ai-assistant');
  const showCollaboration = activeComponents.has('collaboration');
  const showWaveform = activeComponents.has('waveform');
  const showSpectrogram = activeComponents.has('spectrogram');

  const transportControlsClass = studioUtils.getClassName(
    'flex items-center space-x-2 bg-gray-900 p-3 rounded-lg'
  );

  return (
    <div className={studioUtils.getClassName(
      'remix-studio-main h-screen flex flex-col bg-gray-950 text-white',
      className
    )}>
      {/* Header Bar */}
      <header className="flex items-center justify-between p-4 bg-gray-900 border-b border-gray-700">
        <div className="flex items-center space-x-4">
          <button 
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            {sidebarCollapsed ? <ChevronRightIcon className="h-5 w-5" /> : <ChevronLeftIcon className="h-5 w-5" />}
          </button>
          
          <h1 className="text-xl font-bold text-white">
            Remix Studio
          </h1>
          
          <div className="text-sm text-gray-400">
            {projectId ? `Project: ${projectId}` : 'Untitled Project'}
          </div>
        </div>

        {/* Transport Controls */}
        <div className={transportControlsClass}>
          <button
            onClick={handleStop}
            className="p-2 hover:bg-gray-700 rounded transition-colors"
            title="Stop (Esc)"
          >
            <StopIcon className="h-5 w-5" style={{ color: studioColors.status.stopped }} />
          </button>
          
          <button
            onClick={handlePlay}
            className="p-3 hover:bg-gray-700 rounded transition-colors"
            title="Play/Pause (Space)"
          >
            {studioState.isPlaying ? (
              <PauseIcon className="h-6 w-6" style={{ color: studioColors.status.playing }} />
            ) : (
              <PlayIcon className="h-6 w-6" style={{ color: studioColors.status.playing }} />
            )}
          </button>
          
          <button
            onClick={handleRecord}
            className={studioUtils.getClassName(
              'p-2 rounded transition-colors',
              studioState.isRecording ? 'bg-red-600 hover:bg-red-700' : 'hover:bg-gray-700'
            )}
            title="Record (Ctrl+R)"
          >
            <MicrophoneIcon 
              className="h-5 w-5" 
              style={{ color: studioState.isRecording ? 'white' : studioColors.status.recording }} 
            />
          </button>
          
          <div className="mx-4 text-sm font-mono">
            {studioUtils.msToTime(studioState.currentTime)}
          </div>
          
          <div className="text-sm">
            {studioState.tempo} BPM
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleSave}
            className="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded transition-colors text-sm"
            title="Save (Ctrl+S)"
          >
            Save
          </button>
          
          <button
            onClick={() => setShowExportDialog(true)}
            className="p-2 hover:bg-gray-800 rounded transition-colors"
            title="Export"
          >
            <DocumentArrowDownIcon className="h-5 w-5" />
          </button>
          
          <button
            onClick={() => toggleComponent('collaboration')}
            className={studioUtils.getClassName(
              'p-2 rounded transition-colors',
              showCollaboration ? 'bg-blue-600 hover:bg-blue-700' : 'hover:bg-gray-800'
            )}
            title="Collaboration"
          >
            <ShareIcon className="h-5 w-5" />
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        {!sidebarCollapsed && (
          <aside className="w-80 bg-gray-900 border-r border-gray-700 flex flex-col">
            {/* Component Toggles */}
            <div className="p-4 border-b border-gray-700">
              <h3 className="text-sm font-semibold text-gray-300 mb-3">Components</h3>
              <div className="grid grid-cols-2 gap-2">
                {([
                  { key: 'timeline', label: 'Timeline' },
                  { key: 'mixer', label: 'Mixer' },
                  { key: 'effects', label: 'Effects' },
                  { key: 'instruments', label: 'Instruments' },
                  { key: 'ai-assistant', label: 'AI Assistant' },
                  { key: 'waveform', label: 'Waveform' },
                  { key: 'spectrogram', label: 'Spectrum' },
                  { key: 'collaboration', label: 'Collab' }
                ] as const).map(({ key, label }) => (
                  <button
                    key={key}
                    onClick={() => toggleComponent(key)}
                    className={studioUtils.getClassName(
                      'px-2 py-1 text-xs rounded transition-colors',
                      activeComponents.has(key) 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    )}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Instrument Selector */}
            {showInstruments && (
              <div className="flex-1 overflow-auto">
                <InstrumentSelector onSelectInstrument={(instrument: any) => {
                  info(`Selected instrument: ${instrument.name}`);
                }} />
              </div>
            )}

            {/* AI Assistant */}
            {showAI && (
              <div className="flex-1 overflow-auto">
                <AIAssistantInterface 
                  studioState={studioState}
                  onApplySuggestion={(suggestion) => {
                    success(`Applied AI suggestion: ${suggestion.title}`);
                  }}
                />
              </div>
            )}
          </aside>
        )}

        {/* Central Workspace */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {/* Timeline Editor */}
          {showTimeline && (
            <div className="h-80 border-b border-gray-700">
              <TimelineEditor
                tracks={studioState.tracks}
                currentTime={studioState.currentTime}
                zoomLevel={studioState.zoomLevel}
                isPlaying={studioState.isPlaying}
                selectedTracks={studioState.selectedTracks}
                onTimeChange={(time) => setStudioState(prev => ({ ...prev, currentTime: time }))}
                onTrackUpdate={updateTrack}
                onTrackSelect={(trackId) => {
                  setStudioState(prev => ({ 
                    ...prev, 
                    selectedTracks: [trackId] 
                  }));
                }}
                onAddTrack={addTrack}
                onRemoveTrack={removeTrack}
              />
            </div>
          )}

          {/* Waveform Visualizer */}
          {showWaveform && (
            <div className="h-32 border-b border-gray-700">
              <WaveformVisualizer
                audioUrl={studioState.tracks[0]?.audioUrl}
                currentTime={studioState.currentTime}
                isPlaying={studioState.isPlaying}
                onSeek={(time) => setStudioState(prev => ({ ...prev, currentTime: time }))}
              />
            </div>
          )}

          {/* Spectrogram Analyzer */}
          {showSpectrogram && (
            <div className="h-40 border-b border-gray-700">
              <SpectrogramAnalyzer
                audioUrl={studioState.tracks[0]?.audioUrl}
                isAnalyzing={studioState.isPlaying}
              />
            </div>
          )}

          {/* Effects Panel */}
          {showEffects && (
            <div className="flex-1 overflow-auto">
              <EffectsPanel
                selectedTracks={studioState.selectedTracks}
                tracks={studioState.tracks}
                onEffectChange={(trackId, effects) => {
                  updateTrack(trackId, { effects });
                }}
              />
            </div>
          )}
        </main>

        {/* Right Sidebar - Mixer */}
        {showMixer && (
          <aside className="w-96 bg-gray-900 border-l border-gray-700">
            <TrackMixer
              tracks={studioState.tracks}
              onTrackUpdate={updateTrack}
              masterVolume={1.0}
              onMasterVolumeChange={(volume) => {
                info(`Master volume: ${Math.round(volume * 100)}%`);
              }}
            />
          </aside>
        )}

        {/* Collaboration Panel */}
        {showCollaboration && (
          <CollaborativeWorkspace
            projectId={projectId || 'default'}
            currentUser={state.user}
            onUserAction={(action: string) => {
              info(`Collaboration: ${action}`);
            }}
          />
        )}
      </div>

      {/* Export Dialog */}
      {showExportDialog && (
        <ExportManager
          studioState={studioState}
          onExport={(exportData: any) => {
            if (onExport) {
              onExport(exportData);
            }
            setShowExportDialog(false);
            success('Export completed successfully');
          }}
          onClose={() => setShowExportDialog(false)}
        />
      )}
    </div>
  );
};

export default RemixStudioMain;