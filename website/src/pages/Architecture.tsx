import { Cpu, Database, Radio, Server, Shield, Terminal } from 'lucide-react'

import { Container } from '../components/Container'
import { PageHeader } from '../components/PageHeader'
import { PipelineViz } from '../components/PipelineViz'
import { Reveal } from '../components/Reveal'
import { ButtonLink } from '../components/Button'

export function Architecture() {
  return (
    <>
      <PageHeader
        eyebrow="System Design"
        title="Detection Pipeline & Technical Architecture"
        body="TraceGuard AI is designed as a high-throughput, low-latency intrusion detection pipeline that combines stream processing, deterministic automata replay, and unsupervised ML."
      >
        <div className="mt-4 flex gap-3">
          <ButtonLink href="#pipeline" variant="signal">
            <span>Explore 8 Stages</span>
          </ButtonLink>
          <ButtonLink href="https://github.com/ojas-mohbansi/TRACEGUARD-AI" variant="secondary" target="_blank" rel="noreferrer">
            <span>View Source Code</span>
          </ButtonLink>
        </div>
      </PageHeader>

      {/* 8-Stage Sequential Detection Pipeline */}
      <section id="pipeline" className="border-t border-line bg-surface/40 py-20 sm:py-28">
        <Container size="xl">
          <Reveal>
            <div className="flex flex-col items-center text-center">
              <span className="font-mono text-xs uppercase tracking-wider text-signal-soft">Execution Flow</span>
              <h2 className="mt-2 text-[28px] font-bold text-white sm:text-[38px]">
                End-to-End Ingestion to Telemetry Pipeline
              </h2>
              <p className="mt-3 max-w-[660px] text-sm text-muted">
                Each incoming network session is ingested, reconstructed into chronological order, verified against the formal automaton, scored by Isolation Forest, and broadcast via WebSockets.
              </p>
            </div>
          </Reveal>

          <div className="mt-14">
            <PipelineViz />
          </div>
        </Container>
      </section>

      {/* Technology Stack Grid */}
      <section className="border-t border-line bg-black py-20 sm:py-28">
        <Container size="xl">
          <Reveal>
            <div className="flex flex-col items-center text-center">
              <span className="font-mono text-xs uppercase tracking-wider text-trace-soft">Software Stack</span>
              <h2 className="mt-2 text-[28px] font-bold text-white sm:text-[38px]">
                Production Engineering Stack
              </h2>
              <p className="mt-3 max-w-[620px] text-sm text-muted">
                Engineered with modern, type-safe primitives across both backend detection microservices and client telemetry interfaces.
              </p>
            </div>
          </Reveal>

          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="flex flex-col gap-3 rounded-card border border-line bg-surface p-6">
              <div className="flex items-center gap-3">
                <div className="grid size-10 place-items-center rounded-[12px] bg-signal-wash text-signal-soft">
                  <Server className="size-5" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-base">Backend Engine</h3>
                  <span className="font-mono text-xs text-muted">Python 3.11 + FastAPI</span>
                </div>
              </div>
              <p className="text-xs text-soft leading-relaxed">
                Asynchronous event processing powered by Uvicorn. High-performance REST endpoints paired with real-time full-duplex WebSocket channels.
              </p>
            </div>

            <div className="flex flex-col gap-3 rounded-card border border-line bg-surface p-6">
              <div className="flex items-center gap-3">
                <div className="grid size-10 place-items-center rounded-[12px] bg-trace-wash text-trace-soft">
                  <Shield className="size-5" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-base">Dual Detection Tiers</h3>
                  <span className="font-mono text-xs text-muted">FSM + scikit-learn</span>
                </div>
              </div>
              <p className="text-xs text-soft leading-relaxed">
                Native O(1) Deterministic Finite Automaton combined with an unsupervised 100-tree IsolationForest model over 15 extracted session features.
              </p>
            </div>

            <div className="flex flex-col gap-3 rounded-card border border-line bg-surface p-6">
              <div className="flex items-center gap-3">
                <div className="grid size-10 place-items-center rounded-[12px] bg-white/[0.06] text-white">
                  <Database className="size-5" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-base">Persistence Layer</h3>
                  <span className="font-mono text-xs text-muted">SQLAlchemy 2.0 + SQLite</span>
                </div>
              </div>
              <p className="text-xs text-soft leading-relaxed">
                ACID-compliant relational storage logging full session metadata, transition proofs, anomaly vectors, and tamper-resistant audit trails.
              </p>
            </div>

            <div className="flex flex-col gap-3 rounded-card border border-line bg-surface p-6">
              <div className="flex items-center gap-3">
                <div className="grid size-10 place-items-center rounded-[12px] bg-signal-wash text-signal-soft">
                  <Radio className="size-5" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-base">Live Telemetry</h3>
                  <span className="font-mono text-xs text-muted">WebSocket Stream</span>
                </div>
              </div>
              <p className="text-xs text-soft leading-relaxed">
                Zero-polling event push delivering sub-second anomaly alerts and live state machine transitions directly to connected operator dashboards.
              </p>
            </div>

            <div className="flex flex-col gap-3 rounded-card border border-line bg-surface p-6">
              <div className="flex items-center gap-3">
                <div className="grid size-10 place-items-center rounded-[12px] bg-trace-wash text-trace-soft">
                  <Cpu className="size-5" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-base">Frontend Platform</h3>
                  <span className="font-mono text-xs text-muted">React 19 + TypeScript + Vite</span>
                </div>
              </div>
              <p className="text-xs text-soft leading-relaxed">
                Zero-slop interface with Tailwind CSS v4, Motion physics, accessible semantic landmarks, and reactive state machine visualizers.
              </p>
            </div>

            <div className="flex flex-col gap-3 rounded-card border border-line bg-surface p-6">
              <div className="flex items-center gap-3">
                <div className="grid size-10 place-items-center rounded-[12px] bg-white/[0.06] text-white">
                  <Terminal className="size-5" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-base">Deployment Engine</h3>
                  <span className="font-mono text-xs text-muted">Docker Compose</span>
                </div>
              </div>
              <p className="text-xs text-soft leading-relaxed">
                Reproducible containerized architecture orchestrating backend API, simulator services, and frontend presentation environments in one command.
              </p>
            </div>
          </div>
        </Container>
      </section>
    </>
  )
}
