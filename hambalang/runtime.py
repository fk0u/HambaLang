"""
Runtime bersama untuk tree-walking interpreter dan HambaVM v4.

Isinya: representasi nilai (fungsi, builtin), environment/scope, konversi
nilai, semantik operator, dan state "negara" (anggaran, progress, dsb).
Interpreter dan VM wajib memakai fungsi-fungsi di sini supaya semantiknya
identik — test suite membandingkan output keduanya.
"""
import contextlib
import json
import math
import operator
import random
import sys
import time
from typing import Any, Callable, Dict, List, Optional

from hambalang.errors import NegaraBangkrut, OperasiIlegal

ANGGARAN_AWAL = 1_000_000_000

# Variabel bawaan yang selalu global dan disimpan di state runtime.
STATE_VARS = ("anggaran", "progress", "status_proyek", "total_korupsi")


# ===================================================================== values

class HambaFunction:
    """Fungsi buatan user. ``body`` dipakai interpreter, ``code`` dipakai VM."""

    __slots__ = ("name", "params", "kind", "closure", "body", "code")

    def __init__(self, name: str, params: List[str], kind: str, closure: "Env",
                 body=None, code=None):
        self.name = name
        self.params = params
        self.kind = kind
        self.closure = closure
        self.body = body
        self.code = code

    def __repr__(self) -> str:
        return f"<{self.kind} {self.name}({', '.join(self.params)})>"


class Builtin:
    __slots__ = ("name", "fn", "min_args", "max_args")

    def __init__(self, name: str, fn: Callable, min_args: int, max_args: Optional[int]):
        self.name = name
        self.fn = fn
        self.min_args = min_args
        self.max_args = max_args

    def __call__(self, rt: "Runtime", args: List[Any]) -> Any:
        n = len(args)
        if n < self.min_args or (self.max_args is not None and n > self.max_args):
            if self.min_args == self.max_args:
                expected = str(self.min_args)
            elif self.max_args is None:
                expected = f"minimal {self.min_args}"
            else:
                expected = f"{self.min_args}-{self.max_args}"
            raise OperasiIlegal(f"{self.name}() butuh {expected} argumen, diberikan {n}")
        return self.fn(rt, *args)

    def __repr__(self) -> str:
        return f"<builtin {self.name}>"


# ================================================================ environment

class Env:
    """
    Scope variabel.

    * Scope fungsi (``is_function=True``): assignment ke nama yang belum ada di
      dalam fungsi membuat variabel lokal (seperti Python). Pakai ``global x``
      untuk menulis ke global.
    * Scope blok (``mulai``, ``prosedur``): assignment memperbarui variabel di
      scope terdekat yang sudah punya nama itu, baru membuat lokal kalau belum
      ada di mana pun.
    """

    __slots__ = ("vars", "parent", "is_function", "global_names")

    def __init__(self, parent: Optional["Env"] = None, is_function: bool = False):
        self.vars: Dict[str, Any] = {}
        self.parent = parent
        self.is_function = is_function
        self.global_names: Optional[set] = None

    def root(self) -> "Env":
        e = self
        while e.parent is not None:
            e = e.parent
        return e

    def lookup(self, name: str) -> Any:
        e: Optional[Env] = self
        while e is not None:
            if name in e.vars:
                return e.vars[name]
            e = e.parent
        raise KeyError(name)

    def has(self, name: str) -> bool:
        e: Optional[Env] = self
        while e is not None:
            if name in e.vars:
                return True
            e = e.parent
        return False

    def assign(self, name: str, value: Any):
        e: Optional[Env] = self
        while e is not None:
            if name in e.vars:
                e.vars[name] = value
                return
            if e.is_function:
                if e.global_names and name in e.global_names:
                    self.root().vars[name] = value
                    return
                break
            e = e.parent
        self.vars[name] = value

    def define(self, name: str, value: Any):
        self.vars[name] = value

    def declare_global(self, names: List[str]):
        e: Optional[Env] = self
        while e is not None and not e.is_function:
            e = e.parent
        if e is None:
            return  # sudah di top-level
        if e.global_names is None:
            e.global_names = set()
        e.global_names.update(names)


