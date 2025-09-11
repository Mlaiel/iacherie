/**
 * @fileoverview Export Manager Component for Effects Studio
 * @author Fahed Mlaiel <mlaiel@live.de> - Audio Engineer Role
 * @copyright 2025 Fahed Mlaiel - All Rights Reserved
 */

'use client';

import React, { useState, useCallback } from 'react';

export interface ExportManagerProps {
  onExport: (settings: any) => void;
  onCancel: () => void;
  isExporting?: boolean;
  progress?: number;
}

const ExportManager: React.FC<ExportManagerProps> = ({
  onExport,
  onCancel,
  isExporting = false,
  progress = 0
}) => {
  const [exportSettings, setExportSettings] = useState({
    format: 'wav',
    quality: 'high',
    sampleRate: 44100,
    bitDepth: 24,
    channels: 'stereo',
    normalize: true,
    trimSilence: true
  });

  const handleExport = useCallback(() => {
    onExport(exportSettings);
  }, [exportSettings, onExport]);

  return (
    <div className="export-manager bg-gray-900 p-4 rounded-lg">
      <h3 className="text-white text-lg font-bold mb-4">Export Audio</h3>
      
      <div className="export-settings space-y-4">
        {/* Format Selection */}
        <div>
          <label className="block text-gray-300 text-sm mb-2">Format</label>
          <select
            value={exportSettings.format}
            onChange={(e) => setExportSettings(prev => ({ ...prev, format: e.target.value }))}
            className="w-full bg-gray-800 text-white p-2 rounded border border-gray-700"
          >
            <option value="wav">WAV</option>
            <option value="mp3">MP3</option>
            <option value="flac">FLAC</option>
            <option value="aac">AAC</option>
          </select>
        </div>

        {/* Quality */}
        <div>
          <label className="block text-gray-300 text-sm mb-2">Quality</label>
          <select
            value={exportSettings.quality}
            onChange={(e) => setExportSettings(prev => ({ ...prev, quality: e.target.value }))}
            className="w-full bg-gray-800 text-white p-2 rounded border border-gray-700"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="studio">Studio</option>
          </select>
        </div>

        {/* Options */}
        <div className="space-y-2">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="normalize"
              checked={exportSettings.normalize}
              onChange={(e) => setExportSettings(prev => ({ ...prev, normalize: e.target.checked }))}
              className="mr-2"
            />
            <label htmlFor="normalize" className="text-gray-300 text-sm">Normalize audio</label>
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              id="trimSilence"
              checked={exportSettings.trimSilence}
              onChange={(e) => setExportSettings(prev => ({ ...prev, trimSilence: e.target.checked }))}
              className="mr-2"
            />
            <label htmlFor="trimSilence" className="text-gray-300 text-sm">Trim silence</label>
          </div>
        </div>
      </div>

      {/* Progress */}
      {isExporting && (
        <div className="export-progress mt-4">
          <div className="flex justify-between text-sm text-gray-400 mb-1">
            <span>Exporting...</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Buttons */}
      <div className="export-buttons flex space-x-3 mt-6">
        <button
          onClick={onCancel}
          disabled={isExporting}
          className="flex-1 bg-gray-600 hover:bg-gray-700 disabled:opacity-50 text-white py-2 px-4 rounded"
        >
          Cancel
        </button>
        <button
          onClick={handleExport}
          disabled={isExporting}
          className="flex-1 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white py-2 px-4 rounded"
        >
          {isExporting ? 'Exporting...' : 'Export'}
        </button>
      </div>
    </div>
  );
};

export default ExportManager;