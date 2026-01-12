# 🏗️ HambaLang v2.0 - Complete Edition

**Esoteric Programming Language - Satir Proyek Hambalang**

Bahasa pemrograman lengkap yang menjadi parodi satir proyek Hambalang. Dari joke language menjadi **production-ready programming language** dengan fitur lengkap untuk membangun aplikasi sederhana hingga menengah.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-yellow)

---

## 🌟 What's New in v2.0?

### ✨ Full Programming Language Features

**Core Features:**
- ✅ Variables & Data Types (string, number, boolean, array, object)
- ✅ Functions dengan parameters & return values
- ✅ Control Flow: if/elif/else, while, for loops
- ✅ Arrays & Objects manipulation
- ✅ Mathematical & logical operations
- ✅ String operations

**Advanced Features:**
- ✅ **Database Support**: SQLite, MySQL, PostgreSQL
- ✅ **File I/O**: Read, Write, JSON processing
- ✅ **HTTP/REST API Client**: GET, POST requests
- ✅ **Built-in Functions**: Type conversion, array manipulation
- ✅ **Error Handling**: Meaningful error messages

**Satire Features (Original):**
- ✅ `Mangkrak()` - Delay dengan random events
- ✅ `Korupsi()` - Anggaran menguap secara acak
- ✅ `RapatInfinite()` - Infinite loop rapat
- ✅ `selesai()` - "Selesai" hanya di atas kertas

---

## 📖 Filosofi

```
lapor → lelang → mangkrak → rapat → (mungkin) selesai
```

HambaLang menggabungkan satir birokrasi Indonesia dengan kemampuan programming language yang serius.

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/hambalang.git
cd hambalang

# Install dependencies (optional, untuk fitur advanced)
pip install requests mysql-connector-python psycopg2-binary

# Run example
python interpreter/hamba_v2.py examples/full_demo.hl
```

### Hello Hambalang

```hl
// File: hello.hl
lapor "Hello, Hambalang!"
lapor "Proyek Mega Infrastructure"

anggaran = 1000000000
Korupsi(25)

lapor "Sisa anggaran: Rp " + teks(anggaran)

selesai()
```

Run:
```bash
python interpreter/hamba_v2.py hello.hl
```

---

## 📚 Documentation

📖 **[Full Documentation](docs/index.html)** - Comprehensive guide dengan syntax reference, examples, dan API documentation

### Quick Reference

**Variables & Data Types:**
```hl
nama = "Hambalang"
tahun = 2011
aktif = benar
items = ["A", "B", "C"]
data = {"key": "value"}
```

**Functions:**
```hl
fungsi hitungPajak(nominal, persen)
    hasil = nominal * persen / 100
    kembalikan hasil
akhir

pajak = hitungPajak(1000000, 10)
```

**Control Flow:**
```hl
jika anggaran > 1000000000
    lapor "Disetujui"
ataujika anggaran > 500000000
    lapor "Perlu review"
atau
    lapor "Ditolak"
akhir
```

**Loops:**
```hl
// For range
untuk i dari 1 sampai 10
    lapor teks(i)
akhir

// For array
untuk item dalam array
    lapor item
akhir

// While
selama kondisi
    // code
akhir
```

**Database:**
```hl
sambungDB("mydb", "sqlite", "data.db")
hasil = queryDB("mydb", "SELECT * FROM users")
tutupDB("mydb")
```

**File I/O:**
```hl
tulisFile("data.txt", "Content")
content = bacaFile("data.txt")
```

**HTTP/API:**
```hl
response = httpGet("https://api.example.com/data")
lapor response["body"]
```

---

## 🎯 Use Cases

### 1. **Simple Scripts**
Quick automation, data processing, calculations

### 2. **Database Applications**
CRUD apps, data management, reporting

### 3. **File Processing**
Log analysis, CSV processing, JSON manipulation

### 4. **API Integration**
REST API clients, webhook handlers, data fetching

### 5. **Learning Programming**
Fun way untuk belajar programming concepts dengan context satir yang memorable

---

## 📂 Project Structure

```
HambaLang/
├── interpreter/
│   ├── hamba.py              # Original interpreter (v1.0)
│   └── hamba_v2.py           # Full-featured interpreter (v2.0)
├── examples/
│   ├── demo.hl               # Basic demo (v1.0)
│   ├── full_demo.hl          # Complete feature demo
│   ├── database_example.hl   # Database CRUD
│   ├── file_io_example.hl    # File operations
│   ├── http_api_example.hl   # REST API client
│   ├── algorithms.hl         # Algorithm examples
│   ├── corruption.hl         # Satire demo
│   └── infinite.hl           # RapatInfinite demo
├── web/
│   ├── src/routes/+page.svelte   # Web playground
│   ├── package.json
│   └── svelte.config.js
├── docs/
│   └── index.html            # Full documentation
├── INSTALL.md                # Installation guide
├── SYNTAX.md                 # Syntax cheat sheet
├── requirements.txt          # Python dependencies
└── README.md
```

---

## 🌐 Web Playground

Try HambaLang online tanpa install apapun!

```bash
cd web
npm install
npm run dev
```

Atau visit: [hambalang.vercel.app](https://hambalang.vercel.app) (coming soon)

Features:
- ✅ Code editor dengan syntax highlighting
- ✅ Live execution via Pyodide (Python in browser)
- ✅ Console output real-time
- ✅ Example programs
- ✅ No backend needed

---

## 📦 Examples Gallery

### Calculator
```hl
fungsi kalkulator(a, b, operasi)
    jika operasi == "+"
        kembalikan a + b
    ataujika operasi == "-"
        kembalikan a - b
    atau
        kembalikan 0
    akhir