# ================================================================ conversions

def is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def format_number(v: Any) -> str:
    if isinstance(v, int):
        return str(v)
    if math.isnan(v):
        return "NaN"
    if math.isinf(v):
        return "TakHingga" if v > 0 else "-TakHingga"
    if v.is_integer() and abs(v) < 1e16:
        return str(int(v))
    return format(v, ".15g")


def to_str(v: Any) -> str:
    """Konversi nilai ke teks untuk ``lapor`` / ``teks()``."""
    if isinstance(v, str):
        return v
    return repr_value(v)


def repr_value(v: Any) -> str:
    """Representasi nilai di dalam daftar/objek (teks diberi kutip)."""
    if v is None:
        return "kosong"
    if v is True:
        return "benar"
    if v is False:
        return "salah"
    if isinstance(v, (int, float)):
        return format_number(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        return "[" + ", ".join(repr_value(x) for x in v) + "]"
    if isinstance(v, tuple):
        return "[" + ", ".join(repr_value(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{json.dumps(str(k), ensure_ascii=False)}: {repr_value(x)}"
                              for k, x in v.items()) + "}"
    if isinstance(v, (HambaFunction, Builtin)):
        return repr(v)
    return str(v)


def truthy(v: Any) -> bool:
    if v is None or v is False:
        return False
    if v is True:
        return True
    if isinstance(v, (int, float)):
        return v != 0
    if isinstance(v, (str, list, dict, tuple)):
        return len(v) > 0
    return True


def type_name(v: Any) -> str:
    if v is None:
        return "kosong"
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, (int, float)):
        return "angka"
    if isinstance(v, str):
        return "teks"
    if isinstance(v, (list, tuple)):
        return "daftar"
    if isinstance(v, dict):
        return "objek"
    if isinstance(v, (HambaFunction, Builtin)):
        return "fungsi"
    return type(v).__name__


def parse_number(s: str) -> Any:
    """Teks -> angka. Mengembalikan None kalau bukan angka."""
    s = s.strip().replace("_", "")
    try:
        return int(s)
    except ValueError:
        pass
    try:
        f = float(s)
    except ValueError:
        return None
    return f


def to_number(v: Any) -> Any:
    if is_number(v):
        return v
    if isinstance(v, bool):
        return 1 if v else 0
    if v is None:
        return 0
    if isinstance(v, str):
        n = parse_number(v)
        if n is not None:
            return n
    raise OperasiIlegal(f"{repr_value(v)} tidak bisa diubah menjadi angka")


def deep_copy(v: Any) -> Any:
    if isinstance(v, list):
        return [deep_copy(x) for x in v]
    if isinstance(v, dict):
        return {k: deep_copy(x) for k, x in v.items()}
    return v


@contextlib.contextmanager
def deep_recursion(limit: int = 20000):
    """
    Interpreter & VM rekursif di level Python. Naikkan recursion limit hanya
    selama eksekusi, lalu kembalikan (tidak mengubah proses host secara permanen).
    """
    old = sys.getrecursionlimit()
    if old < limit:
        sys.setrecursionlimit(limit)
    try:
        yield
    finally:
        if old < limit:
            sys.setrecursionlimit(old)


# ================================================================== operators

def _num_operands(op: str, a: Any, b: Any):
    if not (is_number(a) or isinstance(a, bool)) or not (is_number(b) or isinstance(b, bool)):
        raise OperasiIlegal(
            f"Operator '{op}' tidak bisa dipakai untuk {type_name(a)} dan {type_name(b)}")
    return a, b


# Batas ukuran hasil operator supaya program (terutama di sandbox/playground)
# tidak bisa menghabiskan memori/CPU dengan satu ekspresi.
MAX_SEQUENCE = 10_000_000
MAX_INT_BITS = 100_000


def _check_size(n: int):
    if n > MAX_SEQUENCE:
        raise OperasiIlegal(f"Hasil terlalu besar (> {MAX_SEQUENCE:,} elemen). Anggaran memori tidak cukup.")


def _repeat(seq: Any, n: int) -> Any:
    if n > 0:
        _check_size(len(seq) * n)
    return seq * n


# Fast path untuk angka (int/float, bukan bool): semantik identik dengan
# _binary_op, tanpa rangkaian pengecekan tipe. Ini jalur terpanas kedua engine.
_NUMERIC_FAST = {
    "+": operator.add, "-": operator.sub,
    "<": operator.lt, ">": operator.gt, "<=": operator.le, ">=": operator.ge,
    "==": operator.eq, "!=": operator.ne,
}
_NUMBER_TYPES = (int, float)


def binary_op(op: str, a: Any, b: Any) -> Any:
    try:
        if type(a) in _NUMBER_TYPES and type(b) in _NUMBER_TYPES:
            fast = _NUMERIC_FAST.get(op)
            if fast is not None:
                return fast(a, b)
        return _binary_op(op, a, b)
    except OverflowError:
        raise OperasiIlegal(f"Hasil '{op}' terlalu besar (melebihi APBN)")


def _binary_op(op: str, a: Any, b: Any) -> Any:
    if op == "+":
        if isinstance(a, str) or isinstance(b, str):
            sa, sb = to_str(a), to_str(b)
            _check_size(len(sa) + len(sb))
            return sa + sb
        if isinstance(a, list) and isinstance(b, list):
            _check_size(len(a) + len(b))
            return a + b
        if isinstance(a, dict) and isinstance(b, dict):
            _check_size(len(a) + len(b))
            return {**a, **b}
        a, b = _num_operands(op, a, b)
        return a + b
    if op == "-":
        a, b = _num_operands(op, a, b)
        return a - b
    if op == "*":
        if isinstance(a, (str, list)) and isinstance(b, int) and not isinstance(b, bool):
            return _repeat(a, b)
        if isinstance(b, (str, list)) and isinstance(a, int) and not isinstance(a, bool):
            return _repeat(b, a)
        a, b = _num_operands(op, a, b)
        if isinstance(a, int) and isinstance(b, int) and a.bit_length() + b.bit_length() > MAX_INT_BITS:
            raise OperasiIlegal("Hasil perkalian terlalu besar (melebihi APBN)")
        return a * b
    if op == "/":
        a, b = _num_operands(op, a, b)
        if b == 0:
            raise OperasiIlegal("Pembagian dengan nol (kayak bagi anggaran di akhir tahun)")
        if isinstance(a, int) and isinstance(b, int) and a % b == 0:
            return a // b
        return a / b
    if op == "%":
        a, b = _num_operands(op, a, b)
        if b == 0:
            raise OperasiIlegal("Modulo dengan nol")
        return a % b
    if op == "**":
        a, b = _num_operands(op, a, b)
        if isinstance(a, int) and isinstance(b, int) and b > 0 and abs(a) > 1 \
                and b * a.bit_length() > MAX_INT_BITS:
            raise OperasiIlegal("Hasil pangkat terlalu besar (melebihi APBN)")
        try:
            result = a ** b
        except ZeroDivisionError:
            raise OperasiIlegal("Nol dipangkatkan bilangan negatif")
        except OverflowError:
            raise OperasiIlegal("Hasil pangkat terlalu besar (melebihi APBN)")
        if isinstance(result, complex):
            raise OperasiIlegal("Hasil pangkat bukan bilangan real")
        return result
    if op == "==":
        return values_equal(a, b)
    if op == "!=":
        return not values_equal(a, b)
    if op in ("<", ">", "<=", ">="):
        ok = (is_number(a) and is_number(b)) or (isinstance(a, str) and isinstance(b, str)) \
            or (isinstance(a, list) and isinstance(b, list))
        if not ok:
            raise OperasiIlegal(f"Tidak bisa membandingkan {type_name(a)} dengan {type_name(b)}")
        try:
            if op == "<":
                return a < b
            if op == ">":
                return a > b
            if op == "<=":
                return a <= b
            return a >= b
        except TypeError:
            raise OperasiIlegal("Isi daftar tidak bisa dibandingkan")
    raise OperasiIlegal(f"Operator tidak dikenal: {op}")


def values_equal(a: Any, b: Any) -> bool:
    # benar != 1, supaya boolean dan angka tidak tertukar diam-diam — juga di
    # dalam daftar/objek (perbandingan bawaan Python menganggap True == 1).
    if isinstance(a, bool) != isinstance(b, bool):
        return False
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(values_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(values_equal(a[k], b[k]) for k in a)
    return a == b


def unary_op(op: str, v: Any) -> Any:
    if op == "-":
        if not is_number(v):
            raise OperasiIlegal(f"Operator '-' tidak bisa dipakai untuk {type_name(v)}")
        return -v
    if op == "bukan":
        return not truthy(v)
    raise OperasiIlegal(f"Operator tidak dikenal: {op}")


def get_index(obj: Any, key: Any) -> Any:
    if isinstance(obj, (list, str)):
        if not isinstance(key, int) or isinstance(key, bool):
            if isinstance(key, float) and key.is_integer():
                key = int(key)
            else:
                raise OperasiIlegal(f"Index harus bilangan bulat, bukan {type_name(key)}")
        if -len(obj) <= key < len(obj):
            return obj[key]
        raise OperasiIlegal(f"Index {key} di luar jangkauan (panjang {len(obj)})")
    if isinstance(obj, dict):
        k = key if isinstance(key, str) else to_str(key)
        if k in obj:
            return obj[k]
        raise OperasiIlegal(f"Kunci {json.dumps(k, ensure_ascii=False)} tidak ditemukan")
    raise OperasiIlegal(f"Nilai {type_name(obj)} tidak bisa diakses dengan index")


def set_index(obj: Any, key: Any, value: Any):
    if isinstance(obj, list):
        if isinstance(key, float) and key.is_integer():
            key = int(key)
        if not isinstance(key, int) or isinstance(key, bool):
            raise OperasiIlegal(f"Index harus bilangan bulat, bukan {type_name(key)}")
        if -len(obj) <= key < len(obj):
            obj[key] = value
            return
        raise OperasiIlegal(f"Index {key} di luar jangkauan (panjang {len(obj)})")
    if isinstance(obj, dict):
        obj[key if isinstance(key, str) else to_str(key)] = value
        return
    if isinstance(obj, str):
        raise OperasiIlegal("Teks tidak bisa diubah per karakter (immutable, seperti keputusan rapat)")
    raise OperasiIlegal(f"Nilai {type_name(obj)} tidak bisa diubah dengan index")


def get_attr(obj: Any, name: str) -> Any:
    if isinstance(obj, dict):
        if name in obj:
            return obj[name]
        raise OperasiIlegal(f"Properti '{name}' tidak ditemukan")
    if name == "panjang" and isinstance(obj, (list, str)):
        return len(obj)
    raise OperasiIlegal(f"Nilai {type_name(obj)} tidak punya properti '{name}'")


def set_attr(obj: Any, name: str, value: Any):
    if isinstance(obj, dict):
        obj[name] = value
        return
    raise OperasiIlegal(f"Nilai {type_name(obj)} tidak punya properti '{name}'")


def iterate(v: Any) -> List[Any]:
    """Nilai yang bisa dipakai di ``untuk x dalam v``. Disalin supaya aman dimodifikasi."""
    if isinstance(v, (list, tuple)):
        return list(v)
    if isinstance(v, str):
        return list(v)
    if isinstance(v, dict):
        return list(v.keys())
    raise OperasiIlegal(f"'untuk ... dalam' butuh daftar, teks, atau objek, bukan {type_name(v)}")


def range_values(start: Any, end: Any, step: Any):
    """Iterator untuk ``untuk i dari a sampai b langkah s`` (batas atas inklusif)."""
    for name, v in (("dari", start), ("sampai", end), ("langkah", step)):
        if not is_number(v):
            raise OperasiIlegal(f"Nilai '{name}' pada loop harus angka, bukan {type_name(v)}")
    if step == 0:
        raise OperasiIlegal("'langkah' tidak boleh nol (proyek jalan di tempat)")
    i = start
    if step > 0:
        while i <= end:
            yield i
            i += step
    else:
        while i >= end:
            yield i
            i += step


def repeat_count(v: Any) -> int:
    if not is_number(v):
        raise OperasiIlegal(f"Jumlah Rapat harus angka, bukan {type_name(v)}")
    if isinstance(v, float) and not math.isfinite(v):
        raise OperasiIlegal("Jumlah Rapat harus angka berhingga (rapat tanpa ujung dilarang)")
    return max(0, int(v))


# ==================================================================== runtime

class Runtime:
    """State eksekusi: anggaran negara, RNG, I/O, batas langkah."""

    def __init__(self, seed: Optional[int] = None, step_limit: int = 1_000_000,
                 sandbox: bool = False, realtime: bool = False, max_sleep: float = 2.0,
                 output: Optional[Callable[[str], None]] = None,
                 input_fn: Optional[Callable[[str], str]] = None,
                 ctf: bool = False, max_depth: int = 200, delay: float = 0.0):
        self.seed = seed
        self.rng = random.Random(seed)
        self.step_limit = step_limit
        self.steps = 0
        self.sandbox = sandbox
        self.realtime = realtime
        self.max_sleep = max_sleep
        self.ctf = ctf
        self.max_depth = max_depth
        self.delay = delay  # jeda per langkah (detik), untuk demo/visualisasi
        self.depth = 0
        self._output = output
        self._input = input_fn
        self.state: Dict[str, Any] = {
            "anggaran": ANGGARAN_AWAL,
            "progress": 0,
            "status_proyek": "Direncanakan",
            "total_korupsi": 0,
        }
        self.db_connections: Dict[str, Any] = {}
        self.current_line: Optional[int] = None
        # Diisi oleh interpreter/VM: memanggil HambaFunction dari dalam builtin.
        self.call_function: Optional[Callable[[Any, List[Any]], Any]] = None

    # --- I/O
    def write(self, text: str):
        if self._output is not None:
            self._output(text)
        else:
            print(text)
            sys.stdout.flush()

    def read(self, prompt: str = "") -> str:
        if self._input is not None:
            return self._input(prompt)
        try:
            return input(prompt)
        except EOFError:
            return ""

    def sleep(self, seconds: float):
        if self.realtime and seconds > 0:
            time.sleep(min(seconds, self.max_sleep))

    # --- eksekusi
    def tick(self, line: Optional[int]):
        self.current_line = line
        self.steps += 1
        if self.step_limit and self.steps > self.step_limit:
            raise NegaraBangkrut(
                f"Batas {self.step_limit:,} langkah terlampaui. Proyek dihentikan audit KPK.", line)
        if self.delay > 0:
            time.sleep(self.delay)

    def enter_call(self, name: str):
        if self.depth >= self.max_depth:
            raise OperasiIlegal(
                f"Rekursi terlalu dalam di '{name}' (lebih dari {self.max_depth} lapis birokrasi)")
        self.depth += 1

    def exit_call(self):
        self.depth -= 1

    # --- state negara
    def get_state(self, name: str) -> Any:
        return self.state[name]

    def set_state(self, name: str, value: Any):
        if name == "total_korupsi":
            raise OperasiIlegal("total_korupsi hanya bisa dibaca (jejak digital tidak bisa dihapus)")
        if name in ("anggaran", "progress") and not is_number(value):
            raise OperasiIlegal(f"'{name}' harus angka, bukan {type_name(value)}")
        if name == "status_proyek":
            value = to_str(value)
        self.state[name] = value

    def close(self):
        for conn in self.db_connections.values():
            try:
                conn.close()
            except Exception:
                pass
        self.db_connections.clear()
