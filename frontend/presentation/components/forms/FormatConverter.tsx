/**
 * Format Converter - Media format conversion component
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  ArrowPathIcon,
  DocumentArrowDownIcon,
  CogIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

interface ConversionTask {
  id: string;
  filename: string;
  fromFormat: string;
  toFormat: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  size: string;
}

const FormatConverter: React.FC = () => {
  const [tasks, setTasks] = React.useState<ConversionTask[]>([
    {
      id: '1',
      filename: 'video_sample.mp4',
      fromFormat: 'MP4',
      toFormat: 'WEBM',
      status: 'processing',
      progress: 65,
      size: '245 MB'
    },
    {
      id: '2',
      filename: 'audio_track.wav',
      fromFormat: 'WAV',
      toFormat: 'MP3',
      status: 'completed',
      progress: 100,
      size: '12 MB'
    }
  ]);

  const [selectedFormat, setSelectedFormat] = React.useState('MP4');
  const supportedFormats = ['MP4', 'WEBM', 'AVI', 'MOV', 'MP3', 'WAV', 'FLAC', 'OGG'];

  const handleConvert = () => {
    // Simulate conversion start
    const newTask: ConversionTask = {
      id: Date.now().toString(),
      filename: 'new_file.mp4',
      fromFormat: 'MP4',
      toFormat: selectedFormat,
      status: 'pending',
      progress: 0,
      size: '150 MB'
    };
    setTasks(prev => [newTask, ...prev]);
  };

  const getStatusIcon = (status: ConversionTask['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      case 'processing':
        return <ArrowPathIcon className="h-5 w-5 text-blue-500 animate-spin" />;
      default:
        return <CogIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Format Converter</h2>
          <p className="text-gray-600">Convert your media files to different formats</p>
        </div>
      </div>

      {/* Conversion Settings */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Conversion Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Format
            </label>
            <select
              value={selectedFormat}
              onChange={(e) => setSelectedFormat(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {supportedFormats.map(format => (
                <option key={format} value={format}>{format}</option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={handleConvert}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
            >
              Start Conversion
            </button>
          </div>
        </div>
      </div>

      {/* Conversion Queue */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Conversion Queue</h3>
        <div className="space-y-4">
          {tasks.map(task => (
            <div key={task.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(task.status)}
                  <div>
                    <p className="font-medium text-gray-900">{task.filename}</p>
                    <p className="text-sm text-gray-500">
                      {task.fromFormat} → {task.toFormat} • {task.size}
                    </p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  task.status === 'completed' ? 'bg-green-100 text-green-800' :
                  task.status === 'failed' ? 'bg-red-100 text-red-800' :
                  task.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {task.status}
                </span>
              </div>
              
              {task.status === 'processing' && (
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${task.progress}%` }}
                  ></div>
                </div>
              )}
              
              {task.status === 'completed' && (
                <button className="mt-2 flex items-center space-x-2 text-blue-600 hover:text-blue-700">
                  <DocumentArrowDownIcon className="h-4 w-4" />
                  <span className="text-sm">Download</span>
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Format Support Info */}
      <div className="bg-blue-50 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">Supported Formats</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-blue-700">
          {supportedFormats.map(format => (
            <span key={format} className="bg-blue-100 px-2 py-1 rounded">{format}</span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FormatConverter;