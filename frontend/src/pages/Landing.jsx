import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Cpu, Activity, Lock, Layers, Zap, CheckCircle2, ArrowRight } from 'lucide-react';

export default function Landing() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-slate-950">
      {/* Top Navigation */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                TraceGuard<span className="text-cyan-400"> AI</span>
              </span>
              <span className="ml-2 text-xs uppercase px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-400 border border-cyan-800/60">
                SaaS MVP
              </span>
            </div>
          </div>

          <nav className="hidden md:flex items-center space-x-8 text-sm font-medium text-slate-300">
            <a href="#features" className="hover:text-cyan-400 transition-colors">Engines</a>
            <a href="#architecture" className="hover:text-cyan-400 transition-colors">Architecture</a>
            <a href="#pricing" className="hover:text-cyan-400 transition-colors">Tiers</a>
          </nav>

          <div className="flex items-center space-x-4">
            <Link
              to="/login"
              className="text-sm font-medium text-slate-300 hover:text-white px-4 py-2 transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/signup"
              className="text-sm font-semibold text-slate-950 bg-gradient-to-r from-cyan-400 to-blue-500 hover:from-cyan-300 hover:to-blue-400 px-4 py-2 rounded-lg shadow-md shadow-cyan-500/20 transition-all flex items-center gap-1.5"
            >
              Get Started <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-24 pb-20 px-6 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(14,165,233,0.15),rgba(255,255,255,0))]" />
        
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-300 text-xs font-medium mb-8">
            <Zap className="w-3.5 h-3.5" /> Next-Gen Deterministic + ML Protocol NIDS
          </div>

          <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight text-white mb-6 leading-tight">
            Understand network anomalies. <br />
            <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400 bg-clip-text text-transparent">
              Explain every suspicious transition.
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            TraceGuard AI unifies formal Finite-State Machine verification with machine learning anomaly detection to uncover protocol violations, zero-day sequences, and stealth attacks with explainable evidence.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/app"
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold shadow-lg shadow-cyan-500/25 transition-all text-center flex items-center justify-center gap-2"
            >
              Launch Live Platform <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/signup"
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl border border-slate-700 hover:border-slate-600 bg-slate-900/60 hover:bg-slate-800 text-slate-200 font-semibold transition-all text-center"
            >
              Create Free Workspace
            </Link>
          </div>

          {/* KPI Strip */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-16 pt-12 border-t border-slate-800/80 text-left">
            <div className="bg-slate-900/40 p-4 rounded-xl border border-slate-800/60">
              <div className="text-2xl font-bold text-cyan-400">3 Engines</div>
              <div className="text-xs text-slate-400 mt-1">FSM, ML, & Hybrid Consensus</div>
            </div>
            <div className="bg-slate-900/40 p-4 rounded-xl border border-slate-800/60">
              <div className="text-2xl font-bold text-sky-400">68.0%</div>
              <div className="text-xs text-slate-400 mt-1">Unseen Attack Detection Rate</div>
            </div>
            <div className="bg-slate-900/40 p-4 rounded-xl border border-slate-800/60">
              <div className="text-2xl font-bold text-indigo-400">100%</div>
              <div className="text-xs text-slate-400 mt-1">Explainable State Violations</div>
            </div>
            <div className="bg-slate-900/40 p-4 rounded-xl border border-slate-800/60">
              <div className="text-2xl font-bold text-emerald-400">Multi-Tenant</div>
              <div className="text-xs text-slate-400 mt-1">Workspace Isolation & RBAC</div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Engines Section */}
      <section id="features" className="py-20 px-6 border-t border-slate-800/80 bg-slate-900/20">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Three Complementary Detection Disciplines</h2>
            <p className="text-slate-400 max-w-xl mx-auto">
              Conventional NIDS miss out-of-order transitions, while statistical models produce opaque false positives. TraceGuard eliminates both blind spots.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-cyan-500/50 transition-all">
              <div className="w-12 h-12 rounded-xl bg-cyan-950 text-cyan-400 flex items-center justify-center mb-6">
                <Layers className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Deterministic FSM</h3>
              <p className="text-sm text-slate-400 leading-relaxed mb-4">
                Models the 8-state HTTP lifecycle across 15 valid transitions. Immediately intercepts impossible jumps, unauthorized verbs, and early responses with deterministic certainty.
              </p>
              <ul className="text-xs text-slate-400 space-y-2">
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" /> Exact transition identification</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" /> Zero false positive guarantees on specification violations</li>
              </ul>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-sky-500/50 transition-all">
              <div className="w-12 h-12 rounded-xl bg-sky-950 text-sky-400 flex items-center justify-center mb-6">
                <Cpu className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Isolation Forest ML</h3>
              <p className="text-sm text-slate-400 leading-relaxed mb-4">
                Extracts 15 behavioral features across session duration, payload skew, byte ratios, and response timing to capture novel anomaly structures without manual signatures.
              </p>
              <ul className="text-xs text-slate-400 space-y-2">
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-sky-400" /> Evaluated on unseen attack templates</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-sky-400" /> Sub-millisecond inference per session</li>
              </ul>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-indigo-500/50 transition-all">
              <div className="w-12 h-12 rounded-xl bg-indigo-950 text-indigo-400 flex items-center justify-center mb-6">
                <Activity className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Hybrid Consensus</h3>
              <p className="text-sm text-slate-400 leading-relaxed mb-4">
                Combines normalized deterministic scores with statistical anomaly confidence (0.6 FSM + 0.4 ML), enforcing a 60-point risk floor whenever a protocol violation is proven.
              </p>
              <ul className="text-xs text-slate-400 space-y-2">
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" /> Calibrated four-tier risk classification</li>
                <li className="flex items-center gap-2"><CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" /> Responsible event attribution</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing / Tiers Section */}
      <section id="pricing" className="py-20 px-6 border-t border-slate-800/80">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Flexible SaaS Workspace Tiers</h2>
            <p className="text-slate-400 max-w-lg mx-auto">
              Prepared for high-throughput enterprise security teams. Select the entitlement model that fits your operational needs.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Free */}
            <div className="p-8 rounded-2xl bg-slate-900/50 border border-slate-800 flex flex-col justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white">Free Developer</h3>
                <div className="mt-4 mb-6">
                  <span className="text-4xl font-extrabold text-white">$0</span>
                  <span className="text-slate-400 text-sm"> / month</span>
                </div>
                <p className="text-xs text-slate-400 mb-6">For security researchers exploring deterministic FSM modeling.</p>
                <ul className="space-y-3 text-xs text-slate-300 mb-8">
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400" /> 1 Workspace Member</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400" /> 50 Simulations / day</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400" /> Up to 5 Uploaded Datasets</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400" /> All 3 Detection Engines</li>
                </ul>
              </div>
              <Link to="/signup" className="w-full py-2.5 rounded-lg border border-slate-700 hover:bg-slate-800 text-center text-sm font-semibold text-slate-200">
                Get Started
              </Link>
            </div>

            {/* Pro */}
            <div className="p-8 rounded-2xl bg-gradient-to-b from-slate-900 to-cyan-950/20 border-2 border-cyan-500/60 relative flex flex-col justify-between shadow-xl shadow-cyan-950/40">
              <div className="absolute -top-3 right-6 px-3 py-1 bg-cyan-500 text-slate-950 text-xs font-bold rounded-full uppercase tracking-wider">
                Popular
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Professional SOC</h3>
                <div className="mt-4 mb-6">
                  <span className="text-4xl font-extrabold text-white">$49</span>
                  <span className="text-slate-400 text-sm"> / month</span>
                </div>
                <p className="text-xs text-slate-400 mb-6">For incident responders managing active threat queues.</p>
                <ul className="space-y-3 text-xs text-slate-300 mb-8">
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400" /> 5 Workspace Members</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400" /> 500 Simulations / day</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400" /> 50 Uploaded Datasets</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400" /> Advanced Detection Lab Benchmarks</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400" /> CSV & JSON Threat Exports</li>
                </ul>
              </div>
              <Link to="/signup" className="w-full py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-center text-sm font-bold shadow-md shadow-cyan-500/20">
                Start Pro Trial
              </Link>
            </div>

            {/* Team */}
            <div className="p-8 rounded-2xl bg-slate-900/50 border border-slate-800 flex flex-col justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white">Enterprise Team</h3>
                <div className="mt-4 mb-6">
                  <span className="text-4xl font-extrabold text-white">$199</span>
                  <span className="text-slate-400 text-sm"> / month</span>
                </div>
                <p className="text-xs text-slate-400 mb-6">Multi-organization SOCs requiring enterprise compliance.</p>
                <ul className="space-y-3 text-xs text-slate-300 mb-8">
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400" /> Unlimited Workspace Members</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400" /> Custom Role-Based Access Control</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400" /> Unlimited Simulations & Datasets</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-400" /> Dedicated Cloud PostgreSQL Support</li>
                </ul>
              </div>
              <Link to="/signup" className="w-full py-2.5 rounded-lg border border-slate-700 hover:bg-slate-800 text-center text-sm font-semibold text-slate-200">
                Contact Sales
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-900 bg-slate-950 py-10 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-slate-400">
            <Shield className="w-4 h-4 text-cyan-400" />
            <span className="font-semibold text-white">TraceGuard AI</span> &copy; 2026. All rights reserved.
          </div>
          <div className="flex space-x-6 text-slate-400">
            <Link to="/app" className="hover:text-cyan-400">Dashboard</Link>
            <Link to="/login" className="hover:text-cyan-400">Sign In</Link>
            <Link to="/signup" className="hover:text-cyan-400">Register</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
