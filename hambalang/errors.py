"""
Hierarki error HambaLang.

Semua error yang bisa dilihat user turunan dari ``HambaError`` dan membawa
nomor baris/kolom supaya CLI bisa menampilkan potongan source dengan caret.
"""
from typing import Optional


class HambaError(Exception):
    """Base class untuk semua error HambaLang."""

    jenis = "HambaError"

    def __init__(self, message: str, line: Optional[int] = None, col: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.col = col

    def with_position(self, line: Optional[int], col: Optional[int] = None) -> "HambaError":
        """Isi posisi kalau belum ada (error dari builtin belum tahu barisnya)."""
        if self.line is None and line is not None:
            self.line = line
            self.col = col
        return self

    def __str__(self) -> str:
        where = f" (baris {self.line})" if self.line is not None else ""
        return f"[{self.jenis}]{where} {self.message}"


class SalahKetik(HambaError):
    """Syntax error: lexer/parser menolak source."""

    jenis = "SalahKetik"


class InputBelumLengkap(SalahKetik):
    """Source berakhir di tengah blok. Dipakai REPL untuk minta baris lanjutan."""

    jenis = "SalahKetik"


class OperasiIlegal(HambaError):
    """Runtime error umum (tipe salah, variabel tidak ada, index di luar range)."""

    jenis = "OperasiIlegal"


class ProyekMangkrak(HambaError):
    """Error yang dilempar program sendiri lewat ``Mangkrak "pesan"``."""

    jenis = "ProyekMangkrak"


class NegaraBangkrut(HambaError):
    """Batas langkah eksekusi habis. Sengaja tidak bisa ditangkap ``coba``."""

    jenis = "NegaraBangkrut"


class ProgramSelesai(Exception):
    """Sinyal internal untuk ``selesai()``: hentikan program dengan normal."""
