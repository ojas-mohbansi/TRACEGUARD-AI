import React from 'react';
import { Link } from 'react-router-dom';
import {
  Activity,
  Layers,
  Zap,
  CheckCircle2,
  ArrowRight,
  Cpu,
  Binary,
  Sparkles,
  ShieldAlert,
  Server,
  Lock,
  ExternalLink
} from 'lucide-react';

export default function Landing() {
  return (
    <div className="min-h-screen bg-[var(--tg-bg-root)] text-[var(--tg-text-primary)] flex flex-col font-sans selection:bg-emerald-500/30 selection:text-white">
      {/* Top Navigation */}
      <header className="border-b border-[var(--tg-border-subtle)] bg-[var(--tg-bg-base)]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3 group">
            <img
              src="/traceguard-ai-icon-color.svg"
              alt="TraceGuard AI Logo"
              className="w-8 h-8 rounded-lg shadow-sm"
            />
            <div className="flex items-center gap-2">
              <span className="text-base font-semibold tracking-tight text-[var(--tg-text-primary)]">
                TraceGuard<span className="text-[var(--tg-accent-emerald)] font-bold"> AI</span>
              </span>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-[var(--tg-bg-surface)] text-[var(--tg-accent-emerald)] border border-emerald-500/20 font-medium">
                Production NIDS
              </span>
            </div>
          </Link>

          <nav className="hidden md:flex items-center space-x-8 text-xs font-mono text-[var(--tg-text-secondary)]">
            <a href="#engines" className="hover:text-[var(--tg-accent-emerald)] transition-colors">Engines</a>
            <a href="#specifications" className="hover:text-[var(--tg-accent-emerald)] transition-colors">Formal Model</a>
            <a href="#tiers" className="hover:text-[var(--tg-accent-emerald)] transition-colors">Workspace Tiers</a>
          </nav>

          <div className="flex items-center space-x-3">
            <Link
              to="/login"
              className="tg-btn-secondary text-xs"
            >
              Sign In
            </Link>
            <Link
              to="/"
              className="tg-btn-primary text-xs flex items-center gap-1.5"
            >
              <span>Launch Console</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-20 pb-20 px-6 overflow-hidden">
        {/* Subtle background radial glow in emerald */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_-10%,rgba(16,185,129,0.08),rgba(14,19,31,0))]" />

        <div className="max-w-4xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-[var(--tg-accent-emerald)] text-xs font-mono mb-8 font-semibold">
            <Binary className="w-3.5 h-3.5" />
            <span>Deterministic State-Machine & ML Hybrid Telemetry</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-bold tracking-tight text-[var(--tg-text-primary)] mb-6 leading-tight">
            Network protocol verification. <br />
            <span className="text-[var(--tg-accent-emerald)]">
              Mathematically audited against formal automata.
            </span>
          </h1>

          <p className="text-base sm:text-lg text-[var(--tg-text-secondary)] max-w-2xl mx-auto mb-10 leading-relaxed font-normal">
            TraceGuard AI unifies formal Finite-State Machine verification with Isolation Forest anomaly detection to catch zero-day sequences, state violations, and stealth exploits with deterministic explainability.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              to="/"
              className="w-full sm:w-auto px-6 py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-xs shadow-md transition-all text-center flex items-center justify-center gap-2"
            >
              <span>Launch Live Platform</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/signup"
              className="w-full sm:w-auto px-6 py-2.5 rounded-lg border border-[var(--tg-border-default)] hover:border-[var(--tg-border-strong)] bg-[var(--tg-bg-surface)] hover:bg-[var(--tg-bg-elevated)] text-[var(--tg-text-primary)] font-medium text-xs transition-all text-center"
            >
              Register SOC Workspace
            </Link>
          </div>

          {/* Metric Highlights Strip */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-16 pt-12 border-t border-[var(--tg-border-subtle)] text-left">
            <div className="tg-panel p-4">
              <div className="text-2xl font-bold font-mono text-[var(--tg-accent-emerald)]">3 Engines</div>
              <div className="text-xs text-[var(--tg-text-muted)] mt-1 font-mono">FSM, ML, & Hybrid Consensus</div>
            </div>
            <div className="tg-panel p-4">
              <div className="text-2xl font-bold font-mono text-[var(--tg-accent-blue)]">&lt; 0.05 ms</div>
              <div className="text-xs text-[var(--tg-text-muted)] mt-1 font-mono">Mean Inspection Latency</div>
            </div>
            <div className="tg-panel p-4">
              <div className="text-2xl font-bold font-mono text-[var(--tg-text-primary)]">100%</div>
              <div className="text-xs text-[var(--tg-text-muted)] mt-1 font-mono">Explainable State Violations</div>
            </div>
            <div className="tg-panel p-4">
              <div className="text-2xl font-bold font-mono text-[var(--tg-status-warning)]">60% Floor</div>
              <div className="text-xs text-[var(--tg-text-muted)] mt-1 font-mono">DFA Violation Risk Floor</div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Engines Section */}
      <section id="engines" className="py-20 px-6 border-t border-[var(--tg-border-subtle)] bg-[var(--tg-bg-base)]">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-14">
            <div className="text-xs font-mono text-[var(--tg-accent-emerald)] font-semibold uppercase tracking-wider mb-2">Detection Disciplines</div>
            <h2 className="text-2xl sm:text-3xl font-bold text-[var(--tg-text-primary)] mb-3">
              Three Complementary Inspection Engines
            </h2>
            <p className="text-xs sm:text-sm text-[var(--tg-text-muted)] max-w-xl mx-auto">
              Conventional NIDS miss out-of-order transitions, while statistical models produce opaque false positives. TraceGuard fuses both with mathematical rigor.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {/* FSM */}
            <div className="tg-panel p-6 flex flex-col justify-between hover:border-emerald-500/40 transition">
              <div>
                <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-[var(--tg-accent-emerald)] flex items-center justify-center mb-5">
                  <Binary className="w-5 h-5" />
                </div>
                <h3 className="text-base font-semibold text-[var(--tg-text-primary)] mb-2">Deterministic FSM</h3>
                <p className="text-xs text-[var(--tg-text-secondary)] leading-relaxed mb-4">
                  Models the complete 9-state HTTP DFA across 117 transitions (15 valid protocol paths, absorbing TRAP sink) with mathematical certainty.
                </p>
              </div>
              <ul className="text-xs text-[var(--tg-text-muted)] space-y-2 pt-4 border-t border-[var(--tg-border-subtle)] font-mono">
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)] shrink-0" /> Exact transition provenance</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)] shrink-0" /> Zero false positive guarantee on syntax</li>
              </ul>
            </div>

            {/* ML */}
            <div className="tg-panel p-6 flex flex-col justify-between hover:border-blue-500/40 transition">
              <div>
                <div className="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 text-[var(--tg-accent-blue)] flex items-center justify-center mb-5">
                  <Cpu className="w-5 h-5" />
                </div>
                <h3 className="text-base font-semibold text-[var(--tg-text-primary)] mb-2">Isolation Forest ML</h3>
                <p className="text-xs text-[var(--tg-text-secondary)] leading-relaxed mb-4">
                  Extracts 15 behavioral features across session duration, payload skew, byte ratios, and response timing to capture novel anomaly structures without manual signatures.
                </p>
              </div>
              <ul className="text-xs text-[var(--tg-text-muted)] space-y-2 pt-4 border-t border-[var(--tg-border-subtle)] font-mono">
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-blue)] shrink-0" /> Unsupervised behavioral clustering</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-blue)] shrink-0" /> Sub-millisecond vector scoring</li>
              </ul>
            </div>

            {/* Hybrid */}
            <div className="tg-panel p-6 flex flex-col justify-between hover:border-amber-500/40 transition">
              <div>
                <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 text-[var(--tg-status-warning)] flex items-center justify-center mb-5">
                  <Sparkles className="w-5 h-5" />
                </div>
                <h3 className="text-base font-semibold text-[var(--tg-text-primary)] mb-2">Hybrid Consensus</h3>
                <p className="text-xs text-[var(--tg-text-secondary)] leading-relaxed mb-4">
                  Combines normalized deterministic scores with statistical anomaly confidence (0.6 FSM + 0.4 ML), enforcing a 60-point risk floor whenever a protocol violation is proven.
                </p>
              </div>
              <ul className="text-xs text-[var(--tg-text-muted)] space-y-2 pt-4 border-t border-[var(--tg-border-subtle)] font-mono">
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-status-warning)] shrink-0" /> Calibrated four-tier risk classification</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-status-warning)] shrink-0" /> Responsible event attribution</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing / Tiers Section */}
      <section id="tiers" className="py-20 px-6 border-t border-[var(--tg-border-subtle)]">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <div className="text-xs font-mono text-[var(--tg-accent-emerald)] font-semibold uppercase tracking-wider mb-2">Entitlements</div>
            <h2 className="text-2xl sm:text-3xl font-bold text-[var(--tg-text-primary)] mb-3">
              Flexible SOC Workspace Tiers
            </h2>
            <p className="text-xs sm:text-sm text-[var(--tg-text-muted)] max-w-lg mx-auto">
              Prepared for high-throughput enterprise security teams. Select the operational tier suited for your inspection scale.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {/* Free */}
            <div className="tg-panel p-6 flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-semibold text-[var(--tg-text-primary)]">Developer Research</h3>
                <div className="mt-3 mb-4">
                  <span className="text-3xl font-bold font-mono text-[var(--tg-text-primary)]">$0</span>
                  <span className="text-[var(--tg-text-muted)] text-xs font-mono"> / month</span>
                </div>
                <p className="text-xs text-[var(--tg-text-muted)] mb-5">For academic and security researchers exploring deterministic FSM modeling.</p>
                <ul className="space-y-2.5 text-xs text-[var(--tg-text-secondary)] mb-6 font-mono">
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)]" /> 1 Workspace Member</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)]" /> 50 Simulations / day</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)]" /> Up to 5 Uploaded Datasets</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)]" /> All 3 Detection Engines</li>
                </ul>
              </div>
              <Link to="/signup" className="tg-btn-secondary text-xs text-center justify-center">
                Get Started
              </Link>
            </div>

            {/* Pro */}
            <div className="tg-panel p-6 border-emerald-500/50 relative flex flex-col justify-between shadow-lg shadow-emerald-500/5">
              <div className="absolute -top-2.5 right-6 px-2.5 py-0.5 bg-emerald-500 text-slate-950 text-[10px] font-bold rounded-full uppercase tracking-wider font-mono">
                Recommended
              </div>
              <div>
                <h3 className="text-sm font-semibold text-[var(--tg-text-primary)]">Professional SOC</h3>
                <div className="mt-3 mb-4">
                  <span className="text-3xl font-bold font-mono text-[var(--tg-text-primary)]">$49</span>
                  <span className="text-[var(--tg-text-muted)] text-xs font-mono"> / month</span>
                </div>
                <p className="text-xs text-[var(--tg-text-muted)] mb-5">For active incident response teams managing real-time packet triage queues.</p>
                <ul className="space-y-2.5 text-xs text-[var(--tg-text-secondary)] mb-6 font-mono">
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)]" /> 5 Workspace Members</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)]" /> 500 Simulations / day</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)]" /> 50 Uploaded Datasets</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)]" /> Detection Lab Benchmarks</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)]" /> Forensic Incident Notes</li>
                </ul>
              </div>
              <Link to="/signup" className="tg-btn-primary text-xs text-center justify-center">
                Start Pro Trial
              </Link>
            </div>

            {/* Team */}
            <div className="tg-panel p-6 flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-semibold text-[var(--tg-text-primary)]">Enterprise SOC</h3>
                <div className="mt-3 mb-4">
                  <span className="text-3xl font-bold font-mono text-[var(--tg-text-primary)]">$199</span>
                  <span className="text-[var(--tg-text-muted)] text-xs font-mono"> / month</span>
                </div>
                <p className="text-xs text-[var(--tg-text-muted)] mb-5">Multi-tenant SOCs requiring enterprise compliance and unlimited simulation feeds.</p>
                <ul className="space-y-2.5 text-xs text-[var(--tg-text-secondary)] mb-6 font-mono">
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)]" /> Unlimited Workspace Members</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)]" /> Custom Role-Based Access</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)]" /> Unlimited Ingestion Buffers</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)]" /> Dedicated Telemetry Stream</li>
                </ul>
              </div>
              <Link to="/signup" className="tg-btn-secondary text-xs text-center justify-center">
                Contact Sales
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-[var(--tg-border-subtle)] bg-[var(--tg-bg-base)] py-8 px-6 text-xs text-[var(--tg-text-muted)] font-mono">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-[var(--tg-text-secondary)]">
            <img src="/traceguard-ai-icon-color.svg" alt="TraceGuard" className="w-4 h-4" />
            <span className="font-semibold text-[var(--tg-text-primary)]">TraceGuard AI</span> &copy; 2026. All rights reserved.
          </div>
          <div className="flex space-x-6">
            <Link to="/" className="hover:text-[var(--tg-accent-emerald)] transition-colors">Dashboard</Link>
            <Link to="/login" className="hover:text-[var(--tg-accent-emerald)] transition-colors">Sign In</Link>
            <Link to="/signup" className="hover:text-[var(--tg-accent-emerald)] transition-colors">Register</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
