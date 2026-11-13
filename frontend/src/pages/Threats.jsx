import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Filter,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Clock,
  Cpu,
  Binary,
  Sparkles,
  ChevronRight,
  ArrowRight,
  Search,
  FileText
} from 'lucide-react';
import api from '../services/api';
import { useApi } from '../hooks/useApi';
import { useWebSocket } from '../hooks/useWebSocket';
import AlertCard from '../components/AlertCard';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';

export function Threats() {
  const [severityFilter, setSeverityFilter] = useState('all');
  const [engineFilter, setEngineFilter] = useState('all');
  const [selectedAlertId, setSelectedAlertId] = useState(null);
  const [alertDetail, setAlertDetail] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [notesInput, setNotesInput] = useState('');
  const [updatingStatus, setUpdatingStatus] = useState(false);

  const { data: alertsData, loading, error, refetch } = useApi(
    () => api.getAlerts({
      severity: severityFilter !== 'all' ? severityFilter : undefined,
      engine: engineFilter !== 'all' ? engineFilter : undefined,
      limit: 100,
    }),
    [severityFilter, engineFilter]
  );

  useWebSocket('alert', (newAlert) => {
    if (newAlert) {
      refetch();
    }
  });

  useEffect(() => {
    if (!selectedAlertId) {
      setAlertDetail(null);
      return;
    }
    let isMounted = true;
    setLoadingDetail(true);
    api.getAlertDetail(selectedAlertId)
      .then((data) => {
        if (isMounted) {
          setAlertDetail(data);
          setNotesInput(data.investigation_notes || '');
        }
      })
      .catch((err) => {
        console.error('Failed to load alert detail:', err);
      })
      .finally(() => {
        if (isMounted) setLoadingDetail(false);
      });

    return () => { isMounted = false; };
  }, [selectedAlertId]);

  const handleUpdateStatus = async (newStatus) => {
    if (!selectedAlertId) return;
    setUpdatingStatus(true);
    try {
      const updated = await api.updateAlert(selectedAlertId, {
        status: newStatus,
        investigation_notes: notesInput,
      });
      setAlertDetail((prev) => ({ ...prev, ...updated }));
      refetch();
    } catch (err) {
      alert(`Status update failed: ${err.message}`);
    } finally {
      setUpdatingStatus(false);
    }
  };

  const alerts = alertsData?.alerts || [];

  return (
    <div className="space-y-6">
      {/* Editorial Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--tg-border-subtle)]">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-rose-400" />
            <h1 className="text-lg font-semibold tracking-tight text-[var(--tg-text-primary)]">
              Threat Triage & Forensics
            </h1>
          </div>
          <p className="text-xs text-[var(--tg-text-muted)] mt-1">
            Investigate state machine protocol violations, statistical isolation forest outliers, and operator feedback.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Severity Filter */}
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] font-mono text-[var(--tg-text-muted)]">Severity:</span>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="tg-select py-1 text-xs font-mono w-28"
            >
              <option value="all">ALL</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          {/* Engine Filter */}
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] font-mono text-[var(--tg-text-muted)]">Engine:</span>
            <select
              value={engineFilter}
              onChange={(e) => setEngineFilter(e.target.value)}
              className="tg-select py-1 text-xs font-mono w-28"
            >
              <option value="all">ALL</option>
              <option value="fsm">FSM</option>
              <option value="ml">ML</option>
              <option value="hybrid">HYBRID</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Two-Panel Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left: Alerts Master List */}
        <div className="lg:col-span-5 space-y-3">
          <div className="flex items-center justify-between px-1">
            <span className="text-[11px] font-mono uppercase tracking-wider text-[var(--tg-text-muted)]">
              Flagged Incidents ({alerts.length})
            </span>
            <span className="text-[10px] font-mono text-[var(--tg-text-muted)]">
              Live updates enabled
            </span>
          </div>

          {loading && !alertsData ? (
            <LoadingSpinner text="Retrieving threat records..." />
          ) : alerts.length > 0 ? (
            <div className="space-y-2 max-h-[calc(100vh-250px)] overflow-y-auto pr-1">
              {alerts.map((alrt) => (
                <AlertCard
                  key={alrt.alert_id}
                  alert={alrt}
                  isSelected={selectedAlertId === alrt.alert_id}
                  onClick={() => setSelectedAlertId(alrt.alert_id)}
                />
              ))}
            </div>
          ) : (
            <div className="tg-panel p-8 text-center">
              <ShieldAlert className="w-8 h-8 text-[var(--tg-text-muted)] mx-auto mb-2 opacity-50" />
              <p className="text-xs font-mono text-[var(--tg-text-muted)]">
                No alerts match the selected criteria.
              </p>
            </div>
          )}
        </div>

        {/* Right: Forensic Details Panel */}
        <div className="lg:col-span-7">
          {loadingDetail ? (
            <div className="tg-panel p-12 text-center">
              <LoadingSpinner text="Loading forensic payload..." />
            </div>
          ) : alertDetail ? (
            <div className="tg-panel p-6 space-y-5">
              {/* Header Info */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[var(--tg-border-subtle)]">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-semibold text-[var(--tg-text-primary)]">
                      {alertDetail.alert_id}
                    </span>
                    <span className="tg-badge tg-badge-red">
                      {alertDetail.severity}
                    </span>
                  </div>
                  <p className="text-xs text-[var(--tg-text-muted)] font-mono mt-1">
                    Detected in session: <span className="text-blue-400 font-semibold">{alertDetail.session_id}</span>
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleUpdateStatus('investigating')}
                    disabled={updatingStatus || alertDetail.status === 'investigating'}
                    className="tg-btn-secondary text-xs"
                  >
                    Investigating
                  </button>
                  <button
                    onClick={() => handleUpdateStatus('resolved')}
                    disabled={updatingStatus || alertDetail.status === 'resolved'}
                    className="tg-btn-primary text-xs"
                  >
                    Resolve
                  </button>
                </div>
              </div>

              {/* Forensic Metric Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-lg bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)]">
                  <span className="text-[10px] font-mono uppercase text-[var(--tg-text-muted)]">Engine</span>
                  <p className="text-xs font-mono font-semibold text-emerald-400 mt-1 uppercase">
                    {alertDetail.engine}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)]">
                  <span className="text-[10px] font-mono uppercase text-[var(--tg-text-muted)]">Risk Factor</span>
                  <p className="text-xs font-mono font-semibold text-[var(--tg-text-primary)] mt-1">
                    {alertDetail.risk_score !== undefined
                      ? (alertDetail.risk_score > 1 ? `${alertDetail.risk_score}%` : `${(alertDetail.risk_score * 100).toFixed(0)}%`)
                      : '0%'}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)]">
                  <span className="text-[10px] font-mono uppercase text-[var(--tg-text-muted)]">FSM Violation</span>
                  <p className="text-xs font-mono font-semibold mt-1">
                    {alertDetail.fsm_violation ? (
                      <span className="text-rose-400">Yes (DFA Rejection)</span>
                    ) : (
                      <span className="text-emerald-400">Compliant</span>
                    )}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)]">
                  <span className="text-[10px] font-mono uppercase text-[var(--tg-text-muted)]">ML Anomaly</span>
                  <p className="text-xs font-mono font-semibold text-blue-400 mt-1">
                    {alertDetail.ml_anomaly_score !== undefined
                      ? `${(alertDetail.ml_anomaly_score * 100).toFixed(1)}%`
                      : 'N/A'}
                  </p>
                </div>
              </div>

              {/* Summary Description */}
              <div className="p-4 rounded-lg bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)]">
                <h3 className="text-xs font-mono font-semibold text-[var(--tg-text-muted)] uppercase mb-1">
                  Incident Rationale
                </h3>
                <p className="text-xs text-[var(--tg-text-secondary)] leading-relaxed">
                  {alertDetail.summary || 'Anomaly detected during continuous event telemetry verification.'}
                </p>
              </div>

              {/* Investigation Notes Form */}
              <div className="space-y-2">
                <div className="flex items-center gap-1.5 text-xs font-mono text-[var(--tg-text-muted)]">
                  <FileText className="w-3.5 h-3.5" />
                  <span>Operator Forensic Notes</span>
                </div>
                <textarea
                  value={notesInput}
                  onChange={(e) => setNotesInput(e.target.value)}
                  placeholder="Record mitigation notes, network indicators, or false positive rationale..."
                  rows={3}
                  className="tg-input text-xs font-mono resize-none"
                />
                <div className="flex justify-end">
                  <button
                    onClick={() => handleUpdateStatus(alertDetail.status)}
                    disabled={updatingStatus}
                    className="tg-btn-secondary text-xs"
                  >
                    Save Notes
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="tg-panel p-12 text-center space-y-3">
              <ShieldAlert className="w-10 h-10 text-[var(--tg-text-muted)] mx-auto opacity-40" />
              <h3 className="text-sm font-mono font-semibold text-[var(--tg-text-primary)]">
                No Incident Selected
              </h3>
              <p className="text-xs text-[var(--tg-text-muted)] max-w-sm mx-auto">
                Select an alert from the incident triage list on the left to inspect detailed protocol transitions, anomaly scores, and record operator notes.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Threats;
