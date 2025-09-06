'use client';

/**
 * Style Transfer Panel Component
 * 
 * AI-powered style transfer interface for applying musical styles.
 * Enables transformation of musical elements using machine learning.
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
import { SparklesIcon, PlayIcon } from '@heroicons/react/24/outline';
import { studioUtils } from '../remix_studio/remix_studio.styles';

interface StyleTransferPanelProps {
  className?: string;
}

const StyleTransferPanel: React.FC<StyleTransferPanelProps> = ({ className = '' }) => {
  const [selectedStyle, setSelectedStyle] = useState('');
  
  const styles = [
    { id: 'jazz', name: 'Jazz', description: 'Swing rhythms and complex harmonies' },
    { id: 'rock', name: 'Rock', description: 'Powerful drums and electric guitars' },
    { id: 'electronic', name: 'Electronic', description: 'Synthesized sounds and beats' }
  ];

  return (
    <div className={studioUtils.getClassName('style-transfer-panel bg-gray-900 p-4', className)}>
      <div className="flex items-center space-x-2 mb-4">
        <SparklesIcon className="h-5 w-5 text-purple-400" />
        <h3 className="text-lg font-semibold text-white">Style Transfer</h3>
      </div>

      <div className="space-y-3">
        {styles.map(style => (
          <div key={style.id} className="p-3 bg-gray-800 rounded cursor-pointer hover:bg-gray-700 transition-colors">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-white">{style.name}</h4>
                <p className="text-sm text-gray-400">{style.description}</p>
              </div>
              <button className="p-2 text-gray-400 hover:text-purple-400 transition-colors">
                <PlayIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      <button className="w-full mt-4 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded transition-colors">
        Apply Style Transfer
      </button>
    </div>
  );
};

export default StyleTransferPanel;