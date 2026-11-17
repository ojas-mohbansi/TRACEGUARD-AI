import { ArrowRight, Menu } from 'lucide-react'
import { useEffect, useState } from 'react'

import { IconButton } from '../components/Button'
import { Logo } from '../components/Logo'
import { Sheet } from '../components/Sheet'
import { brand, cta, nav } from '../content'
import { cx } from '../lib/cx'
import { isCurrent, Link, useLocation } from '../lib/router'

function GithubIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" className={className} aria-hidden>
      <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
    </svg>
  )
}

export function Nav() {
  const { path } = useLocation()
  const [open, setOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const on = () => setScrolled(window.scrollY > 12)
    on()
    window.addEventListener('scroll', on, { passive: true })
    return () => window.removeEventListener('scroll', on)
  }, [])

  // Close the menu on navigation.
  useEffect(() => setOpen(false), [path])

  return (
    <header
      className={cx(
        'fixed inset-x-0 top-0 z-50 transition-[background-color,backdrop-filter,border-color,box-shadow] duration-200',
        scrolled
          ? 'bg-[#07090E]/95 border-b border-white/[0.12] shadow-sm backdrop-blur-xl'
          : 'bg-[#0E131F]/90 border-b border-white/[0.08] backdrop-blur-md',
      )}
    >
      <div className="mx-auto flex h-16 max-w-[1320px] items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        {/* Brand: Icon + Official Wordmark SVG */}
        <Link
          href="/"
          aria-label="TraceGuard AI home"
          className="-m-2 inline-flex items-center rounded-lg p-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
        >
          <Logo size={28} showBadge={true} />
        </Link>

        {/* Desktop Navigation Links */}
        <nav aria-label="Main" className="hidden lg:flex items-center gap-1.5">
          <ul className="flex items-center gap-1">
            {nav.map((n) => {
              const current = isCurrent(n.href, path)
              return (
                <li key={n.href}>
                  <Link
                    href={n.href}
                    aria-current={current ? 'page' : undefined}
                    className={cx(
                      'inline-flex h-8 items-center rounded-md px-3 text-xs font-mono font-medium transition-all duration-150',
                      current
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 shadow-xs font-semibold'
                        : 'text-slate-300 hover:text-white hover:bg-white/[0.05] border border-transparent',
                    )}
                  >
                    {n.label}
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>

        {/* Right Action Cluster */}
        <div className="flex items-center gap-2.5">
          {/* GitHub Repository Link */}
          <a
            href={brand.github}
            target="_blank"
            rel="noreferrer"
            className="hidden sm:inline-flex items-center gap-2 h-8 px-3 rounded-md text-xs font-mono font-medium text-slate-300 hover:text-white bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.1] transition-colors"
            aria-label="GitHub Repository (opens in new tab)"
          >
            <GithubIcon className="size-3.5 text-slate-400" />
            <span className="hidden md:inline">GitHub</span>
          </a>

          {/* Primary CTA (SaaS Theme Emerald Action) */}
          <Link
            href={cta.href}
            className="hidden sm:inline-flex items-center gap-1.5 h-8 px-3.5 rounded-md bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-xs transition-all shadow-xs active:scale-95"
          >
            <span>{cta.label}</span>
            <ArrowRight className="size-3 text-slate-950" />
          </Link>

          {/* Mobile Drawer Toggle */}
          <IconButton
            onClick={() => setOpen(true)}
            aria-label="Open menu"
            aria-expanded={open}
            className="lg:hidden h-8 w-8 rounded-md border border-white/[0.1] bg-white/[0.03] text-slate-300 hover:text-white hover:bg-white/[0.08]"
          >
            <Menu className="size-4" aria-hidden />
          </IconButton>
        </div>
      </div>

      {/* Mobile Drawer */}
      <Sheet open={open} onClose={() => setOpen(false)} title="Menu">
        <nav aria-label="Mobile" className="mt-4 flex flex-1 flex-col">
          <ul className="flex flex-col gap-1.5">
            {[{ label: 'Home', href: '/' }, ...nav].map((n) => {
              const current = isCurrent(n.href, path)
              return (
                <li key={n.href}>
                  <Link
                    href={n.href}
                    aria-current={current ? 'page' : undefined}
                    className={cx(
                      'flex h-12 items-center rounded-lg px-4 text-[15px] font-mono font-medium tracking-tight transition-colors',
                      current
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 font-semibold'
                        : 'text-slate-300 hover:bg-white/[0.05] hover:text-white',
                    )}
                  >
                    {n.label}
                  </Link>
                </li>
              )
            })}
          </ul>

          <div className="mt-auto space-y-2.5 pt-6">
            <a
              href={brand.github}
              target="_blank"
              rel="noreferrer"
              className="flex h-11 w-full items-center justify-center gap-2 rounded-lg border border-white/[0.12] bg-white/[0.05] px-4 text-xs font-mono font-medium text-slate-200 hover:bg-white/[0.08] hover:text-white transition-colors"
            >
              <GithubIcon className="size-4 text-slate-300" />
              <span>GitHub Repository</span>
            </a>
            <Link
              href={cta.href}
              className="flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 px-4 text-xs font-semibold text-slate-950 transition-all shadow-xs"
            >
              <span>{cta.label}</span>
              <ArrowRight className="size-3.5 text-slate-950" />
            </Link>
          </div>
        </nav>
      </Sheet>
    </header>
  )
}
