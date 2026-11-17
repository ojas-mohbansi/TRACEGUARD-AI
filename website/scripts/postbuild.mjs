// Postbuild cleanup for Cloudflare Workers Static Assets.
// Ensures dist/client is clean without destroying Worker sourcemaps or .assetsignore.
import { readdirSync, rmSync, statSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

function clean(dir) {
  for (const name of readdirSync(dir)) {
    const path = join(dir, name)
    // Only strip OS junk like .DS_Store or Thumbs.db; preserve .assetsignore and sourcemaps
    if (name === '.DS_Store' || name === 'Thumbs.db') {
      rmSync(path, { recursive: true, force: true })
      continue
    }
    if (statSync(path).isDirectory()) clean(path)
  }
}

const clientDir = fileURLToPath(new URL('../dist/client', import.meta.url))
try {
  clean(clientDir)
} catch (e) {
  // directory might not exist yet
}


