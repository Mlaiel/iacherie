/**
 * Upload Hook - Custom hook for file upload management
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { useState, useCallback } from 'react';
import { api } from '../utils/api';

interface UploadProgress {
  [fileId: string]: {
    progress: number;
    status: 'uploading' | 'processing' | 'completed' | 'error';
    message?: string;
  };
}

export const useUpload = () => {
  const [progress, setProgress] = useState<UploadProgress>({});
  const [isUploading, setIsUploading] = useState(false);

  const uploadFiles = useCallback(async (files: File[]) => {
    setIsUploading(true);
    
    try {
      for (const file of files) {
        const fileId = `${file.name}_${Date.now()}`;
        
        setProgress(prev => ({
          ...prev,
          [fileId]: { progress: 0, status: 'uploading' }
        }));

        await api.upload.uploadFile(file, {
          onUploadProgress: (progressEvent: any) => {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setProgress(prev => ({
              ...prev,
              [fileId]: { progress, status: 'uploading' }
            }));
          }
        });

        setProgress(prev => ({
          ...prev,
          [fileId]: { progress: 100, status: 'completed' }
        }));
      }
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  }, []);

  const clearProgress = useCallback(() => {
    setProgress({});
  }, []);

  return {
    progress,
    isUploading,
    uploadFiles,
    clearProgress,
  };
};

export default useUpload;
