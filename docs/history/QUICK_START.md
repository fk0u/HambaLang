# 🚀 HambaLang Quick Start Guide

Panduan cepat untuk mulai menggunakan HambaLang dalam 5 menit!

## 📦 Prerequisites

### Untuk Interpreter (Python)
```bash
# Install Python 3.8 atau lebih tinggi
python --version  # Harus >= 3.8

# Clone repository
git clone https://github.com/yourusername/HambaLang.git
cd HambaLang

# Install dependencies
pip install -r requirements.txt
```

### Untuk Web Playground
```bash
# Install Node.js 18 atau lebih tinggi
node --version  # Harus >= 18

cd web
npm install
```

## 🎯 Your First HambaLang Program

### 1. Hello World
Buat file `hello.hl`:

```hambalang
lapor "Halo dari HambaLang!"
lapor "Proyek Hambalang yang sebenarnya berhasil!"
selesai
```

Jalankan:
```bash
python interpreter/hamba_v2.py hello.hl
```

Output:
```
Halo dari HambaLang!
Proyek Hambalang yang sebenarnya berhasil!
```

### 2. Variables & Operations
Buat file `variables.hl`:

```hambalang
# Deklarasi variabel
nama = "Proyek Hambalang"
budget = 2500000000000
korupsi = 0

lapor "Nama: " + nama
lapor "Budget: Rp " + teks(budget)

# Operasi matematika
sisaBudget = budget - (budget * 0.7)
lapor "Sisa Budget: Rp " + teks(sisaBudget)

selesai
```

### 3. Functions
Buat file `functions.hl`:

```hambalang
# Definisi fungsi
fungsi hitungKorupsi(budget, persenKorupsi)
    korupsi = budget * (persenKorupsi / 100)
    kembalikan korupsi
akhir

# Gunakan fungsi
totalBudget = 1000000000
persen = 60

hasilKorupsi = hitungKorupsi(totalBudget, persen)
lapor "Korupsi " + teks(persen) + "% dari Rp " + teks(totalBudget)
lapor "Total korupsi: Rp " + teks(hasilKorupsi)

selesai
```

### 4. Arrays & Loops
Buat file `arrays.hl`:

```hambalang
# Array
pejabat = ["Menteri A", "Direktur B", "Ketua C"]

lapor "Daftar Pejabat:"
untuk i dari 0 sampai panjang(pejabat)
    lapor teks(i + 1) + ". " + pejabat[i]
akhir

# Tambah data
tambahArray(pejabat, "Inspektur D")
lapor "\nSetelah ditambah: " + teks(panjang(pejabat)) + " orang"

selesai
```

### 5. Database Example
Buat file `database.hl`:

```hambalang
# Connect ke SQLite
db = sambungDB("sqlite", "hambalang.db")

# Buat tabel
queryDB(db, "CREATE TABLE IF NOT EXISTS proyek (id INTEGER PRIMARY KEY, nama TEXT, budget INTEGER)")

# Insert data
queryDB(db, "INSERT INTO proyek VALUES (1, 'Wisma Atlet', 2500000000000)")
queryDB(db, "INSERT INTO proyek VALUES (2, 'Jalan Tol', 500000000000)")

# Query data
hasil = queryDB(db, "SELECT * FROM proyek")
lapor "Data Proyek:"
lapor hasil

# Tutup koneksi
tutupDB(db)

selesai
```

### 6. File I/O Example
Buat file `file_io.hl`:

```hambalang
# Tulis file
konten = "Laporan Proyek Hambalang\nBudget: Rp 2.5T\nStatus: Selesai"
tulisFile("laporan.txt", konten)
lapor "File berhasil ditulis!"

# Baca file
isi = bacaFile("laporan.txt")
lapor "\nIsi file:"
lapor isi

selesai
```

### 7. HTTP API Example
Buat file `http_demo.hl`:

```hambalang
# GET request
lapor "Mengambil data dari API..."
response = httpGet("https://api.github.com/users/github")
lapor "Status: " + teks(response["status"])
lapor "Username: " + response["body"]["login"]

# POST request (contoh)
data = {
    "nama": "Proyek Hambalang",
    "status": "selesai"
}
# result = httpPost("https://api.example.com/projects", data)

selesai
```

### 8. Satire Features (Korupsi & RapatInfinite)
Buat file `satire.hl`:

