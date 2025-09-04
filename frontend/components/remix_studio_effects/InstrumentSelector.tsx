'use client';

/**
 * Instrument Selector Component
 * 
 * Virtual instrument browser and selection interface.
 * Provides access to synthesizers, samplers, and virtual instruments.
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
  MusicalNoteIcon,
  MagnifyingGlassIcon,
  PlayIcon,
  PlusIcon
} from '@heroicons/react/24/outline';
import { studioColors, studioUtils } from '../remix_studio/remix_studio.styles';

interface Instrument {
  id: string;
  name: string;
  category: 'synth' | 'piano' | 'guitar' | 'bass' | 'drum' | 'strings' | 'brass' | 'woodwind' | 'ethnic';
  type: 'vst' | 'sampler' | 'synthesizer';
  previewUrl?: string;
  presets: string[];
  tags: string[];
}

interface InstrumentSelectorProps {
  onSelectInstrument: (instrument: Instrument) => void;
  className?: string;
}

const MOCK_INSTRUMENTS: Instrument[] = [
  {
    id: 'analog-synth-1',
    name: 'Analog Synthesizer',
    category: 'synth',
    type: 'synthesizer',
    presets: ['Lead', 'Bass', 'Pad', 'Arp'],
    tags: ['electronic', 'vintage', 'warm']
  },
  {
    id: 'grand-piano-1',
    name: 'Grand Piano',
    category: 'piano',
    type: 'sampler',
    presets: ['Bright', 'Warm', 'Intimate', 'Pop'],
    tags: ['acoustic', 'classical', 'pop']
  },
  {
    id: 'electric-guitar-1',
    name: 'Electric Guitar',
    category: 'guitar',
    type: 'sampler',
    presets: ['Clean', 'Crunch', 'Lead', 'Rhythm'],
    tags: ['rock', 'blues', 'jazz']
  },
  {
    id: 'analog-bass-1',
    name: 'Analog Bass',
    category: 'bass',
    type: 'synthesizer',
    presets: ['Sub', 'Growl', 'Slap', 'Smooth'],
    tags: ['electronic', 'funk', 'house']
  },
  {
    id: 'acoustic-drums-1',
    name: 'Acoustic Drum Kit',
    category: 'drum',
    type: 'sampler',
    presets: ['Rock', 'Jazz', 'Pop', 'Vintage'],
    tags: ['acoustic', 'live', 'natural']
  }
];

const InstrumentSelector: React.FC<InstrumentSelectorProps> = ({
  onSelectInstrument,
  className = ''
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<Instrument['category'] | 'all'>('all');
  const [selectedInstrument, setSelectedInstrument] = useState<Instrument | null>(null);

  const categories = [
    { key: 'all' as const, label: 'All', icon: '🎵' },
    { key: 'synth' as const, label: 'Synths', icon: '🎹' },
    { key: 'piano' as const, label: 'Piano', icon: '🎹' },
    { key: 'guitar' as const, label: 'Guitar', icon: '🎸' },
    { key: 'bass' as const, label: 'Bass', icon: '🎸' },
    { key: 'drum' as const, label: 'Drums', icon: '🥁' },
    { key: 'strings' as const, label: 'Strings', icon: '🎻' },
    { key: 'brass' as const, label: 'Brass', icon: '🎺' },
    { key: 'woodwind' as const, label: 'Woodwind', icon: '🎷' },
    { key: 'ethnic' as const, label: 'Ethnic', icon: '🪘' }
  ];

  const filteredInstruments = MOCK_INSTRUMENTS.filter(instrument => {
    const matchesSearch = instrument.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         instrument.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCategory = selectedCategory === 'all' || instrument.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleSelectInstrument = useCallback((instrument: Instrument) => {
    setSelectedInstrument(instrument);
    onSelectInstrument(instrument);
  }, [onSelectInstrument]);

  return (
    <div className={studioUtils.getClassName('instrument-selector bg-gray-900 p-4', className)}>
      {/* Header */}
      <div className="flex items-center space-x-2 mb-4">
        <MusicalNoteIcon className="h-5 w-5 text-blue-400" />
        <h3 className="text-lg font-semibold text-white">Instruments</h3>
      </div>

      {/* Search */}
      <div className="relative mb-4">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search instruments..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
        />
      </div>

      {/* Categories */}
      <div className="grid grid-cols-2 gap-1 mb-4">
        {categories.map(({ key, label, icon }) => (
          <button
            key={key}
            onClick={() => setSelectedCategory(key)}
            className={studioUtils.getClassName(
              'flex items-center space-x-1 px-2 py-1 rounded text-xs transition-colors',
              selectedCategory === key
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            )}
          >
            <span>{icon}</span>
            <span>{label}</span>
          </button>
        ))}
      </div>

      {/* Instruments List */}
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {filteredInstruments.map(instrument => (
          <div
            key={instrument.id}
            className={studioUtils.getClassName(
              'p-3 bg-gray-800 border rounded cursor-pointer transition-all',
              selectedInstrument?.id === instrument.id
                ? 'border-blue-500 bg-gray-700'
                : 'border-gray-700 hover:border-gray-600 hover:bg-gray-750'
            )}
            onClick={() => handleSelectInstrument(instrument)}
          >
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-white">{instrument.name}</h4>
                <div className="flex items-center space-x-2 text-xs text-gray-400">
                  <span className="capitalize">{instrument.category}</span>
                  <span>•</span>
                  <span className="capitalize">{instrument.type}</span>
                </div>
              </div>
              
              <div className="flex items-center space-x-1">
                {instrument.previewUrl && (
                  <button className="p-1 text-gray-400 hover:text-blue-400 transition-colors">
                    <PlayIcon className="h-4 w-4" />
                  </button>
                )}
                <button className="p-1 text-gray-400 hover:text-green-400 transition-colors">
                  <PlusIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
            
            {/* Presets */}
            <div className="mt-2 flex flex-wrap gap-1">
              {instrument.presets.slice(0, 3).map(preset => (
                <span
                  key={preset}
                  className="px-2 py-0.5 bg-gray-700 text-xs text-gray-300 rounded"
                >
                  {preset}
                </span>
              ))}
              {instrument.presets.length > 3 && (
                <span className="px-2 py-0.5 bg-gray-700 text-xs text-gray-400 rounded">
                  +{instrument.presets.length - 3}
                </span>
              )}
            </div>
          </div>
        ))}
        
        {filteredInstruments.length === 0 && (
          <div className="text-center py-8">
            <MusicalNoteIcon className="h-12 w-12 text-gray-600 mx-auto mb-2" />
            <div className="text-gray-400">No instruments found</div>
            <div className="text-sm text-gray-500">Try adjusting your search or category filter</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InstrumentSelector;