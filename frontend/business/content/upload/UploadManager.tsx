/**
 * @fileoverview Upload Manager - Intelligent file upload with validation and progress tracking
 * @author Fahed Mlaiel <mlaiel@live.de>
 */

'use client';

import React, { useState, useCallback, useRef } from 'react';
import { ContentUpload, ContentMetadata } from '@/core/types';
import { CONTENT_CONSTANTS } from '@/core/constants';
import { ContentFormat, ProcessingStage } from '@/core/enums';

interface UploadManagerProps {
  onUploadComplete?: (upload: ContentUpload) => void;
  onUploadError?: (error: string) => void;
  maxFiles?: number;
  acceptedFormats?: string[];
  className?: string;
}

export const UploadManager: React.FC<UploadManagerProps> = ({
  onUploadComplete,
  onUploadError,
  maxFiles = 10,
  acceptedFormats = Object.values(CONTENT_CONSTANTS.SUPPORTED_FORMATS).flat(),
  className = '',
}) => {
  const [uploads, setUploads] = useState<ContentUpload[]>([]);
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = useCallback((file: File): string | null => {
    // Check file size
    if (file.size > CONTENT_CONSTANTS.MAX_FILE_SIZE) {
      return `File size exceeds ${CONTENT_CONSTANTS.MAX_FILE_SIZE / (1024 * 1024)}MB limit`;
    }

    // Check file format
    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    if (!fileExtension || !acceptedFormats.includes(fileExtension)) {
      return `Unsupported file format: ${fileExtension}`;
    }

    return null;
  }, [acceptedFormats]);

  const createContentMetadata = useCallback((file: File): Partial<ContentMetadata> => {
    const fileExtension = file.name.split('.').pop()?.toLowerCase() || '';
    const nameWithoutExtension = file.name.replace(/\.[^/.]+$/, '');

    return {
      title: nameWithoutExtension,
      format: fileExtension,
      size: file.size,
      createdAt: new Date(),
      updatedAt: new Date(),
      tags: [],
      categories: [],
    };
  }, []);

  const processFiles = useCallback(async (files: FileList | File[]) => {
    const fileArray = Array.from(files);
    
    if (uploads.length + fileArray.length > maxFiles) {
      onUploadError?.(`Cannot upload more than ${maxFiles} files`);
      return;
    }

    const newUploads: ContentUpload[] = [];

    for (const file of fileArray) {
      const validationError = validateFile(file);
      if (validationError) {
        onUploadError?.(validationError);
        continue;
      }

      const upload: ContentUpload = {
        file,
        metadata: createContentMetadata(file),
        progress: 0,
        status: 'pending',
      };

      newUploads.push(upload);
    }

    if (newUploads.length > 0) {
      setUploads(prev => [...prev, ...newUploads]);
      
      // Start processing uploads
      for (const upload of newUploads) {
        await processUpload(upload);
      }
    }
  }, [uploads.length, maxFiles, validateFile, createContentMetadata, onUploadError]);

  const processUpload = useCallback(async (upload: ContentUpload) => {
    try {
      // Update status to uploading
      setUploads(prev => prev.map(u => 
        u.file.name === upload.file.name 
          ? { ...u, status: 'uploading' }
          : u
      ));

      // Simulate upload progress
      for (let progress = 0; progress <= 100; progress += 10) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setUploads(prev => prev.map(u => 
          u.file.name === upload.file.name 
            ? { ...u, progress }
            : u
        ));
      }

      // Update to processing
      setUploads(prev => prev.map(u => 
        u.file.name === upload.file.name 
          ? { ...u, status: 'processing' }
          : u
      ));

      // Simulate processing delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Complete upload
      const completedUpload = {
        ...upload,
        status: 'completed' as const,
        progress: 100,
        fingerprint: generateFingerprint(upload.file),
      };

      setUploads(prev => prev.map(u => 
        u.file.name === upload.file.name 
          ? completedUpload
          : u
      ));

      onUploadComplete?.(completedUpload);
    } catch (error) {
      setUploads(prev => prev.map(u => 
        u.file.name === upload.file.name 
          ? { ...u, status: 'failed' }
          : u
      ));
      onUploadError?.(`Failed to upload ${upload.file.name}`);
    }
  }, [onUploadComplete, onUploadError]);

  const generateFingerprint = useCallback((file: File): string => {
    // Generate a simple hash-like fingerprint
    return `fp_${file.name}_${file.size}_${Date.now()}`;
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      processFiles(files);
    }
  }, [processFiles]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      processFiles(files);
    }
  }, [processFiles]);

  const removeUpload = useCallback((fileName: string) => {
    setUploads(prev => prev.filter(u => u.file.name !== fileName));
  }, []);

  return (
    <div className={`upload-manager ${className}`}>
      {/* Drop Zone */}
      <div
        className={`
          border-2 border-dashed rounded-lg p-8 text-center transition-colors
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
        `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="cursor-pointer">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <p className="mt-2 text-sm text-gray-600">
            <span className="font-medium text-blue-600">Click to upload</span> or drag and drop
          </p>
          <p className="text-xs text-gray-500">
            Supports: {acceptedFormats.join(', ')} (max {maxFiles} files)
          </p>
        </div>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept={acceptedFormats.map(f => `.${f}`).join(',')}
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Upload list */}
      {uploads.length > 0 && (
        <div className="mt-6 space-y-3">
          <h4 className="text-sm font-medium text-gray-900">Uploads</h4>
          {uploads.map((upload) => (
            <div
              key={upload.file.name}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {upload.file.name}
                </p>
                <p className="text-xs text-gray-500">
                  {(upload.file.size / (1024 * 1024)).toFixed(2)} MB
                </p>
                
                {/* Progress bar */}
                {upload.status === 'uploading' && (
                  <div className="mt-2">
                    <div className="bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${upload.progress}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{upload.progress}%</p>
                  </div>
                )}
              </div>
              
              <div className="flex items-center space-x-2">
                {/* Status indicator */}
                <div className={`
                  w-3 h-3 rounded-full
                  ${upload.status === 'completed' ? 'bg-green-500' : ''}
                  ${upload.status === 'failed' ? 'bg-red-500' : ''}
                  ${upload.status === 'uploading' ? 'bg-blue-500' : ''}
                  ${upload.status === 'processing' ? 'bg-yellow-500' : ''}
                  ${upload.status === 'pending' ? 'bg-gray-400' : ''}
                `} />
                
                {/* Remove button */}
                <button
                  onClick={() => removeUpload(upload.file.name)}
                  className="text-gray-400 hover:text-red-500 transition-colors"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};