```hambalang
# Korupsi: Simulasi korupsi proyek
budget = 1000000000
Korupsi(budget, 50)  # Korupsi 50%

# RapatInfinite: Rapat tak berujung
lapor "\nMemulai rapat koordinasi..."
RapatInfinite(3)  # Rapat 3 kali

# Mangkrak: Proyek mangkrak
Mangkrak("Proyek Stadion", "2015-01-01")

selesai
```

## 🎮 Run Examples

```bash
# Full feature demo
python interpreter/hamba_v2.py examples/full_demo.hl

# Database CRUD
python interpreter/hamba_v2.py examples/database_example.hl

# File I/O
python interpreter/hamba_v2.py examples/file_io_example.hl

# HTTP API
python interpreter/hamba_v2.py examples/http_api_example.hl

# Algorithms
python interpreter/hamba_v2.py examples/algorithms.hl

# Real-world CRUD app
python interpreter/hamba_v2.py examples/crud_app.hl
```

## 🌐 Run Web Playground

```bash
cd web
npm run dev
```

Buka browser: `http://localhost:5173`

## 🧪 Run Tests

```bash
# Run test suite
python tests/test_interpreter.py

# Output:
# Testing basic variables... ✓
# Testing arithmetic operations... ✓
# Testing functions... ✓
# Testing arrays... ✓
# Testing conditionals... ✓
# Testing loops... ✓
# Testing satire functions... ✓
```

## 🐳 Run with Docker

```bash
# Build image
docker build -t hambalang .

# Run container
docker run -it hambalang

# Run specific file
docker run -v $(pwd)/examples:/app/examples hambalang python hamba_v2.py examples/full_demo.hl
```

## 📚 Next Steps

1. **Read Full Documentation**
   - Open `docs/index.html` in browser
   - Read `README.md` for detailed features
   - Check `SYNTAX.md` for syntax reference

2. **Explore Examples**
   - Browse `examples/` directory
   - Study `crud_app.hl` for real-world example
   - Modify examples to learn

3. **Build Your Own App**
   - Create new `.hl` file
   - Use database, file I/O, or HTTP features
   - Test with interpreter

4. **Deploy Web Playground**
   ```bash
   cd web
   npm run build
   vercel deploy
   ```

5. **Contribute**
   - Read `CONTRIBUTING.md`
   - Submit issues or PRs
   - Improve documentation

## 🆘 Troubleshooting

### Error: Module not found
```bash
# Install missing dependencies
pip install requests mysql-connector-python psycopg2-binary
```

### Error: Python version too old
```bash
# Upgrade Python
python --version  # Must be >= 3.8
```

### Error: Database connection failed
```bash
# Check database credentials
# For SQLite: database file created automatically
# For MySQL/PostgreSQL: ensure server is running
```

### Web playground not loading
```bash
# Clear cache and reinstall
cd web
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## 📖 Cheat Sheet

### Keywords
- `lapor` - print output
- `fungsi...akhir` - define function
- `kembalikan` - return value
- `jika...ataujika...atau` - if-elif-else
- `selama...akhir` - while loop
- `untuk...dari...sampai` - for loop
- `hentikan` - break
- `lanjut` - continue
- `selesai` - program end

### Built-in Functions
- `panjang(arr)` - array length
- `tipe(val)` - get type
- `angka(str)` - to number
- `teks(val)` - to string
- `tambahArray(arr, val)` - append
- `hapusArray(arr, idx)` - remove

### Database Functions
- `sambungDB(type, config)` - connect
- `queryDB(db, sql)` - execute query
- `tutupDB(db)` - close connection

### File Functions
- `bacaFile(path)` - read file
- `tulisFile(path, content)` - write file

### HTTP Functions
- `httpGet(url)` - GET request
- `httpPost(url, data)` - POST request

### Satire Functions
- `Korupsi(budget, persen)` - corruption simulation
- `Mangkrak(nama, tanggal)` - abandoned project
- `RapatInfinite(n)` - infinite meetings

## 🎉 Success!

Sekarang kamu sudah siap membuat aplikasi dengan HambaLang!

**Tips:**
- Mulai dari contoh sederhana
- Pelajari error messages
- Eksplorasi examples/
- Baca dokumentasi lengkap
- Bergabung dengan community

**Happy Coding! 🚀**

---

**Need Help?**
- 📖 Documentation: [docs/index.html](docs/index.html)
- 💬 Issues: [GitHub Issues](https://github.com/yourusername/HambaLang/issues)
- 📧 Email: support@hambalang.dev
