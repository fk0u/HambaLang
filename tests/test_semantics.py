"""Semantik bahasa. Setiap test berjalan di interpreter DAN HambaVM v4."""
import pytest

from hambalang import NegaraBangkrut, OperasiIlegal, ProyekMangkrak


def lines(out: str):
    return out.splitlines()


# ------------------------------------------------------------------ ekspresi

@pytest.mark.parametrize("expr,expected", [
    ("10 - 2 - 3", "5"),
    ("1 + 2 * 3", "7"),
    ("(1 + 2) * 3", "9"),
    ("2 ** 3 ** 2", "512"),
    ("-2 ** 2", "-4"),
    ("7 / 2", "3.5"),
    ("8 / 2", "4"),
    ("7 % 3", "1"),
    ("0.1 + 0.2", "0.3"),
    ('"a" + 1', "a1"),
    ('1 + "a"', "1a"),
    ('"ab" * 3', "ababab"),
    ("[1, 2] + [3]", "[1, 2, 3]"),
    ("1 < 2 dan 2 < 3", "benar"),
    ("1 > 2 atau 3 > 2", "benar"),
    ("bukan benar", "salah"),
    ("!salah", "benar"),
    ("1 == 1.0", "benar"),
    ("1 == benar", "salah"),
    ('"a" < "b"', "benar"),
    ("kosong", "kosong"),
    ("[1, \"dua\", benar, kosong]", '[1, "dua", benar, kosong]'),
    ('{a: 1, "b": [2]}', '{"a": 1, "b": [2]}'),
])
def test_expressions(run, expr, expected):
    assert run(f"lapor {expr}") == expected


def test_comparisons_are_not_chained(run):
    # (3 > 2) > 1 -> benar > 1: boolean tidak bisa dibandingkan dengan angka.
    with pytest.raises(OperasiIlegal):
        run("lapor 3 > 2 > 1")


def test_short_circuit_does_not_evaluate_right(run):
    src = """
fungsi boom()
  lapor "boom"
  kembalikan benar
akhir
x = salah dan boom()
y = benar atau boom()
lapor x
lapor y
"""
    assert lines(run(src)) == ["salah", "benar"]


def test_logical_returns_operand_value(run):
    assert run('lapor kosong atau "default"') == "default"


@pytest.mark.parametrize("src,msg", [
    ("lapor 1 / 0", "nol"),
    ('lapor 1 - "a"', "tidak bisa dipakai"),
    ('lapor 1 < "a"', "membandingkan"),
    ("lapor x", "tidak ditemukan"),
    ("x = [1]\nlapor x[5]", "di luar jangkauan"),
    ('x = {}\nlapor x["k"]', "tidak ditemukan"),
    ("lapor 5(1)", "bukan fungsi"),
    ('lapor angka("abc")', "tidak bisa diubah"),
    ("Korupsi(150)", "0-100"),
])
def test_runtime_errors(run, src, msg):
    with pytest.raises(OperasiIlegal) as exc:
        run(src)
    assert msg in str(exc.value)


def test_runtime_error_has_line_number(run):
    with pytest.raises(OperasiIlegal) as exc:
        run("lapor 1\nlapor 2\nlapor tidak_ada")
    assert exc.value.line == 3


def test_error_line_inside_function(run):
    src = "fungsi f()\n  kembalikan 1 / 0\nakhir\nx = 1\nf()"
    with pytest.raises(OperasiIlegal) as exc:
        run(src)
    assert exc.value.line == 2


# ------------------------------------------------------------ data structures

def test_list_mutation_and_index_assign(run):
    src = """
a = [3, 1, 2]
a[0] = 10
a[-1] += 5
tambahArray(a, 99)
lapor a
lapor panjang(a)
lapor hapusArray(a, 0)
lapor a
"""
    assert lines(run(src)) == ["[10, 1, 7, 99]", "4", "10", "[1, 7, 99]"]


def test_dict_index_and_attribute_access(run):
    src = """
p = {nama: "Hambalang", info: {tahun: 2011}}
p["status"] = "Mangkrak"
p.info.tahun += 1
lapor p.nama + " " + p["status"] + " " + p.info.tahun
lapor kunci(p)
"""
    assert lines(run(src)) == ["Hambalang Mangkrak 2012", '["nama", "info", "status"]']


def test_lists_are_shared_by_reference(run):
    src = "a = [1]\nb = a\ntambahArray(b, 2)\nlapor a\nc = salin(a)\ntambahArray(c, 3)\nlapor a"
    assert lines(run(src)) == ["[1, 2]", "[1, 2]"]


