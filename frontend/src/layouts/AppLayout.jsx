import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
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
  PlaySquare,
  ChevronRight,
  ShieldCheck,
  Cpu,
  User,
  LogOut,
  PanelLeftClose,
  PanelLeft
} from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAuth } from '../context/AuthContext';
import PresentationMode from '../components/PresentationMode';

const NAV_ITEMS = [
  { name: 'Overview', path: '/', icon: LayoutDashboard, badge: null },
  { name: 'Automata Lab', path: '/automata', icon: GitBranch, badge: 'TOC' },
  { name: 'Protocol Explorer', path: '/protocol', icon: Activity, badge: 'Simulator' },
  { name: 'Live Monitor', path: '/monitor', icon: Radio, badge: 'Live' },
  { name: 'Threats', path: '/threats', icon: ShieldAlert, badge: null },
  { name: 'Detection Lab', path: '/lab', icon: FlaskConical, badge: 'Multi-Engine' },
  { name: 'Datasets', path: '/datasets', icon: Database, badge: null },
  { name: 'Settings', path: '/settings', icon: Settings, badge: null },
];

export function AppLayout() {
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(() => {
    try {
      return localStorage.getItem('tg_sidebar_collapsed') === 'true';
    } catch {
      return false;
    }
  });
  const [presentationOpen, setPresentationOpen] = useState(false);
  const { status: wsStatus } = useWebSocket();
  const { user, logout, isAuthenticated } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  // Persist sidebar collapse preference
  const toggleCollapse = () => {
    setIsCollapsed((prev) => {
      const next = !prev;
      try {
        localStorage.setItem('tg_sidebar_collapsed', String(next));
      } catch {
        // ignore
      }
      return next;
    });
  };

  // Close mobile drawer on route change
  useEffect(() => {
    setMobileDrawerOpen(false);
  }, [location.pathname]);

  // Support direct entry to presentation mode via query param or hash
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get('presentation') === 'true' || location.hash === '#presentation') {
      setPresentationOpen(true);
    }
  }, [location.search, location.hash]);

  // Close mobile drawer on Escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && mobileDrawerOpen) {
        setMobileDrawerOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [mobileDrawerOpen]);

  // Lock body scroll when mobile drawer is open
  useEffect(() => {
    if (mobileDrawerOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [mobileDrawerOpen]);

  const getStatusIndicator = () => {
    switch (wsStatus) {
      case 'connected':
        return {
          color: 'bg-[var(--tg-accent-emerald)]',
          textColor: 'text-[var(--tg-accent-emerald)]',
          borderColor: 'border-[var(--tg-accent-emerald)]/30',
          label: 'STREAM ONLINE',
        };
      case 'connecting':
        return {
          color: 'bg-[var(--tg-status-warning)]',
          textColor: 'text-[var(--tg-status-warning)]',
          borderColor: 'border-[var(--tg-status-warning)]/30',
          label: 'CONNECTING',
        };
      default:
        return {
          color: 'bg-[var(--tg-status-danger)]',
          textColor: 'text-[var(--tg-status-danger)]',
          borderColor: 'border-[var(--tg-status-danger)]/30',
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
      {/* Mobile Drawer Backdrop Overlay */}
      {mobileDrawerOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/75 backdrop-blur-sm lg:hidden transition-opacity"
          onClick={() => setMobileDrawerOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Primary Sidebar (Responsive: Off-canvas on Mobile, Collapsible on Desktop) */}
      <aside
        className={`fixed lg:static top-0 bottom-0 left-0 z-50 flex flex-col bg-[var(--tg-bg-base)] border-r border-[var(--tg-border-subtle)] transition-all duration-200 ease-out ${
          mobileDrawerOpen ? 'translate-x-0 w-64' : '-translate-x-full lg:translate-x-0'
        } ${isCollapsed ? 'lg:w-16' : 'lg:w-64'}`}
        aria-label="Sidebar Navigation"
      >
        {/* Brand Header: Official Icon & Wordmark Side-by-Side */}
        <div className="flex items-center justify-between h-16 px-3.5 border-b border-[var(--tg-border-subtle)] bg-[var(--tg-bg-surface)]/50">
          <NavLink
            to="/"
            onClick={() => setMobileDrawerOpen(false)}
            className="flex items-center gap-2.5 group focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--tg-status-info)] rounded-md py-1 overflow-hidden"
            aria-label="TraceGuard AI Home"
          >
            {/* Official Icon: 320x320 SVG rendered at consistent square ratio */}
            <img
              src="/traceguard-ai-icon-color.svg"
              alt="TraceGuard AI Icon"
              className="w-7 h-7 shrink-0 object-contain rounded-md"
            />

            {/* Official Wordmark: 712x204 SVG rendered side-by-side (hidden when collapsed on desktop) */}
            {(!isCollapsed || mobileDrawerOpen) && (
              <img
                src="/traceguard-ai-wordmark-color.svg"
                alt="TraceGuard AI Wordmark"
                className="h-5 w-auto max-w-[145px] object-contain transition-opacity duration-150 shrink-0"
              />
            )}
          </NavLink>

          {/* Close button for Mobile Drawer */}
          <button
            onClick={() => setMobileDrawerOpen(false)}
            className="p-1.5 rounded-md lg:hidden text-[var(--tg-text-muted)] hover:text-[var(--tg-text-primary)] hover:bg-[var(--tg-bg-surface)] focus:outline-none"
            aria-label="Close navigation drawer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-2.5 py-4 space-y-1 overflow-y-auto" aria-label="Main Navigation">
          {(!isCollapsed || mobileDrawerOpen) && (
            <div className="px-2.5 pb-2 text-[10px] font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-muted)]">
              Core Modules
            </div>
          )}
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setMobileDrawerOpen(false)}
                title={isCollapsed && !mobileDrawerOpen ? item.name : undefined}
                className={({ isActive }) =>
                  `group flex items-center ${
                    isCollapsed && !mobileDrawerOpen ? 'justify-center px-2 py-2.5' : 'justify-between px-3 py-2'
                  } rounded-md text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-[var(--tg-bg-surface)] text-[var(--tg-text-primary)] border border-[var(--tg-border-default)] shadow-xs'
                      : 'text-[var(--tg-text-secondary)] hover:text-[var(--tg-text-primary)] hover:bg-[var(--tg-bg-surface)]/70'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <div className="flex items-center gap-2.5">
                      <Icon
                        className={`w-4 h-4 shrink-0 transition-colors ${
                          isActive
                            ? 'text-[var(--tg-status-info)]'
                            : 'text-[var(--tg-text-muted)] group-hover:text-[var(--tg-status-info)]'
                        }`}
                      />
                      {(!isCollapsed || mobileDrawerOpen) && <span>{item.name}</span>}
                    </div>
                    {(!isCollapsed || mobileDrawerOpen) && item.badge && (
                      <span
                        className={`text-[9px] font-mono px-1.5 py-0.5 rounded border ${
                          isActive
                            ? 'bg-[var(--tg-accent-emerald-subtle)] text-[var(--tg-accent-emerald)] border-[var(--tg-accent-emerald)]/30'
                            : 'bg-[var(--tg-bg-canvas)] border-[var(--tg-border-subtle)] text-[var(--tg-text-muted)] group-hover:text-[var(--tg-text-secondary)]'
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Telemetry & User Account Footer */}
        <div className="p-3 border-t border-[var(--tg-border-subtle)] bg-[var(--tg-bg-root)]/40 space-y-2">
          {/* Academic Environment Badge (Auth-Free Local Mode) */}
          {(!isCollapsed || mobileDrawerOpen) ? (
            <div className="flex items-center justify-between px-2.5 py-2 rounded-lg bg-[var(--tg-bg-surface)] border border-[var(--tg-border-subtle)]">
              <div className="flex items-center gap-2 min-w-0">
                <div className="w-6 h-6 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-[var(--tg-accent-emerald)] text-[10px] font-mono font-bold shrink-0">
                  <ShieldCheck className="w-3.5 h-3.5" />
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-medium text-[var(--tg-text-primary)] truncate">
                    Academic Edition
                  </p>
                  <p className="text-[10px] font-mono text-[var(--tg-text-muted)] truncate">
                    Theory of Computation Lab
                  </p>
                </div>
              </div>
              <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-[var(--tg-accent-emerald)] border border-emerald-500/30 font-semibold shrink-0">
                ACTIVE
              </span>
            </div>
          ) : (
            <div className="flex justify-center" title="TraceGuard AI · Academic Edition (Theory of Computation Lab)">
              <div className="w-8 h-8 rounded-full bg-[var(--tg-bg-surface)] border border-emerald-500/30 flex items-center justify-center text-[var(--tg-accent-emerald)]">
                <ShieldCheck className="w-4 h-4" />
              </div>
            </div>
          )}

          {/* Engine Status Widget */}
          {(!isCollapsed || mobileDrawerOpen) ? (
            <div className="p-2.5 rounded-lg bg-[var(--tg-bg-surface)] border border-[var(--tg-border-subtle)] space-y-1.5">
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
              <div className="flex items-center justify-between text-[10px] font-mono text-[var(--tg-text-muted)] pt-1.5 border-t border-[var(--tg-border-subtle)]">
                <span>9-State Complete DFA</span>
                <span className="text-[var(--tg-accent-emerald)] font-semibold">M=(Q,Σ,δ)</span>
              </div>
            </div>
          ) : (
            <div className="flex justify-center py-1" title={`Engine Status: ${status.label} · 9-State Complete DFA`}>
              <span className={`w-2.5 h-2.5 rounded-full ${status.color} animate-pulse`} />
            </div>
          )}
        </div>
      </aside>

      {/* Main View Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header Bar */}
        <header className="h-14 px-4 sm:px-6 flex items-center justify-between border-b border-[var(--tg-border-subtle)] bg-[var(--tg-bg-base)]/85 backdrop-blur-md shrink-0">
          <div className="flex items-center gap-3">
            {/* Mobile Hamburger Button */}
            <button
              onClick={() => setMobileDrawerOpen(true)}
              className="p-1.5 rounded-md lg:hidden text-[var(--tg-text-muted)] hover:text-[var(--tg-text-primary)] hover:bg-[var(--tg-bg-surface)] focus:outline-none focus-visible:ring-1 focus-visible:ring-[var(--tg-status-info)]"
              aria-label="Open mobile navigation"
            >
              <Menu className="w-5 h-5" />
            </button>

            {/* Desktop Hamburger Collapse/Expand Toggle Button */}
            <button
              onClick={toggleCollapse}
              className="hidden lg:flex p-1.5 rounded-md text-[var(--tg-text-muted)] hover:text-[var(--tg-text-primary)] hover:bg-[var(--tg-bg-surface)] focus:outline-none focus-visible:ring-1 focus-visible:ring-[var(--tg-status-info)] transition"
              title={isCollapsed ? 'Expand sidebar (Ctrl+B)' : 'Collapse sidebar (Ctrl+B)'}
              aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              {isCollapsed ? <PanelLeft className="w-4 h-4" /> : <PanelLeftClose className="w-4 h-4" />}
            </button>

            {/* Breadcrumb Navigation */}
            <nav className="flex items-center gap-2 text-xs font-mono text-[var(--tg-text-muted)]" aria-label="Breadcrumb">
              <span className="hover:text-[var(--tg-text-secondary)] transition-colors">TraceGuard</span>
              <ChevronRight className="w-3.5 h-3.5 text-[var(--tg-text-disabled)]" />
              <span className="text-[var(--tg-text-primary)] font-semibold">{currentNav.name}</span>
            </nav>
          </div>

          <div className="flex items-center gap-3">
            {/* Presentation Mode CTA */}
            <button
              onClick={() => setPresentationOpen(true)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-[var(--tg-accent-emerald-subtle)] border border-[var(--tg-accent-emerald)]/30 text-[var(--tg-accent-emerald)] hover:bg-[var(--tg-accent-emerald)]/20 text-xs font-mono font-semibold transition focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--tg-accent-emerald)]"
            >
              <PlaySquare className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Presentation Mode</span>
              <span className="sm:hidden">Defense</span>
            </button>

            {/* Academic DFA Specification Badge */}
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-md bg-[var(--tg-bg-surface)] border border-[var(--tg-border-subtle)] text-[11px] font-mono text-[var(--tg-text-secondary)]">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--tg-status-info)]"></span>
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
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 bg-[var(--tg-bg-root)]" role="main">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

export default AppLayout;
