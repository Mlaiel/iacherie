'use client';

import { useAppContext } from '@/app/providers';
import { useCallback, useEffect } from 'react';

export function useContent() {
  const { state, uploadContent, deleteContent, refreshMetrics } = useAppContext();

  const content = state.content;
  const metrics = state.metrics;
  const isLoading = state.isLoading;

  const handleUpload = useCallback(async (files: File[]) => {
    await uploadContent(files);
  }, [uploadContent]);

  const handleDelete = useCallback(async (contentId: string) => {
    await deleteContent(contentId);
  }, [deleteContent]);

  const handleRefreshMetrics = useCallback(async () => {
    await refreshMetrics();
  }, [refreshMetrics]);

  // Auto-refresh metrics on mount
  useEffect(() => {
    handleRefreshMetrics();
  }, [handleRefreshMetrics]);

  return {
    content,
    metrics,
    isLoading,
    uploadContent: handleUpload,
    deleteContent: handleDelete,
    refreshMetrics: handleRefreshMetrics,
  };
}