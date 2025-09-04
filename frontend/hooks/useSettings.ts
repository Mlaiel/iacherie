import { useState, useEffect, useCallback } from 'react';
import { api } from '../utils/api';

export const useSettings = () => {
  const [settings, setSettings] = useState<Record<string, any> | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchSettings = useCallback(async () => {
    try {
      const response = await api.user.getSettings();
      setSettings(response.data);
    } catch (error) {
      console.error('Settings error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateSettings = useCallback(async (newSettings: Record<string, any>) => {
    try {
      await api.user.updateSettings(newSettings);
      setSettings(prev => ({ ...prev, ...newSettings }));
    } catch (error) {
      console.error('Update settings error:', error);
      throw error;
    }
  }, []);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  return { settings, loading, updateSettings, refetch: fetchSettings };
};
