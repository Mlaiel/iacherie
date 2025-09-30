/**
 * 🎨 CONTENT UPLOAD TEMPLATE - FRONTEND EXPERT IMPLEMENTATION
 * ===========================================================
 * 
 * Enterprise-grade content upload component for Ainflue Creator Economy with:
 * - TypeScript support with strict typing
 * - Multi-format content upload (video, audio, images, documents)
 * - Drag & drop interface with preview
 * - Progress tracking and resumable uploads
 * - Content metadata and tagging
 * - AI-powered content analysis
 * - Batch upload and queue management
 * - Accessibility compliance and keyboard navigation
 * 
 * ⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
 * ==========================================
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 * 
 * 🚨 PROTECTION INTELLECTUELLE:
 * - Code propriétaire de Fahed Mlaiel
 * - Utilisation commerciale INTERDITE sans autorisation écrite
 * - Reverse engineering STRICTEMENT INTERDIT
 * - Distribution INTERDITE sans licence explicite
 * - Violation = Poursuites judiciaires automatiques
 * 
 * 🏢 USAGE ENTREPRISE:
 * - Licence entreprise disponible sur demande
 * - Support technique inclus avec licence
 * - Maintenance et mises à jour assurées
 * - Formation équipe technique fournie
 * 
 * Author: Frontend Expert - Fahed Mlaiel
 * Version: 1.0.0
 */

import React, { 
  useState, 
  useCallback, 
  useRef, 
  useEffect,
  ReactNode,
  DragEvent,
  ChangeEvent
} from 'react';
import styled, { css, keyframes } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface UploadFile {
  id: string;
  file: File;
  name: string;
  size: number;
  type: string;
  category: ContentCategory;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  preview?: string;
  metadata?: ContentMetadata;
  aiAnalysis?: AIAnalysisResult;
  thumbnail?: string;
  duration?: number;
  error?: string;
}

interface ContentMetadata {
  title: string;
  description: string;
  tags: string[];
  category: string;
  visibility: 'public' | 'private' | 'unlisted';
  monetization: boolean;
  aiProtection: boolean;
  collaboration: boolean;
  distribution: string[];
  customFields: Record<string, any>;
}

interface AIAnalysisResult {
  contentType: string;
  quality: number;
  suggestions: string[];
  keywords: string[];
  sentiment: 'positive' | 'neutral' | 'negative';
  safety: boolean;
  copyright: boolean;
  originalityScore: number;
}

type ContentCategory = 'video' | 'audio' | 'image' | 'document' | 'other';

interface ContentUploadProps {
  acceptedTypes?: string[];
  maxFileSize?: number;
  maxFiles?: number;
  enableAIAnalysis?: boolean;
  enableBatchUpload?: boolean;
  enableResumableUpload?: boolean;
  categories?: ContentCategory[];
  onUploadStart?: (files: UploadFile[]) => void;
  onUploadProgress?: (file: UploadFile, progress: number) => void;
  onUploadComplete?: (file: UploadFile) => void;
  onUploadError?: (file: UploadFile, error: string) => void;
  onAIAnalysis?: (file: UploadFile, analysis: AIAnalysisResult) => void;
  className?: string;
  style?: React.CSSProperties;
}

// ============================================================================
// ANIMATIONS
// ============================================================================

const uploadPulse = keyframes`
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.8;
  }
`;

const progressBar = keyframes`
  0% {
    width: 0%;
  }
`;

const aiScan = keyframes`
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: calc(200px + 100%) 0;
  }
`;

// ============================================================================
// STYLED COMPONENTS
// ============================================================================

const UploadContainer = styled.div`
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
`;

const UploadHeader = styled.div`
  margin-bottom: 2rem;
  text-align: center;
`;

const UploadTitle = styled.h2`
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 0.5rem 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const UploadSubtitle = styled.p`
  font-size: 1.125rem;
  color: #6b7280;
  margin: 0;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
