import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('traceguard_token') || null);
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('traceguard_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [activeWorkspace, setActiveWorkspace] = useState(() => localStorage.getItem('traceguard_workspace_id') || 'default-workspace');
  const [workspaces, setWorkspaces] = useState([]);
  const [loading, setLoading] = useState(true);

  // Initialize and load user profile if token exists
  useEffect(() => {
    async function loadUser() {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const profile = await api.getMe();
        setUser(profile);
        localStorage.setItem('traceguard_user', JSON.stringify(profile));

        // Load workspaces
        const wsList = await api.getWorkspaces();
        setWorkspaces(wsList);
        if (wsList.length > 0) {
          const match = wsList.find(w => w.workspace_id === activeWorkspace);
          if (!match) {
            setActiveWorkspace(wsList[0].workspace_id);
            api.setWorkspace(wsList[0].workspace_id);
          }
        }
      } catch (err) {
        console.warn('Session expired or invalid token:', err);
        logout();
      } finally {
        setLoading(false);
      }
    }
    loadUser();
  }, [token]);

  const login = async (username, password) => {
    const res = await api.login(username, password);
    setToken(res.access_token);
    setUser(res.user);
    localStorage.setItem('traceguard_user', JSON.stringify(res.user));
    if (res.active_workspace_id) {
      setActiveWorkspace(res.active_workspace_id);
    }
    // Refresh workspaces list
    try {
      const wsList = await api.getWorkspaces();
      setWorkspaces(wsList);
    } catch {
      // ignore
    }
    return res;
  };

  const signup = async (payload) => {
    const res = await api.signup(payload);
    // After signup, automatically login
    return await login(payload.username, payload.password);
  };

  const logout = () => {
    api.logout();
    setToken(null);
    setUser(null);
    setActiveWorkspace('default-workspace');
    setWorkspaces([]);
  };

  const switchWorkspace = (wsId) => {
    setActiveWorkspace(wsId);
    api.setWorkspace(wsId);
    window.location.reload(); // Refresh app states cleanly
  };

  const refreshWorkspaces = async () => {
    try {
      const wsList = await api.getWorkspaces();
      setWorkspaces(wsList);
    } catch (err) {
      console.error('Failed to refresh workspaces:', err);
    }
  };

  const value = {
    token,
    user,
    isAuthenticated: !!token,
    activeWorkspace,
    workspaces,
    loading,
    login,
    signup,
    logout,
    switchWorkspace,
    refreshWorkspaces
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
