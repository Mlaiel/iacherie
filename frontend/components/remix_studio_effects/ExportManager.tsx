'use client';

/**
 * Export Manager Component
 * 
 * Professional export interface with format selection and quality settings.
 * Handles multi-format audio export with optimization for various platforms.
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
  DocumentArrowDownIcon,
  XMarkIcon,
  CheckIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { studioUtils } from '../remix_studio/remix_studio.styles';
import type { StudioState, ExportSettings } from '../remix_studio/index';

interface ExportManagerProps {
  studioState: StudioState;
  onExport: (exportData: any) => void;
  onClose: () => void;
  className?: string;
}

const ExportManager: React.FC<ExportManagerProps> = ({
  studioState,
  onExport,
  onClose,
  className = ''
}) => {
  const [settings, setSettings] = useState<ExportSettings>({
    format: 'wav',
    quality: 'high',
    sampleRate: 44100,
    bitDepth: 24,
    channels: 'stereo',
    normalize: true,
    fadeIn: 0,
    fadeOut: 0,
    trimSilence: true
  });

  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);

  const handleExport = useCallback(async () => {
    setIsExporting(true);
    setExportProgress(0);

    // Simulate export progress
    const interval = setInterval(() => {
      setExportProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsExporting(false);
          onExport({
            settings,
            studioState,
            timestamp: new Date().toISOString()
          });
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  }, [settings, studioState, onExport]);

  const formatOptions = [
    { value: 'wav', label: 'WAV (Uncompressed)', description: 'Best quality, large file size' },
    { value: 'mp3', label: 'MP3 (Compressed)', description: 'Good quality, smaller size' },
    { value: 'flac', label: 'FLAC (Lossless)', description: 'Lossless compression' },
    { value: 'aac', label: 'AAC (Compressed)', description: 'Apple format, good quality' },
    { value: 'ogg', label: 'OGG (Open Source)', description: 'Open source format' }
  ];

  const qualityOptions = [
    { value: 'low', label: 'Low (128 kbps)', bitrate: '128 kbps' },
    { value: 'medium', label: 'Medium (256 kbps)', bitrate: '256 kbps' },
    { value: 'high', label: 'High (320 kbps)', bitrate: '320 kbps' },
    { value: 'lossless', label: 'Lossless', bitrate: 'Variable' }
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className={studioUtils.getClassName('export-manager bg-gray-900 border border-gray-700 rounded-lg p-6 w-full max-w-2xl', className)}>
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <DocumentArrowDownIcon className="h-6 w-6 text-blue-400" />
            <h2 className="text-xl font-semibold text-white">Export Audio</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-300 transition-colors"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        {!isExporting ? (
          <div className="space-y-6">
            {/* Format Selection */}
            <div>
              <h3 className="text-lg font-medium text-white mb-3">Format</h3>
              <div className="space-y-2">
                {formatOptions.map(option => (
                  <label key={option.value} className="flex items-center space-x-3 p-3 bg-gray-800 rounded cursor-pointer hover:bg-gray-750 transition-colors">
                    <input
                      type="radio"
                      name="format"
                      value={option.value}
                      checked={settings.format === option.value}
                      onChange={(e) => setSettings(prev => ({ ...prev, format: e.target.value as any }))}
                      className="text-blue-600"
                    />
                    <div>
                      <div className="text-white font-medium">{option.label}</div>
                      <div className="text-sm text-gray-400">{option.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Quality Settings */}
            <div>
              <h3 className="text-lg font-medium text-white mb-3">Quality</h3>
              <div className="grid grid-cols-2 gap-3">
                {qualityOptions.map(option => (
                  <label key={option.value} className="flex items-center space-x-2 p-3 bg-gray-800 rounded cursor-pointer hover:bg-gray-750 transition-colors">
                    <input
                      type="radio"
                      name="quality"
                      value={option.value}
                      checked={settings.quality === option.value}
                      onChange={(e) => setSettings(prev => ({ ...prev, quality: e.target.value as any }))}
                      className="text-blue-600"
                    />
                    <div>
                      <div className="text-white text-sm">{option.label}</div>
                      <div className="text-xs text-gray-400">{option.bitrate}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Advanced Settings */}
            <div>
              <h3 className="text-lg font-medium text-white mb-3">Advanced Settings</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Sample Rate</label>
                  <select
                    value={settings.sampleRate}
                    onChange={(e) => setSettings(prev => ({ ...prev, sampleRate: parseInt(e.target.value) as any }))}
                    className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-white"
                  >
                    <option value={44100}>44.1 kHz</option>
                    <option value={48000}>48 kHz</option>
                    <option value={96000}>96 kHz</option>
                    <option value={192000}>192 kHz</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Bit Depth</label>
                  <select
                    value={settings.bitDepth}
                    onChange={(e) => setSettings(prev => ({ ...prev, bitDepth: parseInt(e.target.value) as any }))}
                    className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-white"
                  >
                    <option value={16}>16-bit</option>
                    <option value={24}>24-bit</option>
                    <option value={32}>32-bit</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Processing Options */}
            <div>
              <h3 className="text-lg font-medium text-white mb-3">Processing</h3>
              <div className="space-y-3">
                <label className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    checked={settings.normalize}
                    onChange={(e) => setSettings(prev => ({ ...prev, normalize: e.target.checked }))}
                    className="rounded"
                  />
                  <span className="text-white">Normalize audio levels</span>
                </label>
                
                <label className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    checked={settings.trimSilence}
                    onChange={(e) => setSettings(prev => ({ ...prev, trimSilence: e.target.checked }))}
                    className="rounded"
                  />
                  <span className="text-white">Trim silence</span>
                </label>
              </div>
            </div>

            {/* Export Button */}
            <div className="flex justify-end space-x-3 pt-4 border-t border-gray-700">
              <button
                onClick={onClose}
                className="px-4 py-2 text-gray-400 hover:text-gray-300 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleExport}
                className="flex items-center space-x-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded transition-colors"
              >
                <DocumentArrowDownIcon className="h-5 w-5" />
                <span>Export</span>
              </button>
            </div>
          </div>
        ) : (
          /* Export Progress */
          <div className="text-center py-8">
            <div className="mb-4">
              <ClockIcon className="h-12 w-12 text-blue-400 mx-auto mb-2 animate-spin" />
              <h3 className="text-lg font-medium text-white">Exporting Audio...</h3>
              <p className="text-gray-400">Processing your tracks with the selected settings</p>
            </div>
            
            <div className="w-full bg-gray-700 rounded-full h-3 mb-4">
              <div 
                className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${exportProgress}%` }}
              />
            </div>
            
            <div className="text-sm text-gray-300">
              {exportProgress}% complete
            </div>
            
            {exportProgress === 100 && (
              <div className="mt-4 flex items-center justify-center space-x-2 text-green-400">
                <CheckIcon className="h-5 w-5" />
                <span>Export completed successfully!</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ExportManager;