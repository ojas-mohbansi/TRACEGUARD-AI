import React from 'react';

const VARIANT_CONFIG = {
  default: {
    badgeBg: 'bg-white/5',
    badgeText: 'text-[var(--tg-text-secondary)]',
    borderColor: 'border-[var(--tg-border-subtle)]',
    iconColor: 'text-emerald-400',
  },
  info: {
    badgeBg: 'bg-blue-500/10',
    badgeText: 'text-blue-400',
    borderColor: 'border-blue-500/20',
    iconColor: 'text-blue-400',
  },
  warning: {
    badgeBg: 'bg-amber-500/10',
    badgeText: 'text-amber-400',
    borderColor: 'border-amber-500/20',
    iconColor: 'text-amber-400',
  },
  danger: {
    badgeBg: 'bg-rose-500/10',
    badgeText: 'text-rose-400',
    borderColor: 'border-rose-500/20',
    iconColor: 'text-rose-400',
  },
  success: {
    badgeBg: 'bg-emerald-500/10',
    badgeText: 'text-emerald-400',
    borderColor: 'border-emerald-500/20',
    iconColor: 'text-emerald-400',
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
    <div className="tg-panel p-4 flex flex-col justify-between transition-all hover:-translate-y-0.5">
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
          <div className="h-7 w-20 bg-white/5 animate-pulse rounded" />
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