def test_string_indexing_and_iteration(run):
    src = 'untuk c dalam "abc"\n  lapor c\nakhir\nlapor "xyz"[-1]'
    assert lines(run(src)) == ["a", "b", "c", "z"]


# ------------------------------------------------------------------ control flow

def test_if_elif_else(run):
    src = """
untuk n dalam [95, 70, 40]
  jika n >= 80
    lapor "A"
  ataujika n >= 60
    lapor "B"
  atau
    lapor "C"
  akhir
akhir
"""
    assert lines(run(src)) == ["A", "B", "C"]


def test_for_range_inclusive_with_step(run):
    assert lines(run("untuk i dari 10 sampai 0 langkah -5\n lapor i\nakhir")) == ["10", "5", "0"]


def test_for_range_empty(run):
    assert run("untuk i dari 5 sampai 1\n lapor i\nakhir\nlapor \"ok\"") == "ok"


def test_break_and_continue(run):
    src = """
i = 0
selama benar
  i += 1
  jika i % 2 == 0
    lanjut
  akhir
  jika i > 7
    hentikan
  akhir
  lapor i
akhir
untuk x dalam [1, 2, 3, 4]
  jika x == 3
    hentikan
  akhir
  lapor "x" + x
akhir
"""
    assert lines(run(src)) == ["1", "3", "5", "7", "x1", "x2"]


def test_break_out_of_try_and_block_inside_loop(run):
    src = """
untuk i dari 1 sampai 5
  mulai
    coba
      jika i == 2
        hentikan
      akhir
      lapor i
    jikaGagal
      lapor "gagal"
    akhirCoba
  akhir
akhir
coba
  Mangkrak "setelah loop"
jikaGagal e
  lapor e
akhirCoba
"""
    assert lines(run(src)) == ["1", "setelah loop"]


def test_nested_loops_break_inner_only(run):
    src = """
untuk i dari 1 sampai 2
  untuk j dari 1 sampai 3
    jika j == 2
      hentikan
    akhir
    lapor i + "-" + j
  akhir
akhir
"""
    assert lines(run(src)) == ["1-1", "2-1"]


def test_rapat_repeat(run):
    assert lines(run("n = 0\nRapat(3)\n  n += 1\nselesaiRapat\nlapor n")) == ["3"]


def test_formal_dialect(run):
    src = """
Rapat
    Wacana "komentar resmi"
    Anggaran x = 3
    Proyek x > 0 {
        Sita x == 2 {
            Korupsi "dua"
        } Pengadilan Sita x == 1 {
            Korupsi "satu"
        } Pengadilan {
            Korupsi x
        }
        Anggaran x = x - 1
    }
    BagiRata kali(a, b) {
        kembalikan a * b
    }
    Korupsi Janji kali(6, 7)
Bubarkan
"""
    assert lines(run(src)) == ["3", "dua", "satu", "42"]


def test_halt_stops_program(run):
    out = run('lapor "a"\nselesai\nlapor "b"')
    assert out.startswith("a") and "PROYEK SELESAI" in out and not out.endswith("b")


def test_top_level_return_stops_program(run):
    assert run('lapor "a"\nkembalikan\nlapor "b"') == "a"


# ------------------------------------------------------------------ functions

def test_recursion(run):
    src = """
fungsi fib(n)
  jika n < 2
    kembalikan n
  akhir
  kembalikan fib(n - 1) + fib(n - 2)
akhir
lapor fib(20)
"""
    assert run(src) == "6765"


def test_closures_capture_environment(run):
    src = """
fungsi pembuatPenambah(n)
  fungsi tambah(x)
    kembalikan x + n
  akhir
  kembalikan tambah
akhir
tambah5 = pembuatPenambah(5)
tambah10 = pembuatPenambah(10)
lapor tambah5(1) + tambah10(1)
"""
    assert run(src) == "17"


def test_function_scope_does_not_leak(run):
    src = """
x = "global"
fungsi f()
  x = "lokal"
  y = 1
  kembalikan x
akhir
lapor f()
lapor x
coba
  lapor y
jikaGagal
  lapor "y tidak bocor"
akhirCoba
"""
    assert lines(run(src)) == ["lokal", "global", "y tidak bocor"]


def test_global_declaration(run):
    src = "n = 0\nfungsi tambah()\n  global n\n  n = n + 1\nakhir\ntambah()\ntambah()\nlapor n"
    assert run(src) == "2"


def test_prosedur_and_mulai_write_through_to_outer_scope(run):
    src = """
set total = 0
prosedur Tambah()
  set total = total + 10
  set lokal = 1
akhirProsedur
Tambah()
mulai
  set total = total + 1
  set sementara = 5
akhir
lapor total
coba
  lapor sementara
jikaGagal
  lapor "blok punya scope sendiri"
akhirCoba
"""
    assert lines(run(src)) == ["11", "blok punya scope sendiri"]


