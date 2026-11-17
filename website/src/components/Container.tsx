import type { ReactNode } from 'react'

import { cx } from '../lib/cx'

export function Container({ children, className, size = 'lg' }: { children: ReactNode; className?: string; size?: 'md' | 'lg' | 'xl' }) {
  const max = size === 'md' ? 'max-w-[880px]' : size === 'xl' ? 'max-w-[1320px]' : 'max-w-[1200px]'
  return <div className={cx('mx-auto w-full px-5 sm:px-8', max, className)}>{children}</div>
}
