"""
HambaVM v4 — stack machine untuk bytecode HBC v4.

Setiap pemanggilan fungsi membuat ``Frame`` dengan operand stack, environment,
dan stack handler ``coba`` sendiri. Exception di-unwind frame demi frame
sampai ketemu handler, persis seperti semantik interpreter.
"""
from typing import Any, List, Optional, Tuple

from hambalang import bytecode as B
from hambalang.builtins import BUILTINS
from hambalang.bytecode import BINARY_OPS, UNARY_OPS, CodeObject
from hambalang.errors import HambaError, NegaraBangkrut, OperasiIlegal, ProgramSelesai, ProyekMangkrak
from hambalang.interpreter import assign_name, error_value, lookup_name, read_input
from hambalang.runtime import (Builtin, Env, HambaFunction, Runtime, binary_op, get_attr, get_index,
                               iterate, range_values, repeat_count, set_attr, set_index, to_str,
                               truthy, unary_op)


class Frame:
    __slots__ = ("code", "pc", "env", "stack", "handlers", "line", "is_call")

    def __init__(self, code: CodeObject, env: Env, is_call: bool):
        self.code = code
        self.pc = 0
        self.env = env
        self.stack: List[Any] = []
        # (alamat handler, kedalaman stack, env saat SETUP_TRY)
        self.handlers: List[Tuple[int, int, Env]] = []
        self.line = 0
        self.is_call = is_call


