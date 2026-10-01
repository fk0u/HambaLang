"""
Format bytecode HambaLang v4 (``.hbc``).

Layout file (little-endian)::

    magic   4B  b"HBC\\x00"
    version u16 = 4
    code    CodeObject

    CodeObject:
        name   str          kind   str        params  u16 + str*
        instrs u32 + (u8 opcode, u32 arg)*
        lines  u32 per instruksi
        consts u16 + const*

    const = tag u8 + payload
        'N' kosong | 'T' benar | 'F' salah | 'I' i64 | 'B' bigint (str)
        'D' f64    | 'S' str   | 'C' CodeObject
    str = u32 panjang + utf-8

Header v4 sengaja kompatibel dengan v3 (magic sama, versi u16 di offset 4)
sehingga CLI bisa membedakan bytecode legacy dan bytecode baru.
"""
import struct
from dataclasses import dataclass, field
from typing import Any, BinaryIO, List, Tuple

MAGIC = b"HBC\x00"
VERSION = 4

# ---------------------------------------------------------------- opcodes
OPCODES = [
    "NOP", "LOAD_CONST", "LOAD_NAME", "STORE_NAME", "POP", "DUP", "DUP2",
    "BINARY", "UNARY", "INDEX_GET", "INDEX_SET", "ATTR_GET", "ATTR_SET",
    "BUILD_LIST", "BUILD_DICT", "CALL", "RETURN", "PRINT",
    "JUMP", "JUMP_IF_FALSE", "JUMP_IF_FALSE_OR_POP", "JUMP_IF_TRUE_OR_POP",
    "MAKE_FUNCTION", "PUSH_SCOPE", "POP_SCOPE", "SETUP_TRY", "POP_TRY", "RAISE",
    "GET_ITER", "RANGE_ITER", "REPEAT_ITER", "FOR_ITER",
    "INPUT", "GLOBAL", "HALT", "LINE",
]
for _i, _name in enumerate(OPCODES):
    globals()[_name] = _i

# Opcode yang argumennya alamat jump (dipakai disassembler).
JUMP_OPS = {"JUMP", "JUMP_IF_FALSE", "JUMP_IF_FALSE_OR_POP", "JUMP_IF_TRUE_OR_POP",
            "SETUP_TRY", "FOR_ITER"}
# Opcode yang argumennya index konstanta.
CONST_OPS = {"LOAD_CONST", "LOAD_NAME", "STORE_NAME", "ATTR_GET", "ATTR_SET",
             "MAKE_FUNCTION", "GLOBAL"}

BINARY_OPS = ["+", "-", "*", "/", "%", "**", "==", "!=", "<", ">", "<=", ">="]
UNARY_OPS = ["-", "bukan"]


@dataclass
class CodeObject:
    name: str
    kind: str = "modul"  # 'modul' | 'fungsi' | 'prosedur'
    params: List[str] = field(default_factory=list)
    code: List[Tuple[int, int]] = field(default_factory=list)
    lines: List[int] = field(default_factory=list)
    consts: List[Any] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"<kode {self.name}>"


class BytecodeError(Exception):
    pass


# ---------------------------------------------------------- serialization
def _w_str(f: BinaryIO, s: str):
    data = s.encode("utf-8")
    f.write(struct.pack("<I", len(data)))
    f.write(data)


def _r_exact(f: BinaryIO, n: int) -> bytes:
    data = f.read(n)
    if len(data) != n:
        raise BytecodeError("File bytecode terpotong")
    return data


def _r_str(f: BinaryIO) -> str:
    (n,) = struct.unpack("<I", _r_exact(f, 4))
    return _r_exact(f, n).decode("utf-8")


