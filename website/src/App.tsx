import { lazy, Suspense, useEffect, useRef } from 'react'
import type { ComponentType, ReactNode } from 'react'

import { brand } from './content'
import { match, scrollToHash, useLocation } from './lib/router'
import { updateDocumentMetadata } from './seo'
import { Home } from './pages/Home'
import { NotFound } from './pages/NotFound'
import { Footer } from './sections/Footer'
import { Nav } from './sections/Nav'

// Inner pages load on demand so the landing page ships alone.
const page = <K extends string>(load: () => Promise<Record<K, ComponentType<{ slug?: string }>>>, name: K) =>
  lazy(() => load().then((m) => ({ default: m[name] })))

const Technology = page(() => import('./pages/Technology'), 'Technology')
const Automaton = page(() => import('./pages/Automaton'), 'Automaton')
const Architecture = page(() => import('./pages/Architecture'), 'Architecture')
const Research = page(() => import('./pages/Research'), 'Research')
const Presentation = page(() => import('./pages/Presentation'), 'Presentation')
const About = page(() => import('./pages/About'), 'About')
const StyleGuide = page(() => import('./pages/StyleGuide'), 'StyleGuide')

/*
  The route table. Add a page by adding a line here and a link in `nav` (src/content.ts).
*/
type Params = Record<string, string>
type Route = { path: string; title: string | ((p: Params) => string | null); render: (p: Params) => ReactNode }

const routes: Route[] = [
  { path: '/', title: `${brand.name} — Formal Protocol Verification & Network Intrusion Detection`, render: () => <Home /> },
  { path: '/technology', title: 'Technology — FSM & Isolation Forest', render: () => <Technology /> },
  { path: '/automaton', title: 'Automaton Lab — 9-State HTTP DFA', render: () => <Automaton /> },
  { path: '/architecture', title: 'Architecture — 8-Stage Detection Pipeline', render: () => <Architecture /> },
  { path: '/research', title: 'Research & Evaluation Benchmarks', render: () => <Research /> },
  { path: '/presentation', title: 'Defense Deck — Theory of Computation Capstone', render: () => <Presentation /> },
  { path: '/about', title: 'Academic Context — Dept of CSE 2026', render: () => <About /> },
  { path: '/styleguide', title: 'Design System & Style Guide', render: () => <StyleGuide /> },
]

function resolve(path: string) {
  for (const r of routes) {
    const params = match(r.path, path)
    if (!params) continue
    const title = typeof r.title === 'function' ? r.title(params) : r.title
    if (title === null) return null
    return { route: r, params, title }
  }
  return null
}

export function App() {
  const { path, hash } = useLocation()
  const hit = resolve(path)
  const main = useRef<HTMLElement>(null)
  const first = useRef(true)

  useEffect(() => {
    updateDocumentMetadata(path)
  }, [path])

  // On navigation: jump to the hash target or the top, and move focus to <main>.
  useEffect(() => {
    let raf = 0
    let tries = 0
    const run = () => {
      const target = hash ? document.getElementById(decodeURIComponent(hash.slice(1))) : null
      if (hash && !target && tries++ < 120) {
        raf = requestAnimationFrame(run)
        return
      }
      const isFirst = first.current
      first.current = false
      scrollToHash(hash, !isFirst)
      if (!isFirst && !hash) main.current?.focus({ preventScroll: true })
    }
    raf = requestAnimationFrame(run)
    return () => cancelAnimationFrame(raf)
  }, [path, hash])

  return (
    <>
      <a
        href="#main"
        className="sr-only rounded-control bg-white px-5 py-2.5 text-[14px] font-medium text-black focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[70]"
      >
        Skip to content
      </a>
      <Nav />
      <main id="main" ref={main} tabIndex={-1} className="outline-none">
        <Suspense fallback={<div className="min-h-screen bg-black" />}>
          {hit ? hit.route.render(hit.params) : <NotFound />}
        </Suspense>
      </main>
      <Footer />
    </>
  )
}
