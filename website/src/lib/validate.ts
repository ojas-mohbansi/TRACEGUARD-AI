// Validation shared by the forms and the Worker, so both give the same answer.

export const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/

export const TOPICS = ['research', 'automaton', 'collaboration', 'general'] as const

type Errors<T> = Partial<Record<keyof T, string>>

export function validateEmail(email: string): string | undefined {
  if (!email.trim()) return 'Enter your email address.'
  if (!EMAIL_RE.test(email.trim())) return 'Enter a valid email address.'
  return undefined
}

function validateName(name: string): string | undefined {
  const n = name.trim()
  if (n.length < 2) return 'Enter your full name.'
  if (n.length > 80) return 'Keep your name under 80 characters.'
  return undefined
}

export type ContactInput = { name: string; email: string; topic: string; message: string }

export function validateContact(v: Partial<ContactInput>): Errors<ContactInput> {
  const e: Errors<ContactInput> = {}
  const name = validateName(v.name ?? '')
  if (name) e.name = name
  const email = validateEmail(v.email ?? '')
  if (email) e.email = email
  const msg = (v.message ?? '').trim()
  if (msg.length < 10) e.message = `Write at least 10 characters (${msg.length} so far).`
  else if (msg.length > 2000) e.message = 'Keep your message under 2,000 characters.'
  return e
}

export function hasErrors(e: object) {
  return Object.keys(e).length > 0
}
