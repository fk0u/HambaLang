"""
Standard library HambaLang.

Setiap builtin menerima ``rt`` (Runtime) sebagai argumen pertama. Builtin
yang menyentuh dunia luar (file, database, HTTP) diblokir di mode sandbox
(playground web, CTF) lewat dekorator ``unsafe``.
"""
import json
import math
import os
import sqlite3
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from hambalang.errors import OperasiIlegal, ProgramSelesai, ProyekMangkrak
from hambalang.runtime import (Builtin, HambaFunction, Runtime, deep_copy, format_number,
                               is_number, repr_value, to_number, to_str,
                               truthy, type_name)

BUILTINS: Dict[str, Builtin] = {}


def builtin(name: str, min_args: int = 0, max_args: Optional[int] = -1, aliases=()):
    """Daftarkan builtin. ``max_args=-1`` berarti sama dengan ``min_args``."""

    def deco(fn: Callable):
        mx = min_args if max_args == -1 else max_args
        b = Builtin(name, fn, min_args, mx)
        BUILTINS[name] = b
        for alias in aliases:
            BUILTINS[alias] = Builtin(alias, fn, min_args, mx)
        return fn

    return deco


def unsafe(fn: Callable) -> Callable:
    def wrapper(rt: Runtime, *args):
        if rt.sandbox:
            raise OperasiIlegal(f"Akses ditolak: '{fn.__name__.lstrip('_')}' dinonaktifkan di mode sandbox")
        return fn(rt, *args)

    wrapper.__name__ = fn.__name__
    return wrapper


def _expect(name: str, v: Any, kind: str):
    checks = {
        "angka": is_number,
        "teks": lambda x: isinstance(x, str),
        "daftar": lambda x: isinstance(x, list),
        "objek": lambda x: isinstance(x, dict),
        "fungsi": lambda x: isinstance(x, (HambaFunction, Builtin)),
    }
    if not checks[kind](v):
        raise OperasiIlegal(f"{name}() butuh {kind}, bukan {type_name(v)}")


def _int(name: str, v: Any) -> int:
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if not isinstance(v, int) or isinstance(v, bool):
        raise OperasiIlegal(f"{name}() butuh bilangan bulat, bukan {repr_value(v)}")
    return v


def _call(rt: Runtime, fn: Any, args: List[Any]) -> Any:
    if isinstance(fn, Builtin):
        return fn(rt, args)
    if isinstance(fn, HambaFunction) and rt.call_function is not None:
        return rt.call_function(fn, args)
    raise OperasiIlegal(f"{repr_value(fn)} bukan fungsi")


# ===================================================================== konversi

@builtin("panjang", 1)
def _panjang(rt, x):
    if isinstance(x, (str, list, dict)):
        return len(x)
    raise OperasiIlegal(f"panjang() hanya untuk teks/daftar/objek, bukan {type_name(x)}")


@builtin("tipe", 1)
def _tipe(rt, x):
    return type_name(x)


@builtin("angka", 1)
def _angka(rt, x):
    return to_number(x)


@builtin("teks", 1)
def _teks(rt, x):
    return to_str(x)


@builtin("bulat", 1)
def _bulat(rt, x):
    _expect("bulat", to_number(x), "angka")
    n = to_number(x)
    if isinstance(n, float) and not math.isfinite(n):
        raise OperasiIlegal("bulat() tidak bisa untuk NaN/TakHingga")
    return int(n)


@builtin("bulatkan", 1, 2)
def _bulatkan(rt, x, digit=0):
    _expect("bulatkan", x, "angka")
    digit = _int("bulatkan", digit)
    r = round(x, digit)
    return int(r) if digit <= 0 else r


@builtin("boolean", 1)
def _boolean(rt, x):
    return truthy(x)


# ==================================================================== matematika

@builtin("mutlak", 1, aliases=("abs",))
def _mutlak(rt, x):
    _expect("mutlak", x, "angka")
    return abs(x)


@builtin("akar", 1)
def _akar(rt, x):
    _expect("akar", x, "angka")
    if x < 0:
        raise OperasiIlegal("akar() dari bilangan negatif (seperti mencari ujung proyek mangkrak)")
    r = math.sqrt(x)
    return int(r) if r.is_integer() and isinstance(x, int) else r


