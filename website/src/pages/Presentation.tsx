import { Clock, FileText, ArrowUpRight, ExternalLink } from 'lucide-react'

import { Container } from '../components/Container'
import { PageHeader } from '../components/PageHeader'
import { Reveal } from '../components/Reveal'
import { brand, defense } from '../content'

export function Presentation() {
  return (
    <>
      <PageHeader
        eyebrow="Capstone Examination"
        title="Theory of Computation Defense Deck"
        body="Materials prepared for the institutional defense panel, committee viva examination, and technical project review."
      >
        <div className="mt-4 flex flex-wrap gap-3">
          <a
            href="/docs/presentation/PRESENTATION_TEAM_OVERVIEW.md"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex h-9 items-center gap-1.5 rounded-[8px] bg-signal px-4 text-xs font-mono font-medium text-white shadow-sm hover:bg-signal-2 transition-colors"
          >
            <span>Team Presentation Overview</span>
            <ArrowUpRight className="size-3.5" />
          </a>
          <a
            href={`${brand.github}/tree/main/presentation`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex h-9 items-center gap-1.5 rounded-[8px] border border-line bg-surface px-4 text-xs font-mono font-medium text-soft hover:text-white hover:border-signal-border transition-colors"
          >
            <span>View Editorial Deck on GitHub</span>
            <ExternalLink className="size-3.5" />
          </a>
        </div>
      </PageHeader>

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

      {/* Speaker Timetable (15m 20s) */}
      <section className="border-t border-line bg-black py-20 sm:py-28">
        <Container size="xl">
          <Reveal>
            <div className="flex flex-col items-center text-center">
              <span className="font-mono text-xs uppercase tracking-wider text-signal-soft">Defense Schedule</span>
              <h2 className="mt-2 text-[28px] font-bold text-white sm:text-[36px]">
                15m 20s Structured Presentation Protocol
              </h2>
              <p className="mt-2 max-w-[620px] text-sm text-muted">
                Each section aligns with an essential facet of formal language theory, implementation engineering, and academic evaluation.
              </p>
            </div>
          </Reveal>

          <div className="mt-12 flex flex-col gap-3">
            {defense.speakers.map((spk, idx) => (
              <div
                key={spk.name}
                className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-card border border-line bg-surface p-5 hover:border-signal-border transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="grid size-9 place-items-center rounded-control bg-signal-wash text-signal-soft font-mono text-xs font-bold">
                    0{idx + 1}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-white text-sm sm:text-base">{spk.role}</h3>
                      <span className="rounded bg-surface-2 px-1.5 py-0.5 text-[10px] font-mono text-signal-soft border border-line">
                        {spk.slides}
                      </span>
                    </div>
                    <p className="text-xs text-soft mt-0.5">{spk.topic}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <div className="flex items-center gap-1.5 text-xs font-mono text-muted">
                    <Clock className="size-3.5 text-signal-soft" />
                    <span>{spk.duration} allocated</span>
                  </div>
                  <a
                    href={`/docs/presentation/presenter_${idx + 1}.md`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 rounded-[8px] border border-line bg-surface-2 px-3 py-1.5 font-mono text-xs text-soft hover:text-white hover:border-signal-border transition-colors focus:outline-none focus-visible:ring-1 focus-visible:ring-signal"
                    aria-label={`View ${spk.name} Speaking Guide (opens markdown in new tab)`}
                  >
                    <span>Speaking Guide</span>
                    <ArrowUpRight className="size-3 text-signal-soft" />
                  </a>
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
              <a
                key={doc.title}
                href={`${brand.github}/tree/main/docs`}
                target="_blank"
                rel="noopener noreferrer"
                className="group flex flex-col justify-between rounded-card border border-line bg-surface p-5 shadow-card hover:border-signal-border transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-signal"
              >
                <div>
                  <div className="flex items-center justify-between text-signal-soft">
                    <div className="flex items-center gap-2">
                      <FileText className="size-4" />
                      <span className="font-mono text-xs font-bold text-white group-hover:text-signal-soft transition-colors">{doc.title}</span>
                    </div>
                    <ArrowUpRight className="size-3.5 text-muted group-hover:text-signal-soft transition-colors" />
                  </div>
                  <p className="mt-2 text-xs leading-relaxed text-soft">{doc.desc}</p>
                </div>
                <div className="mt-4 pt-3 border-t border-line text-[11px] font-mono text-muted flex items-center justify-between">
                  <span>Academic Specification</span>
                  <span className="text-signal-soft font-mono">View on GitHub →</span>
                </div>
              </a>
            ))}
          </div>
        </Container>
      </section>
    </>
  )
}

