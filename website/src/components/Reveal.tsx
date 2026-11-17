import { motion } from 'motion/react'
import type { ReactNode } from 'react'
import { useReducedMotion } from '../lib/useReducedMotion'

// Fade-and-rise on scroll. Wrap any block; stagger siblings with `delay`.
// Use `as="li"` inside lists so the markup stays valid.
export function Reveal({
  children,
  delay = 0,
  className,
  y = 18,
  as = 'div',
}: {
  children: ReactNode
  delay?: number
  className?: string
  y?: number
  as?: 'div' | 'li'
}) {
  const reduce = useReducedMotion()
  const Tag = as === 'li' ? motion.li : motion.div

  if (reduce) {
    const RawTag = as === 'li' ? 'li' : 'div'
    return <RawTag className={className}>{children}</RawTag>
  }

  return (
    <Tag
      className={className}
      initial={{ opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.05 }}
      transition={{ duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </Tag>
  )
}
