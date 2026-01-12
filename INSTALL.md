# HambaLang Installation Guide

## Requirements

- Python 3.8 or higher
- pip (Python package manager)

## Basic Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/hambalang.git
cd hambalang
```

### 2. Run Basic Programs

No additional dependencies needed for basic features:

```bash
python interpreter/hamba_v2.py examples/full_demo.hl
```

## Advanced Features Installation

### Database Support

**SQLite** (Built-in, no installation needed)

**MySQL:**
```bash
pip install mysql-connector-python
```

**PostgreSQL:**
```bash
pip install psycopg2-binary
```

### HTTP/API Support

```bash
pip install requests
```

### All Dependencies

Install everything at once:

```bash
pip install requests mysql-connector-python psycopg2-binary
```

## Web Playground Installation

### Requirements
- Node.js 18+ and npm

### Steps

```bash
cd web
npm install
npm run dev
```

Access at: `http://localhost:5173`

### Build for Production

```bash
npm run build
```

## Verify Installation

Run test script:

```bash
python interpreter/hamba_v2.py examples/full_demo.hl
```

Expected output:
```
🏗️  Menjalankan: examples/full_demo.hl
==================================================
=== HAMBALANG v2.0 - COMPLETE DEMO ===
...
✅ Eksekusi selesai
```

## Troubleshooting

### Python Not Found
- Install Python from [python.org](https://python.org)
- Add Python to PATH

### Module Not Found
```bash
pip install --upgrade pip
pip install -r requirements.txt  # if available
```

### Permission Denied
Use virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install <package>
```

## Platform-Specific Notes

### Windows
- Use PowerShell or CMD
- Python command might be `py` instead of `python`

### Linux/Mac
- May need `python3` instead of `python`
- May need `sudo` for system-wide installs

### Docker (Coming Soon)
```bash
docker pull hambalang/interpreter
docker run -v $(pwd):/code hambalang/interpreter your_script.hl
```

## Next Steps

After installation:

1. Read [README.md](../README.md) for overview
2. Open [docs/index.html](../docs/index.html) for full documentation
3. Try examples in [examples/](../examples/) directory
4. Visit web playground

## Support

Issues? [Open an issue](https://github.com/yourusername/hambalang/issues)
