import { useState, useEffect } from 'react'
import { cx } from '../lib/cx'

export interface DFADiagramProps {
  animated?: boolean
  activeState?: string
  highlightPath?: string[]
  className?: string
  interactive?: boolean
  onSelectState?: (stateId: string) => void
}

interface StateNode {
  id: string
  label: string
  x: number
  y: number
  isInitial?: boolean
  isAccepting?: boolean
  isTrap?: boolean
  description: string
}

const NODES: StateNode[] = [
  { id: 'IDLE', label: 'IDLE', x: 65, y: 190, isInitial: true, description: 'Initial quiescent state awaiting client TCP handshake' },
  { id: 'CONNECTED', label: 'CONN', x: 165, y: 190, description: 'TCP established; awaiting HTTP request' },
  { id: 'REQUEST_RECEIVED', label: 'REQ_RCVD', x: 285, y: 125, description: 'HTTP request headers received; checking auth' },
  { id: 'AUTH_CHECKED', label: 'AUTH_OK', x: 420, y: 80, description: 'Authentication valid; preparing response' },
  { id: 'AUTH_FAILED', label: 'AUTH_FAIL', x: 420, y: 190, description: 'Authentication rejected; issuing 401/403' },
  { id: 'RESPONSE_SENT', label: 'RESP_SENT', x: 550, y: 140, description: 'HTTP response dispatched; stream active or closing' },
  { id: 'ERROR', label: 'ERROR', x: 420, y: 300, description: 'Malformed request or 500 internal error' },
  { id: 'CLOSED', label: 'CLOSED', x: 660, y: 190, isAccepting: true, description: 'Clean teardown; formal accepting state' },
  { id: 'TRAP', label: 'TRAP', x: 165, y: 320, isTrap: true, description: 'Dead sink state; absorbing all illegal transitions' },
]

interface Edge {
  from: string
  to: string
  symbol: string
  curvature?: number // -1 to 1 curve offset
}

const EDGES: Edge[] = [
  { from: 'IDLE', to: 'CONNECTED', symbol: 'CONNECT' },
  { from: 'CONNECTED', to: 'REQUEST_RECEIVED', symbol: 'REQUEST' },
  { from: 'CONNECTED', to: 'CLOSED', symbol: 'TIMEOUT', curvature: 0.35 },
  { from: 'REQUEST_RECEIVED', to: 'AUTH_CHECKED', symbol: 'AUTH_SUCCESS' },
  { from: 'REQUEST_RECEIVED', to: 'AUTH_FAILED', symbol: 'AUTH_FAILURE' },
  { from: 'REQUEST_RECEIVED', to: 'ERROR', symbol: 'MALFORMED', curvature: -0.15 },
  { from: 'AUTH_CHECKED', to: 'RESPONSE_SENT', symbol: '200 / 301' },
  { from: 'AUTH_CHECKED', to: 'ERROR', symbol: '500', curvature: 0.2 },
  { from: 'AUTH_FAILED', to: 'RESPONSE_SENT', symbol: '401 / 403' },
  { from: 'RESPONSE_SENT', to: 'REQUEST_RECEIVED', symbol: 'REQUEST (loop)', curvature: -0.35 },
  { from: 'RESPONSE_SENT', to: 'CLOSED', symbol: 'CLOSE' },
  { from: 'ERROR', to: 'CLOSED', symbol: 'CLOSE', curvature: 0.15 },
  { from: 'ERROR', to: 'RESPONSE_SENT', symbol: 'ERR_RESP', curvature: -0.1 },
]

