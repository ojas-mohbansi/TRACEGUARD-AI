import { motion } from 'motion/react'
import type { ReactNode } from 'react'

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
  const Tag = as === 'li' ? motion.li : motion.div
  return (
    <Tag
      className={className}
      initial={{ opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '0px 0px -8% 0px' }}
      transition={{ duration: 0.8, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </Tag>
  )
}
