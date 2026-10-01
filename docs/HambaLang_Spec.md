# HambaLang Language Specification (Version 6.0)

**Status:** normatif untuk implementasi di `hambalang/`
**Grammar:** [Grammar.ebnf](Grammar.ebnf) · **VM:** [VM_Spec.md](VM_Spec.md) · **Cheat sheet:** [../SYNTAX.md](../SYNTAX.md)

## 1. Pendahuluan

HambaLang adalah bahasa dinamis bertema satir birokrasi Indonesia. Program
dieksekusi oleh salah satu dari dua engine yang **wajib berperilaku identik**:

1. **Interpreter** — menelusuri AST langsung (engine referensi).
2. **HambaVM v4** — AST dikompilasi ke bytecode HBC v4 lalu dijalankan stack machine.

Pipeline: `source → lexer → parser → AST → (interpreter | compiler → VM)`.

### 1.1 Filosofi desain

- **Realisme birokrasi** — setiap statement memakan satu "langkah"; langkah
  tidak terbatas tidak tersedia (`NegaraBangkrut`).
- **Korupsi eksplisit** — efek samping pada `anggaran` hanya lewat builtin
  satire (`Korupsi`, `Mangkrak`) atau assignment terang-terangan.
- **Kompatibilitas mundur** — semua dialek historis (v2, advanced v3, formal
  v5) diterima satu parser dan bisa dicampur.
- **Determinisme** — dengan `seed` yang sama, output identik di setiap run dan
  di kedua engine.

## 2. Leksikal

- Encoding source UTF-8; BOM diabaikan; `\r\n` dinormalisasi.
- Statement diakhiri newline atau `;`. Newline di dalam `( )` dan `[ ]`
  diabaikan; di dalam literal objek `{ }` juga diabaikan oleh parser.
- Komentar: `// …`, `# …`, `/* … */`. `Wacana ekspresi` adalah komentar
  "resmi" yang diparse tetapi tidak dieksekusi.
- Identifier: `[A-Za-z_][A-Za-z0-9_]*` (ASCII), case-sensitive, bukan kata
  kunci dan bukan nama khusus `Korupsi`, `Mangkrak`, `Rapat`, `selesai`.
- Angka: `42`, `1_000_000`, `3.14`, `.5`, `1.5e9`. Teks: `"…"` atau `'…'`, boleh
  multi-baris, escape `\n \t \r \0 \\ \" \'` (escape lain = `SalahKetik`).
- Tiga kata kunci dibedakan oleh token sesudahnya: `Korupsi(` / `Mangkrak(` /
  `Rapat(` dengan kurung **menempel** adalah pemanggilan/loop; tanpa kurung
  menempel masing-masing berarti print (v5), raise (v5), dan pembuka blok
  program `Rapat … Bubarkan`.

## 3. Tipe

| Tipe | Literal | Keterangan |
|------|---------|------------|
| angka | `1`, `-2.5` | integer presisi bebas atau float IEEE-754 |
| teks | `"abc"` | immutable |
| boolean | `benar`, `salah` | |
| kosong | `kosong` | nilai default fungsi tanpa `kembalikan` |
| daftar | `[a, b]` | mutable, dibagi by-reference |
| objek | `{k: v}` | mutable, kunci selalu teks, urutan sisipan dipertahankan |
| fungsi | `fungsi …`, builtin | first-class, closure leksikal |

### 3.1 Truthiness

`salah`, `kosong`, `0`, `0.0`, `""`, `[]`, `{}` bernilai salah. Semua nilai
lain benar.

### 3.2 Aturan operator

- `+`: jika salah satu operand teks → konkatenasi `teks(a) + teks(b)`;
  `daftar + daftar` → daftar baru; `objek + objek` → merge; selain itu angka.
- `- * / % **`: hanya angka (boolean dihitung 0/1). `teks * n` dan
  `daftar * n` mengulang. `/` mengembalikan integer bila pembagian bulat
  sempurna, selain itu float. Pembagian/modulo dengan nol → `OperasiIlegal`.
