# Instalasi HambaLang

## Kebutuhan

- Python 3.9+
- (opsional) Node.js 18+ untuk playground web

## Dari source

```bash
git clone https://github.com/fk0u/HambaLang.git
cd HambaLang
pip install -e .              # core, tanpa dependency
hambalang --version
hambalang run examples/full_demo.hl --fast
```

Tanpa install sama sekali:

```bash
python -m hambalang run examples/full_demo.hl
python cli/hambalang.py run examples/full_demo.hl      # perintah lama, masih didukung
```

## Fitur opsional

| Extra | Untuk | Perintah |
|-------|-------|----------|
| `http` | `httpGet`, `httpPost` | `pip install -e ".[http]"` |
| `db` | `sambungDB(..., "mysql" / "postgres")` | `pip install -e ".[db]"` |
| `dev` | pytest, ruff | `pip install -e ".[dev]"` |

SQLite sudah bawaan Python, tidak perlu install apa pun.

Koneksi MySQL memakai string `"host=localhost user=root password=x database=db"`;
PostgreSQL memakai DSN standar psycopg2.

## Docker

```bash
docker build -t hambalang .
docker run --rm hambalang                                    # demo
docker run --rm -v "$PWD:/src" hambalang run /src/program.hl
docker run --rm -it hambalang repl
```

## Playground web

```bash
cd web
npm install
npm run dev        # menyalin ../hambalang ke static/ lalu menjalankan Vite
npm run build      # output statis di web/build (siap deploy Vercel/Netlify)
```

## Verifikasi

```bash
pip install -e ".[dev]"
pytest
hambalang check examples/*.hl ctf/*.hl
```
