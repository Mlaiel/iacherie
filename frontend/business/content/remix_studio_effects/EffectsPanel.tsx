/**
 * @fileoverview Effects Panel Component for Audio Studio
 * @author Fahed Mlaiel <mlaiel@live.de> - Audio Engineer Role
 * @copyright 2025 Fahed Mlaiel - All Rights Reserved
 */

'use client';

import React, { useState, useCallback } from 'react';

export interface AudioEffect {
  id: string;
  name: string;
  type: 'reverb' | 'delay' | 'distortion' | 'eq' | 'compressor' | 'chorus' | 'filter';
  enabled: boolean;
  parameters: Record<string, number>;
  preset?: string;
}

export interface EffectsPanelProps {
  effects: AudioEffect[];
  onEffectUpdate: (effectId: string, updates: Partial<AudioEffect>) => void;
  onEffectAdd: (effectType: AudioEffect['type']) => void;
  onEffectRemove: (effectId: string) => void;
  onEffectReorder: (fromIndex: number, toIndex: number) => void;
}

const EffectsPanel: React.FC<EffectsPanelProps> = ({
  effects,
  onEffectUpdate,
  onEffectAdd,
  onEffectRemove,
  onEffectReorder
}) => {
  const [expandedEffects, setExpandedEffects] = useState<Set<string>>(new Set());

  const toggleEffectExpansion = useCallback((effectId: string) => {
    setExpandedEffects(prev => {
      const newSet = new Set(prev);
      if (newSet.has(effectId)) {
        newSet.delete(effectId);
      } else {
        newSet.add(effectId);
      }
      return newSet;
    });
  }, []);

  const updateEffectParameter = useCallback((effectId: string, paramName: string, value: number) => {
    const effect = effects.find(e => e.id === effectId);
    if (effect) {
      onEffectUpdate(effectId, {
        parameters: { ...effect.parameters, [paramName]: value }
      });
    }
  }, [effects, onEffectUpdate]);

  const effectTypes: { type: AudioEffect['type']; label: string }[] = [
    { type: 'reverb', label: 'Reverb' },
    { type: 'delay', label: 'Delay' },
    { type: 'distortion', label: 'Distortion' },
    { type: 'eq', label: 'EQ' },
    { type: 'compressor', label: 'Compressor' },
    { type: 'chorus', label: 'Chorus' },
    { type: 'filter', label: 'Filter' }
  ];

  const renderEffectParameters = (effect: AudioEffect) => {
    const commonParams: { [effectType: string]: { [paramName: string]: { min: number; max: number; step: number; unit?: string } } } = {
      reverb: {
        roomSize: { min: 0, max: 1, step: 0.01 },
        damping: { min: 0, max: 1, step: 0.01 },
        wetLevel: { min: 0, max: 1, step: 0.01 },
        dryLevel: { min: 0, max: 1, step: 0.01 }
      },
      delay: {
        delayTime: { min: 0, max: 2, step: 0.01, unit: 's' },
        feedback: { min: 0, max: 0.9, step: 0.01 },
        wetLevel: { min: 0, max: 1, step: 0.01 }
      },
      distortion: {
        drive: { min: 0, max: 10, step: 0.1 },
        tone: { min: 0, max: 1, step: 0.01 },
        level: { min: 0, max: 1, step: 0.01 }
      },
      eq: {
        lowGain: { min: -12, max: 12, step: 0.1, unit: 'dB' },
        midGain: { min: -12, max: 12, step: 0.1, unit: 'dB' },
        highGain: { min: -12, max: 12, step: 0.1, unit: 'dB' }
      },
      compressor: {
        threshold: { min: -60, max: 0, step: 1, unit: 'dB' },
        ratio: { min: 1, max: 20, step: 0.5 },
        attack: { min: 0, max: 100, step: 1, unit: 'ms' },
        release: { min: 10, max: 1000, step: 10, unit: 'ms' }
      }
    };

    const params = commonParams[effect.type] || {};

    return Object.entries(params).map(([paramName, config]) => {
      const value = effect.parameters[paramName] || 0;
      
      return (
        <div key={paramName} className="parameter-control mb-3">
          <div className="flex justify-between items-center mb-1">
            <label className="text-gray-300 text-sm capitalize">
              {paramName.replace(/([A-Z])/g, ' $1').trim()}
            </label>
            <span className="text-gray-400 text-xs">
              {value.toFixed(config.step < 1 ? 2 : 0)}{config.unit || ''}
            </span>
          </div>
          <input
            type="range"
            min={config.min}
            max={config.max}
            step={config.step}
            value={value}
            onChange={(e) => updateEffectParameter(effect.id, paramName, parseFloat(e.target.value))}
            className="w-full"
          />
        </div>
      );
    });
  };

  return (
    <div className="effects-panel bg-gray-900 p-4 h-full overflow-y-auto">
      <div className="panel-header mb-4">
        <h3 className="text-white text-lg font-bold mb-3">Audio Effects</h3>
        
        {/* Add Effect Dropdown */}
        <div className="add-effect mb-4">
          <select
            className="w-full bg-gray-800 text-white p-2 rounded border border-gray-700"
            onChange={(e) => {
              if (e.target.value) {
                onEffectAdd(e.target.value as AudioEffect['type']);
                e.target.value = '';
              }
            }}
            defaultValue=""
          >
            <option value="" disabled>Add Effect...</option>
            {effectTypes.map(({ type, label }) => (
              <option key={type} value={type}>{label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Effects Chain */}
      <div className="effects-chain space-y-3">
        {effects.length === 0 ? (
          <div className="no-effects text-center py-8">
            <p className="text-gray-500">No effects added yet</p>
            <p className="text-gray-600 text-sm">Add effects to enhance your audio</p>
          </div>
        ) : (
          effects.map((effect, index) => (
            <div key={effect.id} className="effect-item bg-gray-800 rounded-lg p-3">
              <div className="effect-header flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <button
                    className={`w-4 h-4 rounded ${
                      effect.enabled ? 'bg-green-500' : 'bg-gray-600'
                    }`}
                    onClick={() => onEffectUpdate(effect.id, { enabled: !effect.enabled })}
                  />
                  <h4 className="text-white font-medium">{effect.name}</h4>
                  <span className="text-gray-400 text-sm bg-gray-700 px-2 py-1 rounded">
                    {effect.type}
                  </span>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => toggleEffectExpansion(effect.id)}
                    className="text-gray-400 hover:text-white"
                  >
                    {expandedEffects.has(effect.id) ? '−' : '+'}
                  </button>
                  <button
                    onClick={() => onEffectRemove(effect.id)}
                    className="text-red-400 hover:text-red-300 text-sm"
                  >
                    ×
                  </button>
                </div>
              </div>

              {expandedEffects.has(effect.id) && (
                <div className="effect-parameters">
                  {renderEffectParameters(effect)}
                  
                  {/* Preset Selection */}
                  <div className="preset-selector mt-4 pt-3 border-t border-gray-700">
                    <label className="block text-gray-300 text-sm mb-2">Preset</label>
                    <select
                      value={effect.preset || ''}
                      onChange={(e) => onEffectUpdate(effect.id, { preset: e.target.value })}
                      className="w-full bg-gray-700 text-white p-2 rounded border border-gray-600"
                    >
                      <option value="">Custom</option>
                      <option value="subtle">Subtle</option>
                      <option value="moderate">Moderate</option>
                      <option value="intense">Intense</option>
                    </select>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default EffectsPanel;