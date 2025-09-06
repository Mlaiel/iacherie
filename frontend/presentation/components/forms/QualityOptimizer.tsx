/**
 * Quality Optimizer - Media quality optimization component
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  AdjustmentsHorizontalIcon,
  ChartBarIcon,
  PlayIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  PhotoIcon
} from '@heroicons/react/24/outline';

interface OptimizationSettings {
  quality: number;
  resolution: string;
  bitrate: number;
  compression: number;
}

interface OptimizationResult {
  id: string;
  filename: string;
  originalSize: string;
  optimizedSize: string;
  compressionRatio: number;
  qualityScore: number;
  status: 'processing' | 'completed' | 'failed';
}

const QualityOptimizer: React.FC = () => {
  const [settings, setSettings] = React.useState<OptimizationSettings>({
    quality: 85,
    resolution: '1080p',
    bitrate: 5000,
    compression: 70
  });

  const [results, setResults] = React.useState<OptimizationResult[]>([
    {
      id: '1',
      filename: 'video_sample.mp4',
      originalSize: '245 MB',
      optimizedSize: '89 MB',
      compressionRatio: 64,
      qualityScore: 92,
      status: 'completed'
    },
    {
      id: '2',
      filename: 'image_collection.jpg',
      originalSize: '12 MB',
      optimizedSize: '3.2 MB',
      compressionRatio: 73,
      qualityScore: 88,
      status: 'completed'
    }
  ]);

  const [optimizing, setOptimizing] = React.useState(false);

  const resolutionOptions = ['480p', '720p', '1080p', '1440p', '4K'];

  const handleOptimize = () => {
    setOptimizing(true);
    // Simulate optimization process
    setTimeout(() => {
      const newResult: OptimizationResult = {
        id: Date.now().toString(),
        filename: 'new_video.mp4',
        originalSize: '180 MB',
        optimizedSize: '65 MB',
        compressionRatio: 64,
        qualityScore: 90,
        status: 'completed'
      };
      setResults(prev => [newResult, ...prev]);
      setOptimizing(false);
    }, 3000);
  };

  const getQualityColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSavingsColor = (ratio: number) => {
    if (ratio >= 60) return 'text-green-600';
    if (ratio >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Quality Optimizer</h2>
          <p className="text-gray-600">Optimize media quality while reducing file sizes</p>
        </div>
      </div>

      {/* Optimization Settings */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <AdjustmentsHorizontalIcon className="h-5 w-5 mr-2" />
          Optimization Settings
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Quality Slider */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quality: {settings.quality}%
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={settings.quality}
              onChange={(e) => setSettings(prev => ({ ...prev, quality: parseInt(e.target.value) }))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Resolution */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Resolution
            </label>
            <select
              value={settings.resolution}
              onChange={(e) => setSettings(prev => ({ ...prev, resolution: e.target.value }))}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {resolutionOptions.map(res => (
                <option key={res} value={res}>{res}</option>
              ))}
            </select>
          </div>

          {/* Bitrate */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Bitrate: {settings.bitrate} kbps
            </label>
            <input
              type="range"
              min="1000"
              max="10000"
              step="500"
              value={settings.bitrate}
              onChange={(e) => setSettings(prev => ({ ...prev, bitrate: parseInt(e.target.value) }))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Compression */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Compression: {settings.compression}%
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={settings.compression}
              onChange={(e) => setSettings(prev => ({ ...prev, compression: parseInt(e.target.value) }))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={handleOptimize}
            disabled={optimizing}
            className={`px-6 py-2 rounded-md text-white font-medium ${
              optimizing
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            } transition-colors flex items-center space-x-2`}
          >
            {optimizing ? (
              <>
                <ArrowPathIcon className="h-4 w-4 animate-spin" />
                <span>Optimizing...</span>
              </>
            ) : (
              <>
                <PlayIcon className="h-4 w-4" />
                <span>Start Optimization</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Optimization Results */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <ChartBarIcon className="h-5 w-5 mr-2" />
          Optimization Results
        </h3>

        <div className="space-y-4">
          {results.map(result => (
            <div key={result.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <PhotoIcon className="h-8 w-8 text-gray-400" />
                  <div>
                    <h4 className="font-medium text-gray-900">{result.filename}</h4>
                    <p className="text-sm text-gray-500">
                      {result.originalSize} → {result.optimizedSize}
                    </p>
                  </div>
                </div>
                <CheckCircleIcon className="h-6 w-6 text-green-500" />
              </div>

              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">
                    {result.compressionRatio}%
                  </p>
                  <p className={`text-sm font-medium ${getSavingsColor(result.compressionRatio)}`}>
                    Size Reduction
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">
                    {result.qualityScore}
                  </p>
                  <p className={`text-sm font-medium ${getQualityColor(result.qualityScore)}`}>
                    Quality Score
                  </p>
                </div>
                <div className="text-center">
                  <button className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium hover:bg-green-200 transition-colors">
                    Download
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tips */}
      <div className="bg-yellow-50 rounded-lg p-4">
        <h4 className="font-medium text-yellow-900 mb-2">Optimization Tips</h4>
        <ul className="text-sm text-yellow-700 space-y-1">
          <li>• Higher compression reduces file size but may impact quality</li>
          <li>• 85% quality setting usually provides the best balance</li>
          <li>• Lower resolutions significantly reduce file sizes</li>
          <li>• Video bitrate affects both quality and file size</li>
        </ul>
      </div>
    </div>
  );
};

export default QualityOptimizer;