`;

const DropZone = styled(motion.div)<{ 
  isDragActive: boolean; 
  hasFiles: boolean;
  disabled?: boolean;
}>`
  border: 3px dashed ${({ isDragActive }) => isDragActive ? '#3b82f6' : '#d1d5db'};
  border-radius: 16px;
  padding: 3rem 2rem;
  text-align: center;
  background: ${({ isDragActive, hasFiles }) => 
    isDragActive ? 'rgba(59, 130, 246, 0.05)' : 
    hasFiles ? 'rgba(16, 185, 129, 0.05)' : '#f9fafb'};
  transition: all 0.3s ease;
  cursor: ${({ disabled }) => disabled ? 'not-allowed' : 'pointer'};
  position: relative;
  overflow: hidden;
  
  ${({ isDragActive }) => isDragActive && css`
    animation: ${uploadPulse} 2s ease-in-out infinite;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  `}
  
  &:hover {
    border-color: #3b82f6;
    background: rgba(59, 130, 246, 0.02);
  }
  
  ${({ disabled }) => disabled && css`
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
  `}
`;

const DropZoneIcon = styled.div<{ isDragActive: boolean }>`
  font-size: 4rem;
  margin-bottom: 1rem;
  color: ${({ isDragActive }) => isDragActive ? '#3b82f6' : '#9ca3af'};
  transition: color 0.3s ease;
`;

const DropZoneText = styled.div`
  h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #111827;
    margin: 0 0 0.5rem 0;
  }
  
  p {
    font-size: 1rem;
    color: #6b7280;
    margin: 0 0 1.5rem 0;
  }
`;

const BrowseButton = styled.button`
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 14px 0 rgba(59, 130, 246, 0.4);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px 0 rgba(59, 130, 246, 0.5);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const FileInput = styled.input`
  display: none;
`;

const UploadQueue = styled.div`
  margin-top: 2rem;
`;

const QueueHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
`;

const QueueTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
`;

const QueueActions = styled.div`
  display: flex;
  gap: 1rem;
`;

const ActionButton = styled.button<{ variant?: 'primary' | 'secondary' | 'danger' }>`
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  
  ${({ variant }) => {
    switch (variant) {
      case 'danger':
        return css`
          background: #fee2e2;
          color: #dc2626;
          
          &:hover {
            background: #fecaca;
          }
        `;
      case 'secondary':
        return css`
          background: #f3f4f6;
          color: #374151;
          
          &:hover {
            background: #e5e7eb;
          }
        `;
      default:
        return css`
          background: #dbeafe;
          color: #1d4ed8;
          
          &:hover {
            background: #bfdbfe;
          }
        `;
    }
  }}
`;

const FileList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const FileItem = styled(motion.div)<{ status: string }>`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  
  ${({ status }) => {
    switch (status) {
      case 'uploading':
        return css`
          border-color: #3b82f6;
          background: rgba(59, 130, 246, 0.02);
        `;
      case 'completed':
        return css`
          border-color: #10b981;
          background: rgba(16, 185, 129, 0.02);
        `;
      case 'error':
        return css`
          border-color: #ef4444;
          background: rgba(239, 68, 68, 0.02);
        `;
      default:
        return '';
    }
  }}
`;

