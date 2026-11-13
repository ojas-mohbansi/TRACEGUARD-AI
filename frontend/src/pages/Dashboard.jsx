import React from 'react';
import {
  Activity,
  Users,
  AlertTriangle,
  Flame,
  ShieldCheck,
  Clock,
  RefreshCw,
  ExternalLink,
  ChevronRight,
  TrendingUp,
  Cpu
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useApi } from '../hooks/useApi';
import { useWebSocket } from '../hooks/useWebSocket';
import KPICard from '../components/KPICard';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';

const ENGINE_COLORS = {
  fsm: '#10B981',
  ml: '#3B82F6',
  hybrid: '#F59E0B',
};

export function Dashboard() {
  const { data: summary, loading, error, refetch } = useApi(() => api.getDashboardSummary());

  useWebSocket('stats_update', (newStats) => {
    if (newStats) {
      refetch();
    }
  });

  if (loading && !summary) {
    return <LoadingSpinner text="Retrieving telemetry..." />;
  }

  if (error && !summary) {
    return (
      <EmptyState
        title="Could Not Connect to Backend API"
        description={error}
        icon={AlertTriangle}
        actionText="Retry Connection"
        onAction={refetch}
      />
    );
  }

  const kpis = [
    {
      title: 'Total Events',
      value: summary?.total_events?.toLocaleString() || 0,
      icon: Activity,
      variant: 'default',
      subtitle: 'Ingested protocol stream',
    },
    {
      title: 'Active Sessions',
      value: summary?.active_sessions?.toLocaleString() || 0,
      icon: Users,
      variant: 'info',
      subtitle: 'Concurrently tracked',
    },
    {
      title: 'Suspicious Sessions',
      value: summary?.suspicious_sessions?.toLocaleString() || 0,
      icon: AlertTriangle,
      variant: 'warning',
      subtitle: 'Flagged anomalies',
    },
    {
      title: 'Critical Alerts',
      value: summary?.critical_alerts?.toLocaleString() || 0,
      icon: Flame,
      variant: 'danger',
      subtitle: 'High severity flags',
    },
    {
      title: 'Detection Accuracy',
      value: summary?.detection_rate !== undefined ? `${(summary.detection_rate * 100).toFixed(1)}` : '0.0',
      unit: '%',
      icon: ShieldCheck,
      variant: 'success',
      subtitle: 'Hybrid consensus',
    },
    {
      title: 'Mean Inspection Latency',
      value: summary?.avg_processing_time_ms !== undefined ? summary.avg_processing_time_ms.toFixed(2) : '0.00',
      unit: 'ms',
      icon: Clock,
      variant: 'default',
      subtitle: 'Single event parse',
    },
  ];

  const engineDistribution = summary?.engine_distribution || { fsm: 0, ml: 0, hybrid: 0 };
  const pieData = Object.entries(engineDistribution).map(([name, count]) => ({
    name: name.toUpperCase(),
    value: count,
    color: ENGINE_COLORS[name.toLowerCase()] || '#10B981',
  }));

  const eventsByHour = summary?.events_by_hour || [];
  const recentThreats = summary?.recent_threats || [];

  return (
    <div className="space-y-6">
      {/* Editorial Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--tg-border-subtle)]">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <h1 className="text-lg font-semibold tracking-tight text-[var(--tg-text-primary)]">
              Operational Overview
            </h1>
          </div>
          <p className="text-xs text-[var(--tg-text-muted)] mt-1">
            Real-time telemetry, multi-engine detection consensus, and protocol compliance.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={refetch}
            className="tg-btn-secondary text-xs"
            aria-label="Refresh telemetry"
          >
            <RefreshCw className="w-3.5 h-3.5 text-emerald-400" />
            <span>Sync Telemetry</span>
          </button>
        </div>
      </div>

      {/* Rhythmic Metric Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
        {kpis.map((kpi, idx) => (
          <KPICard
            key={idx}
            title={kpi.title}
            value={kpi.value}
            unit={kpi.unit}
            icon={kpi.icon}
            variant={kpi.variant}
            subtitle={kpi.subtitle}
            loading={loading}
          />
        ))}
      </div>

      {/* Observability Visualizations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Timeline AreaChart */}
        <div className="lg:col-span-2 tg-panel p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-400" />
                <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
                  Event Throughput Timeline
                </h2>
              </div>
              <p className="text-[11px] text-[var(--tg-text-muted)] mt-0.5">
                Hourly protocol events ingested across tracked network interfaces
              </p>
            </div>
          </div>
          <div className="h-64 w-full">
            {eventsByHour.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={eventsByHour} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="eventGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10B981" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis
                    dataKey="hour"
                    stroke="#8896AB"
                    fontSize={10}
                    tickLine={false}
                    tickFormatter={(val) => val.split(' ')[1] || val}
                  />
                  <YAxis stroke="#8896AB" fontSize={10} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#141B2B',
                      borderColor: 'rgba(255,255,255,0.1)',
                      borderRadius: '6px',
                      fontSize: '11px',
                      fontFamily: 'JetBrains Mono',
                      color: '#F8FAFC',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="count"
                    stroke="#10B981"
                    strokeWidth={1.5}
                    fillOpacity={1}
                    fill="url(#eventGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs font-mono text-[var(--tg-text-muted)]">
                No timeline records available
              </div>
            )}
          </div>
        </div>

        {/* Engine Distribution Donut */}
        <div className="tg-panel p-5 flex flex-col justify-between">
          <div className="mb-2">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-blue-400" />
              <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
                Engine Classification Share
              </h2>
            </div>
            <p className="text-[11px] text-[var(--tg-text-muted)] mt-0.5">
              Breakdown of alerts generated by detector archetype
            </p>
          </div>
          <div className="h-56 w-full flex items-center justify-center">
            {pieData.some((d) => d.value > 0) ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} stroke="transparent" />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#141B2B',
                      borderColor: 'rgba(255,255,255,0.1)',
                      borderRadius: '6px',
                      fontSize: '11px',
                      fontFamily: 'JetBrains Mono',
                      color: '#F8FAFC',
                    }}
                  />
                  <Legend
                    wrapperStyle={{ fontSize: '11px', fontFamily: 'JetBrains Mono' }}
                    formatter={(val) => <span className="text-[var(--tg-text-secondary)]">{val}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-xs font-mono text-[var(--tg-text-muted)]">
                No engine distribution data
              </div>
            )}
          </div>
          <div className="pt-3 border-t border-[var(--tg-border-subtle)] text-[11px] text-[var(--tg-text-muted)] flex justify-between">
            <span>FSM: Deterministic Invariants</span>
            <span>ML: Isolation Forest</span>
          </div>
        </div>
      </div>

      {/* Recent Alerts Feed Table */}
      <div className="tg-panel p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
              Recent Protocol Violations & Threats
            </h2>
            <p className="text-[11px] text-[var(--tg-text-muted)] mt-0.5">
              High-priority events flagged during active session tracking
            </p>
          </div>
          <Link
            to="/threats"
            className="text-xs font-mono font-medium text-emerald-400 hover:text-emerald-300 flex items-center gap-1 transition"
          >
            <span>View All Alerts</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="tg-table-container">
          <table className="tg-table">
            <thead>
              <tr>
                <th>Alert Identifier</th>
                <th>Target Session</th>
                <th>Timestamp</th>
                <th>Severity</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {recentThreats.length > 0 ? (
                recentThreats.map((threat, idx) => (
                  <tr key={idx}>
                    <td className="font-mono text-xs text-[var(--tg-text-primary)]">
                      {threat.alert_id}
                    </td>
                    <td className="font-mono text-xs text-blue-400">
                      {threat.session_id}
                    </td>
                    <td className="font-mono text-xs text-[var(--tg-text-muted)]">
                      {new Date(threat.timestamp).toLocaleString()}
                    </td>
                    <td>
                      <span
                        className={`tg-badge ${
                          threat.severity?.toLowerCase() === 'high' || threat.severity?.toLowerCase() === 'critical'
                            ? 'tg-badge-red'
                            : threat.severity?.toLowerCase() === 'medium'
                            ? 'tg-badge-amber'
                            : 'tg-badge-blue'
                        }`}
                      >
                        {threat.severity}
                      </span>
                    </td>
                    <td>
                      <Link
                        to={`/threats`}
                        className="text-xs font-mono text-[var(--tg-text-muted)] hover:text-emerald-400 inline-flex items-center gap-1 transition"
                      >
                        <span>Investigate</span>
                        <ExternalLink className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="text-center py-8 text-xs text-[var(--tg-text-muted)]">
                    No active threat records in the current observation window.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
