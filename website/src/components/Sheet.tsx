import { AnimatePresence, motion } from 'motion/react'
import { X } from 'lucide-react'
import { useEffect, useId, useRef } from 'react'
import { createPortal } from 'react-dom'
import type { ReactNode } from 'react'

import { cx } from '../lib/cx'
import { IconButton } from './Button'

const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'

/*
  A modal side sheet (the mobile nav). Traps Tab inside, closes on Esc or a
  backdrop click, locks page scroll, and hands focus back to whatever opened
  it. Slides in from `side`.
*/
export function Sheet({
  open,
  onClose,
  title,
  children,
  side = 'right',
  className,
}: {
  open: boolean
  onClose: () => void
  title: string
  children: ReactNode
  side?: 'right' | 'left'
  className?: string
}) {
  const panel = useRef<HTMLDivElement>(null)
  const titleId = useId()
  const close = useRef(onClose)
  close.current = onClose

  useEffect(() => {
    if (!open) return
    const opener = document.activeElement as HTMLElement | null
    const prevOverflow = document.documentElement.style.overflow
    document.documentElement.style.overflow = 'hidden'
    const focusFirst = requestAnimationFrame(() => {
      panel.current?.querySelector<HTMLElement>(FOCUSABLE)?.focus()
    })
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault()
        close.current()
        return
      }
      if (e.key !== 'Tab' || !panel.current) return
      const items = Array.from(panel.current.querySelectorAll<HTMLElement>(FOCUSABLE)).filter((el) => el.offsetParent !== null)
      if (!items.length) return
      const first = items[0]
      const last = items[items.length - 1]
      if (e.shiftKey && (document.activeElement === first || !panel.current.contains(document.activeElement))) {
        e.preventDefault()
        last.focus()
      } else if (!e.shiftKey && (document.activeElement === last || !panel.current.contains(document.activeElement))) {
        e.preventDefault()
        first.focus()
      }
    }
    document.addEventListener('keydown', onKey)
    return () => {
      cancelAnimationFrame(focusFirst)
      document.removeEventListener('keydown', onKey)
      document.documentElement.style.overflow = prevOverflow
      opener?.focus?.()
    }
  }, [open])

  if (typeof document === 'undefined') return null

  return createPortal(
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-[100]">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="absolute inset-0 bg-black/75 backdrop-blur-sm"
            onClick={onClose}
            aria-hidden
          />
          <motion.div
            ref={panel}
            role="dialog"
            aria-modal="true"
            aria-labelledby={titleId}
            initial={{ x: side === 'right' ? '100%' : '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: side === 'right' ? '100%' : '-100%' }}
            transition={{ type: 'spring', stiffness: 380, damping: 38 }}
            className={cx(
              'depth absolute inset-y-0 flex w-[min(340px,85vw)] flex-col overflow-y-auto bg-surface-2 p-5 border-l border-line shadow-2xl',
              side === 'right' ? 'right-0' : 'left-0',
              className,
            )}
          >
            <div className="flex items-center justify-between pb-3 border-b border-line">
              <h2 id={titleId} className="text-[13px] font-mono uppercase tracking-wider text-muted">
                {title}
              </h2>
              <IconButton onClick={onClose} aria-label="Close menu">
                <X className="size-5" aria-hidden />
              </IconButton>
            </div>
            {children}
          </motion.div>
        </div>
      )}
    </AnimatePresence>,
    document.body
  )
}
