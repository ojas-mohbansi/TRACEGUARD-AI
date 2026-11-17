import { AlertOctagon } from 'lucide-react'
import { ButtonLink } from '../components/Button'
import { Container } from '../components/Container'
import { LinkRow } from '../components/Controls'
import { notFound } from '../content'

export function NotFound() {
  return (
    <section aria-labelledby="nf-title" className="signal-wash-bg relative isolate overflow-hidden pb-24 pt-36 sm:pt-44">
      <Container size="md" className="flex flex-col items-center text-center">
        <div className="grid size-16 place-items-center rounded-card border border-threat-border bg-threat-wash text-threat-soft">
          <AlertOctagon className="size-8" aria-hidden />
        </div>
        <p className="mt-6 font-mono text-xs font-semibold uppercase tracking-wider text-threat-soft">
          Automaton Error 404 · Unrecognized State
        </p>
        <h1 id="nf-title" className="display mt-2 text-[38px] font-bold text-white sm:text-[52px]">
          {notFound.title}
        </h1>
        <p className="mt-3 max-w-[460px] text-[16px] text-soft">{notFound.body}</p>
        <ButtonLink href="/" variant="signal" size="lg" className="mt-8">
          Reset Automaton to Initial (q₀)
        </ButtonLink>
        <ul className="mt-14 w-full max-w-[520px] text-left">
          <li>
            <LinkRow href="/technology" title="Technology" body="Dual-tiered FSM and Isolation Forest architecture." />
          </li>
          <li>
            <LinkRow href="/automaton" title="Automaton Lab" body="Interactive 9-state HTTP protocol finite state machine." />
          </li>
          <li>
            <LinkRow href="/architecture" title="System Architecture" body="8-stage detection pipeline from ingestion to telemetry." />
          </li>
        </ul>
      </Container>
    </section>
  )
}
