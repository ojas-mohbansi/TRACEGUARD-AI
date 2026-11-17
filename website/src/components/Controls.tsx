import { motion } from 'motion/react'
import { AlertCircle, Bookmark, Check, CheckCircle2, ChevronRight, Info, SearchX } from 'lucide-react'
import { useId } from 'react'
import type { ReactNode } from 'react'

import { cx } from '../lib/cx'
import { Link } from '../lib/router'
import type { ForceState } from './Button'

/* ---------- Badge ---------- */

const badgeTones = {
  neutral: 'bg-white/[0.08] text-soft',
  signal: 'bg-signal-wash text-signal-soft border border-signal-border',
  trace: 'bg-trace-wash text-trace-soft border border-trace-border',
  threat: 'bg-threat-wash text-threat-soft border border-threat-border',
  warn: 'bg-warn-wash text-warn-soft border border-warn-border',
  ok: 'bg-ok-wash text-ok-soft border border-ok-border',
  // Backward compatibility aliases
  plasma: 'bg-signal-wash text-signal-soft border border-signal-border',
  fire: 'bg-threat-wash text-threat-soft border border-threat-border',
  success: 'bg-ok-wash text-ok-soft border border-ok-border',
}

export function Badge({
  children,
  tone = 'neutral',
  className,
  pulse,
}: {
  children: ReactNode
  tone?: keyof typeof badgeTones
  className?: string
  pulse?: boolean
}) {
  return (
    <span className={cx('inline-flex min-h-7 py-1 items-center gap-2 rounded-control px-3 text-xs sm:text-[13px] font-medium leading-tight text-balance', badgeTones[tone], className)}>
      {pulse ? (
        <span className="relative flex size-2 shrink-0" aria-hidden>
          <span className="round absolute inset-0 animate-ping rounded-full bg-current opacity-60" />
          <span className="round relative size-2 rounded-full bg-current" />
        </span>
      ) : null}
      {children}
    </span>
  )
}

/* ---------- Chip (filter toggle) ---------- */

export function Chip({
  selected,
  onClick,
  children,
  count,
  force,
  disabled,
}: {
  selected: boolean
  onClick: () => void
  children: ReactNode
  count?: number
  force?: ForceState
  disabled?: boolean
}) {
  return (
    <button
      type="button"
      aria-pressed={selected}
      onClick={onClick}
      disabled={disabled}
      data-force={force}
      className={cx(
        'inline-flex h-10 items-center gap-2 rounded-control px-4 text-[14px] font-medium transition-colors duration-200 focus-visible:outline-2 data-[force=focus]:outline-2 data-[force=focus]:outline-offset-3 data-[force=focus]:outline-signal-soft disabled:opacity-45 active:scale-[0.97] data-[force=pressed]:scale-[0.97]',
        selected
          ? 'bg-white text-black'
          : 'bg-white/[0.06] text-soft ring-1 ring-inset ring-white/10 hover:bg-white/[0.11] hover:text-white data-[force=hover]:bg-white/[0.11] data-[force=hover]:text-white',
      )}
    >
      {children}
      {count !== undefined ? <span className={cx('text-[13px] tabular-nums', selected ? 'text-black/60' : 'text-faint')}>{count}</span> : null}
    </button>
  )
}

/* ---------- Save toggle (bookmark) ---------- */

export function SaveToggle({ saved, onToggle, label, force }: { saved: boolean; onToggle: () => void; label: string; force?: ForceState }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-pressed={saved}
      aria-label={saved ? `Remove ${label} from saved items` : `Save ${label}`}
      data-force={force}
      className={cx(
        'relative z-10 grid size-11 shrink-0 place-items-center rounded-[14px] transition-colors focus-visible:outline-2 data-[force=focus]:outline-2 data-[force=focus]:outline-offset-3 data-[force=focus]:outline-signal-soft active:scale-95',
        saved ? 'bg-signal-wash text-signal-soft border border-signal-border' : 'bg-white/[0.06] text-muted hover:bg-white/[0.12] hover:text-white data-[force=hover]:bg-white/[0.12] data-[force=hover]:text-white',
      )}
    >
      <Bookmark className="size-[18px]" fill={saved ? 'currentColor' : 'none'} aria-hidden />
    </button>
  )
}

/* ---------- Notice ---------- */

