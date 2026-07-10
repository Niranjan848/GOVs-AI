import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { User, AuthResponse } from '../types';
import { authAPI } from '../lib/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Restore session from localStorage
    const savedToken = localStorage.getItem('govsai_token');
    const savedUser = localStorage.getItem('govsai_user');
    if (savedToken && savedUser) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem('govsai_token');
        localStorage.removeItem('govsai_user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const { data } = await authAPI.login(email, password);
    const authData = data as AuthResponse;
    setToken(authData.access_token);
    setUser(authData.user);
    localStorage.setItem('govsai_token', authData.access_token);
    localStorage.setItem('govsai_user', JSON.stringify(authData.user));
  };

  const signup = async (email: string, password: string, name: string) => {
    const { data } = await authAPI.signup(email, password, name);
    const authData = data as AuthResponse;
    setToken(authData.access_token);
    setUser(authData.user);
    localStorage.setItem('govsai_token', authData.access_token);
    localStorage.setItem('govsai_user', JSON.stringify(authData.user));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('govsai_token');
    localStorage.removeItem('govsai_user');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        isAuthenticated: !!token && !!user,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