def test_loop_variable_inside_function_is_local(run):
    src = """
fungsi jumlahSampai(n)
  total = 0
  untuk i dari 1 sampai n
    total += i
  akhir
  kembalikan total
akhir
untuk i dari 1 sampai 3
  x = jumlahSampai(10)
  lapor i
akhir
"""
    assert lines(run(src)) == ["1", "2", "3"]


def test_wrong_arity(run):
    with pytest.raises(OperasiIlegal, match="butuh 2 argumen"):
        run("fungsi f(a, b)\n kembalikan a\nakhir\nf(1)")


def test_higher_order_builtins(run):
    src = """
fungsi kuadrat(x)
  kembalikan x * x
akhir
fungsi genap(x)
  kembalikan x % 2 == 0
akhir
fungsi tambah(a, b)
  kembalikan a + b
akhir
lapor petakan([1, 2, 3], kuadrat)
lapor saring(rentang(10), genap)
lapor lipat([1, 2, 3, 4], tambah, 0)
"""
    assert lines(run(src)) == ["[1, 4, 9]", "[0, 2, 4, 6, 8]", "10"]


def test_error_inside_callback_is_catchable(run):
    src = """
fungsi rusak(x)
  kembalikan x / 0
akhir
coba
  petakan([1], rusak)
jikaGagal e
  lapor "tertangkap: " + e
akhirCoba
lapor "lanjut"
"""
    out = lines(run(src))
    assert out[0].startswith("tertangkap: Pembagian dengan nol")
    assert out[1] == "lanjut"


def test_deep_recursion_is_reported(run):
    src = "fungsi f(n)\n  kembalikan f(n + 1)\nakhir\nf(0)"
    with pytest.raises(OperasiIlegal, match="Rekursi terlalu dalam"):
        run(src)


# ------------------------------------------------------------------ errors

def test_try_catch_binds_message_and_continues(run):
    src = """
coba
  x = [1][9]
jikaGagal err
  lapor "Error: " + err
akhirCoba
lapor "aman"
"""
    out = lines(run(src))
    assert out[0].startswith("Error: Index 9") and out[1] == "aman"


def test_error_propagates_through_function_to_caller_try(run):
    src = """
fungsi a()
  Mangkrak "dari dalam"
akhir
fungsi b()
  a()
  lapor "tidak tercetak"
akhir
coba
  b()
jikaGagal e
  lapor "ditangkap: " + e
akhirCoba
"""
    assert run(src) == "ditangkap: dari dalam"


def test_uncaught_mangkrak(run):
    with pytest.raises(ProyekMangkrak):
        run('Mangkrak("audit gagal")')


def test_step_limit_cannot_be_caught(run):
    src = "coba\n  selama benar\n  akhir\njikaGagal\n  lapor \"lolos\"\nakhirCoba"
    with pytest.raises(NegaraBangkrut):
        run(src, step_limit=500)


def test_pastikan(run):
    with pytest.raises(OperasiIlegal, match="Audit gagal: harus positif"):
        run('pastikan(-1 > 0, "harus positif")')


# ------------------------------------------------------------------ satire & state

def test_korupsi_is_deterministic_with_seed(run):
    src = "Korupsi(20)\nlapor anggaran"
    assert run(src, seed=1) == run(src, seed=1)
    assert run(src, seed=1) != run(src, seed=2)


def test_korupsi_updates_state(run):
    src = "Korupsi(50)\nlapor anggaran < 1000000000\nlapor total_korupsi + anggaran"
    assert lines(run(src))[-2:] == ["benar", "1000000000"]


def test_state_vars_are_global_from_functions(run):
    src = "fungsi kerja()\n  progress = progress + 25\nakhir\nkerja()\nkerja()\nlapor progress"
    assert run(src) == "50"


def test_total_korupsi_is_read_only(run):
    with pytest.raises(OperasiIlegal, match="hanya bisa dibaca"):
        run("total_korupsi = 0")


def test_mangkrak_numeric_is_delay_not_error(run):
    out = run("Mangkrak(1000)\nlapor \"lanjut\"")
    assert "mangkrak selama 1 detik" in out and out.endswith("lanjut")


def test_tagih_reads_numbers(run):
    src = "Tagih x\nTagih y, \"Nama: \"\nlapor x + 1\nlapor y"
    assert lines(run(src, inputs=["41", "Budi"])) == ["Nama: ", "42", "Budi"]


