/**
 * Content Preview with Metadata Component - Professional Dashboard
 * 
 * Provides content preview functionality with comprehensive metadata display
 * Supports multiple file formats and detailed content information
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  DocumentTextIcon,
  MusicalNoteIcon,
  VideoCameraIcon,
  PhotoIcon,
  InformationCircleIcon,
  ShieldCheckIcon,
  CalendarIcon,
  FolderIcon,
  TagIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  PlayIcon,
  PauseIcon
} from '@heroicons/react/24/outline';

interface ContentMetadata {
  id: string;
  filename: string;
  type: 'audio' | 'video' | 'image' | 'document';
  size: number;
  duration?: number;
  resolution?: string;
  format: string;
  uploadDate: string;
  lastModified: string;
  protection_status: 'protected' | 'processing' | 'unprotected';
  fingerprint_id?: string;
  tags: string[];
  description: string;
  thumbnail_url?: string;
  preview_url?: string;
  metadata: {
    artist?: string;
    album?: string;
    genre?: string;
    bitrate?: number;
    sampleRate?: number;
    channels?: number;
    codec?: string;
    [key: string]: any;
  };
}

interface ContentPreviewProps {
  selectedContent?: ContentMetadata | null;
  onClose?: () => void;
}

export function ContentPreview({ selectedContent, onClose }: ContentPreviewProps) {
  const [content, setContent] = useState<ContentMetadata[]>([]);
  const [selectedItem, setSelectedItem] = useState<ContentMetadata | null>(selectedContent || null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [loading, setLoading] = useState(true);

  // Sample content data
  useEffect(() => {
    // Simulate API call to fetch recent content
    setTimeout(() => {
      const sampleContent: ContentMetadata[] = [
        {
          id: '1',
          filename: 'Epic_Track_2024_Final.mp3',
          type: 'audio',
          size: 8392847,
          duration: 245,
          format: 'MP3',
          uploadDate: '2024-01-15T10:30:00Z',
          lastModified: '2024-01-15T10:30:00Z',
          protection_status: 'protected',
          fingerprint_id: 'fp_audio_7829',
          tags: ['music', 'electronic', 'original'],
          description: 'Original electronic track with professional mastering',
          thumbnail_url: '/api/thumbnails/audio_1.jpg',
          preview_url: '/api/preview/audio_1.mp3',
          metadata: {
            artist: 'Creator Name',
            album: '2024 Collection',
            genre: 'Electronic',
            bitrate: 320,
            sampleRate: 44100,
            channels: 2,
            codec: 'MP3'
          }
        },
        {
          id: '2',
          filename: 'Tutorial_Video_Part1.mp4',
          type: 'video',
          size: 142857264,
          duration: 1847,
          resolution: '1920x1080',
          format: 'MP4',
          uploadDate: '2024-01-14T14:22:00Z',
          lastModified: '2024-01-14T14:22:00Z',
          protection_status: 'protected',
          fingerprint_id: 'fp_video_4582',
          tags: ['tutorial', 'education', 'professional'],
          description: 'Professional tutorial video in 4K quality',
          thumbnail_url: '/api/thumbnails/video_2.jpg',
          preview_url: '/api/preview/video_2.mp4',
          metadata: {
            codec: 'H.264',
            framerate: 30,
            bitrate: 8000
          }
        },
        {
          id: '3',
          filename: 'Portfolio_Image_HD.jpg',
          type: 'image',
          size: 2547293,
          format: 'JPEG',
          resolution: '3840x2160',
          uploadDate: '2024-01-13T09:15:00Z',
          lastModified: '2024-01-13T09:15:00Z',
          protection_status: 'processing',
          tags: ['portfolio', 'photography', 'professional'],
          description: 'High-resolution portfolio image',
          thumbnail_url: '/api/thumbnails/image_3.jpg',
          metadata: {
            camera: 'Canon EOS R5',
            lens: 'RF 24-70mm f/2.8',
            iso: 200,
            aperture: 'f/4.0',
            shutter: '1/125s'
          }
        }
      ];
      
      setContent(sampleContent);
      if (!selectedContent && sampleContent.length > 0) {
        setSelectedItem(sampleContent[0]);
      }
      setLoading(false);
    }, 500);
  }, [selectedContent]);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'audio': return MusicalNoteIcon;
      case 'video': return VideoCameraIcon;
      case 'image': return PhotoIcon;
      case 'document': return DocumentTextIcon;
      default: return FolderIcon;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'protected': return 'bg-green-100 text-green-800 border-green-200';
      case 'processing': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'unprotected': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatFileSize = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return 'N/A';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${Math.floor(secs).toString().padStart(2, '0')}`;
    }
    return `${minutes}:${Math.floor(secs).toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md border p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-3 bg-gray-200 rounded"></div>
            <div className="h-3 bg-gray-200 rounded w-5/6"></div>
            <div className="h-3 bg-gray-200 rounded w-4/6"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md border">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <InformationCircleIcon className="w-5 h-5 text-blue-500" />
            <h3 className="text-lg font-semibold text-gray-900">Content Preview & Metadata</h3>
          </div>
          {onClose && (
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-xl font-semibold"
            >
              ×
            </button>
          )}
        </div>
      </div>

      <div className="flex">
        {/* Content List Sidebar */}
        <div className="w-1/3 border-r border-gray-200 p-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Recent Content</h4>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {content.map((item) => {
              const TypeIcon = getTypeIcon(item.type);
              return (
                <div
                  key={item.id}
                  onClick={() => setSelectedItem(item)}
                  className={`p-3 rounded-lg cursor-pointer border transition-colors ${
                    selectedItem?.id === item.id 
                      ? 'bg-blue-50 border-blue-200' 
                      : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <TypeIcon className="w-5 h-5 text-gray-500" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {item.filename}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatFileSize(item.size)} • {item.format}
                      </p>
                    </div>
                  </div>
                  <div className="mt-2">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(item.protection_status)}`}>
                      {item.protection_status}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Content Details */}
        <div className="flex-1 p-6">
          {selectedItem ? (
            <div className="space-y-6">
              {/* File Info */}
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  {React.createElement(getTypeIcon(selectedItem.type), { className: "w-8 h-8 text-blue-500" })}
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900">{selectedItem.filename}</h4>
                    <p className="text-sm text-gray-600">{selectedItem.description}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {selectedItem.type === 'audio' && (
                    <button
                      onClick={() => setIsPlaying(!isPlaying)}
                      className="p-2 bg-blue-100 hover:bg-blue-200 rounded-full transition-colors"
                    >
                      {isPlaying ? (
                        <PauseIcon className="w-5 h-5 text-blue-600" />
                      ) : (
                        <PlayIcon className="w-5 h-5 text-blue-600" />
                      )}
                    </button>
                  )}
                  <button className="p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors">
                    <ArrowDownTrayIcon className="w-5 h-5 text-gray-600" />
                  </button>
                  <button className="p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors">
                    <EyeIcon className="w-5 h-5 text-gray-600" />
                  </button>
                </div>
              </div>

              {/* Preview */}
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <h5 className="text-sm font-semibold text-gray-700 mb-3">Preview</h5>
                {selectedItem.type === 'image' ? (
                  <div className="bg-white rounded-lg p-4 border border-gray-200">
                    <div className="w-full h-48 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg flex items-center justify-center">
                      <PhotoIcon className="w-12 h-12 text-gray-400" />
                    </div>
                  </div>
                ) : selectedItem.type === 'video' ? (
                  <div className="bg-black rounded-lg aspect-video flex items-center justify-center">
                    <div className="text-white text-center">
                      <VideoCameraIcon className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                      <p className="text-sm">Video Preview</p>
                      <p className="text-xs text-gray-400">{selectedItem.resolution}</p>
                    </div>
                  </div>
                ) : selectedItem.type === 'audio' ? (
                  <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border border-gray-200">
                    <div className="text-center">
                      <MusicalNoteIcon className="w-12 h-12 mx-auto mb-3 text-blue-500" />
                      <p className="text-sm font-medium text-gray-700">Audio Waveform</p>
                      <div className="mt-4 flex items-center justify-center space-x-1">
                        {Array.from({ length: 40 }, (_, i) => (
                          <div 
                            key={i}
                            className="bg-blue-400 w-1 rounded-full"
                            style={{ 
                              height: `${Math.random() * 24 + 8}px`,
                              opacity: isPlaying ? 0.8 : 0.4
                            }}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="bg-white rounded-lg p-4 border border-gray-200">
                    <DocumentTextIcon className="w-12 h-12 mx-auto text-gray-400" />
                    <p className="text-center text-sm text-gray-600 mt-2">Document Preview</p>
                  </div>
                )}
              </div>

              {/* Metadata Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Essential Information */}
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <h5 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                    <FolderIcon className="w-4 h-4 mr-2" />
                    Essential Information
                  </h5>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Size:</span>
                      <span className="font-medium">{formatFileSize(selectedItem.size)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Format:</span>
                      <span className="font-medium">{selectedItem.format}</span>
                    </div>
                    {selectedItem.duration && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Duration:</span>
                        <span className="font-medium">{formatDuration(selectedItem.duration)}</span>
                      </div>
                    )}
                    {selectedItem.resolution && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Resolution:</span>
                        <span className="font-medium">{selectedItem.resolution}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Protection Status */}
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <h5 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                    <ShieldCheckIcon className="w-4 h-4 mr-2" />
                    Protection Status
                  </h5>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">Status:</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(selectedItem.protection_status)}`}>
                        {selectedItem.protection_status}
                      </span>
                    </div>
                    {selectedItem.fingerprint_id && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Fingerprint ID:</span>
                        <span className="font-medium text-xs">{selectedItem.fingerprint_id}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Dates */}
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <h5 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                    <CalendarIcon className="w-4 h-4 mr-2" />
                    Timestamps
                  </h5>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Uploaded:</span>
                      <span className="font-medium">{new Date(selectedItem.uploadDate).toLocaleDateString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Modified:</span>
                      <span className="font-medium">{new Date(selectedItem.lastModified).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                {/* Tags */}
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <h5 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                    <TagIcon className="w-4 h-4 mr-2" />
                    Tags
                  </h5>
                  <div className="flex flex-wrap gap-2">
                    {selectedItem.tags.map((tag, index) => (
                      <span 
                        key={index}
                        className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Technical Metadata */}
              {Object.keys(selectedItem.metadata).length > 0 && (
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <h5 className="text-sm font-semibold text-gray-700 mb-3">Technical Metadata</h5>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    {Object.entries(selectedItem.metadata).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="text-gray-600 capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}:</span>
                        <span className="font-medium">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <FolderIcon className="w-12 h-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600">Select content to view details and metadata</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}