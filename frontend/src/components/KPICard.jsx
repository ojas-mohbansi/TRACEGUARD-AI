import React from 'react';

const VARIANT_CONFIG = {
  default: {
    badgeBg: 'bg-[var(--tg-bg-canvas)]',
    badgeText: 'text-[var(--tg-text-secondary)]',
    borderColor: 'border-[var(--tg-border-subtle)]',
    iconColor: 'text-[var(--tg-status-info)]',
  },
  info: {
    badgeBg: 'bg-[var(--tg-status-info-subtle)]',
    badgeText: 'text-[var(--tg-status-info)]',
    borderColor: 'border-[var(--tg-status-info)]/20',
    iconColor: 'text-[var(--tg-status-info)]',
  },
  warning: {
    badgeBg: 'bg-[var(--tg-status-warning-subtle)]',
    badgeText: 'text-[var(--tg-status-warning)]',
    borderColor: 'border-[var(--tg-status-warning)]/20',
    iconColor: 'text-[var(--tg-status-warning)]',
  },
  danger: {
    badgeBg: 'bg-[var(--tg-status-danger-subtle)]',
    badgeText: 'text-[var(--tg-status-danger)]',
    borderColor: 'border-[var(--tg-status-danger)]/20',
    iconColor: 'text-[var(--tg-status-danger)]',
  },
  success: {
    badgeBg: 'bg-[var(--tg-accent-emerald-subtle)]',
    badgeText: 'text-[var(--tg-accent-emerald)]',
    borderColor: 'border-[var(--tg-accent-emerald)]/20',
    iconColor: 'text-[var(--tg-accent-emerald)]',
  },
};

export function KPICard({
  title,
  value,
  unit,
  icon: Icon,
  variant = 'default',
  subtitle,
  loading = false,
}) {
  const config = VARIANT_CONFIG[variant] || VARIANT_CONFIG.default;

  return (
    <div className="tg-panel p-4 flex flex-col justify-between transition-transform duration-150 ease-out hover:-translate-y-0.5">
      <div className="flex items-center justify-between gap-2">
        <span className="text-[11px] font-mono uppercase tracking-wider text-[var(--tg-text-muted)] truncate">
          {title}
        </span>
        {Icon && (
          <div className={`p-1.5 rounded-md ${config.badgeBg} ${config.iconColor}`}>
            <Icon className="w-3.5 h-3.5" />
          </div>
        )}
      </div>

      <div className="mt-3">
        {loading ? (
          <div className="h-7 w-20 bg-[var(--tg-bg-canvas)] animate-pulse rounded" />
        ) : (
          <div className="flex items-baseline gap-1 font-mono">
            <span className="text-2xl font-semibold tracking-tight text-[var(--tg-text-primary)]">
              {value}
            </span>
            {unit && (
              <span className="text-xs text-[var(--tg-text-muted)] font-medium">
                {unit}
              </span>
            )}
          </div>
        )}
        {subtitle && (
          <p className="mt-1 text-[11px] text-[var(--tg-text-muted)] truncate">
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
}

export default KPICard;
