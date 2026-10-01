# HambaLang v6 — Syntax Cheat Sheet

Grammar formal: [docs/Grammar.ebnf](docs/Grammar.ebnf) · Spesifikasi: [docs/HambaLang_Spec.md](docs/HambaLang_Spec.md)

## Dasar

```hl
// komentar baris          # juga komentar          /* komentar blok */
lapor "Halo"               // print "Halo" juga boleh
lapor                      // baris kosong
x = 1; y = 2               // ';' memisahkan statement di satu baris
```

## Nilai & tipe

| Tipe (`tipe(x)`) | Contoh | Catatan |
|------------------|--------|---------|
| `angka` | `42`, `-7`, `3.14`, `1_000_000`, `1.5e9` | `7 / 2` → `3.5`, `8 / 2` → `4` |
| `teks` | `"a"`, `'b'`, `"baris\nbaru\t\"kutip\""` | Boleh multi-baris |
| `boolean` | `benar`, `salah` (atau `BENAR`, `SALAH`) | |
| `kosong` | `kosong` | null |
| `daftar` | `[1, "dua", benar]` | Dibagi by-reference; `salin(x)` untuk copy |
| `objek` | `{nama: "Hambalang", "tahun": 2011}` | Kunci selalu teks |
| `fungsi` | `fib`, `panjang` | First-class, bisa dikirim sebagai argumen |

**Truthiness:** `salah`, `kosong`, `0`, `""`, `[]`, `{}` dianggap salah; sisanya benar.

## Variabel & assignment

```hl
x = 10
set y = 20                 // gaya advanced
Anggaran z = 30            // gaya formal v5
x += 5                     // juga -= *= /= %=
daftar[0] = "baru"
obj["kunci"] = 1
obj.kunci += 1
```

Variabel bawaan (selalu global): `anggaran` (awal 1.000.000.000), `progress`,
`status_proyek`, `total_korupsi` (read-only).

## Operator (prioritas rendah → tinggi)

| Operator | Arti |
|----------|------|
| `atau` / `ATAU` | OR (short-circuit, mengembalikan operand) |
| `dan` / `DAN` | AND (short-circuit) |
| `bukan` / `BUKAN` | NOT |
| `== != < > <= >=` | Perbandingan (`1 == benar` → `salah`) |
| `+ -` | Tambah/kurang. `teks + apa saja` = gabung teks, `daftar + daftar`, `objek + objek` |
| `* / %` | `"ab" * 3` = `"ababab"` |
| `-x  !x` | Negasi, NOT |
| `**` | Pangkat (asosiatif kanan) |
| `f(x)  a[i]  o.k` | Panggil, index (negatif boleh), properti |

## Percabangan

```hl
jika nilai >= 80
    lapor "A"
ataujika nilai >= 60          // atau: "atau jika"
    lapor "B"
atau
    lapor "C"
akhir

jika anggaran < 0 maka lapor "Bangkrut"     // satu baris

Sita x == 1 {                               // dialek formal v5
    Korupsi "satu"
} Pengadilan Sita x == 2 {
    Korupsi "dua"
} Pengadilan {
    Korupsi "lainnya"
}
```

## Loop

```hl
untuk i dari 1 sampai 10              // batas atas inklusif
untuk i dari 10 sampai 0 langkah -2
untuk item dalam daftar               // juga teks (per karakter) & objek (per kunci)
selama kondisi
Rapat(3)                              // ulangi 3 kali
    ...
selesaiRapat
Proyek kondisi { ... }                // while gaya v5

hentikan                              // break
lanjut                                // continue
```

Semua loop `untuk`/`selama`/`Rapat` ditutup `akhir` (kecuali `Rapat(n)` → `selesaiRapat`).

## Fungsi & scope

