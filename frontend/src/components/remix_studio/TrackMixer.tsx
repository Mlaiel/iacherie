'use client';

/**
 * Track Mixer Component
 * 
 * Professional mixing console interface with channel strips, faders, and EQ.
 * Provides comprehensive audio mixing capabilities for multi-track projects.
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

import React, { useState, useRef, useCallback, useMemo } from 'react';
import { 
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
  MicrophoneIcon,
  AdjustmentsVerticalIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';
import { studioColors, studioComponents, studioUtils } from './remix_studio.styles';
import type { AudioTrack } from './index';

interface TrackMixerProps {
  tracks: AudioTrack[];
  onTrackUpdate: (trackId: string, updates: Partial<AudioTrack>) => void;
  masterVolume: number;
  onMasterVolumeChange: (volume: number) => void;
  className?: string;
}

interface EQBand {
  frequency: number;
  gain: number;
  q: number;
  type: 'highpass' | 'lowpass' | 'bell' | 'shelf';
}

interface ChannelEQ {
  high: EQBand;
  mid: EQBand;
  low: EQBand;
  enabled: boolean;
}

interface VUMeterProps {
  level: number;
  peak: number;
  width?: number;
  height?: number;
}

const VUMeter: React.FC<VUMeterProps> = ({ 
  level, 
  peak, 
  width = 20, 
  height = 200 
}) => {
  const segments = 40;
  const segmentHeight = height / segments;
  
  const getSegmentColor = (index: number) => {
    const normalizedIndex = index / segments;
    if (normalizedIndex > 0.9) return studioColors.audio.peak;
    if (normalizedIndex > 0.75) return studioColors.studio.warning;
    return studioColors.audio.rms;
  };

  return (
    <div 
      className="relative bg-gray-800 rounded"
      style={{ width, height }}
    >
      {Array.from({ length: segments }, (_, i) => {
        const segmentLevel = (segments - i) / segments;
        const isActive = segmentLevel <= level;
        const isPeak = Math.abs(segmentLevel - peak) < 0.02;
        
        return (
          <div
            key={i}
            className="absolute"
            style={{
              top: i * segmentHeight,
              left: 2,
              right: 2,
              height: segmentHeight - 1,
              backgroundColor: isActive || isPeak 
                ? getSegmentColor(segments - i)
                : 'transparent',
              opacity: isPeak ? 1 : isActive ? 0.8 : 0.2
            }}
          />
        );
      })}
    </div>
  );
};

interface KnobProps {
  value: number;
  min?: number;
  max?: number;
  step?: number;
  size?: number;
  label?: string;
  onChange: (value: number) => void;
}

const Knob: React.FC<KnobProps> = ({
  value,
  min = 0,
  max = 1,
  step = 0.01,
  size = 40,
  label,
  onChange
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const knobRef = useRef<HTMLDivElement>(null);
  
  const normalizedValue = (value - min) / (max - min);
  const rotation = (normalizedValue - 0.5) * 270; // -135° to +135°
  
  const handleMouseDown = useCallback((event: React.MouseEvent) => {
    setIsDragging(true);
    event.preventDefault();
  }, []);
  
  const handleMouseMove = useCallback((event: MouseEvent) => {
    if (!isDragging || !knobRef.current) return;
    
    const rect = knobRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    const deltaY = event.clientY - centerY;
    const sensitivity = 0.005;
    const delta = -deltaY * sensitivity * (max - min);
    
    const newValue = Math.max(min, Math.min(max, value + delta));
    onChange(newValue);
  }, [isDragging, value, min, max, onChange]);
  
  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);
  
  React.useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);
  
  return (
    <div className="flex flex-col items-center space-y-1">
      {label && (
        <label className="text-xs text-gray-400 text-center">{label}</label>
      )}
      <div
        ref={knobRef}
        className="relative cursor-pointer select-none"
        style={{ width: size, height: size }}
        onMouseDown={handleMouseDown}
      >
        <div
          className="w-full h-full rounded-full border-2 border-gray-600 relative"
          style={{
            background: `conic-gradient(from 45deg, ${studioColors.controls.knob} 0deg, ${studioColors.controls.knobActive} ${rotation + 135}deg, ${studioColors.controls.knob} ${rotation + 145}deg, ${studioColors.controls.knob} 360deg)`
          }}
        >
          <div
            className="absolute w-1 h-4 bg-white rounded"
            style={{
              top: 2,
              left: '50%',
              transformOrigin: '50% 16px',
              transform: `translateX(-50%) rotate(${rotation}deg)`
            }}
          />
        </div>
      </div>
      <div className="text-xs text-gray-500 text-center min-w-12">
        {value.toFixed(2)}
      </div>
    </div>
  );
};

interface FaderProps {
  value: number;
  min?: number;
  max?: number;
  height?: number;
  label?: string;
  onChange: (value: number) => void;
}

const Fader: React.FC<FaderProps> = ({
  value,
  min = 0,
  max = 1,
  height = 300,
  label,
  onChange
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const faderRef = useRef<HTMLDivElement>(null);
  
  const normalizedValue = (value - min) / (max - min);
  const faderPosition = (1 - normalizedValue) * (height - 20);
  
  const handleMouseDown = useCallback((event: React.MouseEvent) => {
    setIsDragging(true);
    event.preventDefault();
  }, []);
  
  const handleMouseMove = useCallback((event: MouseEvent) => {
    if (!isDragging || !faderRef.current) return;
    
    const rect = faderRef.current.getBoundingClientRect();
    const relativeY = event.clientY - rect.top;
    const normalizedPosition = Math.max(0, Math.min(1, (height - relativeY) / height));
    const newValue = min + normalizedPosition * (max - min);
    
    onChange(newValue);
  }, [isDragging, height, min, max, onChange]);
  
  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);
  
  React.useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);
  
  return (
    <div className="flex flex-col items-center space-y-2">
      {label && (
        <label className="text-xs text-gray-400 text-center">{label}</label>
      )}
      <div
        ref={faderRef}
        className="relative w-8 bg-gray-700 rounded cursor-pointer"
        style={{ height }}
        onMouseDown={handleMouseDown}
      >
        {/* Fader Track */}
        <div className="absolute inset-x-2 inset-y-0 bg-gray-600 rounded" />
        
        {/* Fader Handle */}
        <div
          className="absolute w-full h-5 bg-gray-300 border border-gray-400 rounded shadow-sm"
          style={{ top: faderPosition }}
        />
        
        {/* Scale Markers */}
        {[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9].map(position => (
          <div
            key={position}
            className="absolute w-1 h-0.5 bg-gray-500 right-0"
            style={{ top: (1 - position) * height - 1 }}
          />
        ))}
      </div>
      <div className="text-xs text-gray-500 text-center min-w-12">
        {value < 0.01 ? '−∞' : `${Math.round(studioUtils.linearToDb(value))}dB`}
      </div>
    </div>
  );
};

