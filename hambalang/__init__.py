"""
HambaLang — bahasa pemrograman satir birokrasi, versi core terpadu.

API singkat::

    from hambalang import run_source
    output = run_source('lapor "Halo, " + "Dunia"', seed=1)

``engine="vm"`` mengompilasi ke bytecode HBC v4 dan menjalankannya di HambaVM;
``engine="interpreter"`` (default) memakai tree-walking interpreter.
"""
from typing import List, Optional

from hambalang.errors import (HambaError, InputBelumLengkap, NegaraBangkrut, OperasiIlegal,
                              ProyekMangkrak, SalahKetik)
from hambalang.parser import parse
from hambalang.runtime import Runtime, deep_recursion

__version__ = "6.0.0"

__all__ = [
    "__version__", "parse", "run_source", "execute", "Runtime", "HambaError", "SalahKetik",
    "OperasiIlegal", "ProyekMangkrak", "NegaraBangkrut", "InputBelumLengkap",
]

def execute(source: str, runtime: Runtime, engine: str = "interpreter", filename: str = "<input>"):
    """Parse + jalankan ``source`` dengan runtime yang sudah disiapkan."""
    try:
        with deep_recursion():
            program = parse(source)
            if engine == "vm":
                from hambalang.compiler import compile_program
                from hambalang.vm import VM
                VM(runtime).run(compile_program(program, filename))
            elif engine == "interpreter":
                from hambalang.interpreter import Interpreter
                Interpreter(runtime).run(program)
            else:
                raise ValueError(f"engine tidak dikenal: {engine}")
    except RecursionError:
        raise OperasiIlegal("Rekursi terlalu dalam (stack birokrasi meluap)", runtime.current_line)
    finally:
        runtime.close()


def run_source(source: str, engine: str = "interpreter", inputs: Optional[List[str]] = None,
               **runtime_opts) -> str:
    """
    Jalankan source dan kembalikan seluruh output sebagai string (berguna untuk
    test/web). Kalau ``output`` diberikan, output tetap diteruskan ke callback itu.
    """
    lines: List[str] = []
    pending = list(inputs or [])
    forward = runtime_opts.pop("output", None)

    def write(text: str):
        lines.append(text)
        if forward is not None:
            forward(text)

    def read(prompt: str) -> str:
        if prompt:
            write(prompt)
        return pending.pop(0) if pending else ""

    runtime_opts.setdefault("input_fn", read)
    rt = Runtime(output=write, **runtime_opts)
    execute(source, rt, engine)
    return "\n".join(lines)
