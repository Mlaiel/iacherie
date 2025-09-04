/**
 * Upload Context - File upload management context
 */

import { createContext, useContext, ReactNode, useState } from 'react';

interface UploadItem {
  id: string;
  file: File;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
}

interface UploadContextType {
  uploads: UploadItem[];
  addUpload: (file: File) => string;
  updateProgress: (id: string, progress: number) => void;
  setStatus: (id: string, status: UploadItem['status'], error?: string) => void;
  removeUpload: (id: string) => void;
  clearCompleted: () => void;
}

const UploadContext = createContext<UploadContextType | undefined>(undefined);

export function UploadProvider({ children }: { children: ReactNode }) {
  const [uploads, setUploads] = useState<UploadItem[]>([]);

  const addUpload = (file: File): string => {
    const id = `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const uploadItem: UploadItem = {
      id,
      file,
      progress: 0,
      status: 'uploading',
    };
    setUploads(prev => [...prev, uploadItem]);
    return id;
  };

  const updateProgress = (id: string, progress: number) => {
    setUploads(prev => prev.map(upload =>
      upload.id === id ? { ...upload, progress } : upload
    ));
  };

  const setStatus = (id: string, status: UploadItem['status'], error?: string) => {
    setUploads(prev => prev.map(upload =>
      upload.id === id ? { ...upload, status, error } : upload
    ));
  };

  const removeUpload = (id: string) => {
    setUploads(prev => prev.filter(upload => upload.id !== id));
  };

  const clearCompleted = () => {
    setUploads(prev => prev.filter(upload => 
      upload.status !== 'completed' && upload.status !== 'error'
    ));
  };

  return (
    <UploadContext.Provider value={{
      uploads,
      addUpload,
      updateProgress,
      setStatus,
      removeUpload,
      clearCompleted,
    }}>
      {children}
    </UploadContext.Provider>
  );
}

export const useUpload = () => {
  const context = useContext(UploadContext);
  if (!context) {
    throw new Error('useUpload must be used within an UploadProvider');
  }
  return context;
};