const noticeTones = {
  info: { cls: 'bg-signal-wash text-soft border border-signal-border', icon: Info, iconCls: 'text-signal-soft' },
  success: { cls: 'bg-ok-wash text-[#c9f4dd] border border-ok-border', icon: CheckCircle2, iconCls: 'text-ok-soft' },
  error: { cls: 'bg-threat-wash text-[#ffd8d1] border border-threat-border', icon: AlertCircle, iconCls: 'text-threat-soft' },
  warn: { cls: 'bg-warn-wash text-[#fef3c7] border border-warn-border', icon: AlertCircle, iconCls: 'text-warn-soft' },
}

/** Inline message box. `role` is status for info/success and alert for errors. */
export function Notice({ tone = 'info', title, children, className }: { tone?: keyof typeof noticeTones; title?: ReactNode; children?: ReactNode; className?: string }) {
  const t = noticeTones[tone]
  const Icon = t.icon
  return (
    <motion.div
      initial={{ opacity: 0, y: -4 }}
      animate={{ opacity: 1, y: 0 }}
      role={tone === 'error' ? 'alert' : 'status'}
      className={cx('depth relative flex gap-3 rounded-[18px] px-4 py-3.5 text-[14px] leading-relaxed', t.cls, className)}
    >
      <Icon className={cx('mt-[3px] size-4 shrink-0', t.iconCls)} aria-hidden />
      <div>
        {title ? <div className="font-medium text-white">{title}</div> : null}
        {children}
      </div>
    </motion.div>
  )
}

/* ---------- Empty state ---------- */

export function EmptyState({ title, body, action, className }: { title: string; body: ReactNode; action?: ReactNode; className?: string }) {
  return (
    <div className={cx('depth relative flex flex-col items-center gap-3 rounded-card bg-surface px-6 py-14 text-center', className)}>
      <span className="grid size-12 place-items-center rounded-[16px] bg-white/[0.06] text-muted">
        <SearchX className="size-5" aria-hidden />
      </span>
      <h3 className="text-[17px] font-medium text-white">{title}</h3>
      <p className="max-w-[360px] text-[15px] text-muted">{body}</p>
      {action}
    </div>
  )
}

/* ---------- Link row (item list) ---------- */

export function LinkRow({ href, title, body, force, className }: { href: string; title: string; body: string; force?: ForceState; className?: string }) {
  return (
    <Link
      href={href}
      data-force={force}
      className={cx(
        'group flex items-center gap-6 border-t border-line py-5 transition-colors focus-visible:outline-2 focus-visible:outline-offset-0 data-[force=focus]:outline-2 data-[force=focus]:outline-signal-soft',
        className,
      )}
    >
      <span className="flex min-w-0 flex-1 flex-col gap-1">
        <span className="text-[16px] font-medium text-white">{title}</span>
        <span className="text-pretty text-[15px] leading-snug text-muted transition-colors group-hover:text-soft group-data-[force=hover]:text-soft">{body}</span>
      </span>
      <ChevronRight
        className="size-5 shrink-0 text-faint transition-transform duration-200 group-hover:translate-x-1 group-hover:text-white group-data-[force=hover]:translate-x-1"
        aria-hidden
      />
    </Link>
  )
}

/* ---------- Choice card (radio group of big options) ---------- */

