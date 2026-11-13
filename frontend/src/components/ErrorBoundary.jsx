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
        <div className="p-8 my-4 rounded-xl border border-[#FF647C]/40 bg-[#101622] text-center">
          <div className="inline-flex p-3 rounded-full bg-[#FF647C]/10 text-[#FF647C] mb-3 border border-[#FF647C]/20">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <h2 className="text-base font-semibold text-[#EDF3FA]">Component Error</h2>
          <p className="mt-1 text-xs text-[#91A0B5] max-w-md mx-auto">
            {this.state.error?.message || 'Something went wrong while rendering this component.'}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-4 px-3 py-1.5 text-xs font-medium rounded-lg bg-[#161F2D] hover:bg-[#253247] text-[#EDF3FA] border border-[#253247] transition flex items-center space-x-1.5 mx-auto"
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
