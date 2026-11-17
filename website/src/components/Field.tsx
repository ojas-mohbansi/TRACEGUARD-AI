import { AnimatePresence, motion } from 'motion/react'
import { AlertCircle, Check, ChevronDown } from 'lucide-react'
import { forwardRef, useId } from 'react'
import type { InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes } from 'react'

import { cx } from '../lib/cx'

/*
  Form primitives. `Field` owns the label, hint and error text and wires the
  ids (aria-describedby / aria-invalid) into whichever control it wraps via a
  render prop. Input, Textarea and Select share one look: a 52px dark well
  with a 1px ring that turns blue on focus and coral on error.
*/

export const controlClass =
  'w-full min-w-0 rounded-field bg-white/[0.05] px-4 text-[16px] text-white outline-none ring-1 ring-white/10 transition-[box-shadow,background-color] duration-200 placeholder:text-faint hover:ring-white/20 data-[force=hover]:ring-white/20 data-[force=focus]:ring-2 data-[force=focus]:ring-plasma-text data-[force=focus]:bg-white/[0.08] focus:bg-white/[0.08] focus:ring-2 focus:ring-plasma-text focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 aria-[invalid=true]:ring-danger aria-[invalid=true]:focus:ring-danger'

export type ControlProps = { id: string; 'aria-describedby'?: string; 'aria-invalid'?: boolean }

export function Field({
  label,
  hint,
  error,
  optional,
  children,
  className,
  labelAction,
}: {
  label: ReactNode
  hint?: ReactNode
  error?: string
  optional?: boolean
  children: (props: ControlProps) => ReactNode
  className?: string
  labelAction?: ReactNode
}) {
  const id = useId()
  const hintId = `${id}-hint`
  const errId = `${id}-err`
  const describedBy = [hint ? hintId : null, error ? errId : null].filter(Boolean).join(' ') || undefined
  return (
    <div className={cx('flex flex-col gap-2', className)}>
      <div className="flex items-baseline justify-between gap-3">
        <label htmlFor={id} className="text-[14px] font-medium text-soft">
          {label}
          {optional ? <span className="ml-1.5 font-normal text-faint">(optional)</span> : null}
        </label>
        {labelAction}
      </div>
      {children({ id, 'aria-describedby': describedBy, 'aria-invalid': error ? true : undefined })}
      {hint && !error ? (
        <p id={hintId} className="text-[13px] text-faint">
          {hint}
        </p>
      ) : null}
      <AnimatePresence initial={false}>
        {error ? (
          <motion.p
            key="err"
            id={errId}
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.18 }}
            className="flex items-center gap-1.5 text-[13px] text-danger"
          >
            <AlertCircle className="size-3.5 shrink-0" aria-hidden />
            {error}
          </motion.p>
        ) : null}
      </AnimatePresence>
    </div>
  )
}

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement> & { trailing?: ReactNode }>(function Input(
  { className, trailing, ...rest },
  ref,
) {
  if (!trailing) return <input ref={ref} className={cx(controlClass, 'h-[52px]', className)} {...rest} />
  return (
    <div className="relative">
      <input ref={ref} className={cx(controlClass, 'h-[52px] pr-12', className)} {...rest} />
      <div className="absolute inset-y-0 right-1.5 flex items-center">{trailing}</div>
    </div>
  )
})

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaHTMLAttributes<HTMLTextAreaElement>>(function Textarea({ className, ...rest }, ref) {
  return <textarea ref={ref} className={cx(controlClass, 'min-h-[140px] resize-y py-3.5 leading-relaxed', className)} {...rest} />
})

export const Select = forwardRef<HTMLSelectElement, SelectHTMLAttributes<HTMLSelectElement>>(function Select({ className, children, ...rest }, ref) {
  return (
    <div className="relative">
      <select ref={ref} className={cx(controlClass, 'h-[52px] cursor-pointer appearance-none pr-11 [&>option]:bg-surface-2', className)} {...rest}>
        {children}
      </select>
      <ChevronDown className="pointer-events-none absolute right-4 top-1/2 size-4 -translate-y-1/2 text-muted" aria-hidden />
    </div>
  )
})

/** A square checkbox with a plasma-blue fill and an animated tick. */
export function Checkbox({
  checked,
  onChange,
  children,
  error,
  disabled,
  className,
}: {
  checked: boolean
  onChange: (next: boolean) => void
  children: ReactNode
  error?: string
  disabled?: boolean
  className?: string
}) {
  const id = useId()
  return (
    <div className={cx('flex flex-col gap-1.5', className)}>
      <label htmlFor={id} className={cx('group flex cursor-pointer items-start gap-3 text-[14px] text-muted', disabled && 'cursor-not-allowed opacity-50')}>
        <span className="relative mt-[1px] grid size-5 shrink-0 place-items-center">
          <input
            id={id}
            type="checkbox"
            checked={checked}
            disabled={disabled}
            onChange={(e) => onChange(e.target.checked)}
            aria-invalid={error ? true : undefined}
            aria-describedby={error ? `${id}-err` : undefined}
            className="peer absolute inset-0 m-0 cursor-pointer appearance-none rounded-[6px] bg-white/[0.06] ring-1 ring-white/20 transition-colors checked:bg-plasma checked:ring-plasma group-hover:ring-white/35 aria-[invalid=true]:ring-danger disabled:cursor-not-allowed"
          />
          <motion.span initial={false} animate={{ scale: checked ? 1 : 0, opacity: checked ? 1 : 0 }} transition={{ type: 'spring', stiffness: 500, damping: 26 }} className="pointer-events-none relative">
            <Check className="size-3.5 text-white" strokeWidth={3} aria-hidden />
          </motion.span>
        </span>
        <span className="leading-snug">{children}</span>
      </label>
      {error ? (
        <p id={`${id}-err`} className="ml-8 flex items-center gap-1.5 text-[13px] text-danger">
          <AlertCircle className="size-3.5" aria-hidden />
          {error}
        </p>
      ) : null}
    </div>
  )
}
