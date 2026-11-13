import React, { useState, useEffect } from 'react';
import {
  Play,
  Square,
  Sliders,
  Filter,
  RefreshCw,
  Radio,
  Wifi,
  WifiOff,
  Zap,
  Activity,
  Layers,
  Search,
  Trash2
} from 'lucide-react';
import api from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';
import EventTable from '../components/EventTable';
import LoadingSpinner from '../components/LoadingSpinner';

export function LiveMonitor() {
  const [events, setEvents] = useState([]);
  const [simConfig, setSimConfig] = useState({
    mode: 'mixed',
    speed: 1.0,
    event_count: 150,
    anomaly_ratio: 0.25,
  });
  const [currentSimulation, setCurrentSimulation] = useState(null);
  const [isStarting, setIsStarting] = useState(false);
  const [isStopping, setIsStopping] = useState(false);
  const [filterType, setFilterType] = useState('all');
  const [filterSession, setFilterSession] = useState('');

  // Initial prefetch of events
  useEffect(() => {
    let isMounted = true;
    api.getEvents({ limit: 50 })
      .then((res) => {
        if (isMounted && res.events) {
          setEvents(res.events);
        }
      })
      .catch((err) => console.warn('Could not prefetch events:', err.message));
    return () => { isMounted = false; };
  }, []);

  // WebSocket event stream
  const { status: wsStatus } = useWebSocket('event', (data) => {
    if (data) {
      setEvents((prev) => [data, ...prev.slice(0, 199)]);
    }
  });

  useWebSocket('simulation_status', (data) => {
    if (data) {
      if (data.status === 'running') {
        setCurrentSimulation((prev) => ({ ...prev, ...data }));
      } else if (data.status === 'stopped' || data.status === 'completed') {
        setCurrentSimulation(null);
      }
    }
  });

  const handleStartSimulation = async () => {
    setIsStarting(true);
    try {
      const res = await api.startSimulation(simConfig);
      setCurrentSimulation(res);
    } catch (err) {
      alert(`Simulation start failed: ${err.message}`);
    } finally {
      setIsStarting(false);
    }
  };

  const handleStopSimulation = async () => {
    if (!currentSimulation?.simulation_id) return;
    setIsStopping(true);
    try {
      await api.stopSimulation(currentSimulation.simulation_id);
      setCurrentSimulation(null);
    } catch (err) {
      alert(`Simulation stop failed: ${err.message}`);
    } finally {
      setIsStopping(false);
    }
  };

  const filteredEvents = events.filter((evt) => {
    if (filterType !== 'all') {
      if (filterType === 'anomalous' && evt.label !== 'anomalous') return false;
      if (filterType === 'normal' && evt.label === 'anomalous') return false;
      if (['CONNECT', 'REQUEST', 'RESPONSE_200', 'CLOSE'].includes(filterType) && evt.event_type !== filterType) {
        return false;
      }
    }
    if (filterSession.trim()) {
      return evt.session_id?.toLowerCase().includes(filterSession.toLowerCase());
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Editorial Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--tg-border-subtle)]">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <h1 className="text-lg font-semibold tracking-tight text-[var(--tg-text-primary)]">
              Live Protocol Monitor
            </h1>
          </div>
          <p className="text-xs text-[var(--tg-text-muted)] mt-1">
            Real-time packet capture stream, HTTP finite-state validation, and anomaly classification.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-[var(--tg-bg-surface)] border border-[var(--tg-border-subtle)] text-xs font-mono">
            {wsStatus === 'connected' ? (
              <Wifi className="w-3.5 h-3.5 text-emerald-400" />
            ) : (
              <WifiOff className="w-3.5 h-3.5 text-rose-400" />
            )}
            <span className="text-[var(--tg-text-muted)]">Stream:</span>
            <span className={wsStatus === 'connected' ? 'text-emerald-400 font-semibold' : 'text-rose-400'}>
              {wsStatus.toUpperCase()}
            </span>
          </div>
          <button
            onClick={() => setEvents([])}
            className="tg-btn-secondary text-xs"
            aria-label="Clear active feed"
          >
            <Trash2 className="w-3.5 h-3.5 text-[var(--tg-text-muted)]" />
            <span>Clear Feed</span>
          </button>
        </div>
      </div>

      {/* Simulator Generator Panel */}
      <div className="tg-panel p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[var(--tg-border-subtle)]">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-emerald-400" />
            <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
              Synthetic Traffic Generator
            </h2>
          </div>
          {currentSimulation && (
            <div className="flex items-center gap-2 px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              <span className="text-xs font-mono text-emerald-400 font-semibold">
                ACTIVE: {currentSimulation.simulation_id}
              </span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          {/* Mode Selector */}
          <div>
            <label className="block text-[11px] font-mono text-[var(--tg-text-muted)] mb-1.5 uppercase">
              Traffic Mode
            </label>
            <select
              value={simConfig.mode}
              disabled={!!currentSimulation}
              onChange={(e) => setSimConfig({ ...simConfig, mode: e.target.value })}
              className="tg-select text-xs font-mono"
            >
              <option value="normal">Normal (Compliant Session Path)</option>
              <option value="anomalous">Anomalous (DFA Violations)</option>
              <option value="mixed">Mixed (Real-World Distribution)</option>
            </select>
          </div>

          {/* Speed Slider */}
          <div>
            <div className="flex justify-between text-[11px] font-mono text-[var(--tg-text-muted)] mb-1.5">
              <span className="uppercase">Rate Multiplier</span>
              <span className="text-emerald-400 font-semibold">{simConfig.speed}x</span>
            </div>
            <input
              type="range"
              min="0.5"
              max="5.0"
              step="0.5"
              value={simConfig.speed}
              disabled={!!currentSimulation}
              onChange={(e) => setSimConfig({ ...simConfig, speed: parseFloat(e.target.value) })}
              className="w-full accent-emerald-500 cursor-pointer"
            />
          </div>

          {/* Event Count */}
          <div>
            <label className="block text-[11px] font-mono text-[var(--tg-text-muted)] mb-1.5 uppercase">
              Target Event Volume
            </label>
            <input
              type="number"
              min="20"
              max="1000"
              value={simConfig.event_count}
              disabled={!!currentSimulation}
              onChange={(e) => setSimConfig({ ...simConfig, event_count: parseInt(e.target.value) || 50 })}
              className="tg-input text-xs font-mono"
            />
          </div>

          {/* Action Button */}
          <div className="flex items-end">
            {currentSimulation ? (
              <button
                onClick={handleStopSimulation}
                disabled={isStopping}
                className="w-full inline-flex items-center justify-center gap-1.5 py-2 px-3 rounded-md bg-rose-500/10 border border-rose-500/30 text-rose-400 hover:bg-rose-500/20 text-xs font-mono font-semibold transition"
              >
                <Square className="w-3.5 h-3.5" />
                <span>{isStopping ? 'Halting Stream...' : 'Halt Stream'}</span>
              </button>
            ) : (
              <button
                onClick={handleStartSimulation}
                disabled={isStarting}
                className="w-full tg-btn-primary text-xs"
              >
                <Play className="w-3.5 h-3.5" />
                <span>{isStarting ? 'Injecting...' : 'Inject Traffic'}</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Stream Filtering & Live Table */}
      <div className="tg-panel p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[var(--tg-border-subtle)]">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-cyan-400" />
            <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
              Live Ingestion Buffer ({filteredEvents.length} events)
            </h2>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* Search filter */}
            <div className="relative">
              <Search className="w-3 h-3 text-[var(--tg-text-muted)] absolute left-2.5 top-2.5" />
              <input
                type="text"
                placeholder="Filter session ID..."
                value={filterSession}
                onChange={(e) => setFilterSession(e.target.value)}
                className="tg-input pl-7 py-1 text-xs font-mono w-44"
              />
            </div>

            {/* Event Category Filter */}
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="tg-select py-1 text-xs font-mono w-36"
            >
              <option value="all">All Events</option>
              <option value="anomalous">Only Anomalies</option>
              <option value="normal">Only Compliant</option>
              <option value="CONNECT">CONNECT</option>
              <option value="REQUEST">REQUEST</option>
              <option value="RESPONSE_200">RESPONSE_200</option>
              <option value="CLOSE">CLOSE</option>
            </select>
          </div>
        </div>

        {/* Live Table */}
        <EventTable events={filteredEvents} />
      </div>
    </div>
  );
}

export default LiveMonitor;
