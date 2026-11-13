import React from 'react';

export function LoadingSpinner({ size = 'md', text = 'Loading data...' }) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  };

  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-3">
      <div
        className={`${sizeClasses[size] || sizeClasses.md} rounded-full border-t-transparent animate-spin`}
        style={{ borderColor: 'var(--border-color)', borderTopColor: 'var(--accent-primary)' }}
      />
      {text && <p className="text-xs font-mono text-[#91A0B5]">{text}</p>}
    </div>
  );
}

export default LoadingSpinner;
