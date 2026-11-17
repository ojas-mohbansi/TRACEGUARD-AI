import { Clock, FileText } from 'lucide-react'

import { Container } from '../components/Container'
import { PageHeader } from '../components/PageHeader'
import { Reveal } from '../components/Reveal'
import { defense } from '../content'

export function Presentation() {
  return (
    <>
      <PageHeader
        eyebrow="Capstone Examination"
        title="Theory of Computation Defense Deck"
        body="Materials prepared for the institutional defense panel, committee viva examination, and technical project review."
      />

      {/* Defense Deck Key Metrics */}
      <section className="border-t border-line bg-surface/40 py-16 sm:py-24">
        <Container size="xl">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {defense.stats.map((s) => (
              <div key={s.label} className="rounded-card border border-line bg-surface p-6 shadow-card">
                <div className="text-xs font-mono text-muted">{s.label}</div>
                <div className="mt-2 text-3xl font-bold text-white font-mono">{s.value}</div>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* Speaker Timetable (13m 30s) */}
      <section className="border-t border-line bg-black py-20 sm:py-28">
        <Container size="xl">
          <Reveal>
            <div className="flex flex-col items-center text-center">
              <span className="font-mono text-xs uppercase tracking-wider text-signal-soft">Defense Schedule</span>
              <h2 className="mt-2 text-[28px] font-bold text-white sm:text-[36px]">
                13m 30s Structured Presentation Protocol
              </h2>
              <p className="mt-2 max-w-[620px] text-sm text-muted">
                Each section aligns with an essential facet of formal language theory, implementation engineering, and academic evaluation.
              </p>
            </div>
          </Reveal>

          <div className="mt-12 flex flex-col gap-3">
            {defense.speakers.map((spk, idx) => (
              <div
                key={spk.role}
                className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-card border border-line bg-surface p-5 hover:border-signal-border transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="grid size-9 place-items-center rounded-control bg-signal-wash text-signal-soft font-mono text-xs font-bold">
                    0{idx + 1}
                  </div>
                  <div>
                    <h3 className="font-semibold text-white text-sm sm:text-base">{spk.role}</h3>
                    <p className="text-xs text-soft">{spk.topic}</p>
                  </div>
                </div>
                <div className="flex items-center gap-1.5 text-xs font-mono text-muted">
                  <Clock className="size-3.5 text-signal-soft" />
                  <span>2m 42s allocated</span>
                </div>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* Primary Academic Artifacts */}
      <section className="border-t border-line bg-surface/50 py-20 sm:py-28">
        <Container size="xl">
          <Reveal>
            <div className="flex flex-col items-center text-center">
              <span className="font-mono text-xs uppercase tracking-wider text-trace-soft">Research Artifacts</span>
              <h2 className="mt-2 text-[28px] font-bold text-white sm:text-[36px]">
                Comprehensive Committee Documentation
              </h2>
              <p className="mt-2 max-w-[620px] text-sm text-muted">
                The repository includes full formal proofs, transition matrices, algorithm derivations, and viva Q&A preparation guides.
              </p>
            </div>
          </Reveal>

          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {defense.documents.map((doc) => (
              <div key={doc.title} className="flex flex-col justify-between rounded-card border border-line bg-surface p-5 shadow-card">
                <div>
                  <div className="flex items-center gap-2 text-signal-soft">
                    <FileText className="size-4" />
                    <span className="font-mono text-xs font-bold">{doc.title}</span>
                  </div>
                  <p className="mt-2 text-xs leading-relaxed text-soft">{doc.desc}</p>
                </div>
                <div className="mt-4 pt-3 border-t border-line text-[11px] font-mono text-muted">
                  Academic Publication Standard
                </div>
              </div>
            ))}
          </div>
        </Container>
      </section>
    </>
  )
}
