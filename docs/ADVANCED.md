# HambaLang Advanced (Phase 2)

Fitur baru untuk menjadikan HambaLang "esoteric serious satire" + CTF-ready.

## Bahasa: Fitur Lanjutan

### 1) Blok Birokrasi (Scoped Block)
```
mulai
  set nama = "Perencanaan"
  lapor "Tahap: " + nama
akhir
```
- Variabel di dalam `mulai...akhir` bersifat lokal.
- Bisa dinest.

### 2) Variabel & Penugasan
```
set target = 1000000000
set status = "Proyek X"
```
- Mendukung string & number.
- Variabel built-in global: `anggaran`, `progress`, `tahun`.

### 3) Loop Rapat Terkontrol
```
Rapat(3)
  lapor "Rapat ke-" + teks(progress)
  set progress = progress + 10
selesaiRapat
```
- Loop n kali, berbeda dari `RapatInfinite`.

### 4) Prosedur Birokrasi (tanpa return)
```
prosedur Audit()
  lapor "Audit berjalan"
  Korupsi(5)
akhirProsedur

Audit()
```
- Scope lokal dalam prosedur.

### 5) Error & Exception Satir
```
coba
  Mangkrak("Jalan Tol")
jikaGagal
  lapor "Diselamatkan dengan rapat"
akhirCoba
```
- Exception baru: `ProyekMangkrakError`, `DanaHabisError`, `AuditKPKError`.

## Runtime Lanjutan
- Deterministic random seed (`--seed`) untuk CTF.
- Execution step limit (`--step-limit`) default 2000 untuk anti abuse.
- Fake timeline (`tahun` bertambah 0.01 per langkah).
- Progress auto-update pada beberapa aksi.
- CTF mode (`--ctf`) dengan flag tersembunyi di `Korupsi()`.
- Debug trace (`--debug`) dan delay eksekusi per langkah (`--delay 0.1`) untuk mode step-by-step / speed slider.

## Arsitektur Interpreter
- Terpisah: Parser → AST Node → Evaluator → Runtime.
- AST per statement: Block, Set, Print, RapatLoop, ProcDef/Call, TryCatch, Korupsi, Mangkrak.
- Evaluator dengan scope stack (push/pop).
- Error trace dengan nomor baris.

## Cara Jalan (Advanced)
```
# Demo fitur lanjut
python interpreter/hamba_advanced.py examples/advanced_features.hl --seed 42 --step-limit 500 --ctf --debug --delay 0.05

# CTF/Puzzle
python interpreter/hamba_advanced.py examples/advanced_ctf.hl --ctf --seed 42 --step-limit 800
```

## Catatan CTF
- `Korupsi()` menyimpan total; jika total % 424242 == 0 (ctf mode) akan print FLAG.
- Step limit bisa diset untuk puzzle.

## TODO Web Playground (ide singkat)
- Highlight .hl, slider kecepatan, step-by-step, permalink share.
- Belum diimplementasi di fase ini; PR welcome.
