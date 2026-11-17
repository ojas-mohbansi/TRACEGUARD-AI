import { motion } from 'motion/react'
import { ArrowRight, ShieldCheck } from 'lucide-react'

import { ButtonLink } from '../components/Button'
import { Badge } from '../components/Controls'
import { Container } from '../components/Container'
import { DFADiagram } from '../components/DFADiagram'
import { hero } from '../content'
import { cx } from '../lib/cx'

const ease = [0.22, 1, 0.36, 1] as const

export function Hero() {
  return (
    <section aria-labelledby="hero-title" className="relative isolate overflow-hidden">
      {/* Deep security dark glow background */}
      <div className="absolute inset-0 -z-10 bg-[linear-gradient(180deg,#000_0%,#030612_40%,#07122b_75%,#0a1b42_100%)]" aria-hidden />
      <div className="absolute inset-x-0 bottom-0 -z-10 h-px bg-gradient-to-r from-transparent via-signal/50 to-transparent" aria-hidden />

      {/* Subtle radial ambient light */}
      <div className="absolute -top-40 right-1/4 -z-10 size-[500px] rounded-full bg-signal-glow blur-[140px] opacity-40 pointer-events-none" aria-hidden />
      <div className="absolute top-1/2 -left-20 -z-10 size-[400px] rounded-full bg-trace-glow blur-[130px] opacity-30 pointer-events-none" aria-hidden />

      <Container size="xl" className="grid min-h-[min(100svh,940px)] items-center gap-12 pb-16 pt-32 lg:grid-cols-[1.05fr_1.1fr] lg:pb-12 lg:pt-28">
        <div className="flex flex-col items-start gap-7">
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, ease }}>
            <Badge tone="signal" pulse>
              <ShieldCheck className="size-3.5" aria-hidden />
              <span>{hero.eyebrow}</span>
            </Badge>
          </motion.div>

          <motion.h1
            id="hero-title"
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.08, ease }}
            className="display text-balance text-[44px] font-semibold tracking-[-0.035em] sm:text-[60px] lg:text-[72px]"
          >
            {hero.title.map((l, idx) => (
              <span key={l} className={cx('block', idx === 1 ? 'text-transparent bg-clip-text bg-gradient-to-r from-signal-soft via-blue-400 to-trace-soft' : 'text-white')}>
                {l}
              </span>
            ))}
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.16, ease }}
            className="max-w-[540px] text-pretty text-[17px] leading-[1.6] text-soft"
          >
            {hero.body}
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.24, ease }}
            className="flex flex-wrap items-center gap-3.5"
          >
            <ButtonLink href={hero.primary.href} variant="signal" size="lg" className="gap-2">
              <span>{hero.primary.label}</span>
              <ArrowRight className="size-4" aria-hidden />
            </ButtonLink>
            <ButtonLink href={hero.secondary.href} variant="secondary" size="lg">
              {hero.secondary.label}
            </ButtonLink>
          </motion.div>

          <motion.dl
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.4 }}
            className="mt-2 grid w-full max-w-[560px] grid-cols-3 gap-4 border-t border-line pt-6"
          >
            {hero.stats.map((s) => (
              <div key={s.label} className="flex flex-col gap-1">
                <dt className="order-2 text-[12px] leading-snug text-muted">{s.label}</dt>
                <dd className="order-1 text-[28px] font-bold tracking-[-0.03em] text-white sm:text-[34px]">
                  {s.value}
                  {s.unit ? <span className="ml-1 text-[16px] text-soft sm:text-[18px]">{s.unit}</span> : null}
                </dd>
              </div>
            ))}
          </motion.dl>
        </div>

        {/* Hero Visual: Live Animated 9-State DFA Diagram */}
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1.1, delay: 0.15, ease }}
          className="relative mx-auto w-full max-w-[660px]"
        >
          <div className="absolute inset-0 -z-10 rounded-full bg-signal-glow/20 blur-[100px]" aria-hidden />
          <DFADiagram animated={true} />
        </motion.div>
      </Container>
    </section>
  )
}