```hl
fungsi luas(p, l)
    kembalikan p * l
akhir

fungsi pembuatPenambah(n)          // closure
    fungsi tambah(x)
        kembalikan x + n
    akhir
    kembalikan tambah
akhir

BagiRata kali(a, b) { kembalikan a * b }   // gaya v5
lapor Janji kali(6, 7)                     // 'Janji' = panggilan gaya v5

prosedur Laporan()                         // prosedur: assignment menembus ke luar
    set total = total + 1
akhirProsedur
Laporan()
```

Aturan scope:

- **fungsi** — assignment membuat variabel lokal (seperti Python). Pakai `global x` untuk menulis global.
- **prosedur** dan **`mulai … akhir`** — assignment memperbarui variabel luar yang sudah ada; variabel baru tetap lokal.
- Blok `jika`/loop tidak membuat scope baru.
- `hentikan`/`lanjut` di luar loop = error sintaks.

## Error handling

```hl
coba
    x = [1, 2][5]
jikaGagal pesan                 // variabel pesan opsional
    lapor "Gagal: " + pesan
akhirCoba

Mangkrak "Dana tidak cair"      // lempar ProyekMangkrak
Mangkrak("Dana tidak cair")     // sama
Mangkrak(2000)                  // ANGKA = tunda 2 detik + kemungkinan event
pastikan(x > 0, "x harus positif")
```

Jenis error: `SalahKetik` (sintaks), `OperasiIlegal` (runtime), `ProyekMangkrak`
(dilempar program), `NegaraBangkrut` (batas langkah — **tidak bisa** ditangkap).

## Input / program formal

```hl
Tagih umur                       // input; teks yang berupa angka otomatis jadi angka
Tagih nama, "Nama Anda: "

Rapat                            // pembungkus program v5 (tanpa scope baru)
    Wacana "komentar resmi"
    Anggaran x = 1
Bubarkan

selesai                          // atau selesai(): akhiri program
```

## Standard library

| Kategori | Fungsi |
|----------|--------|
| Konversi | `panjang` `tipe` `angka` `teks` `bulat` `bulatkan(x, digit)` `boolean` |
| Matematika | `mutlak` `akar` `pangkat` `minimum` `maksimum` `jumlah` `rataRata` `acak()` `acak(n)` `acak(a, b)` `acakPilih` `rentang(n)` `rentang(a, b, langkah)` |
| Daftar | `tambahArray`/`tambah` `hapusArray`/`hapus` `sisipkan` `ambilAkhir` `urutkan(x, turun)` `balik` `irisan(x, a, b)` `indeksDari` `berisi` `salin` |
| Higher-order | `petakan(daftar, f)` `saring(daftar, f)` `lipat(daftar, f, awal)` |
| Teks | `gabung(daftar, sep)` `pisah(teks, sep)` `besar` `kecil` `rapikan` `ganti` `mulaiDengan` `akhiriDengan` `ulangi` `rupiah` `kode` `karakter` |
| Objek | `kunci` `nilai` `punya` |
| JSON | `keJSON(x, indent)` `dariJSON(teks)` `bacaJSON(path)` `tulisJSON(path, x)` |
| File* | `tulisFile` `tambahFile` `bacaFile` `adaFile` `hapusFile` |
| Database* | `sambungDB(nama, "sqlite"/"mysql"/"postgres", target)` `queryDB(nama, sql, [params])` `tutupDB` |
| HTTP* | `httpGet(url)` `httpPost(url, data)` → `{status, body, json}` |
| Lain | `masukan(prompt)` `waktu()` `tanggal()` `pastikan(c, pesan)` |
| Satire | `Korupsi(persen)` `Mangkrak(ms)` `selesai()` `RapatInfinite()` `Audit()` |

\* diblokir di mode `--sandbox` / `--strict` / playground / CTF.

`queryDB` mengembalikan daftar objek untuk `SELECT` (`rows[0].nama`) dan jumlah
baris terdampak untuk perintah lain. Selalu pakai placeholder `?` + daftar
parameter untuk input user:

```hl
queryDB("db", "SELECT * FROM proyek WHERE nama = ?", [nama_input])
```
