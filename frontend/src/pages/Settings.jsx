import React, { useState } from 'react';
import {
  Sliders,
  User,
  Shield,
  Save,
  CheckCircle2,
  Server,
  Zap,
  Lock,
  Cpu,
  Binary,
  Layers
} from 'lucide-react';
import api from '../services/api';

export function Settings() {
  const [fsmWeight, setFsmWeight] = useState(0.6);
  const [mlWeight, setMlWeight] = useState(0.4);
  const [minViolationFloor, setMinViolationFloor] = useState(60);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const [username, setUsername] = useState('demo');
  const [email, setEmail] = useState('demo@traceguard.ai');

  const handleSaveWeights = (e) => {
    e.preventDefault();
    localStorage.setItem(
      'traceguard_hybrid_config',
      JSON.stringify({ fsmWeight, mlWeight, minViolationFloor })
    );
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Editorial Header */}
      <div className="pb-2 border-b border-[var(--tg-border-subtle)]">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-[var(--tg-accent-emerald)]" />
          <h1 className="text-lg font-semibold tracking-tight text-[var(--tg-text-primary)]">
            System Configuration & Hybrid Tuning
          </h1>
        </div>
        <p className="text-xs text-[var(--tg-text-muted)] mt-1">
          Adjust multi-engine consensus weights, violation floors, and operator workspace preferences.
        </p>
      </div>

      {/* Consensus Tuning Panel */}
      <div className="tg-panel p-5 space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-[var(--tg-border-subtle)]">
          <Layers className="w-4 h-4 text-[var(--tg-accent-emerald)]" />
          <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
            Hybrid Consensus Weight Calibration
          </h2>
        </div>

        {/* Academic scope notice */}
        <div className="mb-2 px-3 py-2 rounded bg-amber-500/10 border border-amber-500/20 text-[11px] font-mono text-[var(--tg-status-warning)]">
          <span className="font-semibold">Academic Demonstration Scope:</span> Weight values are saved locally to your browser for reference. The deployed hybrid engine uses the standard consensus formula S_h = 0.6·S_FSM + 0.4·S_ML as defined in the project specification. No backend API endpoint for runtime weight mutation is provided.
        </div>
        <form onSubmit={handleSaveWeights} className="space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* FSM Weight */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-[var(--tg-text-muted)] uppercase flex items-center gap-1.5">
                  <Binary className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)]" />
                  <span>FSM Invariant Weight (reference)</span>
                </span>
                <span className="text-[var(--tg-accent-emerald)] font-semibold">{(fsmWeight * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="1.0"
                step="0.05"
                value={fsmWeight}
                onChange={(e) => {
                  const val = parseFloat(e.target.value);
                  setFsmWeight(val);
                  setMlWeight(parseFloat((1.0 - val).toFixed(2)));
                }}
                className="w-full accent-emerald-500 cursor-pointer"
              />
              <p className="text-[11px] text-[var(--tg-text-muted)]">
                Relative contribution of deterministic DFA state-sequence verification. Default: 60%.
              </p>
            </div>

            {/* ML Weight */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-[var(--tg-text-muted)] uppercase flex items-center gap-1.5">
                  <Cpu className="w-3.5 h-3.5 text-[var(--tg-accent-blue)]" />
                  <span>Isolation Forest ML Weight (reference)</span>
                </span>
                <span className="text-[var(--tg-accent-blue)] font-semibold">{(mlWeight * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="1.0"
                step="0.05"
                value={mlWeight}
                onChange={(e) => {
                  const val = parseFloat(e.target.value);
                  setMlWeight(val);
                  setFsmWeight(parseFloat((1.0 - val).toFixed(2)));
                }}
                className="w-full accent-blue-500 cursor-pointer"
              />
              <p className="text-[11px] text-[var(--tg-text-muted)]">
                Statistical anomaly detection contribution from Isolation Forest model. Default: 40%.
              </p>
            </div>
          </div>

          {/* Violation Floor Slider */}
          <div className="space-y-2 pt-2 border-t border-[var(--tg-border-subtle)]">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-[var(--tg-text-muted)] uppercase">FSM Violation Risk Floor</span>
              <span className="text-[var(--tg-status-warning)] font-semibold">{minViolationFloor}%</span>
            </div>
            <input
              type="range"
              min="20"
              max="95"
              step="5"
              value={minViolationFloor}
              onChange={(e) => setMinViolationFloor(parseInt(e.target.value))}
              className="w-full accent-amber-500 cursor-pointer"
            />
            <p className="text-[11px] text-[var(--tg-text-muted)]">
              Guaranteed minimum risk rating applied whenever an explicit DFA protocol violation is detected.
            </p>
          </div>

          <div className="flex items-center justify-between pt-2">
            {savedSuccess ? (
              <span className="text-xs font-mono text-[var(--tg-accent-emerald)] font-semibold flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" />
                <span>Reference weights saved to browser</span>
              </span>
            ) : (
              <span />
            )}
            <button type="submit" className="tg-btn-primary text-xs">
              <Save className="w-3.5 h-3.5" />
              <span>Save Reference Weights</span>
            </button>
          </div>
        </form>
      </div>

      {/* Academic Environment Profile Card */}
      <div className="tg-panel p-5 space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-[var(--tg-border-subtle)]">
          <Shield className="w-4 h-4 text-[var(--tg-accent-emerald)]" />
          <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
            Academic Research Environment
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-[11px] font-mono text-[var(--tg-text-muted)] mb-1.5 uppercase">
              Demonstration Role
            </label>
            <input
              type="text"
              value="Theory of Computation Researcher"
              disabled
              className="tg-input text-xs font-mono opacity-80"
            />
          </div>
          <div>
            <label className="block text-[11px] font-mono text-[var(--tg-text-muted)] mb-1.5 uppercase">
              Runtime Mode
            </label>
            <input
              type="text"
              value="LOCAL_ACADEMIC (Auth-Free Sandbox)"
              disabled
              className="tg-input text-xs font-mono opacity-80"
            />
          </div>
        </div>

        <div className="pt-2 flex items-center justify-between text-xs font-mono text-[var(--tg-text-muted)]">
          <span>Active Workspace: default-workspace</span>
          <span className="tg-badge tg-badge-emerald">Academic Verified</span>
        </div>
      </div>
    </div>
  );
}

export default Settings;
