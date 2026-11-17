import React, { useState, useEffect, useMemo, useCallback } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  MarkerType,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Play,
  RotateCcw,
  StepForward,
  AlertTriangle,
  CheckCircle2,
  GitBranch,
  Info
} from 'lucide-react';
import api from '../services/api';
import { useApi } from '../hooks/useApi';
import LoadingSpinner from '../components/LoadingSpinner';

const STATE_POSITIONS = {
  IDLE: { x: 50, y: 180 },
  CONNECTED: { x: 250, y: 180 },
  REQUEST_RECEIVED: { x: 450, y: 180 },
  AUTH_CHECKED: { x: 700, y: 80 },
  AUTH_FAILED: { x: 700, y: 280 },
  RESPONSE_SENT: { x: 950, y: 180 },
  ERROR: { x: 700, y: 420 },
  CLOSED: { x: 1200, y: 180 },
  TRAP: { x: 600, y: 560 },
};

export function ProtocolExplorer() {
  const { data: fsmDef, loading, error, refetch } = useApi(() => api.getHttpFsm());

  const [inputSequence, setInputSequence] = useState('CONNECT, REQUEST, AUTH_SUCCESS, RESPONSE_200, CLOSE');
  const [playbackSteps, setPlaybackSteps] = useState([]);
  const [currentStepIndex, setCurrentStepIndex] = useState(-1);
  const [currentState, setCurrentState] = useState('IDLE');
  const [validationLog, setValidationLog] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);

  // Parse input sequence into array of event strings
  const parsedEvents = useMemo(() => {
    return inputSequence
      .split(',')
      .map((s) => s.trim().toUpperCase())
      .filter(Boolean);
  }, [inputSequence]);

  // Build ReactFlow Nodes
  const initialNodes = useMemo(() => {
    if (!fsmDef?.states) return [];
    return fsmDef.states.map((st) => {
      const isCurrent = st.id === currentState;
      const isInitial = st.is_initial;
      const isFinal = st.is_final;
      const pos = STATE_POSITIONS[st.id] || { x: 100, y: 100 };

      return {
        id: st.id,
        position: pos,
        data: {
          label: (
            <div className="text-center font-mono">
              <div className="text-[11px] font-bold tracking-wider">{st.label || st.id}</div>
              <div className="text-[9px] text-[var(--tg-text-muted)] truncate max-w-[120px]">{st.description}</div>
            </div>
          ),
        },
        style: {
          background: isCurrent ? 'var(--tg-bg-elevated)' : 'var(--tg-bg-surface)',
          color: isCurrent ? 'var(--tg-accent-emerald)' : 'var(--tg-text-primary)',
          border: isCurrent
            ? '2px solid var(--tg-accent-emerald)'
            : isInitial
            ? '1.5px dashed var(--tg-status-info)'
            : isFinal
            ? '1.5px solid var(--tg-status-warning)'
            : '1px solid var(--tg-border-subtle)',
          borderRadius: '12px',
          padding: '10px 14px',
          boxShadow: isCurrent ? '0 0 15px rgba(16, 185, 129, 0.25)' : 'none',
          transition: 'all 0.3s ease',
        },
      };
    });
  }, [fsmDef, currentState]);

  // Build ReactFlow Edges
  const initialEdges = useMemo(() => {
    if (!fsmDef?.transitions) return [];
    const lastValidation = validationLog[validationLog.length - 1];

    return fsmDef.transitions.map((tr, idx) => {
      const isTraversed =
        lastValidation &&
        lastValidation.from === tr.from &&
        lastValidation.to === tr.to &&
        lastValidation.event === tr.event;

      const isInvalidActive =
        lastValidation &&
        !lastValidation.valid &&
        lastValidation.from === tr.from &&
        lastValidation.event === tr.event;

      let strokeColor = 'var(--tg-border-strong)';
      let strokeWidth = 1.5;
      let animated = false;

      if (isTraversed && lastValidation.valid) {
        strokeColor = 'var(--tg-accent-emerald)';
        strokeWidth = 3;
        animated = true;
      } else if (isInvalidActive) {
        strokeColor = 'var(--tg-status-danger)';
        strokeWidth = 3;
        animated = true;
      }

      return {
        id: `e-${tr.from}-${tr.to}-${tr.event}-${idx}`,
        source: tr.from,
        target: tr.to,
        label: tr.event,
        animated,
        labelStyle: { fill: strokeColor, fontFamily: 'JetBrains Mono', fontSize: 10, fontWeight: 600 },
        labelBgStyle: { fill: 'var(--tg-bg-surface)', fillOpacity: 0.95, rx: 4, ry: 4 },
        style: { stroke: strokeColor, strokeWidth },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: strokeColor,
        },
      };
    });
  }, [fsmDef, validationLog]);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    setNodes(initialNodes);
  }, [initialNodes, setNodes]);

  useEffect(() => {
    setEdges(initialEdges);
  }, [initialEdges, setEdges]);

  // Reset simulator
  const handleReset = () => {
    setCurrentStepIndex(-1);
    setCurrentState('IDLE');
    setValidationLog([]);
    setIsPlaying(false);
  };

  // Step Forward
  const handleStepForward = useCallback(() => {
    if (!fsmDef?.transitions) return;
    const nextIndex = currentStepIndex + 1;
    if (nextIndex >= parsedEvents.length) {
      setIsPlaying(false);
      return;
    }

    const nextEvent = parsedEvents[nextIndex];
    // Find matching transition from currentState
    const validTransition = fsmDef.transitions.find(
      (t) => t.from === currentState && t.event === nextEvent
    );

    if (validTransition) {
      setCurrentState(validTransition.to);
      setValidationLog((prev) => [
        ...prev,
        {
          step: nextIndex + 1,
          from: currentState,
          to: validTransition.to,
          event: nextEvent,
          valid: true,
          reason: `Valid transition: ${currentState} -> ${validTransition.to} via ${nextEvent}`,
        },
      ]);
    } else {
      // Violation!
      setValidationLog((prev) => [
        ...prev,
        {
          step: nextIndex + 1,
          from: currentState,
          to: currentState,
          event: nextEvent,
          valid: false,
          reason: `VIOLATION: Unexpected event '${nextEvent}' in state '${currentState}'. Expected: [${fsmDef.transitions
            .filter((t) => t.from === currentState)
            .map((t) => t.event)
            .join(', ')}]`,
        },
      ]);
    }
    setCurrentStepIndex(nextIndex);
  }, [currentStepIndex, parsedEvents, fsmDef, currentState]);

  // Playback timer
  useEffect(() => {
    let timer;
    if (isPlaying) {
      timer = setInterval(() => {
        if (currentStepIndex + 1 < parsedEvents.length) {
          handleStepForward();
        } else {
          setIsPlaying(false);
        }
      }, 1200);
    }
    return () => clearInterval(timer);
  }, [isPlaying, currentStepIndex, parsedEvents, handleStepForward]);

  if (loading && !fsmDef) {
    return <LoadingSpinner text="Retrieving HTTP State Machine graph specification..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold font-mono tracking-tight text-[var(--tg-text-primary)]">
            PROTOCOL FSM EXPLORER & PLAYBACK
          </h1>
          <p className="text-xs text-[var(--tg-text-muted)] mt-0.5">
            Interactive state transition diagram and dynamic invariant violation debugger
          </p>
        </div>
      </div>

      {/* Playback Controls & Sequence Input */}
      <div className="tg-panel p-5 space-y-4">
        <div className="flex flex-col lg:flex-row items-stretch lg:items-end gap-3">
          <div className="flex-1">
            <label className="block text-[11px] font-mono text-[var(--tg-text-muted)] mb-1.5 uppercase">
              Event Sequence (Comma Separated)
            </label>
            <input
              type="text"
              value={inputSequence}
              onChange={(e) => {
                setInputSequence(e.target.value);
                handleReset();
              }}
              className="tg-input text-xs font-mono"
              placeholder="e.g. CONNECT, REQUEST, AUTH_SUCCESS, RESPONSE_200, CLOSE"
            />
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="tg-btn-primary text-xs"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{isPlaying ? 'Pause' : 'Auto Play'}</span>
            </button>

            <button
              onClick={handleStepForward}
              disabled={isPlaying || currentStepIndex + 1 >= parsedEvents.length}
              className="tg-btn-secondary text-xs disabled:opacity-40"
            >
              <StepForward className="w-3.5 h-3.5" />
              <span>Step</span>
            </button>

            <button
              onClick={handleReset}
              className="tg-btn-secondary text-xs"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          </div>
        </div>

        {/* Preset Sequence Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[var(--tg-border-subtle)]">
          <span className="text-[11px] font-mono text-[var(--tg-text-muted)]">Quick Presets:</span>
          {[
            {
              name: 'Normal 200 OK',
              seq: 'CONNECT, REQUEST, AUTH_SUCCESS, RESPONSE_200, CLOSE',
            },
            {
              name: 'Auth Failure & 401',
              seq: 'CONNECT, REQUEST, AUTH_FAILURE, RESPONSE_401, CLOSE',
            },
            {
              name: 'Early Response Violation',
              seq: 'CONNECT, RESPONSE_200, REQUEST, CLOSE',
            },
            {
              name: 'Missing Auth Sequence',
              seq: 'CONNECT, REQUEST, RESPONSE_200, CLOSE',
            },
          ].map((preset) => (
            <button
              key={preset.name}
              onClick={() => {
                setInputSequence(preset.seq);
                handleReset();
              }}
              className="px-2 py-0.5 rounded text-[10px] font-mono bg-[var(--tg-bg-canvas)] hover:bg-[var(--tg-bg-hover)] text-[var(--tg-accent-emerald)] border border-emerald-500/20 transition"
            >
              {preset.name}
            </button>
          ))}
        </div>
      </div>

      {/* Main Flow Canvas & Stepper Log */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* ReactFlow Interactive Canvas */}
        <div className="lg:col-span-8 h-[550px] tg-panel overflow-hidden relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
          >
            <Background color="var(--tg-border-subtle)" gap={20} size={1} />
            <Controls className="bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] text-[var(--tg-text-primary)]" />
            <MiniMap
              nodeColor={(n) => (n.id === currentState ? 'var(--tg-accent-emerald)' : 'var(--tg-border-strong)')}
              maskColor="var(--tg-bg-overlay)"
              className="border border-[var(--tg-border-subtle)] rounded-lg overflow-hidden"
            />
          </ReactFlow>

          <div className="absolute top-4 left-4 p-2.5 rounded-lg bg-[var(--tg-bg-base)]/80 backdrop-blur border border-[var(--tg-border-subtle)] text-xs font-mono space-y-1">
            <div className="flex items-center space-x-2">
              <span className="text-[var(--tg-text-muted)]">ACTIVE STATE:</span>
              <span className="text-[var(--tg-accent-emerald)] font-bold">{currentState}</span>
            </div>
            <div className="text-[10px] text-[var(--tg-text-muted)]">
              Step: {currentStepIndex + 1} / {parsedEvents.length}
            </div>
          </div>
        </div>

        {/* Step-by-Step Validation Feed */}
        <div className="lg:col-span-4 p-5 tg-panel flex flex-col h-[550px]">
          <div className="mb-3">
            <h3 className="text-xs font-semibold font-mono uppercase text-[var(--tg-text-primary)]">
              Step Playback Audit Log
            </h3>
            <p className="text-[10px] text-[var(--tg-text-muted)]">Real-time invariant checking</p>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 pr-1">
            {validationLog.length > 0 ? (
              validationLog.map((log, idx) => (
                <div
                  key={idx}
                  className={`p-2.5 rounded-lg border font-mono text-xs ${
                    log.valid
                      ? 'bg-emerald-500/10 border-emerald-500/30 text-[var(--tg-text-primary)]'
                      : 'bg-rose-500/10 border-rose-500/30 text-[var(--tg-status-danger)]'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] text-[var(--tg-text-muted)]">Step {log.step}</span>
                    <span
                      className={`text-[10px] font-bold ${
                        log.valid ? 'text-[var(--tg-accent-emerald)]' : 'text-[var(--tg-status-danger)]'
                      }`}
                    >
                      {log.valid ? 'COMPLIANT' : 'VIOLATION'}
                    </span>
                  </div>
                  <div className="mt-1 text-[11px] leading-tight">{log.reason}</div>
                </div>
              ))
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-center text-xs font-mono text-[var(--tg-text-muted)]">
                <GitBranch className="w-8 h-8 opacity-40 mb-2" />
                <span>Press Step or Auto Play to begin transition simulation.</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProtocolExplorer;
