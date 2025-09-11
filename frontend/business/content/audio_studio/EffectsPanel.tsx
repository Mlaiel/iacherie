'use client';

/**
 * Effects Panel Component
 * 
 * Professional audio effects processing interface with real-time controls.
 * Provides comprehensive effect chains for creative audio manipulation.
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

import React, { useState, useCallback } from 'react';
import { 
  PlusIcon,
  TrashIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  PowerIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';
import { studioColors, studioUtils } from '../remix_studio/remix_studio.styles';
import type { AudioTrack, AudioEffect } from '../remix_studio/index';

interface EffectsPanelProps {
  selectedTracks: string[];
  tracks: AudioTrack[];
  onEffectChange: (trackId: string, effects: AudioEffect[]) => void;
  className?: string;
}

interface EffectPreset {
  name: string;
  type: AudioEffect['type'];
  parameters: Record<string, number>;
}

const EFFECT_PRESETS: EffectPreset[] = [
  // Reverb Presets
  { name: 'Hall Reverb', type: 'reverb', parameters: { size: 0.8, damping: 0.3, wet: 0.4, dry: 0.6 } },
  { name: 'Room Reverb', type: 'reverb', parameters: { size: 0.4, damping: 0.5, wet: 0.3, dry: 0.7 } },
  { name: 'Plate Reverb', type: 'reverb', parameters: { size: 0.6, damping: 0.2, wet: 0.35, dry: 0.65 } },
  
  // Delay Presets
  { name: 'Eighth Note Delay', type: 'delay', parameters: { time: 0.25, feedback: 0.3, wet: 0.2, dry: 0.8 } },
  { name: 'Dotted Eighth', type: 'delay', parameters: { time: 0.375, feedback: 0.4, wet: 0.25, dry: 0.75 } },
  { name: 'Slap Echo', type: 'delay', parameters: { time: 0.125, feedback: 0.2, wet: 0.15, dry: 0.85 } },
  
  // Compressor Presets
  { name: 'Vocal Compressor', type: 'compressor', parameters: { ratio: 3, attack: 3, release: 30, threshold: -18, makeup: 2 } },
  { name: 'Drum Compressor', type: 'compressor', parameters: { ratio: 4, attack: 1, release: 10, threshold: -12, makeup: 3 } },
  { name: 'Bus Compressor', type: 'compressor', parameters: { ratio: 2, attack: 10, release: 100, threshold: -6, makeup: 1 } },
  
  // EQ Presets
  { name: 'Vocal EQ', type: 'eq', parameters: { low: -2, lowMid: 1, highMid: 3, high: 2, presence: 4 } },
  { name: 'Bass EQ', type: 'eq', parameters: { low: 3, lowMid: -1, highMid: -2, high: 1, presence: 0 } },
  { name: 'Bright EQ', type: 'eq', parameters: { low: 0, lowMid: 0, highMid: 2, high: 4, presence: 3 } },
  
  // Distortion Presets
  { name: 'Warm Saturation', type: 'distortion', parameters: { drive: 0.3, tone: 0.6, mix: 0.2, output: 0.8 } },
  { name: 'Hard Distortion', type: 'distortion', parameters: { drive: 0.8, tone: 0.4, mix: 0.7, output: 0.6 } },
  { name: 'Tube Warmth', type: 'distortion', parameters: { drive: 0.2, tone: 0.7, mix: 0.15, output: 0.9 } },
];

interface KnobControlProps {
  label: string;
  value: number;
  min?: number;
  max?: number;
  step?: number;
  unit?: string;
  onChange: (value: number) => void;
}

const KnobControl: React.FC<KnobControlProps> = ({
  label,
  value,
  min = 0,
  max = 1,
  step = 0.01,
  unit = '',
  onChange
}) => {
  const [isDragging, setIsDragging] = useState(false);
  
  const handleMouseDown = useCallback((event: React.MouseEvent) => {
    setIsDragging(true);
    event.preventDefault();
  }, []);
  
  const handleMouseMove = useCallback((event: MouseEvent) => {
    if (!isDragging) return;
    
    const deltaY = -event.movementY;
    const sensitivity = 0.01;
    const delta = deltaY * sensitivity * (max - min);
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
  
  const normalizedValue = (value - min) / (max - min);
  const rotation = (normalizedValue - 0.5) * 270;
  
  return (
    <div className="flex flex-col items-center space-y-1">
      <label className="text-xs text-gray-400">{label}</label>
      <div
        className="w-10 h-10 rounded-full border-2 border-gray-600 relative cursor-pointer select-none"
        style={{
          background: `conic-gradient(from 45deg, #374151 0deg, #4f46e5 ${rotation + 135}deg, #374151 ${rotation + 145}deg, #374151 360deg)`
        }}
        onMouseDown={handleMouseDown}
      >
        <div
          className="absolute w-0.5 h-3 bg-white rounded"
          style={{
            top: 2,
            left: '50%',
            transformOrigin: '50% 16px',
            transform: `translateX(-50%) rotate(${rotation}deg)`
          }}
        />
      </div>
      <div className="text-xs text-gray-500 text-center">
        {value.toFixed(2)}{unit}
      </div>
    </div>
  );
};

interface EffectControlProps {
  effect: AudioEffect;
  onUpdate: (updates: Partial<AudioEffect>) => void;
  onRemove: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
  canMoveUp: boolean;
  canMoveDown: boolean;
}

const EffectControl: React.FC<EffectControlProps> = ({
  effect,
  onUpdate,
  onRemove,
  onMoveUp,
  onMoveDown,
  canMoveUp,
  canMoveDown
}) => {
  const renderEffectControls = () => {
    switch (effect.type) {
      case 'reverb':
        return (
          <div className="grid grid-cols-2 gap-3">
            <KnobControl
              label="Size"
              value={effect.parameters.size || 0.5}
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, size: value } })}
            />
            <KnobControl
              label="Damping"
              value={effect.parameters.damping || 0.5}
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, damping: value } })}
            />
            <KnobControl
              label="Wet"
              value={effect.parameters.wet || 0.3}
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, wet: value } })}
            />
            <KnobControl
              label="Dry"
              value={effect.parameters.dry || 0.7}
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, dry: value } })}
            />
          </div>
        );
        
      case 'delay':
        return (
          <div className="grid grid-cols-2 gap-3">
            <KnobControl
              label="Time"
              value={effect.parameters.time || 0.25}
              max={2}
              unit="s"
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, time: value } })}
            />
            <KnobControl
              label="Feedback"
              value={effect.parameters.feedback || 0.3}
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, feedback: value } })}
            />
            <KnobControl
              label="Wet"
              value={effect.parameters.wet || 0.2}
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, wet: value } })}
            />
            <KnobControl
              label="Dry"
              value={effect.parameters.dry || 0.8}
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, dry: value } })}
            />
          </div>
        );
        
      case 'compressor':
        return (
          <div className="grid grid-cols-3 gap-2">
            <KnobControl
              label="Ratio"
              value={effect.parameters.ratio || 2}
              min={1}
              max={20}
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, ratio: value } })}
            />
            <KnobControl
              label="Attack"
              value={effect.parameters.attack || 5}
              min={0.1}
              max={100}
              unit="ms"
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, attack: value } })}
            />
            <KnobControl
              label="Release"
              value={effect.parameters.release || 50}
              min={1}
              max={1000}
              unit="ms"
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, release: value } })}
            />
            <KnobControl
              label="Threshold"
              value={effect.parameters.threshold || -12}
              min={-60}
              max={0}
              unit="dB"
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, threshold: value } })}
            />
            <KnobControl
              label="Makeup"
              value={effect.parameters.makeup || 0}
              min={-10}
              max={10}
              unit="dB"
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, makeup: value } })}
            />
          </div>
        );
        
      case 'eq':
        return (
          <div className="grid grid-cols-3 gap-2">
            <KnobControl
              label="Low"
              value={effect.parameters.low || 0}
              min={-15}
              max={15}
              unit="dB"
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, low: value } })}
            />
            <KnobControl
              label="Mid"
              value={effect.parameters.mid || 0}
              min={-15}
              max={15}
              unit="dB"
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, mid: value } })}
            />
            <KnobControl
              label="High"
              value={effect.parameters.high || 0}
              min={-15}
              max={15}
              unit="dB"
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, high: value } })}
            />
          </div>
        );
        
      case 'distortion':
        return (
          <div className="grid grid-cols-2 gap-3">
            <KnobControl
              label="Drive"
              value={effect.parameters.drive || 0.5}
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, drive: value } })}
            />
            <KnobControl
              label="Tone"
              value={effect.parameters.tone || 0.5}
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, tone: value } })}
            />
            <KnobControl
              label="Mix"
              value={effect.parameters.mix || 0.5}
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, mix: value } })}
            />
            <KnobControl
              label="Output"
              value={effect.parameters.output || 0.8}
              onChange={(value) => onUpdate({ parameters: { ...effect.parameters, output: value } })}
            />
          </div>
        );
        
      default:
        return (
          <div className="text-center text-gray-400 py-4">
            Controls not available for {effect.type}
          </div>
        );
    }
  };
  
  const getEffectColor = (type: AudioEffect['type']) => {
    const colors = {
      reverb: studioColors.track.audio,
      delay: studioColors.track.midi,
      compressor: studioColors.track.instrument,
      eq: studioColors.studio.primary,
      distortion: studioColors.studio.secondary,
      chorus: studioColors.studio.success,
      filter: studioColors.studio.warning
    };
    return colors[type] || studioColors.studio.accent;
  };
  
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-3">
      {/* Effect Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div 
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: getEffectColor(effect.type) }}
          />
          <h4 className="font-medium text-white capitalize">{effect.type}</h4>
          {effect.presetName && (
            <span className="text-xs text-gray-400">({effect.presetName})</span>
          )}
        </div>
        
        <div className="flex items-center space-x-1">
          <button
            onClick={() => onUpdate({ enabled: !effect.enabled })}
            className={studioUtils.getClassName(
              'p-1 rounded transition-colors',
              effect.enabled ? 'text-green-400 hover:text-green-300' : 'text-gray-500 hover:text-gray-400'
            )}
            title={effect.enabled ? 'Disable' : 'Enable'}
          >
            <PowerIcon className="h-4 w-4" />
          </button>
          
          <button
            onClick={onMoveUp}
            disabled={!canMoveUp}
            className="p-1 text-gray-400 hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Move up"
          >
            <ArrowUpIcon className="h-4 w-4" />
          </button>
          
          <button
            onClick={onMoveDown}
            disabled={!canMoveDown}
            className="p-1 text-gray-400 hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Move down"
          >
            <ArrowDownIcon className="h-4 w-4" />
          </button>
          
          <button
            onClick={onRemove}
            className="p-1 text-red-400 hover:text-red-300 transition-colors"
            title="Remove effect"
          >
            <TrashIcon className="h-4 w-4" />
          </button>
        </div>
      </div>
      
      {/* Effect Controls */}
      <div className={effect.enabled ? 'opacity-100' : 'opacity-50'}>
        {renderEffectControls()}
      </div>
    </div>
  );
};