@builtin("pangkat", 2)
def _pangkat(rt, a, b):
    from hambalang.runtime import binary_op
    return binary_op("**", a, b)


def _min_max(name: str, args, pick):
    items = args[0] if len(args) == 1 and isinstance(args[0], list) else list(args)
    if not items:
        raise OperasiIlegal(f"{name}() butuh minimal satu nilai")
    for v in items:
        if not is_number(v) and not isinstance(v, str):
            raise OperasiIlegal(f"{name}() tidak bisa membandingkan {type_name(v)}")
    try:
        return pick(items)
    except TypeError:
        raise OperasiIlegal(f"{name}() tidak bisa mencampur angka dan teks")


@builtin("minimum", 1, None, aliases=("min",))
def _minimum(rt, *args):
    return _min_max("minimum", args, min)


@builtin("maksimum", 1, None, aliases=("max",))
def _maksimum(rt, *args):
    return _min_max("maksimum", args, max)


@builtin("jumlah", 1)
def _jumlah(rt, xs):
    _expect("jumlah", xs, "daftar")
    total = 0
    for v in xs:
        _expect("jumlah", v, "angka")
        total += v
    return total


@builtin("rataRata", 1)
def _rata(rt, xs):
    _expect("rataRata", xs, "daftar")
    if not xs:
        raise OperasiIlegal("rataRata() dari daftar kosong")
    from hambalang.runtime import binary_op
    return binary_op("/", _jumlah(rt, xs), len(xs))


@builtin("acak", 0, 2)
def _acak(rt, a=None, b=None):
    """acak() -> 0..1, acak(n) -> 0..n-1, acak(a, b) -> a..b (inklusif)."""
    if a is None:
        return rt.rng.random()
    if b is None:
        n = _int("acak", a)
        if n <= 0:
            raise OperasiIlegal("acak(n) butuh n > 0")
        return rt.rng.randrange(n)
    lo, hi = _int("acak", a), _int("acak", b)
    if lo > hi:
        raise OperasiIlegal("acak(a, b) butuh a <= b")
    return rt.rng.randint(lo, hi)


@builtin("acakPilih", 1)
def _acak_pilih(rt, xs):
    _expect("acakPilih", xs, "daftar")
    if not xs:
        raise OperasiIlegal("acakPilih() dari daftar kosong")
    return rt.rng.choice(xs)


@builtin("rentang", 1, 3)
def _rentang(rt, a, b=None, step=1):
    """rentang(n) -> [0..n-1], rentang(a, b) -> [a..b-1] (seperti Python)."""
    if b is None:
        a, b = 0, a
    a, b, step = _int("rentang", a), _int("rentang", b), _int("rentang", step)
    if step == 0:
        raise OperasiIlegal("rentang() dengan langkah 0")
    r = range(a, b, step)
    if len(r) > 10_000_000:
        raise OperasiIlegal("rentang() terlalu besar (anggaran memori tidak cukup)")
    return list(r)


# ======================================================================= daftar

@builtin("tambahArray", 2, aliases=("tambah",))
def _tambah(rt, xs, v):
    _expect("tambahArray", xs, "daftar")
    xs.append(v)
    return xs


@builtin("hapusArray", 2, aliases=("hapus",))
def _hapus(rt, xs, idx):
    if isinstance(xs, dict):
        key = to_str(idx)
        if key not in xs:
            raise OperasiIlegal(f"Kunci {json.dumps(key, ensure_ascii=False)} tidak ditemukan")
        return xs.pop(key)
    _expect("hapusArray", xs, "daftar")
    i = _int("hapusArray", idx)
    if -len(xs) <= i < len(xs):
        return xs.pop(i)
    raise OperasiIlegal(f"Index {i} di luar jangkauan (panjang {len(xs)})")


@builtin("sisipkan", 3)
def _sisipkan(rt, xs, idx, v):
    _expect("sisipkan", xs, "daftar")
    xs.insert(_int("sisipkan", idx), v)
    return xs


@builtin("ambilAkhir", 1, aliases=("pop",))
def _pop(rt, xs):
    _expect("ambilAkhir", xs, "daftar")
    if not xs:
        raise OperasiIlegal("ambilAkhir() dari daftar kosong")
    return xs.pop()


