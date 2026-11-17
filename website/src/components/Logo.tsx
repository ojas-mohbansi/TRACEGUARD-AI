import { cx } from '../lib/cx'

export function LogoMark({ className, size = 32 }: { className?: string; size?: number }) {
  return (
    <img
      src="/brand/traceguard-ai-icon-color.svg"
      width={size}
      height={size}
      alt="TraceGuard AI Logo"
      className={cx('shrink-0 select-none object-contain', className)}
    />
  )
}

export function Logo({
  className,
  size = 32,
  showBadge = false,
}: {
  className?: string
  size?: number
  showBadge?: boolean
}) {
  return (
    <span className={cx('inline-flex items-center gap-2.5 sm:gap-3 select-none group', className)}>
      <img
        src="/brand/traceguard-ai-icon-color.svg"
        width={size}
        height={size}
        alt="TraceGuard AI Icon"
        className="shrink-0 object-contain rounded-md shadow-xs transition-transform duration-200 group-hover:scale-105"
      />
      <img
        src="/brand/traceguard-ai-wordmark-color.svg"
        alt="TraceGuard AI"
        className="h-5 sm:h-5.5 w-auto max-w-[150px] sm:max-w-[175px] object-contain shrink-0"
      />
      {showBadge && (
        <span className="hidden xl:inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-medium tracking-wide bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          Academic NIDS
        </span>
      )}
    </span>
  )
}
