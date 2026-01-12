# HambaLang Web Interface

Web-based interpreter untuk HambaLang menggunakan SvelteKit + Pyodide.

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
3. Framework preset: SvelteKit
4. Build command: `npm run build`
5. Output directory: `build`

## Tech Stack

- SvelteKit (Static Adapter)
- Pyodide 0.25.0 (Python in browser)
- Vite
