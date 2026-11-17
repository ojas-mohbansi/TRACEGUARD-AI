import { Shield, Sparkles, ArrowRight } from 'lucide-react'
import { Container } from '../components/Container'
import { Reveal } from '../components/Reveal'
import { ButtonLink } from '../components/Button'
import { HybridFormula } from '../components/HybridFormula'
import { hybridEngine } from '../content'

export function HybridSection() {
  return (
    <section aria-labelledby="hybrid-title" className="border-t border-line bg-black py-24 sm:py-32">
      <Container size="xl">
        <div className="grid gap-12 lg:grid-cols-[1.1fr_1fr] items-center">
          <Reveal>
            <div className="flex flex-col items-start gap-5">
              <span className="font-mono text-xs uppercase tracking-wider text-signal-soft">
                {hybridEngine.eyebrow}
              </span>
              <h2 id="hybrid-title" className="text-balance text-[32px] font-semibold tracking-[-0.02em] text-white sm:text-[44px]">
                {hybridEngine.title}
              </h2>
              <p className="text-pretty text-[16px] leading-relaxed text-soft">
                {hybridEngine.body}
              </p>

              <div className="mt-2 grid w-full gap-3 sm:grid-cols-2">
                <div className="rounded-[16px] border border-signal-border bg-signal-wash p-4">
                  <div className="flex items-center gap-2 font-mono text-xs font-semibold text-signal-soft">
                    <Shield className="size-4" aria-hidden />
                    <span>Tier 1: Formal Grammar</span>
                  </div>
                  <p className="mt-1.5 text-xs text-soft">
                    Zero false positives on compliant sessions. Instant proof-of-violation when order breaks.
                  </p>
                </div>

                <div className="rounded-[16px] border border-trace-border bg-trace-wash p-4">
                  <div className="flex items-center gap-2 font-mono text-xs font-semibold text-trace-soft">
                    <Sparkles className="size-4" aria-hidden />
                    <span>Tier 2: Isolation Forest</span>
                  </div>
                  <p className="mt-1.5 text-xs text-soft">
                    Detects volumetric spikes, rate bursts, and behavioral timing anomalies across 15 features.
                  </p>
                </div>
              </div>

              {/* 4 Quadrants Summary */}
              <div className="mt-2 w-full overflow-hidden rounded-[16px] border border-line bg-surface">
                <div className="border-b border-line bg-surface-2 px-4 py-2.5 font-mono text-[11px] font-semibold uppercase text-muted">
                  Detection Quadrants
                </div>
                <div className="divide-y divide-line text-xs">
                  {hybridEngine.quadrants.map((q) => (
                    <div key={q.name} className="flex flex-wrap items-center justify-between gap-2 p-3">
                      <div>
                        <span className="font-semibold text-white">{q.name}</span>
                        <div className="text-[11px] text-faint font-mono">{q.fsm} · {q.ml}</div>
                      </div>
                      <span className="font-mono text-xs font-medium text-signal-soft">
                        {q.verdict}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-2">
                <ButtonLink href="/technology" variant="signal" size="md">
                  <span>Explore Technology & Formulas</span>
                  <ArrowRight className="size-4" aria-hidden />
                </ButtonLink>
              </div>
            </div>
          </Reveal>

          <Reveal delay={0.15}>
            <HybridFormula />
          </Reveal>
        </div>
      </Container>
    </section>
  )
}
