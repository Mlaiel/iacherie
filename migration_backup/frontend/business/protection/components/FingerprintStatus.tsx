/**
 * Fingerprint Status - Monitor content fingerprinting status
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  FingerPrintIcon, 
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  ClockIcon,
  EyeIcon,
  DocumentIcon,
  MusicalNoteIcon,
  VideoCameraIcon,
  PhotoIcon
} from '@heroicons/react/24/outline';

interface FingerprintItem {
  id: string;
  filename: string;
  type: 'audio' | 'video' | 'image' | 'document';
  status: 'processing' | 'completed' | 'failed' | 'pending';
  accuracy: number;
  processedAt?: string;
  fingerprintId?: string;
  fileSize: number;
  duration?: number;
}

interface FingerprintStats {
  totalProcessed: number;
  successRate: number;
  averageAccuracy: number;
  processingTime: number;
}

const FingerprintStatus: React.FC = () => {
  const [fingerprints, setFingerprints] = React.useState<FingerprintItem[]>([]);
  const [stats, setStats] = React.useState<FingerprintStats | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [filter, setFilter] = React.useState<'all' | 'audio' | 'video' | 'image'>('all');

  React.useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      const items: FingerprintItem[] = [
        {
          id: '1',
          filename: 'Track_Master_Final.mp3',
          type: 'audio',
          status: 'completed',
          accuracy: 98.5,
          processedAt: '2024-01-15T10:30:00Z',
          fingerprintId: 'fp_audio_abc123',
          fileSize: 8547328,
          duration: 245
        },
        {
          id: '2',
          filename: 'Music_Video_HD.mp4',
          type: 'video',
          status: 'completed',
          accuracy: 95.2,
          processedAt: '2024-01-14T15:45:00Z',
          fingerprintId: 'fp_video_def456',
          fileSize: 157286400,
          duration: 180
        },
        {
          id: '3',
          filename: 'Album_Cover_Art.jpg',
          type: 'image',
          status: 'completed',
          accuracy: 99.1,
          processedAt: '2024-01-13T09:20:00Z',
          fingerprintId: 'fp_image_ghi789',
          fileSize: 2048576
        },
        {
          id: '4',
          filename: 'New_Upload_Song.wav',
          type: 'audio',
          status: 'processing',
          accuracy: 0,
          fileSize: 45678912,
          duration: 320
        },
        {
          id: '5',
          filename: 'Behind_Scenes.mp4',
          type: 'video',
          status: 'failed',
          accuracy: 0,
          fileSize: 89234567
        }
      ];

      setFingerprints(items);
      
      const completedItems = items.filter(item => item.status === 'completed');
      setStats({
        totalProcessed: items.length,
        successRate: (completedItems.length / items.length) * 100,
        averageAccuracy: completedItems.reduce((sum, item) => sum + item.accuracy, 0) / completedItems.length,
        processingTime: 45 // Average seconds
      });
      
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'processing': return <ClockIcon className="h-5 w-5 text-yellow-500 animate-spin" />;
      case 'failed': return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'pending': return <ExclamationTriangleIcon className="h-5 w-5 text-gray-500" />;
      default: return <ClockIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'audio': return <MusicalNoteIcon className="h-6 w-6 text-purple-500" />;
      case 'video': return <VideoCameraIcon className="h-6 w-6 text-red-500" />;
      case 'image': return <PhotoIcon className="h-6 w-6 text-blue-500" />;
      default: return <DocumentIcon className="h-6 w-6 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'pending': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '-';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const filteredFingerprints = filter === 'all' 
    ? fingerprints 
    : fingerprints.filter(item => item.type === filter);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Fingerprint Status</h1>
            <p className="text-gray-600">Monitor content fingerprinting processing and accuracy</p>
          </div>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center">
            <EyeIcon className="h-5 w-5 mr-2" />
            View Details
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Processed</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.totalProcessed}</p>
            </div>
            <FingerPrintIcon className="h-10 w-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.successRate.toFixed(1)}%</p>
            </div>
            <CheckCircleIcon className="h-10 w-10 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Accuracy</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.averageAccuracy.toFixed(1)}%</p>
            </div>
            <FingerPrintIcon className="h-10 w-10 text-purple-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Processing</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.processingTime}s</p>
            </div>
            <ClockIcon className="h-10 w-10 text-yellow-500" />
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="bg-white rounded-lg shadow-md mb-8">
        <div className="border-b">
          <nav className="flex space-x-8 p-6">
            {[
              { id: 'all', name: 'All Files', count: fingerprints.length },
              { id: 'audio', name: 'Audio', count: fingerprints.filter(f => f.type === 'audio').length },
              { id: 'video', name: 'Video', count: fingerprints.filter(f => f.type === 'video').length },
              { id: 'image', name: 'Images', count: fingerprints.filter(f => f.type === 'image').length },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setFilter(tab.id as 'all' | 'audio' | 'video' | 'image')}
                className={`pb-4 border-b-2 font-medium text-sm transition-colors ${
                  filter === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.name} ({tab.count})
              </button>
            ))}
          </nav>
        </div>

        {/* Fingerprint List */}
        <div className="p-6">
          <div className="space-y-4">
            {filteredFingerprints.map((item) => (
              <div key={item.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    {getFileIcon(item.type)}
                    <div>
                      <h4 className="font-medium text-gray-900">{item.filename}</h4>
                      <p className="text-sm text-gray-500">
                        {formatFileSize(item.fileSize)} • {formatDuration(item.duration)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                      {item.status.toUpperCase()}
                    </span>
                    {getStatusIcon(item.status)}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Type:</span>
                    <span className="ml-2 font-medium capitalize">{item.type}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Accuracy:</span>
                    <span className={`ml-2 font-medium ${
                      item.accuracy >= 95 ? 'text-green-600' : 
                      item.accuracy >= 85 ? 'text-yellow-600' : 
                      item.accuracy > 0 ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      {item.accuracy > 0 ? `${item.accuracy}%` : '-'}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Processed:</span>
                    <span className="ml-2 font-medium">
                      {item.processedAt ? new Date(item.processedAt).toLocaleDateString() : '-'}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Fingerprint ID:</span>
                    <span className="ml-2 font-mono text-xs">
                      {item.fingerprintId || '-'}
                    </span>
                  </div>
                </div>

                {item.status === 'completed' && (
                  <div className="mt-3 pt-3 border-t">
                    <div className="flex space-x-4">
                      <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                        View Fingerprint
                      </button>
                      <button className="text-green-600 hover:text-green-700 text-sm font-medium">
                        Monitor Violations
                      </button>
                      <button className="text-gray-600 hover:text-gray-700 text-sm font-medium">
                        Reprocess
                      </button>
                    </div>
                  </div>
                )}

                {item.status === 'failed' && (
                  <div className="mt-3 pt-3 border-t">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-red-600">Processing failed. Please try again.</span>
                      <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                        Retry
                      </button>
                    </div>
                  </div>
                )}

                {item.status === 'processing' && (
                  <div className="mt-3 pt-3 border-t">
                    <div className="flex items-center space-x-3">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
                      </div>
                      <span className="text-sm text-gray-600">Processing...</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {filteredFingerprints.length === 0 && (
            <div className="text-center py-12">
              <FingerPrintIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No fingerprints found</h3>
              <p className="text-gray-600">No files match the selected filter criteria.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FingerprintStatus;