akhir

hasil = kalkulator(10, 5, "+")
lapor "Hasil: " + teks(hasil)
```

### Database CRUD
```hl
sambungDB("proyek_db", "sqlite", "proyek.db")

create_sql = "CREATE TABLE IF NOT EXISTS proyek (id INTEGER PRIMARY KEY, nama TEXT, anggaran INTEGER)"
queryDB("proyek_db", create_sql)

insert_sql = "INSERT INTO proyek (nama, anggaran) VALUES ('Hambalang', 2500000000)"
queryDB("proyek_db", insert_sql)

select_sql = "SELECT * FROM proyek"
results = queryDB("proyek_db", select_sql)
lapor teks(results)

tutupDB("proyek_db")
```

### API Client
```hl
url = "https://jsonplaceholder.typicode.com/posts/1"
response = httpGet(url)

jika response["status"] == 200
    lapor "Success!"
    lapor teks(response["json"])
atau
    lapor "Failed!"
akhir
```

**More examples:** See [examples/](examples/) directory

---

## 🔧 API Reference

### Satire Functions

| Function | Parameters | Description |
|----------|-----------|-------------|
| `Mangkrak(ms)` | milliseconds | Delay + random event (vendor kabur, audit KPK, dll) |
| `Korupsi(persen)` | 0-100 | Mengurangi anggaran secara acak |
| `RapatInfinite()` | - | Infinite loop rapat (auto-stop demo) |
| `selesai()` | - | Terminate dengan status "Selesai di atas kertas" |

### Built-in Functions

| Function | Description |
|----------|-------------|
| `panjang(x)` | Get length of string/array/object |
| `tipe(x)` | Get type of variable |
| `angka(x)` | Convert to number |
| `teks(x)` | Convert to string |
| `tambahArray(arr, val)` | Add item to array |
| `hapusArray(arr, index)` | Remove item from array |

### Database Operations

- `sambungDB(nama, tipe, connection_string)` - Connect to database
- `queryDB(nama, sql)` - Execute SQL query
- `tutupDB(nama)` - Close connection

### File Operations

- `tulisFile(path, content)` - Write file
- `bacaFile(path)` - Read file

### HTTP Operations

- `httpGet(url)` - GET request
- `httpPost(url, data)` - POST request

---

## 🎓 Learning Path

1. **Basic Syntax** → Start with [examples/full_demo.hl](examples/full_demo.hl)
2. **Functions & Loops** → Try [examples/algorithms.hl](examples/algorithms.hl)
3. **File I/O** → Practice with [examples/file_io_example.hl](examples/file_io_example.hl)
4. **Database** → Build CRUD with [examples/database_example.hl](examples/database_example.hl)
5. **API Integration** → Make API calls with [examples/http_api_example.hl](examples/http_api_example.hl)

---

## 🚀 Deployment

### Run Locally
```bash
python interpreter/hamba_v2.py your_script.hl
```

### Web Playground (Vercel)
```bash
cd web
npm run build
vercel deploy
```

### Docker (Coming Soon)
```bash
docker build -t hambalang .
docker run hambalang your_script.hl
```

---

## 🤝 Contributing

Contributions welcome! Areas:

- 🎯 New satire keywords & features
- 🐛 Bug fixes & optimizations
- 📚 Documentation improvements
- 📝 Example programs
- 🌐 Language extensions

**How to contribute:**
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file

---

## 🙏 Credits

Created by [Your Name]

Inspired by:
- Proyek Hambalang (2011-2013)
- Indonesian bureaucracy & infrastructure projects
- Esoteric programming languages (Brainfuck, LOLCODE, ArnoldC)
- Real programming languages (Python, JavaScript, Go)

---

## 🌟 Showcase

Built with HambaLang? Share your project!

- Tag: `#HambaLang`
- Twitter: [@yourhandle](https://twitter.com/yourhandle)
- Discord: [Join Server](https://discord.gg/yourserver)

---

## 📞 Contact

- **Email:** your@email.com
- **Twitter:** [@yourhandle](https://twitter.com/yourhandle)
- **GitHub:** [@yourusername](https://github.com/yourusername)

---

<div align="center">

**Made with 🇮🇩 for Indonesian Developer Community**

*"Mangkrak, tapi beneran jalan!"*

[Documentation](docs/index.html) • [Examples](examples/) • [Web Playground](#) • [GitHub](#)

</div>
