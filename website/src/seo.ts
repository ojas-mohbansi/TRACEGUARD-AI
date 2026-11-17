/*
  TraceGuard AI — Technical SEO & Discovery Metadata Engine
  Handles canonical URL resolution, per-route Open Graph, Twitter Cards,
  and validated JSON-LD structured data.
*/

import { brand } from './content'

export interface RouteMeta {
  title: string
  description: string
  canonicalPath: string
  ogType: 'website' | 'article'
  ogImage?: string
  noindex?: boolean
  structuredData?: Record<string, unknown>
}

export function getPublicSiteUrl(): string {
  // Check build-time or runtime environment variables
  const envUrl =
    (typeof process !== 'undefined' && process.env?.PUBLIC_SITE_URL) ||
    (typeof import.meta !== 'undefined' && import.meta.env?.VITE_PUBLIC_SITE_URL) ||
    ''

  if (envUrl && typeof envUrl === 'string' && envUrl.trim() !== '') {
    return envUrl.trim().replace(/\/+$/, '')
  }

  // Browser execution fallback
  if (typeof window !== 'undefined' && window.location?.origin) {
    return window.location.origin
  }

  // Safe fallback for local build / preview
  return 'http://localhost:5303'
}

export const routesMetadata: Record<string, RouteMeta> = {
  '/': {
    title: 'TraceGuard AI — Formal Protocol Verification & Network Intrusion Detection',
    description:
      'TraceGuard AI detects suspicious network behaviour by combining a deterministic 9-state HTTP protocol automaton with Isolation Forest machine-learning anomaly detection.',
    canonicalPath: '/',
    ogType: 'website',
    ogImage: '/brand/traceguard-ai-preview.png',
    structuredData: {
      '@context': 'https://schema.org',
      '@type': 'SoftwareApplication',
      name: 'TraceGuard AI',
      headline: 'Formal Protocol Verification & Network Intrusion Detection',
      applicationCategory: 'SecurityApplication',
      operatingSystem: 'Linux, Windows, macOS, Cloudflare Workers',
      softwareVersion: '1.0.0',
      description:
        'Dual-tiered network intrusion detection system combining an O(1) step deterministic 9-state HTTP protocol automaton with an unsupervised 15-feature Isolation Forest.',
      author: {
        '@type': 'EducationalOrganization',
        name: 'Department of Computer Science & Engineering',
        description: 'Theory of Computation / Formal Languages & Automata Theory Capstone 2026',
      },
      offers: {
        '@type': 'Offer',
        price: '0.00',
        priceCurrency: 'USD',
      },
    },
  },
  '/technology': {
    title: 'Technology — Deterministic DFA & Isolation Forest | TraceGuard AI',
    description:
      'Explore TraceGuard AI dual-tiered architecture: an O(1) step complete HTTP protocol automaton paired with a 15-feature Isolation Forest for volumetric and rate anomalies.',
    canonicalPath: '/technology',
    ogType: 'article',
    ogImage: '/brand/traceguard-ai-preview.png',
    structuredData: {
      '@context': 'https://schema.org',
      '@type': 'TechArticle',
      headline: 'Deterministic Automata Meets Statistical ML: TraceGuard AI Architecture',
      description:
        'Technical specification of the dual-tiered detection engine: 9-state Complete Total DFA protocol verification and 15-feature Isolation Forest anomaly detection.',
      proficiencyLevel: 'Expert',
    },
  },
  '/automaton': {
    title: 'Automaton Lab — 9-State HTTP Protocol DFA | TraceGuard AI',
    description:
      'Interactive formal language lab featuring a Total Complete 9-State, 117-Transition HTTP protocol DFA with live trace execution and O(1) step proofs.',
    canonicalPath: '/automaton',
    ogType: 'website',
    ogImage: '/brand/traceguard-ai-preview.png',
    structuredData: {
      '@context': 'https://schema.org',
      '@type': 'TechArticle',
      headline: 'HTTP Protocol Automaton: M = (Q, Σ, δ, q₀, F)',
      description:
        'Mathematical specification and interactive state machine for 9 states, 13 alphabet symbols, and 117 transition cells including absorbing TRAP sink.',
    },
  },
  '/architecture': {
    title: 'System Architecture — 8-Stage Detection Pipeline | TraceGuard AI',
    description:
      'TraceGuard AI sequential detection pipeline from high-throughput streaming ingestion to state machine verification, ML scoring, and live WebSocket telemetry.',
    canonicalPath: '/architecture',
    ogType: 'article',
    ogImage: '/brand/traceguard-ai-preview.png',
    structuredData: {
      '@context': 'https://schema.org',
      '@type': 'TechArticle',
      headline: '8-Stage Sequential Intrusion Detection Pipeline',
      description:
        'Architecture specification from packet ingestion to session aggregation, DFA verification, feature extraction, Isolation Forest, consensus, and telemetry.',
    },
  },
  '/research': {
    title: 'Research & Benchmarks — Attribution Provenance | TraceGuard AI',
    description:
      'Calibrated corpus benchmark attribution, Chomsky hierarchy formal language placement, synthetic evaluation results, and transparent academic limits.',
    canonicalPath: '/research',
    ogType: 'article',
    ogImage: '/brand/traceguard-ai-preview.png',
    structuredData: {
      '@context': 'https://schema.org',
      '@type': 'TechArticle',
      headline: 'Research Methodology, Corpus Benchmarks & Academic Limitations',
      description:
        'Empirical benchmark results over calibrated corpus, 149/149 test verification, and Chomsky regular language boundaries.',
    },
  },
  '/presentation': {
    title: 'Capstone Defense Deck — Theory of Computation | TraceGuard AI',
    description:
      'Academic presentation slides, structured 13m 30s committee defense protocol, and comprehensive formal documentation for university examination.',
    canonicalPath: '/presentation',
    ogType: 'article',
    ogImage: '/brand/traceguard-ai-preview.png',
    structuredData: {
      '@context': 'https://schema.org',
      '@type': 'CreativeWork',
      headline: 'Theory of Computation Defense Presentation Deck',
      description:
        'Institutional capstone defense deck, 22 slides, 5 presenter speaking protocols, and viva examination documentation.',
    },
  },
  '/about': {
    title: 'Academic Context & Scope — Dept of CSE 2026 | TraceGuard AI',
    description:
      'Capstone research context for Theory of Computation and Formal Languages & Automata Theory at Department of Computer Science & Engineering, 2026.',
    canonicalPath: '/about',
    ogType: 'website',
    ogImage: '/brand/traceguard-ai-preview.png',
    structuredData: {
      '@context': 'https://schema.org',
      '@type': 'Course',
      name: 'Theory of Computation / Formal Languages and Automata Theory',
      description:
        'Academic cybersecurity capstone demonstrating formal automata application to network intrusion detection.',
      provider: {
        '@type': 'Organization',
        name: 'Department of Computer Science & Engineering',
      },
    },
  },
  '/styleguide': {
    title: 'Design System & Style Guide | TraceGuard AI',
    description: 'Internal design system, token scale, and UI component showcase.',
    canonicalPath: '/styleguide',
    ogType: 'website',
    noindex: true,
  },
}