export function DFADiagram({
  animated = true,
  activeState: controlledState,
  highlightPath,
  className,
  interactive = true,
  onSelectState,
}: DFADiagramProps) {
  const [selectedState, setSelectedState] = useState<string>(controlledState || 'IDLE')
  const [stepIndex, setStepIndex] = useState(0)

  // Canonical happy-path trace for animation
  const canonicalPath = ['IDLE', 'CONNECTED', 'REQUEST_RECEIVED', 'AUTH_CHECKED', 'RESPONSE_SENT', 'CLOSED']

  useEffect(() => {
    if (controlledState) {
      setSelectedState(controlledState)
    }
  }, [controlledState])

  useEffect(() => {
    if (!animated) return
    const timer = setInterval(() => {
      setStepIndex((prev) => (prev + 1) % canonicalPath.length)
    }, 1800)
    return () => clearInterval(timer)
  }, [animated, canonicalPath.length])

  const currentActive = controlledState || (animated ? canonicalPath[stepIndex] : selectedState)

  const handleNodeClick = (node: StateNode) => {
    if (!interactive) return
    setSelectedState(node.id)
    onSelectState?.(node.id)
  }

  const selectedNodeInfo = NODES.find((n) => n.id === selectedState)

  return (
    <div className={cx('relative flex flex-col rounded-card border border-line bg-surface/90 p-4 shadow-card backdrop-blur-xl', className)}>
      {/* Header bar / status indicator */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line pb-3 text-xs">
        <div className="flex items-center gap-2">
          <span className="round size-2 animate-ping rounded-full bg-signal" />
          <span className="font-mono font-medium text-white">HTTP DFA: M = (Q, Σ, δ, q₀, F)</span>
        </div>
        <div className="flex items-center gap-3 font-mono text-[11px] text-muted">
          <span className="inline-flex items-center gap-1">
            <span className="round size-2 rounded-full bg-signal" /> Valid Path
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="round size-2 rounded-full bg-trace" /> Accepting (F)
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="round size-2 rounded-full bg-threat" /> TRAP Sink
          </span>
        </div>
      </div>

      {/* SVG Canvas */}
      <div className="relative my-2 w-full overflow-hidden">
        <svg
          viewBox="0 0 740 380"
          className="h-auto w-full select-none"
          role="img"
          aria-label="Deterministic Finite Automaton state transition diagram"
        >
          <defs>
            {/* Markers for arrowheads */}
            <marker id="arrow-blue" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#3B82F6" />
            </marker>
            <marker id="arrow-active" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#60a5fa" />
            </marker>
            <marker id="arrow-gray" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
              <path d="M 0 2 L 6 5 L 0 8 z" fill="rgba(255,255,255,0.25)" />
            </marker>

            {/* Glowing filter */}
            <filter id="glow-node" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Initial state entry pointer */}
          <g>
            <line x1="15" y1="190" x2="40" y2="190" stroke="#3B82F6" strokeWidth="2.5" markerEnd="url(#arrow-blue)" />
            <text x="18" y="180" fill="#60a5fa" fontSize="10" fontFamily="monospace" fontWeight="600">START</text>
          </g>

          {/* Transition Edges */}
          {EDGES.map((edge, i) => {
            const fromNode = NODES.find((n) => n.id === edge.from)!
            const toNode = NODES.find((n) => n.id === edge.to)!

            let d = ''
            let midX = (fromNode.x + toNode.x) / 2
            let midY = (fromNode.y + toNode.y) / 2

            if (edge.curvature) {
              const dx = toNode.x - fromNode.x
              const dy = toNode.y - fromNode.y
              const normalX = -dy * edge.curvature
              const normalY = dx * edge.curvature
              const cx = midX + normalX
              const cy = midY + normalY
              d = `M ${fromNode.x} ${fromNode.y} Q ${cx} ${cy} ${toNode.x} ${toNode.y}`
              midX = (fromNode.x + 2 * cx + toNode.x) / 4
              midY = (fromNode.y + 2 * cy + toNode.y) / 4
            } else {
              d = `M ${fromNode.x} ${fromNode.y} L ${toNode.x} ${toNode.y}`
            }

            const isEdgeActive =
              (highlightPath && highlightPath.includes(edge.from) && highlightPath.includes(edge.to)) ||
              (currentActive === edge.to && canonicalPath.indexOf(edge.to) === canonicalPath.indexOf(edge.from) + 1)

            return (
              <g key={i} className="transition-opacity duration-300">
                <path
                  d={d}
                  fill="none"
                  stroke={isEdgeActive ? '#60a5fa' : 'rgba(255,255,255,0.18)'}
                  strokeWidth={isEdgeActive ? 2.5 : 1.2}
                  strokeDasharray={isEdgeActive ? 'none' : undefined}
                  markerEnd={isEdgeActive ? 'url(#arrow-active)' : 'url(#arrow-gray)'}
                />
                <rect
                  x={midX - 28}
                  y={midY - 8}
                  width="56"
                  height="16"
                  rx="4"
                  fill="#0a0d16"
                  stroke={isEdgeActive ? '#3B82F6' : 'rgba(255,255,255,0.08)'}
                  strokeWidth="0.8"
                />
                <text
                  x={midX}
                  y={midY + 3.5}
                  textAnchor="middle"
                  fill={isEdgeActive ? '#93c5fd' : '#9ca3af'}
                  fontSize="8"
                  fontFamily="monospace"
                  fontWeight={isEdgeActive ? '600' : '400'}
                >
                  {edge.symbol}
                </text>
              </g>
            )
          })}

          {/* TRAP State self-loops and undefined edge indication */}
          <path
            d="M 145 338 C 120 375, 120 320, 142 322"
            fill="none"
            stroke="#ef4444"
            strokeWidth="1.2"
            strokeDasharray="3 3"
            markerEnd="url(#arrow-gray)"
          />
          <text x="110" y="375" fill="#f87171" fontSize="8" fontFamily="monospace">
            ∀σ ∉ Valid: δ → TRAP
          </text>

          {/* State Nodes */}
          {NODES.map((node) => {
            const isActive = currentActive === node.id
            const isSelected = selectedState === node.id
            const nodeRadius = node.isAccepting ? 26 : 24

            let strokeColor = '#3B82F6'
            let fillColor = '#0e1420'
            let textColor = '#ffffff'

            if (node.isAccepting) {
              strokeColor = '#10B981'
              fillColor = '#062c1d'
              textColor = '#34d399'
            } else if (node.isTrap) {
              strokeColor = '#ef4444'
              fillColor = '#2b0909'
              textColor = '#f87171'
            }

            if (isActive) {
              strokeColor = node.isTrap ? '#ef4444' : node.isAccepting ? '#10B981' : '#60a5fa'
              fillColor = node.isTrap ? '#450a0a' : node.isAccepting ? '#064e3b' : '#1e3a5f'
            }

            return (
              <g
                key={node.id}
                transform={`translate(${node.x}, ${node.y})`}
                onClick={() => handleNodeClick(node)}
                className={cx('cursor-pointer transition-transform duration-200 hover:scale-105', isActive && 'scale-105')}
                role="button"
                tabIndex={0}
                aria-label={`State ${node.id}: ${node.description}`}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    handleNodeClick(node)
                  }
                }}
              >
                {/* Accepting state outer double ring */}
                {node.isAccepting && (
                  <circle
                    r={nodeRadius + 5}
                    fill="none"
                    stroke="#10B981"
                    strokeWidth="1.5"
                    strokeOpacity={isActive ? '0.9' : '0.5'}
                  />
                )}

                {/* Pulsing ring for active state */}
                {isActive && (
                  <circle
                    r={nodeRadius + 8}
                    fill="none"
                    stroke={strokeColor}
                    strokeWidth="1.5"
                    className="animate-ping opacity-35"
                  />
                )}

                {/* Main node circle */}
                <circle
                  r={nodeRadius}
                  fill={fillColor}
                  stroke={strokeColor}
                  strokeWidth={isActive || isSelected ? 2.5 : 1.5}
                  strokeDasharray={node.isTrap ? '4 2' : 'none'}
                  filter={isActive ? 'url(#glow-node)' : undefined}
                />

                {/* State Label */}
                <text
                  textAnchor="middle"
                  dy="3.5"
                  fill={textColor}
                  fontSize="9.5"
                  fontWeight="600"
                  fontFamily="monospace"
                >
                  {node.label}
                </text>
              </g>
            )
          })}
        </svg>
      </div>

      {/* Selected / Active State Inspector card */}
      {selectedNodeInfo && (
        <div className="mt-2 flex flex-col gap-1 rounded-[14px] border border-line bg-surface-2 p-3 text-xs">
          <div className="flex items-center justify-between">
            <span className="font-mono font-semibold text-white">
              State: <span className="text-signal-soft">{selectedNodeInfo.id}</span>
            </span>
            <span
              className={cx(
                'rounded-control px-2 py-0.5 font-mono text-[10px] font-semibold uppercase',
                selectedNodeInfo.isAccepting
                  ? 'bg-trace-wash text-trace-soft border border-trace-border'
                  : selectedNodeInfo.isTrap
                  ? 'bg-threat-wash text-threat-soft border border-threat-border'
                  : 'bg-signal-wash text-signal-soft border border-signal-border',
              )}
            >
              {selectedNodeInfo.isAccepting ? 'Accepting (F)' : selectedNodeInfo.isTrap ? 'Absorbing Sink' : 'Operational'}
            </span>
          </div>
          <p className="text-soft">{selectedNodeInfo.description}</p>
        </div>
      )}
    </div>
  )
}
