"""CLI end-to-end + pipeline legacy v3 (obfuscator/ObfuscatedVM) tetap berfungsi."""
import os
import shutil

import pytest

from hambalang.cli import main

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def write(path, text):
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_run_interpreter_and_vm(workdir, capsys):
    f = write(workdir / "a.hl", 'lapor "halo " + (40 + 2)\n')
    assert main(["run", f]) == 0
    assert main(["run", f, "--vm"]) == 0
    assert capsys.readouterr().out.splitlines() == ["halo 42", "halo 42"]


def test_run_reports_runtime_error_with_source(workdir, capsys):
    f = write(workdir / "e.hl", "x = 1\nlapor x / 0\n")
    assert main(["run", f]) == 1
    err = capsys.readouterr().err
    assert "OperasiIlegal" in err and "e.hl:2" in err and "lapor x / 0" in err


def test_syntax_error_exit_code_and_caret(workdir, capsys):
    f = write(workdir / "s.hl", "lapor 1 +* 2\n")
    assert main(["run", f]) == 2
    err = capsys.readouterr().err
    assert "s.hl:1:10" in err and "^" in err


def test_compile_run_disasm_v4(workdir, capsys):
    f = write(workdir / "p.hl", "fungsi f(x)\n  kembalikan x * 3\nakhir\nlapor f(14)\n")
    assert main(["compile", f]) == 0
    assert main(["run", str(workdir / "p.hbc")]) == 0
    assert main(["disasm", str(workdir / "p.hbc")]) == 0
    out = capsys.readouterr().out
    assert "42" in out and "== fungsi f(x)" in out


def test_check(workdir, capsys):
    ok = write(workdir / "ok.hl", "lapor 1\n")
    bad = write(workdir / "bad.hl", "jika benar\n")
    assert main(["check", ok]) == 0
    assert main(["check", ok, bad]) == 1
    assert "1/2 file lolos" in capsys.readouterr().out


def test_audit_flag(workdir, capsys):
    f = write(workdir / "k.hl", "Korupsi(10)\n")
    assert main(["run", f, "--seed", "1", "--audit"]) == 0
    assert "Laporan Audit" in capsys.readouterr().out


def test_strict_mode_is_sandboxed(workdir, capsys):
    f = write(workdir / "io.hl", 'tulisFile("x.txt", "a")\n')
    assert main(["run", f, "--strict"]) == 1
    assert not (workdir / "x.txt").exists()


def test_ctf_command(workdir, capsys, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "1337")
    assert main(["ctf", os.path.join(ROOT, "ctf", "challenge_easy.hl")]) == 0
    assert "HLCTF{anggaran_bocor_halus}" in capsys.readouterr().out


def test_repl_multiline_and_values(capsys, monkeypatch):
    feed = iter(["x = 20", "fungsi dobel(n)", "  kembalikan n * 2", "akhir", "dobel(x) + 2",
                 ":vars", "lapor kosong_var", ":keluar"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(feed))
    assert main(["repl"]) == 0
    captured = capsys.readouterr()
    assert "42" in captured.out and "x = 20" in captured.out
    assert "tidak ditemukan" in captured.err


def test_debugger_breakpoint_and_print(workdir, capsys, monkeypatch):
    f = write(workdir / "d.hl", "fungsi dobel(n)\n  kembalikan n * 2\nakhir\na = 1\nb = a + 41\nlapor b\n")
    feed = iter(["p a + 1", "p dobel(b)", "p tidak_ada", "vars", "c"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(feed))
    assert main(["debug", f, "-b", "6"]) == 0
    out = capsys.readouterr().out
    assert "→   6 | lapor b" in out and "\n2\n" in out and "\n84\n" in out
    assert "tidak ditemukan" in out and "b = 42" in out and "Program selesai" in out


# ------------------------------------------------------------------ legacy v3

def test_legacy_compile_obfuscate_and_run(workdir, capsys):
    src = shutil.copy(os.path.join(ROOT, "examples", "simple_test.hl"), workdir / "s.hl")
    assert main(["compile", str(src), "--legacy", "-o", "s3.hbc"]) == 0
    assert main(["run", "s3.hbc"]) == 0
    assert main(["obfuscate", "s3.hbc", "--level", "2", "--seed", "5"]) == 0
    assert main(["run", "s3_obf.hbc", "--obfuscated", "--seed", "5"]) == 0
    assert main(["disasm", "s3.hbc"]) == 0
    out = capsys.readouterr().out
    assert out.count("10 + 20 = 30") >= 2 and "HAMBALANG BYTECODE" in out


def test_legacy_shim_entrypoint(workdir, capsys):
    import runpy
    import sys
    f = write(workdir / "x.hl", 'lapor "via shim"\n')
    old = sys.argv
    sys.argv = ["hamba_v2.py", f]
    try:
        with pytest.raises(SystemExit) as exc:
            runpy.run_path(os.path.join(ROOT, "interpreter", "hamba_v2.py"), run_name="__main__")
    finally:
        sys.argv = old
    assert exc.value.code == 0
    assert "via shim" in capsys.readouterr().out
