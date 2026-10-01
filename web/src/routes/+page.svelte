<script>
	import { onMount } from 'svelte';
	import { base } from '$app/paths';

	const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/';

	// Contoh program. Semua dijalankan oleh core HambaLang yang sama dengan CLI
	// (paket Python `hambalang/`, disalin ke static/ oleh scripts/sync-core.mjs).
	const EXAMPLES = {
		demo: `// HambaLang — demo fitur inti
lapor "=== MEGA PROYEK HAMBALANG ==="

nama = "Hambalang"
tahun = 2011
lapor "Proyek: " + nama + " (" + tahun + ")"

kontraktor = ["PT Adhi", "PT Waskita", "PT Wijaya"]
lapor "Jumlah kontraktor: " + panjang(kontraktor)

fungsi hitungPajak(nominal, persen)
    kembalikan nominal * persen / 100
akhir

lapor "Pajak 10%: " + rupiah(hitungPajak(anggaran, 10))

jika anggaran > 500000000
    lapor "✅ Dana mencukupi"
atau
    lapor "⚠️ Dana kurang"
akhir

untuk i dari 1 sampai 3
    lapor "Tingkat " + i + " - Disetujui"
akhir

lapor "\\n[SATIRE] Simulasi Korupsi..."
Korupsi(25)
Mangkrak(1500)
selesai()`,
		algoritma: `// Rekursi, higher-order function, objek
fungsi fib(n)
    jika n < 2
        kembalikan n
    akhir
    kembalikan fib(n - 1) + fib(n - 2)
akhir

lapor petakan(rentang(10), fib)

fungsi mahal(p)
    kembalikan p.anggaran > 1000000000
akhir

proyek = [
    {nama: "Hambalang", anggaran: 2500000000},
    {nama: "Pos Ronda", anggaran: 15000000},
    {nama: "Tol Langit", anggaran: 9000000000}
]

untuk p dalam saring(proyek, mahal)
    lapor p.nama + " -> " + rupiah(p.anggaran)
akhir`,
		error: `// Exception handling ala birokrasi
fungsi cairkanDana(jumlah)
    jika jumlah > anggaran
        Mangkrak "Dana tidak cukup, proyek mangkrak"
    akhir
    anggaran -= jumlah
    kembalikan anggaran
akhir

coba
    lapor "Sisa: " + rupiah(cairkanDana(400000000))
    lapor "Sisa: " + rupiah(cairkanDana(900000000))
jikaGagal e
    lapor "⚠️ Ditangkap: " + e
akhirCoba

coba
    x = [1, 2, 3][10]
jikaGagal e
    lapor "⚠️ " + e
akhirCoba`,
		formal: `// Dialek formal v5 (sesuai docs/Grammar.ebnf)
Rapat
    Wacana "Kalkulator pelicin anggaran"
    Anggaran dana = 1000
    Anggaran putaran = 0

    BagiRata potong(x) {
        kembalikan x - x / 10
    }

    Proyek dana > 500 {
        Anggaran dana = Janji potong(dana)
        Anggaran putaran = putaran + 1
    }

    Sita putaran > 5 {
        Korupsi "Butuh " + putaran + " rapat. Birokrasi sehat."
    } Pengadilan {
        Korupsi "Cepat sekali, pasti ada orang dalam."
    }
Bubarkan`
	};

	let selectedExample = 'demo';
	let code = EXAMPLES.demo;
	let engine = 'interpreter';
	let seed = '';
	let output = '';
	let isRunning = false;
	let pyodide = null;
	let pyodideStatus = 'Loading...';

	const GLUE = `
import sys, js
from hambalang import HambaError, Runtime, execute

def run_hambalang(code, engine, seed):
    out = []
    rt = Runtime(
        seed=None if seed == "" else int(seed),
        sandbox=True,
        step_limit=200_000,
        output=out.append,
        input_fn=lambda prompt: (js.prompt(prompt) or ""),
    )
    status = "ok"
    try:
        execute(code, rt, engine)
    except HambaError as e:
        status = "error"
        out.append("")
        out.append(f"❌ {e.jenis}" + (f" (baris {e.line})" if e.line else "") + f": {e.message}")
    out.append("")
    out.append(f"— {rt.steps:,} langkah · anggaran akhir Rp {rt.state['anggaran']:,} —".replace(",", "."))
    return status + "\\n" + "\\n".join(out)
`;

	onMount(async () => {
		try {
			pyodideStatus = 'Loading Pyodide...';
			const pyodideModule = await import(/* @vite-ignore */ `${PYODIDE_URL}pyodide.mjs`);
			pyodide = await pyodideModule.loadPyodide({ indexURL: PYODIDE_URL });

			pyodideStatus = 'Loading HambaLang core...';
			const manifest = await (await fetch(`${base}/hambalang/manifest.json`)).json();
			pyodide.FS.mkdirTree('/lib/hambalang');
			for (const file of manifest.files) {
				const src = await (await fetch(`${base}/hambalang/${file}`)).text();
				pyodide.FS.writeFile(`/lib/hambalang/${file}`, src);
			}
			await pyodide.runPythonAsync(`import sys\nsys.path.insert(0, "/lib")\n${GLUE}`);
			pyodideStatus = `Ready (HambaLang ${manifest.version})`;
		} catch (error) {
			pyodideStatus = 'Error loading runtime';
			output = `❌ Error: ${error.message}`;
		}
	});

	async function runCode() {
		if (!pyodide || !pyodideStatus.startsWith('Ready')) {
			output = '⚠️ Runtime belum siap. Tunggu sebentar...';
			return;
		}
		if (seed !== '' && !/^-?\d+$/.test(seed)) {
			output = '⚠️ Seed harus bilangan bulat (atau kosong untuk acak).';
			return;
		}

		isRunning = true;
		const label = engine === 'vm' ? 'HambaVM v4 (bytecode)' : 'Interpreter';
		output = `🏗️ Menjalankan dengan ${label}...\n${'='.repeat(50)}\n\n`;

		try {
			pyodide.globals.set('_code', code);
			pyodide.globals.set('_engine', engine);
			pyodide.globals.set('_seed', seed);
			const result = await pyodide.runPythonAsync('run_hambalang(_code, _engine, _seed)');
			const [status, ...rest] = result.split('\n');
			output += rest.join('\n');
			if (status === 'ok') output += '\n✅ Eksekusi selesai';
		} catch (error) {
			output += `\n\n❌ Error internal: ${error.message}`;
		} finally {
			isRunning = false;
		}
	}

	function loadExample() {
		code = EXAMPLES[selectedExample];
	}

	function handleKeydown(event) {
		if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
			event.preventDefault();
			runCode();
		}
	}
