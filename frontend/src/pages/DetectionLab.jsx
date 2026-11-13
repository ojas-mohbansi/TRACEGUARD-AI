import React, { useState } from 'react';
import {
  FlaskConical,
  Play,
  BarChart2,
  CheckCircle,
  AlertTriangle,
  Zap,
  Target,
  Clock,
  ShieldCheck,
  Cpu,
  Binary,
  Sparkles
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import api from '../services/api';
import { useApi } from '../hooks/useApi';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';

export function DetectionLab() {
  const [selectedDatasetId, setSelectedDatasetId] = useState('');
  const [runningEngines, setRunningEngines] = useState({ fsm: false, ml: false, hybrid: false });
  const [runSuccess, setRunSuccess] = useState(null);

  const { data: datasetsData } = useApi(() => api.getDatasets());

  const {
    data: comparison,
    loading: loadingComparison,
    error: comparisonError,
    refetch: refetchComparison
  } = useApi(
    () => {
      if (!selectedDatasetId) return Promise.resolve(null);
      return api.getDetectionComparison(selectedDatasetId);
    },
    [selectedDatasetId],
    false
  );

  const handleSelectDataset = (dsId) => {
    setSelectedDatasetId(dsId);
    if (dsId) {
      setTimeout(() => refetchComparison(), 50);
    }
  };

  const handleRunEngine = async (engine) => {
    if (!selectedDatasetId) {
      alert('Please select a dataset first.');
      return;
    }
    setRunningEngines((prev) => ({ ...prev, [engine]: true }));
    setRunSuccess(null);
    try {
      const res = await api.runDetection({
        session_ids: [],
        engines: [engine],
        dataset_id: selectedDatasetId,
      });
      setRunSuccess(`Engine ${engine.toUpperCase()} processed ${res.results?.length || 0} sessions successfully.`);
      refetchComparison();
    } catch (err) {
      alert(`Detection run failed: ${err.message}`);
    } finally {
      setRunningEngines((prev) => ({ ...prev, [engine]: false }));
    }
  };

  const datasets = datasetsData?.datasets || [];
  const engines = comparison?.engines || {};

  const metricKeys = [
    { key: 'precision', label: 'Precision' },
    { key: 'recall', label: 'Recall' },
    { key: 'f1_score', label: 'F1 Score' },
    { key: 'detection_rate', label: 'Detection Rate' },
    { key: 'false_positive_rate', label: 'FPR' },
  ];

  const chartData = metricKeys.map((m) => ({
    metric: m.label,
    FSM: engines.fsm ? parseFloat((engines.fsm[m.key] * 100).toFixed(1)) : 0,
    ML: engines.ml ? parseFloat((engines.ml[m.key] * 100).toFixed(1)) : 0,
    Hybrid: engines.hybrid ? parseFloat((engines.hybrid[m.key] * 100).toFixed(1)) : 0,
  }));

  return (
    <div className="space-y-6">
      {/* Editorial Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--tg-border-subtle)]">
        <div>
          <div className="flex items-center gap-2">
            <FlaskConical className="w-4 h-4 text-emerald-400" />
            <h1 className="text-lg font-semibold tracking-tight text-[var(--tg-text-primary)]">
              Detection Benchmark Lab
            </h1>
          </div>
          <p className="text-xs text-[var(--tg-text-muted)] mt-1">
            Empirical comparative analysis of FSM state invariance, Isolation Forest ML anomaly scores, and Hybrid consensus.
          </p>
        </div>
      </div>

      {/* Dataset Selection & Benchmark Actions */}
      <div className="tg-panel p-5 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
          {/* Target Dataset Dropdown */}
          <div className="md:col-span-6">
            <label className="block text-[11px] font-mono text-[var(--tg-text-muted)] mb-1.5 uppercase">
              Target Evaluation Dataset
            </label>
            <select
              value={selectedDatasetId}
              onChange={(e) => handleSelectDataset(e.target.value)}
              className="tg-select text-xs font-mono"
            >
              <option value="">-- Select Benchmark Dataset --</option>
              {datasets.map((ds) => (
                <option key={ds.dataset_id} value={ds.dataset_id}>
                  {ds.name} ({ds.session_count || ds.event_count || 0} records)
                </option>
              ))}
            </select>
          </div>

          {/* Engine Runner Buttons */}
          <div className="md:col-span-6 flex flex-wrap items-center gap-2">
            <button
              onClick={() => handleRunEngine('fsm')}
              disabled={runningEngines.fsm || !selectedDatasetId}
              className="flex-1 tg-btn-secondary text-xs disabled:opacity-40"
            >
              <Binary className="w-3.5 h-3.5 text-emerald-400" />
              <span>{runningEngines.fsm ? 'Running FSM...' : 'Run FSM'}</span>
            </button>

            <button
              onClick={() => handleRunEngine('ml')}
              disabled={runningEngines.ml || !selectedDatasetId}
              className="flex-1 tg-btn-secondary text-xs disabled:opacity-40"
            >
              <Cpu className="w-3.5 h-3.5 text-blue-400" />
              <span>{runningEngines.ml ? 'Running ML...' : 'Run ML'}</span>
            </button>

            <button
              onClick={() => handleRunEngine('hybrid')}
              disabled={runningEngines.hybrid || !selectedDatasetId}
              className="flex-1 tg-btn-primary text-xs disabled:opacity-40"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{runningEngines.hybrid ? 'Evaluating...' : 'Run Hybrid'}</span>
            </button>
          </div>
        </div>

        {runSuccess && (
          <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-xs font-mono text-emerald-400 flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            <span>{runSuccess}</span>
          </div>
        )}
      </div>

      {/* Comparison Results Area */}
      {loadingComparison ? (
        <LoadingSpinner text="Computing cross-engine confusion matrices and statistical benchmarks..." />
      ) : comparison && comparison.engines ? (
        <div className="space-y-6">
          {/* Comparison Bar Chart */}
          <div className="tg-panel p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
                  Performance Metric Consensus (%)
                </h2>
                <p className="text-[11px] text-[var(--tg-text-muted)] mt-0.5">
                  Comparison across Precision, Recall, F1 Score, Detection Rate, and False Positive Rate
                </p>
              </div>
            </div>

            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="metric" stroke="#8896AB" fontSize={11} tickLine={false} />
                  <YAxis stroke="#8896AB" fontSize={11} tickLine={false} domain={[0, 100]} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#141B2B',
                      borderColor: 'rgba(255,255,255,0.1)',
                      borderRadius: '6px',
                      fontSize: '11px',
                      fontFamily: 'JetBrains Mono',
                      color: '#F8FAFC',
                    }}
                  />
                  <Legend
                    wrapperStyle={{ fontSize: '11px', fontFamily: 'JetBrains Mono' }}
                    formatter={(val) => <span className="text-[var(--tg-text-secondary)]">{val}</span>}
                  />
                  <Bar dataKey="FSM" fill="#10B981" radius={[3, 3, 0, 0]} />
                  <Bar dataKey="ML" fill="#3B82F6" radius={[3, 3, 0, 0]} />
                  <Bar dataKey="Hybrid" fill="#F59E0B" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Engine Metric Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* FSM Card */}
            <div className="tg-panel p-5 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-[var(--tg-border-subtle)]">
                <div className="flex items-center gap-2">
                  <Binary className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-mono font-semibold uppercase text-[var(--tg-text-primary)]">
                    FSM Engine
                  </span>
                </div>
                <span className="tg-badge tg-badge-emerald">Deterministic</span>
              </div>
              <div className="space-y-2 text-xs font-mono">
                <div className="flex justify-between">
                  <span className="text-[var(--tg-text-muted)]">Precision</span>
                  <span className="text-[var(--tg-text-primary)] font-semibold">
                    {engines.fsm?.precision !== undefined ? `${(engines.fsm.precision * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--tg-text-muted)]">Recall</span>
                  <span className="text-[var(--tg-text-primary)] font-semibold">
                    {engines.fsm?.recall !== undefined ? `${(engines.fsm.recall * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--tg-text-muted)]">F1 Score</span>
                  <span className="text-emerald-400 font-semibold">
                    {engines.fsm?.f1_score !== undefined ? `${(engines.fsm.f1_score * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--tg-text-muted)]">False Positive Rate</span>
                  <span className="text-[var(--tg-text-secondary)]">
                    {engines.fsm?.false_positive_rate !== undefined ? `${(engines.fsm.false_positive_rate * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
              </div>
            </div>

            {/* ML Card */}
            <div className="tg-panel p-5 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-[var(--tg-border-subtle)]">
                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-blue-400" />
                  <span className="text-xs font-mono font-semibold uppercase text-[var(--tg-text-primary)]">
                    Isolation Forest ML
                  </span>
                </div>
                <span className="tg-badge tg-badge-blue">Statistical</span>
              </div>
              <div className="space-y-2 text-xs font-mono">
                <div className="flex justify-between">
                  <span className="text-[var(--tg-text-muted)]">Precision</span>
                  <span className="text-[var(--tg-text-primary)] font-semibold">
                    {engines.ml?.precision !== undefined ? `${(engines.ml.precision * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--tg-text-muted)]">Recall</span>
                  <span className="text-[var(--tg-text-primary)] font-semibold">
                    {engines.ml?.recall !== undefined ? `${(engines.ml.recall * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--tg-text-muted)]">F1 Score</span>
                  <span className="text-blue-400 font-semibold">
                    {engines.ml?.f1_score !== undefined ? `${(engines.ml.f1_score * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--tg-text-muted)]">False Positive Rate</span>
                  <span className="text-[var(--tg-text-secondary)]">
                    {engines.ml?.false_positive_rate !== undefined ? `${(engines.ml.false_positive_rate * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
              </div>
            </div>

            {/* Hybrid Card */}
            <div className="tg-panel p-5 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-[var(--tg-border-subtle)]">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  <span className="text-xs font-mono font-semibold uppercase text-[var(--tg-text-primary)]">
                    Hybrid Consensus
                  </span>
                </div>
                <span className="tg-badge tg-badge-amber">Weighted</span>
              </div>
              <div className="space-y-2 text-xs font-mono">
                <div className="flex justify-between">
                  <span className="text-[var(--tg-text-muted)]">Precision</span>
                  <span className="text-[var(--tg-text-primary)] font-semibold">
                    {engines.hybrid?.precision !== undefined ? `${(engines.hybrid.precision * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--tg-text-muted)]">Recall</span>
                  <span className="text-[var(--tg-text-primary)] font-semibold">
                    {engines.hybrid?.recall !== undefined ? `${(engines.hybrid.recall * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--tg-text-muted)]">F1 Score</span>
                  <span className="text-amber-400 font-semibold">
                    {engines.hybrid?.f1_score !== undefined ? `${(engines.hybrid.f1_score * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--tg-text-muted)]">False Positive Rate</span>
                  <span className="text-[var(--tg-text-secondary)]">
                    {engines.hybrid?.false_positive_rate !== undefined ? `${(engines.hybrid.false_positive_rate * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="tg-panel p-12 text-center space-y-3">
          <FlaskConical className="w-10 h-10 text-[var(--tg-text-muted)] mx-auto opacity-40" />
          <h3 className="text-sm font-mono font-semibold text-[var(--tg-text-primary)]">
            No Evaluation Selected
          </h3>
          <p className="text-xs text-[var(--tg-text-muted)] max-w-sm mx-auto">
            Choose a benchmark dataset from the selector above to inspect cross-engine evaluation scores or run inference on demand.
          </p>
        </div>
      )}
    </div>
  );
}

export default DetectionLab;
