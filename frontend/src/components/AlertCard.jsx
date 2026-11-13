import React from 'react';
import { ShieldAlert, Cpu, Sparkles, Binary } from 'lucide-react';

const ENGINE_CONFIG = {
  fsm: { label: 'FSM Engine', icon: Binary, color: 'text-emerald-400' },
  ml: { label: 'ML Engine', icon: Cpu, color: 'text-blue-400' },
  hybrid: { label: 'Hybrid Consensus', icon: Sparkles, color: 'text-amber-400' },
};

export function AlertCard({ alert, isSelected = false, onClick = null }) {
  const engineInfo = ENGINE_CONFIG[alert.engine?.toLowerCase()] || {
    label: alert.engine?.toUpperCase() || 'ENGINE',
    icon: ShieldAlert,
    color: 'text-[var(--tg-text-secondary)]',
  };
  const EngineIcon = engineInfo.icon;

  const getSeverityBadgeClass = (sev) => {
    switch (sev?.toLowerCase()) {
      case 'critical':
      case 'high':
        return 'tg-badge-red';
      case 'medium':
        return 'tg-badge-amber';
      default:
        return 'tg-badge-emerald';
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status?.toLowerCase()) {
      case 'new':
        return 'tg-badge-blue';
      case 'investigating':
        return 'tg-badge-amber';
      case 'resolved':
        return 'tg-badge-emerald';
      default:
        return 'tg-badge-neutral';
    }
  };

  return (
    <div
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick && onClick(); } }}
      className={`p-3.5 rounded-lg border transition-all cursor-pointer relative ${
        isSelected
          ? 'bg-[var(--tg-bg-elevated)] border-emerald-500 shadow-sm'
          : 'bg-[var(--tg-bg-surface)] border-[var(--tg-border-subtle)] hover:border-[var(--tg-border-default)] hover:bg-[var(--tg-bg-hover)]'
      }`}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded-md bg-white/5 border border-white/10">
            <EngineIcon className={`w-3.5 h-3.5 ${engineInfo.color}`} />
          </div>
          <span className="font-mono text-xs font-semibold text-[var(--tg-text-primary)] uppercase tracking-wide">
            {engineInfo.label}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className={`tg-badge ${getSeverityBadgeClass(alert.severity)}`}>
            {alert.severity}
          </span>
          <span className={`tg-badge ${getStatusBadgeClass(alert.status)}`}>
            {alert.status}
          </span>
        </div>
      </div>

      <div className="mt-2.5 space-y-1">
        <div className="flex items-center justify-between text-xs font-mono">
          <span className="text-[var(--tg-text-muted)]">Session:</span>
          <span className="text-blue-400 font-medium truncate max-w-[150px]">
            {alert.session_id}
          </span>
        </div>
        <div className="flex items-center justify-between text-xs font-mono">
          <span className="text-[var(--tg-text-muted)]">Risk Factor:</span>
          <span className="text-[var(--tg-text-primary)] font-semibold">
            {(alert.risk_score * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      {alert.summary && (
        <p className="mt-2 text-[11px] text-[var(--tg-text-secondary)] line-clamp-2 leading-relaxed">
          {alert.summary}
        </p>
      )}

      <div className="mt-2.5 pt-2 border-t border-[var(--tg-border-subtle)] flex items-center justify-between text-[10px] font-mono text-[var(--tg-text-muted)]">
        <span>{alert.alert_id}</span>
        <span>{alert.timestamp ? new Date(alert.timestamp).toLocaleTimeString() : '—'}</span>
      </div>
    </div>
  );
}

export default AlertCard;
