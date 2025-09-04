/**
 * Protection Hook - Custom hook for content protection management
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { useState, useEffect, useCallback } from 'react';
import { api } from '../utils/api';

interface ProtectionData {
  fingerprints: Array<{
    id: string;
    contentId: string;
    hash: string;
    status: 'active' | 'inactive';
    created: string;
  }>;
  violations: Array<{
    id: string;
    contentId: string;
    platform: string;
    status: 'detected' | 'reported' | 'resolved';
    severity: 'low' | 'medium' | 'high';
    timestamp: string;
  }>;
}

export const useProtection = () => {
  const [data, setData] = useState<ProtectionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProtectionData = useCallback(async () => {
    try {
      setLoading(true);
      const [fingerprints, violations] = await Promise.all([
        api.protection.getFingerprints(),
        api.protection.getViolations(),
      ]);

      setData({
        fingerprints: fingerprints.data,
        violations: violations.data,
      });
      setError(null);
    } catch (err) {
      setError('Failed to fetch protection data');
      console.error('Protection error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const reportViolation = useCallback(async (violationData: Record<string, unknown>) => {
    try {
      await api.protection.reportViolation(violationData);
      await fetchProtectionData(); // Refresh data
    } catch (err) {
      console.error('Report violation error:', err);
      throw err;
    }
  }, [fetchProtectionData]);

  const sendDMCA = useCallback(async (violationId: string) => {
    try {
      await api.protection.sendDMCA(violationId);
      await fetchProtectionData(); // Refresh data
    } catch (err) {
      console.error('DMCA error:', err);
      throw err;
    }
  }, [fetchProtectionData]);

  useEffect(() => {
    fetchProtectionData();
  }, [fetchProtectionData]);

  return {
    data,
    loading,
    error,
    refetch: fetchProtectionData,
    reportViolation,
    sendDMCA,
  };
};

export default useProtection;