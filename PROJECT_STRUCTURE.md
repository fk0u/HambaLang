# Struktur Proyek HambaLang v6

```
HambaLang/
├── hambalang/               ⭐ Core terpadu (dipakai CLI, test, dan web)
│   ├── lexer.py             token + posisi, escape, komentar
│   ├── parser.py            recursive descent, semua dialek → satu AST
│   ├── nodes.py             definisi AST
│   ├── interpreter.py       tree-walking interpreter (engine referensi)
│   ├── compiler.py          AST → bytecode HBC v4
│   ├── bytecode.py          opcode, format .hbc, disassembler
│   ├── vm.py                HambaVM v4 (stack machine berbasis frame)
│   ├── runtime.py           nilai, operator, scope, state negara
│   ├── builtins.py          standard library
│   ├── errors.py            SalahKetik, OperasiIlegal, ProyekMangkrak, NegaraBangkrut
│   └── cli.py               run/compile/disasm/debug/check/repl/ctf
│
├── tests/                   pytest: parser, semantik (×2 engine), program, CLI
├── examples/                contoh program .hl (+ .hbc legacy v3)
├── ctf/                     CTF pack (dialek formal v5) + Hell Mode legacy
├── docs/                    Grammar.ebnf, HambaLang_Spec.md, VM_Spec.md, Semantics.md
│   └── history/             catatan Phase 1–5 (arsip)
├── paper/                   paper gaya SIGBOVIK
├── web/                     playground SvelteKit + Pyodide
│
├── cli/                     shim CLI lama → hambalang.cli (+ perintah legacy)
├── interpreter/             shim hamba.py/hamba_v2.py; hamba_advanced.py (parser legacy v3)
├── compiler/, vm/           toolchain bytecode legacy v3
├── obfuscator/              opcode remapping & junk injection (legacy v3)
├── wasm/                    eksperimen runtime WebAssembly
│
├── pyproject.toml           paket & entry point `hambalang`
├── Dockerfile
├── README.md · SYNTAX.md · INSTALL.md · CONTRIBUTING.md · CHANGELOG.md
```

## Ke mana kalau ingin…

| Tujuan | File |
|--------|------|
| Menambah sintaks | `hambalang/parser.py` + `nodes.py`, lalu `interpreter.py` **dan** `compiler.py` |
| Menambah builtin | `hambalang/builtins.py` (otomatis tersedia di kedua engine) |
| Mengubah semantik operator/scope | `hambalang/runtime.py` |
| Menambah opcode | `hambalang/bytecode.py`, `compiler.py`, `vm.py`, `docs/VM_Spec.md` |
| Menambah perintah CLI | `hambalang/cli.py` |
| Menambah test | `tests/test_semantics.py` (fixture `run` otomatis menguji kedua engine) |