@builtin("urutkan", 1, 2)
def _urutkan(rt, xs, desc=False):
    _expect("urutkan", xs, "daftar")
    if all(is_number(v) for v in xs) or all(isinstance(v, str) for v in xs):
        return sorted(xs, reverse=truthy(desc))
    raise OperasiIlegal("urutkan() butuh daftar berisi angka saja atau teks saja")


@builtin("balik", 1)
def _balik(rt, x):
    if isinstance(x, (list, str)):
        return x[::-1]
    raise OperasiIlegal(f"balik() butuh daftar atau teks, bukan {type_name(x)}")


@builtin("irisan", 2, 3)
def _irisan(rt, x, a, b=None):
    if not isinstance(x, (list, str)):
        raise OperasiIlegal(f"irisan() butuh daftar atau teks, bukan {type_name(x)}")
    a = _int("irisan", a)
    return x[a:] if b is None else x[a:_int("irisan", b)]


@builtin("indeksDari", 2)
def _indeks(rt, x, v):
    if isinstance(x, str):
        return x.find(to_str(v))
    _expect("indeksDari", x, "daftar")
    from hambalang.runtime import values_equal
    for i, item in enumerate(x):
        if values_equal(item, v):
            return i
    return -1


@builtin("berisi", 2)
def _berisi(rt, x, v):
    if isinstance(x, str):
        return to_str(v) in x
    if isinstance(x, dict):
        return to_str(v) in x
    _expect("berisi", x, "daftar")
    return _indeks(rt, x, v) >= 0


@builtin("salin", 1)
def _salin(rt, x):
    return deep_copy(x)


@builtin("petakan", 2, aliases=("map",))
def _petakan(rt, xs, fn):
    _expect("petakan", xs, "daftar")
    _expect("petakan", fn, "fungsi")
    return [_call(rt, fn, [v]) for v in list(xs)]


@builtin("saring", 2, aliases=("filter",))
def _saring(rt, xs, fn):
    _expect("saring", xs, "daftar")
    _expect("saring", fn, "fungsi")
    return [v for v in list(xs) if truthy(_call(rt, fn, [v]))]


@builtin("lipat", 3, aliases=("reduce",))
def _lipat(rt, xs, fn, awal):
    _expect("lipat", xs, "daftar")
    _expect("lipat", fn, "fungsi")
    acc = awal
    for v in list(xs):
        acc = _call(rt, fn, [acc, v])
    return acc


# ========================================================================= teks

@builtin("gabung", 1, 2, aliases=("join",))
def _gabung(rt, xs, sep=""):
    _expect("gabung", xs, "daftar")
    return to_str(sep).join(to_str(v) for v in xs)


@builtin("pisah", 1, 2, aliases=("split",))
def _pisah(rt, s, sep=None):
    _expect("pisah", s, "teks")
    if sep is None:
        return s.split()
    if sep == "":
        return list(s)
    return s.split(to_str(sep))


@builtin("besar", 1, aliases=("hurufBesar",))
def _besar(rt, s):
    _expect("besar", s, "teks")
    return s.upper()


@builtin("kecil", 1, aliases=("hurufKecil",))
def _kecil(rt, s):
    _expect("kecil", s, "teks")
    return s.lower()


@builtin("rapikan", 1, aliases=("trim",))
def _rapikan(rt, s):
    _expect("rapikan", s, "teks")
    return s.strip()


@builtin("ganti", 3, aliases=("replace",))
def _ganti(rt, s, a, b):
    _expect("ganti", s, "teks")
    return s.replace(to_str(a), to_str(b))


@builtin("mulaiDengan", 2)
def _mulai_dengan(rt, s, p):
    _expect("mulaiDengan", s, "teks")
    return s.startswith(to_str(p))


@builtin("akhiriDengan", 2)
def _akhiri_dengan(rt, s, p):
    _expect("akhiriDengan", s, "teks")
    return s.endswith(to_str(p))


@builtin("ulangi", 2)
def _ulangi(rt, s, n):
    _expect("ulangi", s, "teks")
    return s * max(0, _int("ulangi", n))


