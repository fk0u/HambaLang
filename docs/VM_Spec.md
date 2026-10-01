# HambaVM v4 — Spesifikasi Bytecode & Mesin Virtual

Implementasi: `hambalang/bytecode.py` (format, disassembler),
`hambalang/compiler.py` (AST → bytecode), `hambalang/vm.py` (eksekusi).

## 1. Model eksekusi

HambaVM adalah stack machine dengan **frame per pemanggilan fungsi**. Setiap
`Frame` memiliki:

| Field | Isi |
|-------|-----|
| `code` | `CodeObject` yang sedang dieksekusi |
| `pc` | index instruksi berikutnya |
| `env` | environment variabel (rantai scope, sama dengan interpreter) |
| `stack` | operand stack frame ini |
| `handlers` | stack handler `coba`: `(alamat, kedalaman stack, env)` |
| `line` | baris source terakhir (`LINE`), dipakai untuk pesan error |

Variabel diakses **berdasarkan nama** melalui environment, sehingga semantik
scope (fungsi vs blok, closure, `global`) identik dengan tree-walking
interpreter. Nilai, operator, dan builtin dipanggil dari `hambalang/runtime.py`
dan `hambalang/builtins.py` yang juga dipakai interpreter.

### Kesetaraan dengan interpreter

Compiler menyisipkan `LINE n` di awal setiap statement dan di back-edge
setiap loop. `LINE` menaikkan penghitung langkah persis seperti interpreter
menghitung statement, jadi `Audit().langkah`, batas `--step-limit`, dan nomor
baris error sama di kedua engine. Test suite memverifikasi ini dengan
menjalankan setiap program di keduanya dan membandingkan output.

## 2. Format file `.hbc`

Semua integer little-endian.

```
magic    4 byte   "HBC\0"
version  u16      4
code     CodeObject (modul)

CodeObject:
  name    str
  kind    str                 "modul" | "fungsi" | "prosedur"
  params  u16 n, str × n
  code    u32 n, (u8 opcode, u32 arg) × n
  lines   u32 × n             baris source per instruksi
  consts  u16 n, const × n

const := tag u8 + payload
  'N' kosong   'T' benar   'F' salah
  'I' i64      'X' bigint (u32 n + n byte two's-complement LE)   'D' f64
  'B' bigint sebagai str desimal (format awal; hanya dibaca, tidak ditulis)
  'S' str      'C' CodeObject (fungsi bersarang)

str := u32 panjang + byte UTF-8
```

Header kompatibel dengan bytecode legacy v3 (magic sama, versi `u16` di offset
4), sehingga `hambalang run/disasm` otomatis memilih HambaVM v4 atau VM legacy.

Konstanta di-deduplikasi berdasarkan `(tipe, nilai)` — `1`, `1.0`, dan `benar`
tetap konstanta terpisah.

### Verifikasi saat load

`load` menolak file (dengan `BytecodeError`) bila ada index konstanta/nama
di luar jangkauan, target lompat tidak valid, operator tidak dikenal, operand
`INPUT` selain 0/1, atau bila — ditelusuri lewat aliran kontrol seperti
verifier JVM — operand stack bisa underflow, `POP_TRY`/`POP_SCOPE` tidak
punya pasangan, atau kedalaman stack/handler/scope berbeda di titik pertemuan. VM tidak pernah
menjalankan bytecode yang belum lolos verifikasi.

## 3. Instruction set

| # | Opcode | Arg | Efek pada stack / state |
|---|--------|-----|-------------------------|
| 0 | `NOP` | – | – |
| 1 | `LOAD_CONST` | k | push `consts[k]` |
| 2 | `LOAD_NAME` | k | push nilai variabel `consts[k]` (state negara → env → builtin) |
| 3 | `STORE_NAME` | k | pop → assign ke `consts[k]` (aturan scope §4) |
| 4 | `POP` | – | buang top |
| 5 | `DUP` | – | duplikasi top |
| 6 | `DUP2` | – | duplikasi dua teratas (untuk `a[i] += x`) |
| 7 | `BINARY` | op | `b = pop; a = pop; push a op b`; op index ke `+ - * / % ** == != < > <= >=` |
| 8 | `UNARY` | op | top = op(top); op index ke `- bukan` |
| 9 | `INDEX_GET` | – | `k = pop; o = pop; push o[k]` |
| 10 | `INDEX_SET` | – | `v = pop; k = pop; o = pop; o[k] = v` |
| 11 | `ATTR_GET` | k | top = top.`consts[k]` |
| 12 | `ATTR_SET` | k | `v = pop; o = pop; o.consts[k] = v` |
| 13 | `BUILD_LIST` | n | pop n item → push daftar |
| 14 | `BUILD_DICT` | n | pop n pasangan kunci/nilai → push objek |
| 15 | `CALL` | n | pop n argumen + fungsi; builtin dipanggil langsung, fungsi user mendorong frame baru |
| 16 | `RETURN` | – | pop nilai, buang frame, push nilai ke frame pemanggil |
| 17 | `PRINT` | – | pop → tulis ke output |
| 18 | `JUMP` | a | `pc = a` |
| 19 | `JUMP_IF_FALSE` | a | pop; jika falsy `pc = a` |
| 20 | `JUMP_IF_FALSE_OR_POP` | a | `dan`: jika top falsy lompat (top tetap), selain itu pop |
| 21 | `JUMP_IF_TRUE_OR_POP` | a | `atau`: jika top truthy lompat (top tetap), selain itu pop |
| 22 | `MAKE_FUNCTION` | k | push closure dari `consts[k]` + env saat ini |
| 23 | `PUSH_SCOPE` | – | `env = Env(env)` (`mulai`) |
| 24 | `POP_SCOPE` | – | `env = env.parent` |
| 25 | `SETUP_TRY` | a | daftarkan handler di alamat `a` |
| 26 | `POP_TRY` | – | lepas handler teratas |
| 27 | `RAISE` | – | pop pesan → lempar `ProyekMangkrak` |
| 28 | `GET_ITER` | – | top = iterator (daftar/teks/kunci objek, disalin) |
| 29 | `RANGE_ITER` | – | pop langkah, akhir, awal → push iterator inklusif |
| 30 | `REPEAT_ITER` | – | top = iterator `range(n)` untuk `Rapat(n)` |
| 31 | `FOR_ITER` | a | push `next(top)`; jika habis pop iterator dan `pc = a` |
| 32 | `INPUT` | p | (p=1: pop prompt) → push input (teks angka jadi angka) |
| 33 | `GLOBAL` | k | deklarasikan `consts[k]` global di scope fungsi |
| 34 | `HALT` | – | jalankan `selesai()` dan hentikan program |
| 35 | `LINE` | n | catat baris, tick langkah (`NegaraBangkrut` bila melebihi batas) |

