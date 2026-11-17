import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Play,
  Pause,
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
  Cpu,
  Clock,
  Gauge
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
  // -1 indicates Stage 0 (Initial state q0 = IDLE, no symbols consumed yet)
  const [stepIndex, setStepIndex] = useState(-1);
  const [currentState, setCurrentState] = useState('IDLE');
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0); // 0.5x, 1x, 2x
  const [executing, setExecuting] = useState(false);
  const [searchTable, setSearchTable] = useState('');
  const [selectedStateFilter, setSelectedStateFilter] = useState('ALL');

  const playTimerRef = useRef(null);

  const parsedSymbols = useMemo(() => {
    return inputSequence
      .split(',')
      .map((s) => s.trim().toUpperCase())
      .filter(Boolean);
  }, [inputSequence]);

  // Load step execution data from backend
  const fetchSimulationSteps = useCallback(async (symbols) => {
    if (!symbols || symbols.length === 0) return null;
    setExecuting(true);
    try {
      const res = await api.stepExecuteAutomaton(symbols);
      setStepData(res);
      return res;
    } catch (err) {
      console.error('Failed to execute DFA sequence:', err);
      return null;
    } finally {
      setExecuting(false);
    }
  }, []);

  // Reset simulation to Stage 0 (Initial state q0 = IDLE)
  const handleReset = useCallback(() => {
    if (playTimerRef.current) {
      clearInterval(playTimerRef.current);
      playTimerRef.current = null;
    }
    setIsPlaying(false);
    setStepIndex(-1);
    setCurrentState('IDLE');
  }, []);

  // Step Forward: advance by exactly 1 stage
  const handleStepForward = useCallback(async () => {
    let currentData = stepData;
    if (!currentData || currentData.input_symbols?.join(',') !== parsedSymbols.join(',')) {
      currentData = await fetchSimulationSteps(parsedSymbols);
    }
    if (!currentData || !currentData.steps || currentData.steps.length === 0) return;

    if (stepIndex >= currentData.steps.length - 1) {
      setIsPlaying(false);
      return;
    }

    const nextIdx = stepIndex + 1;
    setStepIndex(nextIdx);
    const step = currentData.steps[nextIdx];
    setCurrentState(step.next_state || step.current_state);

    // If step was invalid (entered TRAP), pause progression
    if (!step.valid) {
      setIsPlaying(false);
    }
  }, [stepData, stepIndex, parsedSymbols, fetchSimulationSteps]);

  // Step Backward: move back by 1 stage
  const handleStepBackward = useCallback(() => {
    if (stepIndex <= 0) {
      handleReset();
      return;
    }
    const prevIdx = stepIndex - 1;
    setStepIndex(prevIdx);
    if (stepData && stepData.steps[prevIdx]) {
      const step = stepData.steps[prevIdx];
      setCurrentState(step.next_state || step.current_state);
    } else {
      setCurrentState('IDLE');
    }
  }, [stepIndex, stepData, handleReset]);

  // Auto-play / Pause toggle
  const togglePlay = useCallback(async () => {
    if (isPlaying) {
      setIsPlaying(false);
      return;
    }

    // If starting fresh or at the end, ensure steps are loaded and reset
    let currentData = stepData;
    if (!currentData || currentData.input_symbols?.join(',') !== parsedSymbols.join(',')) {
      currentData = await fetchSimulationSteps(parsedSymbols);
      setStepIndex(-1);
      setCurrentState('IDLE');
    } else if (stepIndex >= (currentData.steps?.length || 0) - 1) {
      setStepIndex(-1);
      setCurrentState('IDLE');
    }

    if (currentData && currentData.steps?.length > 0) {
      setIsPlaying(true);
    }
  }, [isPlaying, stepData, stepIndex, parsedSymbols, fetchSimulationSteps]);

  // Simulation Playback Timer Loop (advances through stages 1 -> 2 -> 3 -> ... -> N)
  useEffect(() => {
    if (!isPlaying) {
      if (playTimerRef.current) {
        clearInterval(playTimerRef.current);
        playTimerRef.current = null;
      }
      return;
    }

    const intervalMs = Math.round(1000 / playbackSpeed);

    playTimerRef.current = setInterval(() => {
      setStepIndex((prevIdx) => {
        if (!stepData || !stepData.steps) {
          setIsPlaying(false);
          return prevIdx;
        }

        const nextIdx = prevIdx + 1;
        if (nextIdx >= stepData.steps.length) {
          setIsPlaying(false);
          return prevIdx;
        }

        const step = stepData.steps[nextIdx];
        setCurrentState(step.next_state || step.current_state);

        // If transition is invalid (routed to TRAP), stop simulation at violation stage
        if (!step.valid) {
          setIsPlaying(false);
        }

        return nextIdx;
      });
    }, intervalMs);

    return () => {
      if (playTimerRef.current) {
        clearInterval(playTimerRef.current);
        playTimerRef.current = null;
      }
    };
  }, [isPlaying, playbackSpeed, stepData]);

  // Nodes for ReactFlow
  const nodes = useMemo(() => {
    if (!formalData?.Q_states) return [];
    return formalData.Q_states.map((st) => {
      const isCurrent = st.id === currentState;
      const isInitial = st.is_initial;
      const isFinal = st.is_accepting;
      const isTrap = st.is_trap;
      const pos = STATE_POSITIONS[st.id] || { x: 100, y: 100 };

      let borderColor = 'var(--tg-border-subtle)';
      let bgColor = 'var(--tg-bg-surface)';
      let textColor = 'var(--tg-text-primary)';

      if (isCurrent) {
        if (isTrap) {
          borderColor = 'var(--tg-status-danger)';
          bgColor = 'rgba(239, 68, 68, 0.2)';
          textColor = 'var(--tg-status-danger)';
        } else {
          borderColor = 'var(--tg-accent-emerald)';
          bgColor = 'rgba(16, 185, 129, 0.2)';
          textColor = 'var(--tg-accent-emerald)';
        }
      } else if (isTrap) {
        borderColor = 'rgba(239, 68, 68, 0.35)';
        textColor = 'var(--tg-status-danger)';
        bgColor = 'rgba(239, 68, 68, 0.05)';
      } else if (isFinal) {
        borderColor = 'var(--tg-status-warning)';
      } else if (isInitial) {
        borderColor = 'var(--tg-brand-blue)';
      }

      return {
        id: st.id,
        position: pos,
        data: {
          label: (
            <div className="text-center font-mono">
              <div className="flex items-center justify-center gap-1 mb-0.5">
                {isInitial && <span className="text-[8px] px-1 rounded bg-blue-500/20 text-[var(--tg-accent-blue)] font-semibold">q₀</span>}
                {isFinal && <span className="text-[8px] px-1 rounded bg-amber-500/20 text-[var(--tg-status-warning)] font-semibold">F</span>}
                {isTrap && <span className="text-[8px] px-1 rounded bg-rose-500/20 text-[var(--tg-status-danger)] font-semibold">TRAP</span>}
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
          boxShadow: isCurrent
            ? isTrap
              ? '0 0 16px rgba(239, 68, 68, 0.45)'
              : '0 0 16px rgba(16, 185, 129, 0.45)'
            : '0 1px 3px rgba(0,0,0,0.4)',
          transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
        },
      };
    });
  }, [formalData, currentState]);

  // Edges for ReactFlow with active transition animation
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
          stroke: isActiveTransition ? 'var(--tg-accent-emerald)' : 'var(--tg-border-strong)',
          strokeWidth: isActiveTransition ? 2.8 : 1.2,
        },
        labelStyle: {
          fill: isActiveTransition ? 'var(--tg-accent-emerald)' : 'var(--tg-text-secondary)',
          fontSize: 9,
          fontWeight: isActiveTransition ? '600' : 'normal',
          fontFamily: 'JetBrains Mono, monospace',
        },
        labelBgStyle: {
          fill: 'var(--tg-bg-surface)',
          fillOpacity: 0.95,
          rx: 3,
          ry: 3,
        },
      };
    });
  }, [fsmDef, stepData, stepIndex]);

  // Consumed, active, and remaining symbols partitioning
  const streamTokens = useMemo(() => {
    return parsedSymbols.map((sym, idx) => {
      let status = 'pending';
      if (idx < stepIndex) {
        status = 'consumed';
      } else if (idx === stepIndex) {
        status = 'active';
      }
      return { symbol: sym, index: idx, status };
    });
  }, [parsedSymbols, stepIndex]);

  const activeStepDetail = stepData && stepIndex >= 0 ? stepData.steps[stepIndex] : null;

  if (loadingFsm || loadingFormal) {
    return <LoadingSpinner text="Retrieving formal automata specification..." />;
  }

  return (
    <div className="space-y-6">
      {/* Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-[var(--tg-border-subtle)]">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <h1 className="text-lg font-semibold tracking-tight text-[var(--tg-text-primary)]">
              Automata Laboratory
            </h1>
          </div>
          <p className="text-xs text-[var(--tg-text-muted)] mt-1">
            Complete HTTP 9-State Total DFA (M=(Q, Σ, δ, q₀, F)) with interactive stage simulation and full 117-cell transition matrix.
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
                    ? 'bg-[var(--tg-bg-surface)] text-[var(--tg-accent-emerald)] font-semibold border border-emerald-500/30 shadow-xs'
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

      {/* TAB 1: INTERACTIVE AUTOMATON & STAGE SIMULATION */}
      {activeTab === 'visualizer' && (
        <div className="space-y-5">
          {/* Controls Bar & Stage Stream Inspector */}
          <div className="tg-panel p-5 space-y-4">
            <div className="flex flex-col lg:flex-row items-stretch lg:items-end gap-3">
              <div className="flex-1">
                <label className="text-[11px] font-mono text-[var(--tg-text-muted)] block mb-1.5 uppercase">
                  Input Event Sequence (symbols separated by commas):
                </label>
                <input
                  type="text"
                  value={inputSequence}
                  onChange={(e) => {
                    setInputSequence(e.target.value);
                    handleReset();
                  }}
                  placeholder="CONNECT, REQUEST, AUTH_SUCCESS, RESPONSE_200, CLOSE"
                  className="tg-input text-xs font-mono"
                />
              </div>

              {/* Playback Controls */}
              <div className="flex flex-wrap items-center gap-2 pt-2 lg:pt-0">
                {/* Play / Pause Button */}
                <button
                  onClick={togglePlay}
                  disabled={executing || parsedSymbols.length === 0}
                  className="tg-btn-primary text-xs flex items-center gap-1.5 min-w-[100px] justify-center"
                >
                  {isPlaying ? (
                    <>
                      <Pause className="w-3.5 h-3.5 fill-current" />
                      <span>Pause</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-3.5 h-3.5 fill-current" />
                      <span>{stepIndex >= 0 && stepData ? 'Resume' : 'Run Simulation'}</span>
                    </>
                  )}
                </button>

                {/* Step Backward */}
                <button
                  onClick={handleStepBackward}
                  disabled={isPlaying || stepIndex < 0}
                  className="tg-btn-secondary text-xs disabled:opacity-40"
                  title="Previous Step"
                >
                  <StepBack className="w-3.5 h-3.5" />
                  <span>Back</span>
                </button>

                {/* Step Forward */}
                <button
                  onClick={handleStepForward}
                  disabled={isPlaying || (stepData && stepIndex >= stepData.steps.length - 1)}
                  className="tg-btn-secondary text-xs disabled:opacity-40"
                  title="Next Step"
                >
                  <span>Step</span>
                  <StepForward className="w-3.5 h-3.5" />
                </button>

                {/* Reset Button */}
                <button
                  onClick={handleReset}
                  className="p-2 rounded-md tg-btn-secondary text-xs"
                  title="Reset Automaton State (q₀ = IDLE)"
                  aria-label="Reset Automaton State"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>

                {/* Playback Speed Selector */}
                <div className="flex items-center gap-1 pl-1 border-l border-[var(--tg-border-subtle)] text-[11px] font-mono">
                  <span className="text-[var(--tg-text-muted)] mr-0.5">Speed:</span>
                  {[0.5, 1.0, 2.0].map((spd) => (
                    <button
                      key={spd}
                      onClick={() => setPlaybackSpeed(spd)}
                      className={`px-1.5 py-0.5 rounded text-[10px] font-mono transition ${
                        playbackSpeed === spd
                          ? 'bg-[var(--tg-accent-emerald-subtle)] text-[var(--tg-accent-emerald)] border border-emerald-500/30 font-semibold'
                          : 'text-[var(--tg-text-muted)] hover:text-[var(--tg-text-primary)]'
                      }`}
                    >
                      {spd}x
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Input Sequence Stream Visualizer */}
            <div className="pt-2 border-t border-[var(--tg-border-subtle)] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono">
              <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
                <span className="text-[11px] text-[var(--tg-text-muted)] shrink-0">Stream:</span>
                <span className="px-2 py-0.5 rounded bg-blue-500/10 text-[var(--tg-accent-blue)] border border-blue-500/20 shrink-0 font-semibold">
                  q₀: IDLE
                </span>
                <ArrowRight className="w-3 h-3 text-[var(--tg-text-disabled)] shrink-0" />
                {streamTokens.map((tok) => {
                  let badgeClass = 'bg-[var(--tg-bg-canvas)] text-[var(--tg-text-muted)] border-[var(--tg-border-subtle)]';
                  if (tok.status === 'consumed') {
                    badgeClass = 'bg-emerald-500/15 text-[var(--tg-accent-emerald)] border-emerald-500/30';
                  } else if (tok.status === 'active') {
                    badgeClass = 'bg-amber-500/20 text-[var(--tg-status-warning)] border-amber-500/40 animate-pulse font-bold';
                  }
                  return (
                    <span
                      key={tok.index}
                      className={`px-2 py-0.5 rounded border text-[11px] shrink-0 font-semibold transition-all ${badgeClass}`}
                    >
                      {tok.symbol}
                    </span>
                  );
                })}
              </div>

              {/* Current Stage Indicator */}
              <div className="text-[11px] text-[var(--tg-text-muted)] shrink-0 flex items-center gap-2">
                <span>
                  Stage:{' '}
                  <strong className="text-[var(--tg-accent-emerald)]">
                    {stepIndex < 0 ? '0 (Initial State)' : `${stepIndex + 1} of ${parsedSymbols.length}`}
                  </strong>
                </span>
                <span className="text-[var(--tg-text-disabled)]">|</span>
                <span>
                  State: <strong className="text-[var(--tg-text-primary)]">{currentState}</strong>
                </span>
              </div>
            </div>

            {/* Preset Sequence Pills */}
            <div className="flex flex-wrap items-center gap-1.5 pt-2 border-t border-[var(--tg-border-subtle)]">
              <span className="text-[11px] font-mono text-[var(--tg-text-muted)] mr-1">Presets:</span>
              {PRESET_SEQUENCES.map((preset) => (
                <button
                  key={preset.name}
                  onClick={() => {
                    setInputSequence(preset.seq);
                    handleReset();
                  }}
                  className="px-2 py-0.5 rounded text-[10px] font-mono bg-[var(--tg-bg-canvas)] hover:bg-[var(--tg-bg-hover)] text-[var(--tg-accent-emerald)] border border-emerald-500/20 transition"
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
                <Background color="var(--tg-border-subtle)" gap={20} size={1} />
                <Controls className="bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] text-[var(--tg-text-primary)]" />
                <MiniMap
                  nodeColor={(n) => (n.id === currentState ? 'var(--tg-accent-emerald)' : 'var(--tg-border-strong)')}
                  maskColor="var(--tg-bg-overlay)"
                  className="border border-[var(--tg-border-subtle)] rounded-md overflow-hidden"
                />
              </ReactFlow>

              {/* Float Overlay Indicator */}
              <div className="absolute top-4 left-4 p-3 rounded-lg bg-[var(--tg-bg-base)]/90 backdrop-blur-md border border-[var(--tg-border-default)] text-xs font-mono space-y-1 shadow-md">
                <div className="flex items-center gap-2">
                  <span className="text-[var(--tg-text-muted)]">ACTIVE DFA STATE:</span>
                  <span className="text-[var(--tg-accent-emerald)] font-bold">{currentState}</span>
                </div>
                <div className="flex items-center gap-3 text-[10px] text-[var(--tg-text-muted)]">
                  <span>Stage: {stepIndex >= 0 ? stepIndex + 1 : 0} / {parsedSymbols.length}</span>
                  <span>q₀: IDLE</span>
                  <span>F: &#123;CLOSED&#125;</span>
                </div>
                {activeStepDetail && (
                  <div className="pt-1 border-t border-[var(--tg-border-subtle)] text-[10px] text-[var(--tg-text-secondary)]">
                    Transition: <span className="font-semibold text-[var(--tg-accent-blue)]">{activeStepDetail.delta_lookup}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Stepper Details & Invariant Inspector */}
            <div className="lg:col-span-4 tg-panel p-5 flex flex-col h-[550px]">
              <div className="mb-3">
                <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
                  Transition Step Execution Audit
                </h2>
                <p className="text-[10px] font-mono text-[var(--tg-text-muted)]">
                  Formal lookup: δ(q, σ) → q'
                </p>
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
                            setIsPlaying(false);
                            setStepIndex(idx);
                            setCurrentState(st.next_state || st.current_state);
                          }}
                          className={`p-2.5 rounded-lg border font-mono text-xs cursor-pointer transition ${
                            isCurrent
                              ? 'border-emerald-500 bg-[var(--tg-bg-elevated)] shadow-xs ring-1 ring-emerald-500/40'
                              : st.valid
                              ? 'border-[var(--tg-border-subtle)] bg-[var(--tg-bg-base)] text-[var(--tg-text-secondary)]'
                              : 'border-rose-500/40 bg-rose-500/10 text-[var(--tg-status-danger)]'
                          }`}
                        >
                          <div className="flex items-center justify-between text-[10px]">
                            <span className="font-semibold">Stage {st.step_number}</span>
                            <span
                              className={`px-1.5 py-0.2 rounded font-semibold ${
                                st.valid
                                  ? 'bg-emerald-500/20 text-[var(--tg-accent-emerald)]'
                                  : 'bg-rose-500/20 text-[var(--tg-status-danger)]'
                              }`}
                            >
                              {st.valid ? 'VALID δ' : 'REJECTED ∅'}
                            </span>
                          </div>
                          <div className="text-[11px] font-semibold text-[var(--tg-text-primary)] mt-1">
                            {st.delta_lookup}
                          </div>
                          <div className="text-[10px] text-[var(--tg-text-muted)] mt-0.5 leading-tight">
                            {st.explanation}
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Verdict Footer */}
                  <div
                    className={`mt-4 p-3 rounded-lg border font-mono text-xs ${
                      stepData.verdict === 'ACCEPTED'
                        ? 'bg-emerald-500/10 border-emerald-500/30 text-[var(--tg-accent-emerald)]'
                        : stepData.verdict === 'INCOMPLETE_VALID'
                        ? 'bg-amber-500/10 border-amber-500/30 text-[var(--tg-status-warning)]'
                        : 'bg-rose-500/10 border-rose-500/30 text-[var(--tg-status-danger)]'
                    }`}
                  >
                    <div className="flex justify-between items-center font-semibold">
                      <span>VERDICT: {stepData.verdict}</span>
                      <span>Terminal State: {stepData.final_state}</span>
                    </div>
                    {stepData.rejection_reason && (
                      <p className="text-[10px] mt-1 leading-normal opacity-90">{stepData.rejection_reason}</p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-center font-mono text-xs text-[var(--tg-text-muted)]">
                  <GitBranch className="w-8 h-8 opacity-40 mb-2 text-[var(--tg-accent-emerald)]" />
                  <span>Click "Run Simulation" or "Step" to begin state transition verification.</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: FORMAL 5-TUPLE DEFINITION */}
      {activeTab === 'formal' && formalData && (
        <div className="space-y-6">
          <div className="tg-panel p-6 border-emerald-500/30 text-center font-mono space-y-2">
            <span className="text-xs text-[var(--tg-text-muted)] uppercase tracking-wider">Formal Automaton Specification</span>
            <div className="text-2xl font-bold text-[var(--tg-accent-emerald)]">{formalData.tuple_notation}</div>
            <p className="text-xs text-[var(--tg-text-muted)] max-w-2xl mx-auto">
              A 5-tuple defining the HTTP protocol state machine as a Deterministic Finite Automaton (DFA) recognized by TraceGuard AI.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="tg-panel p-5 space-y-3">
              <div className="flex items-center justify-between border-b border-[var(--tg-border-subtle)] pb-2 font-mono">
                <span className="text-xs font-semibold text-[var(--tg-accent-blue)] uppercase">Q: Finite Set of States (|Q| = {formalData.Q_states.length})</span>
              </div>
              <div className="space-y-2 font-mono text-xs">
                {formalData.Q_states.map((st) => (
                  <div key={st.id} className="p-2.5 rounded-lg bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)]">
                    <div className="flex items-center gap-2">
                      <span className="text-[var(--tg-accent-emerald)] font-semibold">{st.id}</span>
                      {st.is_initial && <span className="tg-badge tg-badge-blue">q₀ (Initial)</span>}
                      {st.is_accepting && <span className="tg-badge tg-badge-amber">F (Accepting)</span>}
                    </div>
                    <p className="text-[10px] text-[var(--tg-text-muted)] mt-1">{st.meaning}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="tg-panel p-5 space-y-3">
              <div className="flex items-center justify-between border-b border-[var(--tg-border-subtle)] pb-2 font-mono">
                <span className="text-xs font-semibold text-[var(--tg-accent-blue)] uppercase">Σ: Finite Alphabet of Event Symbols (|Σ| = {formalData.Sigma_alphabet.length})</span>
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

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 font-mono text-xs">
            <div className="tg-panel p-4">
              <span className="text-[var(--tg-text-muted)]">Initial State (q₀):</span>
              <div className="text-lg font-bold text-[var(--tg-accent-blue)] mt-1">{formalData.q0}</div>
              <p className="text-[10px] text-[var(--tg-text-muted)] mt-1">Socket listener initialized, awaiting TCP handshake.</p>
            </div>
            <div className="tg-panel p-4">
              <span className="text-[var(--tg-text-muted)]">Accepting States Set (F):</span>
              <div className="text-lg font-bold text-[var(--tg-status-warning)] mt-1">&#123;{formalData.F_accepting.join(', ')}&#125;</div>
              <p className="text-[10px] text-[var(--tg-text-muted)] mt-1">Language acceptance condition: δ*(q₀, w) ∈ F.</p>
            </div>
            <div className="tg-panel p-4">
              <span className="text-[var(--tg-text-muted)]">Transition Cardinality (|δ|):</span>
              <div className="text-lg font-bold text-[var(--tg-accent-emerald)] mt-1">{formalData.transition_function_delta.length} Defined Transitions</div>
              <p className="text-[10px] text-[var(--tg-text-muted)] mt-1">
                Complete total mapping: {formalData.total_matrix_cells} cells ({formalData.valid_protocol_transitions_count} valid, {formalData.total_matrix_cells - formalData.valid_protocol_transitions_count} trap absorbing).
              </p>
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
                Complete total deterministic state transition matrix (|Q| × |Σ| = 9 × 13 = 117 cells). Valid protocol paths reach next operational states; non-permitted transitions route deterministically to TRAP.
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
                          const isTrapTarget = target === 'TRAP';
                          const isValid = target && target !== 'TRAP' && target !== '∅';
                          return (
                            <td
                              key={sym.symbol}
                              className={`text-center font-mono text-[11px] whitespace-nowrap px-2 py-1.5 transition-colors ${
                                isValid
                                  ? 'text-[var(--tg-accent-emerald)] font-semibold bg-emerald-500/10 border-emerald-500/20'
                                  : isTrapTarget
                                  ? 'text-[var(--tg-status-danger)]/70 bg-rose-500/5 font-mono'
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
                <div className="p-2 rounded bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] text-[10px] text-[var(--tg-accent-emerald)] break-all">
                  {testCase.seq}
                </div>
                <button
                  onClick={() => {
                    setInputSequence(testCase.seq);
                    handleReset();
                    setActiveTab('visualizer');
                  }}
                  className="w-full tg-btn-secondary text-xs text-[var(--tg-accent-emerald)] hover:text-emerald-700 font-semibold"
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
            <h2 className="text-base font-semibold text-[var(--tg-accent-emerald)]">Theoretical Foundations & Formal Language Semantics</h2>
            
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
                  <li><strong className="text-[var(--tg-accent-emerald)]">Accepted String (w ∈ L(M))</strong>: Every transition is defined in δ and terminal state q ∈ F.</li>
                  <li><strong className="text-[var(--tg-status-warning)]">Valid Incomplete Prefix</strong>: Every transition executed was valid in δ, but sequence ended in q ∉ F. (Normal in-progress network streams).</li>
                  <li><strong className="text-[var(--tg-status-danger)]">Rejected String (w ∉ L(M))</strong>: An event was received where δ(q, σ) = ∅. This constitutes an immediate security violation.</li>
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
