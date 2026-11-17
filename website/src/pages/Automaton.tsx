import { useState } from 'react'
import { Check, AlertTriangle, Play, RotateCcw } from 'lucide-react'

import { Container } from '../components/Container'
import { PageHeader } from '../components/PageHeader'
import { DFADiagram } from '../components/DFADiagram'
import { Reveal } from '../components/Reveal'
import { automatonSummary } from '../content'
import { cx } from '../lib/cx'

const SAMPLE_TRACES = [
  {
    name: 'Normal 200 OK (Clean)',
    symbols: ['CONNECT', 'REQUEST', 'AUTH_SUCCESS', 'RESPONSE_200', 'CLOSE'],
    expected: 'ACCEPTED',
  },
  {
    name: 'Auth Failure 401 (Clean)',
    symbols: ['CONNECT', 'REQUEST', 'AUTH_FAILURE', 'RESPONSE_401', 'CLOSE'],
    expected: 'ACCEPTED',
  },
  {
    name: 'In-Flight Active Session',
    symbols: ['CONNECT', 'REQUEST', 'AUTH_SUCCESS'],
    expected: 'INCOMPLETE_VALID',
  },
  {
    name: 'Auth Bypass Attack (Illegal)',
    symbols: ['CONNECT', 'REQUEST', 'RESPONSE_200'],
    expected: 'REJECTED (Enters TRAP)',
  },
  {
    name: 'Response Injection without Handshake',
    symbols: ['RESPONSE_200'],
    expected: 'REJECTED (Enters TRAP)',
  },
]

