# Changelog

All notable changes to HambaLang will be documented in this file.

## [6.0.0] - 2026-10-01 — The Unification Era

### Ringkasan audit (alasan rilis ini)
- Ada 5 implementasi terpisah (`hamba.py`, `hamba_v2.py`, `hamba_advanced.py`,
  compiler/VM v3, interpreter inline di web) dengan 4 dialek yang tidak kompatibel.
- Grammar resmi di `docs/Grammar.ebnf` (dialek `Rapat … Bubarkan`) tidak punya
  implementasi sama sekali, sehingga 3 challenge CTF tidak bisa dimainkan.
- Evaluator berbasis `str.split`: `10 - 2 - 3` menghasilkan `11`, `f(1) + g(2)`
  hanya mengembalikan `f(1)`, escape `\n` tidak diproses, string berisi operator rusak.
- 14 dari 17 contoh gagal dijalankan; test suite 6/7; build web gagal
  (`src/app.html` tidak ada, `npm ci` tanpa lockfile).

### Added
- Paket `hambalang/`: lexer, parser (semua dialek → satu AST), tree-walking
  interpreter, compiler bytecode HBC v4, HambaVM v4, runtime & stdlib bersama.
- Fitur bahasa: closure, fungsi first-class, `global`, compound assignment
  (`+=` dst), operator `**`, akses `obj.properti`, index negatif,
  `untuk … langkah`, `atau jika`, `coba … jikaGagal e`, komentar `#` dan `/* */`,
  `;` sebagai pemisah statement, string multi-baris & escape.
- Dialek formal v5 kini benar-benar jalan: `Rapat/Bubarkan`, `Anggaran`,
  `Sita/Pengadilan`, `Proyek`, `Tagih`, `BagiRata`, `Janji`, `Wacana`.
- Stdlib 60+ fungsi: higher-order (`petakan`, `saring`, `lipat`), teks, objek,
  JSON, `rupiah()`, `pastikan()`, `Audit()`, `queryDB` dengan parameter binding.
- CLI terpadu: `run`, `compile`, `disasm`, `debug` (breakpoint, step,
  evaluasi ekspresi), `check`, `repl`, `ctf`; laporan error dengan cuplikan
  source dan caret; `--seed`, `--step-limit`, `--sandbox`, `--audit`, `--fast`.
- `pyproject.toml` dengan entry point `hambalang`; extras `[http]`, `[db]`, `[dev]`.
- Test suite pytest (650+ test): setiap test semantik jalan di interpreter dan
  VM; differential testing semua contoh & CTF + 400 program fuzz acak;
  round-trip bytecode; CLI E2E.
- Spesifikasi baru yang sesuai implementasi: `docs/Grammar.ebnf`,
  `docs/HambaLang_Spec.md`, `docs/VM_Spec.md`, `SYNTAX.md`.

### Changed
- `interpreter/hamba_v2.py`, `interpreter/hamba.py`, `cli/hambalang.py` menjadi
  shim ke core baru (perintah lama tetap jalan).
- `queryDB` SELECT mengembalikan daftar objek (`rows[0].nama`), bukan tuple.
- `tipe()` mengembalikan nama tipe HambaLang (`angka`, `teks`, `daftar`, …).
- `Korupsi`, `Mangkrak`, `acak` memakai satu RNG ber-seed per run (deterministik).
- Playground web memuat core Python yang sama via Pyodide (CDN), dengan pilihan
  engine Interpreter/VM, seed, dan mode sandbox.
- Contoh database dibuat idempoten dan memakai hasil query sungguhan.
- Dokumen historis Phase 3–5 dipindah ke `docs/history/`.

### Security
- Mode sandbox memblokir file/DB/HTTP (aktif di CTF dan playground).
- `queryDB(db, sql, params)` mendukung placeholder untuk mencegah SQL injection.
- Batas langkah tidak bisa ditangkap `coba`; rekursi dibatasi 200 lapis.

### Compatibility
- Toolchain legacy v3 (compiler lama, obfuscator, ObfuscatedVM, Hell Mode)
  tetap didukung: `hambalang compile --legacy`, `run file.hbc --obfuscated`,
  `obfuscate`, `analyze`. Bytecode v3/v4 dideteksi otomatis dari header.

## [2.0.0] - 2026-01-12

### Added - Complete Programming Language Features
- ✨ **Variables & Data Types**: string, number, boolean, array, object
- ✨ **Functions**: User-defined functions with parameters and return values
- ✨ **Control Flow**: if/elif/else, while loops, for loops (range & iteration)
- ✨ **Loop Control**: `hentikan` (break) and `lanjut` (continue)
- ✨ **Operators**: Arithmetic (+, -, *, /, %), comparison (==, !=, <, >, <=, >=), logical (dan, atau)
- ✨ **Arrays**: Create, access, modify, append, remove
- ✨ **Objects**: Dictionary-like key-value pairs
- ✨ **Database Support**: SQLite, MySQL, PostgreSQL connections and queries
- ✨ **File I/O**: Read and write text files, JSON support
- ✨ **HTTP/REST API**: GET and POST requests with JSON support
- ✨ **Built-in Functions**: 
  - `panjang()` - Get length
  - `tipe()` - Get type
  - `angka()` - Convert to number
  - `teks()` - Convert to string
  - `tambahArray()` - Add to array
  - `hapusArray()` - Remove from array
- 📚 **Comprehensive Documentation**: Full HTML documentation site
- 📝 **Real-world Examples**: Database CRUD, file processing, API client, algorithms
- 🌐 **Enhanced Web Playground**: Updated UI with better examples

### Changed
- 🔧 Interpreter completely rewritten for advanced features (`hamba_v2.py`)
- 📖 README expanded with full feature list and usage guide
- 🎨 Web interface updated with better code examples

### Original Features (v1.0)
- ✅ `Mangkrak()` - Delay dengan random events
- ✅ `Korupsi()` - Budget reduction simulation
- ✅ `RapatInfinite()` - Infinite loop rapat
- ✅ `selesai()` - Administrative completion
- ✅ `anggaran`, `status_proyek`, `progress` built-in variables

## [1.0.0] - 2026-01-11

### Initial Release
- 🎭 Basic esoteric programming language
- 💰 Satire features: Mangkrak, Korupsi, RapatInfinite
- 📝 Simple syntax: lapor, print, jika...maka
- 🏗️ Python interpreter
- 🌐 Web playground with Pyodide
- 📚 Basic documentation
- 🎯 .hl file extension

---

**Note:** HambaLang adalah satir dari proyek Hambalang dan birokrasi Indonesia. 
Project ini untuk tujuan edukasi, portfolio, dan hiburan.