</script>

<svelte:head>
	<title>HambaLang Playground</title>
	<meta name="description" content="Satir Proyek Hambalang dalam bentuk bahasa pemrograman" />
</svelte:head>

<main>
	<header>
		<h1>🏗️ HambaLang</h1>
		<p class="subtitle">Bahasa pemrograman satir birokrasi — interpreter &amp; bytecode VM di browser</p>
		<div class="status">
			Status: <span class:ready={pyodideStatus.startsWith('Ready')}>{pyodideStatus}</span>
		</div>
	</header>

	<div class="container">
		<section class="editor-section">
			<div class="editor-header">
				<h2>Editor (.hl)</h2>
				<div class="buttons">
					<select bind:value={selectedExample} on:change={loadExample} disabled={isRunning} aria-label="Contoh program">
						<option value="demo">Demo</option>
						<option value="algoritma">Algoritma</option>
						<option value="error">Error handling</option>
						<option value="formal">Dialek formal v5</option>
					</select>
					<select bind:value={engine} disabled={isRunning} aria-label="Engine">
						<option value="interpreter">Interpreter</option>
						<option value="vm">HambaVM v4</option>
					</select>
					<input class="seed" bind:value={seed} placeholder="seed" aria-label="Seed RNG" disabled={isRunning} />
					<button on:click={runCode} disabled={isRunning || !pyodideStatus.startsWith('Ready')} class="run-btn">
						{isRunning ? '⏳ Running...' : '▶️ Run'}
					</button>
				</div>
			</div>
			<textarea bind:value={code} on:keydown={handleKeydown} spellcheck="false" disabled={isRunning}></textarea>
		</section>

		<section class="output-section">
			<div class="output-header">
				<h2>Console Output</h2>
			</div>
			<pre class="output">{output || '// Output akan muncul di sini... (Ctrl+Enter untuk run)'}</pre>
		</section>
	</div>

	<footer>
		<div class="syntax-guide">
			<h3>Syntax Reference</h3>
			<ul>
				<li><code>lapor ekspresi</code> — cetak nilai</li>
				<li><code>x = 1</code> / <code>set x = 1</code> / <code>Anggaran x = 1</code> — assignment</li>
				<li><code>jika .. ataujika .. atau .. akhir</code> — percabangan</li>
				<li><code>untuk i dari 1 sampai 10</code>, <code>untuk x dalam daftar</code>, <code>selama</code> — loop</li>
				<li><code>fungsi f(a) .. kembalikan .. akhir</code> — fungsi &amp; closure</li>
				<li><code>coba .. jikaGagal e .. akhirCoba</code> — tangkap error</li>
				<li><code>Korupsi(persen)</code>, <code>Mangkrak(ms)</code>, <code>selesai()</code> — satire</li>
				<li>Mode sandbox: akses file/DB/HTTP dimatikan di browser</li>
			</ul>
		</div>
	</footer>