## 4. Aturan scope (`STORE_NAME`)

1. Nama state negara (`anggaran`, `progress`, `status_proyek`, `total_korupsi`) → state global.
2. Cari nama dari env sekarang ke atas; berhenti setelah memeriksa env fungsi terdekat.
3. Ketemu → update di env tersebut. Nama dideklarasikan `global` → tulis ke env global.
4. Tidak ketemu → buat di env sekarang.

Env fungsi dibuat dengan `is_function = (kind == "fungsi")`; `prosedur` memakai
env blok sehingga assignment menembus ke luar.

## 5. Kompilasi kontrol alur

```
selama c:
  top:  <c>
        JUMP_IF_FALSE end
        <body>
  cont: LINE               (target 'lanjut')
        JUMP top
  end:

untuk x dalam e / untuk i dari..sampai / Rapat(n):
        <iterator>
  top:  FOR_ITER end       (habis: pop iterator, lompat ke end)
        STORE_NAME x       (Rapat: POP)
        <body>
  cont: LINE               (target 'lanjut')
        JUMP top
  brk:  POP                (hanya bila ada 'hentikan')
  end:
```

`hentikan`/`lanjut` di dalam `coba` atau `mulai` lebih dulu memancarkan
`POP_TRY`/`POP_SCOPE` sebanyak blok yang ditinggalkan.

```
coba:   SETUP_TRY handler
        <body>
        POP_TRY
        JUMP end
handler:STORE_NAME e   (atau POP)
        <handler body>
end:
```

## 6. Exception

Saat instruksi melempar `HambaError`, VM mengisi nomor baris dari frame aktif
lalu mencari handler dari frame teratas ke bawah. Handler ditemukan → stack
frame dipotong ke kedalaman saat `SETUP_TRY`, env dipulihkan, pesan error
di-push, `pc` lompat ke handler. Frame tanpa handler dibuang (call depth
dikurangi). `NegaraBangkrut` dan `selesai()` tidak bisa ditangkap.

Builtin higher-order (`petakan`, `saring`, `lipat`) memanggil fungsi user
lewat `VM.call_function`, yang menjalankan loop VM bersarang sampai frame
tersebut return; exception yang tidak tertangkap di dalamnya diteruskan ke
frame pemanggil seperti biasa.

## 7. Batas

| Batas | Default | Error |
|-------|---------|-------|
| Langkah eksekusi | 1.000.000 (`--step-limit`, 0 = tanpa batas) | `NegaraBangkrut` |
| Kedalaman pemanggilan | 200 frame | `OperasiIlegal` |
| Konstanta per CodeObject | 65.535 | – |

---

## Lampiran: Bytecode legacy v3

Toolchain Phase 3–4 (`compiler/bytecode.py`, `vm/hamba_vm.py`,
`vm/obfuscated_vm.py`, `obfuscator/`) tetap tersedia untuk obfuscation dan
Hell Mode CTF. Format v3 memakai operand 16-bit, variabel bernomor, dan hanya
mendukung subset dialek advanced (`set`, `lapor`, `Korupsi`, `jika` tanpa
`atau`, `Rapat(n)`). Ekspresi diparse dengan parser v6 lalu diturunkan ke
opcode v3; karena format v3 tidak punya tipe boolean/kosong, `benar`/`salah`
menjadi `1`/`0`, `kosong` menjadi `0`, dan `dan`/`atau` menghasilkan 1/0
(tetap short-circuit). Definisi `fungsi` ditolak parser legacy
(`Syntax tidak dikenali`); daftar, objek, dan pemanggilan fungsi di dalam
ekspresi ditolak dengan pesan yang menyarankan `hambalang compile` (HBC v4). Gunakan `hambalang compile --legacy` untuk menghasilkannya.
