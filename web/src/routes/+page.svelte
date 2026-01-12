<script>
	import { onMount } from 'svelte';

	let code = `// HambaLang v2.0 Demo
lapor "=== MEGA PROYEK HAMBALANG ==="

// Variables
nama = "Hambalang"
tahun = 2011
lapor "Proyek: " + nama + " (" + teks(tahun) + ")"

// Arrays
kontraktor = ["PT Adhi", "PT Waskita", "PT Wijaya"]
lapor "Kontraktor: " + teks(panjang(kontraktor))

// Functions
fungsi hitungPajak(nominal, persen)
    hasil = nominal * persen / 100
    kembalikan hasil
akhir

anggaran_awal = 1000000000
pajak = hitungPajak(anggaran_awal, 10)
lapor "Pajak 10%: Rp " + teks(pajak)

// Control Flow
jika anggaran > 500000000
    lapor "✅ Dana mencukupi"
atau
    lapor "⚠️ Dana kurang"
akhir

// Loops
lapor "\\nProses approval:"
untuk i dari 1 sampai 3
    lapor "Tingkat " + teks(i) + " - Disetujui"
akhir

// Satire
lapor "\\n[SATIRE] Simulasi Korupsi..."
Korupsi(25)
Mangkrak(1500)

selesai()`;

	let output = '';
	let isRunning = false;
	let pyodide = null;
	let pyodideStatus = 'Loading...';
	let selectedExample = 'demo';

	const interpreterCode = `import sys
import time
import random
import re
from js import console


class HambaRuntime:
    def __init__(self):
        self.anggaran = 1_000_000_000
        self.status_proyek = "Direncanakan"
        self.progress = 0
        self.output = []
        self.terminated = False
    
    def log(self, message):
        self.output.append(str(message))
    
    def get_output(self):
        return "\\n".join(self.output)


class HambaInterpreter:
    def __init__(self, runtime=None):
        self.runtime = runtime or HambaRuntime()
        self.in_rapat_infinite = False
    
    def execute(self, code):
        lines = code.strip().split('\\n')
        
        for line_num, line in enumerate(lines, 1):
            if self.runtime.terminated:
                break
            
            line = line.strip()
            
            if not line or line.startswith('//'):
                continue
            
            try:
                self._execute_line(line)
            except Exception as e:
                error_msg = f"Error Birokrasi pada baris {line_num}: {str(e)}"
                self.runtime.log(error_msg)
                raise Exception(error_msg)
    
    def _execute_line(self, line):
        if line.startswith('lapor '):
            content = line[6:].strip()
            message = self._eval_expression(content)
            self.runtime.log(message)
            return
        
        if line.startswith('print '):
            content = line[6:].strip()
            message = self._eval_expression(content)
            self.runtime.log(message)
            return
        
        match = re.match(r'Mangkrak\\((\\d+)\\)', line)
        if match:
            ms = int(match.group(1))
            self._mangkrak(ms)
            return
        
        match = re.match(r'Korupsi\\((\\d+)\\)', line)
        if match:
            percent = int(match.group(1))
            self._korupsi(percent)
            return
        
        if line == 'RapatInfinite()':
            self._rapat_infinite()
            return
        
        if line == 'selesai()':
            self._selesai()
            return
        
        if line.startswith('jika '):
            self._execute_conditional(line)
            return
        
        if '=' in line and not any(op in line for op in ['>', '<', '==']):
            self._assign_variable(line)
            return
        
        raise Exception(f"Syntax tidak dikenali: {line}")
    
    def _eval_expression(self, expr):
        expr = expr.strip()
        
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        
        if expr == 'anggaran':
            return f"Rp {self.runtime.anggaran:,.0f}"
        
        if expr == 'status_proyek':
            return self.runtime.status_proyek
        
        if expr == 'progress':
            return f"{self.runtime.progress}%"
        
        try:
            return str(eval(expr))
        except:
            return expr
    
    def _mangkrak(self, ms):
        seconds = ms / 1000
        self.runtime.log(f"⏳ Proyek mangkrak selama {seconds} detik...")
        
        events = [
            "💸 Dana habis untuk operasional!",
            "🏃 Vendor kabur dengan uang muka!",
            "🌧️ Longsor menghancurkan pondasi!",
            "🚨 Audit mendadak dari KPK!",
            "📄 Dokumen perizinan bermasalah!",
            "👷 Pekerja mogok kerja!",
        ]
        
        if random.random() < 0.3:
            event = random.choice(events)
            self.runtime.log(f"🚧 EVENT: {event}")
            self.runtime.anggaran -= random.randint(10_000_000, 100_000_000)
            if self.runtime.anggaran < 0:
                self.runtime.anggaran = 0
    
    def _korupsi(self, percent):
        if percent < 0 or percent > 100:
            raise Exception("Persentase korupsi harus 0-100")
        
        actual_percent = random.uniform(percent * 0.8, percent * 1.2)
        amount = self.runtime.anggaran * (actual_percent / 100)
        self.runtime.anggaran -= amount
        
        if self.runtime.anggaran < 0:
            self.runtime.anggaran = 0
        
        self.runtime.log(f"💰 Korupsi {actual_percent:.1f}%: Rp {amount:,.0f} menguap!")
        self.runtime.log(f"📊 Sisa anggaran: Rp {self.runtime.anggaran:,.0f}")
    
    def _rapat_infinite(self):
        self.runtime.log("🔄 Memulai RapatInfinite()...")
        self.runtime.log("⚠️ Program terjebak dalam rapat berkepanjangan!")
        
        for i in range(5):
            self.runtime.log(f"📋 Rapat sesi ke-{i+1}: Belum ada keputusan...")
        
        self.runtime.log("⏸️ (RapatInfinite dihentikan paksa untuk demo)")
    
    def _selesai(self):
        self.runtime.status_proyek = "Selesai (di atas kertas)"
        self.runtime.progress = 100
        
        bar = "█" * 9 + "░"
        self.runtime.log(f"\\n✅ PROYEK SELESAI!")
        self.runtime.log(f"Progress: 100% [{bar}]")
        self.runtime.log(f"Status: {self.runtime.status_proyek}")
        self.runtime.log(f"Sisa Anggaran: Rp {self.runtime.anggaran:,.0f}")
        self.runtime.log(f"(Kondisi fisik: Data tidak tersedia)")
        
        self.runtime.terminated = True
    
    def _execute_conditional(self, line):
        match = re.match(r'jika\\s+(.+?)\\s+maka\\s+(.+)', line)
        if not match:
            raise Exception("Format: jika <kondisi> maka <aksi>")
        
        condition = match.group(1).strip()
        action = match.group(2).strip()
        
        condition_eval = condition.replace('anggaran', str(self.runtime.anggaran))
        
        try:
            result = eval(condition_eval)
        except:
            raise Exception(f"Kondisi tidak valid: {condition}")
        
        if result:
            self._execute_line(action)
    
    def _assign_variable(self, line):
        parts = line.split('=', 1)
        if len(parts) != 2:
            raise Exception(f"Assignment tidak valid: {line}")
        
        var_name = parts[0].strip()
        value = parts[1].strip()
        
        if var_name == 'anggaran':
            try:
                self.runtime.anggaran = float(eval(value))
            except:
                raise Exception(f"Nilai anggaran tidak valid: {value}")
        elif var_name == 'status_proyek':
            self.runtime.status_proyek = self._eval_expression(value)
        elif var_name == 'progress':
            try:
                self.runtime.progress = int(eval(value))
            except:
                raise Exception(f"Nilai progress tidak valid: {value}")
        else:
            raise Exception(f"Variable tidak dikenal: {var_name}")


def run_hambalang(code):
    runtime = HambaRuntime()
    interpreter = HambaInterpreter(runtime)
    
    try:
        interpreter.execute(code)
        return runtime.get_output()
    except Exception as e:
        return runtime.get_output() + "\\n\\n" + str(e)
`;

	onMount(async () => {
		try {
			pyodideStatus = 'Loading Pyodide...';
			const pyodideModule = await import('pyodide');
			pyodide = await pyodideModule.loadPyodide({
				indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/'
			});

			await pyodide.runPythonAsync(interpreterCode);
			pyodideStatus = 'Ready';
		} catch (error) {
			pyodideStatus = 'Error loading Pyodide';
			output = `❌ Error: ${error.message}`;
		}
	});

	async function runCode() {
		if (!pyodide || pyodideStatus !== 'Ready') {
			output = '⚠️ Pyodide belum siap. Tunggu sebentar...';
			return;
		}

		isRunning = true;
		output = '🏗️ Menjalankan HambaLang...\n' + '='.repeat(50) + '\n\n';

		try {
			const result = await pyodide.runPythonAsync(`run_hambalang(${JSON.stringify(code)})`);
			output += result;
			output += '\n\n' + '='.repeat(50);
			output += '\n✅ Eksekusi selesai';
		} catch (error) {
			output += `\n\n❌ Error: ${error.message}`;
		} finally {
			isRunning = false;
		}
	}

	function loadExample() {
		code = `// HambaLang Demo - Satir Proyek Hambalang
lapor "=== MEGA PROYEK HAMBALANG ==="
lapor "Wisma Atlet Kelas Dunia"

lapor "Budget awal:"
print anggaran

lapor "[FASE 1] Perencanaan"
Mangkrak(2000)

lapor "[FASE 2] Tender & Pengadaan"
Korupsi(20)

jika anggaran > 500000000 maka lapor "✅ Anggaran mencukupi, lanjut!"

lapor "[FASE 3] Pelaksanaan"
Korupsi(25)
Mangkrak(3000)

lapor "[FASE 4] Finishing"
Korupsi(15)

lapor "Anggaran tersisa:"
print anggaran

jika anggaran < 100000000 maka lapor "⚠️ WARNING: Dana kritis!"

selesai()`;
	}
