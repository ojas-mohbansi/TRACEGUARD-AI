import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 my-4 rounded-xl border border-[var(--tg-status-danger)]/40 bg-[var(--tg-bg-surface)] text-center shadow-lg">
          <div className="inline-flex p-3 rounded-full bg-[var(--tg-status-danger-subtle)] text-[var(--tg-status-danger)] mb-3 border border-[var(--tg-status-danger)]/20">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <h2 className="text-base font-semibold text-[var(--tg-text-primary)]">Component Error</h2>
          <p className="mt-1 text-xs text-[var(--tg-text-muted)] max-w-md mx-auto">
            {this.state.error?.message || 'Something went wrong while rendering this component.'}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-4 px-3 py-1.5 text-xs font-medium rounded-lg bg-[var(--tg-bg-base)] hover:bg-[var(--tg-bg-hover)] text-[var(--tg-text-primary)] border border-[var(--tg-border-default)] transition flex items-center space-x-1.5 mx-auto focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--tg-status-danger)]"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Try Again</span>
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
