import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import ErrorBoundary from './components/ErrorBoundary';

import Dashboard from './pages/Dashboard';
import AutomataLab from './pages/AutomataLab';
import LiveMonitor from './pages/LiveMonitor';
import Threats from './pages/Threats';
import DetectionLab from './pages/DetectionLab';
import Datasets from './pages/Datasets';
import Settings from './pages/Settings';

export function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="automata" element={<AutomataLab />} />
            <Route path="protocol" element={<Navigate to="/automata" replace />} />
            <Route path="monitor" element={<LiveMonitor />} />
            <Route path="threats" element={<Threats />} />
            <Route path="lab" element={<DetectionLab />} />
            <Route path="datasets" element={<Datasets />} />
            <Route path="settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </ErrorBoundary>
    </BrowserRouter>
  );
}

export default App;
