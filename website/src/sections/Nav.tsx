import { Menu } from 'lucide-react'
import { useEffect, useState } from 'react'

import { ButtonLink, IconButton } from '../components/Button'
import { Logo } from '../components/Logo'
import { Sheet } from '../components/Sheet'
import { brand, cta, nav } from '../content'
import { cx } from '../lib/cx'
import { isCurrent, Link, useLocation } from '../lib/router'

function GithubIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
      <path d="M9 18c-4.51 2-5-2-7-2" />
    </svg>
  )
}

export function Nav() {
  const { path } = useLocation()
  const [open, setOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const on = () => setScrolled(window.scrollY > 8)
    on()
    window.addEventListener('scroll', on, { passive: true })
    return () => window.removeEventListener('scroll', on)
  }, [])

  // Close the menu on navigation.
  useEffect(() => setOpen(false), [path])

  return (
    <header
      className={cx(
        'fixed inset-x-0 top-0 z-50 transition-[background-color,backdrop-filter,border-color] duration-200 border-b',
        scrolled
          ? 'bg-[#060810]/90 border-line-mid backdrop-blur-md shadow-[0_1px_3px_rgba(0,0,0,0.5)]'
          : 'bg-[#060810]/75 border-line backdrop-blur-md',
      )}
    >
      <div className="mx-auto flex h-16 max-w-[1320px] items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <Link
          href="/"
          aria-label="TraceGuard AI home"
          className="inline-flex items-center rounded-[8px] p-1.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-signal"
        >
          <Logo />
        </Link>
        <nav aria-label="Main Navigation" className="hidden lg:block">
          <ul className="flex items-center gap-1 font-mono text-[13px]">
            {nav.map((n) => {
              const current = isCurrent(n.href, path)
              return (
                <li key={n.href}>
                  <Link
                    href={n.href}
                    aria-current={current ? 'page' : undefined}
                    className={cx(
                      'inline-flex h-9 items-center rounded-[8px] px-3.5 font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-signal',
                      current
                        ? 'bg-signal-wash text-signal-soft border border-signal-border/50'
                        : 'text-muted hover:text-white hover:bg-white/[0.04]',
                    )}
                  >
                    {n.label}
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>
        <div className="flex items-center gap-2.5">
          <a
            href={brand.github}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex h-9 items-center gap-2 rounded-[8px] border border-line bg-surface-2 px-3 text-xs font-mono font-medium text-soft hover:border-signal-border hover:bg-signal-wash hover:text-white transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-signal"
            aria-label="TraceGuard AI GitHub Repository (opens in new tab)"
          >
            <GithubIcon className="size-4 shrink-0" />
            <span className="hidden sm:inline">GitHub</span>
          </a>
          <div className="hidden sm:inline-flex">
            <ButtonLink href={cta.href} variant="signal" size="sm">
              {cta.label}
            </ButtonLink>
          </div>
          <IconButton
            onClick={() => setOpen(true)}
            aria-label="Open navigation menu"
            aria-expanded={open}
            className="lg:hidden"
          >
            <Menu className="size-5" aria-hidden="true" />
          </IconButton>
        </div>
      </div>
      <Sheet open={open} onClose={() => setOpen(false)} title="Navigation Menu">
        <nav aria-label="Mobile Navigation" className="mt-4 flex flex-1 flex-col">
          <ul className="flex flex-col gap-1 font-mono">
            {[{ label: 'Home', href: '/' }, ...nav].map((n) => {
              const current = isCurrent(n.href, path)
              return (
                <li key={n.href}>
                  <Link
                    href={n.href}
                    aria-current={current ? 'page' : undefined}
                    className={cx(
                      'flex h-12 items-center rounded-[12px] px-4 text-base font-medium tracking-tight focus:outline-none focus-visible:ring-2 focus-visible:ring-signal',
                      current
                        ? 'bg-signal-wash text-signal-soft border border-signal-border/50'
                        : 'text-soft hover:bg-white/[0.05]',
                    )}
                  >
                    {n.label}
                  </Link>
                </li>
              )
            })}
          </ul>
          <div className="mt-auto pt-6 flex flex-col gap-3">
            <a
              href={brand.github}
              target="_blank"
              rel="noopener noreferrer"
              className="flex h-11 items-center justify-center gap-2.5 rounded-[12px] border border-line bg-surface-2 px-4 font-mono text-sm font-medium text-soft hover:text-white hover:border-signal-border transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-signal"
              aria-label="TraceGuard AI GitHub Repository (opens in new tab)"
            >
              <GithubIcon className="size-4 shrink-0 text-signal-soft" />
              <span>GitHub Repository</span>
            </a>
            <ButtonLink href={cta.href} variant="signal" size="lg" className="w-full">
              {cta.label}
            </ButtonLink>
          </div>
        </nav>
      </Sheet>
    </header>
  )
}

