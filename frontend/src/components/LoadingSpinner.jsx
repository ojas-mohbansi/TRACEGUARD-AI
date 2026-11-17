import React from 'react';

export function LoadingSpinner({ size = 'md', text = 'Loading data...' }) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-2',
    lg: 'w-12 h-12 border-3',
  };

  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-3" role="status" aria-live="polite">
      <div
        className={`${sizeClasses[size] || sizeClasses.md} rounded-full border-t-transparent animate-spin`}
        style={{
          borderColor: 'var(--tg-border-default)',
          borderTopColor: 'var(--tg-accent-emerald)',
        }}
      />
      {text && <p className="text-xs font-mono text-[var(--tg-text-muted)]">{text}</p>}
      <span className="sr-only">{text}</span>
    </div>
  );
}

export default LoadingSpinner;
