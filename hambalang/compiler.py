"""
Compiler AST -> bytecode HBC v4.

Setiap statement diawali instruksi ``LINE`` (tick langkah + posisi error)
sehingga jumlah langkah dan nomor baris error di VM sama dengan interpreter.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from hambalang import bytecode as B
from hambalang import nodes as N
from hambalang.bytecode import BINARY_OPS, UNARY_OPS, CodeObject
from hambalang.errors import SalahKetik


@dataclass
class _Loop:
    break_jumps: List[int]
    continue_target: Optional[int]
    continue_jumps: List[int]
    scope_depth: int
    try_depth: int
    has_iter: bool


class _FunctionCompiler:
    def __init__(self, name: str, kind: str, params: List[str]):
        self.co = CodeObject(name=name, kind=kind, params=list(params))
        self.const_index: Dict[Tuple[type, Any], int] = {}
        self.loops: List[_Loop] = []
        self.scope_depth = 0
        self.try_depth = 0
        self.line = 0

    # ------------------------------------------------------------ emit helpers
    def emit(self, op: int, arg: int = 0) -> int:
        self.co.code.append((op, arg))
        self.co.lines.append(self.line)
        return len(self.co.code) - 1

    def patch(self, at: int, target: Optional[int] = None):
        op, _ = self.co.code[at]
        self.co.code[at] = (op, len(self.co.code) if target is None else target)

    def here(self) -> int:
        return len(self.co.code)

    def const(self, value: Any) -> int:
        if isinstance(value, CodeObject):
            self.co.consts.append(value)
            return len(self.co.consts) - 1
        # (tipe, nilai) supaya 1, 1.0, dan benar tidak tergabung.
        key = (type(value), value)
        idx = self.const_index.get(key)
        if idx is None:
            idx = len(self.co.consts)
            self.co.consts.append(value)
            self.const_index[key] = idx
        return idx

    # ------------------------------------------------------------ statements
    def body(self, stmts: List[N.Node]):
        for s in stmts:
            self.stmt(s)

    def stmt(self, node: N.Node):
        self.line = node.line
        self.emit(B.LINE, node.line)
        getattr(self, "s_" + type(node).__name__)(node)

    def s_Print(self, node: N.Print):
        self.expr(node.expr)
        self.emit(B.PRINT)

    def s_ExprStmt(self, node: N.ExprStmt):
        self.expr(node.expr)
        self.emit(B.POP)

    def s_Assign(self, node: N.Assign):
        t = node.target
        if isinstance(t, N.Name):
            if node.op:
                self.emit(B.LOAD_NAME, self.const(t.name))
                self.expr(node.value)
                self.emit(B.BINARY, BINARY_OPS.index(node.op))
            else:
                self.expr(node.value)
            self.emit(B.STORE_NAME, self.const(t.name))
        elif isinstance(t, N.Index):
            self.expr(t.obj)
            self.expr(t.index)
            if node.op:
                self.emit(B.DUP2)
                self.emit(B.INDEX_GET)
                self.expr(node.value)
                self.emit(B.BINARY, BINARY_OPS.index(node.op))
            else:
                self.expr(node.value)
            self.emit(B.INDEX_SET)
        else:
            self.expr(t.obj)
            if node.op:
                self.emit(B.DUP)
                self.emit(B.ATTR_GET, self.const(t.name))
                self.expr(node.value)
                self.emit(B.BINARY, BINARY_OPS.index(node.op))
            else:
                self.expr(node.value)
            self.emit(B.ATTR_SET, self.const(t.name))

    def s_If(self, node: N.If):
        end_jumps = []
        for cond, body in node.branches:
            self.expr(cond)
            skip = self.emit(B.JUMP_IF_FALSE)
            self.body(body)
            end_jumps.append(self.emit(B.JUMP))
            self.patch(skip)
        if node.else_body is not None:
            self.body(node.else_body)
        for j in end_jumps:
            self.patch(j)

    def _loop(self, has_iter: bool, continue_target: Optional[int]) -> _Loop:
        loop = _Loop([], continue_target, [], self.scope_depth, self.try_depth, has_iter)
        self.loops.append(loop)
        return loop

    def s_While(self, node: N.While):
        top = self.here()
        self.expr(node.cond)
        exit_jump = self.emit(B.JUMP_IF_FALSE)
        loop = self._loop(False, None)
        self.body(node.body)
        self.loops.pop()
        # 'lanjut' melompat ke sini: tick back-edge lalu cek kondisi lagi.
        cont = self.here()
        self.line = node.line
        self.emit(B.LINE, node.line)
        self.emit(B.JUMP, top)
        self.patch(exit_jump)
        for j in loop.continue_jumps:
            self.patch(j, cont)
        for j in loop.break_jumps:
            self.patch(j)

    def _iter_loop(self, var: Optional[str], body: List[N.Node], line: int):
        """Loop berbasis iterator (stack teratas = iterator)."""
        top = self.here()
        exhausted = self.emit(B.FOR_ITER)
        if var is None:
            self.emit(B.POP)
        else:
            self.emit(B.STORE_NAME, self.const(var))
        loop = self._loop(True, None)
        self.body(body)
        self.loops.pop()
        # Back-edge: 1 langkah per iterasi (sama dengan interpreter), juga
        # target 'lanjut'. Tanpa ini loop dengan body kosong lolos step limit.
        cont = self.here()
        self.line = line
        self.emit(B.LINE, line)
        self.emit(B.JUMP, top)
        # 'hentikan': buang iterator dulu.
        if loop.break_jumps:
            for j in loop.break_jumps:
                self.patch(j)
            self.emit(B.POP)
        self.patch(exhausted)
        for j in loop.continue_jumps:
            self.patch(j, cont)

    def s_ForRange(self, node: N.ForRange):
        self.expr(node.start)
        self.expr(node.end)
        if node.step is not None:
            self.expr(node.step)
        else:
            self.emit(B.LOAD_CONST, self.const(1))
        self.emit(B.RANGE_ITER)
        self._iter_loop(node.var, node.body, node.line)

    def s_ForEach(self, node: N.ForEach):
        self.expr(node.iterable)
        self.emit(B.GET_ITER)
        self._iter_loop(node.var, node.body, node.line)

    def s_Repeat(self, node: N.Repeat):
        self.expr(node.count)
        self.emit(B.REPEAT_ITER)
        self._iter_loop(None, node.body, node.line)

    def s_FuncDef(self, node: N.FuncDef):
        sub = _FunctionCompiler(node.name, node.kind, node.params)
        sub.line = node.line
        sub.body(node.body)
        sub.emit(B.LOAD_CONST, sub.const(None))
        sub.emit(B.RETURN)
        self.emit(B.MAKE_FUNCTION, self.const(sub.co))
        self.emit(B.STORE_NAME, self.const(node.name))

    def s_Return(self, node: N.Return):
        if node.value is not None:
            self.expr(node.value)
        else:
            self.emit(B.LOAD_CONST, self.const(None))
        self.emit(B.RETURN)

    def _unwind_to(self, loop: _Loop):
        for _ in range(self.try_depth - loop.try_depth):
            self.emit(B.POP_TRY)
        for _ in range(self.scope_depth - loop.scope_depth):
            self.emit(B.POP_SCOPE)

    def s_Break(self, node: N.Break):
        if not self.loops:
            raise SalahKetik("'hentikan' di luar loop", node.line)
        loop = self.loops[-1]
        self._unwind_to(loop)
        loop.break_jumps.append(self.emit(B.JUMP))

    def s_Continue(self, node: N.Continue):
        if not self.loops:
            raise SalahKetik("'lanjut' di luar loop", node.line)
        loop = self.loops[-1]
        self._unwind_to(loop)
        loop.continue_jumps.append(self.emit(B.JUMP))

    def s_Block(self, node: N.Block):
        self.emit(B.PUSH_SCOPE)
        self.scope_depth += 1
        self.body(node.body)
        self.scope_depth -= 1
        self.emit(B.POP_SCOPE)

    def s_Seq(self, node: N.Seq):
        self.body(node.body)

    def s_Try(self, node: N.Try):
        setup = self.emit(B.SETUP_TRY)
        self.try_depth += 1
        self.body(node.body)
        self.try_depth -= 1
        self.emit(B.POP_TRY)
        done = self.emit(B.JUMP)
        self.patch(setup)
        # VM mendorong pesan error ke stack sebelum melompat ke handler.
        if node.err_var:
            self.emit(B.STORE_NAME, self.const(node.err_var))
        else:
            self.emit(B.POP)
        self.body(node.handler)
        self.patch(done)

    def s_Raise(self, node: N.Raise):
        if node.value is not None:
            self.expr(node.value)
        else:
            self.emit(B.LOAD_CONST, self.const("Proyek mangkrak"))
        self.emit(B.RAISE)

    def s_Input(self, node: N.Input):
        if node.prompt is not None:
            self.expr(node.prompt)
        self.emit(B.INPUT, 1 if node.prompt is not None else 0)
        self.emit(B.STORE_NAME, self.const(node.name))

    def s_Global(self, node: N.Global):
        for name in node.names:
            self.emit(B.GLOBAL, self.const(name))

    def s_Halt(self, node: N.Halt):
        self.emit(B.HALT)

    # ------------------------------------------------------------ expressions
    def expr(self, node: N.Node):
        t = type(node)
        if t is N.Literal:
            self.emit(B.LOAD_CONST, self.const(node.value))
        elif t is N.Name:
            self.emit(B.LOAD_NAME, self.const(node.name))
        elif t is N.Binary:
            self.expr(node.left)
            self.expr(node.right)
            self.emit(B.BINARY, BINARY_OPS.index(node.op))
        elif t is N.Logical:
            self.expr(node.left)
            op = B.JUMP_IF_FALSE_OR_POP if node.op == "dan" else B.JUMP_IF_TRUE_OR_POP
            j = self.emit(op)
            self.expr(node.right)
            self.patch(j)
        elif t is N.Unary:
            self.expr(node.operand)
            self.emit(B.UNARY, UNARY_OPS.index(node.op))
        elif t is N.Call:
            self.expr(node.callee)
            for a in node.args:
                self.expr(a)
            self.emit(B.CALL, len(node.args))
        elif t is N.Index:
            self.expr(node.obj)
            self.expr(node.index)
            self.emit(B.INDEX_GET)
        elif t is N.Attr:
            self.expr(node.obj)
            self.emit(B.ATTR_GET, self.const(node.name))
        elif t is N.ListLit:
            for item in node.items:
                self.expr(item)
            self.emit(B.BUILD_LIST, len(node.items))
        elif t is N.DictLit:
            for k, v in node.pairs:
                self.expr(k)
                self.expr(v)
            self.emit(B.BUILD_DICT, len(node.pairs))
        else:
            raise SalahKetik(f"Ekspresi tidak bisa dikompilasi: {t.__name__}", node.line)


def compile_program(program: N.Program, name: str = "<modul>") -> CodeObject:
    fc = _FunctionCompiler(name, "modul", [])
    fc.body(program.body)
    fc.emit(B.LOAD_CONST, fc.const(None))
    fc.emit(B.RETURN)
    return fc.co


def compile_source(source: str, name: str = "<modul>") -> CodeObject:
    from hambalang.parser import parse
    return compile_program(parse(source), name)