interface ChannelStripProps {
  track: AudioTrack;
  vuLevel: number;
  vuPeak: number;
  onUpdate: (updates: Partial<AudioTrack>) => void;
}

const ChannelStrip: React.FC<ChannelStripProps> = ({
  track,
  vuLevel,
  vuPeak,
  onUpdate
}) => {
  const [eq, setEQ] = useState<ChannelEQ>({
    high: { frequency: 8000, gain: 0, q: 0.7, type: 'shelf' },
    mid: { frequency: 1000, gain: 0, q: 0.7, type: 'bell' },
    low: { frequency: 120, gain: 0, q: 0.7, type: 'shelf' },
    enabled: true
  });
  
  const [showEQ, setShowEQ] = useState(false);
  
  const handleEQChange = useCallback((band: keyof Omit<ChannelEQ, 'enabled'>, param: keyof EQBand, value: number) => {
    setEQ(prev => ({
      ...prev,
      [band]: { ...prev[band], [param]: value }
    }));
  }, []);
  
  return (
    <div 
      className="bg-gray-800 border border-gray-700 rounded-lg p-3 flex flex-col space-y-3"
      style={{ width: studioComponents.mixer.channelWidth }}
    >
      {/* Channel Header */}
      <div className="text-center">
        <div className="text-xs font-medium text-white truncate" title={track.name}>
          {track.name}
        </div>
        <div 
          className="w-full h-1 rounded mt-1"
          style={{ backgroundColor: track.color }}
        />
      </div>
      
      {/* Input Controls */}
      <div className="flex justify-center">
        <button
          onClick={() => onUpdate({ armed: !track.armed })}
          className={studioUtils.getClassName(
            'p-1 rounded transition-colors',
            track.armed ? 'bg-red-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          )}
          title="Arm for Recording"
        >
          <MicrophoneIcon className="h-4 w-4" />
        </button>
      </div>
      
      {/* EQ Section */}
      <div className="space-y-2">
        <button
          onClick={() => setShowEQ(!showEQ)}
          className="w-full flex items-center justify-center space-x-1 p-1 bg-gray-700 hover:bg-gray-600 rounded text-xs transition-colors"
        >
          <AdjustmentsVerticalIcon className="h-3 w-3" />
          <span>EQ</span>
        </button>
        
        {showEQ && (
          <div className="space-y-2">
            <Knob
              value={eq.high.gain}
              min={-15}
              max={15}
              size={30}
              label="High"
              onChange={(value) => handleEQChange('high', 'gain', value)}
            />
            <Knob
              value={eq.mid.gain}
              min={-15}
              max={15}
              size={30}
              label="Mid"
              onChange={(value) => handleEQChange('mid', 'gain', value)}
            />
            <Knob
              value={eq.low.gain}
              min={-15}
              max={15}
              size={30}
              label="Low"
              onChange={(value) => handleEQChange('low', 'gain', value)}
            />
          </div>
        )}
      </div>
      
      {/* Pan Control */}
      <Knob
        value={track.pan}
        min={-1}
        max={1}
        size={35}
        label="Pan"
        onChange={(value) => onUpdate({ pan: value })}
      />
      
      {/* Mute/Solo */}
      <div className="flex space-x-1">
        <button
          onClick={() => onUpdate({ muted: !track.muted })}
          className={studioUtils.getClassName(
            'flex-1 py-1 px-2 text-xs rounded transition-colors',
            track.muted ? 'bg-red-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          )}
        >
          M
        </button>
        <button
          onClick={() => onUpdate({ solo: !track.solo })}
          className={studioUtils.getClassName(
            'flex-1 py-1 px-2 text-xs rounded transition-colors',
            track.solo ? 'bg-yellow-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          )}
        >
          S
        </button>
      </div>
      
      {/* VU Meter */}
      <div className="flex justify-center">
        <VUMeter 
          level={track.muted ? 0 : vuLevel * track.volume}
          peak={track.muted ? 0 : vuPeak * track.volume}
          width={parseInt(studioComponents.mixer.meterWidth)}
          height={parseInt(studioComponents.mixer.meterHeight)}
        />
      </div>
      
      {/* Volume Fader */}
      <div className="flex justify-center">
        <Fader
          value={track.volume}
          min={0}
          max={1.5}
          height={parseInt(studioComponents.mixer.faderHeight)}
          onChange={(value) => onUpdate({ volume: value })}
        />
      </div>
    </div>
  );
};

const TrackMixer: React.FC<TrackMixerProps> = ({
  tracks,
  onTrackUpdate,
  masterVolume,
  onMasterVolumeChange,
  className = ''
}) => {
  // Simulate VU meter levels (in real implementation, would come from audio analysis)
  const [vuLevels] = useState<Record<string, { level: number; peak: number }>>(
    tracks.reduce((acc, track) => ({
      ...acc,
      [track.id]: { 
        level: Math.random() * 0.8, 
        peak: Math.random() * 0.9 + 0.1 
      }
    }), {})
  );
  
  const [masterVULevel] = useState({ level: 0.6, peak: 0.8 });
  const [showMasterEQ, setShowMasterEQ] = useState(false);
  
  const handleTrackUpdate = useCallback((trackId: string) => {
    return (updates: Partial<AudioTrack>) => {
      onTrackUpdate(trackId, updates);
    };
  }, [onTrackUpdate]);
  
  return (
    <div className={studioUtils.getClassName('track-mixer bg-gray-900 p-4 overflow-auto', className)}>
      <div className="flex space-x-3">
        {/* Channel Strips */}
        {tracks.map(track => (
          <ChannelStrip
            key={track.id}
            track={track}
            vuLevel={vuLevels[track.id]?.level || 0}
            vuPeak={vuLevels[track.id]?.peak || 0}
            onUpdate={handleTrackUpdate(track.id)}
          />
        ))}
        
        {/* Master Section */}
        <div className="bg-gray-800 border-2 border-yellow-600 rounded-lg p-3 flex flex-col space-y-3 ml-4">
          {/* Master Header */}
          <div className="text-center">
            <div className="text-sm font-bold text-yellow-400">MASTER</div>
            <div className="w-full h-1 bg-yellow-600 rounded mt-1" />
          </div>
          
          {/* Master EQ */}
          <div className="space-y-2">
            <button
              onClick={() => setShowMasterEQ(!showMasterEQ)}
              className="w-full flex items-center justify-center space-x-1 p-1 bg-gray-700 hover:bg-gray-600 rounded text-xs transition-colors"
            >
              <Cog6ToothIcon className="h-3 w-3" />
              <span>Master EQ</span>
            </button>
            
            {showMasterEQ && (
              <div className="space-y-2">
                <Knob
                  value={0}
                  min={-15}
                  max={15}
                  size={30}
                  label="High"
                  onChange={() => {}}
                />
                <Knob
                  value={0}
                  min={-15}
                  max={15}
                  size={30}
                  label="Mid"
                  onChange={() => {}}
                />
                <Knob
                  value={0}
                  min={-15}
                  max={15}
                  size={30}
                  label="Low"
                  onChange={() => {}}
                />
              </div>
            )}
          </div>
          
          {/* Master VU Meter */}
          <div className="flex justify-center">
            <VUMeter 
              level={masterVULevel.level * masterVolume}
              peak={masterVULevel.peak * masterVolume}
              width={parseInt(studioComponents.mixer.meterWidth)}
              height={parseInt(studioComponents.mixer.meterHeight)}
            />
          </div>
          
          {/* Master Fader */}
          <div className="flex justify-center">
            <Fader
              value={masterVolume}
              min={0}
              max={2}
              height={parseInt(studioComponents.mixer.faderHeight)}
              label="Master"
              onChange={onMasterVolumeChange}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrackMixer;