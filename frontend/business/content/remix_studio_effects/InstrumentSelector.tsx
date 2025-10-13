/**
 * @fileoverview Instrument Selector Component for Audio Studio
 * @author Fahed Mlaiel <mlaiel@live.de> - Audio Engineer Role
 * @copyright 2025 Fahed Mlaiel - All Rights Reserved
 */

'use client';

import React, { useState, useCallback } from 'react';

export interface VirtualInstrument {
  id: string;
  name: string;
  category: 'synth' | 'piano' | 'organ' | 'guitar' | 'bass' | 'drums' | 'strings' | 'brass' | 'woodwind';
  presets: string[];
  isLoaded: boolean;
}

export interface InstrumentSelectorProps {
  instruments: VirtualInstrument[];
  selectedInstrument?: VirtualInstrument;
  onInstrumentSelect: (instrument: VirtualInstrument) => void;
  onInstrumentLoad: (instrumentId: string) => void;
  onPresetChange: (instrumentId: string, preset: string) => void;
}

const InstrumentSelector: React.FC<InstrumentSelectorProps> = ({
  instruments,
  selectedInstrument,
  onInstrumentSelect,
  onInstrumentLoad,
  onPresetChange
}) => {
  const [selectedCategory, setSelectedCategory] = useState<VirtualInstrument['category']>('synth');
  const [searchTerm, setSearchTerm] = useState('');

  const categories: { category: VirtualInstrument['category']; label: string; icon: string }[] = [
    { category: 'synth', label: 'Synthesizers', icon: '🎹' },
    { category: 'piano', label: 'Piano', icon: '🎹' },
    { category: 'organ', label: 'Organ', icon: '🎹' },
    { category: 'guitar', label: 'Guitar', icon: '🎸' },
    { category: 'bass', label: 'Bass', icon: '🎸' },
    { category: 'drums', label: 'Drums', icon: '🥁' },
    { category: 'strings', label: 'Strings', icon: '🎻' },
    { category: 'brass', label: 'Brass', icon: '🎺' },
    { category: 'woodwind', label: 'Woodwind', icon: '🎷' }
  ];

  const filteredInstruments = instruments.filter(instrument => {
    const matchesCategory = instrument.category === selectedCategory;
    const matchesSearch = instrument.name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const handleInstrumentSelect = useCallback((instrument: VirtualInstrument) => {
    if (!instrument.isLoaded) {
      onInstrumentLoad(instrument.id);
    }
    onInstrumentSelect(instrument);
  }, [onInstrumentSelect, onInstrumentLoad]);

  return (
    <div className="instrument-selector bg-gray-900 p-4 h-full">
      <div className="selector-header mb-4">
        <h3 className="text-white text-lg font-bold mb-3">Virtual Instruments</h3>
        
        {/* Search */}
        <div className="search-bar mb-4">
          <input
            type="text"
            placeholder="Search instruments..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-gray-800 text-white p-2 rounded border border-gray-700 focus:border-blue-500"
          />
        </div>

        {/* Category Tabs */}
        <div className="category-tabs flex flex-wrap gap-2 mb-4">
          {categories.map(({ category, label, icon }) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`flex items-center space-x-2 px-3 py-2 rounded text-sm ${
                selectedCategory === category
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <span>{icon}</span>
              <span>{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Instrument Grid */}
      <div className="instruments-grid grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 mb-4">
        {filteredInstruments.length === 0 ? (
          <div className="no-instruments col-span-full text-center py-8">
            <p className="text-gray-500">No instruments found</p>
            <p className="text-gray-600 text-sm">Try adjusting your search or category</p>
          </div>
        ) : (
          filteredInstruments.map((instrument) => (
            <div
              key={instrument.id}
              onClick={() => handleInstrumentSelect(instrument)}
              className={`instrument-card bg-gray-800 rounded-lg p-3 cursor-pointer transition-all ${
                selectedInstrument?.id === instrument.id
                  ? 'border-2 border-blue-500 bg-gray-750'
                  : 'border border-gray-700 hover:border-gray-600'
              }`}
            >
              <div className="card-header flex items-center justify-between mb-2">
                <h4 className="text-white font-medium text-sm">{instrument.name}</h4>
                <div className="status-indicator">
                  {instrument.isLoaded ? (
                    <div className="w-2 h-2 bg-green-500 rounded-full" title="Loaded" />
                  ) : (
                    <div className="w-2 h-2 bg-gray-500 rounded-full" title="Not loaded" />
                  )}
                </div>
              </div>
              
              <div className="card-info">
                <p className="text-gray-400 text-xs mb-2">
                  {categories.find(c => c.category === instrument.category)?.label}
                </p>
                <p className="text-gray-500 text-xs">
                  {instrument.presets.length} presets
                </p>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Selected Instrument Details */}
      {selectedInstrument && (
        <div className="selected-instrument bg-gray-800 rounded-lg p-4">
          <h4 className="text-white font-bold mb-3">
            {selectedInstrument.name}
            {!selectedInstrument.isLoaded && (
              <span className="ml-2 text-yellow-400 text-sm">(Loading...)</span>
            )}
          </h4>
          
          {selectedInstrument.isLoaded && (
            <>
              {/* Preset Selection */}
              <div className="preset-selection mb-4">
                <label className="block text-gray-300 text-sm mb-2">Preset</label>
                <select
                  onChange={(e) => onPresetChange(selectedInstrument.id, e.target.value)}
                  className="w-full bg-gray-700 text-white p-2 rounded border border-gray-600"
                  defaultValue=""
                >
                  <option value="" disabled>Select a preset</option>
                  {selectedInstrument.presets.map((preset) => (
                    <option key={preset} value={preset}>
                      {preset}
                    </option>
                  ))}
                </select>
              </div>

              {/* Virtual Keyboard Preview */}
              <div className="virtual-keyboard">
                <label className="block text-gray-300 text-sm mb-2">Quick Test</label>
                <div className="keyboard-keys flex space-x-1">
                  {['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'].map((note) => (
                    <button
                      key={note}
                      className={`key px-2 py-1 text-xs rounded ${
                        note.includes('#') 
                          ? 'bg-gray-900 text-white' 
                          : 'bg-white text-black'
                      } hover:opacity-80`}
                      onClick={() => {
                        // Trigger note play
                        console.log(`Playing ${note}`);
                      }}
                    >
                      {note}
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default InstrumentSelector;