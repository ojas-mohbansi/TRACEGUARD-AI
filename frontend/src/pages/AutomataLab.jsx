import React, { useState, useEffect, useMemo } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Play,
  RotateCcw,
  StepForward,
  StepBack,
  AlertTriangle,
  CheckCircle2,
  GitBranch,
  BookOpen,
  Table,
  FlaskConical,
  Activity,
  Layers,
  HelpCircle,
  Search,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Cpu
} from 'lucide-react';
import api from '../services/api';
import { useApi } from '../hooks/useApi';
import LoadingSpinner from '../components/LoadingSpinner';

const STATE_POSITIONS = {
  IDLE: { x: 60, y: 220 },
  CONNECTED: { x: 260, y: 220 },
  REQUEST_RECEIVED: { x: 480, y: 220 },
  AUTH_CHECKED: { x: 740, y: 100 },
  AUTH_FAILED: { x: 740, y: 340 },
  RESPONSE_SENT: { x: 1000, y: 220 },
  ERROR: { x: 740, y: 480 },
  CLOSED: { x: 1240, y: 220 },
  TRAP: { x: 600, y: 620 },
};

const PRESET_SEQUENCES = [
  {
    name: 'Canonical Valid Transaction',
    category: 'Valid (w ∈ L(M))',
    seq: 'CONNECT, REQUEST, AUTH_SUCCESS, RESPONSE_200, CLOSE',
    desc: 'Normal client authentication and 200 OK delivery terminating in CLOSED.'
  },
  {
    name: 'Pipelined Keep-Alive Session',
    category: 'Valid Cyclic',
    seq: 'CONNECT, REQUEST, AUTH_SUCCESS, RESPONSE_200, REQUEST, AUTH_SUCCESS, RESPONSE_200, CLOSE',
    desc: 'Two sequential HTTP transactions within a single persistent connection.'
  },
  {
    name: 'Auth Failure & 401 Response',
    category: 'Valid Security Exception',
    seq: 'CONNECT, REQUEST, AUTH_FAILURE, RESPONSE_401, CLOSE',
    desc: 'Rejected credentials properly generating an HTTP 401 response.'
  },
  {
    name: 'Premature Response Violation',
    category: 'Invalid (Out-of-Order)',
    seq: 'CONNECT, RESPONSE_200, REQUEST, CLOSE',
    desc: 'Illegal server response emitted before client sent request.'
  },
  {
    name: 'Authentication Bypass Violation',
    category: 'Invalid (Security Invariant)',
    seq: 'CONNECT, REQUEST, RESPONSE_200, CLOSE',
    desc: 'Attempt to deliver status 200 without executing authentication check.'
  },
  {
    name: 'Malformed Request Error Trap',
    category: 'Valid Anomaly Handled',
    seq: 'CONNECT, REQUEST, MALFORMED, ERROR_RESPONSE, CLOSE',
    desc: 'Bad request properly routed to ERROR state and handled via error response.'
  },
  {
    name: 'Valid Incomplete Prefix',
    category: 'Incomplete Prefix',
    seq: 'CONNECT, REQUEST, AUTH_SUCCESS',
    desc: 'Legal sequence currently in progress, ending in non-accepting state AUTH_CHECKED.'
  },
  {
    name: 'Connection Idle Timeout',
    category: 'Valid Termination',
    seq: 'CONNECT, TIMEOUT',
    desc: 'Connection timing out before client submits request.'
  }
];

