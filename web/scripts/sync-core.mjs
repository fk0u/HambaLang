// Salin core Python HambaLang (../hambalang) ke static/ supaya Pyodide di
// playground menjalankan kode yang sama persis dengan CLI.
//
// Penyalinan dilakukan ke folder sementara lalu di-rename, jadi sync yang gagal
// di tengah jalan tidak pernah meninggalkan static/hambalang setengah jadi.
import { existsSync, mkdirSync, readdirSync, readFileSync, renameSync, rmSync, writeFileSync, copyFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, '..', '..', 'hambalang');
const dest = join(here, '..', 'static', 'hambalang');
const tmp = `${dest}.tmp-${process.pid}`;
// cli.py & __main__.py tidak dibutuhkan di browser.
const skip = new Set(['cli.py', '__main__.py']);

function fail(msg) {
	console.error(`sync-core: ${msg}`);
	process.exit(1);
}

const initPath = join(src, '__init__.py');
if (!existsSync(initPath)) fail(`paket Python tidak ditemukan di ${src} (clone repo lengkap, bukan hanya web/)`);

const match = readFileSync(initPath, 'utf8').match(/^__version__\s*=\s*["']([^"']+)["']/m);
if (!match) fail(`__version__ tidak ditemukan di ${initPath}`);
const version = match[1];

const files = readdirSync(src).filter((f) => f.endsWith('.py') && !skip.has(f)).sort();
if (files.length === 0) fail(`tidak ada file .py di ${src}`);

rmSync(tmp, { recursive: true, force: true });
mkdirSync(tmp, { recursive: true });
try {
	for (const f of files) copyFileSync(join(src, f), join(tmp, f));
	writeFileSync(join(tmp, 'manifest.json'), JSON.stringify({ version, files }, null, 2));
	rmSync(dest, { recursive: true, force: true });
	mkdirSync(dirname(dest), { recursive: true });
	renameSync(tmp, dest);
} catch (err) {
	rmSync(tmp, { recursive: true, force: true });
	fail(err.message);
}
console.log(`hambalang core ${version}: ${files.length} file disalin ke static/hambalang`);
