import { useCallback, useSyncExternalStore } from 'react'

/*
  Tiny localStorage-backed state. `useStored(key, fallback)` behaves like
  useState but survives reloads and syncs across components and tabs. Reads
  and writes are wrapped so a blocked storage (private mode) just falls back
  to memory.
*/

const PREFIX = 'traceguard:'
const EVENT = 'traceguard:store'
const memory = new Map<string, string>()
const cache = new Map<string, { raw: string | null; value: unknown }>()

function readRaw(key: string): string | null {
  try {
    return window.localStorage.getItem(PREFIX + key)
  } catch {
    return memory.get(key) ?? null
  }
}

function writeRaw(key: string, raw: string | null) {
  try {
    if (raw === null) window.localStorage.removeItem(PREFIX + key)
    else window.localStorage.setItem(PREFIX + key, raw)
  } catch {
    if (raw === null) memory.delete(key)
    else memory.set(key, raw)
  }
  window.dispatchEvent(new CustomEvent(EVENT, { detail: key }))
}

function read<T>(key: string, fallback: T): T {
  const raw = readRaw(key)
  const hit = cache.get(key)
  if (hit && hit.raw === raw) return hit.value as T
  let value: T = fallback
  if (raw !== null) {
    try {
      value = JSON.parse(raw) as T
    } catch {
      value = fallback
    }
  }
  cache.set(key, { raw, value })
  return value
}

function subscribe(cb: () => void) {
  window.addEventListener(EVENT, cb)
  window.addEventListener('storage', cb)
  return () => {
    window.removeEventListener(EVENT, cb)
    window.removeEventListener('storage', cb)
  }
}

export function useStored<T>(key: string, fallback: T): [T, (next: T | ((prev: T) => T)) => void, () => void] {
  const value = useSyncExternalStore(
    subscribe,
    () => read(key, fallback),
    () => fallback,
  )
  const set = useCallback(
    (next: T | ((prev: T) => T)) => {
      const prev = read(key, fallback)
      const v = typeof next === 'function' ? (next as (p: T) => T)(prev) : next
      writeRaw(key, JSON.stringify(v))
    },
    // fallback is a literal at every call site; the key identifies the slot.
    [key],
  )
  const clear = useCallback(() => writeRaw(key, null), [key])
  return [value, set, clear]
}

/** POST JSON to a Worker route. Resolves with field errors on 4xx. */
export async function postJson<T = { ok: true }>(
  url: string,
  data: unknown,
): Promise<{ ok: true; data: T } | { ok: false; error: string; errors?: Record<string, string> }> {
  try {
    const res = await fetch(url, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(data) })
    const json = (await res.json().catch(() => ({}))) as { error?: string; errors?: Record<string, string> }
    if (!res.ok) return { ok: false, error: json.error ?? 'Something went wrong. Try again.', errors: json.errors }
    return { ok: true, data: json as T }
  } catch {
    return { ok: false, error: 'You appear to be offline. Check your connection and try again.' }
  }
}
