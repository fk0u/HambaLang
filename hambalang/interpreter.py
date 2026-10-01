"""
Tree-walking interpreter HambaLang (engine referensi).

HambaVM v4 (``hambalang.vm``) harus menghasilkan output yang sama persis
dengan interpreter ini untuk program apa pun; test suite memverifikasinya.
"""
from typing import Any, List, Optional

from hambalang import nodes as N
from hambalang.builtins import BUILTINS
from hambalang.errors import HambaError, NegaraBangkrut, OperasiIlegal, ProgramSelesai, ProyekMangkrak
from hambalang.runtime import (STATE_VARS, Builtin, Env, HambaFunction, Runtime, binary_op, get_attr,
                               get_index, iterate, parse_number, range_values, repeat_count,
                               set_attr, set_index, to_str, truthy, unary_op)


class _Break(Exception):
    pass


class _Continue(Exception):
    pass


class _Return(Exception):
    def __init__(self, value: Any):
        self.value = value


def lookup_name(rt: Runtime, env: Env, name: str) -> Any:
    if name in STATE_VARS:
        return rt.get_state(name)
    try:
        return env.lookup(name)
    except KeyError:
        pass
    b = BUILTINS.get(name)
    if b is not None:
        return b
    raise OperasiIlegal(f"Variabel '{name}' tidak ditemukan")


def assign_name(rt: Runtime, env: Env, name: str, value: Any):
    if name in STATE_VARS:
        rt.set_state(name, value)
    else:
        env.assign(name, value)


def read_input(rt: Runtime, prompt: Optional[str]) -> Any:
    """``Tagih x``: input yang terlihat seperti angka otomatis jadi angka."""
    raw = rt.read(prompt if prompt is not None else "")
    n = parse_number(raw)
    return n if n is not None and raw.strip() else raw


def error_value(err: HambaError) -> str:
    return err.message