@builtin("rupiah", 1)
def _rupiah(rt, n):
    """Format angka gaya Indonesia: 1500000 -> 'Rp 1.500.000'."""
    _expect("rupiah", n, "angka")
    sign = "-" if n < 0 else ""
    whole = f"{int(round(abs(n))):,}".replace(",", ".")
    return f"{sign}Rp {whole}"


@builtin("kode", 1, aliases=("ord",))
def _kode(rt, s):
    _expect("kode", s, "teks")
    if len(s) != 1:
        raise OperasiIlegal("kode() butuh teks dengan tepat satu karakter")
    return ord(s)


@builtin("karakter", 1, aliases=("chr",))
def _karakter(rt, n):
    n = _int("karakter", n)
    if not 0 <= n <= 0x10FFFF:
        raise OperasiIlegal(f"karakter() di luar jangkauan Unicode: {n}")
    return chr(n)


# ======================================================================== objek

@builtin("kunci", 1, aliases=("keys",))
def _kunci(rt, d):
    _expect("kunci", d, "objek")
    return list(d.keys())


@builtin("nilai", 1, aliases=("values",))
def _nilai(rt, d):
    _expect("nilai", d, "objek")
    return list(d.values())


@builtin("punya", 2)
def _punya(rt, d, k):
    _expect("punya", d, "objek")
    return to_str(k) in d


# ======================================================================== json

def _to_json_value(v: Any) -> Any:
    if isinstance(v, (HambaFunction, Builtin)):
        raise OperasiIlegal("Fungsi tidak bisa diubah ke JSON")
    if isinstance(v, float) and not math.isfinite(v):
        raise OperasiIlegal("NaN/TakHingga tidak bisa diubah ke JSON")
    if isinstance(v, list):
        return [_to_json_value(x) for x in v]
    if isinstance(v, dict):
        return {k: _to_json_value(x) for k, x in v.items()}
    return v


@builtin("keJSON", 1, 2)
def _ke_json(rt, v, indent=None):
    ind = None if indent is None else _int("keJSON", indent)
    return json.dumps(_to_json_value(v), ensure_ascii=False, indent=ind)


@builtin("dariJSON", 1)
def _dari_json(rt, s):
    _expect("dariJSON", s, "teks")
    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        raise OperasiIlegal(f"JSON tidak valid: {e.msg} (posisi {e.pos})")


# ======================================================================== misc

@builtin("pastikan", 1, 2, aliases=("assert",))
def _pastikan(rt, cond, pesan="kondisi tidak terpenuhi"):
    if not truthy(cond):
        raise OperasiIlegal(f"Audit gagal: {to_str(pesan)}")
    return True


@builtin("masukan", 0, 1, aliases=("input",))
def _masukan(rt, prompt=""):
    return rt.read(to_str(prompt))


@builtin("waktu", 0)
def _waktu(rt):
    return time.time()


@builtin("tanggal", 0)
def _tanggal(rt):
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ======================================================================= satire

MANGKRAK_EVENTS = [
    "💸 Dana habis untuk operasional!",
    "🏃 Vendor kabur dengan uang muka!",
    "🌧️ Longsor menghancurkan pondasi!",
    "🚨 Audit mendadak dari KPK!",
    "📄 Dokumen perizinan bermasalah!",
    "👷 Pekerja mogok kerja!",
]


@builtin("Korupsi", 1)
def _korupsi(rt, persen):
    """Korupsi(p): anggaran menguap sekitar p% (±20%, deterministik dengan --seed)."""
    p = to_number(persen)
    if not 0 <= p <= 100:
        raise OperasiIlegal("Persentase korupsi harus 0-100 (bahkan koruptor punya batas)")
    actual = min(100.0, p * rt.rng.uniform(0.8, 1.2))
    anggaran = rt.state["anggaran"]
    amount = int(anggaran * actual / 100)
    rt.state["anggaran"] = anggaran - amount
    rt.state["total_korupsi"] += amount
    rt.write(f"💰 Korupsi {actual:.1f}%: {_rupiah(rt, amount)} menguap!")
    rt.write(f"📊 Sisa anggaran: {_rupiah(rt, rt.state['anggaran'])}")
    if rt.ctf and rt.state["total_korupsi"] > 0 and rt.state["total_korupsi"] % 424242 == 0:
        rt.write("🚩 FLAG{K0RUPSI_NUMBER_TH30RY_42}")
    return amount