</main>

<style>
	:global(body) {
		margin: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
		background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
		color: #333;
		min-height: 100vh;
	}

	main {
		max-width: 1400px;
		margin: 0 auto;
		padding: 2rem;
	}

	header {
		text-align: center;
		color: white;
		margin-bottom: 2rem;
	}

	h1 {
		font-size: 3rem;
		margin: 0;
		text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
	}

	.subtitle {
		font-size: 1.2rem;
		opacity: 0.9;
		margin: 0.5rem 0;
	}

	.status {
		margin-top: 1rem;
		padding: 0.5rem 1rem;
		background: rgba(255, 255, 255, 0.1);
		border-radius: 8px;
		display: inline-block;
	}

	.status span {
		color: #ffd700;
		font-weight: bold;
	}

	.status span.ready {
		color: #4ade80;
	}

	.container {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2rem;
		margin-bottom: 2rem;
	}

	section {
		background: white;
		border-radius: 12px;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
		overflow: hidden;
	}

	.editor-header,
	.output-header {
		background: #f8f9fa;
		padding: 1rem 1.5rem;
		border-bottom: 2px solid #e9ecef;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	h2 {
		margin: 0;
		font-size: 1.2rem;
		color: #495057;
	}

	.buttons {
		display: flex;
		gap: 0.5rem;
	}

	button {
		padding: 0.5rem 1rem;
		border: none;
		border-radius: 6px;
		background: #6c757d;
		color: white;
		cursor: pointer;
		font-size: 0.9rem;
		transition: all 0.2s;
	}

	button:hover:not(:disabled) {
		background: #5a6268;
		transform: translateY(-1px);
	}

	button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	select,
	.seed {
		padding: 0.5rem;
		border-radius: 6px;
		border: 1px solid #ccc;
		font-size: 0.9rem;
	}

	.seed {
		width: 4.5rem;
	}

	.run-btn {
		background: #28a745;
	}

	.run-btn:hover:not(:disabled) {
		background: #218838;
	}

	textarea {
		width: 100%;
		height: 500px;
		padding: 1.5rem;
		border: none;
		font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
		font-size: 0.95rem;
		line-height: 1.6;
		resize: vertical;
		background: #f8f9fa;
	}

	textarea:focus {
		outline: none;
		background: #fff;
	}

	.output {
		margin: 0;
		padding: 1.5rem;
		min-height: 500px;
		font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
		font-size: 0.9rem;
		line-height: 1.6;
		background: #1e1e1e;
		color: #d4d4d4;
		overflow-x: auto;
		white-space: pre-wrap;
		word-wrap: break-word;
	}

	footer {
		background: white;
		border-radius: 12px;
		padding: 2rem;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	}

	.syntax-guide h3 {
		margin-top: 0;
		color: #495057;
	}

	.syntax-guide ul {
		list-style: none;
		padding: 0;
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
		gap: 0.75rem;
	}

	.syntax-guide li {
		padding: 0.5rem 1rem;
		background: #f8f9fa;
		border-radius: 6px;
		border-left: 3px solid #2a5298;
	}

	.syntax-guide code {
		background: #e9ecef;
		padding: 0.2rem 0.5rem;
		border-radius: 4px;
		font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
		color: #d63384;
	}

	@media (max-width: 968px) {
		.container {
			grid-template-columns: 1fr;
		}

		h1 {
			font-size: 2rem;
		}

		.syntax-guide ul {
			grid-template-columns: 1fr;
		}
	}
</style>
