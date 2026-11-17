import React, { useState } from 'react';
import { Link, useNavigate, Navigate, useLocation } from 'react-router-dom';
import { Lock, User, AlertCircle, ArrowRight, ShieldCheck, Key } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  if (isAuthenticated) {
    const from = location.state?.from?.pathname || '/';
    return <Navigate to={from} replace />;
  }

  const handleFillDemo = () => {
    setUsername('demo');
    setPassword('traceguard2024');
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await login(username, password);
      const from = location.state?.from?.pathname || '/';
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message || 'Invalid username or password');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--tg-bg-root)] flex flex-col justify-center items-center px-6 py-12 text-[var(--tg-text-primary)] font-sans">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center mb-8">
        {/* Official Brand Logo Treatment: Icon + Wordmark Side-by-Side */}
        <div className="inline-flex items-center justify-center gap-3 mb-6">
          <img
            src="/traceguard-ai-icon-color.svg"
            alt="TraceGuard AI Icon"
            className="w-10 h-10 object-contain rounded-lg"
          />
          <img
            src="/traceguard-ai-wordmark-color.svg"
            alt="TraceGuard AI Wordmark"
            className="h-8 w-auto max-w-[200px] object-contain"
          />
        </div>
        <h1 className="text-xl font-bold text-[var(--tg-text-primary)] tracking-tight">
          Sign in to your SOC Workspace
        </h1>
        <p className="mt-2 text-xs text-[var(--tg-text-muted)] font-mono">
          Formal protocol automata verification & hybrid anomaly detection
        </p>
      </div>

      <div className="w-full max-w-md tg-panel p-8">
        {error && (
          <div className="mb-6 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-[var(--tg-status-danger)] text-xs flex items-start gap-2.5 font-mono">
            <AlertCircle className="w-4 h-4 flex-shrink-0 text-[var(--tg-status-danger)] mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-[11px] font-mono text-[var(--tg-text-muted)] mb-1.5 uppercase">
              Username
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[var(--tg-text-muted)]">
                <User className="w-4 h-4" />
              </div>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username"
                className="tg-input pl-9 text-xs font-mono"
                autoComplete="username"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-mono text-[var(--tg-text-muted)] mb-1.5 uppercase">
              Password
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[var(--tg-text-muted)]">
                <Lock className="w-4 h-4" />
              </div>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                className="tg-input pl-9 text-xs font-mono"
                autoComplete="current-password"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full tg-btn-primary py-2.5 text-xs font-semibold flex items-center justify-center gap-2 mt-2"
          >
            <span>{submitting ? 'Verifying Credentials...' : 'Sign In'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Demo Credentials Quick Pill */}
        <div className="mt-6 pt-5 border-t border-[var(--tg-border-subtle)] flex items-center justify-between">
          <span className="text-[11px] font-mono text-[var(--tg-text-muted)]">Academic Review?</span>
          <button
            type="button"
            onClick={handleFillDemo}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] font-mono bg-[var(--tg-bg-surface)] hover:bg-[var(--tg-bg-hover)] border border-[var(--tg-border-default)] text-[var(--tg-accent-emerald)] transition"
          >
            <Key className="w-3 h-3" />
            <span>Use Demo Account</span>
          </button>
        </div>

        <div className="mt-4 text-center">
          <p className="text-[11px] text-[var(--tg-text-muted)] font-mono">
            New organization?{' '}
            <Link to="/signup" className="text-[var(--tg-accent-emerald)] hover:underline font-semibold">
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
