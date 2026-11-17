import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import ErrorBoundary from './components/ErrorBoundary';
import LoadingSpinner from './components/LoadingSpinner';
import { AuthProvider, useAuth } from './context/AuthContext';

// Route-level Lazy Loading for Heavy Feature Pages & Visualization Engines
const Dashboard = lazy(() => import('./pages/Dashboard'));
const AutomataLab = lazy(() => import('./pages/AutomataLab'));
const ProtocolExplorer = lazy(() => import('./pages/ProtocolExplorer'));
const LiveMonitor = lazy(() => import('./pages/LiveMonitor'));
const Threats = lazy(() => import('./pages/Threats'));
const DetectionLab = lazy(() => import('./pages/DetectionLab'));
const Datasets = lazy(() => import('./pages/Datasets'));
const Settings = lazy(() => import('./pages/Settings'));
const Landing = lazy(() => import('./pages/Landing'));
const Login = lazy(() => import('./pages/Login'));
const Signup = lazy(() => import('./pages/Signup'));

function RouteFallback() {
  return (
    <div className="min-h-[50vh] flex flex-col items-center justify-center gap-3">
      <LoadingSpinner size="lg" />
      <span className="text-xs font-mono text-[var(--tg-text-muted)] animate-pulse">
        Initializing Security Module...
      </span>
    </div>
  );
}

function ProtectedRoute({ children }) {
  // Local Academic Mode: Always allows immediate direct entry to product features
  return children;
}

export function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <AuthProvider>
          <Suspense fallback={<RouteFallback />}>
            <Routes>
              {/* Local Academic Experience: Direct entry to SOC Console */}
              <Route path="/login" element={<Navigate to="/" replace />} />
              <Route path="/signup" element={<Navigate to="/" replace />} />
              <Route path="/landing" element={<Landing />} />

              {/* Primary Product Application Console */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <AppLayout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<Dashboard />} />
                <Route path="automata" element={<AutomataLab />} />
                <Route path="protocol" element={<ProtocolExplorer />} />
                <Route path="monitor" element={<LiveMonitor />} />
                <Route path="threats" element={<Threats />} />
                <Route path="lab" element={<DetectionLab />} />
                <Route path="detection" element={<DetectionLab />} />
                <Route path="datasets" element={<Datasets />} />
                <Route path="settings" element={<Settings />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Route>
            </Routes>
          </Suspense>
        </AuthProvider>
      </ErrorBoundary>
    </BrowserRouter>
  );
}

export default App;