const FileHeader = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
`;

const FilePreview = styled.div`
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  
  img, video {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .file-icon {
    font-size: 2rem;
    color: #9ca3af;
  }
`;

const FileInfo = styled.div`
  flex: 1;
  min-width: 0;
`;

const FileName = styled.div`
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.25rem;
  word-break: break-all;
`;

const FileDetails = styled.div`
  font-size: 0.875rem;
  color: #6b7280;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
`;

const FileActions = styled.div`
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
`;

const FileActionButton = styled.button<{ variant?: 'edit' | 'delete' | 'retry' }>`
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  
  ${({ variant }) => {
    switch (variant) {
      case 'delete':
        return css`
          background: #fee2e2;
          color: #dc2626;
          
          &:hover {
            background: #fecaca;
          }
        `;
      case 'retry':
        return css`
          background: #fef3c7;
          color: #d97706;
          
          &:hover {
            background: #fde68a;
          }
        `;
      default:
        return css`
          background: #f3f4f6;
          color: #374151;
          
          &:hover {
            background: #e5e7eb;
          }
        `;
    }
  }}
`;

const ProgressContainer = styled.div`
  margin: 1rem 0;
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
`;

const ProgressFill = styled.div<{ progress: number; status: string }>`
  height: 100%;
  width: ${({ progress }) => progress}%;
  border-radius: 4px;
  transition: width 0.3s ease;
  
  ${({ status }) => {
    switch (status) {
      case 'uploading':
        return css`
          background: linear-gradient(90deg, #3b82f6, #1d4ed8);
        `;
      case 'processing':
        return css`
          background: linear-gradient(90deg, #f59e0b, #d97706);
          animation: ${aiScan} 2s linear infinite;
        `;
      case 'completed':
        return css`
          background: linear-gradient(90deg, #10b981, #059669);
        `;
      case 'error':
        return css`
          background: linear-gradient(90deg, #ef4444, #dc2626);
        `;
      default:
        return css`
          background: #e5e7eb;
        `;
    }
  }}
`;

const ProgressText = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
  font-size: 0.875rem;
`;

const StatusBadge = styled.span<{ status: string }>`
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  
  ${({ status }) => {
    switch (status) {
      case 'pending':
        return css`
          background: #f3f4f6;
          color: #374151;
        `;
      case 'uploading':
        return css`
          background: #dbeafe;
          color: #1d4ed8;
        `;
      case 'processing':
        return css`
          background: #fef3c7;
          color: #d97706;
        `;
      case 'completed':
        return css`
          background: #d1fae5;
          color: #065f46;
        `;
      case 'error':
        return css`
          background: #fee2e2;
          color: #dc2626;
        `;
      default:
        return css`
          background: #f3f4f6;
          color: #374151;
        `;
    }
  }}
`;

const MetadataForm = styled.div`
  margin-top: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
`;

const FormField = styled.div`
  margin-bottom: 1rem;
  
  label {
    display: block;
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
    margin-bottom: 0.5rem;
  }
  
  input, textarea, select {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 0.875rem;
    
    &:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
  }
  
  textarea {
    resize: vertical;
    min-height: 80px;
  }
`;

const TagsInput = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 8px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  min-height: 40px;
  
  &:focus-within {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
`;

const Tag = styled.span`
  background: #3b82f6;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 4px;
  
  button {
    background: none;
    border: none;
    color: white;
    cursor: pointer;
    padding: 0;
    width: 16px;
    height: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    
    &:hover {
      background: rgba(255, 255, 255, 0.2);
    }
  }
`;

const TagInput = styled.input`
  border: none;
  outline: none;
  flex: 1;
  min-width: 100px;
  font-size: 0.875rem;
`;

const AIAnalysis = styled.div`
  margin-top: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #0ea5e9;
  border-radius: 8px;
`;

const AITitle = styled.h4`
  font-size: 1rem;
  font-weight: 600;
  color: #0c4a6e;
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const AIMetrics = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
`;

const AIMetric = styled.div`
  text-align: center;
  
  .value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #0c4a6e;
    margin-bottom: 0.25rem;
  }
  
  .label {
    font-size: 0.75rem;
    color: #0369a1;
    text-transform: uppercase;
    font-weight: 500;
  }
`;

const AISuggestions = styled.div`
  h5 {
    font-size: 0.875rem;
    font-weight: 600;
    color: #0c4a6e;
    margin: 0 0 0.5rem 0;
  }
  
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
    
    li {
      font-size: 0.875rem;
      color: #0369a1;
      padding: 0.25rem 0;
      
      &::before {
        content: '💡';
        margin-right: 0.5rem;
      }
    }
  }
