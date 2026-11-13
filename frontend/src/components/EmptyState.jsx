import React from 'react';
import { AlertCircle, FolderOpen, RefreshCw } from 'lucide-react';

export function EmptyState({
  title = 'No Data Available',
  description = 'There are currently no records to display.',
  icon: Icon = FolderOpen,
  actionText = null,
  onAction = null,
}) {
  return (
    <div className="flex flex-col items-center justify-center p-10 text-center rounded-xl border border-[#253247]/60 bg-[#101622]/40 backdrop-blur">
      <div className="p-3 mb-3 rounded-full bg-[#161F2D] text-[#91A0B5] border border-[#253247]">
        <Icon className="w-6 h-6" />
      </div>
      <h3 className="text-sm font-semibold text-[#EDF3FA]">{title}</h3>
      <p className="mt-1 text-xs text-[#91A0B5] max-w-sm">{description}</p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="mt-4 px-3 py-1.5 text-xs font-medium rounded-lg bg-[#161F2D] hover:bg-[#253247] text-[#42D6B2] border border-[#42D6B2]/30 transition-all flex items-center space-x-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>{actionText}</span>
        </button>
      )}
    </div>
  );
}

export default EmptyState;