def _w_code(f: BinaryIO, co: CodeObject):
    if len(co.lines) != len(co.code):
        raise BytecodeError(f"'{co.name}': tabel baris ({len(co.lines)}) tidak sama dengan "
                            f"jumlah instruksi ({len(co.code)})")
    if len(co.consts) > 0xFFFF or len(co.params) > 0xFFFF:
        raise BytecodeError(f"'{co.name}' punya terlalu banyak konstanta untuk format HBC v4")
    _w_str(f, co.name)
    _w_str(f, co.kind)
    f.write(struct.pack("<H", len(co.params)))
    for p in co.params:
        _w_str(f, p)
    f.write(struct.pack("<I", len(co.code)))
    for op, arg in co.code:
        f.write(struct.pack("<BI", op, arg))
    for line in co.lines:
        f.write(struct.pack("<I", line))
    f.write(struct.pack("<H", len(co.consts)))
    for c in co.consts:
        _w_const(f, c)


def _w_const(f: BinaryIO, c: Any):
    if c is None:
        f.write(b"N")
    elif c is True:
        f.write(b"T")
    elif c is False:
        f.write(b"F")
    elif isinstance(c, int):
        if -(2 ** 63) <= c < 2 ** 63:
            f.write(b"I" + struct.pack("<q", c))
        else:
            # Bigint: byte two's-complement (tidak kena batas digit konversi str<->int).
            data = c.to_bytes((c.bit_length() + 8) // 8, "little", signed=True)
            f.write(b"B" + struct.pack("<I", len(data)))
            f.write(data)
    elif isinstance(c, float):
        f.write(b"D" + struct.pack("<d", c))
    elif isinstance(c, str):
        f.write(b"S")
        _w_str(f, c)
    elif isinstance(c, CodeObject):
        f.write(b"C")
        _w_code(f, c)
    else:
        raise BytecodeError(f"Konstanta tidak bisa diserialisasi: {c!r}")


def _r_code(f: BinaryIO) -> CodeObject:
    name = _r_str(f)
    kind = _r_str(f)
    (np,) = struct.unpack("<H", _r_exact(f, 2))
    params = [_r_str(f) for _ in range(np)]
    (n,) = struct.unpack("<I", _r_exact(f, 4))
    code = [struct.unpack("<BI", _r_exact(f, 5)) for _ in range(n)]
    for op, _ in code:
        if op >= len(OPCODES):
            raise BytecodeError(f"Opcode tidak dikenal: {op}")
    lines = [struct.unpack("<I", _r_exact(f, 4))[0] for _ in range(n)]
    (nc,) = struct.unpack("<H", _r_exact(f, 2))
    consts = [_r_const(f) for _ in range(nc)]
    co = CodeObject(name, kind, params, [tuple(c) for c in code], lines, consts)
    _validate(co)
    return co


_NAME_OPS = {"LOAD_NAME", "STORE_NAME", "ATTR_GET", "ATTR_SET", "GLOBAL"}


def _validate(co: CodeObject):
    """Tolak bytecode rusak saat load, bukan crash IndexError saat eksekusi."""
    n = len(co.code)
    if co.kind not in ("modul", "fungsi", "prosedur"):
        raise BytecodeError(f"'{co.name}': jenis kode tidak dikenal: {co.kind!r}")
    if n == 0 or OPCODES[co.code[-1][0]] not in ("RETURN", "JUMP", "HALT"):
        raise BytecodeError(f"'{co.name}': kode tidak diakhiri RETURN")
    for i, (op, arg) in enumerate(co.code):
        name = OPCODES[op]
        bad = None
        if name in CONST_OPS:
            if arg >= len(co.consts):
                bad = f"index konstanta {arg} di luar jangkauan"
            elif name in _NAME_OPS and not isinstance(co.consts[arg], str):
                bad = "operand nama harus teks"
            elif name == "MAKE_FUNCTION" and not isinstance(co.consts[arg], CodeObject):
                bad = "MAKE_FUNCTION butuh konstanta kode"
        elif name in JUMP_OPS and arg >= n:
            bad = f"alamat lompat {arg} di luar kode"
        elif name == "BINARY" and arg >= len(BINARY_OPS):
            bad = f"operator biner {arg} tidak dikenal"
        elif name == "UNARY" and arg >= len(UNARY_OPS):
            bad = f"operator unary {arg} tidak dikenal"
        if bad:
            raise BytecodeError(f"'{co.name}' instruksi {i} ({name}): {bad}")


def _r_const(f: BinaryIO) -> Any:
    tag = _r_exact(f, 1)
    if tag == b"N":
        return None
    if tag == b"T":
        return True
    if tag == b"F":
        return False
    if tag == b"I":
        return struct.unpack("<q", _r_exact(f, 8))[0]
    if tag == b"B":
        (n,) = struct.unpack("<I", _r_exact(f, 4))
        return int.from_bytes(_r_exact(f, n), "little", signed=True)
    if tag == b"D":
        return struct.unpack("<d", _r_exact(f, 8))[0]
    if tag == b"S":
        return _r_str(f)
    if tag == b"C":
        return _r_code(f)
    raise BytecodeError(f"Tag konstanta tidak dikenal: {tag!r}")


def dump(co: CodeObject, f: BinaryIO):
    f.write(MAGIC)
    f.write(struct.pack("<H", VERSION))
    _w_code(f, co)


def dumps(co: CodeObject) -> bytes:
    import io
    buf = io.BytesIO()
    dump(co, buf)
    return buf.getvalue()


def save(co: CodeObject, path: str):
    with open(path, "wb") as f:
        dump(co, f)


def read_version(path: str) -> int:
    """Versi bytecode di file (3 = legacy HambaVM, 4 = format ini)."""
    with open(path, "rb") as f:
        head = f.read(6)
    if len(head) < 6 or head[:4] != MAGIC:
        raise BytecodeError("Bukan file bytecode HambaLang (magic salah)")
    return struct.unpack("<H", head[4:6])[0]


def load(path: str) -> CodeObject:
    with open(path, "rb") as f:
        return loads_from(f)


def loads(data: bytes) -> CodeObject:
    import io
    return loads_from(io.BytesIO(data))


def loads_from(f: BinaryIO) -> CodeObject:
    try:
        return _loads_from(f)
    except BytecodeError:
        raise
    except (UnicodeDecodeError, struct.error, ValueError, OverflowError, RecursionError) as e:
        raise BytecodeError(f"Bytecode rusak: {e}") from None


def _loads_from(f: BinaryIO) -> CodeObject:
    if f.read(4) != MAGIC:
        raise BytecodeError("Bukan file bytecode HambaLang (magic salah)")
    (version,) = struct.unpack("<H", _r_exact(f, 2))
    if version != VERSION:
        raise BytecodeError(f"Versi bytecode {version} tidak didukung HambaVM v4")
    return _r_code(f)


# ------------------------------------------------------------ disassembler
def disassemble(co: CodeObject) -> str:
    out: List[str] = []
    _disasm(co, out)
    return "\n".join(out)


def _disasm(co: CodeObject, out: List[str]):
    from hambalang.runtime import repr_value
    params = ", ".join(co.params)
    out.append(f"== {co.kind} {co.name}({params}) — {len(co.code)} instruksi, {len(co.consts)} konstanta ==")
    targets = {arg for op, arg in co.code if OPCODES[op] in JUMP_OPS}
    last_line = None
    for i, (op, arg) in enumerate(co.code):
        name = OPCODES[op]
        line = co.lines[i] if i < len(co.lines) else 0
        line_col = f"{line:>4}" if line != last_line else "    "
        last_line = line
        marker = ">>" if i in targets else "  "
        text = f"{line_col} {marker} {i:>4} {name:<22}"
        if name in CONST_OPS:
            c = co.consts[arg]
            shown = c.name if isinstance(c, CodeObject) else repr_value(c)
            text += f"{arg:<4} ({shown})"
        elif name in JUMP_OPS:
            text += f"-> {arg}"
        elif name == "BINARY":
            text += f"{arg:<4} ({BINARY_OPS[arg]})"
        elif name == "UNARY":
            text += f"{arg:<4} ({UNARY_OPS[arg]})"
        elif name in ("BUILD_LIST", "BUILD_DICT", "CALL", "INPUT", "LINE"):
            text += str(arg)
        out.append(text.rstrip())
    for c in co.consts:
        if isinstance(c, CodeObject):
            out.append("")
            _disasm(c, out)
