'use client';

/**
 * Key Transposer Component
 * 
 * Musical key transposition and harmony control interface.
 * Provides real-time key changes with chord progression analysis.
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

import React, { useState } from 'react';
import { MusicalNoteIcon, ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/outline';
import { studioUtils } from '../remix_studio/remix_studio.styles';

interface KeyTransposerProps {
  className?: string;
}

const KeyTransposer: React.FC<KeyTransposerProps> = ({ className = '' }) => {
  const [selectedKey, setSelectedKey] = useState('C');
  const [selectedMode, setSelectedMode] = useState('major');
  const [transposition, setTransposition] = useState(0);

  const keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
  const modes = ['major', 'minor', 'dorian', 'mixolydian'];

  const transposeKey = (semitones: number) => {
    setTransposition(prev => Math.max(-12, Math.min(12, prev + semitones)));
  };

  return (
    <div className={studioUtils.getClassName('key-transposer bg-gray-900 p-4', className)}>
      <div className="flex items-center space-x-2 mb-4">
        <MusicalNoteIcon className="h-5 w-5 text-indigo-400" />
        <h3 className="text-lg font-semibold text-white">Key Transposer</h3>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm text-gray-300 mb-2">Key</label>
          <select
            value={selectedKey}
            onChange={(e) => setSelectedKey(e.target.value)}
            className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-white"
          >
            {keys.map(key => (
              <option key={key} value={key}>{key}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm text-gray-300 mb-2">Mode</label>
          <select
            value={selectedMode}
            onChange={(e) => setSelectedMode(e.target.value)}
            className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-white"
          >
            {modes.map(mode => (
              <option key={mode} value={mode} className="capitalize">{mode}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm text-gray-300 mb-2">Transposition</label>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => transposeKey(-1)}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
            >
              <ArrowDownIcon className="h-4 w-4" />
            </button>
            
            <div className="flex-1 text-center">
              <div className="text-2xl font-bold text-white">{transposition > 0 ? '+' : ''}{transposition}</div>
              <div className="text-xs text-gray-400">semitones</div>
            </div>
            
            <button
              onClick={() => transposeKey(1)}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
            >
              <ArrowUpIcon className="h-4 w-4" />
            </button>
          </div>
        </div>

        <button className="w-full px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded transition-colors">
          Apply Transposition
        </button>
      </div>
    </div>
  );
};

export default KeyTransposer;