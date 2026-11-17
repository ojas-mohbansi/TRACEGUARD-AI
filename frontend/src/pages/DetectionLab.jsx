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

  // Showcase state
  const [activeLabTab, setActiveLabTab] = useState('showcase'); // 'showcase' | 'benchmark'
  const [showcaseRunning, setShowcaseRunning] = useState(false);
  const [showcaseResult, setShowcaseResult] = useState(null);
  const [showcaseResetMsg, setShowcaseResetMsg] = useState('');

  const handleRunShowcase = async (scenarioId) => {
    setShowcaseRunning(true);
    setShowcaseResetMsg('');
    try {
      const res = await api.runShowcaseScenario(scenarioId);
      setShowcaseResult(res);
    } catch (err) {
      alert(`Showcase run failed: ${err.message}`);
    } finally {
      setShowcaseRunning(false);
    }
  };

  const handleResetShowcase = async () => {
    try {
      const res = await api.resetShowcaseData();
      setShowcaseResetMsg(res.message);
      setShowcaseResult(null);
    } catch (err) {
      alert(`Reset failed: ${err.message}`);
    }
  };

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
    true
  );

  const handleSelectDataset = (dsId) => {
    setSelectedDatasetId(dsId);
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

  const datasets = Array.isArray(datasetsData)
    ? datasetsData
    : (datasetsData?.datasets || []);
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
      {/* Editorial Header & Tab Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--tg-border-subtle)]">
        <div>
          <div className="flex items-center gap-2">
            <FlaskConical className="w-4 h-4 text-[var(--tg-accent-emerald)]" />
            <h1 className="text-lg font-semibold tracking-tight text-[var(--tg-text-primary)]">
              Detection Benchmark & Academic Showcase Lab
            </h1>
          </div>
          <p className="text-xs text-[var(--tg-text-muted)] mt-1">
            Empirical comparative analysis of FSM state invariance, Isolation Forest ML anomaly scores, and Hybrid consensus.
          </p>
        </div>

        {/* Lab Navigation Mode Tabs */}
        <div className="flex items-center p-1 rounded-lg bg-[var(--tg-bg-surface)] border border-[var(--tg-border-subtle)] text-xs font-mono">
          <button
            onClick={() => setActiveLabTab('showcase')}
            className={`px-3 py-1 rounded font-semibold transition-colors ${
              activeLabTab === 'showcase'
                ? 'bg-[var(--tg-accent-emerald)] text-black shadow-sm'
                : 'text-[var(--tg-text-secondary)] hover:text-[var(--tg-text-primary)]'
            }`}
          >
            Academic Showcase (4 Scenarios)
          </button>
          <button
            onClick={() => setActiveLabTab('benchmark')}
            className={`px-3 py-1 rounded font-semibold transition-colors ${
              activeLabTab === 'benchmark'
                ? 'bg-[var(--tg-accent-emerald)] text-black shadow-sm'
                : 'text-[var(--tg-text-secondary)] hover:text-[var(--tg-text-primary)]'
            }`}
          >
            Dataset Benchmarks
          </button>
        </div>
      </div>

      {/* TAB 1: ACADEMIC DETECTION ENGINE SHOWCASE */}
      {activeLabTab === 'showcase' && (
        <div className="space-y-5">
          {/* Showcase Control Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl tg-panel border border-[var(--tg-border-subtle)]">
            <div>
              <div className="flex items-center gap-2 text-xs font-mono font-semibold text-[var(--tg-text-primary)] uppercase">
                <Target className="w-4 h-4 text-[var(--tg-accent-emerald)]" />
                <span>Detection Engine Showcase — Interactive Verification</span>
              </div>
              <p className="text-[11px] text-[var(--tg-text-muted)] mt-0.5">
                Run controlled real-time sequences through the real detection pipeline to prove independent FSM and ML capabilities.
              </p>
            </div>

            <button
              onClick={handleResetShowcase}
              className="tg-btn-secondary text-xs flex items-center gap-1.5 self-start sm:self-auto"
              title="Clean demonstration alerts and events without touching real alerts"
            >
              <span>Reset Demo Data</span>
            </button>
          </div>

          {showcaseResetMsg && (
            <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-xs font-mono text-[var(--tg-accent-emerald)] flex items-center gap-2">
              <CheckCircle className="w-4 h-4 shrink-0" />
              <span>{showcaseResetMsg}</span>
            </div>
          )}

          {/* 4 Interactive Scenario Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Scenario 1: Normal Flow */}
            <div className="tg-panel p-4 flex flex-col justify-between space-y-3 font-mono border-t-2 border-t-emerald-500">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-[var(--tg-text-muted)] uppercase">Scenario 1</span>
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold">NORMAL</span>
                </div>
                <h3 className="text-xs font-bold text-[var(--tg-text-primary)] mt-1">Legitimate Flow</h3>
                <p className="text-[11px] text-[var(--tg-text-secondary)] mt-1">
                  Canonical HTTP DFA sequence (CONNECT → REQUEST → AUTH → 200 → CLOSE) with typical payload.
                </p>
                <div className="mt-2 text-[10px] text-[var(--tg-text-muted)] space-y-0.5 border-t border-[var(--tg-border-subtle)] pt-2">
                  <div><strong>FSM:</strong> Conforms (CLOSED)</div>
                  <div><strong>ML:</strong> Normal Profile</div>
                  <div><strong>Result:</strong> No Alert</div>
                </div>
              </div>
              <button
                onClick={() => handleRunShowcase('normal')}
                disabled={showcaseRunning}
                className="w-full tg-btn-secondary text-xs flex items-center justify-center gap-1"
              >
                <Play className="w-3 h-3 fill-current text-[var(--tg-accent-emerald)]" />
                <span>Run Legitimate</span>
              </button>
            </div>

            {/* Scenario 2: FSM-Only Violation */}
            <div className="tg-panel p-4 flex flex-col justify-between space-y-3 font-mono border-t-2 border-t-cyan-500">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-[var(--tg-text-muted)] uppercase">Scenario 2</span>
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-400 font-bold">FSM ONLY</span>
                </div>
                <h3 className="text-xs font-bold text-[var(--tg-text-primary)] mt-1">FSM Violation</h3>
                <p className="text-[11px] text-[var(--tg-text-secondary)] mt-1">
                  Post-close illegal request transition violating state invariant into absorbing TRAP state.
                </p>
                <div className="mt-2 text-[10px] text-[var(--tg-text-muted)] space-y-0.5 border-t border-[var(--tg-border-subtle)] pt-2">
                  <div><strong>FSM:</strong> Violation (TRAP)</div>
                  <div><strong>ML:</strong> Normal Feature Profile</div>
                  <div><strong>Attribution:</strong> <span className="text-cyan-400 font-bold">fsm (≥60% floor)</span></div>
                </div>
              </div>
              <button
                onClick={() => handleRunShowcase('fsm_only')}
                disabled={showcaseRunning}
                className="w-full tg-btn-secondary text-xs flex items-center justify-center gap-1 hover:border-cyan-500/40"
              >
                <Play className="w-3 h-3 fill-current text-cyan-400" />
                <span>Run FSM Violation</span>
              </button>
            </div>

            {/* Scenario 3: ML-Only Anomaly */}
            <div className="tg-panel p-4 flex flex-col justify-between space-y-3 font-mono border-t-2 border-t-blue-500">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-[var(--tg-text-muted)] uppercase">Scenario 3</span>
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 font-bold">ML ONLY</span>
                </div>
                <h3 className="text-xs font-bold text-[var(--tg-text-primary)] mt-1">ML Outlier</h3>
                <p className="text-[11px] text-[var(--tg-text-secondary)] mt-1">
                  Protocol conforms to DFA, but session exhibits anomalous 4.5MB exfiltration byte burst.
                </p>
                <div className="mt-2 text-[10px] text-[var(--tg-text-muted)] space-y-0.5 border-t border-[var(--tg-border-subtle)] pt-2">
                  <div><strong>FSM:</strong> Conforms (CLOSED)</div>
                  <div><strong>ML:</strong> Isolation Forest Outlier</div>
                  <div><strong>Attribution:</strong> <span className="text-blue-400 font-bold">ml (S_ML ≥ 0.55)</span></div>
                </div>
              </div>
              <button
                onClick={() => handleRunShowcase('ml_only')}
                disabled={showcaseRunning}
                className="w-full tg-btn-secondary text-xs flex items-center justify-center gap-1 hover:border-blue-500/40"
              >
                <Play className="w-3 h-3 fill-current text-blue-400" />
                <span>Run ML Outlier</span>
              </button>
            </div>

            {/* Scenario 4: Hybrid Consensus */}
            <div className="tg-panel p-4 flex flex-col justify-between space-y-3 font-mono border-t-2 border-t-purple-500">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-[var(--tg-text-muted)] uppercase">Scenario 4</span>
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-400 font-bold">HYBRID</span>
                </div>
                <h3 className="text-xs font-bold text-[var(--tg-text-primary)] mt-1">Hybrid Consensus</h3>
                <p className="text-[11px] text-[var(--tg-text-secondary)] mt-1">
                  Out-of-order 200 response without prior request plus massive volume burst. Both engines flag.
                </p>
                <div className="mt-2 text-[10px] text-[var(--tg-text-muted)] space-y-0.5 border-t border-[var(--tg-border-subtle)] pt-2">
                  <div><strong>FSM:</strong> Violation (TRAP)</div>
                  <div><strong>ML:</strong> Statistical Outlier</div>
                  <div><strong>Attribution:</strong> <span className="text-purple-400 font-bold">hybrid (Consensus)</span></div>
                </div>
              </div>
              <button
                onClick={() => handleRunShowcase('hybrid')}
                disabled={showcaseRunning}
                className="w-full tg-btn-primary text-xs flex items-center justify-center gap-1"
              >
                <Play className="w-3 h-3 fill-current text-purple-300" />
                <span>Run Hybrid Consensus</span>
              </button>
            </div>
          </div>

          {/* Showcase Live Execution Results Panel */}
          {showcaseResult && (
            <div className="tg-panel p-5 space-y-4 font-mono text-xs border border-[var(--tg-border-default)] animate-fadeIn">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[var(--tg-border-subtle)]">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs uppercase font-bold text-[var(--tg-text-primary)]">
                      Showcase Execution Result: {showcaseResult.scenario.toUpperCase()}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-[var(--tg-accent-emerald)] border border-emerald-500/30 font-bold">
                      {showcaseResult.source_label}
                    </span>
                  </div>
                  <div className="text-[11px] text-[var(--tg-text-muted)] mt-0.5">
                    Session ID: <strong className="text-[var(--tg-text-primary)]">{showcaseResult.session_id}</strong> | Events: {showcaseResult.events_count}
                  </div>
                </div>

                {showcaseResult.created_alert ? (
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] text-[var(--tg-text-muted)]">Attributed Alert:</span>
                    <span className={`px-2.5 py-1 rounded text-xs font-bold border ${
                      showcaseResult.created_alert.engine === 'fsm'
                        ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                        : showcaseResult.created_alert.engine === 'ml'
                        ? 'bg-blue-500/20 text-blue-300 border-blue-500/40'
                        : 'bg-purple-500/20 text-purple-300 border-purple-500/40'
                    }`}>
                      {showcaseResult.created_alert.engine.toUpperCase()} ENGINE (Risk: {showcaseResult.created_alert.risk_score}%)
                    </span>
                  </div>
                ) : (
                  <span className="px-2.5 py-1 rounded text-xs font-bold bg-emerald-500/10 text-[var(--tg-accent-emerald)] border border-emerald-500/30">
                    NORMAL (No Alert Warranted)
                  </span>
                )}
              </div>

              {/* 3 Component Evaluation Columns */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Column 1: FSM Evaluation */}
                <div className="p-3.5 rounded-lg bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] space-y-2">
                  <div className="flex items-center justify-between text-xs font-bold">
                    <span className="text-cyan-400">1. Deterministic FSM</span>
                    <span className={showcaseResult.fsm_evaluation.violation ? 'text-[var(--tg-status-danger)]' : 'text-[var(--tg-accent-emerald)]'}>
                      {showcaseResult.fsm_evaluation.violation ? 'VIOLATION' : 'CONFORMS'}
                    </span>
                  </div>
                  <div className="text-[11px] text-[var(--tg-text-secondary)] space-y-1">
                    <div>Ending State: <strong className="text-[var(--tg-text-primary)]">{showcaseResult.fsm_evaluation.final_state}</strong></div>
                    <div>FSM Score: <strong>{showcaseResult.fsm_evaluation.risk_score}%</strong></div>
                    <div className="text-[10px] text-[var(--tg-text-muted)] leading-tight pt-1">
                      {showcaseResult.fsm_evaluation.explanation}
                    </div>
                  </div>
                </div>

                {/* Column 2: ML Evaluation */}
                <div className="p-3.5 rounded-lg bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] space-y-2">
                  <div className="flex items-center justify-between text-xs font-bold">
                    <span className="text-blue-400">2. Statistical ML</span>
                    <span className={showcaseResult.ml_evaluation.prediction === 'anomalous' ? 'text-[var(--tg-status-danger)]' : 'text-[var(--tg-accent-emerald)]'}>
                      {showcaseResult.ml_evaluation.prediction.toUpperCase()}
                    </span>
                  </div>
                  <div className="text-[11px] text-[var(--tg-text-secondary)] space-y-1">
                    <div>Anomaly Score S_ML: <strong>{showcaseResult.ml_evaluation.anomaly_score}</strong></div>
                    <div>ML Risk Score: <strong>{showcaseResult.ml_evaluation.risk_score}%</strong></div>
                    <div className="text-[10px] text-[var(--tg-text-muted)] leading-tight pt-1">
                      Isolation Forest model evaluated 15 flow features without heuristic shortcuts.
                    </div>
                  </div>
                </div>

                {/* Column 3: Hybrid Synthesis */}
                <div className="p-3.5 rounded-lg bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] space-y-2">
                  <div className="flex items-center justify-between text-xs font-bold">
                    <span className="text-purple-400">3. Hybrid Synthesis</span>
                    <span className="text-[var(--tg-text-primary)] font-bold">
                      S_h: {showcaseResult.hybrid_evaluation.combined_risk_score}%
                    </span>
                  </div>
                  <div className="text-[11px] text-[var(--tg-text-secondary)] space-y-1">
                    <div>Attribution: <strong className="uppercase text-[var(--tg-accent-emerald)]">{showcaseResult.hybrid_evaluation.attribution}</strong></div>
                    <div>Formula: <code>{showcaseResult.hybrid_evaluation.formula}</code></div>
                    {showcaseResult.hybrid_evaluation.floor_applied && (
                      <div className="text-[10px] text-amber-400 font-semibold">
                        ★ Mandatory 60% FSM Risk Floor Applied
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: DATASET BENCHMARKS (PRESERVED FROM PHASE 15) */}
      {activeLabTab === 'benchmark' && (
        <>
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
              <Binary className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)]" />
              <span>{runningEngines.fsm ? 'Running FSM...' : 'Run FSM'}</span>
            </button>

            <button
              onClick={() => handleRunEngine('ml')}
              disabled={runningEngines.ml || !selectedDatasetId}
              className="flex-1 tg-btn-secondary text-xs disabled:opacity-40"
            >
              <Cpu className="w-3.5 h-3.5 text-[var(--tg-accent-blue)]" />
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
          <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-xs font-mono text-emerald-700 dark:text-emerald-300 flex items-center gap-2">
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
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--tg-border-subtle)" />
                  <XAxis dataKey="metric" stroke="var(--tg-text-muted)" fontSize={11} tickLine={false} />
                  <YAxis stroke="var(--tg-text-muted)" fontSize={11} tickLine={false} domain={[0, 100]} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--tg-bg-surface)',
                      borderColor: 'var(--tg-border-default)',
                      borderRadius: '8px',
                      fontSize: '11px',
                      fontFamily: 'JetBrains Mono',
                      color: 'var(--tg-text-primary)',
                      boxShadow: 'var(--tg-shadow-md)',
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
                  <Binary className="w-4 h-4 text-[var(--tg-accent-emerald)]" />
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
                  <span className="text-[var(--tg-accent-emerald)] font-semibold">
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
                  <Cpu className="w-4 h-4 text-[var(--tg-accent-blue)]" />
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
                  <span className="text-[var(--tg-accent-blue)] font-semibold">
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
                  <Sparkles className="w-4 h-4 text-[var(--tg-status-warning)]" />
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
                  <span className="text-[var(--tg-status-warning)] font-semibold">
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
        </>
      )}
    </div>
  );
}

export default DetectionLab;
