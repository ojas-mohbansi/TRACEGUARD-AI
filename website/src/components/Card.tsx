import type { ReactNode } from 'react'
import { cx } from '../lib/cx'

/*
  Surfaces. Every card is a lit squircle; `tone` picks its light:
  - plain: deep security dark surface
  - signal: protocol / FSM blue glow
  - trace: ML / anomaly emerald glow
  - threat: violation / alert red glow
  - grid: subtle cyber matrix pattern with signal accent
*/
export type CardTone = 'plain' | 'signal' | 'trace' | 'threat' | 'grid' | 'fire' | 'ocean' | 'stripes' | 'steel'

const tones: Record<CardTone, string> = {
  plain: 'bg-surface border border-line',
  signal: 'bg-[radial-gradient(120%_90%_at_50%_100%,#1d4ed8_0%,#0d1e3d_45%,#0a0d16_100%)] border border-signal-border',
  trace: 'bg-[radial-gradient(120%_90%_at_50%_100%,#047857_0%,#062c1d_45%,#0a0d16_100%)] border border-trace-border',
  threat: 'bg-[radial-gradient(120%_90%_at_50%_100%,#991b1b_0%,#330c0c_45%,#0a0d16_100%)] border border-threat-border',
  grid: 'bg-surface-2 border border-line-mid',
  // Backward compatibility aliases
  ocean: 'bg-[radial-gradient(120%_90%_at_50%_100%,#1d4ed8_0%,#0d1e3d_45%,#0a0d16_100%)] border border-signal-border',
  fire: 'bg-[radial-gradient(120%_90%_at_50%_100%,#991b1b_0%,#330c0c_45%,#0a0d16_100%)] border border-threat-border',
  stripes: 'bg-surface-2 border border-signal-border',
  steel: 'bg-surface-2 border border-line',
}

export function Card({
  tone = 'plain',
  children,
  className,
  as: As = 'div',
  interactive = false,
  id,
}: {
  id?: string
  tone?: CardTone
  children: ReactNode
  className?: string
  as?: 'div' | 'article' | 'li' | 'section'
  interactive?: boolean
}) {
  return (
    <As
      id={id}
      className={cx(
        'depth relative isolate overflow-hidden rounded-card',
        tones[tone],
        interactive && 'transition-transform duration-300 ease-out hover:-translate-y-1',
        className,
      )}
    >
      {children}
    </As>
  )
}

/** The text block that sits at the top of a feature card. */
export function CardText({ title, body, className }: { title: ReactNode; body: ReactNode; className?: string }) {
  return (
    <div className={cx('relative z-10 flex flex-col gap-1 p-5 sm:p-6', className)}>
      <h3 className="text-[16px] font-medium text-white">{title}</h3>
      <p className="text-pretty text-[16px] leading-[1.42] text-soft">{body}</p>
    </div>
  )
}
