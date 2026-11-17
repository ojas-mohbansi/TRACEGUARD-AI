import React from 'react';
import LoadingSpinner from './LoadingSpinner';
import EmptyState from './EmptyState';
import { ArrowRight } from 'lucide-react';

export function EventTable({ events = [], loading = false, onRowClick = null, highlightId = null }) {
  if (loading && (!events || events.length === 0)) {
    return <LoadingSpinner text="Fetching network events..." />;
  }

  if (!events || events.length === 0) {
    return <EmptyState title="No Events Recorded" description="Network event streams will appear here as packets and requests are simulated." />;
  }

  return (
    <div className="tg-table-container">
      <table className="tg-table">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Event Type</th>
            <th>Session ID</th>
            <th>Source &rarr; Destination</th>
            <th>HTTP Details</th>
            <th>Payload</th>
            <th>Classification</th>
          </tr>
        </thead>
        <tbody>
          {events.map((evt) => {
            const isAnomalous = evt.label === 'anomalous';
            const isHighlighted = highlightId && evt.event_id === highlightId;

            return (
              <tr
                key={evt.event_id || `${evt.session_id}-${evt.timestamp}`}
                onClick={() => onRowClick && onRowClick(evt)}
                className={`transition-colors ${
                  isHighlighted ? 'bg-[var(--tg-accent-emerald-subtle)] border-l-2 border-[var(--tg-accent-emerald)]' : ''
                } ${onRowClick ? 'cursor-pointer hover:bg-[var(--tg-bg-hover)]' : ''}`}
              >
                <td className="font-mono text-xs text-[var(--tg-text-muted)] whitespace-nowrap">
                  {evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString() : '—'}
                </td>
                <td>
                  <span className="tg-badge tg-badge-blue">
                    {evt.event_type}
                  </span>
                </td>
                <td className="font-mono text-xs text-[var(--tg-text-secondary)] truncate max-w-[130px]" title={evt.session_id}>
                  {evt.session_id}
                </td>
                <td className="font-mono text-xs whitespace-nowrap">
                  <span className="text-[var(--tg-text-muted)]">{evt.source || '0.0.0.0'}</span>
                  <span className="sr-only"> to </span>
                  <ArrowRight className="inline-block w-3 h-3 text-[var(--tg-accent-emerald)] mx-1.5" aria-hidden="true" />
                  <span className="text-[var(--tg-text-primary)]">{evt.destination || '0.0.0.0'}</span>
                </td>
                <td className="font-mono text-xs whitespace-nowrap">
                  {evt.method && (
                    <span className="mr-1.5 px-1.5 py-0.5 rounded bg-[var(--tg-bg-canvas)] border border-[var(--tg-border-subtle)] text-[var(--tg-text-primary)] font-semibold text-[10px]">
                      {evt.method}
                    </span>
                  )}
                  {evt.status_code ? (
                    <span
                      className={`text-[11px] font-semibold ${
                        evt.status_code >= 400
                          ? 'text-[var(--tg-status-danger)]'
                          : evt.status_code >= 300
                          ? 'text-[var(--tg-status-warning)]'
                          : 'text-[var(--tg-accent-emerald)]'
                      }`}
                    >
                      {evt.status_code}
                    </span>
                  ) : null}
                  {evt.uri && (
                    <span className="ml-1 text-[var(--tg-text-muted)] truncate max-w-[140px] inline-block align-bottom" title={evt.uri}>
                      {evt.uri}
                    </span>
                  )}
                </td>
                <td className="font-mono text-xs text-[var(--tg-text-muted)] whitespace-nowrap">
                  {evt.bytes !== undefined ? `${evt.bytes.toLocaleString()} B` : '—'}
                </td>
                <td>
                  {isAnomalous ? (
                    <span className="tg-badge tg-badge-red">
                      Anomalous
                    </span>
                  ) : (
                    <span className="tg-badge tg-badge-emerald">
                      Compliant
                    </span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default EventTable;
