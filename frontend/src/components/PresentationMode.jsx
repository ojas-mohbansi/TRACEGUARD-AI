import React, { useState } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  Maximize2,
  X,
  Play,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  GitBranch,
  Cpu,
  Layers,
  BookOpen
} from 'lucide-react';
import api from '../services/api';

const PRESENTATION_STEPS = [
  {
    step: 1,
    title: 'Problem Statement & Motivation',
    subtitle: 'Why Network Intrusion Detection Needs Formal Automata',
    content: (
      <div className="space-y-4">
        <p className="text-sm text-[#91A0B5] leading-relaxed">
          Modern application protocols (HTTP, TLS, SSH) are fundamentally stateful communication systems. 
          Standard signature-based firewalls inspect payload strings, while deep learning models compute statistical likelihoods. 
          Neither mathematically verifies whether an observed sequence of protocol operations is legal according to specification.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-[#161F2D] border border-[#253247]">
            <h4 className="text-xs font-bold font-mono text-[#FF647C] mb-1">Out-of-Order Execution</h4>
            <p className="text-[11px] text-[#91A0B5]">Attackers sending response packets before requests or accessing private endpoints before authentication.</p>
          </div>
          <div className="p-4 rounded-xl bg-[#161F2D] border border-[#253247]">
            <h4 className="text-xs font-bold font-mono text-[#F5B84B] mb-1">State Tampering</h4>
            <p className="text-[11px] text-[#91A0B5]">Injecting state modifications into existing sessions to bypass authentication gates.</p>
          </div>
          <div className="p-4 rounded-xl bg-[#161F2D] border border-[#253247]">
            <h4 className="text-xs font-bold font-mono text-[#42D6B2] mb-1">The TOC Solution</h4>
            <p className="text-[11px] text-[#91A0B5]">Model the protocol as a Deterministic Finite Automaton (DFA) that decides valid sequence membership with O(1) step time.</p>
          </div>
        </div>
      </div>
    ),
  },
  {
    step: 2,
    title: 'The Finite Automaton Model',
    subtitle: 'Formal Concepts: States, Alphabet, and Transitions',
    content: (
      <div className="space-y-4">
        <p className="text-sm text-[#91A0B5] leading-relaxed">
          In Theory of Computation, an automaton is an abstract mathematical machine that reads input strings symbol-by-symbol, transitioning between finite internal states according to a fixed transition function.
        </p>
        <div className="p-4 rounded-xl bg-[#080B12] border border-[#253247] font-mono text-xs text-[#EDF3FA] space-y-2">
          <div className="text-[#42D6B2] font-bold">Key Theoretical Characteristics:</div>
          <div>• <span className="text-[#54A7FF]">Memorylessness</span>: Future transitions depend strictly on current state and next input symbol.</div>
          <div>• <span className="text-[#54A7FF]">Determinism</span>: For every pair of state and symbol, there is at most one legal next state.</div>
          <div>• <span className="text-[#54A7FF]">Decidability</span>: Halting and membership are guaranteed in linear time O(|w|).</div>
        </div>
      </div>
    ),
  },
  {
    step: 3,
    title: 'Formal 5-Tuple Definition: M = (Q, Σ, δ, q₀, F)',
    subtitle: 'Mathematical Formulation of the HTTP Protocol Automaton',
    content: (
      <div className="space-y-4">
        <div className="p-4 rounded-xl bg-[#080B12] border border-[#42D6B2]/40 text-center font-mono">
          <span className="text-lg font-bold text-[#42D6B2]">M = (Q, Σ, δ, q₀, F)</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          <div className="p-3 rounded-lg bg-[#161F2D] border border-[#253247]">
            <span className="text-[#54A7FF] font-bold">Q (9 States, incl. TRAP sink):</span>
            <p className="text-[11px] text-[#91A0B5] mt-1">&#123;IDLE, CONNECTED, REQUEST_RECEIVED, AUTH_CHECKED, AUTH_FAILED, RESPONSE_SENT, ERROR, CLOSED, TRAP&#125;</p>
          </div>
          <div className="p-3 rounded-lg bg-[#161F2D] border border-[#253247]">
            <span className="text-[#54A7FF] font-bold">Σ (13 Event Symbols):</span>
            <p className="text-[11px] text-[#91A0B5] mt-1">&#123;CONNECT, REQUEST, AUTH_SUCCESS, AUTH_FAILURE, RESPONSE_200, RESPONSE_301, RESPONSE_401, RESPONSE_403, RESPONSE_500, CLOSE, TIMEOUT, MALFORMED, ERROR_RESPONSE&#125;</p>
          </div>
          <div className="p-3 rounded-lg bg-[#161F2D] border border-[#253247]">
            <span className="text-[#54A7FF] font-bold">q₀ (Start State):</span>
            <p className="text-[11px] text-[#91A0B5] mt-1">IDLE (Awaiting initial TCP connection)</p>
          </div>
          <div className="p-3 rounded-lg bg-[#161F2D] border border-[#253247]">
            <span className="text-[#54A7FF] font-bold">F (Accepting States Set):</span>
            <p className="text-[11px] text-[#91A0B5] mt-1">&#123;CLOSED&#125; (Clean termination)</p>
          </div>
        </div>
      </div>
    ),
  },
  {
    step: 4,
    title: 'State Transition Diagram',
    subtitle: 'Graph Topology and Directed Transitions',
    content: (
      <div className="space-y-4">
        <p className="text-sm text-[#91A0B5] leading-relaxed">
          The 15 valid transitions form a directed graph representing the lifecycle of an HTTP connection.
          Nodes represent operational protocol phases, while edges represent observable network events.
        </p>
        <div className="p-4 rounded-xl bg-[#161F2D] border border-[#253247] space-y-2 font-mono text-xs">
          <div className="flex justify-between items-center text-[11px]">
            <span className="text-[#54A7FF]">Initial State:</span>
            <span className="text-[#EDF3FA]">IDLE (In-Degree: 0, Out-Degree: 1)</span>
          </div>
          <div className="flex justify-between items-center text-[11px]">
            <span className="text-[#54A7FF]">Cyclic Loop (Keep-Alive):</span>
            <span className="text-[#EDF3FA]">RESPONSE_SENT &#8594; REQUEST &#8594; REQUEST_RECEIVED</span>
          </div>
          <div className="flex justify-between items-center text-[11px]">
            <span className="text-[#54A7FF]">Terminal Sink:</span>
            <span className="text-[#42D6B2]">CLOSED (In-Degree: 3, Out-Degree: 0)</span>
          </div>
          <div className="flex justify-between items-center text-[11px]">
            <span className="text-[#54A7FF]">Total Matrix Cells:</span>
            <span className="text-[#F5B84B]">|Q| × |Σ| = 117 (15 defined, 102 undefined/trap & self-loops)</span>
          </div>
        </div>
      </div>
    ),
  },
  {
    step: 5,
    title: 'Executing a Valid HTTP Sequence',
    subtitle: 'Demonstration of Sequence Acceptance (w ∈ L(M))',
    interactive: true,
    testSequence: ['CONNECT', 'REQUEST', 'AUTH_SUCCESS', 'RESPONSE_200', 'CLOSE'],
    description: 'This canonical sequence represents a valid authenticated transaction terminating gracefully in CLOSED.',
  },
  {
    step: 6,
    title: 'Executing an Invalid HTTP Sequence',
    subtitle: 'Immediate Invariant Violation Detection',
    interactive: true,
    testSequence: ['CONNECT', 'RESPONSE_200', 'REQUEST', 'CLOSE'],
    description: 'The server transmits a response before a request was ever received. Transition δ(CONNECTED, RESPONSE_200) is undefined.',
  },
  {
    step: 7,
    title: 'Incomplete Prefix vs. Acceptance',
    subtitle: 'Distinguishing Language Acceptance from Transition Validity',
    interactive: true,
    testSequence: ['CONNECT', 'REQUEST', 'AUTH_SUCCESS'],
    description: 'All 3 transitions are completely legal, but execution terminates in AUTH_CHECKED ∉ F. It is a valid prefix, not a rejection.',
  },
  {
    step: 8,
    title: 'Machine Learning Anomaly Detection',
    subtitle: 'Statistical Profiling via Isolation Forest',
    content: (
      <div className="space-y-4">
        <p className="text-sm text-[#91A0B5] leading-relaxed">
          While the FSM enforces strict structural protocol rules, Machine Learning (Isolation Forest) models statistical deviations.
          It extracts 15 session-level features: duration, packet counts, inter-arrival time variance, error ratios, and byte distributions.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          <div className="p-3 rounded-lg bg-[#161F2D] border border-[#253247]">
            <span className="text-[#54A7FF] font-bold">FSM vs. ML Role:</span>
            <p className="text-[11px] text-[#91A0B5] mt-1">FSM is primary: provides exact, zero-false-positive violation proofs. ML is secondary: detects volumetric brute-force floods that follow valid transitions.</p>
          </div>
          <div className="p-3 rounded-lg bg-[#161F2D] border border-[#253247]">
            <span className="text-[#42D6B2] font-bold">Unsupervised Isolation:</span>
            <p className="text-[11px] text-[#91A0B5] mt-1">Isolates anomalies without requiring prior labeled attack signatures by measuring tree path length.</p>
          </div>
        </div>
      </div>
    ),
  },
  {
    step: 9,
    title: 'Hybrid Engine Synthesis',
    subtitle: 'Combining Mathematical Guarantees with Statistical Scores',
    content: (
      <div className="space-y-4">
        <div className="p-4 rounded-xl bg-[#080B12] border border-[#253247] font-mono text-center space-y-2">
          <div className="text-xs text-[#91A0B5]">HYBRID SCORING FORMULA:</div>
          <div className="text-sm font-bold text-[#EDF3FA]">Hybrid = (0.6 × FSM_Score) + (0.4 × ML_Score)</div>
          <div className="text-xs text-[#FF647C] font-semibold">Invariant Floor: If FSM_Violations &gt; 0 &#8658; Score = max(Score, 85)</div>
        </div>
        <p className="text-xs text-[#91A0B5] leading-relaxed">
          The hybrid architecture ensures that proven formal protocol violations can never be dismissed or watered down by statistical variance, maintaining rigorous safety guarantees.
        </p>
      </div>
    ),
  },
  {
    step: 10,
    title: 'Evaluation Metrics & Scope Limitations',
    subtitle: 'Academic Conclusions and Research Boundaries',
    content: (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-center font-mono">
          <div className="p-3 rounded-lg bg-[#161F2D] border border-[#253247]">
            <div className="text-xl font-bold text-[#42D6B2]">31 / 31</div>
            <div className="text-[10px] text-[#91A0B5]">Automated Tests Passing</div>
          </div>
          <div className="p-3 rounded-lg bg-[#161F2D] border border-[#253247]">
            <div className="text-xl font-bold text-[#54A7FF]">O(1)</div>
            <div className="text-[10px] text-[#91A0B5]">Transition Lookup Time</div>
          </div>
          <div className="p-3 rounded-lg bg-[#161F2D] border border-[#253247]">
            <div className="text-xl font-bold text-[#F5B84B]">0%</div>
            <div className="text-[10px] text-[#91A0B5]">FSM False Positive Rate</div>
          </div>
        </div>
        <div className="p-3 rounded-xl bg-[#161F2D]/60 border border-[#253247] text-xs text-[#91A0B5] space-y-1">
          <span className="font-bold text-[#EDF3FA]">Educational Abstraction Note:</span>
          <p>
            This HTTP model is an educational abstraction designed for university demonstration of Theory of Computation concepts.
            It models core session sequencing rather than the entire RFC 7230/9112 specification.
          </p>
        </div>
      </div>
    ),
  },
];

export function PresentationMode({ onClose }) {
  const [currentIdx, setCurrentIdx] = useState(0);
  const [executionResult, setExecutionResult] = useState(null);
  const [executing, setExecuting] = useState(false);

  const stepData = PRESENTATION_STEPS[currentIdx];

  const handleRunInteractive = async () => {
    if (!stepData.testSequence) return;
    setExecuting(true);
    try {
      const res = await api.stepExecuteAutomaton(stepData.testSequence);
      setExecutionResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setExecuting(false);
    }
  };

  const handleNext = () => {
    if (currentIdx < PRESENTATION_STEPS.length - 1) {
      setCurrentIdx(currentIdx + 1);
      setExecutionResult(null);
    }
  };

  const handlePrev = () => {
    if (currentIdx > 0) {
      setCurrentIdx(currentIdx - 1);
      setExecutionResult(null);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-[#080B12]/95 backdrop-blur-md flex flex-col text-[#EDF3FA]">
      {/* Top Bar */}
      <div className="h-14 px-6 border-b border-[#253247] flex items-center justify-between bg-[#101622]/80">
        <div className="flex items-center space-x-3">
          <span className="px-2.5 py-0.5 rounded text-[10px] font-mono font-bold bg-[#42D6B2]/10 border border-[#42D6B2]/30 text-[#42D6B2]">
            TOC PRESENTATION MODE
          </span>
          <span className="text-xs text-[#91A0B5] font-mono">
            Slide {stepData.step} of {PRESENTATION_STEPS.length}
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-[#161F2D] hover:bg-[#253247] text-[#91A0B5] hover:text-[#EDF3FA] transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Main Slide Content */}
      <div className="flex-1 overflow-y-auto p-8 max-w-4xl mx-auto w-full flex flex-col justify-center">
        <div className="mb-6">
          <span className="text-[11px] font-mono text-[#42D6B2] uppercase tracking-wider">
            STEP {stepData.step}: {stepData.subtitle}
          </span>
          <h2 className="text-2xl font-bold font-mono tracking-tight text-[#EDF3FA] mt-1">
            {stepData.title}
          </h2>
        </div>

        {stepData.content && <div>{stepData.content}</div>}

        {stepData.interactive && (
          <div className="space-y-4">
            <p className="text-sm text-[#91A0B5]">{stepData.description}</p>
            <div className="p-4 rounded-xl bg-[#080B12] border border-[#253247] space-y-3">
              <div className="text-xs font-mono text-[#91A0B5]">
                Target Event Sequence:
              </div>
              <div className="flex flex-wrap gap-1.5 font-mono text-xs">
                {stepData.testSequence.map((sym, i) => (
                  <span
                    key={i}
                    className="px-2 py-1 rounded bg-[#161F2D] border border-[#253247] text-[#54A7FF]"
                  >
                    {sym}
                  </span>
                ))}
              </div>

              <div className="pt-2 flex items-center space-x-3">
                <button
                  onClick={handleRunInteractive}
                  disabled={executing}
                  className="px-4 py-2 rounded-xl text-xs font-mono font-bold bg-[#42D6B2] text-[#080B12] hover:bg-[#38bda0] transition flex items-center space-x-2 shadow-lg shadow-[#42D6B2]/20"
                >
                  <Play className="w-4 h-4 fill-current" />
                  <span>{executing ? 'Executing...' : 'Run Sequence on DFA'}</span>
                </button>
              </div>
            </div>

            {executionResult && (
              <div
                className={`p-4 rounded-xl border font-mono text-xs space-y-2 ${
                  executionResult.verdict === 'ACCEPTED'
                    ? 'bg-[#42D6B2]/10 border-[#42D6B2]/30 text-[#42D6B2]'
                    : executionResult.verdict === 'INCOMPLETE_VALID'
                    ? 'bg-[#F5B84B]/10 border-[#F5B84B]/30 text-[#F5B84B]'
                    : 'bg-[#FF647C]/10 border-[#FF647C]/30 text-[#FF647C]'
                }`}
              >
                <div className="flex items-center justify-between font-bold">
                  <span>DFA VERDICT: {executionResult.verdict}</span>
                  <span>Terminal State: {executionResult.final_state}</span>
                </div>
                {executionResult.rejection_reason && (
                  <div className="text-[11px] leading-relaxed">
                    {executionResult.rejection_reason}
                  </div>
                )}
                <div className="pt-1 text-[10px] text-[#91A0B5] border-t border-white/10">
                  Total Steps: {executionResult.steps.length} | All Transitions Valid: {String(executionResult.all_transitions_valid)} | Accepting State Reached: {String(executionResult.is_in_accepting_state)}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Bottom Navigation */}
      <div className="h-16 px-8 border-t border-[#253247] flex items-center justify-between bg-[#101622]/80">
        <button
          onClick={handlePrev}
          disabled={currentIdx === 0}
          className="px-4 py-2 rounded-xl text-xs font-mono bg-[#161F2D] hover:bg-[#253247] text-[#EDF3FA] disabled:opacity-40 transition flex items-center space-x-2"
        >
          <ChevronLeft className="w-4 h-4" />
          <span>Previous Step</span>
        </button>

        <div className="flex space-x-1.5">
          {PRESENTATION_STEPS.map((_, i) => (
            <button
              key={i}
              onClick={() => {
                setCurrentIdx(i);
                setExecutionResult(null);
              }}
              className={`w-2.5 h-2.5 rounded-full transition-all ${
                i === currentIdx ? 'bg-[#42D6B2] w-6' : 'bg-[#253247] hover:bg-[#91A0B5]'
              }`}
            />
          ))}
        </div>

        <button
          onClick={handleNext}
          disabled={currentIdx === PRESENTATION_STEPS.length - 1}
          className="px-4 py-2 rounded-xl text-xs font-mono bg-[#161F2D] hover:bg-[#253247] text-[#EDF3FA] disabled:opacity-40 transition flex items-center space-x-2"
        >
          <span>Next Step</span>
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

export default PresentationMode;
