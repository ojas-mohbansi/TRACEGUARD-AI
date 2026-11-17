import { Hono } from 'hono'
import { hasErrors, validateContact, validateEmail } from '../lib/validate'

// The Worker in front of the static site.
type Env = {
  ASSETS: Fetcher
}

const app = new Hono<{ Bindings: Env }>()

async function body<T>(c: { req: { json: <U>() => Promise<U> } }): Promise<Partial<T> | null> {
  try {
    const v = await c.req.json<Partial<T>>()
    return v && typeof v === 'object' ? v : null
  } catch {
    return null
  }
}

app.get('/api/health', (c) => c.json({ ok: true, project: 'TraceGuard AI' }))

app.post('/api/contact', async (c) => {
  const v = await body<Record<string, string>>(c)
  if (!v) return c.json({ error: 'Send a JSON body.' }, 400)
  const errors = validateContact(v)
  if (hasErrors(errors)) return c.json({ error: 'Check the highlighted fields.', errors }, 422)
  return c.json({ ok: true, reference: `TG-${Date.now().toString(36).toUpperCase()}` })
})

app.post('/api/subscribe', async (c) => {
  const v = await body<{ email: string }>(c)
  if (!v) return c.json({ error: 'Send a JSON body.' }, 400)
  const err = validateEmail(v.email ?? '')
  if (err) return c.json({ error: err, errors: { email: err } }, 422)
  return c.json({ ok: true })
})

app.all('/api/*', (c) => c.json({ error: 'Not found' }, 404))

app.all('*', (c) => c.env.ASSETS.fetch(c.req.raw))

export default app
