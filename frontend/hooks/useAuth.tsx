'use client';

import { useAppContext } from '@/app/providers';
import { useCallback } from 'react';

export function useAuth() {
  const { state, login, logout } = useAppContext();

  const isAuthenticated = state.isAuthenticated;
  const user = state.user;
  const isLoading = state.isLoading;

  const handleLogin = useCallback(async (email: string, password: string) => {
    return await login(email, password);
  }, [login]);

  const handleLogout = useCallback(() => {
    logout();
  }, [logout]);

  return {
    user,
    isAuthenticated,
    isLoading,
    login: handleLogin,
    logout: handleLogout,
  };
}