const EffectsPanel: React.FC<EffectsPanelProps> = ({
  selectedTracks,
  tracks,
  onEffectChange,
  className = ''
}) => {
  const [showPresets, setShowPresets] = useState(false);
  
  const selectedTrack = selectedTracks.length === 1 
    ? tracks.find(t => t.id === selectedTracks[0])
    : null;
  
  const addEffect = useCallback((preset: EffectPreset) => {
    if (!selectedTrack) return;
    
    const newEffect: AudioEffect = {
      id: `effect-${Date.now()}`,
      type: preset.type,
      name: preset.name,
      enabled: true,
      parameters: { ...preset.parameters },
      presetName: preset.name
    };
    
    const updatedEffects = [...selectedTrack.effects, newEffect];
    onEffectChange(selectedTrack.id, updatedEffects);
    setShowPresets(false);
  }, [selectedTrack, onEffectChange]);
  
  const updateEffect = useCallback((effectIndex: number, updates: Partial<AudioEffect>) => {
    if (!selectedTrack) return;
    
    const updatedEffects = selectedTrack.effects.map((effect, index) =>
      index === effectIndex ? { ...effect, ...updates } : effect
    );
    
    onEffectChange(selectedTrack.id, updatedEffects);
  }, [selectedTrack, onEffectChange]);
  
  const removeEffect = useCallback((effectIndex: number) => {
    if (!selectedTrack) return;
    
    const updatedEffects = selectedTrack.effects.filter((_, index) => index !== effectIndex);
    onEffectChange(selectedTrack.id, updatedEffects);
  }, [selectedTrack, onEffectChange]);
  
  const moveEffect = useCallback((fromIndex: number, toIndex: number) => {
    if (!selectedTrack) return;
    
    const updatedEffects = [...selectedTrack.effects];
    const [movedEffect] = updatedEffects.splice(fromIndex, 1);
    updatedEffects.splice(toIndex, 0, movedEffect);
    
    onEffectChange(selectedTrack.id, updatedEffects);
  }, [selectedTrack, onEffectChange]);
  
  if (selectedTracks.length === 0) {
    return (
      <div className={studioUtils.getClassName('effects-panel bg-gray-900 p-4', className)}>
        <div className="text-center py-8">
          <Cog6ToothIcon className="h-12 w-12 text-gray-600 mx-auto mb-2" />
          <div className="text-gray-400 mb-2">No track selected</div>
          <div className="text-sm text-gray-500">
            Select a track to access effect controls
          </div>
        </div>
      </div>
    );
  }
  
  if (selectedTracks.length > 1) {
    return (
      <div className={studioUtils.getClassName('effects-panel bg-gray-900 p-4', className)}>
        <div className="text-center py-8">
          <Cog6ToothIcon className="h-12 w-12 text-gray-600 mx-auto mb-2" />
          <div className="text-gray-400 mb-2">Multiple tracks selected</div>
          <div className="text-sm text-gray-500">
            Select a single track to edit effects
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className={studioUtils.getClassName('effects-panel bg-gray-900 p-4 overflow-auto', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Cog6ToothIcon className="h-5 w-5 text-blue-400" />
          <h3 className="text-lg font-semibold text-white">Effects</h3>
          {selectedTrack && (
            <span className="text-sm text-gray-400">({selectedTrack.name})</span>
          )}
        </div>
        
        <button
          onClick={() => setShowPresets(!showPresets)}
          className="flex items-center space-x-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded transition-colors"
        >
          <PlusIcon className="h-4 w-4" />
          <span>Add Effect</span>
        </button>
      </div>
      
      {/* Presets Panel */}
      {showPresets && (
        <div className="mb-4 p-3 bg-gray-800 rounded-lg">
          <h4 className="text-sm font-semibold text-gray-300 mb-2">Effect Presets</h4>
          <div className="grid grid-cols-1 gap-1 max-h-40 overflow-y-auto">
            {EFFECT_PRESETS.map((preset, index) => (
              <button
                key={index}
                onClick={() => addEffect(preset)}
                className="text-left p-2 hover:bg-gray-700 rounded text-sm transition-colors"
              >
                <div className="text-white">{preset.name}</div>
                <div className="text-xs text-gray-400 capitalize">{preset.type}</div>
              </button>
            ))}
          </div>
        </div>
      )}
      
      {/* Effects Chain */}
      <div className="space-y-3">
        {selectedTrack?.effects.map((effect, index) => (
          <EffectControl
            key={effect.id}
            effect={effect}
            onUpdate={(updates) => updateEffect(index, updates)}
            onRemove={() => removeEffect(index)}
            onMoveUp={() => moveEffect(index, index - 1)}
            onMoveDown={() => moveEffect(index, index + 1)}
            canMoveUp={index > 0}
            canMoveDown={index < selectedTrack.effects.length - 1}
          />
        ))}
        
        {selectedTrack?.effects.length === 0 && (
          <div className="text-center py-8">
            <div className="text-gray-400 mb-2">No effects applied</div>
            <div className="text-sm text-gray-500">
              Click "Add Effect" to start building your effect chain
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EffectsPanel;