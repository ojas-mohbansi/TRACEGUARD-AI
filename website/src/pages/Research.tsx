import { AlertTriangle } from 'lucide-react'

import { Container } from '../components/Container'
import { PageHeader } from '../components/PageHeader'
import { Reveal } from '../components/Reveal'
import { research } from '../content'

export function Research() {
  return (
    <>
      <PageHeader
        eyebrow="Academic Evaluation"
        title="Research Methodology & Corpus Benchmarks"
        body="TraceGuard AI was developed and evaluated against a controlled 600-session benchmark corpus (seed=42). We document all empirical findings, mathematical foundations, and system constraints with scientific rigor."
      />

      {/* 100-Session Calibrated Corpus Breakdown */}
      <section className="border-t border-line bg-surface/40 py-20 sm:py-28">
        <Container size="xl">
          <Reveal>
            <div className="flex flex-col items-center text-center">
              <span className="font-mono text-xs uppercase tracking-wider text-signal-soft">Corpus Attribution</span>
              <h2 className="mt-2 text-[28px] font-bold text-white sm:text-[38px]">
                Alert Provenance on Calibrated Corpus
              </h2>
              <p className="mt-3 max-w-[680px] text-sm text-muted">
                In our calibrated multi-stage corpus, every alert event was traceable to an exact mathematical mechanism. Zero alerts were left unexplained.
              </p>
            </div>
          </Reveal>

          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {research.attributionData.map((item) => (
              <div key={item.label} className="flex flex-col justify-between rounded-card border border-line bg-surface p-6 shadow-card">
                <div>
                  <div className="font-mono text-3xl font-bold text-white">{item.percent}</div>
                  <div className="mt-1 text-sm font-semibold text-signal-soft">{item.label}</div>
                  <div className="mt-0.5 font-mono text-xs text-muted">{item.count}</div>
                  <p className="mt-3 text-xs leading-relaxed text-soft">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 rounded-card border border-line bg-surface-2 p-5 text-center text-xs text-soft">
            <span className="font-mono font-semibold text-trace-soft">100% Causal Explainability: </span>
            Unlike deep learning black-box classifiers where attribution is opaque, TraceGuard AI provides formal state-edge counterexamples for FSM events and feature contribution indices for ML events.
          </div>
        </Container>
      </section>

      {/* Synthetic Benchmark Results */}
      <section className="border-t border-line bg-black py-20 sm:py-28">
        <Container size="xl">
          <Reveal>
            <div className="flex flex-col items-center text-center">
              <span className="font-mono text-xs uppercase tracking-wider text-trace-soft">Synthetic Benchmark</span>
              <h2 className="mt-2 text-[28px] font-bold text-white sm:text-[38px]">
                Isolation Forest Evaluation
              </h2>
              <p className="mt-3 max-w-[660px] text-sm text-muted">
                {research.benchmarks.note}
              </p>
            </div>
          </Reveal>

          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {research.benchmarks.metrics.map((m) => (
              <div key={m.label} className="rounded-card border border-line bg-surface p-6">
                <div className="font-mono text-xs text-muted">{m.label}</div>
                <div className="mt-2 text-3xl font-bold text-white font-mono">{m.value}</div>
                <div className="mt-2 text-xs text-soft">{m.detail}</div>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* Chomsky Hierarchy & Formal Foundations */}
      <section className="border-t border-line bg-surface/50 py-20 sm:py-28">
        <Container size="xl">
          <Reveal>
            <div className="grid gap-10 lg:grid-cols-2 items-center">
              <div>
                <span className="font-mono text-xs uppercase tracking-wider text-signal-soft">Theoretical Foundations</span>
                <h2 className="mt-2 text-[28px] font-bold text-white sm:text-[36px]">
                  Placement in the Chomsky Hierarchy
                </h2>
                <p className="mt-4 text-pretty text-[15px] leading-relaxed text-soft">
                  A central question of Theory of Computation is: <em>what class of automaton is required to recognize a language?</em>
                </p>
                <div className="mt-5 flex flex-col gap-3 text-xs leading-relaxed text-muted">
                  <div className="rounded-[14px] border border-line bg-surface p-4">
                    <span className="font-semibold text-white">Regular Languages (Type 3) — The Protocol Lifecycle</span>
                    <p className="mt-1">
                      The sequencing of HTTP events (CONNECT → REQUEST → AUTH → RESPONSE → CLOSE) has finite memory and no recursion. Thus, a Deterministic Finite Automaton (Type 3) is strictly sufficient, executing in deterministic O(1) time.
                    </p>
                  </div>
                  <div className="rounded-[14px] border border-line bg-surface p-4">
                    <span className="font-semibold text-white">Context-Free Languages (Type 2) — Payload Inspection</span>
                    <p className="mt-1">
                      Nested JSON bodies, XML schemas, or mathematical expressions require pushdown automata with stack memory. TraceGuard AI deliberately decouples session sequencing (DFA) from payload parsing.
                    </p>
                  </div>
                </div>
              </div>

              {/* Theoretical Summary Box */}
              <div className="rounded-card border border-line bg-surface p-6">
                <div className="border-b border-line pb-3 font-mono text-xs font-semibold text-signal-soft">
                  Chomsky Classification Summary
                </div>
                <div className="mt-4 space-y-3 font-mono text-xs">
                  <div className="flex justify-between border-b border-line pb-2">
                    <span className="text-muted">Grammar Type:</span>
                    <span className="text-white">Type 3 (Regular Grammar)</span>
                  </div>
                  <div className="flex justify-between border-b border-line pb-2">
                    <span className="text-muted">Machine Model:</span>
                    <span className="text-white">Total Deterministic Finite Automaton</span>
                  </div>
                  <div className="flex justify-between border-b border-line pb-2">
                    <span className="text-muted">Per-Event Complexity:</span>
                    <span className="text-trace-soft font-bold">O(1) Time, O(1) Space</span>
                  </div>
                  <div className="flex justify-between border-b border-line pb-2">
                    <span className="text-muted">Completeness:</span>
                    <span className="text-white">117 cells (Total transition matrix)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted">Dead State:</span>
                    <span className="text-threat-soft font-bold">TRAP (Absorbing Sink)</span>
                  </div>
                </div>
              </div>
            </div>
          </Reveal>
        </Container>
      </section>

      {/* Documented Academic Limitations */}
      <section className="border-t border-line bg-black py-20 sm:py-28">
        <Container size="xl">
          <Reveal>
            <div className="flex flex-col items-center text-center">
              <span className="font-mono text-xs uppercase tracking-wider text-warn-soft">Scientific Transparency</span>
              <h2 className="mt-2 text-[28px] font-bold text-white sm:text-[38px]">
                Documented Academic Limitations
              </h2>
              <p className="mt-3 max-w-[680px] text-sm text-muted">
                Per the project charter and academic honesty principles, the following constraints are documented to establish the precise research scope.
              </p>
            </div>
          </Reveal>

          <div className="mt-12 grid gap-6 sm:grid-cols-2">
            {research.limitations.map((lim) => (
              <div key={lim.title} className="flex gap-4 rounded-card border border-line bg-surface p-6">
                <div className="grid size-10 place-items-center rounded-[12px] bg-warn-wash text-warn-soft shrink-0">
                  <AlertTriangle className="size-5" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-base">{lim.title}</h3>
                  <p className="mt-2 text-xs leading-relaxed text-muted">{lim.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </Container>
      </section>
    </>
  )
}
