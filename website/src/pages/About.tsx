import { CheckCircle2, GraduationCap, BookOpen, Layers, ShieldCheck, ArrowRight } from 'lucide-react'

import { Container } from '../components/Container'
import { PageHeader } from '../components/PageHeader'
import { Reveal } from '../components/Reveal'
import { ButtonLink } from '../components/Button'
import { about } from '../content'

const PEDAGOGICAL_OBJECTIVES = [
  {
    icon: Layers,
    title: 'Language Theoretic Formalism',
    body: 'Translating RFC HTTP protocol grammars into a Total Complete Deterministic Finite Automaton M = (Q, Σ, δ, q₀, F) to eliminate state desynchronization and sequence manipulation.',
    badge: 'Formal Theory',
  },
  {
    icon: ShieldCheck,
    title: 'Hybrid Dual-Tier Consensus',
    body: 'Pairing formal language verification with unsupervised Isolation Forest modeling to catch both out-of-order protocol violations and volumetric rate outliers with an enforced 60% safety floor.',
    badge: 'Consensus Logic',
  },
  {
    icon: BookOpen,
    title: 'Constructive Proofs for SOC Teams',
    body: 'Replacing opaque neural black boxes with constructive formal proofs: rejected traces output the exact causal state-symbol violation pair and reproducible transition logs.',
    badge: 'Explainability',
  },
]

export function About() {
  return (
    <>
      <PageHeader
        eyebrow={about.eyebrow}
        title={about.title}
        body={about.body}
      />

      {/* Institutional Context & Registry */}
      <section className="border-t border-line bg-surface/40 py-20 sm:py-28">
        <Container size="xl">
          <div className="grid gap-10 lg:grid-cols-2 items-center">
            <Reveal>
              <div>
                <span className="font-mono text-xs uppercase tracking-wider text-signal-soft">Contextual Overview</span>
                <h2 className="mt-2 text-[28px] font-bold text-white sm:text-[36px]">
                  Bridging Automata Theory & Applied Security
                </h2>
                <p className="mt-4 text-pretty text-[15px] leading-relaxed text-soft">
                  Theory of Computation is frequently taught as pure mathematical abstraction — pumping lemmas, equivalence partitions, Turing completeness, and decidability proofs.
                </p>
                <p className="mt-3 text-pretty text-[15px] leading-relaxed text-soft">
                  TraceGuard AI demonstrates that these exact theoretical principles solve one of the most stubborn challenges in modern cybersecurity: verifying state integrity in application protocols without state desynchronization or exponential signature bloat.
                </p>

                <div className="mt-6 flex flex-col gap-3">
                  <div className="flex items-center gap-3 rounded-[14px] border border-line bg-surface p-3.5">
                    <CheckCircle2 className="size-4 text-trace-soft shrink-0" />
                    <span className="text-xs text-soft">
                      149 / 149 passing unit, integration, and security tests in CI
                    </span>
                  </div>
                  <div className="flex items-center gap-3 rounded-[14px] border border-line bg-surface p-3.5">
                    <CheckCircle2 className="size-4 text-trace-soft shrink-0" />
                    <span className="text-xs text-soft">
                      Complete Total DFA coverage with 117 transition entries
                    </span>
                  </div>
                  <div className="flex items-center gap-3 rounded-[14px] border border-line bg-surface p-3.5">
                    <CheckCircle2 className="size-4 text-trace-soft shrink-0" />
                    <span className="text-xs text-soft">
                      Deterministic O(1) step complexity for protocol verification
                    </span>
                  </div>
                </div>
              </div>
            </Reveal>

            {/* Course Metadata Card */}
            <Reveal delay={0.1}>
              <div className="rounded-card border border-line bg-surface p-6 shadow-card">
                <div className="flex items-center gap-2 border-b border-line pb-4 font-mono text-xs font-semibold text-white">
                  <GraduationCap className="size-4 text-signal-soft" />
                  <span>Academic Metadata Registry</span>
                </div>
                <div className="mt-4 divide-y divide-line text-xs font-mono">
                  {about.metadata.map((item) => (
                    <div key={item.label} className="flex flex-col py-3 sm:flex-row sm:justify-between sm:items-center gap-1">
                      <span className="text-muted">{item.label}</span>
                      <span className="font-semibold text-white">{item.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </Reveal>
          </div>
        </Container>
      </section>

      {/* Pedagogical Objectives & Research Pillars */}
      <section className="border-t border-line bg-black py-20 sm:py-28">
        <Container size="xl">
          <Reveal>
            <div className="flex flex-col items-center text-center">
              <span className="font-mono text-xs uppercase tracking-wider text-trace-soft">Curriculum Milestones</span>
              <h2 className="mt-2 text-[28px] font-bold text-white sm:text-[36px]">
                Capstone Pedagogical Objectives
              </h2>
              <p className="mt-3 max-w-[680px] text-sm text-muted">
                Engineered to satisfy rigorous degree capstone criteria: bridging abstract mathematical formalisms with production-ready software engineering.
              </p>
            </div>
          </Reveal>

          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {PEDAGOGICAL_OBJECTIVES.map((obj, i) => {
              const Icon = obj.icon
              return (
                <Reveal key={obj.title} delay={i * 0.1}>
                  <div className="flex h-full flex-col justify-between rounded-card border border-line bg-surface p-6 transition-colors hover:border-signal-border hover:bg-surface-2">
                    <div>
                      <div className="flex items-center justify-between pb-3 border-b border-line">
                        <span className="rounded-control border border-signal-border bg-signal-wash px-2.5 py-0.5 font-mono text-[11px] text-signal-soft">
                          {obj.badge}
                        </span>
                        <Icon className="size-4 text-muted" aria-hidden="true" />
                      </div>
                      <h3 className="mt-4 text-[17px] font-semibold text-white">{obj.title}</h3>
                      <p className="mt-2 text-[14px] leading-relaxed text-muted">{obj.body}</p>
                    </div>
                  </div>
                </Reveal>
              )
            })}
          </div>

          <div className="mt-14 flex flex-wrap justify-center gap-4">
            <ButtonLink href="/presentation" variant="signal" size="md">
              <span>View Defense Presentation Deck</span>
              <ArrowRight className="size-4" aria-hidden="true" />
            </ButtonLink>
            <ButtonLink href="/research" variant="secondary" size="md">
              <span>Inspect Evaluation Benchmarks</span>
            </ButtonLink>
          </div>
        </Container>
      </section>
    </>
  )
}