export function AutomataLab() {
  const [activeTab, setActiveTab] = useState('visualizer');
  const { data: fsmDef, loading: loadingFsm } = useApi(() => api.getHttpFsm());
  const { data: formalData, loading: loadingFormal } = useApi(() => api.getFormalAutomaton());

  const [inputSequence, setInputSequence] = useState('CONNECT, REQUEST, AUTH_SUCCESS, RESPONSE_200, CLOSE');
  const [stepData, setStepData] = useState(null);
  const [stepIndex, setStepIndex] = useState(-1);
  const [currentState, setCurrentState] = useState('IDLE');
  const [executing, setExecuting] = useState(false);
  const [searchTable, setSearchTable] = useState('');
  const [selectedStateFilter, setSelectedStateFilter] = useState('ALL');

  const parsedSymbols = useMemo(() => {
    return inputSequence
      .split(',')
      .map((s) => s.trim().toUpperCase())
      .filter(Boolean);
  }, [inputSequence]);

  const runSequence = async () => {
    setExecuting(true);
    try {
      const res = await api.stepExecuteAutomaton(parsedSymbols);
      setStepData(res);
      setStepIndex(res.steps.length > 0 ? 0 : -1);
      if (res.steps.length > 0) {
        setCurrentState(res.steps[0].valid ? res.steps[0].next_state : res.steps[0].current_state);
      } else {
        setCurrentState('IDLE');
      }
    } catch (err) {
      console.error('Failed to execute DFA sequence:', err);
    } finally {
      setExecuting(false);
    }
  };

  const handleReset = () => {
    setStepIndex(-1);
    setCurrentState('IDLE');
    setStepData(null);
  };

  const handleStepForward = () => {
    if (!stepData || stepIndex >= stepData.steps.length - 1) return;
    const nextIdx = stepIndex + 1;
    setStepIndex(nextIdx);
    const step = stepData.steps[nextIdx];
    setCurrentState(step.valid ? step.next_state : step.current_state);
  };

  const handleStepBackward = () => {
    if (!stepData || stepIndex <= 0) {
      handleReset();
      return;
    }
    const prevIdx = stepIndex - 1;
    setStepIndex(prevIdx);
    const step = stepData.steps[prevIdx];
    setCurrentState(step.valid ? step.next_state : step.current_state);
  };

  const nodes = useMemo(() => {
    if (!formalData?.Q_states) return [];
    return formalData.Q_states.map((st) => {
      const isCurrent = st.id === currentState;
      const isInitial = st.is_initial;
      const isFinal = st.is_accepting;
      const isTrap = st.is_trap;
      const pos = STATE_POSITIONS[st.id] || { x: 100, y: 100 };

      let borderColor = 'rgba(255, 255, 255, 0.12)';
      let bgColor = '#141B2B';
      let textColor = '#F8FAFC';

      if (isCurrent) {
        if (isTrap) {
          borderColor = '#EF4444';
          bgColor = '#2A151B';
          textColor = '#EF4444';
        } else {
          borderColor = '#10B981';
          bgColor = '#112922';
          textColor = '#10B981';
        }
      } else if (isTrap) {
        borderColor = 'rgba(239, 68, 68, 0.4)';
        textColor = '#EF4444';
      } else if (isFinal) {
        borderColor = '#F59E0B';
      } else if (isInitial) {
        borderColor = '#3B82F6';
      }

      return {
        id: st.id,
        position: pos,
        data: {
          label: (
            <div className="text-center font-mono">
              <div className="flex items-center justify-center gap-1 mb-0.5">
                {isInitial && <span className="text-[8px] px-1 rounded bg-blue-500/20 text-blue-400 font-semibold">q₀</span>}
                {isFinal && <span className="text-[8px] px-1 rounded bg-amber-500/20 text-amber-400 font-semibold">F</span>}
                {isTrap && <span className="text-[8px] px-1 rounded bg-rose-500/20 text-rose-400 font-semibold">TRAP</span>}
                <div className="text-[11px] font-semibold tracking-wider">{st.id}</div>
              </div>
              <div className="text-[9px] text-[var(--tg-text-muted)] truncate max-w-[130px]">{st.meaning}</div>
            </div>
          ),
        },
        style: {
          background: bgColor,
          color: textColor,
          border: `1.5px solid ${borderColor}`,
          borderRadius: '8px',
          padding: '8px 12px',
          boxShadow: isCurrent ? (isTrap ? '0 0 16px rgba(239, 68, 68, 0.35)' : '0 0 16px rgba(16, 185, 129, 0.35)') : '0 1px 3px rgba(0,0,0,0.3)',
          transition: 'all 0.2s ease',
        },
      };
    });
  }, [formalData, currentState]);

  const edges = useMemo(() => {
    if (!fsmDef?.transitions) return [];
    const activeStep = stepData && stepIndex >= 0 ? stepData.steps[stepIndex] : null;

    return fsmDef.transitions.map((tr, idx) => {
      const isActiveTransition =
        activeStep &&
        activeStep.valid &&
        activeStep.current_state === tr.from &&
        activeStep.next_state === tr.to &&
        activeStep.symbol === tr.event;

      return {
        id: `e-${tr.from}-${tr.to}-${tr.event}-${idx}`,
        source: tr.from,
        target: tr.to,
        label: tr.event,
        animated: isActiveTransition,
        style: {
          stroke: isActiveTransition ? '#10B981' : '#334155',
          strokeWidth: isActiveTransition ? 2.5 : 1,
        },
        labelStyle: {
          fill: isActiveTransition ? '#10B981' : '#8896AB',
          fontSize: 9,
          fontWeight: isActiveTransition ? '600' : 'normal',
          fontFamily: 'JetBrains Mono, monospace',
        },
        labelBgStyle: {
          fill: '#0E131F',
          fillOpacity: 0.95,
          rx: 3,
          ry: 3,
        },
      };
    });
  }, [fsmDef, stepData, stepIndex]);

  if (loadingFsm || loadingFormal) {
    return <LoadingSpinner text="Retrieving formal automata specification..." />;
  }

  return (
    <div className="space-y-6">
      {/* Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-[var(--tg-border-subtle)]">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400" />
            <h1 className="text-lg font-semibold tracking-tight text-[var(--tg-text-primary)]">
              Automata Laboratory
            </h1>
          </div>
          <p className="text-xs text-[var(--tg-text-muted)] mt-1">
            Deterministic Finite Automaton (DFA) verification, interactive step execution, and complete transition matrix.
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-1 p-1 rounded-lg bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] text-xs font-mono">
          {[
            { id: 'visualizer', label: 'Interactive Automaton', icon: GitBranch },
            { id: 'formal', label: '5-Tuple Definition', icon: BookOpen },
            { id: 'table', label: 'Transition Matrix', icon: Table },
            { id: 'testing', label: 'Automaton Test Suite', icon: FlaskConical },
            { id: 'theory', label: 'TOC Documentation', icon: Layers },
          ].map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition ${
                  active
                    ? 'bg-[var(--tg-bg-surface)] text-emerald-400 border border-emerald-500/30 shadow-xs'
                    : 'text-[var(--tg-text-secondary)] hover:text-[var(--tg-text-primary)]'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* TAB 1: INTERACTIVE AUTOMATON & STEPPER */}
      {activeTab === 'visualizer' && (
        <div className="space-y-6">
          {/* Controls Bar */}
          <div className="tg-panel p-5 space-y-3">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div className="flex-1">
                <label className="text-[11px] font-mono text-[var(--tg-text-muted)] block mb-1 uppercase">
                  Input Event String (symbols separated by commas):
                </label>
                <input
                  type="text"
                  value={inputSequence}
                  onChange={(e) => setInputSequence(e.target.value)}
                  placeholder="CONNECT, REQUEST, AUTH_SUCCESS, RESPONSE_200, CLOSE"
                  className="tg-input text-xs font-mono"
                />
              </div>

              <div className="flex items-center gap-2 pt-2 md:pt-4">
                <button
                  onClick={runSequence}
                  disabled={executing || parsedSymbols.length === 0}
                  className="tg-btn-primary text-xs"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>{executing ? 'Evaluating...' : 'Load & Run'}</span>
                </button>

                <button
                  onClick={handleStepBackward}
                  disabled={!stepData || stepIndex <= 0}
                  className="tg-btn-secondary text-xs disabled:opacity-40"
                >
                  <StepBack className="w-3.5 h-3.5" />
                  <span>Back</span>
                </button>

                <button
                  onClick={handleStepForward}
                  disabled={!stepData || stepIndex >= (stepData?.steps?.length || 0) - 1}
                  className="tg-btn-secondary text-xs disabled:opacity-40"
                >
                  <span>Step</span>
                  <StepForward className="w-3.5 h-3.5" />
                </button>

                <button
                  onClick={handleReset}
                  className="p-2 rounded-md tg-btn-secondary text-xs"
                  title="Reset Automaton State"
                  aria-label="Reset Automaton State"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* Presets */}
            <div className="flex flex-wrap items-center gap-1.5 pt-2 border-t border-[var(--tg-border-subtle)]">
              <span className="text-[11px] font-mono text-[var(--tg-text-muted)] mr-1">Presets:</span>
              {PRESET_SEQUENCES.map((preset) => (
                <button
                  key={preset.name}
                  onClick={() => {
                    setInputSequence(preset.seq);
                    handleReset();
                  }}
                  className="px-2 py-0.5 rounded text-[10px] font-mono bg-white/5 hover:bg-white/10 text-cyan-400 border border-cyan-500/20 transition"
                  title={preset.desc}
                >
                  {preset.name}
                </button>
              ))}
            </div>
          </div>

          {/* Graph & Execution Inspector */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
            {/* ReactFlow Canvas */}
            <div className="lg:col-span-8 h-[550px] tg-panel overflow-hidden relative">
              <ReactFlow nodes={nodes} edges={edges} fitView>
                <Background color="rgba(255,255,255,0.06)" gap={20} size={1} />
                <Controls className="bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] text-[var(--tg-text-primary)]" />
                <MiniMap
                  nodeColor={(n) => (n.id === currentState ? '#10B981' : '#334155')}
                  maskColor="rgba(10, 13, 20, 0.75)"
                  className="border border-[var(--tg-border-subtle)] rounded-md overflow-hidden"
                />
              </ReactFlow>

              <div className="absolute top-4 left-4 p-3 rounded-lg bg-[var(--tg-bg-base)]/90 backdrop-blur-md border border-[var(--tg-border-default)] text-xs font-mono space-y-1 shadow-md">
                <div className="flex items-center gap-2">
                  <span className="text-[var(--tg-text-muted)]">CURRENT DFA STATE:</span>
                  <span className="text-emerald-400 font-bold">{currentState}</span>
                </div>
                <div className="flex items-center gap-3 text-[10px] text-[var(--tg-text-muted)]">
                  <span>Step: {stepIndex >= 0 ? stepIndex + 1 : 0} / {parsedSymbols.length}</span>
                  <span>q₀: IDLE</span>
                  <span>F: &#123;CLOSED&#125;</span>
                </div>
              </div>
            </div>

            {/* Stepper Details & Invariant Inspector */}
            <div className="lg:col-span-4 tg-panel p-5 flex flex-col h-[550px]">
              <div className="mb-3">
                <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
                  Step-by-Step Transition Audit
                </h2>
                <p className="text-[10px] font-mono text-[var(--tg-text-muted)]">Formal lookup: δ(q, σ) → q'</p>
              </div>

              {stepData ? (
                <div className="flex-1 flex flex-col justify-between overflow-hidden">
                  <div className="overflow-y-auto space-y-2 pr-1 flex-1">
                    {stepData.steps.map((st, idx) => {
                      const isCurrent = idx === stepIndex;
                      return (
                        <div
                          key={idx}
                          onClick={() => {
                            setStepIndex(idx);
                            setCurrentState(st.valid ? st.next_state : st.current_state);
                          }}
                          className={`p-2.5 rounded-lg border font-mono text-xs cursor-pointer transition ${
                            isCurrent
                              ? 'border-emerald-500 bg-[var(--tg-bg-elevated)] shadow-xs'
                              : st.valid
                              ? 'border-[var(--tg-border-subtle)] bg-[var(--tg-bg-base)] text-[var(--tg-text-secondary)]'
                              : 'border-rose-500/40 bg-rose-500/10 text-rose-400'
                          }`}
                        >
                          <div className="flex items-center justify-between text-[10px]">
                            <span className="font-semibold">Step {st.step_number}</span>
                            <span
                              className={`px-1.5 py-0.2 rounded font-semibold ${
                                st.valid ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                              }`}
                            >
                              {st.valid ? 'VALID δ' : 'REJECTED ∅'}
                            </span>
                          </div>
                          <div className="text-[11px] font-semibold text-[var(--tg-text-primary)] mt-1">{st.delta_lookup}</div>
                          <div className="text-[10px] text-[var(--tg-text-muted)] mt-0.5 leading-tight">{st.explanation}</div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Verdict Footer */}
                  <div
                    className={`mt-4 p-3 rounded-lg border font-mono text-xs ${
                      stepData.verdict === 'ACCEPTED'
                        ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                        : stepData.verdict === 'INCOMPLETE_VALID'
                        ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                        : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
                    }`}
                  >
                    <div className="flex justify-between items-center font-semibold">
                      <span>VERDICT: {stepData.verdict}</span>
                      <span>State: {stepData.final_state}</span>
                    </div>
                    {stepData.rejection_reason && (
                      <p className="text-[10px] mt-1 leading-normal opacity-90">{stepData.rejection_reason}</p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-center font-mono text-xs text-[var(--tg-text-muted)]">
                  <GitBranch className="w-8 h-8 opacity-40 mb-2" />
                  <span>Click "Load & Run" to execute the string through the formal automaton.</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: FORMAL 5-TUPLE DEFINITION */}
      {activeTab === 'formal' && formalData && (
        <div className="space-y-6">
          {/* Tuple Banner */}
          <div className="tg-panel p-6 border-emerald-500/30 text-center font-mono space-y-2">
            <span className="text-xs text-[var(--tg-text-muted)] uppercase tracking-wider">Formal Automaton Specification</span>
            <div className="text-2xl font-bold text-emerald-400">{formalData.tuple_notation}</div>
            <p className="text-xs text-[var(--tg-text-muted)] max-w-2xl mx-auto">
              A 5-tuple defining the HTTP protocol state machine as a Deterministic Finite Automaton (DFA) recognized by TraceGuard AI.
            </p>
          </div>

          {/* 5 Components Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Q States */}
            <div className="tg-panel p-5 space-y-3">
              <div className="flex items-center justify-between border-b border-[var(--tg-border-subtle)] pb-2 font-mono">
                <span className="text-xs font-semibold text-blue-400 uppercase">Q: Finite Set of States (|Q| = {formalData.Q_states.length})</span>
              </div>
              <div className="space-y-2 font-mono text-xs">
                {formalData.Q_states.map((st) => (
                  <div key={st.id} className="p-2.5 rounded-lg bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)]">
                    <div className="flex items-center gap-2">
                      <span className="text-emerald-400 font-semibold">{st.id}</span>
                      {st.is_initial && <span className="tg-badge tg-badge-blue">q₀ (Initial)</span>}
                      {st.is_accepting && <span className="tg-badge tg-badge-amber">F (Accepting)</span>}
                    </div>
                    <p className="text-[10px] text-[var(--tg-text-muted)] mt-1">{st.meaning}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Sigma Alphabet */}
            <div className="tg-panel p-5 space-y-3">
              <div className="flex items-center justify-between border-b border-[var(--tg-border-subtle)] pb-2 font-mono">
                <span className="text-xs font-semibold text-blue-400 uppercase">Σ: Finite Alphabet of Event Symbols (|Σ| = {formalData.Sigma_alphabet.length})</span>
              </div>
              <div className="space-y-2 font-mono text-xs">
                {formalData.Sigma_alphabet.map((sym) => (
                  <div key={sym.symbol} className="p-2.5 rounded-lg bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] flex justify-between items-center">
                    <div>
                      <span className="text-[var(--tg-text-primary)] font-semibold">{sym.symbol}</span>
                      <p className="text-[10px] text-[var(--tg-text-muted)]">{sym.meaning}</p>
                    </div>
                    <span className="tg-badge tg-badge-neutral">
                      {sym.category}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Initial & Accepting States & Delta Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 font-mono text-xs">
            <div className="tg-panel p-4">
              <span className="text-[var(--tg-text-muted)]">Initial State (q₀):</span>
              <div className="text-lg font-bold text-blue-400 mt-1">{formalData.q0}</div>
              <p className="text-[10px] text-[var(--tg-text-muted)] mt-1">Socket listener initialized, awaiting TCP handshake.</p>
            </div>
            <div className="tg-panel p-4">
              <span className="text-[var(--tg-text-muted)]">Accepting States Set (F):</span>
              <div className="text-lg font-bold text-amber-400 mt-1">&#123;{formalData.F_accepting.join(', ')}&#125;</div>
              <p className="text-[10px] text-[var(--tg-text-muted)] mt-1">Language acceptance condition: δ*(q₀, w) ∈ F.</p>
            </div>
            <div className="tg-panel p-4">
              <span className="text-[var(--tg-text-muted)]">Transition Cardinality (|δ|):</span>
              <div className="text-lg font-bold text-emerald-400 mt-1">{formalData.transition_function_delta.length} Defined Transitions</div>
              <p className="text-[10px] text-[var(--tg-text-muted)] mt-1">89 undefined cell pairs implicitly map to ∅ (Reject).</p>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: TRANSITION MATRIX & TABLE */}
      {activeTab === 'table' && formalData && (
        <div className="space-y-6">
          <div className="tg-panel p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
                Transition Matrix: δ(q, σ)
              </h2>
              <p className="text-xs text-[var(--tg-text-muted)] mt-0.5">
                Complete deterministic state transition table. Undefined cell pairs yield ∅ (rejection).
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-[var(--tg-text-muted)] absolute left-2.5 top-2.5" />
                <input
                  type="text"
                  placeholder="Filter symbols..."
                  value={searchTable}
                  onChange={(e) => setSearchTable(e.target.value)}
                  className="tg-input pl-8 py-1 text-xs font-mono w-40"
                />
              </div>

              <select
                value={selectedStateFilter}
                onChange={(e) => setSelectedStateFilter(e.target.value)}
                className="tg-select py-1 text-xs font-mono w-36"
              >
                <option value="ALL">All States (Q)</option>
                {formalData.Q_states.map((s) => (
                  <option key={s.id} value={s.id}>{s.id}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Matrix Table */}
          <div className="tg-table-container">
            <table className="tg-table">
              <thead>
                <tr>
                  <th>Current State (q)</th>
                  {formalData.Sigma_alphabet
                    .filter((sym) => !searchTable || sym.symbol.toLowerCase().includes(searchTable.toLowerCase()))
                    .map((sym) => (
                      <th key={sym.symbol} className="text-center text-[10px] whitespace-nowrap">
                        {sym.symbol}
                      </th>
                    ))}
                </tr>
              </thead>
              <tbody>
                {formalData.full_matrix
                  .filter((row) => selectedStateFilter === 'ALL' || row.state === selectedStateFilter)
                  .map((row) => (
                    <tr key={row.state}>
                      <td className="font-mono text-xs font-semibold text-[var(--tg-text-primary)] whitespace-nowrap">
                        <div className="flex items-center gap-1.5">
                          {row.is_initial && <span className="tg-badge tg-badge-blue">q₀</span>}
                          {row.is_accepting && <span className="tg-badge tg-badge-amber">F</span>}
                          <span>{row.state}</span>
                        </div>
                      </td>
                      {formalData.Sigma_alphabet
                        .filter((sym) => !searchTable || sym.symbol.toLowerCase().includes(searchTable.toLowerCase()))
                        .map((sym) => {
                          const target = row.entries[sym.symbol];
                          const isValid = target !== '∅';
                          return (
                            <td
                              key={sym.symbol}
                              className={`text-center font-mono text-xs whitespace-nowrap ${
                                isValid
                                  ? 'text-emerald-400 font-semibold bg-emerald-500/5'
                                  : 'text-[var(--tg-text-muted)] opacity-30'
                              }`}
                            >
                              {target}
                            </td>
                          );
                        })}
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 4: AUTOMATON TEST SUITE */}
      {activeTab === 'testing' && (
        <div className="space-y-6">
          <div className="tg-panel p-5">
            <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
              Automaton Comprehensive Test Battery
            </h2>
            <p className="text-xs text-[var(--tg-text-muted)] mt-0.5">
              Verify formal edge cases: empty strings, invalid first steps, valid incomplete prefixes, authentication bypass attempts, and cyclic keep-alive loops.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {PRESET_SEQUENCES.map((testCase, idx) => (
              <div
                key={idx}
                className="tg-panel p-4 space-y-3 font-mono"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-[var(--tg-text-primary)]">{testCase.name}</span>
                  <span className="tg-badge tg-badge-neutral">
                    {testCase.category}
                  </span>
                </div>
                <p className="text-[11px] text-[var(--tg-text-muted)]">{testCase.desc}</p>
                <div className="p-2 rounded bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] text-[10px] text-emerald-400 break-all">
                  {testCase.seq}
                </div>
                <button
                  onClick={() => {
                    setInputSequence(testCase.seq);
                    setActiveTab('visualizer');
                    setTimeout(() => runSequence(), 100);
                  }}
                  className="w-full tg-btn-secondary text-xs text-emerald-400 hover:text-emerald-300"
                >
                  Load in Interactive Visualizer &#8594;
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 5: THEORY OF COMPUTATION DOCUMENTATION */}
      {activeTab === 'theory' && (
        <div className="space-y-6">
          <div className="tg-panel p-6 space-y-4">
            <h2 className="text-base font-semibold text-emerald-400">Theoretical Foundations & Formal Language Semantics</h2>
            
            <div className="space-y-4 text-xs leading-relaxed text-[var(--tg-text-secondary)]">
              <div>
                <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)] mb-1">
                  1. Regular Languages & Chomsky Hierarchy
                </h3>
                <p>
                  Regular languages represent the foundation of formal language theory (Chomsky Type-3). They are recognizable by finite automata and denotable by regular expressions. In network communication, deterministic protocol transactions naturally constitute regular languages over the protocol event alphabet Σ.
                </p>
              </div>

              <div>
                <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)] mb-1">
                  2. Language Recognition vs. Transition Legality
                </h3>
                <p>
                  A critical distinction in automata theory:
                </p>
                <ul className="list-disc pl-5 space-y-1.5 mt-1.5">
                  <li><strong className="text-emerald-400">Accepted String (w ∈ L(M))</strong>: Every transition is defined in δ and terminal state q ∈ F.</li>
                  <li><strong className="text-amber-400">Valid Incomplete Prefix</strong>: Every transition executed was valid in δ, but sequence ended in q ∉ F. (Normal in-progress network streams).</li>
                  <li><strong className="text-rose-400">Rejected String (w ∉ L(M))</strong>: An event was received where δ(q, σ) = ∅. This constitutes an immediate security violation.</li>
                </ul>
              </div>

              <div>
                <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)] mb-1">
                  3. Role of Supporting Machine Learning
                </h3>
                <p>
                  The FSM detector mathematically proves structural protocol violations. However, an attacker executing 100,000 valid logins per minute generates zero FSM violations. Machine Learning (Isolation Forest) supports the FSM by profiling statistical variances in frequency, payload byte size, and inter-arrival intervals without compromising formal state machine guarantees.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AutomataLab;
