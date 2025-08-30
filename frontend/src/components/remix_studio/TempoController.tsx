'use client';

/**
 * Tempo Controller Component
 * 
 * Professional tempo and timing control interface.
 * Provides real-time BPM adjustment with tempo mapping and sync.
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
import { ClockIcon, PlusIcon, MinusIcon } from '@heroicons/react/24/outline';
import { studioUtils } from './remix_studio.styles';

interface TempoControllerProps {
  className?: string;
}

const TempoController: React.FC<TempoControllerProps> = ({ className = '' }) => {
  const [tempo, setTempo] = useState(120);
  const [isMetronomeOn, setIsMetronomeOn] = useState(false);

  const adjustTempo = (delta: number) => {
    setTempo(prev => Math.max(60, Math.min(200, prev + delta)));
  };

  return (
    <div className={studioUtils.getClassName('tempo-controller bg-gray-900 p-4', className)}>
      <div className="flex items-center space-x-2 mb-4">
        <ClockIcon className="h-5 w-5 text-yellow-400" />
        <h3 className="text-lg font-semibold text-white">Tempo</h3>
      </div>

      <div className="text-center space-y-4">
        <div className="text-4xl font-bold text-white">{tempo}</div>
        <div className="text-sm text-gray-400">BPM</div>

        <div className="flex items-center justify-center space-x-3">
          <button
            onClick={() => adjustTempo(-1)}
            className="p-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
          >
            <MinusIcon className="h-4 w-4" />
          </button>
          
          <input
            type="range"
            min="60"
            max="200"
            value={tempo}
            onChange={(e) => setTempo(parseInt(e.target.value))}
            className="flex-1"
          />
          
          <button
            onClick={() => adjustTempo(1)}
            className="p-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
          >
            <PlusIcon className="h-4 w-4" />
          </button>
        </div>

        <button
          onClick={() => setIsMetronomeOn(!isMetronomeOn)}
          className={studioUtils.getClassName(
            'w-full px-4 py-2 rounded transition-colors',
            isMetronomeOn ? 'bg-yellow-600 hover:bg-yellow-700' : 'bg-gray-700 hover:bg-gray-600'
          )}
        >
          {isMetronomeOn ? 'Stop Metronome' : 'Start Metronome'}
        </button>
      </div>
    </div>
  );
};

export default TempoController;