class VM:
    def __init__(self, runtime: Optional[Runtime] = None):
        self.rt = runtime or Runtime()
        self.globals = Env()
        self.frames: List[Frame] = []
        self.rt.call_function = self.call_function
        # Hook opsional untuk debugger: dipanggil sebelum tiap instruksi.
        self.trace = None

    # ------------------------------------------------------------ public API
    def run(self, code: CodeObject) -> Any:
        self.frames = [Frame(code, self.globals, is_call=False)]
        try:
            return self._run(0)
        except ProgramSelesai:
            return None
        finally:
            self.frames = []

    def call_function(self, fn: Any, args: List[Any]) -> Any:
        """Dipanggil builtin (petakan, saring, ...) untuk menjalankan fungsi user."""
        if isinstance(fn, Builtin):
            return fn(self.rt, args)
        base = len(self.frames)
        self._push_call(fn, args)
        return self._run(base)

    # ------------------------------------------------------------ internals
    def _push_call(self, fn: Any, args: List[Any]):
        if not isinstance(fn, HambaFunction):
            raise OperasiIlegal(f"Nilai {to_str(fn)} bukan fungsi")
        if len(args) != len(fn.params):
            raise OperasiIlegal(
                f"{fn.kind.capitalize()} '{fn.name}' butuh {len(fn.params)} argumen, diberikan {len(args)}")
        self.rt.enter_call(fn.name)
        env = Env(fn.closure, is_function=(fn.kind == "fungsi"))
        for p, a in zip(fn.params, args):
            env.define(p, a)
        self.frames.append(Frame(fn.code, env, is_call=True))

    def _pop_frame(self) -> Frame:
        frame = self.frames.pop()
        if frame.is_call:
            self.rt.exit_call()
        if self.frames:
            self.rt.current_line = self.frames[-1].line
        return frame

    def _run(self, base: int) -> Any:
        """Jalankan sampai frame di index ``base`` return."""
        while True:
            try:
                return self._loop(base)
            except NegaraBangkrut:
                self._abandon(base)
                raise
            except HambaError as err:
                err.with_position(self.rt.current_line)
                if not self._handle(err, base):
                    raise
            except RecursionError:
                self._abandon(base)
                raise
            except ProgramSelesai:
                raise

    def _abandon(self, base: int):
        while len(self.frames) > base:
            self._pop_frame()

    def _handle(self, err: HambaError, base: int) -> bool:
        """Cari handler 'coba' terdekat; kembalikan False kalau tidak ada."""
        while len(self.frames) > base:
            frame = self.frames[-1]
            if frame.handlers:
                addr, depth, env = frame.handlers.pop()
                del frame.stack[depth:]
                frame.env = env
                frame.stack.append(error_value(err))
                frame.pc = addr
                return True
            self._pop_frame()
        self._abandon(base)
        return False

    def _loop(self, base: int) -> Any:
        rt = self.rt
        frame = self.frames[-1]
        code = frame.code.code
        consts = frame.code.consts
        stack = frame.stack
        trace = self.trace

        # Opcode di-bind ke variabel lokal (jauh lebih cepat daripada B.X di tiap
        # perbandingan) dan diurutkan dari yang paling sering dieksekusi.
        LINE, LOAD_NAME, LOAD_CONST, STORE_NAME = B.LINE, B.LOAD_NAME, B.LOAD_CONST, B.STORE_NAME
        BINARY, JUMP_IF_FALSE, JUMP, FOR_ITER = B.BINARY, B.JUMP_IF_FALSE, B.JUMP, B.FOR_ITER
        CALL, RETURN, INDEX_GET, POP = B.CALL, B.RETURN, B.INDEX_GET, B.POP
        binary_ops = BINARY_OPS

        while True:
            op, arg = code[frame.pc]
            frame.pc += 1
            if trace is not None:
                trace(self, frame, op, arg)

            if op == LINE:
                frame.line = arg
                rt.tick(arg)
            elif op == LOAD_NAME:
                stack.append(lookup_name(rt, frame.env, consts[arg]))
            elif op == LOAD_CONST:
                stack.append(consts[arg])
            elif op == STORE_NAME:
                assign_name(rt, frame.env, consts[arg], stack.pop())
            elif op == BINARY:
                b = stack.pop()
                stack[-1] = binary_op(binary_ops[arg], stack[-1], b)
            elif op == JUMP_IF_FALSE:
                if not truthy(stack.pop()):
                    frame.pc = arg
            elif op == JUMP:
                frame.pc = arg
            elif op == FOR_ITER:
                try:
                    stack.append(next(stack[-1]))
                except StopIteration:
                    stack.pop()
                    frame.pc = arg
            elif op == CALL:
                args = stack[-arg:] if arg else []
                if arg:
                    del stack[-arg:]
                fn = stack.pop()
                if isinstance(fn, Builtin):
                    stack.append(fn(rt, args))
                else:
                    self._push_call(fn, args)
                    frame = self.frames[-1]
                    code, consts, stack = frame.code.code, frame.code.consts, frame.stack
            elif op == RETURN:
                result = stack.pop()
                self._pop_frame()
                if len(self.frames) <= base:
                    return result
                frame = self.frames[-1]
                code, consts, stack = frame.code.code, frame.code.consts, frame.stack
                stack.append(result)
            elif op == INDEX_GET:
                key = stack.pop()
                stack[-1] = get_index(stack[-1], key)
            elif op == POP:
                stack.pop()
            else:
                self._exec_rare(frame, op, arg)
                # Opcode langka bisa mengganti env, tapi tidak frame/stack.

    def _exec_rare(self, frame: Frame, op: int, arg: int):
        """Opcode yang jarang muncul di hot loop."""
        rt = self.rt
        stack = frame.stack
        consts = frame.code.consts
        if op == B.DUP:
            stack.append(stack[-1])
        elif op == B.DUP2:
            stack.extend(stack[-2:])
        elif op == B.UNARY:
            stack[-1] = unary_op(UNARY_OPS[arg], stack[-1])
        elif op == B.JUMP_IF_FALSE_OR_POP:
            if truthy(stack[-1]):
                stack.pop()
            else:
                frame.pc = arg
        elif op == B.JUMP_IF_TRUE_OR_POP:
            if truthy(stack[-1]):
                frame.pc = arg
            else:
                stack.pop()
        elif op == B.INDEX_SET:
            value = stack.pop()
            key = stack.pop()
            set_index(stack.pop(), key, value)
        elif op == B.ATTR_GET:
            stack[-1] = get_attr(stack[-1], consts[arg])
        elif op == B.ATTR_SET:
            value = stack.pop()
            set_attr(stack.pop(), consts[arg], value)
        elif op == B.BUILD_LIST:
            if arg:
                items = stack[-arg:]
                del stack[-arg:]
            else:
                items = []
            stack.append(items)
        elif op == B.BUILD_DICT:
            flat = stack[-2 * arg:] if arg else []
            if arg:
                del stack[-2 * arg:]
            d = {}
            for i in range(0, len(flat), 2):
                k = flat[i]
                d[k if isinstance(k, str) else to_str(k)] = flat[i + 1]
            stack.append(d)
        elif op == B.PRINT:
            rt.write(to_str(stack.pop()))
        elif op == B.GET_ITER:
            stack[-1] = iter(iterate(stack[-1]))
        elif op == B.RANGE_ITER:
            step = stack.pop()
            end = stack.pop()
            start = stack.pop()
            stack.append(_eager_check(range_values(start, end, step)))
        elif op == B.REPEAT_ITER:
            stack[-1] = iter(range(repeat_count(stack[-1])))
        elif op == B.MAKE_FUNCTION:
            co = consts[arg]
            stack.append(HambaFunction(co.name, co.params, co.kind, frame.env, code=co))
        elif op == B.PUSH_SCOPE:
            frame.env = Env(frame.env)
        elif op == B.POP_SCOPE:
            frame.env = frame.env.parent
        elif op == B.SETUP_TRY:
            frame.handlers.append((arg, len(stack), frame.env))
        elif op == B.POP_TRY:
            frame.handlers.pop()
        elif op == B.RAISE:
            raise ProyekMangkrak(to_str(stack.pop()), frame.line)
        elif op == B.INPUT:
            prompt = to_str(stack.pop()) if arg else None
            stack.append(read_input(rt, prompt))
        elif op == B.GLOBAL:
            frame.env.declare_global([consts[arg]])
        elif op == B.HALT:
            BUILTINS["selesai"](rt, [])
        elif op == B.NOP:
            pass
        else:
            raise OperasiIlegal(f"Opcode tidak dikenal: {op}")


def _eager_check(gen):
    """Validasi argumen range sekarang (generator Python baru jalan saat next())."""
    try:
        first = next(gen)
    except StopIteration:
        return iter(())

    def chain():
        yield first
        yield from gen

    return chain()
