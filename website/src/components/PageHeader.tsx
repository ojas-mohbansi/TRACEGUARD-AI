import type { ReactNode } from 'react'

import { cx } from '../lib/cx'
import { Container } from './Container'
import { Reveal } from './Reveal'
import { Eyebrow } from './Typography'

/*
  The top of every inner page: black sky lifting to blue, an eyebrow, a big
  title and a lede. `aside` renders on the right at desktop widths.
*/
export function PageHeader({
  eyebrow,
  title,
  body,
  aside,
  children,
  tone = 'ocean',
}: {
  eyebrow: string
  title: string
  body?: ReactNode
  aside?: ReactNode
  children?: ReactNode
  tone?: 'ocean' | 'fire' | 'plain'
}) {
  return (
    <section aria-labelledby="page-title" className="relative isolate overflow-hidden pb-16 pt-32 sm:pb-24 sm:pt-40">
      <div
        className={cx(
          'absolute inset-0 -z-10 [mask-image:linear-gradient(to_bottom,#000_70%,transparent)]',
          tone === 'ocean' && 'bg-[linear-gradient(180deg,#000_0%,#000_35%,#081536_80%,#142a5e_100%)]',
          tone === 'fire' && 'bg-[radial-gradient(70%_80%_at_50%_120%,#7a2606_0%,#2a0b02_45%,#000_75%)]',
          tone === 'plain' && 'bg-black',
        )}
        aria-hidden
      />
      <Container size="xl" className={cx('grid items-center gap-12', aside ? 'lg:grid-cols-[1.1fr_1fr]' : null)}>
        <Reveal className="flex flex-col items-start gap-5">
          <Eyebrow tone={tone === 'fire' ? 'fire' : 'plasma'}>{eyebrow}</Eyebrow>
          <h1 id="page-title" className="display max-w-[820px] text-balance text-[44px] sm:text-[60px] lg:text-[68px]">
            {title}
          </h1>
          {body ? <p className="max-w-[580px] text-pretty text-[18px] leading-[1.55] text-muted">{body}</p> : null}
          {children}
        </Reveal>
        {aside ? (
          <Reveal delay={0.1} className="relative">
            {aside}
          </Reveal>
        ) : null}
      </Container>
    </section>
  )
}