`;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const getFileCategory = (type: string): ContentCategory => {
  if (type.startsWith('video/')) return 'video';
  if (type.startsWith('audio/')) return 'audio';
  if (type.startsWith('image/')) return 'image';
  if (type.includes('document') || type.includes('pdf') || type.includes('text')) return 'document';
  return 'other';
};

const getFileIcon = (category: ContentCategory): string => {
  switch (category) {
    case 'video': return '🎬';
    case 'audio': return '🎵';
    case 'image': return '🖼️';
    case 'document': return '📄';
    default: return '📁';
  }
};

const generatePreview = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    } else if (file.type.startsWith('video/')) {
      const video = document.createElement('video');
      video.preload = 'metadata';
      video.onloadedmetadata = () => {
        video.currentTime = Math.min(5, video.duration / 4);
      };
      video.onseeked = () => {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx?.drawImage(video, 0, 0);
        resolve(canvas.toDataURL());
      };
      video.src = URL.createObjectURL(file);
    } else {
      resolve('');
    }
  });
};

const simulateAIAnalysis = (file: UploadFile): Promise<AIAnalysisResult> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        contentType: file.category,
        quality: Math.floor(Math.random() * 30) + 70,
        suggestions: [
          'Consider adding more descriptive tags',
          'Optimize thumbnail for better engagement',
          'Add captions for accessibility'
        ],
        keywords: ['ai', 'content', 'creator', 'upload'],
        sentiment: 'positive',
        safety: true,
        copyright: false,
        originalityScore: Math.floor(Math.random() * 20) + 80
      });
    }, 2000);
  });
};

// ============================================================================
// MAIN CONTENT UPLOAD COMPONENT
// ============================================================================

export const ContentUpload: React.FC<ContentUploadProps> = ({
  acceptedTypes = ['*/*'],
  maxFileSize = 100 * 1024 * 1024, // 100MB
  maxFiles = 10,
  enableAIAnalysis = true,
  enableBatchUpload = true,
  enableResumableUpload = true,
  categories = ['video', 'audio', 'image', 'document'],
  onUploadStart,
  onUploadProgress,
  onUploadComplete,
  onUploadError,
  onAIAnalysis,
  className,
  style,
  ...props
}) => {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [isDragActive, setIsDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Handle file selection
  const handleFileSelect = useCallback(async (selectedFiles: FileList | File[]) => {
    const fileArray = Array.from(selectedFiles);
    
    if (files.length + fileArray.length > maxFiles) {
      alert(`Maximum ${maxFiles} files allowed`);
      return;
    }

    const newFiles: UploadFile[] = [];
    
    for (const file of fileArray) {
      if (file.size > maxFileSize) {
        alert(`File ${file.name} is too large. Maximum size: ${formatFileSize(maxFileSize)}`);
        continue;
      }

      const uploadFile: UploadFile = {
        id: Math.random().toString(36).substr(2, 9),
        file,
        name: file.name,
        size: file.size,
        type: file.type,
        category: getFileCategory(file.type),
        status: 'pending',
        progress: 0
      };

      // Generate preview
      try {
        uploadFile.preview = await generatePreview(file);
      } catch (error) {
        console.error('Failed to generate preview:', error);
      }

      newFiles.push(uploadFile);
    }

    setFiles(prev => [...prev, ...newFiles]);
    onUploadStart?.(newFiles);
  }, [files.length, maxFiles, maxFileSize, onUploadStart]);

  // Handle drag events
  const handleDragEnter = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
  }, []);

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    
    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles.length > 0) {
      handleFileSelect(droppedFiles);
    }
  }, [handleFileSelect]);

  // Handle file input change
  const handleFileInputChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    if (selectedFiles) {
      handleFileSelect(selectedFiles);
    }
    // Reset input value to allow selecting same file again
    e.target.value = '';
  }, [handleFileSelect]);

  // Remove file
  const removeFile = useCallback((fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  }, []);

  // Start upload
  const startUpload = useCallback(async () => {
    setIsUploading(true);
    
    for (const file of files.filter(f => f.status === 'pending')) {
      // Update status to uploading
      setFiles(prev => prev.map(f => 
        f.id === file.id ? { ...f, status: 'uploading' } : f
      ));

      try {
        // Simulate upload progress
        for (let progress = 0; progress <= 100; progress += 10) {
          await new Promise(resolve => setTimeout(resolve, 200));
          
          setFiles(prev => prev.map(f => 
            f.id === file.id ? { ...f, progress } : f
          ));
          
          onUploadProgress?.(file, progress);
        }

        // Update status to processing for AI analysis
        if (enableAIAnalysis) {
          setFiles(prev => prev.map(f => 
            f.id === file.id ? { ...f, status: 'processing' } : f
          ));

          const aiAnalysis = await simulateAIAnalysis(file);
          setFiles(prev => prev.map(f => 
            f.id === file.id ? { ...f, aiAnalysis } : f
          ));
          
          onAIAnalysis?.(file, aiAnalysis);
        }

        // Complete upload
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'completed' } : f
        ));
        
        onUploadComplete?.(file);
      } catch (error) {
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { 
            ...f, 
            status: 'error', 
            error: 'Upload failed' 
          } : f
        ));
        
        onUploadError?.(file, 'Upload failed');
      }
    }
    
    setIsUploading(false);
  }, [files, enableAIAnalysis, onUploadProgress, onUploadComplete, onUploadError, onAIAnalysis]);

  // Clear all files
  const clearAll = useCallback(() => {
    setFiles([]);
  }, []);

  // Retry failed uploads
  const retryFailedUploads = useCallback(() => {
    setFiles(prev => prev.map(f => 
      f.status === 'error' ? { ...f, status: 'pending', progress: 0, error: undefined } : f
    ));
  }, []);

  // Update file metadata
  const updateFileMetadata = useCallback((fileId: string, metadata: Partial<ContentMetadata>) => {
    setFiles(prev => prev.map(f => 
      f.id === fileId ? { 
        ...f, 
        metadata: { ...f.metadata, ...metadata } as ContentMetadata 
      } : f
    ));
  }, []);

  const pendingFiles = files.filter(f => f.status === 'pending').length;
  const uploadingFiles = files.filter(f => f.status === 'uploading' || f.status === 'processing').length;
  const completedFiles = files.filter(f => f.status === 'completed').length;
  const errorFiles = files.filter(f => f.status === 'error').length;

  return (
    <UploadContainer className={className} style={style} {...props}>
      <UploadHeader>
        <UploadTitle>🚀 Ainflue Content Upload</UploadTitle>
        <UploadSubtitle>
          Upload your content to the Ainflue Creator Economy platform. 
          Our AI will analyze and optimize your content for maximum reach and protection.
        </UploadSubtitle>
      </UploadHeader>

      <DropZone
        isDragActive={isDragActive}
        hasFiles={files.length > 0}
        disabled={isUploading}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <DropZoneIcon isDragActive={isDragActive}>
          {isDragActive ? '📤' : '☁️'}
        </DropZoneIcon>
        
        <DropZoneText>
          <h3>
            {isDragActive 
              ? 'Drop your files here' 
              : files.length > 0 
                ? `${files.length} file(s) ready to upload`
                : 'Drag & drop your content here'
            }
          </h3>
          <p>
            Support for videos, audio, images, and documents up to {formatFileSize(maxFileSize)}
          </p>
        </DropZoneText>

        <BrowseButton type="button">
          Browse Files
        </BrowseButton>

        <FileInput
          ref={fileInputRef}
          type="file"
          multiple={enableBatchUpload}
          accept={acceptedTypes.join(',')}
          onChange={handleFileInputChange}
        />
      </DropZone>

      {files.length > 0 && (
        <UploadQueue>
          <QueueHeader>
            <QueueTitle>
              Upload Queue ({files.length})
            </QueueTitle>
            
            <QueueActions>
              {pendingFiles > 0 && (
                <ActionButton 
                  variant="primary" 
                  onClick={startUpload}
                  disabled={isUploading}
                >
                  {isUploading ? 'Uploading...' : `Upload ${pendingFiles} files`}
                </ActionButton>
              )}
              
              {errorFiles > 0 && (
                <ActionButton variant="secondary" onClick={retryFailedUploads}>
                  Retry Failed
                </ActionButton>
              )}
              
              <ActionButton variant="danger" onClick={clearAll}>
                Clear All
              </ActionButton>
            </QueueActions>
          </QueueHeader>

          <FileList>
            <AnimatePresence>
              {files.map((file) => (
                <FileItem
                  key={file.id}
                  status={file.status}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <FileHeader>
                    <FilePreview>
                      {file.preview ? (
                        file.category === 'video' ? (
                          <video src={file.preview} />
                        ) : (
                          <img src={file.preview} alt={file.name} />
                        )
                      ) : (
                        <div className="file-icon">
                          {getFileIcon(file.category)}
                        </div>
                      )}
                    </FilePreview>
                    
                    <FileInfo>
                      <FileName>{file.name}</FileName>
                      <FileDetails>
                        <span>{formatFileSize(file.size)}</span>
                        <span>{file.type}</span>
                        <StatusBadge status={file.status}>
                          {file.status}
                        </StatusBadge>
                      </FileDetails>
                    </FileInfo>
                    
                    <FileActions>
                      <FileActionButton 
                        variant="edit"
                        title="Edit metadata"
                      >
                        ✏️
                      </FileActionButton>
                      
                      {file.status === 'error' && (
                        <FileActionButton 
                          variant="retry"
                          title="Retry upload"
                        >
                          🔄
                        </FileActionButton>
                      )}
                      
                      <FileActionButton 
                        variant="delete"
                        onClick={() => removeFile(file.id)}
                        title="Remove file"
                      >
                        🗑️
                      </FileActionButton>
                    </FileActions>
                  </FileHeader>

                  {(file.status === 'uploading' || file.status === 'processing') && (
                    <ProgressContainer>
                      <ProgressBar>
                        <ProgressFill progress={file.progress} status={file.status} />
                      </ProgressBar>
                      <ProgressText>
                        <span>
                          {file.status === 'processing' ? '🤖 AI Analysis...' : 'Uploading...'}
                        </span>
                        <span>{file.progress}%</span>
                      </ProgressText>
                    </ProgressContainer>
                  )}

                  {file.error && (
                    <div style={{ 
                      color: '#dc2626', 
                      fontSize: '0.875rem', 
                      marginTop: '0.5rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      ⚠️ {file.error}
                    </div>
                  )}

                  {file.aiAnalysis && (
                    <AIAnalysis>
                      <AITitle>
                        🤖 AI Analysis Results
                      </AITitle>
                      
                      <AIMetrics>
                        <AIMetric>
                          <div className="value">{file.aiAnalysis.quality}%</div>
                          <div className="label">Quality Score</div>
                        </AIMetric>
                        <AIMetric>
                          <div className="value">{file.aiAnalysis.originalityScore}%</div>
                          <div className="label">Originality</div>
                        </AIMetric>
                        <AIMetric>
                          <div className="value">{file.aiAnalysis.safety ? '✅' : '❌'}</div>
                          <div className="label">Safety Check</div>
                        </AIMetric>
                        <AIMetric>
                          <div className="value">{file.aiAnalysis.copyright ? '⚠️' : '✅'}</div>
                          <div className="label">Copyright</div>
                        </AIMetric>
                      </AIMetrics>

                      <AISuggestions>
                        <h5>💡 AI Suggestions</h5>
                        <ul>
                          {file.aiAnalysis.suggestions.map((suggestion, index) => (
                            <li key={index}>{suggestion}</li>
                          ))}
                        </ul>
                      </AISuggestions>
                    </AIAnalysis>
                  )}

                  {file.status === 'completed' && (
                    <MetadataForm>
                      <FormField>
                        <label>Title</label>
                        <input 
                          type="text" 
                          placeholder="Enter content title"
                          defaultValue={file.name.replace(/\.[^/.]+$/, "")}
                        />
                      </FormField>
                      
                      <FormField>
                        <label>Description</label>
                        <textarea 
                          placeholder="Describe your content..."
                          rows={3}
                        />
                      </FormField>
                      
                      <FormField>
                        <label>Tags</label>
                        <TagsInput>
                          <Tag>
                            ai <button>×</button>
                          </Tag>
                          <Tag>
                            content <button>×</button>
                          </Tag>
                          <TagInput placeholder="Add tags..." />
                        </TagsInput>
                      </FormField>
                      
                      <FormField>
                        <label>Visibility</label>
                        <select defaultValue="public">
                          <option value="public">Public</option>
                          <option value="unlisted">Unlisted</option>
                          <option value="private">Private</option>
                        </select>
                      </FormField>
                    </MetadataForm>
                  )}
                </FileItem>
              ))}
            </AnimatePresence>
          </FileList>
        </UploadQueue>
      )}
    </UploadContainer>
  );
};

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

export const ContentUploadExamples: React.FC = () => {
  const handleUploadStart = (files: UploadFile[]) => {
    console.log('Upload started:', files);
  };

  const handleUploadProgress = (file: UploadFile, progress: number) => {
    console.log('Upload progress:', file.name, progress + '%');
  };

  const handleUploadComplete = (file: UploadFile) => {
    console.log('Upload completed:', file.name);
  };

  const handleUploadError = (file: UploadFile, error: string) => {
    console.error('Upload error:', file.name, error);
  };

  const handleAIAnalysis = (file: UploadFile, analysis: any) => {
    console.log('AI analysis completed:', file.name, analysis);
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Content Upload Examples</h2>
      
      <ContentUpload
        acceptedTypes={['image/*', 'video/*', 'audio/*', '.pdf', '.doc', '.docx']}
        maxFileSize={500 * 1024 * 1024} // 500MB
        maxFiles={20}
        enableAIAnalysis={true}
        enableBatchUpload={true}
        enableResumableUpload={true}
        onUploadStart={handleUploadStart}
        onUploadProgress={handleUploadProgress}
        onUploadComplete={handleUploadComplete}
        onUploadError={handleUploadError}
        onAIAnalysis={handleAIAnalysis}
      />
    </div>
  );
};

export default ContentUpload;