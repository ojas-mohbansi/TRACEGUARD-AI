import { ArrowRight } from 'lucide-react'
import { Container } from '../components/Container'
import { Reveal } from '../components/Reveal'
import { ButtonLink } from '../components/Button'
import { PipelineViz } from '../components/PipelineViz'
import { pipeline } from '../content'

export function PipelineSection() {
  return (
    <section aria-labelledby="pipeline-title" className="border-t border-line bg-surface/50 py-24 sm:py-32">
      <Container size="xl">
        <Reveal>
          <div className="flex flex-col items-center text-center">
            <span className="font-mono text-xs uppercase tracking-wider text-signal-soft">
              {pipeline.eyebrow}
            </span>
            <h2 id="pipeline-title" className="mt-3 text-balance text-[32px] font-semibold tracking-[-0.02em] text-white sm:text-[44px]">
              {pipeline.title}
            </h2>
            <p className="mt-3 max-w-[640px] text-pretty text-[16px] text-muted">
              From raw network packet ingestion to formal automata validation and real-time frontend telemetry dispatch.
            </p>
          </div>
        </Reveal>

        <div className="mt-14">
          <PipelineViz />
        </div>

        <div className="mt-12 flex justify-center">
          <ButtonLink href="/architecture" variant="secondary" size="md">
            <span>Inspect Full Pipeline & Components</span>
            <ArrowRight className="size-4" aria-hidden />
          </ButtonLink>
        </div>
      </Container>
    </section>
  )
}
