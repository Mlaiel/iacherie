import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'volunteer' | 'medcare' | 'user';
  avatar?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string, role: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Charger le token depuis localStorage au démarrage
  useEffect(() => {
    const storedToken = localStorage.getItem('ia2good_token');
    const storedUser = localStorage.getItem('ia2good_user');

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }

    setIsLoading(false);
  }, []);

  // Auto-refresh token toutes les 15 minutes
  useEffect(() => {
    if (!token) return;

    const interval = setInterval(() => {
      refreshToken().catch((error) => {
        console.error('Token refresh failed:', error);
        logout();
      });
    }, 15 * 60 * 1000); // 15 minutes

    return () => clearInterval(interval);
  }, [token]);

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/ia2good/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Échec de connexion');
      }

      const data = await response.json();

      // Stocker token et user
      localStorage.setItem('ia2good_token', data.access_token);
      localStorage.setItem('ia2good_user', JSON.stringify(data.user));

      setToken(data.access_token);
      setUser(data.user);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const register = async (email: string, password: string, name: string, role: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/ia2good/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, name, role }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Échec de création de compte');
      }

      const data = await response.json();

      // Stocker token et user
      localStorage.setItem('ia2good_token', data.access_token);
      localStorage.setItem('ia2good_user', JSON.stringify(data.user));

      setToken(data.access_token);
      setUser(data.user);
    } catch (error) {
      console.error('Register error:', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('ia2good_token');
    localStorage.removeItem('ia2good_user');
    setToken(null);
    setUser(null);
  };

  const refreshToken = async () => {
    if (!token) return;

    try {
      const response = await fetch('http://localhost:8000/api/v1/ia2good/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();

      localStorage.setItem('ia2good_token', data.access_token);
      setToken(data.access_token);
    } catch (error) {
      console.error('Refresh token error:', error);
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    isLoading,
    login,
    register,
    logout,
    refreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
