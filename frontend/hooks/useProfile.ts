import { useState, useEffect, useCallback } from 'react';
import { api } from '../utils/api';

export const useProfile = () => {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchProfile = useCallback(async () => {
    try {
      const response = await api.user.getProfile();
      setProfile(response.data);
    } catch (error) {
      console.error('Profile error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateProfile = useCallback(async (updates: Record<string, any>) => {
    try {
      await api.user.updateProfile(updates);
      setProfile((prev: any) => ({ ...prev, ...updates }));
    } catch (error) {
      console.error('Update profile error:', error);
      throw error;
    }
  }, []);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  return { profile, loading, updateProfile, refetch: fetchProfile };
};