- `==`/`!=`: kesetaraan nilai; boolean tidak pernah sama dengan angka.
- `< > <= >=`: angka-angka, teks-teks (leksikografis), atau daftar-daftar.
  Kombinasi lain → `OperasiIlegal`. Perbandingan tidak berantai.
- `dan`/`atau`: short-circuit, mengembalikan salah satu operand.

### 3.3 Konversi ke teks

`kosong` → `kosong`, boolean → `benar`/`salah`, float bulat → tanpa `.0`
(`4.0` → `4`), float lain → 15 digit signifikan (`0.1 + 0.2` → `0.3`). Di
dalam daftar/objek, teks diberi kutip: `[1, "a", benar]`.

## 4. Model memori & scope

- **Env global** dibuat saat program mulai.
- **Fungsi** (`fungsi`, `BagiRata`) membuat env fungsi saat dipanggil, induknya
  env tempat fungsi didefinisikan (closure). Assignment ke nama yang tidak ada
  di dalam fungsi membuat variabel lokal; `global x` mengalihkannya ke global.
- **Prosedur** (`prosedur`) dan **blok** (`mulai … akhir`) membuat env blok:
  assignment memperbarui variabel terdekat yang sudah ada di rantai scope,
  atau membuat variabel lokal baru.
- `jika`, loop, `coba`, `Rapat … Bubarkan` tidak membuat scope.
- **State negara** — `anggaran` (awal `1_000_000_000`), `progress`,
  `status_proyek`, `total_korupsi` — selalu global; `anggaran`/`progress` wajib
  angka, `total_korupsi` read-only.
- Resolusi nama: state negara → rantai env → builtin. Variabel user boleh
  membayangi builtin.

## 5. Kontrol alur

- `untuk i dari a sampai b [langkah s]`: batas atas **inklusif**; `s` boleh
  negatif, tidak boleh 0. Ekspresi dievaluasi sekali.
- `untuk x dalam e`: iterasi salinan dangkal daftar, karakter teks, atau
  kunci objek.
- `Rapat(n)`: ulangi `max(0, int(n))` kali.
- `hentikan`/`lanjut` hanya sah di dalam loop pada fungsi yang sama (dicek
  saat parsing).
- `kembalikan` di top-level menghentikan program dengan normal.
- `selesai` / `selesai()` mencetak laporan akhir lalu menghentikan program.

## 6. Error

| Jenis | Kapan | Bisa ditangkap `coba` |
|-------|-------|-----------------------|
| `SalahKetik` | lexer/parser menolak source | – (sebelum eksekusi) |
| `OperasiIlegal` | tipe salah, nama tidak ada, index di luar jangkauan, rekursi > 200 | ya |
| `ProyekMangkrak` | `Mangkrak "alasan"` / `Mangkrak("alasan")` | ya |
| `NegaraBangkrut` | langkah melebihi batas | **tidak** |

`coba … jikaGagal e … akhirCoba` mengikat **pesan** error (teks) ke `e`. Error
yang tidak tertangkap menghentikan program; CLI menampilkan jenis, posisi
`file:baris[:kolom]`, dan cuplikan source.

## 7. Eksekusi terbatas & determinisme

- Setiap statement yang dieksekusi = 1 langkah; setiap putaran loop
  (`selama`, `untuk`, `Rapat(n)`, `Proyek`) yang selesai menambah 1 langkah
  di back-edge, sehingga loop dengan body kosong pun tetap dibatasi. Default batas 1.000.000.
- Semua keacakan (`Korupsi`, event `Mangkrak`, `acak*`) memakai satu RNG per
  run yang di-seed dari `--seed`. Tanpa seed, RNG di-seed acak.
- `Mangkrak(ms)` hanya benar-benar tidur jika runtime `realtime` (CLI tanpa
  `--fast`), maksimal 2 detik per panggilan.

## 8. Sandbox

Mode sandbox (`--sandbox`, `--strict`, `hambalang ctf`, playground web)
menonaktifkan builtin file, database, dan HTTP dengan `OperasiIlegal`.

## 9. Konkurensi

HambaLang single-threaded. Konkurensi dianggap "proyek tumpang tindih" dan
masih dilarang regulasi.
