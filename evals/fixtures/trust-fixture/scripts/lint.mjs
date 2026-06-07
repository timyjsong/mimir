// Minimal lint gate: syntax-check every JS file in src/ and test/.
import { readdirSync, existsSync } from 'node:fs'
import { execFileSync } from 'node:child_process'

const files = []
for (const dir of ['src', 'test']) {
  if (!existsSync(dir)) continue
  for (const f of readdirSync(dir)) if (f.endsWith('.js')) files.push(`${dir}/${f}`)
}
for (const f of files) execFileSync('node', ['--check', f], { stdio: 'inherit' })
console.log(`lint OK (${files.length} file(s))`)
