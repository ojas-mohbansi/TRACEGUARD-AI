import React from 'react';
import { FolderOpen, RefreshCw } from 'lucide-react';

export function EmptyState({
  title = 'No Data Available',
  description = 'There are currently no records to display.',
  icon: Icon = FolderOpen,
  actionText = null,
  onAction = null,
}) {
  return (
    <div className="flex flex-col items-center justify-center p-10 text-center rounded-xl border border-[var(--tg-border-subtle)] bg-[var(--tg-bg-surface)]/60 backdrop-blur-sm">
      <div className="p-3 mb-3 rounded-full bg-[var(--tg-bg-base)] text-[var(--tg-text-muted)] border border-[var(--tg-border-subtle)] shadow-xs">
        <Icon className="w-6 h-6" />
      </div>
      <h3 className="text-sm font-semibold text-[var(--tg-text-primary)]">{title}</h3>
      <p className="mt-1 text-xs text-[var(--tg-text-muted)] max-w-sm">{description}</p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="mt-4 px-3 py-1.5 text-xs font-medium rounded-lg bg-[var(--tg-bg-surface)] hover:bg-[var(--tg-bg-hover)] text-[var(--tg-accent-emerald)] border border-[var(--tg-accent-emerald)]/30 transition-all flex items-center space-x-1.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--tg-accent-emerald)]"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>{actionText}</span>
        </button>
      )}
    </div>
  );
}

export default EmptyState;