export const fallback404Meta: RouteMeta = {
  title: 'Protocol State: TRAP (404) | TraceGuard AI',
  description: 'The requested route does not exist in the formal navigation automaton. Returned to TRAP sink state.',
  canonicalPath: '/404',
  ogType: 'website',
  noindex: true,
}

export function updateDocumentMetadata(path: string) {
  if (typeof document === 'undefined') return

  const meta = routesMetadata[path] || fallback404Meta
  const baseUrl = getPublicSiteUrl()
  const canonicalUrl = `${baseUrl}${meta.canonicalPath}`
  const ogImageUrl = meta.ogImage ? `${baseUrl}${meta.ogImage}` : `${baseUrl}/brand/traceguard-ai-preview.png`

  // 1. Page Title
  document.title = meta.title

  // Helper to get or create a tag
  const setMeta = (attr: 'name' | 'property', key: string, content: string) => {
    let el = document.querySelector<HTMLMetaElement>(`meta[${attr}="${key}"]`)
    if (!el) {
      el = document.createElement('meta')
      el.setAttribute(attr, key)
      document.head.appendChild(el)
    }
    el.setAttribute('content', content)
  }

  // 2. Primary Meta Tags
  setMeta('name', 'description', meta.description)
  setMeta('name', 'viewport', 'width=device-width, initial-scale=1')
  setMeta('name', 'theme-color', '#060810')

  // 3. Robots (noindex for /styleguide and 404)
  if (meta.noindex) {
    setMeta('name', 'robots', 'noindex, nofollow')
  } else {
    const robotsEl = document.querySelector<HTMLMetaElement>('meta[name="robots"]')
    if (robotsEl) robotsEl.remove()
  }

  // 4. Canonical Link
  let canonicalEl = document.querySelector<HTMLLinkElement>('link[rel="canonical"]')
  if (!canonicalEl) {
    canonicalEl = document.createElement('link')
    canonicalEl.setAttribute('rel', 'canonical')
    document.head.appendChild(canonicalEl)
  }
  canonicalEl.setAttribute('href', canonicalUrl)

  // 5. Open Graph
  setMeta('property', 'og:title', meta.title)
  setMeta('property', 'og:description', meta.description)
  setMeta('property', 'og:url', canonicalUrl)
  setMeta('property', 'og:type', meta.ogType)
  setMeta('property', 'og:site_name', brand.name)
  setMeta('property', 'og:image', ogImageUrl)

  // 6. Twitter / X Cards
  setMeta('name', 'twitter:card', 'summary_large_image')
  setMeta('name', 'twitter:title', meta.title)
  setMeta('name', 'twitter:description', meta.description)
  setMeta('name', 'twitter:image', ogImageUrl)

  // 7. Structured Data (JSON-LD)
  let jsonLdEl = document.querySelector<HTMLScriptElement>('script#structured-data-jsonld')
  if (meta.structuredData) {
    if (!jsonLdEl) {
      jsonLdEl = document.createElement('script')
      jsonLdEl.id = 'structured-data-jsonld'
      jsonLdEl.type = 'application/ld+json'
      document.head.appendChild(jsonLdEl)
    }
    const fullData = {
      ...meta.structuredData,
      url: canonicalUrl,
    }
    jsonLdEl.textContent = JSON.stringify(fullData)
  } else if (jsonLdEl) {
    jsonLdEl.remove()
  }
}
