import { AlertCircle, ArrowRight } from 'lucide-react'
import { Container } from '../components/Container'
import { Reveal } from '../components/Reveal'
import { ButtonLink } from '../components/Button'
import { research } from '../content'

export function ResearchSection() {
  return (
    <section aria-labelledby="research-title" className="border-t border-line bg-bg-deep py-24 sm:py-32">
      <Container size="xl">
        <Reveal>
          <div className="flex flex-col items-center text-center">
            <span className="font-mono text-xs uppercase tracking-wider text-trace-soft">
              {research.eyebrow}
            </span>
            <h2 id="research-title" className="mt-3 text-balance text-[32px] font-semibold tracking-[-0.02em] text-white sm:text-[44px]">
              {research.title}
            </h2>
            <p className="mt-3 max-w-[680px] text-pretty text-[16px] text-muted">
              TraceGuard AI is an academic research prototype. We document all benchmark methodologies, attribution splits, and theoretical boundaries with zero exaggeration.
            </p>
          </div>
        </Reveal>

        {/* 100-session Corpus Attribution Grid */}
        <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {research.attributionData.map((item, idx) => (
            <Reveal key={item.label} delay={idx * 0.08}>
              <div className="flex h-full flex-col justify-between rounded-card border border-line bg-surface p-6">
                <div>
                  <div className="text-[32px] font-bold text-white font-mono">{item.percent}</div>
                  <div className="mt-1 text-sm font-semibold text-signal-soft">{item.label}</div>
                  <div className="text-xs font-mono text-faint">{item.count}</div>
                  <p className="mt-3 text-xs leading-relaxed text-muted">{item.desc}</p>
                </div>
              </div>
            </Reveal>
          ))}
        </div>

        {/* Transparent Limitations Callouts */}
        <div className="mt-10 rounded-card border border-line bg-surface p-6 sm:p-8">
          <div className="flex items-center gap-2 pb-4 border-b border-line text-sm font-semibold text-white">
            <AlertCircle className="size-4 text-warn-soft" aria-hidden />
            <span>Documented Academic Limitations</span>
          </div>
          <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-4 text-xs">
            {research.limitations.map((lim) => (
              <div key={lim.title} className="flex flex-col gap-1.5">
                <span className="font-semibold text-white font-mono">{lim.title}</span>
                <p className="leading-relaxed text-muted">{lim.desc}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-12 flex justify-center gap-4 flex-wrap">
          <ButtonLink href="/research" variant="signal" size="md">
            <span>Read Research Benchmarks</span>
            <ArrowRight className="size-4" aria-hidden />
          </ButtonLink>
          <ButtonLink href="/presentation" variant="secondary" size="md">
            <span>View Capstone Defense Deck</span>
          </ButtonLink>
        </div>
      </Container>
    </section>
  )
}
