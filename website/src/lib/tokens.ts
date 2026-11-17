/*
  The design tokens as data, for the style guide and inspector. Keep in step with the
  @theme block in src/styles.css (the CSS is the source of truth).
*/
export interface ColorToken {
  name: string
  hex: string
}

export interface ColorGroup {
  name: string
  colors: ColorToken[]
}

export interface TypeScaleToken {
  name: string
  cls: string
  size: string
}

export const colorGroups: ColorGroup[] = [
  {
    name: 'Surfaces',
    colors: [
      { name: 'bg', hex: '#000000' },
      { name: 'bg-deep', hex: '#030508' },
      { name: 'surface', hex: '#0a0d16' },
      { name: 'surface-2', hex: '#0e1420' },
      { name: 'raised', hex: '#141928' },
      { name: 'overlay', hex: '#1a2033' },
    ],
  },
  {
    name: 'Text',
    colors: [
      { name: 'fg', hex: '#ffffff' },
      { name: 'soft', hex: '#d6dae2' },
      { name: 'muted', hex: '#9ca3af' },
      { name: 'faint', hex: '#6b7280' },
    ],
  },
  {
    name: 'Signal (Blue / FSM / Protocol)',
    colors: [
      { name: 'signal', hex: '#3B82F6' },
      { name: 'signal-soft', hex: '#60a5fa' },
      { name: 'signal-dim', hex: '#1d4ed8' },
      { name: 'signal-wash', hex: 'rgb(59 130 246 / 0.12)' },
    ],
  },
  {
    name: 'Trace (Emerald / ML / Anomaly)',
    colors: [
      { name: 'trace', hex: '#10B981' },
      { name: 'trace-soft', hex: '#34d399' },
      { name: 'trace-dim', hex: '#059669' },
      { name: 'trace-wash', hex: 'rgb(16 185 129 / 0.10)' },
    ],
  },
  {
    name: 'Status (Threat / Warn / OK)',
    colors: [
      { name: 'threat', hex: '#ef4444' },
      { name: 'threat-soft', hex: '#f87171' },
      { name: 'warn', hex: '#f59e0b' },
      { name: 'warn-soft', hex: '#fbbf24' },
      { name: 'ok', hex: '#22c55e' },
      { name: 'ok-soft', hex: '#4ade80' },
    ],
  },
]

export const typeScale: TypeScaleToken[] = [
  { name: 'Display XL', cls: 'display text-[76px]', size: '76 / 1.02, 500, -0.035em' },
  { name: 'Display L', cls: 'display text-[56px]', size: '56 / 1.02, 500, -0.035em' },
  { name: 'Display M', cls: 'display text-[40px]', size: '40 / 1.02, 500, -0.035em' },
  { name: 'Title', cls: 'text-[24px] font-medium tracking-[-0.02em]', size: '24, 500' },
  { name: 'Card title', cls: 'text-[16px] font-medium', size: '16, 500' },
  { name: 'Lede', cls: 'text-[18px] leading-[1.55] text-muted', size: '18 / 1.55, 400' },
  { name: 'Body', cls: 'text-[16px] leading-[1.5] text-soft', size: '16 / 1.5, 400' },
  { name: 'Small', cls: 'text-[14px] text-muted', size: '14, 400' },
  { name: 'Caption', cls: 'text-[13px] text-faint', size: '13, 400' },
]

export const spacing = [4, 8, 12, 16, 20, 24, 32, 40, 56, 80, 128]

export const radii = [
  { name: 'field', px: 14 },
  { name: 'card-sm', px: 20 },
  { name: 'card', px: 28 },
  { name: 'panel', px: 32 },
  { name: 'control (pill)', px: 999 },
]

export const shadows = [
  { name: 'card', value: '0 40px 80px -30px rgb(0 0 0 / 0.85)', cls: 'shadow-card' },
  { name: 'glow-signal', value: '0 0 120px -10px rgb(59 130 246 / 0.35)', cls: 'shadow-glow-signal' },
  { name: 'glow-trace', value: '0 0 120px -10px rgb(16 185 129 / 0.30)', cls: 'shadow-glow-trace' },
  { name: 'glow-threat', value: '0 0 80px -10px rgb(239 68 68 / 0.30)', cls: 'shadow-glow-threat' },
  { name: 'depth edge', value: 'inset 1px line + 1px top highlight', cls: 'depth' },
]

export const motion = [
  { name: 'reveal', value: '0.8s cubic-bezier(0.22, 1, 0.36, 1), rise 18px', kind: 'reveal' as const },
  { name: 'pulse-signal', value: '4.8s ease-in-out infinite (protocol pulse)', kind: 'pulse-signal' as const },
  { name: 'pulse-trace', value: '6s ease-in-out infinite (anomaly pulse)', kind: 'pulse-trace' as const },
  { name: 'float', value: '8s ease-in-out infinite', kind: 'float' as const },
  { name: 'press', value: '200ms scale 0.97 on :active', kind: 'press' as const },
]
