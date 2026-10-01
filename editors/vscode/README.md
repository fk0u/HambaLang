# HambaLang untuk VS Code

Syntax highlighting, komentar, bracket matching, auto-indent, dan folding
untuk file `.hl` (semua dialek: v2, advanced, formal v5).

## Instalasi lokal

```bash
# dari root repo
rm -rf ~/.vscode/extensions/hambalang-6.0.0
mkdir -p ~/.vscode/extensions
cp -r editors/vscode ~/.vscode/extensions/hambalang-6.0.0
# restart VS Code
```

Atau paketkan: `npx @vscode/vsce package` di folder ini lalu
*Extensions → … → Install from VSIX*.

## Catatan

VS Code hanya mendukung satu jenis komentar baris untuk *Toggle Line Comment*
(Ctrl+/), jadi perintah itu memakai `//`. Komentar `#` tetap di-highlight
dengan benar, tetapi tidak di-toggle oleh Ctrl+/.