@builtin("Mangkrak", 0, 1)
def _mangkrak(rt, x=None):
    """Mangkrak(ms): proyek tertunda. Mangkrak("alasan"): lempar ProyekMangkrak."""
    if x is None or not is_number(x):
        raise ProyekMangkrak("Proyek mangkrak" if x is None else to_str(x))
    seconds = max(0, x) / 1000
    rt.write(f"⏳ Proyek mangkrak selama {format_number(seconds)} detik...")
    rt.sleep(seconds)
    if rt.rng.random() < 0.3:
        rt.write(f"🚧 EVENT: {rt.rng.choice(MANGKRAK_EVENTS)}")
        loss = rt.rng.randint(10_000_000, 100_000_000)
        rt.state["anggaran"] = max(0, rt.state["anggaran"] - loss)
    return None


@builtin("RapatInfinite", 0)
def _rapat_infinite(rt):
    rt.write("🔄 Memulai RapatInfinite()...")
    rt.write("⚠️ Program terjebak dalam rapat berkepanjangan!")
    for i in range(5):
        rt.write(f"📋 Rapat sesi ke-{i + 1}: Belum ada keputusan...")
        rt.sleep(0.3)
    rt.write("⏸️ (RapatInfinite dihentikan paksa untuk demo)")
    return None


@builtin("selesai", 0)
def _selesai(rt):
    rt.state["status_proyek"] = "Selesai (di atas kertas)"
    rt.state["progress"] = 100
    rt.write("\n✅ PROYEK SELESAI!")
    rt.write(f"Progress: 100% [{'█' * 9}░]")
    rt.write(f"Status: {rt.state['status_proyek']}")
    rt.write(f"Sisa Anggaran: {_rupiah(rt, rt.state['anggaran'])}")
    rt.write("(Kondisi fisik: Data tidak tersedia)")
    if rt.ctf and rt.state["anggaran"] == 0:
        rt.write("🚩 FLAG{H4MB4_VM_M4ST3R_PERFECT_BUDGET}")
    raise ProgramSelesai()


@builtin("Audit", 0)
def _audit(rt):
    """Kembalikan snapshot state negara sebagai objek."""
    return {
        "anggaran": rt.state["anggaran"],
        "progress": rt.state["progress"],
        "status_proyek": rt.state["status_proyek"],
        "total_korupsi": rt.state["total_korupsi"],
        "langkah": rt.steps,
    }


# ========================================================================= file

@builtin("tulisFile", 2)
@unsafe
def _tulisFile(rt, path, content):
    path = to_str(path)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(to_str(content))
    except OSError as e:
        raise OperasiIlegal(f"Gagal menulis file '{path}': {e.strerror}")
    rt.write(f"✅ File ditulis: {path}")
    return True


@builtin("tambahFile", 2)
@unsafe
def _tambahFile(rt, path, content):
    path = to_str(path)
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(to_str(content))
    except OSError as e:
        raise OperasiIlegal(f"Gagal menulis file '{path}': {e.strerror}")
    return True


