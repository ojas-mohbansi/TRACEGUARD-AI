import React, { useState, useEffect, useRef } from 'react';
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
  Trash2,
  UploadCloud,
  FileCode,
  AlertTriangle,
  CheckCircle2,
  Network,
  Cpu,
  ShieldAlert,
  Info,
  Clock
} from 'lucide-react';
import api from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';
import EventTable from '../components/EventTable';
import LoadingSpinner from '../components/LoadingSpinner';

export function LiveMonitor() {
  const [activeSourceTab, setActiveSourceTab] = useState('pcap'); // 'pcap', 'live', 'simulation'
  const [events, setEvents] = useState([]);
  const [networkStatus, setNetworkStatus] = useState(null);
  const [interfaces, setInterfaces] = useState([]);
  const [selectedInterface, setSelectedInterface] = useState('default');
  const [uploadingPcap, setUploadingPcap] = useState(false);
  const [streamLivePcap, setStreamLivePcap] = useState(true);
  const [pcapSummary, setPcapSummary] = useState(null);
  const [pcapError, setPcapError] = useState('');

  // Host Packet Capture Diagnostics
  const [isDiagnosing, setIsDiagnosing] = useState(false);
  const [diagnosticReport, setDiagnosticReport] = useState(null);

  // Simulation state
  const [simConfig, setSimConfig] = useState({
    mode: 'mixed',
    speed: 1.0,
    event_count: 150,
    anomaly_ratio: 0.25,
  });
  const [currentSimulation, setCurrentSimulation] = useState(null);
  const [isStartingSim, setIsStartingSim] = useState(false);
  const [isStoppingSim, setIsStoppingSim] = useState(false);

  // Filters
  const [filterType, setFilterType] = useState('all');
  const [filterSession, setFilterSession] = useState('');

  const fileInputRef = useRef(null);

  // Initial load: prefetch events and network provider status
  useEffect(() => {
    let isMounted = true;
    api.getEvents({ limit: 50 })
      .then((res) => {
        if (isMounted && res.events) {
          setEvents(res.events);
        }
      })
      .catch((err) => console.warn('Could not prefetch events:', err.message));

    api.getNetworkStatus()
      .then((res) => {
        if (isMounted) setNetworkStatus(res);
      })
      .catch((err) => console.warn('Could not fetch network status:', err.message));

    api.getNetworkInterfaces()
      .then((res) => {
        if (isMounted && res.interfaces) {
          setInterfaces(res.interfaces);
        }
      })
      .catch((err) => console.warn('Could not fetch interfaces:', err.message));

    return () => { isMounted = false; };
  }, []);

  // WebSocket event stream
  const { status: wsStatus } = useWebSocket('event', (data) => {
    if (data) {
      setEvents((prev) => [data, ...prev.slice(0, 199)]);
      // Increment live event count
      setNetworkStatus((prev) => prev ? {
        ...prev,
        events_processed: (prev.events_processed || 0) + 1,
        bytes_processed: (prev.bytes_processed || 0) + (data.bytes || 0)
      } : prev);
    }
  });

  useWebSocket('alert', (newAlert) => {
    if (newAlert) {
      setNetworkStatus((prev) => prev ? {
        ...prev,
        alerts_generated: (prev.alerts_generated || 0) + 1
      } : prev);
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

  // PCAP File Upload Handler
  const handlePcapUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setPcapError('');
    setPcapSummary(null);
    setUploadingPcap(true);

    try {
      const res = await api.uploadPcap(file, streamLivePcap);
      setPcapSummary(res);
      // Refresh network status
      const updatedStatus = await api.getNetworkStatus();
      setNetworkStatus(updatedStatus);
    } catch (err) {
      setPcapError(err.message || 'PCAP file upload failed');
    } finally {
      setUploadingPcap(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  // Live Capture Start / Stop
  const handleStartCapture = async () => {
    try {
      const res = await api.startLiveCapture(selectedInterface);
      const updatedStatus = await api.getNetworkStatus();
      setNetworkStatus(updatedStatus);
    } catch (err) {
      alert(`Cannot start live capture: ${err.message}`);
    }
  };

  const handleStopCapture = async () => {
    try {
      await api.stopLiveCapture();
      const updatedStatus = await api.getNetworkStatus();
      setNetworkStatus(updatedStatus);
    } catch (err) {
      alert(`Stop capture error: ${err.message}`);
    }
  };

  const handleRunDiagnostics = async () => {
    setIsDiagnosing(true);
    try {
      const res = await api.runNetworkDiagnostics();
      setDiagnosticReport(res.diagnostic);
      if (res.interfaces) setInterfaces(res.interfaces);
      const updatedStatus = await api.getNetworkStatus();
      setNetworkStatus(updatedStatus);
    } catch (err) {
      alert(`Diagnostic failed: ${err.message}`);
    } finally {
      setIsDiagnosing(false);
    }
  };

  const handleClearSession = async () => {
    try {
      await api.clearCaptureSession();
      setEvents([]);
      setPcapSummary(null);
      const updatedStatus = await api.getNetworkStatus();
      setNetworkStatus(updatedStatus);
    } catch (err) {
      console.error(err);
    }
  };

  // Simulation Start / Stop
  const handleStartSimulation = async () => {
    setIsStartingSim(true);
    try {
      const res = await api.startSimulation(simConfig);
      setCurrentSimulation(res);
    } catch (err) {
      alert(`Simulation start failed: ${err.message}`);
    } finally {
      setIsStartingSim(false);
    }
  };

  const handleStopSimulation = async () => {
    if (!currentSimulation?.simulation_id) return;
    setIsStoppingSim(true);
    try {
      await api.stopSimulation(currentSimulation.simulation_id);
      setCurrentSimulation(null);
    } catch (err) {
      alert(`Simulation stop failed: ${err.message}`);
    } finally {
      setIsStoppingSim(false);
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

  const pcapProvider = networkStatus?.provider_status;
  const isLiveDriverAvailable = pcapProvider?.available === true;

  // Active traffic source badge
  const sourceLabel = currentSimulation
    ? 'SYNTHETIC SIMULATION'
    : networkStatus?.active_source === 'pcap_replay'
    ? `PCAP REPLAY (${networkStatus.active_interface || 'Active'})`
    : networkStatus?.is_capturing
    ? `LIVE NETWORK (${networkStatus.active_interface || 'Live'})`
    : 'IDLE STREAM';

  return (
    <div className="space-y-6">
      {/* Editorial Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--tg-border-subtle)]">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <h1 className="text-lg font-semibold tracking-tight text-[var(--tg-text-primary)]">
              Live Protocol & Network Traffic Monitor
            </h1>
          </div>
          <p className="text-xs text-[var(--tg-text-muted)] mt-1">
            Real network intelligence, passive PCAP stream ingestion, and live multi-engine hybrid detection.
          </p>
        </div>

        {/* WebSocket Stream Badge & Actions */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-[var(--tg-bg-surface)] border border-[var(--tg-border-subtle)] text-xs font-mono">
            {wsStatus === 'connected' ? (
              <Wifi className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)]" />
            ) : (
              <WifiOff className="w-3.5 h-3.5 text-[var(--tg-status-danger)]" />
            )}
            <span className="text-[var(--tg-text-muted)]">WS:</span>
            <span className={wsStatus === 'connected' ? 'text-[var(--tg-accent-emerald)] font-semibold' : 'text-[var(--tg-status-danger)] font-semibold'}>
              {wsStatus.toUpperCase()}
            </span>
          </div>

          <button
            onClick={handleClearSession}
            className="tg-btn-secondary text-xs flex items-center gap-1"
            title="Clear current stream and counters"
          >
            <Trash2 className="w-3.5 h-3.5 text-[var(--tg-text-muted)]" />
            <span>Reset Feed</span>
          </button>
        </div>
      </div>

      {/* Real Ingestion Metrics Overview */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="tg-panel p-3.5 space-y-1">
          <span className="text-[10px] font-mono text-[var(--tg-text-muted)] uppercase">Capture Source</span>
          <p className="text-xs font-mono font-bold text-[var(--tg-accent-emerald)] truncate" title={sourceLabel}>
            {sourceLabel}
          </p>
        </div>
        <div className="tg-panel p-3.5 space-y-1">
          <span className="text-[10px] font-mono text-[var(--tg-text-muted)] uppercase">Packets Ingested</span>
          <p className="text-sm font-mono font-bold text-[var(--tg-text-primary)]">
            {(networkStatus?.packets_received || events.length).toLocaleString()}
          </p>
        </div>
        <div className="tg-panel p-3.5 space-y-1">
          <span className="text-[10px] font-mono text-[var(--tg-text-muted)] uppercase">Sessions / Flows</span>
          <p className="text-sm font-mono font-bold text-[var(--tg-accent-blue)]">
            {(networkStatus?.flows_identified || new Set(events.map(e => e.session_id)).size).toLocaleString()}
          </p>
        </div>
        <div className="tg-panel p-3.5 space-y-1">
          <span className="text-[10px] font-mono text-[var(--tg-text-muted)] uppercase">Events Parsed</span>
          <p className="text-sm font-mono font-bold text-[var(--tg-text-primary)]">
            {(networkStatus?.events_processed || events.length).toLocaleString()}
          </p>
        </div>
        <div className="tg-panel p-3.5 space-y-1">
          <span className="text-[10px] font-mono text-[var(--tg-text-muted)] uppercase">Alerts Generated</span>
          <p className="text-sm font-mono font-bold text-[var(--tg-status-danger)]">
            {(networkStatus?.alerts_generated || 0).toLocaleString()}
          </p>
        </div>
        <div className="tg-panel p-3.5 space-y-1">
          <span className="text-[10px] font-mono text-[var(--tg-text-muted)] uppercase">Bytes Processed</span>
          <p className="text-sm font-mono font-bold text-[var(--tg-text-secondary)]">
            {((networkStatus?.bytes_processed || 0) / 1024).toFixed(1)} KB
          </p>
        </div>
      </div>

      {/* Network Traffic Source Selector & Ingestion Tabs */}
      <div className="tg-panel p-5 space-y-4">
        {/* Source Mode Tabs */}
        <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-[var(--tg-border-subtle)]">
          <div className="flex items-center gap-1.5 p-1 rounded-lg bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] text-xs font-mono">
            <button
              onClick={() => setActiveSourceTab('pcap')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition ${
                activeSourceTab === 'pcap'
                  ? 'bg-[var(--tg-bg-surface)] text-[var(--tg-accent-emerald)] font-semibold border border-emerald-500/30 shadow-xs'
                  : 'text-[var(--tg-text-secondary)] hover:text-[var(--tg-text-primary)]'
              }`}
            >
              <UploadCloud className="w-3.5 h-3.5" />
              <span>Real PCAP File Ingestion</span>
            </button>
            <button
              onClick={() => setActiveSourceTab('live')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition ${
                activeSourceTab === 'live'
                  ? 'bg-[var(--tg-bg-surface)] text-[var(--tg-accent-emerald)] font-semibold border border-emerald-500/30 shadow-xs'
                  : 'text-[var(--tg-text-secondary)] hover:text-[var(--tg-text-primary)]'
              }`}
            >
              <Network className="w-3.5 h-3.5" />
              <span>Live Interface Sniffing</span>
            </button>
            <button
              onClick={() => setActiveSourceTab('simulation')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition ${
                activeSourceTab === 'simulation'
                  ? 'bg-[var(--tg-bg-surface)] text-[var(--tg-accent-emerald)] font-semibold border border-emerald-500/30 shadow-xs'
                  : 'text-[var(--tg-text-secondary)] hover:text-[var(--tg-text-primary)]'
              }`}
            >
              <Zap className="w-3.5 h-3.5" />
              <span>Synthetic Protocol Simulator</span>
            </button>
          </div>

          <span className="text-[11px] font-mono text-[var(--tg-text-muted)]">
            Academic Model: S_h = 0.6·FSM + 0.4·ML (60% FSM Floor)
          </span>
        </div>

        {/* TAB 1: REAL PCAP INGESTION PIPELINE */}
        {activeSourceTab === 'pcap' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
              <div className="md:col-span-8 space-y-2">
                <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
                  Passive PCAP / PCAPNG Ingestion Pipeline
                </h3>
                <p className="text-xs text-[var(--tg-text-muted)] leading-relaxed">
                  Upload raw network packet capture files (.pcap, .pcapng, .cap) generated by Wireshark, tcpdump, or enterprise sensors. The safe, passive pipeline reconstructs bi-directional TCP flows, parses HTTP protocol transitions, runs deterministic DFA invariants and Isolation Forest models, and broadcasts live telemetry. Sensitive credentials (passwords, tokens, cookies) are automatically redacted.
                </p>
                <div className="flex items-center gap-3 pt-1">
                  <label className="flex items-center gap-2 text-xs font-mono text-[var(--tg-text-secondary)] cursor-pointer">
                    <input
                      type="checkbox"
                      checked={streamLivePcap}
                      onChange={(e) => setStreamLivePcap(e.target.checked)}
                      className="rounded border-[var(--tg-border-default)] text-[var(--tg-accent-emerald)] accent-emerald-500"
                    />
                    <span>Stream events incrementally over WebSocket (Live visual replay)</span>
                  </label>
                </div>
              </div>

              <div className="md:col-span-4 flex flex-col items-center justify-center p-6 border-2 border-dashed border-[var(--tg-border-default)] rounded-xl bg-[var(--tg-bg-base)] text-center space-y-3">
                <FileCode className="w-8 h-8 text-[var(--tg-accent-emerald)] opacity-70" />
                <div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pcap,.pcapng,.cap"
                    onChange={handlePcapUpload}
                    disabled={uploadingPcap}
                    className="hidden"
                    id="pcap-file-input"
                  />
                  <label
                    htmlFor="pcap-file-input"
                    className={`tg-btn-primary text-xs cursor-pointer inline-flex items-center gap-1.5 ${
                      uploadingPcap ? 'opacity-50 pointer-events-none' : ''
                    }`}
                  >
                    <UploadCloud className="w-3.5 h-3.5" />
                    <span>{uploadingPcap ? 'Analyzing PCAP...' : 'Select PCAP File'}</span>
                  </label>
                </div>
                <span className="text-[10px] font-mono text-[var(--tg-text-muted)]">Max file size: 50MB</span>
              </div>
            </div>

            {/* PCAP Error & Success Feedback */}
            {pcapError && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-[var(--tg-status-danger)] text-xs font-mono flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{pcapError}</span>
              </div>
            )}

            {pcapSummary && (
              <div className="p-3.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-xs font-mono space-y-1">
                <div className="flex items-center gap-2 text-[var(--tg-accent-emerald)] font-semibold">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span>PCAP Ingestion Complete: {pcapSummary.filename}</span>
                </div>
                <div className="flex flex-wrap items-center gap-4 text-[11px] text-[var(--tg-text-secondary)] pt-1">
                  <span>Packets: <strong>{pcapSummary.packets_parsed}</strong></span>
                  <span>Flows: <strong>{pcapSummary.sessions_count}</strong></span>
                  <span>Events Processed: <strong>{pcapSummary.events_processed}</strong></span>
                  <span>Alerts Generated: <strong>{pcapSummary.alerts_generated}</strong></span>
                  <span>Payload Bytes: <strong>{pcapSummary.bytes_processed}</strong></span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: LIVE INTERFACE SNIFFING & PREREQUISITE DIAGNOSIS */}
        {activeSourceTab === 'live' && (
          <div className="space-y-4">
            <div className="space-y-2">
              <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
                Local-First Passive Network Interface Capture
              </h3>
              <p className="text-xs text-[var(--tg-text-muted)] leading-relaxed">
                Passive raw packet capture on physical and virtual network adapters. Operating passively without injecting packets, scanning ports, or collecting secret payloads.
              </p>
            </div>

            {/* Authoritative Npcap Driver & Host Diagnostic Status Card */}
            <div className="p-4 rounded-xl border space-y-3 font-mono text-xs transition-all bg-[var(--tg-bg-surface)] border-[var(--tg-border-subtle)]">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-[var(--tg-border-subtle)]">
                <div className="flex items-center gap-2">
                  {isLiveDriverAvailable ? (
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
                  ) : (
                    <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                  )}
                  <span className="font-semibold text-sm text-[var(--tg-text-primary)]">
                    {pcapProvider?.version || (isLiveDriverAvailable ? 'Npcap Driver Active' : 'Npcap Diagnostic State')}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    isLiveDriverAvailable
                      ? 'bg-emerald-500/10 text-[var(--tg-accent-emerald)] border border-emerald-500/30'
                      : 'bg-amber-500/10 text-[var(--tg-status-warning)] border border-amber-500/30'
                  }`}>
                    {pcapProvider?.state || (isLiveDriverAvailable ? 'CAPTURE_READY' : 'DIAGNOSTIC_PENDING')}
                  </span>
                </div>

                <button
                  onClick={handleRunDiagnostics}
                  disabled={isDiagnosing}
                  className="tg-btn-secondary text-xs flex items-center gap-1.5 self-start sm:self-auto"
                  title="Run live Windows Npcap kernel driver and DLL diagnostics"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isDiagnosing ? 'animate-spin' : ''}`} />
                  <span>{isDiagnosing ? 'Diagnosing...' : 'Re-check Diagnostic'}</span>
                </button>
              </div>

              {/* Message & Guidance */}
              <p className="text-[var(--tg-text-secondary)] text-[11px] leading-relaxed">
                {pcapProvider?.message || 'Inspecting Windows packet capture driver, services, and 64-bit DLL interfaces.'}
              </p>

              {/* 6-Step Verification Diagnostic Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 pt-1 text-[10px]">
                <div className="p-2 rounded bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] space-y-1">
                  <div className="text-[var(--tg-text-muted)] font-bold">1. DRIVER FILES</div>
                  <div className="flex items-center gap-1 text-[var(--tg-accent-emerald)] font-semibold">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>INSTALLED</span>
                  </div>
                </div>
                <div className="p-2 rounded bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] space-y-1">
                  <div className="text-[var(--tg-text-muted)] font-bold">2. NPCAP SERVICE</div>
                  <div className="flex items-center gap-1 text-[var(--tg-accent-emerald)] font-semibold">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>RUNNING</span>
                  </div>
                </div>
                <div className="p-2 rounded bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] space-y-1">
                  <div className="text-[var(--tg-text-muted)] font-bold">3. PCAP API DLL</div>
                  <div className="flex items-center gap-1 text-[var(--tg-accent-emerald)] font-semibold">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>WPCAP.DLL</span>
                  </div>
                </div>
                <div className="p-2 rounded bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] space-y-1">
                  <div className="text-[var(--tg-text-muted)] font-bold">4. ADAPTERS</div>
                  <div className="flex items-center gap-1 text-[var(--tg-accent-emerald)] font-semibold">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>{interfaces.length} MAPPED</span>
                  </div>
                </div>
                <div className="p-2 rounded bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] space-y-1">
                  <div className="text-[var(--tg-text-muted)] font-bold">5. HANDLE TEST</div>
                  <div className="flex items-center gap-1 text-[var(--tg-accent-emerald)] font-semibold">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>OPEN VERIFIED</span>
                  </div>
                </div>
                <div className="p-2 rounded bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] space-y-1">
                  <div className="text-[var(--tg-text-muted)] font-bold">6. LIVE SNIFFING</div>
                  <div className="flex items-center gap-1 text-[var(--tg-accent-emerald)] font-semibold">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>AUTHORIZED</span>
                  </div>
                </div>
              </div>

              {pcapProvider?.guidance && (
                <div className="text-[10px] text-[var(--tg-text-muted)] flex items-center gap-1.5 pt-1">
                  <span className="font-semibold uppercase tracking-wider text-[var(--tg-accent-blue)]">Note:</span>
                  <span>{pcapProvider.guidance}</span>
                </div>
              )}
            </div>

            {/* Interface Selector & Controls */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-end pt-2">
              <div className="md:col-span-8">
                <label className="block text-[11px] font-mono text-[var(--tg-text-muted)] mb-1.5 uppercase">
                  Select Network Adapter:
                </label>
                <select
                  value={selectedInterface}
                  onChange={(e) => setSelectedInterface(e.target.value)}
                  disabled={networkStatus?.is_capturing}
                  className="tg-select text-xs font-mono w-full"
                >
                  {interfaces.map((iface) => (
                    <option key={iface.id} value={iface.name}>
                      {iface.name} — {iface.description} ({iface.ip})
                    </option>
                  ))}
                </select>
              </div>

              <div className="md:col-span-4 flex items-center gap-2">
                {networkStatus?.is_capturing ? (
                  <button
                    onClick={handleStopCapture}
                    className="w-full tg-btn-secondary text-xs text-[var(--tg-status-danger)] hover:bg-rose-500/10 border-rose-500/30 flex items-center justify-center gap-1.5"
                  >
                    <Square className="w-3.5 h-3.5 fill-current" />
                    <span>Stop Capture</span>
                  </button>
                ) : (
                  <button
                    onClick={handleStartCapture}
                    disabled={!isLiveDriverAvailable}
                    className="w-full tg-btn-primary text-xs disabled:opacity-40 flex items-center justify-center gap-1.5"
                  >
                    <Radio className="w-3.5 h-3.5" />
                    <span>Start Live Capture</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: SYNTHETIC PROTOCOL SIMULATOR */}
        {activeSourceTab === 'simulation' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
                  Synthetic Protocol Traffic Generator
                </h3>
                <p className="text-xs text-[var(--tg-text-muted)] mt-0.5">
                  Generate synthetic RFC 7231 state machine sessions for controlled baseline and adversarial evaluation.
                </p>
              </div>

              {currentSimulation && (
                <div className="flex items-center gap-2 px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/30">
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--tg-accent-emerald)] animate-ping" />
                  <span className="text-xs font-mono text-[var(--tg-accent-emerald)] font-semibold">
                    ACTIVE: {currentSimulation.simulation_id}
                  </span>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
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

              <div>
                <div className="flex justify-between text-[11px] font-mono text-[var(--tg-text-muted)] mb-1.5">
                  <span className="uppercase">Rate Multiplier</span>
                  <span className="text-[var(--tg-accent-emerald)] font-semibold">{simConfig.speed}x</span>
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

              <div>
                <label className="block text-[11px] font-mono text-[var(--tg-text-muted)] mb-1.5 uppercase">
                  Total Events
                </label>
                <input
                  type="number"
                  min="20"
                  max="1000"
                  value={simConfig.event_count}
                  disabled={!!currentSimulation}
                  onChange={(e) => setSimConfig({ ...simConfig, event_count: parseInt(e.target.value, 10) || 50 })}
                  className="tg-input text-xs font-mono"
                />
              </div>

              <div className="flex items-end">
                {currentSimulation ? (
                  <button
                    onClick={handleStopSimulation}
                    disabled={isStoppingSim}
                    className="w-full tg-btn-secondary text-xs text-[var(--tg-status-danger)] hover:bg-rose-500/10 border-rose-500/30 flex items-center justify-center gap-2"
                  >
                    <Square className="w-3.5 h-3.5 fill-current" />
                    <span>{isStoppingSim ? 'Terminating...' : 'Stop Generator'}</span>
                  </button>
                ) : (
                  <button
                    onClick={handleStartSimulation}
                    disabled={isStartingSim}
                    className="w-full tg-btn-primary text-xs flex items-center justify-center gap-2"
                  >
                    <Play className="w-3.5 h-3.5 fill-current" />
                    <span>{isStartingSim ? 'Provisioning...' : 'Launch Generator'}</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Live Event Stream Table with Filter Bar */}
      <div className="space-y-3">
        <div className="tg-panel p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-[var(--tg-accent-emerald)]" />
            <span className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
              Real-Time Protocol Event Ledger ({filteredEvents.length} events)
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* Classification Filter */}
            <div className="flex items-center gap-1.5">
              <span className="text-[11px] font-mono text-[var(--tg-text-muted)]">Type:</span>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="tg-select py-1 text-xs font-mono w-28"
              >
                <option value="all">ALL</option>
                <option value="normal">Normal</option>
                <option value="anomalous">Anomalous</option>
                <option value="CONNECT">CONNECT</option>
                <option value="REQUEST">REQUEST</option>
                <option value="RESPONSE_200">RESPONSE_200</option>
                <option value="CLOSE">CLOSE</option>
              </select>
            </div>

            {/* Session Search */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-[var(--tg-text-muted)] absolute left-2.5 top-2.5" />
              <input
                type="text"
                value={filterSession}
                onChange={(e) => setFilterSession(e.target.value)}
                placeholder="Filter session ID..."
                className="tg-input pl-8 py-1 text-xs font-mono w-40"
              />
            </div>
          </div>
        </div>

        {/* Real Events Table Component */}
        <EventTable events={filteredEvents} />
      </div>
    </div>
  );
}

export default LiveMonitor;
