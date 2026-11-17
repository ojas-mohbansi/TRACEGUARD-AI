import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';
import wsService from '../services/websocket';

const ACADEMIC_USER = {
  username: 'academic',
  role: 'admin',
  full_name: 'Academic Researcher',
  email: 'academic@traceguard.local',
};

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // Local academic mode: directly authenticated without login gate
  const [user, setUser] = useState(ACADEMIC_USER);
  const [activeWorkspace, setActiveWorkspace] = useState('default-workspace');
  const [workspaces, setWorkspaces] = useState([
    { workspace_id: 'default-workspace', name: 'Academic Research Lab', role: 'owner' }
  ]);
  const [loading, setLoading] = useState(false);

  // Optional background sync with backend profile if available
  useEffect(() => {
    async function syncProfile() {
      try {
        const profile = await api.getMe();
        if (profile && profile.username) {
          setUser({ ...ACADEMIC_USER, ...profile });
        }
      } catch {
        // In local academic mode, fallback smoothly to ACADEMIC_USER
      }
    }
    syncProfile();
  }, []);

  const login = async () => {
    setUser(ACADEMIC_USER);
    return { access_token: 'local-academic-token', user: ACADEMIC_USER };
  };

  const signup = async () => {
    setUser(ACADEMIC_USER);
    return { access_token: 'local-academic-token', user: ACADEMIC_USER };
  };

  const logout = () => {
    // In local academic mode, logout is a safe no-op that retains academic workspace
    console.info('Logout invoked in local academic mode — maintaining academic session.');
  };

  const switchWorkspace = (wsId) => {
    setActiveWorkspace(wsId);
    api.setWorkspace(wsId);
  };

  const refreshWorkspaces = async () => {
    try {
      const wsList = await api.getWorkspaces();
      if (wsList && wsList.length > 0) setWorkspaces(wsList);
    } catch {
      // ignore
    }
  };

  const value = {
    token: 'local-academic-token',
    user,
    isAuthenticated: true,
    activeWorkspace,
    workspaces,
    loading: false,
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
