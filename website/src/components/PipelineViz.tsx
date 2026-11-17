import { ArrowRight, Database, Eye, GitCommit, Layers, Radio, Shield, Sparkles } from 'lucide-react'
import { pipeline } from '../content'
import { cx } from '../lib/cx'

const icons = [Radio, Layers, Shield, GitCommit, Sparkles, Database, Shield, Eye]

export function PipelineViz({ className }: { className?: string }) {
  return (
    <div className={cx('flex flex-col gap-6', className)}>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {pipeline.stages.map((stage, idx) => {
          const Icon = icons[idx % icons.length]
          return (
            <div
              key={stage.step}
              className="group relative flex flex-col justify-between rounded-card border border-line bg-surface p-5 transition-all duration-300 hover:border-signal-border hover:bg-surface-2"
            >
              <div>
                <div className="flex items-center justify-between pb-3">
                  <span className="font-mono text-xs font-semibold text-signal-soft">{stage.step}</span>
                  <div className="grid size-8 place-items-center rounded-[10px] bg-white/[0.05] text-soft transition-colors group-hover:bg-signal-wash group-hover:text-signal-soft">
                    <Icon className="size-4" aria-hidden />
                  </div>
                </div>
                <h4 className="text-[16px] font-semibold text-white group-hover:text-signal-soft transition-colors">
                  {stage.name}
                </h4>
                <p className="mt-2 text-xs leading-relaxed text-muted group-hover:text-soft transition-colors">
                  {stage.desc}
                </p>
              </div>

              {idx < pipeline.stages.length - 1 && (
                <div className="mt-4 flex items-center gap-1.5 text-[11px] font-mono text-faint">
                  <span>Pass to 0{idx + 2}</span>
                  <ArrowRight className="size-3" aria-hidden />
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
