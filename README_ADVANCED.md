# 🏗️ HambaLang - Advanced Edition

**Esoteric Programming Language - Satir Proyek Hambalang**

Bahasa pemrograman esoterik yang berkembang dari meme interpreter menjadi **esoteric-but-serious language** dengan fitur advanced, clean architecture, dan CTF-ready.

![Version](https://img.shields.io/badge/version-3.0--advanced-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-yellow)

---

## 🌟 Phase 2: Advanced Features

### ✨ Language Features

**Phase 1 (v2.0):**
- Variables, functions, loops, conditionals
- Arrays, objects, operators
- Database (SQLite/MySQL/PostgreSQL)
- File I/O, HTTP client
- Satire features (Korupsi, Mangkrak, RapatInfinite)

**Phase 2 (v3.0 Advanced) - NEW:**
- 🔷 **Scoped Blocks** (`mulai...akhir`) - Variabel lokal, nested scopes
- 🔷 **Prosedur Birokrasi** (`prosedur...akhirProsedur`) - Functions tanpa return
- 🔷 **Controlled Loops** (`Rapat(n)...selesaiRapat`) - Loop terjadwal
- 🔷 **Exception Handling** (`coba...jikaGagal...akhirCoba`) - Satire exceptions
- 🔷 **Custom Errors** - `ProyekMangkrakError`, `DanaHabisError`, `AuditKPKError`

### 🎯 Advanced Runtime

- **AST-based Interpreter** - Clean separation: Parser → AST → Evaluator
- **Deterministic Seed** (`--seed`) - Reproducible untuk CTF challenges
- **Step Limit** (`--step-limit`) - Anti infinite loop abuse
- **Debug Mode** (`--debug`) - Execution tracing per statement
- **Execution Delay** (`--delay`) - Speed control untuk visualisasi
- **CTF Mode** (`--ctf`) - Hidden flags di behavior Korupsi()
- **Fake Timeline** - Variable `tahun` increment per step

---

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/yourusername/HambaLang.git
cd HambaLang
pip install -r requirements.txt
```

### Basic Usage (v2)
```bash
python interpreter/hamba_v2.py examples/full_demo.hl
```

### Advanced Usage (v3)
```bash
# Demo fitur advanced
python interpreter/hamba_advanced.py examples/advanced_features.hl

# CTF mode dengan seed deterministik
python interpreter/hamba_advanced.py examples/advanced_ctf.hl --ctf --seed 42 --step-limit 800

# Debug mode dengan tracing
python interpreter/hamba_advanced.py examples/advanced_nested.hl --debug --delay 0.1

# Speed control untuk visualisasi
python interpreter/hamba_advanced.py examples/advanced_features.hl --delay 0.05
```

### Web Playground
```bash
# SvelteKit playground (v2)
cd web && npm install && npm run dev

# Standalone advanced playground
open web/playground_advanced.html
```

---

## 📝 Syntax Examples

### Scoped Blocks
```hambalang
mulai
  set fase = "Perencanaan"
  set budget = 2000000000
  lapor "Budget: Rp " + teks(budget)
  
  mulai
    set subFase = "Tender"
    Korupsi(10)
  akhir
akhir
```

### Prosedur (No Return)
```hambalang
prosedur LaporanAudit()
  lapor "[Audit] Memulai audit"
  Korupsi(5)
  set progress = progress + 10
  lapor "[Audit] Selesai"
akhirProsedur

LaporanAudit()
```

### Controlled Loops
```hambalang
Rapat(5)
  lapor "Rapat koordinasi ke-" + teks(progress)
  set progress = progress + 8
selesaiRapat
```

### Exception Handling
```hambalang
coba
  jika progress < 50
    Mangkrak("Progress kurang dari target")
  akhir
jikaGagal
  lapor "Diselamatkan dengan rapat darurat"
  Rapat(3)
    set progress = progress + 15
  selesaiRapat
akhirCoba
```

---

## 🏗️ Architecture

### Interpreter Pipeline (v3)
```
Source Code (.hl)
    ↓
Parser (line-based)
    ↓
AST Nodes (dataclasses)
    ↓
Evaluator (visitor-like)
    ↓
Runtime (scoped variables, procedures, step control)
    ↓
Output
```

### AST Nodes
- `Program` - Root node
- `Block` - Scoped block (`mulai...akhir`)
- `SetStmt` - Variable assignment
- `PrintStmt` - Output (`lapor`)
- `KorupsiStmt` - Korupsi satire
- `MangkrakStmt` - Mangkrak satire
- `RapatLoop` - Controlled loop
- `ProcDef` / `ProcCall` - Procedure definition/call
- `TryCatch` - Exception handling

### Runtime Features
- **Scope Stack** - Push/pop untuk nested blocks & procedures
- **Step Counter** - Limit untuk anti-abuse
- **Timeline Simulation** - `tahun` variable auto-increment
- **Korupsi Tracker** - Total tracking untuk CTF flags
- **Procedure Registry** - User-defined procedures
- **Expression Evaluator** - Recursive expression parser

---

## 🎮 CTF Mode

### Hidden Flag Mechanism
```python
if ctf_mode and int(korupsi_total) % 424242 == 0:
    print("FLAG{hambalang_ctf_korupsi}")
```

### Challenge Example
```hambalang
// Goal: Capai progress 100% tanpa habis anggaran
set anggaran = 500000000

Rapat(10)
  set progress = progress + 8
  Korupsi(4)  // Hati-hati: terlalu besar → bangkrut
selesaiRapat
```

Run:
```bash
python interpreter/hamba_advanced.py ctf_challenge.hl --ctf --seed 1337
```

---

## 📚 Documentation

- [README.md](README.md) - Main documentation (v2)
- [ADVANCED.md](docs/ADVANCED.md) - Phase 2 advanced features
- [SYNTAX.md](SYNTAX.md) - Syntax reference
- [QUICK_START.md](QUICK_START.md) - 5-minute tutorial
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Codebase overview

---

## 🎯 Use Cases

1. **Esoteric Language Portfolio** - Showcase interpreter engineering
2. **CTF Challenges** - Create puzzles dengan deterministic behavior
3. **Educational Tool** - Teach interpreter design dengan satire
4. **Satire Art** - Express bureaucratic frustration via code
5. **Code Golf** - Minimal code challenges dengan syntax unik

---

## 🔧 Development

### Run Tests
```bash
python tests/test_interpreter.py
```

### Docker
```bash
docker build -t hambalang .
docker run -v $(pwd)/examples:/app/examples hambalang python hamba_advanced.py examples/advanced_features.hl
```

### CI/CD
GitHub Actions automatically:
- Run tests on push
- Build web playground
- Validate syntax

---

## 📈 Roadmap

**Phase 2 (Current):**
- ✅ AST-based interpreter
- ✅ Scoped blocks & procedures
- ✅ Exception handling
- ✅ CTF mode
- ✅ Debug & speed control
- ✅ Advanced playground

**Phase 3 (Future):**
- [ ] Web playground dengan syntax highlighting
- [ ] Step-by-step debugger UI
- [ ] Shared permalink untuk code
- [ ] LSP (Language Server Protocol)
- [ ] Package manager (`paket install`)
- [ ] More CTF challenges

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

1. Fork repository
2. Create feature branch
3. Add tests
4. Submit PR

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

## 🎭 Philosophy

> "Dari proyek yang mangkrak,  
> Lahir bahasa yang berkah,  
> Satir birokrasi jadi kode,  
> RapatInfinite tiada mode."

HambaLang: Where bureaucratic satire meets serious interpreter engineering.

---

**Made with 💰 (korupsi) and ⏳ (mangkrak) in Indonesia**