def test_sandbox_blocks_io(run):
    with pytest.raises(OperasiIlegal, match="sandbox"):
        run('tulisFile("x.txt", "a")', sandbox=True)


def test_sqlite_roundtrip_with_params(run, tmp_path):
    db = str(tmp_path / "t.db")
    src = f"""
sambungDB("d", "sqlite", "{db}")
queryDB("d", "CREATE TABLE p (nama TEXT, dana INTEGER)")
queryDB("d", "INSERT INTO p VALUES (?, ?)", ["Hambalang'; DROP TABLE p; --", 100])
rows = queryDB("d", "SELECT * FROM p")
lapor rows[0].dana
lapor panjang(queryDB("d", "SELECT * FROM p"))
tutupDB("d")
"""
    out = lines(run(src))
    assert out[-3:-1] == ["100", "1"]


def test_builtins_misc(run):
    src = """
lapor rupiah(1500000)
lapor gabung(pisah("a,b,c", ","), "-")
lapor besar("hamba") + kecil("LANG")
lapor urutkan([3, 1, 2])
lapor maksimum([4, 9, 2]) + minimum(4, 9, 2)
lapor bulatkan(3.14159, 2)
lapor tipe([]) + tipe({}) + tipe("") + tipe(1) + tipe(kosong) + tipe(benar)
lapor dariJSON(keJSON({a: [1, benar, kosong]}))
lapor akar(16)
"""
    assert lines(run(src)) == [
        "Rp 1.500.000", "a-b-c", "HAMBAlang", "[1, 2, 3]", "11", "3.14",
        "daftarobjekteksangkakosongboolean",
        '{"a": [1, benar, kosong]}', "4",
    ]


def test_audit_reports_steps(run):
    out = run("x = 1\ny = 2\nlapor Audit().langkah")
    assert out == "3"


@pytest.mark.parametrize("src", [
    'x = "a" * 100000000',
    "x = [0] * 100000000",
    "x = 2 ** 100000000",
    'x = ulangi("ab", 100000000)',
    "x = 10 ** 400 / 3",
    "x = 10 ** 400 * 1.5",
    "x = rentang(100000000)",
])
def test_resource_guards(run, src):
    with pytest.raises(OperasiIlegal, match="terlalu besar"):
        run(src)


def test_big_integers_still_work(run):
    assert run("lapor 2 ** 200 % 1000") == "376"


def test_repeated_squaring_is_bounded(run):
    with pytest.raises(OperasiIlegal, match="terlalu besar"):
        run("x = 3\nRapat(40)\n  x = x * x\nselesaiRapat")


@pytest.mark.parametrize("src", [
    "untuk i dari 1 sampai 1000000000\nakhir",
    "Rapat(1000000000000000000)\nselesaiRapat",
    "untuk x dalam rentang(2000)\nakhir",
])
def test_empty_loops_still_hit_step_limit(run, src):
    with pytest.raises(NegaraBangkrut):
        run(src, step_limit=1000)


def test_iteration_counts_as_step(run):
    # 1 (untuk) + 3 iterasi x (1 statement body + 1 back-edge) + 1 (lapor)
    assert run("untuk i dari 1 sampai 3\n  x = i\nakhir\nlapor Audit().langkah") == "8"


@pytest.mark.parametrize("src", [
    'x = ulangi("a", 6000000)\ny = x + x',
    "x = rentang(6000000)\ny = x + x",
])
def test_concat_guard(run, src):
    with pytest.raises(OperasiIlegal, match="terlalu besar"):
        run(src)


def test_nested_equality_keeps_bool_distinct(run):
    assert run("lapor [benar] == [1]\nlapor {a: [salah]} == {a: [0]}\nlapor [1, [2]] == [1, [2]]") \
        == "salah\nsalah\nbenar"


@pytest.mark.parametrize("src", ['lapor acak(kosong)', 'lapor pisah("a b", kosong)', 'lapor bulatkan(angka("nan"))',
                                 'Rapat(angka("inf"))\nselesaiRapat'])
def test_explicit_kosong_and_non_finite_are_errors(run, src):
    with pytest.raises(OperasiIlegal):
        run(src)


def test_run_source_forwards_output():
    from hambalang import run_source
    seen = []
    assert run_source('lapor "a"\nlapor "b"', output=seen.append) == "a\nb"
    assert seen == ["a", "b"]


def test_recursion_limit_is_restored():
    import sys
    from hambalang import run_source
    before = sys.getrecursionlimit()
    run_source("fungsi f(n)\n jika n > 0\n  kembalikan f(n - 1)\n akhir\n kembalikan 0\nakhir\nlapor f(150)")
    assert sys.getrecursionlimit() == before
