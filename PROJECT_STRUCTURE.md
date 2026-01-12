# HambaLang v2.0 - Project Structure

```
HambaLang/
│
├── 📁 interpreter/              # Core interpreters
│   ├── hamba.py                # Original v1.0 interpreter
│   └── hamba_v2.py             # Full-featured v2.0 interpreter ⭐
│
├── 📁 examples/                 # Example programs (.hl files)
│   ├── demo.hl                 # Basic demo (v1.0)
│   ├── full_demo.hl            # Complete feature showcase ⭐
│   ├── algorithms.hl           # Algorithm examples
│   ├── database_example.hl     # Database CRUD operations
│   ├── file_io_example.hl      # File I/O operations
│   ├── http_api_example.hl     # REST API client
│   ├── crud_app.hl             # Real-world CRUD application ⭐
│   ├── corruption.hl           # Satire demo
│   └── infinite.hl             # RapatInfinite demo
│
├── 📁 web/                      # Web playground (SvelteKit)
│   ├── src/
│   │   └── routes/
│   │       ├── +page.svelte    # Main playground page ⭐
│   │       └── +layout.js      # Layout config
│   ├── static/                 # Static assets
│   ├── package.json            # Node dependencies
│   ├── svelte.config.js        # SvelteKit config
│   ├── vite.config.js          # Vite config
│   ├── vercel.json             # Vercel deployment config
│   ├── jsconfig.json           # JavaScript config
│   └── README.md               # Web-specific docs
│
├── 📁 docs/                     # Documentation website
│   └── index.html              # Full HTML documentation ⭐
│
├── 📁 tests/                    # Test suite
│   └── test_interpreter.py     # Interpreter unit tests
│
├── 📁 .github/                  # GitHub configuration
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI/CD
│
├── 📄 README.md                 # Main documentation ⭐
├── 📄 INSTALL.md                # Installation guide
├── 📄 SYNTAX.md                 # Syntax cheat sheet
├── 📄 CHANGELOG.md              # Version history
├── 📄 CONTRIBUTING.md           # Contribution guidelines
├── 📄 LICENSE                   # MIT License
├── 📄 requirements.txt          # Python dependencies
├── 📄 Dockerfile                # Docker configuration
└── 📄 .gitignore                # Git ignore rules

```

## Key Files (⭐)

### 1. **interpreter/hamba_v2.py**
Main interpreter dengan full features:
- Variables, functions, loops, arrays, objects
- Database support (SQLite, MySQL, PostgreSQL)
- File I/O operations
- HTTP/REST API client
- Built-in functions
- Satire features

### 2. **examples/full_demo.hl**
Comprehensive example showcasing all features

### 3. **examples/crud_app.hl**
Real-world CRUD application example

### 4. **web/src/routes/+page.svelte**
Web playground interface with code editor

### 5. **docs/index.html**
Complete HTML documentation with:
- Syntax reference
- API documentation
- Examples
- Tutorials

### 6. **README.md**
Main project documentation with:
- Feature overview
- Quick start guide
- Usage examples
- API reference

## File Types

- `.hl` - HambaLang source code files
- `.py` - Python interpreter code
- `.svelte` - Svelte components (web UI)
- `.md` - Markdown documentation
- `.json` - Configuration files
- `.html` - HTML documentation

## Dependencies

### Python (Interpreter)
- Python 3.8+
- requests (HTTP operations)
- mysql-connector-python (MySQL support)
- psycopg2-binary (PostgreSQL support)

### Node.js (Web Playground)
- Node.js 18+
- SvelteKit
- Pyodide (Python in browser)
- Vite

## Quick Navigation

**Want to...**
- **Run HambaLang programs?** → `interpreter/hamba_v2.py`
- **See examples?** → `examples/` directory
- **Read documentation?** → `docs/index.html` or `README.md`
- **Contribute?** → `CONTRIBUTING.md`
- **Learn syntax?** → `SYNTAX.md`
- **Deploy web?** → `web/` directory
- **Run tests?** → `tests/test_interpreter.py`

## Total Files Created

- **Interpreters:** 2 files
- **Examples:** 9 .hl files
- **Web UI:** 8 files
- **Documentation:** 6 files
- **Tests:** 1 file
- **Config:** 5 files
- **Total:** ~31 files

## Lines of Code (Approximate)

- **Python (Interpreter):** ~800 lines
- **HambaLang (.hl):** ~1000+ lines
- **Svelte (Web UI):** ~400 lines
- **HTML (Docs):** ~700 lines
- **Documentation:** ~2000+ lines
- **Total:** ~4900+ lines

## Technologies Used

1. **Python** - Interpreter
2. **SvelteKit** - Web framework
3. **Pyodide** - Python in browser (WASM)
4. **SQLite/MySQL/PostgreSQL** - Databases
5. **Vite** - Build tool
6. **Vercel** - Deployment platform
7. **Docker** - Containerization
8. **GitHub Actions** - CI/CD

---

**Project Status:** ✅ Production Ready

**Version:** 2.0.0

**Last Updated:** January 12, 2026
