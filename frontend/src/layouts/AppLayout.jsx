import React, { useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Radio,
  ShieldAlert,
  FlaskConical,
  GitBranch,
  Database,
  Settings,
  Activity,
  Menu,
  X,
  Server,
  PlaySquare,
  ChevronRight,
  ShieldCheck,
  Cpu
} from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';
import PresentationMode from '../components/PresentationMode';

const NAV_ITEMS = [
  { name: 'Overview', path: '/', icon: LayoutDashboard, badge: null },
  { name: 'Automata Lab', path: '/automata', icon: GitBranch, badge: 'TOC' },
  { name: 'Live Monitor', path: '/monitor', icon: Radio, badge: 'Live' },
  { name: 'Threats', path: '/threats', icon: ShieldAlert, badge: null },
  { name: 'Detection Lab', path: '/lab', icon: FlaskConical, badge: 'Multi-Engine' },
  { name: 'Datasets', path: '/datasets', icon: Database, badge: null },
  { name: 'Settings', path: '/settings', icon: Settings, badge: null },
];

export function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [presentationOpen, setPresentationOpen] = useState(false);
  const { status: wsStatus } = useWebSocket();
  const location = useLocation();

  const getStatusIndicator = () => {
    switch (wsStatus) {
      case 'connected':
        return {
          color: 'bg-emerald-500',
          textColor: 'text-emerald-400',
          borderColor: 'border-emerald-500/30',
          label: 'STREAM ONLINE',
        };
      case 'connecting':
        return {
          color: 'bg-amber-500',
          textColor: 'text-amber-400',
          borderColor: 'border-amber-500/30',
          label: 'RECONNECTING',
        };
      default:
        return {
          color: 'bg-rose-500',
          textColor: 'text-rose-400',
          borderColor: 'border-rose-500/30',
          label: 'OFFLINE',
        };
    }
  };

  const status = getStatusIndicator();

  // Find active route item for breadcrumbs
  const currentNav = NAV_ITEMS.find((item) =>
    item.path === '/' ? location.pathname === '/' : location.pathname.startsWith(item.path)
  ) || { name: 'Overview' };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[var(--tg-bg-root)] text-[var(--tg-text-primary)]">
      {/* Mobile backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm lg:hidden transition-opacity"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Primary Sidebar */}
      <aside
        className={`fixed lg:static top-0 bottom-0 left-0 z-50 w-64 flex flex-col bg-[var(--tg-bg-base)] border-r border-[var(--tg-border-subtle)] transition-transform duration-200 ease-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Brand Header */}
        <div className="flex items-center justify-between h-16 px-5 border-b border-[var(--tg-border-subtle)] bg-[var(--tg-bg-root)]/40">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-sm">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-semibold text-sm tracking-tight text-[var(--tg-text-primary)]">
                  TraceGuard
                </span>
                <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  AI
                </span>
              </div>
              <p className="text-[10px] font-mono text-[var(--tg-text-muted)] tracking-wider">
                NETWORK INTELLIGENCE
              </p>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-1.5 rounded-md lg:hidden text-[var(--tg-text-muted)] hover:text-[var(--tg-text-primary)] hover:bg-[var(--tg-bg-surface)] focus:outline-none focus:ring-1 focus:ring-emerald-500"
            aria-label="Close sidebar"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto" aria-label="Main Navigation">
          <div className="px-2 pb-2 text-[10px] font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-muted)]">
            Core Modules
          </div>
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `group flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-[var(--tg-bg-surface)] text-[var(--tg-text-primary)] border border-[var(--tg-border-default)] shadow-xs'
                      : 'text-[var(--tg-text-secondary)] hover:text-[var(--tg-text-primary)] hover:bg-[var(--tg-bg-surface)]/60'
                  }`
                }
              >
                <div className="flex items-center gap-2.5">
                  <Icon className="w-4 h-4 text-[var(--tg-text-muted)] group-hover:text-emerald-400 transition-colors" />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-[var(--tg-text-muted)] group-hover:text-[var(--tg-text-secondary)]">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Telemetry & Daemon Status Footer */}
        <div className="p-4 border-t border-[var(--tg-border-subtle)] bg-[var(--tg-bg-root)]/30 space-y-3">
          <div className="p-2.5 rounded-lg bg-[var(--tg-bg-surface)] border border-[var(--tg-border-subtle)] space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono text-[var(--tg-text-muted)] flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5" />
                <span>Detection Engine</span>
              </span>
              <div className="flex items-center gap-1.5">
                <span className={`w-1.5 h-1.5 rounded-full ${status.color} animate-pulse`} />
                <span className={`text-[10px] font-mono font-semibold ${status.textColor}`}>
                  {status.label}
                </span>
              </div>
            </div>
            <div className="flex items-center justify-between text-[10px] font-mono text-[var(--tg-text-muted)] pt-1 border-t border-[var(--tg-border-subtle)]">
              <span>9-State DFA</span>
              <span className="text-emerald-400">Formal M=(Q,Σ,δ)</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main View Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header Bar */}
        <header className="h-14 px-6 flex items-center justify-between border-b border-[var(--tg-border-subtle)] bg-[var(--tg-bg-base)]/80 backdrop-blur-md shrink-0">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-1.5 rounded-md lg:hidden text-[var(--tg-text-muted)] hover:text-[var(--tg-text-primary)] hover:bg-[var(--tg-bg-surface)]"
              aria-label="Open sidebar"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2 text-xs font-mono text-[var(--tg-text-muted)]">
              <span>TraceGuard</span>
              <ChevronRight className="w-3.5 h-3.5 text-[var(--tg-text-disabled)]" />
              <span className="text-[var(--tg-text-primary)] font-semibold">{currentNav.name}</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Presentation Mode CTA */}
            <button
              onClick={() => setPresentationOpen(true)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20 text-xs font-mono font-semibold transition"
            >
              <PlaySquare className="w-3.5 h-3.5" />
              <span>Presentation Mode</span>
            </button>

            {/* Academic DFA Badge */}
            <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-md bg-[var(--tg-bg-surface)] border border-[var(--tg-border-subtle)] text-[11px] font-mono text-[var(--tg-text-secondary)]">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
              <span className="text-[var(--tg-text-muted)]">DFA Spec:</span>
              <span className="text-[var(--tg-text-primary)] font-medium">9 States · 13 Symbols · 117 δ</span>
            </div>
          </div>
        </header>

        {/* Presentation Modal */}
        {presentationOpen && (
          <PresentationMode onClose={() => setPresentationOpen(false)} />
        )}

        {/* Primary Page Outlet */}
        <main className="flex-1 overflow-y-auto p-6 bg-[var(--tg-bg-root)]">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

export default AppLayout;
