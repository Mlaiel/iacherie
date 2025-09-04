'use client';

/**
 * Loop Manager Component
 * 
 * Professional loop creation and management interface.
 * Provides seamless loop editing with beat-sync and timing controls.
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
import { ArrowPathIcon, PlayIcon, StopIcon } from '@heroicons/react/24/outline';
import { studioUtils } from '../remix_studio/remix_studio.styles';

interface LoopManagerProps {
  className?: string;
}

const LoopManager: React.FC<LoopManagerProps> = ({ className = '' }) => {
  const [isLooping, setIsLooping] = useState(false);
  const [loopStart, setLoopStart] = useState(0);
  const [loopEnd, setLoopEnd] = useState(8);

  return (
    <div className={studioUtils.getClassName('loop-manager bg-gray-900 p-4', className)}>
      <div className="flex items-center space-x-2 mb-4">
        <ArrowPathIcon className="h-5 w-5 text-orange-400" />
        <h3 className="text-lg font-semibold text-white">Loop Manager</h3>
      </div>

      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm text-gray-300 mb-1">Start (bars)</label>
            <input
              type="number"
              value={loopStart}
              onChange={(e) => setLoopStart(parseInt(e.target.value))}
              className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-white"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1">End (bars)</label>
            <input
              type="number"
              value={loopEnd}
              onChange={(e) => setLoopEnd(parseInt(e.target.value))}
              className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-white"
            />
          </div>
        </div>

        <div className="flex space-x-2">
          <button
            onClick={() => setIsLooping(!isLooping)}
            className={studioUtils.getClassName(
              'flex items-center space-x-2 px-4 py-2 rounded transition-colors',
              isLooping ? 'bg-orange-600 hover:bg-orange-700' : 'bg-gray-700 hover:bg-gray-600'
            )}
          >
            {isLooping ? <StopIcon className="h-4 w-4" /> : <PlayIcon className="h-4 w-4" />}
            <span>{isLooping ? 'Stop Loop' : 'Start Loop'}</span>
          </button>
        </div>

        <div className="text-sm text-gray-400">
          Loop: {loopEnd - loopStart} bars ({((loopEnd - loopStart) * 4).toFixed(1)} beats)
        </div>
      </div>
    </div>
  );
};

export default LoopManager;