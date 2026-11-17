import { useState } from 'react'
import { CheckCircle2, ArrowRight } from 'lucide-react'

import { Container } from '../components/Container'
import { PageHeader } from '../components/PageHeader'
import { Reveal } from '../components/Reveal'
import { ButtonLink } from '../components/Button'
import { HybridFormula } from '../components/HybridFormula'
import { hybridEngine, automatonSummary } from '../content'
import { cx } from '../lib/cx'

export function Technology() {
  const [selectedCategory, setSelectedCategory] = useState(0)

  return (
    <>
      <PageHeader
        eyebrow="Core Technology"
        title="Deterministic Automata Meets Statistical ML"
        body="TraceGuard AI replaces brittle signature databases and opaque deep-learning models with a dual-tiered detection engine: a mathematically total Deterministic Finite Automaton for protocol syntax, paired with an Isolation Forest for volumetric outliers."
      >
        <div className="mt-4 flex flex-wrap gap-3">
          <ButtonLink href="/automaton" variant="signal">
            <span>Automaton Specification</span>
            <ArrowRight className="size-4" aria-hidden />
          </ButtonLink>
          <ButtonLink href="#hybrid" variant="secondary">
            <span>Hybrid Formula</span>
          </ButtonLink>
        </div>
      </PageHeader>

      {/* Tier 1: Deterministic Finite Automaton */}
      <section className="border-t border-line bg-surface/40 py-20 sm:py-28">
        <Container size="xl">
          <Reveal>
            <div className="grid gap-10 lg:grid-cols-2 items-center">
              <div>
                <span className="font-mono text-xs uppercase tracking-wider text-signal-soft">Tier 1 Primitive</span>
                <h2 className="mt-2 text-[28px] font-bold text-white sm:text-[38px]">
                  Deterministic Finite Automaton (DFA)
                </h2>
                <p className="mt-4 text-pretty text-[16px] leading-relaxed text-soft">
                  The primary gate of TraceGuard AI is a complete 9-state HTTP protocol automaton. Because the set of valid HTTP event sequences constitutes a regular language, our DFA executes each state transition in deterministic <code className="rounded bg-surface-2 px-1.5 py-0.5 font-mono text-signal-soft">O(1)</code> time per event, achieving strictly linear <code className="rounded bg-surface-2 px-1.5 py-0.5 font-mono text-signal-soft">O(n)</code> processing for any sequence of <span className="font-mono text-white">n</span> session events.
                </p>

                <div className="mt-6 flex flex-col gap-3">
                  <div className="flex items-start gap-3 rounded-[14px] border border-line bg-surface p-3.5">
                    <CheckCircle2 className="mt-0.5 size-4 text-trace-soft shrink-0" />
                    <div className="text-xs">
                      <span className="font-semibold text-white">Mathematical Completeness</span>
                      <p className="text-muted">Total 9 × 13 = 117 transition matrix with an absorbing TRAP sink state prevents undefined behavior.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 rounded-[14px] border border-line bg-surface p-3.5">
                    <CheckCircle2 className="mt-0.5 size-4 text-trace-soft shrink-0" />
                    <div className="text-xs">
                      <span className="font-semibold text-white">Zero False Positives</span>
                      <p className="text-muted">Any session following RFC-compliant HTTP state transitions is mathematically guaranteed to be accepted.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 rounded-[14px] border border-line bg-surface p-3.5">
                    <CheckCircle2 className="mt-0.5 size-4 text-trace-soft shrink-0" />
                    <div className="text-xs">
                      <span className="font-semibold text-white">Constructive Proof-of-Violation</span>
                      <p className="text-muted">Rejected sequences yield exact causal state/symbol breach points for SOC investigators.</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Automaton 5-tuple display */}
              <div className="rounded-card border border-line bg-surface p-6 shadow-card">
                <div className="flex items-center justify-between border-b border-line pb-4 font-mono text-xs text-muted">
                  <span>Formal 5-Tuple Definition</span>
                  <span className="text-signal-soft">M = (Q, Σ, δ, q₀, F)</span>
                </div>
                <div className="mt-4 flex flex-col divide-y divide-line text-xs font-mono">
                  {automatonSummary.tuple.map((t) => (
                    <div key={t.symbol} className="py-3">
                      <span className="font-bold text-signal-soft">{t.symbol} ({t.name}):</span>
                      <p className="mt-1 font-sans text-soft">{t.detail}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Reveal>
        </Container>
      </section>

      {/* Tier 2: Feature Extraction & Isolation Forest */}
      <section className="border-t border-line bg-black py-20 sm:py-28">
        <Container size="xl">
          <Reveal>
            <div className="flex flex-col items-center text-center">
              <span className="font-mono text-xs uppercase tracking-wider text-trace-soft">Tier 2 Anomaly Detection</span>
              <h2 className="mt-2 text-[28px] font-bold text-white sm:text-[38px]">
                15 Session Features + Isolation Forest
              </h2>
              <p className="mt-3 max-w-[680px] text-[16px] text-muted">
                Attackers who obey legal protocol sequencing to perform credential stuffing or volumetric DOS are identified through multi-dimensional statistical feature profiling.
              </p>
            </div>
          </Reveal>

          {/* Interactive Feature Categories */}
          <div className="mt-12">
            <div className="flex flex-wrap justify-center gap-2 border-b border-line pb-4">
              {hybridEngine.features.map((cat, idx) => (
                <button
                  key={cat.category}
                  type="button"
                  onClick={() => setSelectedCategory(idx)}
                  className={cx(
                    'rounded-control px-4 py-2 font-mono text-xs font-medium transition-colors',
                    selectedCategory === idx
                      ? 'bg-trace text-black font-semibold'
                      : 'bg-surface text-muted hover:text-white border border-line',
                  )}
                >
                  {cat.category}
                </button>
              ))}
            </div>

            <div className="mt-6 mx-auto max-w-2xl rounded-card border border-trace-border bg-trace-wash p-6 text-center">
              <span className="font-mono text-xs text-trace-soft uppercase">
                Active Category: {hybridEngine.features[selectedCategory].category}
              </span>
              <div className="mt-4 flex flex-wrap justify-center gap-2.5">
                {hybridEngine.features[selectedCategory].items.map((item) => (
                  <span
                    key={item}
                    className="rounded-[10px] border border-trace-border bg-surface px-3 py-1.5 font-mono text-xs text-soft shadow-sm"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* ML Model Parameters Specs */}
          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-card border border-line bg-surface p-5">
              <div className="text-xs font-mono text-muted">Estimators (Trees)</div>
              <div className="mt-1 text-2xl font-bold text-white font-mono">100 Trees</div>
              <p className="mt-2 text-xs text-muted">Scikit-learn IsolationForest ensemble with random feature partitioning.</p>
            </div>
            <div className="rounded-card border border-line bg-surface p-5">
              <div className="text-xs font-mono text-muted">Contamination Ratio</div>
              <div className="mt-1 text-2xl font-bold text-trace-soft font-mono">0.10 (10%)</div>
              <p className="mt-2 text-xs text-muted">Baseline expected proportion of anomalies in training corpus.</p>
            </div>
            <div className="rounded-card border border-line bg-surface p-5">
              <div className="text-xs font-mono text-muted">Threshold Boundary</div>
              <div className="mt-1 text-2xl font-bold text-signal-soft font-mono">≥ 0.70</div>
              <p className="mt-2 text-xs text-muted">Normalized anomaly score threshold triggering ML anomalous flag.</p>
            </div>
            <div className="rounded-card border border-line bg-surface p-5">
              <div className="text-xs font-mono text-muted">Reproducibility Seed</div>
              <div className="mt-1 text-2xl font-bold text-white font-mono">seed = 42</div>
              <p className="mt-2 text-xs text-muted">Deterministic RNG seed ensuring consistent benchmark validation.</p>
            </div>
          </div>
        </Container>
      </section>

      {/* Tier 3: Hybrid Consensus */}
      <section id="hybrid" className="border-t border-line bg-surface/50 py-20 sm:py-28">
        <Container size="xl">
          <div className="grid gap-12 lg:grid-cols-2 items-center">
            <div>
              <span className="font-mono text-xs uppercase tracking-wider text-signal-soft">Consensus Engine</span>
              <h2 className="mt-2 text-[28px] font-bold text-white sm:text-[38px]">
                Tier 3: Hybrid Scoring & Safety Floor
              </h2>
              <p className="mt-4 text-pretty text-[16px] leading-relaxed text-soft">
                TraceGuard AI unifies the deterministic verdict of the DFA with the statistical likelihood of the Isolation Forest into a single, calibrated 0–100 risk score.
              </p>

              <div className="mt-6 flex flex-col gap-3 text-xs">
                <div className="rounded-[14px] border border-line bg-surface p-4">
                  <span className="font-semibold text-white">Why 60% FSM Weight?</span>
                  <p className="mt-1 text-muted">
                    Formal language theory provides deductive truth. When protocol syntax is broken, the session is definitively an attack or protocol defect, requiring immediate elevated priority.
                  </p>
                </div>
                <div className="rounded-[14px] border border-line bg-surface p-4">
                  <span className="font-semibold text-white">Why 40% ML Weight?</span>
                  <p className="mt-1 text-muted">
                    Volumetric deviations provide inductive signals. When sessions conform to grammar but exhibit 10x request rates or strange status code distributions, the ML score drives remediation.
                  </p>
                </div>
              </div>
            </div>

            <HybridFormula />
          </div>
        </Container>
      </section>
    </>
  )
}