export function Automaton() {
  const [selectedState, setSelectedState] = useState<string>('IDLE')
  const [traceHistory, setTraceHistory] = useState<string[]>([])
  const [activeSimulationState, setActiveSimulationState] = useState<string>('IDLE')

  // DFA execution engine
  const stepTrace = (symbol: string) => {
    setTraceHistory((prev) => [...prev, symbol])

    // Find valid transition from current state
    const valid = automatonSummary.validTransitions.find(
      (t) => t.from === activeSimulationState && t.symbol === symbol,
    )

    if (valid) {
      setActiveSimulationState(valid.to)
    } else {
      // In a total DFA, any undefined transition moves to TRAP
      setActiveSimulationState('TRAP')
    }
  }

  const resetTrace = () => {
    setTraceHistory([])
    setActiveSimulationState('IDLE')
  }

  const loadSample = (sample: typeof SAMPLE_TRACES[0]) => {
    resetTrace()
    let curr = 'IDLE'
    for (const sym of sample.symbols) {
      const valid = automatonSummary.validTransitions.find(
        (t) => t.from === curr && t.symbol === sym,
      )
      curr = valid ? valid.to : 'TRAP'
    }
    setTraceHistory(sample.symbols)
    setActiveSimulationState(curr)
  }

  const isAccepted = activeSimulationState === 'CLOSED'
  const isTrap = activeSimulationState === 'TRAP'

  return (
    <>
      <PageHeader
        eyebrow="Formal Specification Lab"
        title="HTTP Protocol Automaton: M = (Q, Σ, δ, q₀, F)"
        body="Inspect the mathematical 9-state HTTP protocol automaton. A mathematically Complete Total DFA eliminates undefined behavior by formally proving whether any input event sequence belongs to the regular language L(M)."
      />

      {/* Interactive State Machine Diagram & State Inspector */}
      <section className="border-t border-line bg-black py-16 sm:py-24">
        <Container size="xl">
          <Reveal>
            <div className="grid gap-8 lg:grid-cols-[1.3fr_1fr]">
              <div className="flex flex-col gap-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold text-white">Interactive State Graph</h2>
                  <span className="font-mono text-xs text-muted">Click any state node to inspect</span>
                </div>
                <DFADiagram
                  animated={false}
                  activeState={selectedState}
                  onSelectState={(s) => setSelectedState(s)}
                />
              </div>

              {/* State Details Panel */}
              <div className="flex flex-col gap-4">
                <h3 className="text-xl font-bold text-white">State Inspector: {selectedState}</h3>
                {(() => {
                  const info = automatonSummary.statesList.find((s) => s.id === selectedState)!
                  const outgoing = automatonSummary.validTransitions.filter((t) => t.from === selectedState)

                  return (
                    <div className="flex flex-col gap-4 rounded-card border border-line bg-surface p-6">
                      <div className="flex items-center justify-between border-b border-line pb-3">
                        <span className="font-mono text-sm font-bold text-signal-soft">{info.id}</span>
                        <span
                          className={cx(
                            'rounded-control px-2.5 py-0.5 font-mono text-xs font-semibold uppercase',
                            info.type === 'final'
                              ? 'bg-trace-wash text-trace-soft border border-trace-border'
                              : info.type === 'sink'
                              ? 'bg-threat-wash text-threat-soft border border-threat-border'
                              : 'bg-signal-wash text-signal-soft border border-signal-border',
                          )}
                        >
                          {info.type}
                        </span>
                      </div>
                      <p className="text-sm text-soft leading-relaxed">{info.desc}</p>

                      <div className="mt-2">
                        <span className="font-mono text-xs font-semibold uppercase text-muted">
                          Legal Outgoing Transitions ({outgoing.length})
                        </span>
                        {outgoing.length === 0 ? (
                          <p className="mt-2 text-xs text-faint font-mono">
                            {info.id === 'CLOSED'
                              ? 'Terminal accepting state. Any subsequent input routes to TRAP.'
                              : 'Absorbing sink. All 13 alphabet symbols self-loop to TRAP.'}
                          </p>
                        ) : (
                          <div className="mt-2.5 flex flex-col gap-2">
                            {outgoing.map((t, idx) => (
                              <div
                                key={idx}
                                className="flex items-center justify-between rounded-[10px] border border-line bg-surface-2 px-3 py-2 text-xs font-mono"
                              >
                                <span className="text-signal-soft">{t.symbol}</span>
                                <span className="text-muted">→ {t.to}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>

                      <div className="mt-2 rounded-[12px] border border-line-mid bg-surface-2 p-3 text-xs text-muted">
                        <span className="font-semibold text-white">Completeness Check:</span> In accordance with Total DFA rules, the remaining {13 - outgoing.length} alphabet symbols for this state explicitly map to <strong className="text-threat-soft">TRAP</strong>.
                      </div>
                    </div>
                  )
                })()}
              </div>
            </div>
          </Reveal>
        </Container>
      </section>

      {/* Live Interactive Trace Simulator */}
      <section className="border-t border-line bg-surface/40 py-16 sm:py-24">
        <Container size="xl">
          <Reveal>
            <div className="flex flex-col items-center text-center">
              <span className="font-mono text-xs uppercase tracking-wider text-signal-soft">Live Simulator</span>
              <h2 className="mt-2 text-[28px] font-bold text-white sm:text-[38px]">
                Deterministic Protocol Trace Validator
              </h2>
              <p className="mt-2 max-w-[640px] text-sm text-muted">
                Step through sequence events manually or load sample protocol sessions to observe the DFA state transitions and verdict classification.
              </p>
            </div>
          </Reveal>

          <div className="mt-10 grid gap-8 lg:grid-cols-[1.2fr_1fr]">
            {/* Interactive Step Console */}
            <div className="flex flex-col gap-4 rounded-card border border-line bg-surface p-6 shadow-card">
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line pb-4">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs text-muted">Current Automaton State:</span>
                  <span
                    className={cx(
                      'rounded-control px-2.5 py-0.5 font-mono text-xs font-bold',
                      isAccepted
                        ? 'bg-trace-wash text-trace-soft border border-trace-border'
                        : isTrap
                        ? 'bg-threat-wash text-threat-soft border border-threat-border'
                        : 'bg-signal-wash text-signal-soft border border-signal-border',
                    )}
                  >
                    {activeSimulationState}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={resetTrace}
                  className="inline-flex items-center gap-1.5 rounded-control border border-line bg-surface-2 px-3 py-1 font-mono text-xs text-soft hover:text-white"
                >
                  <RotateCcw className="size-3" aria-hidden />
                  <span>Reset (IDLE)</span>
                </button>
              </div>

              {/* Symbol Buttons */}
              <div className="mt-2">
                <span className="font-mono text-xs text-muted">Dispatch Input Symbol (σ ∈ Σ):</span>
                <div className="mt-3 flex flex-wrap gap-2">
                  {[
                    'CONNECT',
                    'REQUEST',
                    'AUTH_SUCCESS',
                    'AUTH_FAILURE',
                    'RESPONSE_200',
                    'RESPONSE_301',
                    'RESPONSE_401',
                    'RESPONSE_403',
                    'RESPONSE_500',
                    'CLOSE',
                    'TIMEOUT',
                    'MALFORMED',
                    'ERROR_RESPONSE',
                  ].map((sym) => (
                    <button
                      key={sym}
                      type="button"
                      onClick={() => stepTrace(sym)}
                      className="rounded-[10px] border border-line bg-surface-2 px-3 py-1.5 font-mono text-xs text-soft hover:border-signal-border hover:bg-signal-wash hover:text-signal-soft transition-colors"
                    >
                      +{sym}
                    </button>
                  ))}
                </div>
              </div>

              {/* Trace Log */}
              <div className="mt-4 flex flex-col gap-1.5 rounded-[14px] border border-line bg-surface-2 p-4 font-mono text-xs">
                <span className="text-faint">Executed Sequence Trace (w):</span>
                {traceHistory.length === 0 ? (
                  <span className="text-muted italic">No symbols dispatched yet. Quiescent at q₀ = IDLE.</span>
                ) : (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {traceHistory.map((s, idx) => (
                      <span key={idx} className="rounded bg-black/60 px-2 py-0.5 text-soft border border-line">
                        {idx + 1}. {s}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Verdict & Classification Card */}
            <div className="flex flex-col gap-4">
              <div className="flex flex-col gap-4 rounded-card border border-line bg-surface p-6 shadow-card">
                <span className="font-mono text-xs uppercase tracking-wider text-muted">Automata Classification</span>
                <div className="flex items-center gap-3">
                  <div
                    className={cx(
                      'grid size-12 place-items-center rounded-card text-xl font-bold',
                      isAccepted
                        ? 'bg-trace-wash text-trace-soft border border-trace-border'
                        : isTrap
                        ? 'bg-threat-wash text-threat-soft border border-threat-border'
                        : 'bg-warn-wash text-warn-soft border border-warn-border',
                    )}
                  >
                    {isAccepted ? <Check className="size-6" /> : isTrap ? <AlertTriangle className="size-6" /> : <Play className="size-5" />}
                  </div>
                  <div>
                    <h4 className="text-lg font-bold text-white">
                      {isAccepted ? 'ACCEPTED' : isTrap ? 'REJECTED' : 'INCOMPLETE_VALID'}
                    </h4>
                    <span className="font-mono text-xs text-muted">
                      {isAccepted
                        ? 'δ*(IDLE, w) ∈ {CLOSED}'
                        : isTrap
                        ? 'δ*(IDLE, w) = TRAP (Protocol Violation)'
                        : 'δ*(IDLE, w) ∉ F, no TRAP reached'}
                    </span>
                  </div>
                </div>

                <div className="mt-2 border-t border-line pt-3 font-mono text-xs text-soft">
                  <div className="flex justify-between py-1">
                    <span>Computed Risk Score:</span>
                    <span className="font-bold text-white">
                      {isAccepted ? '0 (Clean)' : isTrap ? '60+ (Violation Floor)' : '30 (Incomplete)'}
                    </span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span>FSM Violation Flag:</span>
                    <span className={isTrap ? 'text-threat-soft font-bold' : 'text-trace-soft'}>
                      {isTrap ? 'TRUE (Active)' : 'FALSE'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Quick Sample Traces */}
              <div className="rounded-card border border-line bg-surface p-5">
                <span className="font-mono text-xs text-muted uppercase">Pre-Loaded Test Scenarios:</span>
                <div className="mt-3 flex flex-col gap-2">
                  {SAMPLE_TRACES.map((sample) => (
                    <button
                      key={sample.name}
                      type="button"
                      onClick={() => loadSample(sample)}
                      className="flex items-center justify-between rounded-[10px] border border-line bg-surface-2 p-2.5 text-left text-xs transition-colors hover:border-signal-border"
                    >
                      <span className="font-medium text-white">{sample.name}</span>
                      <span className="font-mono text-[11px] text-signal-soft">{sample.expected}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </Container>
      </section>

      {/* 117 Transition Matrix Completeness Table */}
      <section className="border-t border-line bg-black py-16 sm:py-24">
        <Container size="xl">
          <Reveal>
            <div className="flex flex-col items-center text-center">
              <span className="font-mono text-xs uppercase tracking-wider text-signal-soft">Mathematical Proof</span>
              <h2 className="mt-2 text-[26px] font-bold text-white sm:text-[34px]">
                Exhaustive 117-Cell Transition Completeness
              </h2>
              <p className="mt-2 max-w-[700px] text-sm text-muted">
                9 States × 13 Alphabet Symbols = 117 explicit cell entries. 15 valid protocol paths are explicitly registered in code, while 102 undefined combinations map to the absorbing TRAP sink.
              </p>
            </div>
          </Reveal>

          <div className="mt-10 overflow-x-auto rounded-card border border-line bg-surface p-4 sm:p-6">
            <table className="w-full min-w-[560px] text-left font-mono text-xs">
              <thead>
                <tr className="border-b border-line text-muted">
                  <th className="pb-3 pr-4 font-semibold">Transition Component</th>
                  <th className="pb-3 pr-4 font-semibold">Count</th>
                  <th className="pb-3 font-semibold">Formal Semantics</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line text-soft">
                <tr>
                  <td className="py-3 font-medium text-white">Explicit Valid Transitions</td>
                  <td className="py-3 text-signal-soft font-bold">15</td>
                  <td className="py-3 text-muted">Defined RFC HTTP protocol sequences (CONNECT, REQUEST, AUTH, RESP, CLOSE)</td>
                </tr>
                <tr>
                  <td className="py-3 font-medium text-white">Undefined Operational Pairs (7 states × 13 − 15)</td>
                  <td className="py-3 text-threat-soft font-bold">76</td>
                  <td className="py-3 text-muted">Any unpermitted symbol during operational state routes directly to TRAP</td>
                </tr>
                <tr>
                  <td className="py-3 font-medium text-white">Post-CLOSED Sequences</td>
                  <td className="py-3 text-threat-soft font-bold">13</td>
                  <td className="py-3 text-muted">∀σ ∈ Σ, δ(CLOSED, σ) = TRAP. No data allowed after terminal connection close</td>
                </tr>
                <tr>
                  <td className="py-3 font-medium text-white">TRAP Absorbing Self-Loops</td>
                  <td className="py-3 text-threat-soft font-bold">13</td>
                  <td className="py-3 text-muted">∀σ ∈ Σ, δ(TRAP, σ) = TRAP. Permanent absorbing sink state</td>
                </tr>
                <tr className="border-t-2 border-line-strong font-bold text-white">
                  <td className="py-3">Total Complete DFA Table (|Q × Σ|)</td>
                  <td className="py-3 text-trace-soft text-sm">117</td>
                  <td className="py-3 text-white">100% Total Function Coverage (No undefined cells)</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Container>
      </section>
    </>
  )
}
