/**
 * Media Slice - Redux state management for media content
 * 
 * Manages media files, upload state, processing status, and metadata
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

export interface MediaFile {
  id: string;
  name: string;
  originalName: string;
  size: number;
  type: string;
  mimeType: string;
  url?: string;
  thumbnailUrl?: string;
  previewUrl?: string;
  status: 'uploading' | 'processing' | 'ready' | 'error' | 'deleted';
  progress: number;
  metadata: {
    duration?: number;
    dimensions?: { width: number; height: number };
    bitrate?: number;
    codec?: string;
    format?: string;
    quality?: string;
    colorProfile?: string;
    frameRate?: number;
    sampleRate?: number;
    channels?: number;
  };
  protection: {
    enabled: boolean;
    level: 'basic' | 'advanced' | 'premium';
    fingerprints: string[];
    watermark: boolean;
    drm: boolean;
  };
  distribution: {
    platforms: string[];
    scheduled: boolean;
    publishAt?: Date;
    autoDistribute: boolean;
  };
  analytics: {
    views: number;
    downloads: number;
    shares: number;
    engagement: number;
    revenue: number;
  };
  tags: string[];
  description?: string;
  category?: string;
  visibility: 'public' | 'private' | 'unlisted';
  createdAt: Date;
  updatedAt: Date;
  uploadedBy: string;
  folder?: string;
}

export interface UploadProgress {
  fileId: string;
  fileName: string;
  progress: number;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
  estimatedTimeRemaining?: number;
  uploadSpeed?: number;
}

export interface MediaFilter {
  type?: string[];
  status?: string[];
  category?: string;
  tags?: string[];
  dateRange?: {
    start: Date;
    end: Date;
  };
  sizeRange?: {
    min: number;
    max: number;
  };
  sortBy: 'name' | 'date' | 'size' | 'views' | 'engagement';
  sortOrder: 'asc' | 'desc';
  search?: string;
}

export interface MediaState {
  files: MediaFile[];
  uploads: UploadProgress[];
  loading: boolean;
  error: string | null;
  filters: MediaFilter;
  selectedFiles: string[];
  totalFiles: number;
  totalSize: number;
  storageUsed: number;
  storageLimit: number;
  currentPage: number;
  itemsPerPage: number;
  view: 'grid' | 'list';
  bulkOperations: {
    active: boolean;
    operation?: 'delete' | 'move' | 'protect' | 'distribute';
    progress: number;
  };
}

const initialState: MediaState = {
  files: [],
  uploads: [],
  loading: false,
  error: null,
  filters: {
    sortBy: 'date',
    sortOrder: 'desc'
  },
  selectedFiles: [],
  totalFiles: 0,
  totalSize: 0,
  storageUsed: 0,
  storageLimit: 1024 * 1024 * 1024 * 100, // 100GB default
  currentPage: 1,
  itemsPerPage: 20,
  view: 'grid',
  bulkOperations: {
    active: false,
    progress: 0
  }
};

// Async thunks for API calls
export const uploadFiles = createAsyncThunk(
  'media/uploadFiles',
  async (files: File[], { dispatch }) => {
    const uploadPromises = files.map(async (file) => {
      const fileId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      
      // Initialize upload progress
      dispatch(addUploadProgress({
        fileId,
        fileName: file.name,
        progress: 0,
        status: 'pending'
      }));

      try {
        // Simulate file upload with progress updates
        for (let progress = 0; progress <= 100; progress += 10) {
          await new Promise(resolve => setTimeout(resolve, 200));
          dispatch(updateUploadProgress({ fileId, progress, status: 'uploading' }));
        }

        // Create media file object
        const mediaFile: MediaFile = {
          id: fileId,
          name: file.name.split('.')[0],
          originalName: file.name,
          size: file.size,
          type: file.type.split('/')[0],
          mimeType: file.type,
          status: 'ready',
          progress: 100,
          metadata: {
            format: file.type.split('/')[1]
          },
          protection: {
            enabled: false,
            level: 'basic',
            fingerprints: [],
            watermark: false,
            drm: false
          },
          distribution: {
            platforms: [],
            scheduled: false,
            autoDistribute: false
          },
          analytics: {
            views: 0,
            downloads: 0,
            shares: 0,
            engagement: 0,
            revenue: 0
          },
          tags: [],
          visibility: 'private',
          createdAt: new Date(),
          updatedAt: new Date(),
          uploadedBy: 'current-user'
        };

        dispatch(updateUploadProgress({ fileId, progress: 100, status: 'completed' }));
        return mediaFile;
      } catch (error) {
        dispatch(updateUploadProgress({ 
          fileId, 
          status: 'error', 
          error: error instanceof Error ? error.message : 'Upload failed' 
        }));
        throw error;
      }
    });

    return Promise.all(uploadPromises);
  }
);

export const deleteFiles = createAsyncThunk(
  'media/deleteFiles',
  async (fileIds: string[]) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    return fileIds;
  }
);

export const updateFileMetadata = createAsyncThunk(
  'media/updateFileMetadata',
  async ({ fileId, metadata }: { fileId: string; metadata: Partial<MediaFile> }) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500));
    return { fileId, metadata };
  }
);

export const enableProtection = createAsyncThunk(
  'media/enableProtection',
  async ({ fileId, level }: { fileId: string; level: 'basic' | 'advanced' | 'premium' }) => {
    // Simulate API call for protection setup
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const fingerprints = ['audio-fp-' + Math.random().toString(36), 'visual-fp-' + Math.random().toString(36)];
    
    return {
      fileId,
      protection: {
        enabled: true,
        level,
        fingerprints,
        watermark: level !== 'basic',
        drm: level === 'premium'
      }
    };
  }
);

export const distributeToPlattforms = createAsyncThunk(
  'media/distributeToPlattforms',
  async ({ fileId, platforms }: { fileId: string; platforms: string[] }) => {
    // Simulate API call for content distribution
    await new Promise(resolve => setTimeout(resolve, 2000));
    return { fileId, platforms };
  }
);

const mediaSlice = createSlice({
  name: 'media',
  initialState,
  reducers: {
    // Upload management
    addUploadProgress: (state, action: PayloadAction<UploadProgress>) => {
      state.uploads.push(action.payload);
    },
    updateUploadProgress: (state, action: PayloadAction<Partial<UploadProgress> & { fileId: string }>) => {
      const upload = state.uploads.find(u => u.fileId === action.payload.fileId);
      if (upload) {
        Object.assign(upload, action.payload);
      }
    },
    removeUploadProgress: (state, action: PayloadAction<string>) => {
      state.uploads = state.uploads.filter(u => u.fileId !== action.payload);
    },
    clearCompletedUploads: (state) => {
      state.uploads = state.uploads.filter(u => u.status !== 'completed');
    },

    // File selection
    selectFile: (state, action: PayloadAction<string>) => {
      if (!state.selectedFiles.includes(action.payload)) {
        state.selectedFiles.push(action.payload);
      }
    },
    deselectFile: (state, action: PayloadAction<string>) => {
      state.selectedFiles = state.selectedFiles.filter(id => id !== action.payload);
    },
    selectAllFiles: (state) => {
      state.selectedFiles = state.files.map(f => f.id);
    },
    clearSelection: (state) => {
      state.selectedFiles = [];
    },

    // Filtering and sorting
    updateFilters: (state, action: PayloadAction<Partial<MediaFilter>>) => {
      state.filters = { ...state.filters, ...action.payload };
      state.currentPage = 1; // Reset to first page when filters change
    },
    clearFilters: (state) => {
      state.filters = {
        sortBy: 'date',
        sortOrder: 'desc'
      };
      state.currentPage = 1;
    },

    // View management
    setView: (state, action: PayloadAction<'grid' | 'list'>) => {
      state.view = action.payload;
    },
    setPage: (state, action: PayloadAction<number>) => {
      state.currentPage = action.payload;
    },
    setItemsPerPage: (state, action: PayloadAction<number>) => {
      state.itemsPerPage = action.payload;
      state.currentPage = 1;
    },

    // Bulk operations
    startBulkOperation: (state, action: PayloadAction<'delete' | 'move' | 'protect' | 'distribute'>) => {
      state.bulkOperations = {
        active: true,
        operation: action.payload,
        progress: 0
      };
    },
    updateBulkProgress: (state, action: PayloadAction<number>) => {
      state.bulkOperations.progress = action.payload;
    },
    completeBulkOperation: (state) => {
      state.bulkOperations = {
        active: false,
        progress: 0
      };
      state.selectedFiles = [];
    },

    // File management
    addFiles: (state, action: PayloadAction<MediaFile[]>) => {
      state.files.unshift(...action.payload);
      state.totalFiles += action.payload.length;
      state.totalSize += action.payload.reduce((sum, file) => sum + file.size, 0);
      state.storageUsed += action.payload.reduce((sum, file) => sum + file.size, 0);
    },
    updateFile: (state, action: PayloadAction<{ id: string; updates: Partial<MediaFile> }>) => {
      const file = state.files.find(f => f.id === action.payload.id);
      if (file) {
        Object.assign(file, action.payload.updates);
        file.updatedAt = new Date();
      }
    },
    removeFiles: (state, action: PayloadAction<string[]>) => {
      const removedFiles = state.files.filter(f => action.payload.includes(f.id));
      const removedSize = removedFiles.reduce((sum, file) => sum + file.size, 0);
      
      state.files = state.files.filter(f => !action.payload.includes(f.id));
      state.totalFiles -= removedFiles.length;
      state.totalSize -= removedSize;
      state.storageUsed -= removedSize;
      state.selectedFiles = state.selectedFiles.filter(id => !action.payload.includes(id));
    },

    // Error handling
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Upload files
      .addCase(uploadFiles.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(uploadFiles.fulfilled, (state, action) => {
        state.loading = false;
        state.files.unshift(...action.payload);
        state.totalFiles += action.payload.length;
        state.totalSize += action.payload.reduce((sum, file) => sum + file.size, 0);
        state.storageUsed += action.payload.reduce((sum, file) => sum + file.size, 0);
        
        // Clean up upload progress for completed uploads
        const completedFileIds = action.payload.map(f => f.id);
        state.uploads = state.uploads.filter(u => !completedFileIds.includes(u.fileId));
      })
      .addCase(uploadFiles.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Upload failed';
      })

      // Delete files
      .addCase(deleteFiles.pending, (state) => {
        state.loading = true;
      })
      .addCase(deleteFiles.fulfilled, (state, action) => {
        state.loading = false;
        const removedFiles = state.files.filter(f => action.payload.includes(f.id));
        const removedSize = removedFiles.reduce((sum, file) => sum + file.size, 0);
        
        state.files = state.files.filter(f => !action.payload.includes(f.id));
        state.totalFiles -= removedFiles.length;
        state.totalSize -= removedSize;
        state.storageUsed -= removedSize;
        state.selectedFiles = state.selectedFiles.filter(id => !action.payload.includes(id));
      })
      .addCase(deleteFiles.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Delete failed';
      })

      // Update metadata
      .addCase(updateFileMetadata.fulfilled, (state, action) => {
        const file = state.files.find(f => f.id === action.payload.fileId);
        if (file) {
          Object.assign(file, action.payload.metadata);
          file.updatedAt = new Date();
        }
      })

      // Enable protection
      .addCase(enableProtection.fulfilled, (state, action) => {
        const file = state.files.find(f => f.id === action.payload.fileId);
        if (file) {
          file.protection = action.payload.protection;
          file.updatedAt = new Date();
        }
      })

      // Distribute to platforms
      .addCase(distributeToPlattforms.fulfilled, (state, action) => {
        const file = state.files.find(f => f.id === action.payload.fileId);
        if (file) {
          file.distribution.platforms = action.payload.platforms;
          file.updatedAt = new Date();
        }
      });
  }
});

export const {
  addUploadProgress,
  updateUploadProgress,
  removeUploadProgress,
  clearCompletedUploads,
  selectFile,
  deselectFile,
  selectAllFiles,
  clearSelection,
  updateFilters,
  clearFilters,
  setView,
  setPage,
  setItemsPerPage,
  startBulkOperation,
  updateBulkProgress,
  completeBulkOperation,
  addFiles,
  updateFile,
  removeFiles,
  setError,
  clearError
} = mediaSlice.actions;

// Selectors
export const selectAllMediaFiles = (state: { media: MediaState }) => state.media.files;
export const selectSelectedFiles = (state: { media: MediaState }) => state.media.selectedFiles;
export const selectMediaFilters = (state: { media: MediaState }) => state.media.filters;
export const selectUploadProgress = (state: { media: MediaState }) => state.media.uploads;
export const selectStorageInfo = (state: { media: MediaState }) => ({
  used: state.media.storageUsed,
  limit: state.media.storageLimit,
  percentage: (state.media.storageUsed / state.media.storageLimit) * 100
});
export const selectIsLoading = (state: { media: MediaState }) => state.media.loading;
export const selectError = (state: { media: MediaState }) => state.media.error;

// Filtered files selector
export const selectFilteredFiles = (state: { media: MediaState }) => {
  const { files, filters } = state.media;
  let filtered = [...files];

  // Apply filters
  if (filters.type?.length) {
    filtered = filtered.filter(file => filters.type!.includes(file.type));
  }
  
  if (filters.status?.length) {
    filtered = filtered.filter(file => filters.status!.includes(file.status));
  }

  if (filters.category) {
    filtered = filtered.filter(file => file.category === filters.category);
  }

  if (filters.tags?.length) {
    filtered = filtered.filter(file => 
      filters.tags!.some(tag => file.tags.includes(tag))
    );
  }

  if (filters.search) {
    const searchLower = filters.search.toLowerCase();
    filtered = filtered.filter(file => 
      file.name.toLowerCase().includes(searchLower) ||
      file.originalName.toLowerCase().includes(searchLower) ||
      file.description?.toLowerCase().includes(searchLower) ||
      file.tags.some(tag => tag.toLowerCase().includes(searchLower))
    );
  }

  if (filters.dateRange) {
    filtered = filtered.filter(file => 
      file.createdAt >= filters.dateRange!.start &&
      file.createdAt <= filters.dateRange!.end
    );
  }

  if (filters.sizeRange) {
    filtered = filtered.filter(file => 
      file.size >= filters.sizeRange!.min &&
      file.size <= filters.sizeRange!.max
    );
  }

  // Apply sorting
  filtered.sort((a, b) => {
    let aValue: any;
    let bValue: any;

    switch (filters.sortBy) {
      case 'name':
        aValue = a.name.toLowerCase();
        bValue = b.name.toLowerCase();
        break;
      case 'date':
        aValue = a.createdAt.getTime();
        bValue = b.createdAt.getTime();
        break;
      case 'size':
        aValue = a.size;
        bValue = b.size;
        break;
      case 'views':
        aValue = a.analytics.views;
        bValue = b.analytics.views;
        break;
      case 'engagement':
        aValue = a.analytics.engagement;
        bValue = b.analytics.engagement;
        break;
      default:
        aValue = a.createdAt.getTime();
        bValue = b.createdAt.getTime();
    }

    if (filters.sortOrder === 'asc') {
      return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
    } else {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
    }
  });

  return filtered;
};

export default mediaSlice.reducer;