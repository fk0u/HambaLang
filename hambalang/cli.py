"""
CLI HambaLang.

    hambalang run program.hl [--vm] [--seed N] [--sandbox] [--audit]
    hambalang compile program.hl [-o out.hbc] [--legacy]
    hambalang disasm program.hbc
    hambalang debug program.hl
    hambalang check *.hl
    hambalang repl
    hambalang ctf ctf/challenge_easy.hl

Bytecode legacy v3 (Phase 3/4: obfuscator, Hell Mode) tetap didukung lewat
``compile --legacy``, ``run file.hbc --obfuscated/--hell``, ``obfuscate``.
"""
import argparse
import os
import sys
from typing import List, Optional

from hambalang import __version__
from hambalang import bytecode as B
from hambalang.errors import HambaError, InputBelumLengkap, SalahKetik
from hambalang.runtime import Runtime, repr_value

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def require_legacy() -> bool:
    """Toolchain v3 (compiler/, vm/, obfuscator/) hanya ada di source checkout."""
    for root in (PROJECT_ROOT, os.getcwd()):
        if os.path.isdir(os.path.join(root, "compiler")) and os.path.isdir(os.path.join(root, "vm")):
            if root not in sys.path:
                sys.path.insert(0, root)
            return True
    error("Toolchain legacy v3 tidak ditemukan. Jalankan dari source checkout HambaLang.")
    return False


# ===================================================================== output

