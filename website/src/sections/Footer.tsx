import { Shield } from 'lucide-react'
import { Container } from '../components/Container'
import { Logo } from '../components/Logo'
import { brand, footer } from '../content'
import { Link } from '../lib/router'

function GithubIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" className={className} aria-hidden>
      <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
    </svg>
  )
}

export function Footer() {
  return (
    <footer className="border-t border-line bg-black pb-12 pt-16">
      <Container size="xl">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
          {/* Column 1: Brand & Academic Overview */}
          <div className="flex flex-col gap-4">
            <Link href="/" aria-label="TraceGuard AI home" className="-m-2 self-start rounded-[12px] p-2">
              <Logo />
            </Link>
            <p className="max-w-[280px] text-[14px] leading-relaxed text-muted">{footer.blurb}</p>
            <div className="flex flex-col gap-1 text-[13px] text-faint">
              <span className="font-medium text-soft">{brand.department}</span>
              <span>{brand.course}</span>
              <span>Academic Year {brand.academicYear}</span>
            </div>
            <div>
              <a
                href={brand.github}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 rounded-control border border-line bg-surface px-3 py-1.5 text-xs text-soft transition-colors hover:border-signal-border hover:text-white"
              >
                <GithubIcon className="size-3.5" />
                <span>GitHub Repository</span>
              </a>
            </div>
          </div>

          {/* Navigation Columns */}
          {footer.columns.map((c) => (
            <nav key={c.title} aria-label={c.title}>
              <h2 className="text-[13px] font-mono font-semibold uppercase tracking-wider text-white">{c.title}</h2>
              <ul className="mt-4 flex flex-col gap-1">
                {c.links.map((l) => (
                  <li key={l.href}>
                    {l.href.startsWith('http') ? (
                      <a
                        href={l.href}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex min-h-8 items-center text-[14px] text-muted transition-colors hover:text-white"
                      >
                        {l.label}
                      </a>
                    ) : (
                      <Link
                        href={l.href}
                        className="inline-flex min-h-8 items-center text-[14px] text-muted transition-colors hover:text-white"
                      >
                        {l.label}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </nav>
          ))}
        </div>

        {/* Disclaimer Callout */}
        <div className="mt-12 flex items-center gap-3 rounded-[16px] border border-line bg-surface p-4 text-xs text-muted">
          <Shield className="size-4 shrink-0 text-signal-soft" aria-hidden />
          <p>{footer.disclaimer}</p>
        </div>

        {/* Legal & Copyright */}
        <div className="mt-8 border-t border-line pt-6 text-[12px] text-faint">
          <p>{footer.copyright}</p>
        </div>
      </Container>
    </footer>
  )
}
