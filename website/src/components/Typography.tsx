import type { ReactNode } from 'react'

import { cx } from '../lib/cx'

/** Small label above a heading. Sentence case, never all caps. */
export function Eyebrow({ children, className, tone = 'plasma' }: { children: ReactNode; className?: string; tone?: 'plasma' | 'fire' | 'muted' }) {
  return (
    <p
      className={cx(
        'text-[14px] font-medium tracking-[-0.005em]',
        tone === 'plasma' ? 'text-plasma-text' : tone === 'fire' ? 'text-fire-3' : 'text-muted',
        className,
      )}
    >
      {children}
    </p>
  )
}

/** A centred or left-aligned section title, optionally over two lines. */
export function SectionHeading({
  title,
  eyebrow,
  body,
  align = 'center',
  size = 'lg',
  as: As = 'h2',
  className,
  id,
}: {
  title: string | string[]
  eyebrow?: ReactNode
  body?: ReactNode
  align?: 'center' | 'left'
  size?: 'md' | 'lg' | 'xl'
  as?: 'h1' | 'h2' | 'h3'
  className?: string
  id?: string
}) {
  const lines = Array.isArray(title) ? title : [title]
  const sizeClass =
    size === 'xl' ? 'text-[44px] sm:text-[60px] lg:text-[72px]' : size === 'lg' ? 'text-[36px] sm:text-[48px] lg:text-[56px]' : 'text-[28px] sm:text-[34px] lg:text-[40px]'
  return (
    <div className={cx('flex flex-col gap-4', align === 'center' ? 'items-center text-center' : 'items-start', className)}>
      {eyebrow ? <Eyebrow>{eyebrow}</Eyebrow> : null}
      <As id={id} className={cx('display text-balance', sizeClass)}>
        {lines.map((l, i) => (
          <span key={i} className="block">
            {l}
          </span>
        ))}
      </As>
      {body ? <p className={cx('max-w-[600px] text-pretty text-[17px] leading-[1.55] text-muted', align === 'center' && 'mx-auto')}>{body}</p> : null}
    </div>
  )
}
