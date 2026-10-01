"""
Lexer HambaLang.

Mengubah source menjadi daftar ``Token``. Newline signifikan (statement
diakhiri newline), kecuali di dalam ``(...)`` atau ``[...]``. Kurung kurawal
tidak menekan newline karena ``{`` dipakai untuk blok (dialek Sita/Proyek)
sekaligus literal objek; parser yang melewati newline di dalam literal objek.
"""
from dataclasses import dataclass
from typing import List

from hambalang.errors import InputBelumLengkap, SalahKetik

# Token types
NAME = "NAME"
NUMBER = "NUMBER"
STRING = "STRING"
OP = "OP"
NEWLINE = "NEWLINE"
EOF = "EOF"

# Kata kunci tidak boleh dipakai sebagai nama variabel.
KEYWORDS = {
    # struktur v2
    "jika", "maka", "ataujika", "atau", "akhir", "selama", "untuk", "dari", "sampai",
    "langkah", "dalam", "fungsi", "kembalikan", "hentikan", "lanjut", "lapor", "print",
    "dan", "bukan", "benar", "salah", "kosong", "global",
    # dialek advanced
    "set", "mulai", "coba", "jikaGagal", "akhirCoba", "prosedur", "akhirProsedur",
    "selesaiRapat",
    # dialek formal v5
    "Bubarkan", "Anggaran", "Tagih", "Sita", "Pengadilan", "Proyek", "BagiRata", "Janji",
    "Wacana", "DAN", "ATAU", "BUKAN", "BENAR", "SALAH", "KOSONG",
}

# Operator diurutkan dari yang terpanjang supaya ``<=`` tidak terbaca ``<`` ``=``.
OPERATORS = [
    "**", "==", "!=", "<=", ">=", "+=", "-=", "*=", "/=", "%=",
    "+", "-", "*", "/", "%", "<", ">", "=", "!",
    "(", ")", "[", "]", "{", "}", ",", ":", ".",
]

ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"', "'": "'", "0": "\0"}


@dataclass
class Token:
    type: str
    value: object
    line: int
    col: int
    spaced: bool = False  # ada whitespace sebelum token ini (di baris yang sama)

    def is_op(self, *values: str) -> bool:
        return self.type == OP and self.value in values

    def is_name(self, *values: str) -> bool:
        return self.type == NAME and self.value in values

    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value!r}, {self.line}:{self.col})"


class Lexer:
    def __init__(self, source: str):
        # Normalisasi line ending dan buang BOM.
        self.src = source.replace("\r\n", "\n").replace("\r", "\n").lstrip("﻿")
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: List[Token] = []
        self.depth = 0  # kedalaman () dan []
        self.open_brackets: List[Token] = []

    def error(self, msg: str) -> SalahKetik:
        return SalahKetik(msg, self.line, self.col)

    def peek(self, offset: int = 0) -> str:
        i = self.pos + offset
        return self.src[i] if i < len(self.src) else ""

    def advance(self) -> str:
        ch = self.src[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def add(self, type_: str, value, line: int, col: int, spaced: bool):
        self.tokens.append(Token(type_, value, line, col, spaced))

    def tokenize(self) -> List[Token]:
        spaced = False
        while self.pos < len(self.src):
            ch = self.peek()

            if ch in " \t":
                self.advance()
                spaced = True
                continue

            if ch == "\n":
                line, col = self.line, self.col
                self.advance()
                if self.depth == 0:
                    self._add_newline(line, col)
                spaced = False
                continue

            # Komentar baris: // ... atau # ...
            if (ch == "/" and self.peek(1) == "/") or ch == "#":
                while self.pos < len(self.src) and self.peek() != "\n":
                    self.advance()
                continue

            # Komentar blok: /* ... */
            if ch == "/" and self.peek(1) == "*":
                start_line = self.line
                self.advance()
                self.advance()
                while not (self.peek() == "*" and self.peek(1) == "/"):
                    if self.pos >= len(self.src):
                        raise InputBelumLengkap("Komentar /* tidak ditutup", start_line)
                    self.advance()
                self.advance()
                self.advance()
                spaced = True
                continue

            # Titik koma = pemisah statement, sama seperti newline.
            if ch == ";":
                line, col = self.line, self.col
                self.advance()
                self._add_newline(line, col)
                spaced = False
                continue

            line, col = self.line, self.col
            if ch.isdigit() or (ch == "." and self.peek(1).isdigit()):
                self.add(NUMBER, self._number(), line, col, spaced)
            elif ch in "\"'":
                self.add(STRING, self._string(), line, col, spaced)
            elif ch.isalpha() or ch == "_":
                self.add(NAME, self._name(), line, col, spaced)
            else:
                for op in OPERATORS:
                    if self.src.startswith(op, self.pos):
                        for _ in op:
                            self.advance()
                        self.add(OP, op, line, col, spaced)
                        if op in "([":
                            self.depth += 1
                            self.open_brackets.append(self.tokens[-1])
                        elif op in ")]" and self.depth > 0:
                            self.depth -= 1
                            self.open_brackets.pop()
                        break
                else:
                    raise self.error(f"Karakter tidak dikenal: {ch!r}")
            spaced = False

        if self.open_brackets:
            t = self.open_brackets[-1]
            raise InputBelumLengkap(f"Kurung '{t.value}' belum ditutup", t.line, t.col)
        self._add_newline(self.line, self.col)
        self.add(EOF, None, self.line, self.col, False)
        return self.tokens

    def _add_newline(self, line: int, col: int):
        # Gabungkan newline berturut-turut.
        if self.tokens and self.tokens[-1].type != NEWLINE:
            self.add(NEWLINE, None, line, col, False)

    def _number(self):
        start = self.pos
        is_float = False
        while self.peek().isdigit() or self.peek() == "_":
            self.advance()
        if self.peek() == "." and self.peek(1).isdigit():
            is_float = True
            self.advance()
            while self.peek().isdigit() or self.peek() == "_":
                self.advance()
        if self.peek() in "eE" and (self.peek(1).isdigit() or (self.peek(1) in "+-" and self.peek(2).isdigit())):
            is_float = True
            self.advance()
            if self.peek() in "+-":
                self.advance()
            while self.peek().isdigit():
                self.advance()
        text = self.src[start:self.pos].replace("_", "")
        if self.peek().isalpha() or self.peek() == "_":
            raise self.error(f"Angka tidak valid: {text}{self.peek()}")
        return float(text) if is_float else int(text)

    def _string(self) -> str:
        quote = self.advance()
        start_line = self.line
        out = []
        while True:
            if self.pos >= len(self.src):
                raise InputBelumLengkap("String tidak ditutup", start_line)
            ch = self.advance()
            if ch == quote:
                return "".join(out)
            if ch == "\\":
                if self.pos >= len(self.src):
                    raise SalahKetik("String tidak ditutup", start_line)
                esc = self.advance()
                out.append(ESCAPES.get(esc, "\\" + esc))
            else:
                out.append(ch)

    def _name(self) -> str:
        start = self.pos
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()
        return self.src[start:self.pos]


def tokenize(source: str) -> List[Token]:
    return Lexer(source).tokenize()