export function ChoiceGroup<T extends string>({
  legend,
  options,
  value,
  onChange,
  error,
  columns = 3,
}: {
  legend: string
  options: Array<{ id: T; label: string; hint?: string }>
  value: T | ''
  onChange: (v: T) => void
  error?: string
  columns?: 2 | 3 | 4
}) {
  const id = useId()
  return (
    <fieldset aria-describedby={error ? `${id}-err` : undefined} aria-invalid={error ? true : undefined}>
      <legend className="mb-2 text-[14px] font-medium text-soft">{legend}</legend>
      <div className={cx('grid gap-2.5', columns === 2 ? 'sm:grid-cols-2' : columns === 4 ? 'sm:grid-cols-2 lg:grid-cols-4' : 'sm:grid-cols-3')}>
        {options.map((o) => {
          const checked = value === o.id
          return (
            <label
              key={o.id}
              className={cx(
                'relative flex min-h-[56px] cursor-pointer flex-col justify-center gap-0.5 rounded-[18px] px-4 py-3 ring-1 ring-inset transition-[background-color,box-shadow] has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-signal-soft',
                checked ? 'bg-signal-wash ring-2 ring-signal-soft' : 'bg-white/[0.04] ring-white/10 hover:bg-white/[0.07] hover:ring-white/20',
                error && !checked && 'ring-threat/70',
              )}
            >
              <input type="radio" name={id} value={o.id} checked={checked} onChange={() => onChange(o.id)} className="sr-only" />
              <span className="flex items-center justify-between gap-2 text-[15px] font-medium text-white">
                {o.label}
                <span className={cx('round grid size-5 place-items-center rounded-full ring-1 transition-colors', checked ? 'bg-signal-soft text-black ring-signal-soft' : 'ring-white/25')}>
                  {checked ? <Check className="size-3" strokeWidth={3} aria-hidden /> : null}
                </span>
              </span>
              {o.hint ? <span className="text-[13px] text-muted">{o.hint}</span> : null}
            </label>
          )
        })}
      </div>
      {error ? (
        <p id={`${id}-err`} className="mt-2 flex items-center gap-1.5 text-[13px] text-threat-soft">
          <AlertCircle className="size-3.5" aria-hidden />
          {error}
        </p>
      ) : null}
    </fieldset>
  )
}

/* ---------- Stepper ---------- */

export function Stepper({ steps, current }: { steps: string[]; current: number }) {
  return (
    <ol className="flex items-center gap-2" aria-label="Progress">
      {steps.map((s, i) => {
        const state = i < current ? 'done' : i === current ? 'current' : 'todo'
        return (
          <li key={s} className="flex flex-1 flex-col gap-2" aria-current={state === 'current' ? 'step' : undefined}>
            <span className={cx('h-1 rounded-full transition-colors duration-500', state === 'todo' ? 'bg-white/10' : 'bg-signal-soft')} />
            <span className={cx('text-[13px]', state === 'todo' ? 'text-faint' : 'text-soft')}>
              <span className="sr-only">{state === 'done' ? 'Completed: ' : state === 'current' ? 'Current: ' : 'Next: '}</span>
              {s}
            </span>
          </li>
        )
      })}
    </ol>
  )
}

/* ---------- Slider ---------- */

export function Slider({
  label,
  value,
  min,
  max,
  step = 1,
  onChange,
  format = (n) => String(n),
  disabled,
}: {
  label: ReactNode
  value: number
  min: number
  max: number
  step?: number
  onChange: (n: number) => void
  format?: (n: number) => ReactNode
  disabled?: boolean
}) {
  const id = useId()
  const fill = ((value - min) / (max - min)) * 100
  return (
    <div className={cx('flex flex-col', disabled && 'opacity-50')}>
      <div className="flex items-baseline justify-between gap-4">
        <label htmlFor={id} className="text-[14px] text-muted">
          {label}
        </label>
        <output htmlFor={id} className="text-[20px] font-medium tabular-nums tracking-[-0.02em] text-white">
          {format(value)}
        </output>
      </div>
      <input
        id={id}
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(Number(e.target.value))}
        className="range mt-1 w-full disabled:cursor-not-allowed"
        style={{ ['--fill' as string]: `${fill}%` }}
      />
    </div>
  )
}

/* ---------- Spinner / skeleton ---------- */

export function Skeleton({ className }: { className?: string }) {
  return <div className={cx('skeleton rounded-[12px]', className)} aria-hidden />
}

/* ---------- Check list and success mark ---------- */

export function CheckList({ items, className }: { items: string[]; className?: string }) {
  return (
    <ul className={cx('flex flex-col gap-3', className)}>
      {items.map((it) => (
        <li key={it} className="flex items-start gap-3 text-[16px] text-soft">
          <span className="round mt-0.5 grid size-5 shrink-0 place-items-center rounded-full bg-signal-wash text-signal-soft border border-signal-border">
            <Check className="size-3" strokeWidth={3} aria-hidden />
          </span>
          {it}
        </li>
      ))}
    </ul>
  )
}

export function SuccessMark() {
  return (
    <span className="round grid size-12 place-items-center rounded-full bg-ok-wash text-ok-soft border border-ok-border">
      <Check className="size-6" aria-hidden />
    </span>
  )
}