class Interpreter:
    def __init__(self, runtime: Optional[Runtime] = None):
        self.rt = runtime or Runtime()
        self.globals = Env()
        self.rt.call_function = self.call_function

    # ------------------------------------------------------------ public API
    def run(self, program: N.Program) -> None:
        try:
            self.exec_body(program.body, self.globals)
        except ProgramSelesai:
            pass
        except _Return:
            pass  # 'kembalikan' di top-level = berhenti

    def run_source(self, source: str) -> None:
        from hambalang.parser import parse
        self.run(parse(source))

    def eval_repl(self, program: N.Program) -> Any:
        """Jalankan program REPL; kembalikan nilai ekspresi terakhir (kalau ada)."""
        result = None
        try:
            for stmt in program.body:
                if isinstance(stmt, N.ExprStmt):
                    self.rt.tick(stmt.line)
                    try:
                        result = self.eval(stmt.expr, self.globals)
                    except HambaError as e:
                        raise e.with_position(stmt.line)
                else:
                    result = None
                    self.exec(stmt, self.globals)
        except ProgramSelesai:
            pass
        except (_Break, _Continue, _Return):
            raise OperasiIlegal("'hentikan'/'lanjut'/'kembalikan' di luar tempatnya")
        return result

    # ------------------------------------------------------------ statements
    def exec_body(self, body: List[N.Node], env: Env):
        for stmt in body:
            self.exec(stmt, env)

    def exec(self, node: N.Node, env: Env):
        rt = self.rt
        rt.tick(node.line)
        try:
            method = getattr(self, "exec_" + type(node).__name__)
            method(node, env)
        except HambaError as e:
            raise e.with_position(node.line)

    def exec_Print(self, node: N.Print, env: Env):
        self.rt.write(to_str(self.eval(node.expr, env)))

    def exec_ExprStmt(self, node: N.ExprStmt, env: Env):
        self.eval(node.expr, env)

    def exec_Assign(self, node: N.Assign, env: Env):
        # Urutan evaluasi (nilai lama dulu, baru ruas kanan) sama dengan VM.
        target = node.target
        if isinstance(target, N.Name):
            old = lookup_name(self.rt, env, target.name) if node.op else None
            value = self.eval(node.value, env)
            if node.op:
                value = binary_op(node.op, old, value)
            assign_name(self.rt, env, target.name, value)
        elif isinstance(target, N.Index):
            obj = self.eval(target.obj, env)
            key = self.eval(target.index, env)
            old = get_index(obj, key) if node.op else None
            value = self.eval(node.value, env)
            if node.op:
                value = binary_op(node.op, old, value)
            set_index(obj, key, value)
        else:
            obj = self.eval(target.obj, env)
            old = get_attr(obj, target.name) if node.op else None
            value = self.eval(node.value, env)
            if node.op:
                value = binary_op(node.op, old, value)
            set_attr(obj, target.name, value)

    def exec_If(self, node: N.If, env: Env):
        for cond, body in node.branches:
            if truthy(self.eval(cond, env)):
                self.exec_body(body, env)
                return
        if node.else_body is not None:
            self.exec_body(node.else_body, env)

    def _loop_body(self, body: List[N.Node], env: Env) -> bool:
        """Jalankan body loop. Return False kalau 'hentikan'."""
        try:
            self.exec_body(body, env)
        except _Break:
            return False
        except _Continue:
            pass
        return True

    def exec_While(self, node: N.While, env: Env):
        while truthy(self.eval(node.cond, env)):
            if not self._loop_body(node.body, env):
                break
            self.rt.tick(node.line)

    def exec_ForRange(self, node: N.ForRange, env: Env):
        start = self.eval(node.start, env)
        end = self.eval(node.end, env)
        step = self.eval(node.step, env) if node.step is not None else 1
        for i in range_values(start, end, step):
            assign_name(self.rt, env, node.var, i)
            if not self._loop_body(node.body, env):
                break
            self.rt.tick(node.line)

    def exec_ForEach(self, node: N.ForEach, env: Env):
        for item in iterate(self.eval(node.iterable, env)):
            assign_name(self.rt, env, node.var, item)
            if not self._loop_body(node.body, env):
                break
            self.rt.tick(node.line)

    def exec_Repeat(self, node: N.Repeat, env: Env):
        for _ in range(repeat_count(self.eval(node.count, env))):
            if not self._loop_body(node.body, env):
                break
            self.rt.tick(node.line)

    def exec_FuncDef(self, node: N.FuncDef, env: Env):
        fn = HambaFunction(node.name, node.params, node.kind, env, body=node.body)
        assign_name(self.rt, env, node.name, fn)

    def exec_Return(self, node: N.Return, env: Env):
        raise _Return(self.eval(node.value, env) if node.value is not None else None)

    def exec_Break(self, node: N.Break, env: Env):
        raise _Break()

    def exec_Continue(self, node: N.Continue, env: Env):
        raise _Continue()

    def exec_Block(self, node: N.Block, env: Env):
        self.exec_body(node.body, Env(env))

    def exec_Seq(self, node: N.Seq, env: Env):
        self.exec_body(node.body, env)

    def exec_Try(self, node: N.Try, env: Env):
        try:
            self.exec_body(node.body, env)
        except NegaraBangkrut:
            raise
        except HambaError as e:
            if node.err_var:
                assign_name(self.rt, env, node.err_var, error_value(e))
            self.exec_body(node.handler, env)

    def exec_Raise(self, node: N.Raise, env: Env):
        msg = to_str(self.eval(node.value, env)) if node.value is not None else "Proyek mangkrak"
        raise ProyekMangkrak(msg, node.line)

    def exec_Input(self, node: N.Input, env: Env):
        prompt = to_str(self.eval(node.prompt, env)) if node.prompt is not None else None
        assign_name(self.rt, env, node.name, read_input(self.rt, prompt))

    def exec_Global(self, node: N.Global, env: Env):
        env.declare_global(node.names)

    def exec_Halt(self, node: N.Halt, env: Env):
        BUILTINS["selesai"](self.rt, [])

    # ------------------------------------------------------------ expressions
    def eval(self, node: N.Node, env: Env) -> Any:
        t = type(node)
        if t is N.Literal:
            return node.value
        if t is N.Name:
            return lookup_name(self.rt, env, node.name)
        if t is N.Binary:
            return binary_op(node.op, self.eval(node.left, env), self.eval(node.right, env))
        if t is N.Logical:
            left = self.eval(node.left, env)
            if node.op == "dan":
                return self.eval(node.right, env) if truthy(left) else left
            return left if truthy(left) else self.eval(node.right, env)
        if t is N.Unary:
            return unary_op(node.op, self.eval(node.operand, env))
        if t is N.Call:
            callee = self.eval(node.callee, env)
            args = [self.eval(a, env) for a in node.args]
            return self.call_function(callee, args)
        if t is N.Index:
            return get_index(self.eval(node.obj, env), self.eval(node.index, env))
        if t is N.Attr:
            return get_attr(self.eval(node.obj, env), node.name)
        if t is N.ListLit:
            return [self.eval(i, env) for i in node.items]
        if t is N.DictLit:
            out = {}
            for k, v in node.pairs:
                key = self.eval(k, env)
                out[key if isinstance(key, str) else to_str(key)] = self.eval(v, env)
            return out
        raise OperasiIlegal(f"Node tidak dikenal: {t.__name__}")

    def call_function(self, fn: Any, args: List[Any]) -> Any:
        if isinstance(fn, Builtin):
            return fn(self.rt, args)
        if not isinstance(fn, HambaFunction):
            raise OperasiIlegal(f"Nilai {to_str(fn)!s} bukan fungsi")
        if len(args) != len(fn.params):
            raise OperasiIlegal(
                f"{fn.kind.capitalize()} '{fn.name}' butuh {len(fn.params)} argumen, diberikan {len(args)}")
        local = Env(fn.closure, is_function=(fn.kind == "fungsi"))
        for p, a in zip(fn.params, args):
            local.define(p, a)
        self.rt.enter_call(fn.name)
        try:
            self.exec_body(fn.body, local)
        except _Return as r:
            return r.value
        finally:
            self.rt.exit_call()
        return None
