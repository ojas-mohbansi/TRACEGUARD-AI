import { Shield, Sparkles, AlertTriangle } from 'lucide-react'
import { cx } from '../lib/cx'

export function HybridFormula({ className }: { className?: string }) {
  return (
    <div className={cx('flex flex-col gap-5 rounded-card border border-line bg-surface p-6 shadow-card', className)}>
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line pb-4">
        <div>
          <span className="font-mono text-xs uppercase tracking-wider text-signal-soft">Consensus Engine</span>
          <h4 className="text-[18px] font-semibold text-white">Hybrid Risk Scoring Formula</h4>
        </div>
        <span className="rounded-control border border-signal-border bg-signal-wash px-3 py-1 font-mono text-xs font-medium text-signal-soft">
          Tier 3 Consensus
        </span>
      </div>

      {/* Main mathematical block */}
      <div className="flex flex-col items-center justify-center rounded-[18px] border border-line-mid bg-surface-2 p-5 text-center font-mono">
        <div className="text-[14px] text-muted">Combined Session Risk Index</div>
        <div className="my-2 text-[22px] font-bold text-white sm:text-[26px]">
          <span className="text-white">S</span>
          <span className="text-xs text-signal-soft">h</span>
          <span className="text-faint"> = </span>
          <span className="text-signal-soft">(0.6 × S</span>
          <span className="text-xs text-signal-soft">FSM</span>
          <span className="text-signal-soft">)</span>
          <span className="text-faint"> + </span>
          <span className="text-trace-soft">(0.4 × S</span>
          <span className="text-xs text-trace-soft">ML</span>
          <span className="text-trace-soft">)</span>
        </div>
        <div className="mt-1 flex flex-wrap items-center justify-center gap-4 text-xs text-soft">
          <span className="inline-flex items-center gap-1.5">
            <span className="round size-2 rounded-full bg-signal" />
            S_FSM ∈ [0, 100] (Protocol Violation Score)
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="round size-2 rounded-full bg-trace" />
            S_ML ∈ [0, 100] (Normalized Anomaly × 100)
          </span>
        </div>
      </div>

      {/* Violation Floor Rule Callout */}
      <div className="flex items-start gap-3 rounded-[16px] border border-threat-border bg-threat-wash p-4">
        <AlertTriangle className="mt-0.5 size-5 shrink-0 text-threat-soft" aria-hidden />
        <div className="flex flex-col gap-0.5 text-xs">
          <span className="font-mono font-semibold text-threat-soft">Deterministic Safety Floor Rule:</span>
          <p className="text-soft font-mono">
            if (fsm_violation == true) {'{'} S_h = max(S_h, 60.0) {'}'}
          </p>
          <p className="mt-1 text-soft">
            Guarantees that any formal DFA grammar breach is flagged with at least <strong>High Severity</strong>, even if statistical ML score is minimal.
          </p>
        </div>
      </div>

      {/* Weights breakdown */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div className="flex flex-col gap-1 rounded-[14px] border border-line bg-surface-2 p-3.5">
          <div className="flex items-center gap-2">
            <Shield className="size-4 text-signal-soft" />
            <span className="font-medium text-white text-sm">60% FSM Weight</span>
          </div>
          <p className="text-xs text-muted">
            Strict, unyielding priority for deterministic HTTP protocol sequencing.
          </p>
        </div>
        <div className="flex flex-col gap-1 rounded-[14px] border border-line bg-surface-2 p-3.5">
          <div className="flex items-center gap-2">
            <Sparkles className="size-4 text-trace-soft" />
            <span className="font-medium text-white text-sm">40% ML Weight</span>
          </div>
          <p className="text-xs text-muted">
            Unsupervised Isolation Forest evaluation over 15 behavioral & temporal dimensions.
          </p>
        </div>
      </div>
    </div>
  )
}
