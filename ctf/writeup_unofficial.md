# Unofficial HambaLang CTF Writeup

Buat yang udah nyerah, atau cuma mau nyocokin jawaban.
Ingat: **SPOILER ALERT!**

---

## Challenge 1: Easy (Pelicin Anggaran)
**File:** `challenge_easy.hl`

### Analisis
Source codenya transparan banget.
```
Anggaran target = 1337
...
Tagih setoran
Sita setoran == target
```
Kita cuma perlu masukin angka yang sama dengan `target`.

### Solusi
Input: `1337`
Flag: `HLCTF{anggaran_bocor_halus}`

---

## Challenge 2: Medium (Alur Birokrasi)
**File:** `challenge_medium.hl`

### Analisis
Ini implementasi algoritma mirip **Collatz Conjecture** (3n+1), tapi dibatasi 5 langkah (loop).
Kita harus cari input awal (`X`) yang setelah 5 proses iterasi hasilnya jadi `1`.

Rules:
- Genap: `X / 2`
- Ganjil: `3X + 1`

Mari kita reverse dari hasil akhir `1` mundur ke belakang sebanyak 5 langkah:
1. `1` <- `2` (karena 2/2 = 1)
2. `2` <- `4` (karena 4/2 = 2)
3. `4` <- `8` (8/2 = 4) [Bisa juga 1, tapi 3(1)+1 = 4. Kita cari jalur genap dulu]
4. `8` <- `16` (16/2 = 8)
5. `16` <- `32` (32/2 = 16)

Coba input `32`:
Loop 1: 32 -> 16
Loop 2: 16 -> 8
Loop 3: 8 -> 4
Loop 4: 4 -> 2
Loop 5: 2 -> 1
Hasil akhir: `1`. PASS!

### Solusi
Input: `32`
Flag: `HLCTF{birokrasi_berbelit_tapi_cuan}`

---

## Challenge 3: Hard (Audit Forensik)
**File:** `challenge_hard.hl`

### Analisis
Kita butuh variable `verifikasi` bernilai 3. Artinya semua kondisi `Sita` harus bernilai BENAR.

Kondisi:
1. `saldo > 100`
2. `saldo < 200`
3. `saldo * 2 == 300`

Dari kondisi 3:
`2x = 300` -> `x = 150`

Cek kondisi lain:
- 150 > 100 (BENAR)
- 150 < 200 (BENAR)

Jadi inputnya fix satu angka.

### Solusi
Input: `150`
Flag: `HLCTF{reverse_engineer_plat_merah}`

---

## Kesimpulan
HambaLang sebenernya bahasa yang logis, cuma istilahnya aja yang bikin darah tinggi.
Selamat sudah menyelesaikan CTF gabut ini!
