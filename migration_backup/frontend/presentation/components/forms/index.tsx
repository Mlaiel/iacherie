/**
 * MediaUploader - Multi-format drag & drop upload component
 * 
 * Advanced file upload interface with support for multiple formats,
 * drag & drop functionality, progress tracking, and format validation
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  CloudArrowUpIcon,
  DocumentIcon,
  MusicalNoteIcon,
  VideoCameraIcon,
  PhotoIcon,
  CheckCircleIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  TrashIcon,
  PlusIcon
} from '@heroicons/react/24/outline';

export interface UploadFile {
  id: string;
  name: string;
  size: number;
  type: string;
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
  preview?: string;
  uploadedAt?: Date;
}

export interface MediaUploaderProps {
  maxFiles?: number;
  maxFileSize?: number; // in bytes
  acceptedTypes?: string[];
  onFilesAdded?: (files: UploadFile[]) => void;
  onFileRemoved?: (fileId: string) => void;
  onUploadComplete?: (files: UploadFile[]) => void;
  onUploadError?: (error: string, fileId?: string) => void;
  className?: string;
  disabled?: boolean;
  showPreview?: boolean;
}

const SUPPORTED_FORMATS = {
  image: ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'],
  video: ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/webm'],
  audio: ['audio/mp3', 'audio/wav', 'audio/flac', 'audio/aac', 'audio/ogg'],
  document: ['application/pdf', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
};

const ALL_SUPPORTED_TYPES = Object.values(SUPPORTED_FORMATS).flat();

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const getFileIcon = (type: string) => {
  if (type.startsWith('image/')) return PhotoIcon;
  if (type.startsWith('video/')) return VideoCameraIcon;
  if (type.startsWith('audio/')) return MusicalNoteIcon;
  return DocumentIcon;
};

const getFileCategory = (type: string): string => {
  if (type.startsWith('image/')) return 'Image';
  if (type.startsWith('video/')) return 'Video';
  if (type.startsWith('audio/')) return 'Audio';
  return 'Document';
};

export const MediaUploader: React.FC<MediaUploaderProps> = ({
  maxFiles = 10,
  maxFileSize = 100 * 1024 * 1024, // 100MB default
  acceptedTypes = ALL_SUPPORTED_TYPES,
  onFilesAdded,
  onFileRemoved,
  onUploadComplete,
  onUploadError,
  className = '',
  disabled = false,
  showPreview = true
}) => {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    if (!acceptedTypes.includes(file.type)) {
      return `File type "${file.type}" is not supported`;
    }
    if (file.size > maxFileSize) {
      return `File size exceeds maximum limit of ${formatFileSize(maxFileSize)}`;
    }
    if (files.length >= maxFiles) {
      return `Maximum number of files (${maxFiles}) exceeded`;
    }
    return null;
  };

  const createFilePreview = async (file: File): Promise<string | undefined> => {
    if (!showPreview || !file.type.startsWith('image/')) return undefined;
    
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.onerror = () => resolve(undefined);
      reader.readAsDataURL(file);
    });
  };

  const processFiles = async (fileList: FileList | File[]) => {
    const newFiles: UploadFile[] = [];
    const errors: string[] = [];

    for (const file of Array.from(fileList)) {
      const error = validateFile(file);
      if (error) {
        errors.push(`${file.name}: ${error}`);
        continue;
      }

      const preview = await createFilePreview(file);
      const uploadFile: UploadFile = {
        id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: file.name,
        size: file.size,
        type: file.type,
        file,
        progress: 0,
        status: 'pending',
        preview,
        uploadedAt: new Date()
      };

      newFiles.push(uploadFile);
    }

    if (errors.length > 0) {
      onUploadError?.(errors.join('\n'));
    }

    if (newFiles.length > 0) {
      const updatedFiles = [...files, ...newFiles];
      setFiles(updatedFiles);
      onFilesAdded?.(newFiles);
    }
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setDragActive(true);
    }
  }, []);

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFiles(e.dataTransfer.files);
    }
  }, [disabled, processFiles]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (disabled) return;
    
    const selectedFiles = e.target.files;
    if (selectedFiles && selectedFiles.length > 0) {
      processFiles(selectedFiles);
    }
    
    // Reset input value to allow re-selecting the same file
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeFile = (fileId: string) => {
    const updatedFiles = files.filter(f => f.id !== fileId);
    setFiles(updatedFiles);
    onFileRemoved?.(fileId);
  };

  const retryUpload = (fileId: string) => {
    setFiles(prev => prev.map(f => 
      f.id === fileId 
        ? { ...f, status: 'pending', error: undefined, progress: 0 }
        : f
    ));
  };

  const triggerFileSelect = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const clearAllFiles = () => {
    setFiles([]);
    setUploadProgress({});
  };

  // Simulate upload progress (replace with actual upload logic)
  useEffect(() => {
    const pendingFiles = files.filter(f => f.status === 'pending');
    
    pendingFiles.forEach(file => {
      if (uploadProgress[file.id] !== undefined) return;
      
      setFiles(prev => prev.map(f => 
        f.id === file.id ? { ...f, status: 'uploading' } : f
      ));

      const interval = setInterval(() => {
        setUploadProgress(prev => {
          const currentProgress = prev[file.id] || 0;
          const newProgress = Math.min(currentProgress + Math.random() * 20, 100);
          
          if (newProgress >= 100) {
            clearInterval(interval);
            setFiles(prevFiles => prevFiles.map(f => 
              f.id === file.id 
                ? { ...f, status: 'completed', progress: 100 }
                : f
            ));
            return { ...prev, [file.id]: 100 };
          }
          
          setFiles(prevFiles => prevFiles.map(f => 
            f.id === file.id ? { ...f, progress: newProgress } : f
          ));
          
          return { ...prev, [file.id]: newProgress };
        });
      }, 200);
    });
  }, [files.length]);

  const completedFiles = files.filter(f => f.status === 'completed');
  const hasErrors = files.some(f => f.status === 'error');

  return (
    <div className={`w-full ${className}`}>
      {/* Upload Area */}
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200
          ${dragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
        onDragEnter={handleDragIn}
        onDragLeave={handleDragOut}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={triggerFileSelect}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={acceptedTypes.join(',')}
          onChange={handleFileSelect}
          className="hidden"
          disabled={disabled}
        />

        <div className="space-y-4">
          <div className="flex justify-center">
            {dragActive ? (
              <CloudArrowUpIcon className="w-16 h-16 text-blue-500" />
            ) : (
              <PlusIcon className="w-16 h-16 text-gray-400" />
            )}
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {dragActive ? 'Drop files here' : 'Upload Media Files'}
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Drag and drop files here, or click to select files
            </p>
          </div>

          <div className="text-xs text-gray-400 space-y-1">
            <p>Supported formats: Images, Videos, Audio, Documents</p>
            <p>Maximum file size: {formatFileSize(maxFileSize)}</p>
            <p>Maximum files: {maxFiles}</p>
          </div>
        </div>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-6 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-lg font-semibold text-gray-900">
              Uploaded Files ({files.length}/{maxFiles})
            </h4>
            <button
              onClick={clearAllFiles}
              className="text-sm text-red-600 hover:text-red-700 flex items-center space-x-1"
            >
              <TrashIcon className="w-4 h-4" />
              <span>Clear All</span>
            </button>
          </div>

          <div className="space-y-2">
            {files.map((file) => {
              const IconComponent = getFileIcon(file.type);
              const category = getFileCategory(file.type);

              return (
                <div
                  key={file.id}
                  className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg bg-white"
                >
                  {/* Preview/Icon */}
                  <div className="flex-shrink-0">
                    {file.preview ? (
                      <img
                        src={file.preview}
                        alt={file.name}
                        className="w-12 h-12 object-cover rounded-lg"
                      />
                    ) : (
                      <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                        <IconComponent className="w-6 h-6 text-gray-500" />
                      </div>
                    )}
                  </div>

                  {/* File Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {file.name}
                      </p>
                      <span className="text-xs text-gray-500 ml-2">
                        {category}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(file.size)}
                    </p>

                    {/* Progress Bar */}
                    {file.status === 'uploading' && (
                      <div className="mt-2">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${file.progress}%` }}
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          {Math.round(file.progress)}% uploaded
                        </p>
                      </div>
                    )}

                    {/* Error Message */}
                    {file.status === 'error' && file.error && (
                      <p className="text-xs text-red-600 mt-1">{file.error}</p>
                    )}
                  </div>

                  {/* Status & Actions */}
                  <div className="flex items-center space-x-2">
                    {file.status === 'completed' && (
                      <CheckCircleIcon className="w-5 h-5 text-green-500" />
                    )}
                    {file.status === 'uploading' && (
                      <ArrowPathIcon className="w-5 h-5 text-blue-500 animate-spin" />
                    )}
                    {file.status === 'error' && (
                      <>
                        <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />
                        <button
                          onClick={() => retryUpload(file.id)}
                          className="text-xs text-blue-600 hover:text-blue-700"
                        >
                          Retry
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => removeFile(file.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <XMarkIcon className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Summary */}
          {completedFiles.length > 0 && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <CheckCircleIcon className="w-5 h-5 text-green-500" />
                <span className="text-sm font-medium text-green-800">
                  {completedFiles.length} file(s) uploaded successfully
                </span>
              </div>
            </div>
          )}

          {hasErrors && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />
                <span className="text-sm font-medium text-red-800">
                  Some files failed to upload. Please check and retry.
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MediaUploader;