@builtin("bacaFile", 1)
@unsafe
def _bacaFile(rt, path):
    path = to_str(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        raise OperasiIlegal(f"Gagal membaca file '{path}': {e.strerror}")
    rt.write(f"✅ File dibaca: {path}")
    return content


@builtin("adaFile", 1)
@unsafe
def _adaFile(rt, path):
    return os.path.exists(to_str(path))


@builtin("hapusFile", 1)
@unsafe
def _hapusFile(rt, path):
    path = to_str(path)
    try:
        os.remove(path)
    except OSError as e:
        raise OperasiIlegal(f"Gagal menghapus file '{path}': {e.strerror}")
    return True


# ===================================================================== database

def _db_value(v: Any) -> Any:
    if isinstance(v, (bytes, bytearray)):
        return v.decode("utf-8", errors="replace")
    if isinstance(v, (int, float, str)) or v is None:
        return v
    return str(v)


@builtin("sambungDB", 3)
@unsafe
def _sambungDB(rt, name, db_type, target):
    name, db_type, target = to_str(name), to_str(db_type).lower(), to_str(target)
    try:
        if db_type == "sqlite":
            conn = sqlite3.connect(target)
        elif db_type == "mysql":
            try:
                import mysql.connector  # type: ignore
            except ImportError:
                raise OperasiIlegal("mysql-connector-python tidak terinstall (pip install hambalang[db])")
            conn = mysql.connector.connect(**_parse_dsn(target))
        elif db_type in ("postgres", "postgresql"):
            try:
                import psycopg2  # type: ignore
            except ImportError:
                raise OperasiIlegal("psycopg2 tidak terinstall (pip install hambalang[db])")
            conn = psycopg2.connect(target)
        else:
            raise OperasiIlegal(f"Tipe database tidak didukung: {db_type} (sqlite/mysql/postgres)")
    except OperasiIlegal:
        raise
    except Exception as e:
        raise OperasiIlegal(f"Gagal koneksi database '{name}': {e}")
    if name in rt.db_connections:
        rt.db_connections[name].close()
    rt.db_connections[name] = conn
    rt.write(f"✅ Terhubung ke {db_type}: {name}")
    return True


def _parse_dsn(s: str) -> Dict[str, str]:
    """'host=localhost user=root database=x' -> dict untuk mysql.connector."""
    out = {}
    for part in s.split():
        if "=" in part:
            k, v = part.split("=", 1)
            out[k] = v
    return out


@builtin("queryDB", 2, 3)
@unsafe
def _queryDB(rt, name, sql, params=None):
    """
    queryDB(db, sql [, params]). SELECT -> daftar objek (kolom -> nilai);
    selain itu -> jumlah baris terdampak. Pakai ``params`` (daftar) dengan
    placeholder ``?`` untuk menghindari SQL injection.
    """
    name, sql = to_str(name), to_str(sql)
    conn = rt.db_connections.get(name)
    if conn is None:
        raise OperasiIlegal(f"Database '{name}' belum terhubung (panggil sambungDB dulu)")
    if params is not None and not isinstance(params, list):
        raise OperasiIlegal("Parameter query harus daftar")
    try:
        cur = conn.cursor()
        cur.execute(sql, tuple(params or ()))
        if cur.description is not None:
            cols = [d[0] for d in cur.description]
            rows = [{c: _db_value(v) for c, v in zip(cols, row)} for row in cur.fetchall()]
            cur.close()
            return rows
        conn.commit()
        count = cur.rowcount
        cur.close()
        return count
    except Exception as e:
        raise OperasiIlegal(f"Query gagal: {e}")


@builtin("tutupDB", 1)
@unsafe
def _tutupDB(rt, name):
    name = to_str(name)
    conn = rt.db_connections.pop(name, None)
    if conn is not None:
        conn.close()
        rt.write(f"✅ Koneksi ditutup: {name}")
    return conn is not None


# ========================================================================= http

def _http(method: str, rt: Runtime, url: Any, data: Any = None) -> Dict[str, Any]:
    try:
        import requests  # type: ignore
    except ImportError:
        raise OperasiIlegal("Library 'requests' tidak terinstall (pip install hambalang[http])")
    url = to_str(url)
    if not url.startswith(("http://", "https://")):
        raise OperasiIlegal(f"URL harus diawali http:// atau https://: {url}")
    try:
        if method == "GET":
            resp = requests.get(url, timeout=10)
        else:
            resp = requests.post(url, json=_to_json_value(data), timeout=10)
    except Exception as e:
        raise OperasiIlegal(f"HTTP {method} gagal: {e}")
    body = resp.text
    parsed = None
    if "json" in resp.headers.get("content-type", ""):
        try:
            parsed = resp.json()
        except ValueError:
            parsed = None
    rt.write(f"✅ HTTP {method}: {url} - Status {resp.status_code}")
    return {"status": resp.status_code, "body": body, "json": parsed}


@builtin("httpGet", 1)
@unsafe
def _httpGet(rt, url):
    return _http("GET", rt, url)


@builtin("httpPost", 2)
@unsafe
def _httpPost(rt, url, data):
    return _http("POST", rt, url, data)


@builtin("bacaJSON", 1)
@unsafe
def _bacaJSON(rt, path):
    return _dari_json(rt, _bacaFile(rt, path))


@builtin("tulisJSON", 2)
@unsafe
def _tulisJSON(rt, path, data):
    return _tulisFile(rt, path, _ke_json(rt, data, 2))
