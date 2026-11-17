import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Lock, User, Mail, AlertCircle, ArrowRight, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Signup() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await signup({
        username,
        email,
        password,
        full_name: fullName
      });
      navigate('/');
    } catch (err) {
      setError(err.message || 'Registration failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--tg-bg-root)] flex flex-col justify-center items-center px-6 py-12 text-[var(--tg-text-primary)] font-sans">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center mb-8">
        <Link to="/" className="inline-flex items-center space-x-3 mb-6 group">
          <img
            src="/traceguard-ai-icon-color.svg"
            alt="TraceGuard AI"
            className="w-10 h-10 rounded-xl shadow-sm"
          />
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold tracking-tight text-[var(--tg-text-primary)]">
              TraceGuard<span className="text-[var(--tg-accent-emerald)]"> AI</span>
            </span>
          </div>
        </Link>
        <h2 className="text-xl font-bold text-[var(--tg-text-primary)] tracking-tight">
          Create your SOC Workspace
        </h2>
        <p className="mt-2 text-xs text-[var(--tg-text-muted)] font-mono">
          Already have an account?{' '}
          <Link to="/login" className="text-[var(--tg-accent-emerald)] hover:text-emerald-700 font-semibold transition">
            Sign in
          </Link>
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
              Full Name
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[var(--tg-text-muted)]">
                <User className="w-4 h-4" />
              </div>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="e.g. Alex Vance"
                className="tg-input pl-9 text-xs font-mono"
              />
            </div>
          </div>

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
                placeholder="Choose username"
                className="tg-input pl-9 text-xs font-mono"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-mono text-[var(--tg-text-muted)] mb-1.5 uppercase">
              Work Email
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[var(--tg-text-muted)]">
                <Mail className="w-4 h-4" />
              </div>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="alex@company.com"
                className="tg-input pl-9 text-xs font-mono"
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
                placeholder="Min 6 characters"
                className="tg-input pl-9 text-xs font-mono"
              />
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={submitting}
              className="w-full tg-btn-primary text-xs justify-center flex items-center gap-2 disabled:opacity-50"
            >
              <span>{submitting ? 'Creating Workspace...' : 'Register Workspace'}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </form>

        <div className="mt-6 pt-4 border-t border-[var(--tg-border-subtle)] text-[11px] font-mono text-[var(--tg-text-muted)] space-y-1.5">
          <div className="flex items-center gap-2 text-[var(--tg-text-secondary)]">
            <CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)] shrink-0" />
            <span>Auto-provisions isolated personal tenant workspace</span>
          </div>
          <div className="flex items-center gap-2 text-[var(--tg-text-secondary)]">
            <CheckCircle2 className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)] shrink-0" />
            <span>Assigns Workspace Owner & Security Analyst credentials</span>
          </div>
        </div>
      </div>
    </div>
  );
}
