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
  Cpu,
  Layers
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
  fsm: '#10B981',      // Official Brand Emerald
  ml: '#3B82F6',       // Official Brand Blue
  hybrid: '#8B5CF6',   // Purple Consensus
  unknown: '#64748B',  // Slate
};

export function Dashboard() {
  const [timeRange, setTimeRange] = React.useState('all');
  const [engineActivity, setEngineActivity] = React.useState(null);

  const { data: summary, loading, error, refetch } = useApi(
    () => api.getDashboardSummary(timeRange),
    [timeRange]
  );

  React.useEffect(() => {
    api.getEngineActivity(timeRange)
      .then(res => setEngineActivity(res))
      .catch(err => console.warn('Could not load engine activity:', err));
  }, [timeRange]);

  useWebSocket('stats_update', (newStats) => {
    if (newStats) {
      refetch();
      api.getEngineActivity(timeRange)
        .then(res => setEngineActivity(res))
        .catch(() => {});
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

  const engineDistribution = summary?.engine_distribution || { fsm: 0, ml: 0, hybrid: 0, unknown: 0 };
  const totalEngineAlerts = (engineDistribution.fsm || 0) + (engineDistribution.ml || 0) + (engineDistribution.hybrid || 0) + (engineDistribution.unknown || 0);

  const pieData = [
    {
      name: 'FSM Engine',
      key: 'fsm',
      value: engineDistribution.fsm || 0,
      color: ENGINE_COLORS.fsm,
      desc: 'RFC 7231 Deterministic Invariants'
    },
    {
      name: 'ML Engine',
      key: 'ml',
      value: engineDistribution.ml || 0,
      color: ENGINE_COLORS.ml,
      desc: 'Isolation Forest Outliers'
    },
    {
      name: 'Hybrid Consensus',
      key: 'hybrid',
      value: engineDistribution.hybrid || 0,
      color: ENGINE_COLORS.hybrid,
      desc: 'Synthesized Consensus (S_h)'
    },
    ...(engineDistribution.unknown > 0 ? [{
      name: 'Unknown / Legacy',
      key: 'unknown',
      value: engineDistribution.unknown,
      color: ENGINE_COLORS.unknown,
      desc: 'Historical records without provenance'
    }] : [])
  ];

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
        <div className="flex flex-wrap items-center gap-2">
          {/* Time Range Filter Pills */}
          <div className="flex items-center p-0.5 rounded-lg bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] text-[11px] font-mono">
            {[
              { id: 'all', label: 'All Time' },
              { id: '24h', label: '24 Hours' },
              { id: '7d', label: '7 Days' },
              { id: '30d', label: '30 Days' },
            ].map((t) => (
              <button
                key={t.id}
                onClick={() => setTimeRange(t.id)}
                className={`px-2 py-1 rounded-md transition ${
                  timeRange === t.id
                    ? 'bg-[var(--tg-bg-surface)] text-[var(--tg-accent-emerald)] font-semibold border border-emerald-500/20 shadow-xs'
                    : 'text-[var(--tg-text-muted)] hover:text-[var(--tg-text-primary)]'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          <button
            onClick={refetch}
            className="tg-btn-secondary text-xs"
            aria-label="Sync Telemetry"
          >
            <RefreshCw className="w-3.5 h-3.5 text-[var(--tg-accent-emerald)]" />
            <span>Sync</span>
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
                <TrendingUp className="w-4 h-4 text-[var(--tg-accent-emerald)]" />
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
                      <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.28} />
                      <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--tg-border-subtle)" />
                  <XAxis
                    dataKey="hour"
                    stroke="var(--tg-text-muted)"
                    fontSize={10}
                    tickLine={false}
                    tickFormatter={(val) => val.split(' ')[1] || val}
                  />
                  <YAxis stroke="var(--tg-text-muted)" fontSize={10} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--tg-bg-surface)',
                      borderColor: 'var(--tg-border-default)',
                      borderRadius: '8px',
                      fontSize: '11px',
                      fontFamily: 'JetBrains Mono',
                      color: 'var(--tg-text-primary)',
                      boxShadow: 'var(--tg-shadow-md)',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="count"
                    stroke="#3B82F6"
                    strokeWidth={2}
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
              <Cpu className="w-4 h-4 text-[var(--tg-accent-blue)]" />
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
                    cy="45%"
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} stroke="transparent" />
                    ))}
                  </Pie>
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload;
                        const pct = totalEngineAlerts > 0 ? ((data.value / totalEngineAlerts) * 100).toFixed(1) : '0.0';
                        return (
                          <div className="tg-panel p-2.5 font-mono text-xs space-y-1 shadow-lg border border-[var(--tg-border-default)]">
                            <div className="flex items-center gap-2 font-semibold" style={{ color: data.color }}>
                              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: data.color }} />
                              <span>{data.name}</span>
                            </div>
                            <div className="text-[11px] text-[var(--tg-text-primary)]">
                              Count: <strong>{data.value.toLocaleString()}</strong> ({pct}%)
                            </div>
                            <div className="text-[10px] text-[var(--tg-text-muted)]">
                              {data.desc}
                            </div>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Legend
                    wrapperStyle={{ fontSize: '10px', fontFamily: 'JetBrains Mono', bottom: 0 }}
                    formatter={(val, entry) => {
                      const item = pieData.find((d) => d.name === val);
                      const pct = totalEngineAlerts > 0 && item ? ((item.value / totalEngineAlerts) * 100).toFixed(0) : '0';
                      return (
                        <span className="text-[var(--tg-text-secondary)]">
                          {val}: <strong className="text-[var(--tg-text-primary)]">{item?.value || 0}</strong> ({pct}%)
                        </span>
                      );
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-xs font-mono text-[var(--tg-text-muted)] flex flex-col items-center gap-1.5">
                <Cpu className="w-6 h-6 opacity-40" />
                <span>No engine classification data for this period</span>
              </div>
            )}
          </div>
          <div className="pt-2.5 border-t border-[var(--tg-border-subtle)] text-[10px] font-mono text-[var(--tg-text-muted)] flex items-center justify-between">
            <span>Total Categorized: <strong className="text-[var(--tg-text-primary)]">{totalEngineAlerts}</strong></span>
            <span>Formula: S_h = 0.6·FSM + 0.4·ML</span>
          </div>
        </div>
      </div>

      {/* Engine Contribution & Detection Activity (Overlapping Detection Analytics) */}
      <div className="tg-panel p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-[var(--tg-accent-emerald)]" />
              <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-[var(--tg-text-primary)]">
                Detection Engine Activity & Contribution Proof
              </h2>
            </div>
            <p className="text-[11px] text-[var(--tg-text-muted)] mt-0.5">
              Independent evaluation and detection metrics across deterministic rules, statistical learning, and consensus
            </p>
          </div>
          <div className="px-2.5 py-1 rounded bg-[var(--tg-bg-base)] border border-[var(--tg-border-subtle)] text-[10px] font-mono text-[var(--tg-text-muted)]">
            Overlapping Detection Metric (Non-Mutually Exclusive)
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* FSM Engine Activity */}
          <div className="p-4 rounded-xl border border-cyan-500/30 bg-cyan-500/5 space-y-3 font-mono">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
                <span className="text-xs font-bold text-[var(--tg-text-primary)]">FSM Engine</span>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold">
                DETERMINISTIC
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 pt-1 border-t border-cyan-500/20">
              <div>
                <div className="text-[10px] text-[var(--tg-text-muted)]">VIOLATIONS</div>
                <div className="text-xl font-bold text-cyan-400">
                  {engineActivity?.engine_activity?.fsm?.detections ?? (pieData.find(d => d.key === 'fsm')?.value || 0)}
                </div>
              </div>
              <div>
                <div className="text-[10px] text-[var(--tg-text-muted)]">EVALUATED</div>
                <div className="text-xl font-bold text-[var(--tg-text-primary)]">
                  {engineActivity?.engine_activity?.fsm?.evaluations ?? totalEngineAlerts}
                </div>
              </div>
            </div>
            <div className="text-[10px] text-[var(--tg-text-secondary)] space-y-1 pt-1 border-t border-cyan-500/10">
              <div><strong>Model:</strong> 9-State HTTP DFA (|Q|=9, |Σ|=13, |δ|=117)</div>
              <div><strong>Invariant:</strong> 60% Minimum Hybrid Risk Floor Enforced</div>
            </div>
          </div>

          {/* ML Engine Activity */}
          <div className="p-4 rounded-xl border border-blue-500/30 bg-blue-500/5 space-y-3 font-mono">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-400" />
                <span className="text-xs font-bold text-[var(--tg-text-primary)]">ML Engine</span>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/40 font-bold">
                STATISTICAL
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 pt-1 border-t border-blue-500/20">
              <div>
                <div className="text-[10px] text-[var(--tg-text-muted)]">OUTLIERS</div>
                <div className="text-xl font-bold text-blue-400">
                  {engineActivity?.engine_activity?.ml?.detections ?? (pieData.find(d => d.key === 'ml')?.value || 0)}
                </div>
              </div>
              <div>
                <div className="text-[10px] text-[var(--tg-text-muted)]">EVALUATED</div>
                <div className="text-xl font-bold text-[var(--tg-text-primary)]">
                  {engineActivity?.engine_activity?.ml?.evaluations ?? totalEngineAlerts}
                </div>
              </div>
            </div>
            <div className="text-[10px] text-[var(--tg-text-secondary)] space-y-1 pt-1 border-t border-blue-500/10">
              <div><strong>Model:</strong> Isolation Forest (100 Trees, 15 Features)</div>
              <div><strong>Threshold:</strong> S_ML ≥ 0.55 Anomaly Decision Boundary</div>
            </div>
          </div>

          {/* Hybrid Consensus Activity */}
          <div className="p-4 rounded-xl border border-purple-500/30 bg-purple-500/5 space-y-3 font-mono">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-purple-400" />
                <span className="text-xs font-bold text-[var(--tg-text-primary)]">Hybrid Engine</span>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/40 font-bold">
                SYNTHESIZED
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 pt-1 border-t border-purple-500/20">
              <div>
                <div className="text-[10px] text-[var(--tg-text-muted)]">CONSENSUS</div>
                <div className="text-xl font-bold text-purple-400">
                  {engineActivity?.engine_activity?.hybrid?.detections ?? (pieData.find(d => d.key === 'hybrid')?.value || 0)}
                </div>
              </div>
              <div>
                <div className="text-[10px] text-[var(--tg-text-muted)]">EVALUATED</div>
                <div className="text-xl font-bold text-[var(--tg-text-primary)]">
                  {engineActivity?.engine_activity?.hybrid?.evaluations ?? totalEngineAlerts}
                </div>
              </div>
            </div>
            <div className="text-[10px] text-[var(--tg-text-secondary)] space-y-1 pt-1 border-t border-purple-500/10">
              <div><strong>Formula:</strong> S_h = 0.6·S_FSM + 0.4·S_ML</div>
              <div><strong>Consensus:</strong> Dual-Engine Co-occurrence Detection</div>
            </div>
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
            className="text-xs font-mono font-medium text-[var(--tg-accent-emerald)] hover:text-emerald-700 flex items-center gap-1 transition"
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
                    <td className="font-mono text-xs text-[var(--tg-accent-blue)] font-medium">
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
                        className="text-xs font-mono text-[var(--tg-text-muted)] hover:text-[var(--tg-accent-emerald)] inline-flex items-center gap-1 transition"
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
