// Salin core Python HambaLang (../hambalang) ke static/ supaya Pyodide di
// playground menjalankan kode yang sama persis dengan CLI.
import { mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync, copyFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, '..', '..', 'hambalang');
const dest = join(here, '..', 'static', 'hambalang');
// cli.py & __main__.py tidak dibutuhkan di browser.
const skip = new Set(['cli.py', '__main__.py']);

rmSync(dest, { recursive: true, force: true });
mkdirSync(dest, { recursive: true });

const files = readdirSync(src).filter((f) => f.endsWith('.py') && !skip.has(f)).sort();
for (const f of files) copyFileSync(join(src, f), join(dest, f));

const init = readFileSync(join(src, '__init__.py'), 'utf8');
const version = (init.match(/__version__ = "([^"]+)"/) || [, 'dev'])[1];
writeFileSync(join(dest, 'manifest.json'), JSON.stringify({ version, files }, null, 2));
console.log(`hambalang core ${version}: ${files.length} file disalin ke static/hambalang`);