class Style:
    enabled = sys.stdout.isatty() and not os.environ.get("NO_COLOR")

    @classmethod
    def wrap(cls, code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if cls.enabled else text


def header(msg: str):
    print(Style.wrap("1;95", msg))


def info(msg: str):
    print(Style.wrap("96", f"ℹ {msg}"))


def success(msg: str):
    print(Style.wrap("92", f"✓ {msg}"))


def error(msg: str):
    print(Style.wrap("91", f"✗ {msg}"), file=sys.stderr)


def report_error(err: HambaError, filename: str, source: Optional[str]):
    """Cetak error dengan cuplikan source dan caret, gaya compiler modern."""
    loc = filename
    if err.line:
        loc += f":{err.line}"
        if err.col:
            loc += f":{err.col}"
    print(Style.wrap("1;91", f"{err.jenis}") + f" di {loc}", file=sys.stderr)
    print(f"  {err.message}", file=sys.stderr)
    if source and err.line:
        src_lines = source.replace("\r\n", "\n").split("\n")
        if 0 < err.line <= len(src_lines):
            text = src_lines[err.line - 1]
            gutter = f"{err.line:>5} | "
            print(Style.wrap("2", gutter) + text.rstrip(), file=sys.stderr)
            if err.col:
                print(" " * (len(gutter) + err.col - 1) + Style.wrap("91", "^"), file=sys.stderr)


def read_source(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        error(f"File tidak ditemukan: {path}")
    except UnicodeDecodeError:
        error(f"File bukan teks UTF-8: {path}")
    except OSError as e:
        error(f"Gagal membaca {path}: {e.strerror}")
    return None


def make_runtime(args) -> Runtime:
    seed = getattr(args, "seed", None)
    strict = getattr(args, "strict", False)
    if strict and seed is None:
        seed = 0
    return Runtime(
        seed=seed,
        step_limit=getattr(args, "step_limit", 1_000_000),
        sandbox=getattr(args, "sandbox", False) or strict,
        realtime=not getattr(args, "fast", False),
        ctf=getattr(args, "ctf", False),
    )


def print_audit(rt: Runtime):
    from hambalang.builtins import _rupiah
    print(Style.wrap("2", "─" * 50))
    print("📋 Laporan Audit")
    print(f"   Langkah eksekusi : {rt.steps:,}")
    print(f"   Anggaran akhir   : {_rupiah(rt, rt.state['anggaran'])}")
    print(f"   Total korupsi    : {_rupiah(rt, rt.state['total_korupsi'])}")
    print(f"   Progress         : {repr_value(rt.state['progress'])}%")
    print(f"   Status proyek    : {rt.state['status_proyek']}")


# ===================================================================== run

def cmd_run(args) -> int:
    path = args.file
    if path.endswith(".hbc"):
        return run_bytecode(args)
    source = read_source(path)
    if source is None:
        return 1
    rt = make_runtime(args)
    from hambalang.parser import parse
    try:
        program = parse(source)
        if args.vm:
            from hambalang.compiler import compile_program
            from hambalang.vm import VM
            vm = VM(rt)
            if args.trace:
                vm.trace = _line_tracer()
            vm.run(compile_program(program, os.path.basename(path)))
        else:
            from hambalang.interpreter import Interpreter
            Interpreter(rt).run(program)
    except HambaError as e:
        report_error(e, path, source)
        return 2 if isinstance(e, SalahKetik) else 1
    except RecursionError:
        error("Rekursi terlalu dalam (stack birokrasi meluap)")
        return 1
    finally:
        rt.close()
    if args.audit:
        print_audit(rt)
    return 0


def _line_tracer():
    last = [None]

    def trace(vm, frame, op, arg):
        if op == B.LINE and arg != last[0]:
            last[0] = arg
            print(Style.wrap("2", f"[trace] {frame.code.name}:{arg}"), file=sys.stderr)

    return trace


def run_bytecode(args) -> int:
    path = args.file
    try:
        version = B.read_version(path)
    except (OSError, B.BytecodeError) as e:
        error(str(e))
        return 1
    if version != B.VERSION:
        return run_legacy_bytecode(args)
    rt = make_runtime(args)
    try:
        from hambalang.vm import VM
        VM(rt).run(B.load(path))
    except B.BytecodeError as e:
        error(f"Bytecode rusak: {e}")
        return 1
    except HambaError as e:
        report_error(e, path, None)
        return 1
    finally:
        rt.close()
    if args.audit:
        print_audit(rt)
    return 0


def run_legacy_bytecode(args) -> int:
    """Bytecode v3 (Phase 3/4) dijalankan HambaVM lama / ObfuscatedVM."""
    if not require_legacy():
        return 1
    info("Bytecode legacy v3 terdeteksi, memakai HambaVM lama")
    if args.obfuscated or args.paranoia or args.hell:
        from compiler.bytecode import Bytecode
        from vm.obfuscated_vm import ObfuscatedVM
        header("🔒 ObfuscatedVM - Protected Execution")
        vm = ObfuscatedVM(Bytecode.load(args.file), seed=args.seed, step_limit=args.step_limit,
                          debug=args.trace, paranoia=args.paranoia, obfuscated=args.obfuscated)
        ok = vm.run(ctf_mode=args.ctf, hell_mode=args.hell)
    else:
        from vm.hamba_vm import run_bytecode_file
        ok = run_bytecode_file(args.file, debug=args.trace, seed=args.seed, ctf_mode=args.ctf,
                               step_limit=args.step_limit)
    return 0 if ok else 1


# ===================================================================== compile

def cmd_compile(args) -> int:
    path = args.file
    if not path.endswith(".hl"):
        error("File sumber harus berekstensi .hl")
        return 1
    out = args.output or path[:-3] + ".hbc"
    if args.legacy:
        return compile_legacy(path, out)
    source = read_source(path)
    if source is None:
        return 1
    from hambalang.compiler import compile_source
    try:
        co = compile_source(source, os.path.basename(path))
    except HambaError as e:
        report_error(e, path, source)
        return 2
    B.save(co, out)
    n_funcs = sum(1 for c in co.consts if isinstance(c, B.CodeObject))
    success(f"Bytecode v{B.VERSION} disimpan: {out} ({os.path.getsize(out)} byte, "
            f"{len(co.code)} instruksi, {n_funcs} fungsi)")
    return 0


def compile_legacy(path: str, out: str) -> int:
    if not require_legacy():
        return 1
    from compiler.bytecode import BytecodeCompiler
    from interpreter.hamba_advanced import Parser
    source = read_source(path)
    if source is None:
        return 1
    try:
        bytecode = BytecodeCompiler().compile(Parser(source.split("\n")).parse())
    except Exception as e:
        error(f"Compile legacy gagal: {e}")
        return 1
    bytecode.save(out)
    success(f"Bytecode legacy v3 disimpan: {out} (untuk obfuscate/Hell Mode)")
    return 0


# ===================================================================== disasm

def cmd_disasm(args) -> int:
    path = args.file
    try:
        version = B.read_version(path)
    except (OSError, B.BytecodeError) as e:
        error(str(e))
        return 1
    if version == B.VERSION:
        try:
            print(B.disassemble(B.load(path)))
        except B.BytecodeError as e:
            error(f"Bytecode rusak: {e}")
            return 1
        return 0
    if not require_legacy():
        return 1
    from compiler.bytecode import Bytecode, disassemble
    print(disassemble(Bytecode.load(path)))
    return 0


# ===================================================================== check

def cmd_check(args) -> int:
    from hambalang.compiler import compile_source
    failed = 0
    for path in args.files:
        source = read_source(path)
        if source is None:
            failed += 1
            continue
        try:
            compile_source(source, path)
        except HambaError as e:
            report_error(e, path, source)
            failed += 1
        else:
            success(path)
    if len(args.files) > 1:
        print(f"{len(args.files) - failed}/{len(args.files)} file lolos verifikasi")
    return 1 if failed else 0


# ===================================================================== ctf

def cmd_ctf(args) -> int:
    header("🎯 HambaLang CTF Challenge")
    print("Masukkan jawaban saat diminta. Flag berformat HLCTF{...}")
    print("=" * 60)
    args.sandbox = True
    args.ctf = True
    args.audit = False
    args.trace = False
    args.fast = True
    return cmd_run(args)


# ===================================================================== repl

REPL_HELP = """Perintah REPL:
  :bantuan        tampilkan bantuan ini
  :audit          laporan state negara (anggaran, langkah, ...)
  :vars           daftar variabel global
  :reset          mulai sesi baru
  :keluar         keluar (atau Ctrl+D)
Blok multi-baris (jika/fungsi/selama/...) otomatis dilanjutkan sampai ditutup."""


def cmd_repl(args) -> int:
    from hambalang.interpreter import Interpreter
    from hambalang.parser import parse

    try:
        import readline  # noqa: F401  (history & editing di terminal yang mendukung)
    except ImportError:
        pass

    def fresh():
        return Interpreter(Runtime(seed=args.seed, realtime=False, sandbox=args.sandbox))

    interp = fresh()
    print(f"HambaLang {__version__} REPL — ketik :bantuan untuk bantuan, :keluar untuk keluar.")
    buffer: List[str] = []
    while True:
        try:
            line = input("...  " if buffer else "hl> ")
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print("\n(dibatalkan)")
            buffer = []
            continue
        if not buffer and line.strip().startswith(":"):
            cmd = line.strip()
            if cmd in (":keluar", ":q", ":exit"):
                return 0
            if cmd == ":bantuan":
                print(REPL_HELP)
            elif cmd == ":audit":
                print_audit(interp.rt)
            elif cmd == ":vars":
                for k, v in interp.globals.vars.items():
                    print(f"  {k} = {repr_value(v)}")
            elif cmd == ":reset":
                interp = fresh()
                print("Sesi direset. Anggaran kembali penuh (secara administratif).")
            else:
                error(f"Perintah tidak dikenal: {cmd}")
            continue
        buffer.append(line)
        source = "\n".join(buffer)
        if not source.strip():
            buffer = []
            continue
        try:
            program = parse(source)
        except InputBelumLengkap:
            continue
        except SalahKetik as e:
            report_error(e, "<repl>", source)
            buffer = []
            continue
        buffer = []
        interp.rt.steps = 0
        try:
            result = interp.eval_repl(program)
        except HambaError as e:
            report_error(e, "<repl>", source)
            continue
        except RecursionError:
            error("Rekursi terlalu dalam")
            continue
        if result is not None:
            print(Style.wrap("93", repr_value(result)))


# ===================================================================== debug

DEBUG_HELP = """Perintah debugger (hdb):
  s / step         jalankan sampai baris berikutnya
  si               jalankan satu instruksi bytecode
  c / lanjut       jalan sampai breakpoint berikutnya
  b N              pasang breakpoint di baris N   (b tanpa angka: daftar)
  hapus N          hapus breakpoint baris N
  p EKSPRESI       evaluasi ekspresi di scope saat ini, mis. p anggaran / p arr[0]
  vars             variabel di scope saat ini
  stack            operand stack frame saat ini
  bt               backtrace (tumpukan pemanggilan)
  l                tampilkan source di sekitar baris saat ini
  q                keluar"""


class Debugger:
    def __init__(self, source_lines: List[str]):
        self.lines = source_lines
        self.breakpoints = set()
        self.mode = "step"  # step | stepi | continue
        self.last_line = None

    def __call__(self, vm, frame, op, arg):
        if op == B.LINE:
            new_line = arg != self.last_line
            self.last_line = arg
            stop = (self.mode == "step" and new_line) or (self.mode == "continue" and arg in self.breakpoints)
            if not stop and self.mode != "stepi":
                return
        elif self.mode != "stepi":
            return
        self.prompt(vm, frame, op, arg)

    def show(self, line: int, context: int = 0):
        lo, hi = max(1, line - context), min(len(self.lines), line + context)
        for n in range(lo, hi + 1):
            mark = "→" if n == line else " "
            bp = "●" if n in self.breakpoints else " "
            print(f"{bp}{mark}{n:>4} | {self.lines[n - 1]}")

    def prompt(self, vm, frame, op, arg):
        line = frame.line or arg
        if op == B.LINE and 0 < arg <= len(self.lines):
            self.show(arg)
        else:
            print(f"   [{frame.code.name}] pc={frame.pc - 1} {B.OPCODES[op]} {arg}")
        while True:
            try:
                cmd = input(Style.wrap("96", "(hdb) ")).strip()
            except EOFError:
                cmd = "q"
            name, _, rest = cmd.partition(" ")
            if name in ("s", "step", ""):
                self.mode = "step"
                return
            if name == "si":
                self.mode = "stepi"
                return
            if name in ("c", "lanjut", "continue"):
                self.mode = "continue"
                return
            if name in ("q", "quit", "keluar"):
                raise KeyboardInterrupt
            if name == "b":
                if rest.strip().isdigit():
                    self.breakpoints.add(int(rest))
                    print(f"Breakpoint di baris {rest.strip()}")
                else:
                    print("Breakpoint:", sorted(self.breakpoints) or "(tidak ada)")
            elif name == "hapus" and rest.strip().isdigit():
                self.breakpoints.discard(int(rest))
            elif name == "p":
                self.evaluate(vm, frame, rest)
            elif name == "vars":
                env = frame.env
                depth = 0
                while env is not None:
                    label = "global" if env.parent is None else f"scope -{depth}"
                    for k, v in env.vars.items():
                        print(f"  [{label}] {k} = {repr_value(v)}")
                    env, depth = env.parent, depth + 1
                for k, v in vm.rt.state.items():
                    print(f"  [negara] {k} = {repr_value(v)}")
            elif name == "stack":
                print("  " + ", ".join(repr_value(v) if not hasattr(v, "__next__") else "<iterator>"
                                       for v in frame.stack))
            elif name == "bt":
                for fr in vm.frames:
                    print(f"  {fr.code.kind} {fr.code.name} @ baris {fr.line}")
            elif name == "l":
                self.show(line, 4)
            elif name in ("h", "help", "bantuan"):
                print(DEBUG_HELP)
            else:
                print("Perintah tidak dikenal. Ketik 'bantuan'.")

    def evaluate(self, vm, frame, expr_src: str):
        from hambalang.interpreter import Interpreter
        from hambalang.parser import Parser
        from hambalang.lexer import tokenize
        try:
            p = Parser(tokenize(expr_src))
            expr = p.parse_expression()
            interp = Interpreter(vm.rt)
            print(Style.wrap("93", repr_value(interp.eval(expr, frame.env))))
        except HambaError as e:
            print(f"  {e}")
        finally:
            vm.rt.call_function = vm.call_function


def cmd_debug(args) -> int:
    path = args.file
    source = read_source(path)
    if source is None:
        return 1
    from hambalang.compiler import compile_source
    from hambalang.vm import VM
    try:
        co = compile_source(source, os.path.basename(path))
    except HambaError as e:
        report_error(e, path, source)
        return 2
    header("🐛 HambaLang Debugger (HambaVM v4) — ketik 'bantuan' untuk daftar perintah")
    rt = make_runtime(args)
    rt.realtime = False
    vm = VM(rt)
    dbg = Debugger(source.replace("\r\n", "\n").split("\n"))
    for bp in args.breakpoint or []:
        dbg.breakpoints.add(bp)
    if dbg.breakpoints:
        dbg.mode = "continue"
    vm.trace = dbg
    try:
        vm.run(co)
        success("Program selesai")
    except KeyboardInterrupt:
        print("\nDebugger dihentikan.")
    except HambaError as e:
        report_error(e, path, source)
        return 1
    finally:
        rt.close()
    return 0


# ===================================================================== legacy

def cmd_legacy(args) -> int:
    if not require_legacy():
        return 1
    from cli.cli_extensions import cmd_analyze, cmd_obfuscate
    return (cmd_obfuscate if args.command == "obfuscate" else cmd_analyze)(args)


# ===================================================================== main

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hambalang",
        description="HambaLang — bahasa pemrograman satir birokrasi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Contoh:
  hambalang run examples/algorithms.hl          jalankan dengan interpreter
  hambalang run examples/algorithms.hl --vm     kompilasi & jalankan di HambaVM v4
  hambalang compile examples/demo.hl            hasilkan examples/demo.hbc
  hambalang disasm examples/demo.hbc            lihat isi bytecode
  hambalang debug examples/algorithms.hl -b 20  debugger dengan breakpoint
  hambalang check examples/*.hl                 verifikasi sintaks
  hambalang repl                                mode interaktif
  hambalang ctf ctf/challenge_easy.hl           main CTF
""")
    p.add_argument("--version", action="version", version=f"HambaLang {__version__}")
    sub = p.add_subparsers(dest="command")

    def runtime_opts(sp):
        sp.add_argument("--seed", type=int, help="seed RNG (eksekusi deterministik)")
        sp.add_argument("--step-limit", type=int, default=1_000_000,
                        help="batas langkah eksekusi, 0 = tanpa batas (default 1.000.000)")
        sp.add_argument("--sandbox", action="store_true", help="blokir akses file/DB/HTTP")

    r = sub.add_parser("run", help="jalankan .hl atau .hbc")
    r.add_argument("file")
    runtime_opts(r)
    r.add_argument("--vm", action="store_true", help="kompilasi ke bytecode lalu jalankan di HambaVM v4")
    r.add_argument("--fast", "--cepat", action="store_true", help="lewati jeda Mangkrak()")
    r.add_argument("--audit", action="store_true", help="cetak laporan audit di akhir")
    r.add_argument("--strict", action="store_true", help="sandbox + seed 0 bila tidak diberikan")
    r.add_argument("--trace", "--debug", action="store_true", help="cetak setiap baris yang dieksekusi (VM)")
    r.add_argument("--ctf", action="store_true", help="aktifkan flag rahasia CTF")
    legacy = r.add_argument_group("bytecode legacy v3")
    legacy.add_argument("--obfuscated", action="store_true")
    legacy.add_argument("--paranoia", type=int, default=0)
    legacy.add_argument("--hell", action="store_true")
    r.set_defaults(func=cmd_run)

    c = sub.add_parser("compile", help="kompilasi .hl ke bytecode .hbc")
    c.add_argument("file")
    c.add_argument("-o", "--output")
    c.add_argument("--legacy", action="store_true",
                   help="pakai compiler v3 lama (dialek advanced saja; untuk obfuscate/Hell Mode)")
    c.set_defaults(func=cmd_compile)

    d = sub.add_parser("disasm", help="disassemble bytecode (.hbc v3/v4)")
    d.add_argument("file")
    d.set_defaults(func=cmd_disasm)

    dbg = sub.add_parser("debug", help="debugger interaktif berbasis HambaVM v4")
    dbg.add_argument("file")
    dbg.add_argument("-b", "--breakpoint", type=int, action="append", help="breakpoint baris (boleh berulang)")
    runtime_opts(dbg)
    dbg.set_defaults(func=cmd_debug)

    ck = sub.add_parser("check", help="verifikasi sintaks tanpa menjalankan")
    ck.add_argument("files", nargs="+")
    ck.set_defaults(func=cmd_check)

    rp = sub.add_parser("repl", help="mode interaktif")
    rp.add_argument("--seed", type=int)
    rp.add_argument("--sandbox", action="store_true")
    rp.set_defaults(func=cmd_repl)

    ct = sub.add_parser("ctf", help="jalankan challenge CTF (sandbox)")
    ct.add_argument("file")
    ct.add_argument("--seed", type=int)
    ct.add_argument("--vm", action="store_true")
    ct.add_argument("--step-limit", type=int, default=100_000)
    ct.set_defaults(func=cmd_ctf)

    ob = sub.add_parser("obfuscate", help="[legacy v3] obfuscate bytecode")
    ob.add_argument("file")
    ob.add_argument("--level", type=int, default=1, choices=[1, 2, 3])
    ob.add_argument("--seed", type=int)
    ob.add_argument("--output")
    ob.set_defaults(func=cmd_legacy)

    an = sub.add_parser("analyze", help="[legacy v3] analisis 'akademik' bytecode")
    an.add_argument("file")
    an.add_argument("--deep", action="store_true")
    an.set_defaults(func=cmd_legacy)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # emoji di console Windows
        except (AttributeError, ValueError):
            pass
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1
    for attr, default in (("obfuscated", False), ("paranoia", 0), ("hell", False), ("vm", False),
                          ("trace", False), ("audit", False), ("fast", False), ("ctf", False)):
        if not hasattr(args, attr):
            setattr(args, attr, default)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n⚠ Dihentikan (rapat dibubarkan paksa)", file=sys.stderr)
        return 130
    except BrokenPipeError:
        # mis. `hambalang run x.hl | head`
        try:
            sys.stdout = open(os.devnull, "w")
        except OSError:
            pass
        return 0


if __name__ == "__main__":
    sys.exit(main())
