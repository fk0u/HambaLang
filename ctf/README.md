# 🏴 HambaLang Community CTF Pack (Unofficial)

Selamat datang di **HambaLang CTF Pack**!
Ini adalah kumpulan challenge _unofficial_ yang dibuat oleh komunitas (alias developer gabut) untuk menguji pemahaman Anda tentang birokrasi digital dan logika HambaLang.

## ⚠️ Disclaimer
- Ini bukan ujian CPNS.
- Tidak menjamin Anda jadi pejabat.
- Dibuat untuk bersenang-senang (dan sedikit pusing).

## 🏆 Challenge List

| Level | File | Deskripsi |
|-------|------|-----------|
| **Easy** | `challenge_easy.hl` | Pemanasan. Pahami alur dana anggaran. |
| **Medium**| `challenge_medium.hl`| Logika birokrasi yang berbelit-belit. |
| **Hard** | `challenge_hard.hl` | Butuh sedikit 'audit' mendalam. |

## 🎮 Cara Bermain

Gunakan CLI HambaLang untuk menjalankan challenge.

**Jalankan Challenge:**
```bash
hambalang ctf ctf/challenge_easy.hl
# atau tanpa install: python -m hambalang ctf ctf/challenge_easy.hl
```

Challenge berjalan di sandbox (tanpa akses file/DB/HTTP).

**Input Data:**
Beberapa challenge membutuhkan input interaktif (`Tagih`). Masukkan angka/data yang diminta.

**Submit Flag:**
Kalau berhasil, Anda akan mendapatkan output format `HLCTF{...}`.
Simpan flag tersebut (tidak ada server validasi, ini offline CTF).

## 🛠️ Tips
1. Baca source code `.hl` jika bingung.
2. Perhatikan variabel `Anggaran` dan kondisi `Sita`.
3. Kalau mentok, cek `writeup_unofficial.md` (tapi jangan nyontek dulu!).

---
*"Birokrasi yang baik adalah birokrasi yang bisa di-bypass."* - Anonymous
