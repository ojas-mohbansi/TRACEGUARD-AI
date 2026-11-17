import { cx } from '../lib/cx'

export function LogoMark({ className, size = 28 }: { className?: string; size?: number }) {
  return (
    <img
      src="/brand/traceguard-ai-icon-color.svg"
      width={size}
      height={size}
      alt="TraceGuard AI Logo"
      className={cx('shrink-0 select-none object-contain rounded-md', className)}
    />
  )
}

export function Logo({ className, showIcon = true }: { className?: string; showIcon?: boolean }) {
  return (
    <span className={cx('inline-flex items-center gap-2.5 select-none', className)}>
      {showIcon && (
        <img
          src="/brand/traceguard-ai-icon-color.svg"
          width={28}
          height={28}
          alt=""
          aria-hidden
          className="shrink-0 object-contain rounded-md"
        />
      )}
      <img
        src="/brand/traceguard-ai-wordmark-color.svg"
        alt="TraceGuard AI"
        className="h-5 sm:h-5.5 w-auto max-w-[155px] object-contain shrink-0"
      />
    </span>
  )
}

