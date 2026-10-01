"""
Program nyata: semua contoh di examples/ dan ctf/ harus jalan, dan output
interpreter harus identik dengan output HambaVM v4 (differential testing).
"""
import glob
import os

import pytest

from hambalang import HambaError, run_source
from hambalang import bytecode as B
from hambalang.compiler import compile_source
from hambalang.parser import parse
from hambalang.runtime import Runtime
from hambalang.vm import VM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRAMS = sorted(glob.glob(os.path.join(ROOT, "examples", "*.hl")) +
                  glob.glob(os.path.join(ROOT, "ctf", "*.hl")))
NEEDS_NETWORK = {"http_api_example.hl"}


def _run_both(path, inputs=None):
    with open(path, encoding="utf-8") as f:
        src = f.read()
    outs = []
    for engine in ("interpreter", "vm"):
        outs.append(run_source(src, engine=engine, seed=2024, inputs=list(inputs or [])))
    return outs


@pytest.mark.parametrize("path", PROGRAMS, ids=os.path.basename)
def test_program_runs_identically_on_both_engines(path, tmp_path, monkeypatch):
    if os.path.basename(path) in NEEDS_NETWORK:
        pytest.skip("butuh akses internet")
    monkeypatch.chdir(tmp_path)  # contoh file/DB menulis ke cwd
    interp, vm = _run_both(path, inputs=["0"])
    assert interp == vm
    assert interp.strip(), "program tidak menghasilkan output"


@pytest.mark.parametrize("path", PROGRAMS, ids=os.path.basename)
def test_program_bytecode_roundtrip(path):
    with open(path, encoding="utf-8") as f:
        co = compile_source(f.read(), os.path.basename(path))
    data = B.dumps(co)
    again = B.loads(data)
    assert B.dumps(again) == data
    assert B.disassemble(again)


# ---------------------------------------------------------------- CTF pack

CTF = {
    "challenge_easy.hl": (["1337"], "HLCTF{anggaran_bocor_halus}", ["1336", "9999"]),
    "challenge_medium.hl": (["32"], "HLCTF{birokrasi_berbelit_tapi_cuan}", ["7", "33"]),
    "challenge_hard.hl": (["150"], "HLCTF{reverse_engineer_plat_merah}", ["149", "151"]),
}


@pytest.mark.parametrize("name", sorted(CTF))
@pytest.mark.parametrize("engine", ["interpreter", "vm"])
def test_ctf_flags(name, engine):
    with open(os.path.join(ROOT, "ctf", name), encoding="utf-8") as f:
        src = f.read()
    good, flag, bad_inputs = CTF[name]
    assert flag in run_source(src, engine=engine, inputs=good, sandbox=True)
    for bad in bad_inputs:
        assert flag not in run_source(src, engine=engine, inputs=[bad], sandbox=True)


def test_ctf_flags_file_matches_challenges():
    with open(os.path.join(ROOT, "ctf", "flags.txt"), encoding="utf-8") as f:
        flags = set(f.read().split())
    assert flags == {flag for _, flag, _ in CTF.values()}


# ---------------------------------------------------------------- bytecode

def test_bytecode_file_roundtrip(tmp_path):
    src = 'fungsi f(x)\n  kembalikan x * 2\nakhir\nlapor f(21)\nlapor [1.5, "s", benar, kosong, 2 ** 80]'
    path = str(tmp_path / "p.hbc")
    B.save(compile_source(src), path)
    assert B.read_version(path) == 4
    out = []
    VM(Runtime(output=out.append)).run(B.load(path))
    assert out == ["42", '[1.5, "s", benar, kosong, 1208925819614629174706176]']


def test_bytecode_rejects_garbage(tmp_path):
    path = tmp_path / "x.hbc"
    path.write_bytes(b"BUKAN")
    with pytest.raises(B.BytecodeError):
        B.load(str(path))
    with pytest.raises(B.BytecodeError):
        B.loads(B.MAGIC + b"\x04\x00\x01")  # terpotong


def test_constants_do_not_merge_bool_and_int():
    co = compile_source("lapor 1\nlapor benar\nlapor 1.0")
    assert [c for c in co.consts if c is not None] == [1, True, 1.0]
    assert [type(c) for c in co.consts if c is not None] == [int, bool, float]


def test_disassembler_shows_names_and_jumps():
    text = B.disassemble(compile_source("x = 1\nselama x < 3\n  x += 1\nakhir"))
    assert "STORE_NAME" in text and "JUMP_IF_FALSE" in text and "(\"x\")" in text


def test_parse_errors_surface_from_compile():
    with pytest.raises(HambaError):
        compile_source("jika benar\n")


def test_vm_and_interpreter_count_same_steps():
    src = "untuk i dari 1 sampai 50\n  x = i * 2\nakhir\ni = 0\nselama i < 10\n  i += 1\nakhir"
    steps = []
    for engine in ("interpreter", "vm"):
        rt = Runtime()
        if engine == "vm":
            VM(rt).run(compile_source(src))
        else:
            from hambalang.interpreter import Interpreter
            Interpreter(rt).run(parse(src))
        steps.append(rt.steps)
    assert steps[0] == steps[1]
