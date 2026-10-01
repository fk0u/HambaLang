# HambaLang Web Interface

Playground HambaLang berbasis SvelteKit + Pyodide.

Playground **tidak** punya interpreter sendiri: `scripts/sync-core.mjs`
(dijalankan otomatis oleh `npm run dev/build/check`) menyalin paket Python
`../hambalang/` ke `static/hambalang/`, lalu Pyodide memuatnya di browser.
Artinya interpreter, HambaVM v4, stdlib, dan pesan error di browser sama
persis dengan CLI. Program berjalan dalam mode sandbox (file/DB/HTTP
dimatikan) dengan batas 200.000 langkah. Pyodide dimuat dari CDN jsDelivr.

## Development

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Deploy ke Vercel

1. Push ke GitHub
2. Import project di Vercel
3. Root directory: `web` (folder `../hambalang` harus ikut ter-clone)
4. Framework preset: SvelteKit
5. Build command: `npm run build`
6. Output directory: `build`

## Tech Stack

- SvelteKit (Static Adapter)
- Pyodide 0.25.0 (Python in browser)
- Vite
