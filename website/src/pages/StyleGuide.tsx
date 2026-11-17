import { useState } from 'react'
import type { ReactNode } from 'react'

import { Button, ButtonLink } from '../components/Button'
import type { ButtonVariant, ForceState } from '../components/Button'
import { Card, CardText } from '../components/Card'
import type { CardTone } from '../components/Card'
import { Container } from '../components/Container'
import { Badge, Chip, Notice, SaveToggle, Slider } from '../components/Controls'
import { DFADiagram } from '../components/DFADiagram'
import { HybridFormula } from '../components/HybridFormula'
import { Eyebrow } from '../components/Typography'
import { colorGroups, typeScale } from '../lib/tokens'

const states: Array<{ label: string; force?: ForceState; disabled?: boolean; loading?: boolean }> = [
  { label: 'Default' },
  { label: 'Hover', force: 'hover' },
  { label: 'Focus', force: 'focus' },
  { label: 'Pressed', force: 'pressed' },
  { label: 'Disabled', disabled: true },
  { label: 'Loading', loading: true },
]

function Block({ id, title, children, note }: { id: string; title: string; children: ReactNode; note?: string }) {
  return (
    <section id={id} aria-labelledby={`${id}-h`} className="scroll-mt-24 border-t border-line py-14">
      <h2 id={`${id}-h`} className="text-[28px] font-medium tracking-[-0.02em] text-white">
        {title}
      </h2>
      {note ? <p className="mt-2 max-w-[640px] text-[15px] text-muted">{note}</p> : null}
      <div className="mt-8">{children}</div>
    </section>
  )
}

function Label({ children }: { children: ReactNode }) {
  return <p className="mb-2 text-[13px] text-faint font-mono">{children}</p>
}

export function StyleGuide() {
  const [chip, setChip] = useState(true)
  const [saved, setSaved] = useState(false)
  const [slider, setSlider] = useState(60)

  const nav = ['colours', 'type', 'spacing', 'radii', 'shadows', 'buttons', 'badges', 'controls', 'cards', 'automaton-visuals']

  return (
    <div className="pb-24 pt-28 sm:pt-36 bg-black">
      <Container size="xl">
        <Eyebrow>Design System</Eyebrow>
        <h1 className="display mt-3 text-[48px] font-bold text-white sm:text-[64px]">TraceGuard AI Style Guide</h1>
        <p className="mt-4 max-w-[640px] text-[17px] text-soft">
          Live token audit and component specification for the TraceGuard AI interface. Surfaces are deep security dark, lit by Signal Blue (FSM) and Trace Emerald (ML).
        </p>
        <nav aria-label="Style guide sections" className="mt-8 flex flex-wrap gap-2">
          {nav.map((n) => (
            <ButtonLink key={n} href={`#${n}`} variant="secondary" size="sm" className="capitalize">
              {n}
            </ButtonLink>
          ))}
        </nav>

        {/* Colours */}
        <Block id="colours" title="Color System" note="Strict contrast compliance: signal blue (#3B82F6), trace emerald (#10B981), threat red (#ef4444).">
          <div className="flex flex-col gap-8">
            {colorGroups.map((g) => (
              <div key={g.name}>
                <Label>{g.name}</Label>
                <ul className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-6">
                  {g.colors.map((c) => (
                    <li key={c.name} className="flex flex-col gap-2 rounded-card border border-line bg-surface p-3">
                      <span className="h-14 rounded-[12px] border border-line-mid" style={{ background: c.hex }} />
                      <span className="text-[14px] font-medium text-white">{c.name}</span>
                      <span className="font-mono text-[12px] text-muted">{c.hex}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </Block>

        {/* Type scale */}
        <Block id="type" title="Type Scale" note="Inter (primary UI) and JetBrains Mono (automata states, metrics, and proofs).">
          <ul className="flex flex-col gap-6">
            {typeScale.map((t) => (
              <li key={t.name} className="grid gap-2 sm:grid-cols-[200px_1fr] sm:items-baseline border-b border-line pb-4">
                <div>
                  <span className="text-[14px] font-medium text-white">{t.name}</span>
                  <p className="font-mono text-[12px] text-faint">{t.size}</p>
                </div>
                <div className={t.cls}>TraceGuard Protocol Automaton</div>
              </li>
            ))}
          </ul>
        </Block>

        {/* Buttons */}
        <Block id="buttons" title="Buttons & Actions" note="Pill controls with custom focus rings and scale-down active easing.">
          <div className="flex flex-col gap-6">
            {(['signal', 'trace', 'primary', 'secondary', 'ghost'] as ButtonVariant[]).map((v) => (
              <div key={v} className="flex flex-wrap items-center gap-3">
                <span className="w-28 font-mono text-xs text-muted uppercase">{v}:</span>
                {states.map((s) => (
                  <Button key={s.label} variant={v} size="sm" force={s.force} disabled={s.disabled} loading={s.loading}>
                    {s.label}
                  </Button>
                ))}
              </div>
            ))}
          </div>
        </Block>

        {/* Badges */}
        <Block id="badges" title="Badges & Status Chips" note="Live semantic status indicators with squircle rounding.">
          <div className="flex flex-wrap gap-3">
            <Badge tone="signal" pulse>Signal FSM Active</Badge>
            <Badge tone="trace" pulse>Trace ML Anomaly</Badge>
            <Badge tone="threat">Threat Violation</Badge>
            <Badge tone="warn">Rate Warning</Badge>
            <Badge tone="ok">Compliant OK</Badge>
            <Badge tone="neutral">Idle Baseline</Badge>
          </div>
        </Block>

        {/* Controls */}
        <Block id="controls" title="Form & Feedback Controls">
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="flex flex-col gap-4">
              <Notice tone="info" title="Protocol Verification">
                Session sequence is currently undergoing O(1) DFA validation.
              </Notice>
              <Notice tone="success" title="Formal Verification Passed">
                State δ*(IDLE, w) reached CLOSED with zero transition errors.
              </Notice>
              <Notice tone="error" title="Protocol Violation Detected">
                Illegal state transition from REQUEST_RECEIVED → RESPONSE_200 (Auth Bypass).
              </Notice>
            </div>
            <div className="flex flex-col gap-4">
              <Slider label="Calculated Hybrid Risk Index (S_h)" value={slider} min={0} max={100} onChange={setSlider} format={(n) => `${n}`} />
              <div className="flex items-center gap-4">
                <Chip selected={chip} onClick={() => setChip(!chip)}>
                  Filter Anomalies
                </Chip>
                <SaveToggle saved={saved} onToggle={() => setSaved(!saved)} label="Session Trace" />
              </div>
            </div>
          </div>
        </Block>

        {/* Cards */}
        <Block id="cards" title="Surface Cards" note="Tailored dark tones: plain, signal, trace, threat, grid.">
          <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            {(['plain', 'signal', 'trace', 'threat', 'grid'] as CardTone[]).map((t) => (
              <li key={t}>
                <Card tone={t} className="h-[200px]">
                  <CardText title={t.toUpperCase()} body="Lit squircle card surface." />
                </Card>
              </li>
            ))}
          </ul>
        </Block>

        {/* Automaton Visuals */}
        <Block id="automaton-visuals" title="Automaton & Pipeline Components">
          <div className="grid gap-8 lg:grid-cols-2">
            <div>
              <Label>DFA State Machine Diagram</Label>
              <DFADiagram animated={true} />
            </div>
            <div>
              <Label>Hybrid Consensus Formula Display</Label>
              <HybridFormula />
            </div>
          </div>
        </Block>
      </Container>
    </div>
  )
}