</script>

<svelte:head>
	<title>HambaLang - Esoteric Programming Language</title>
	<meta name="description" content="Satir Proyek Hambalang dalam bentuk bahasa pemrograman" />
</svelte:head>

<main>
	<header>
		<h1>🏗️ HambaLang</h1>
		<p class="subtitle">Esoteric Programming Language - Satir Proyek Hambalang</p>
		<div class="status">
			Status: <span class:ready={pyodideStatus === 'Ready'}>{pyodideStatus}</span>
		</div>
	</header>

	<div class="container">
		<section class="editor-section">
			<div class="editor-header">
				<h2>Editor (.hl)</h2>
				<div class="buttons">
					<button on:click={loadExample} disabled={isRunning}>📝 Load Example</button>
					<button on:click={runCode} disabled={isRunning || pyodideStatus !== 'Ready'} class="run-btn">
						{isRunning ? '⏳ Running...' : '▶️ Run'}
					</button>
				</div>
			</div>
			<textarea bind:value={code} spellcheck="false" disabled={isRunning}></textarea>
		</section>

		<section class="output-section">
			<div class="output-header">
				<h2>Console Output</h2>
			</div>
			<pre class="output">{output || '// Output akan muncul di sini...'}</pre>
		</section>
	</div>

	<footer>
		<div class="syntax-guide">
			<h3>Syntax Reference</h3>
			<ul>
				<li><code>lapor "pesan"</code> - Print message</li>
				<li><code>Mangkrak(ms)</code> - Delay dengan random event</li>
				<li><code>Korupsi(percent)</code> - Kurangi anggaran</li>
				<li><code>jika kondisi maka aksi</code> - Conditional</li>
				<li><code>selesai()</code> - End program</li>
				<li><code>RapatInfinite()</code> - Infinite loop</li>
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
