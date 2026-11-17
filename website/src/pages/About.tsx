import { CheckCircle2, GraduationCap } from 'lucide-react'

import { Container } from '../components/Container'
import { PageHeader } from '../components/PageHeader'
import { Reveal } from '../components/Reveal'
import { about } from '../content'

export function About() {
  return (
    <>
      <PageHeader
        eyebrow={about.eyebrow}
        title={about.title}
        body={about.body}
      />

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
    </>
  )
}
