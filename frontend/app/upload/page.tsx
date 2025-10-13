/**
 * 📤 Upload Page - Multi-Format Content Upload with AI Processing
 * 
 * @fileoverview Advanced upload interface with AI-powered content processing
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

'use client';

import React, { useState, useCallback } from 'react';
import { 
  CloudArrowUpIcon,
  DocumentIcon,
  PhotoIcon,
  MusicalNoteIcon,
  VideoCameraIcon,
  SparklesIcon,
  ShieldCheckIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline';

interface UploadedFile {
  id: string;
  name: string;
  type: 'image' | 'video' | 'audio' | 'document';
  size: number;
  status: 'uploading' | 'processing' | 'complete' | 'error';
  progress: number;
  aiAnalysis?: {
    contentType: string;
    quality: number;
    monetizable: boolean;
    protectionLevel: string;
  };
}

export default function UploadPage() {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  }, []);

  const handleFiles = (fileList: File[]) => {
    const newFiles: UploadedFile[] = fileList.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      type: getFileType(file.type),
      size: file.size,
      status: 'uploading',
      progress: 0
    }));

    setFiles(prev => [...prev, ...newFiles]);

    // Simulate upload and AI processing
    newFiles.forEach(file => {
      simulateUpload(file.id);
    });
  };

  const getFileType = (mimeType: string): 'image' | 'video' | 'audio' | 'document' => {
    if (mimeType.startsWith('image/')) return 'image';
    if (mimeType.startsWith('video/')) return 'video';
    if (mimeType.startsWith('audio/')) return 'audio';
    return 'document';
  };

  const simulateUpload = (fileId: string) => {
    const progressInterval = setInterval(() => {
      setFiles(prev => prev.map(file => {
        if (file.id === fileId) {
          const newProgress = Math.min(file.progress + Math.random() * 20, 100);
          
          if (newProgress >= 100) {
            clearInterval(progressInterval);
            
            // Start AI processing
            setTimeout(() => {
              setFiles(prev => prev.map(f => 
                f.id === fileId ? { 
                  ...f, 
                  status: 'processing',
                  progress: 0
                } : f
              ));

              // Simulate AI analysis
              const aiInterval = setInterval(() => {
                setFiles(prev => prev.map(f => {
                  if (f.id === fileId) {
                    const aiProgress = Math.min(f.progress + Math.random() * 15, 100);
                    
                    if (aiProgress >= 100) {
                      clearInterval(aiInterval);
                      return {
                        ...f,
                        status: 'complete',
                        progress: 100,
                        aiAnalysis: {
                          contentType: 'Creative Content',
                          quality: Math.floor(Math.random() * 30) + 70,
                          monetizable: Math.random() > 0.3,
                          protectionLevel: 'High'
                        }
                      };
                    }
                    
                    return { ...f, progress: aiProgress };
                  }
                  return f;
                }));
              }, 500);
            }, 1000);
            
            return { ...file, status: 'uploading', progress: 100 };
          }
          
          return { ...file, progress: newProgress };
        }
        return file;
      }));
    }, 300);
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'image': return <PhotoIcon className="h-8 w-8 text-green-500" />;
      case 'video': return <VideoCameraIcon className="h-8 w-8 text-blue-500" />;
      case 'audio': return <MusicalNoteIcon className="h-8 w-8 text-purple-500" />;
      default: return <DocumentIcon className="h-8 w-8 text-gray-500" />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Upload Content</h1>
          <p className="text-gray-600 mt-2">Upload your content for AI-powered processing and protection</p>
        </div>

        {/* Upload Area */}
        <div
          className={`relative border-2 border-dashed rounded-lg p-8 mb-8 transition-colors ${
            dragActive 
              ? 'border-blue-400 bg-blue-50' 
              : 'border-gray-300 bg-white hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="text-center">
            <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
            <div className="mt-4">
              <label htmlFor="file-upload" className="cursor-pointer">
                <span className="text-lg font-medium text-gray-900">Drop files here or click to upload</span>
                <input
                  id="file-upload"
                  name="file-upload"
                  type="file"
                  className="sr-only"
                  multiple
                  onChange={(e) => e.target.files && handleFiles(Array.from(e.target.files))}
                />
              </label>
            </div>
            <p className="text-sm text-gray-500 mt-2">
              Support for images, videos, audio files, and documents up to 100MB
            </p>
          </div>
        </div>

        {/* Upload Progress */}
        {files.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Progress</h2>
            <div className="space-y-4">
              {files.map((file) => (
                <div key={file.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      {getFileIcon(file.type)}
                      <div>
                        <p className="text-sm font-medium text-gray-900">{file.name}</p>
                        <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {file.status === 'processing' && (
                        <SparklesIcon className="h-5 w-5 text-yellow-500 animate-pulse" />
                      )}
                      {file.status === 'complete' && (
                        <ShieldCheckIcon className="h-5 w-5 text-green-500" />
                      )}
                      <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                        file.status === 'uploading' ? 'bg-blue-100 text-blue-800' :
                        file.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                        file.status === 'complete' ? 'bg-green-100 text-green-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {file.status === 'uploading' ? 'Uploading' :
                         file.status === 'processing' ? 'AI Processing' :
                         file.status === 'complete' ? 'Complete' : 'Error'}
                      </span>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        file.status === 'uploading' ? 'bg-blue-500' :
                        file.status === 'processing' ? 'bg-yellow-500' :
                        'bg-green-500'
                      }`}
                      style={{ width: `${file.progress}%` }}
                    ></div>
                  </div>

                  {/* AI Analysis Results */}
                  {file.aiAnalysis && (
                    <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                      <h4 className="text-sm font-medium text-gray-900 mb-2">AI Analysis Results</h4>
                      <div className="grid grid-cols-2 gap-4 text-xs">
                        <div>
                          <span className="text-gray-500">Content Type:</span>
                          <span className="ml-2 font-medium">{file.aiAnalysis.contentType}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Quality Score:</span>
                          <span className="ml-2 font-medium">{file.aiAnalysis.quality}%</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Monetizable:</span>
                          <span className={`ml-2 font-medium ${file.aiAnalysis.monetizable ? 'text-green-600' : 'text-red-600'}`}>
                            {file.aiAnalysis.monetizable ? 'Yes' : 'No'}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-500">Protection:</span>
                          <span className="ml-2 font-medium">{file.aiAnalysis.protectionLevel}</span>
                        </div>
                      </div>
                      
                      {file.aiAnalysis.monetizable && (
                        <div className="mt-2 flex items-center space-x-2">
                          <CurrencyDollarIcon className="h-4 w-4 text-green-500" />
                          <span className="text-xs text-green-600 font-medium">
                            Ready for monetization
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Features Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <SparklesIcon className="h-8 w-8 text-purple-500 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Processing</h3>
            <p className="text-gray-600 text-sm">
              Automatic content analysis, quality assessment, and optimization suggestions.
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <ShieldCheckIcon className="h-8 w-8 text-blue-500 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Content Protection</h3>
            <p className="text-gray-600 text-sm">
              Advanced digital fingerprinting and copyright protection for your content.
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <CurrencyDollarIcon className="h-8 w-8 text-green-500 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Monetization</h3>
            <p className="text-gray-600 text-sm">
              Intelligent monetization strategies and platform distribution optimization.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}