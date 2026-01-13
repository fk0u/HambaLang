#!/usr/bin/env python3
"""
HambaLang Interpreter v3 - Advanced Edition
Esoteric-but-serious satire language with scoped blocks, procedures,
controlled loops, satirical exceptions, deterministic runtime (CTF mode),
and execution step limit.
"""
import sys
import re
import math
import random
from dataclasses import dataclass
from typing import Any, List, Dict, Optional, Callable

# =====================
# AST Node Definitions
# =====================
@dataclass
class Node:
    line: int

@dataclass
class Program(Node):
    body: List[Node]

@dataclass
class Block(Node):
    body: List[Node]

@dataclass
class SetStmt(Node):
    name: str
    expr: str

@dataclass
class PrintStmt(Node):
    expr: str

@dataclass
class KorupsiStmt(Node):
    percent_expr: str

@dataclass
class MangkrakStmt(Node):
    info: str

@dataclass
class RapatLoop(Node):
    count_expr: str
    body: List[Node]

@dataclass
class ProcDef(Node):
    name: str
    body: List[Node]

@dataclass
class ProcCall(Node):
    name: str

@dataclass
class TryCatch(Node):
    try_body: List[Node]
    catch_body: List[Node]

@dataclass
class IfStmt(Node):
    condition: str
    if_body: List[Node]
    else_body: Optional[List[Node]] = None


# =====================
# Exceptions
# =====================
class HambaError(Exception):
    pass

class ProyekMangkrakError(HambaError):
    pass

class DanaHabisError(HambaError):
    pass

class AuditKPKError(HambaError):
    pass

class StepLimitError(HambaError):
    pass


# =====================
# Expression Evaluator
# =====================
class ExpressionEvaluator:
    def __init__(self, runtime: 'Runtime'):
        self.runtime = runtime

    def eval(self, expr: str) -> Any:
        expr = expr.strip()
        # String literal
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        # Boolean
        if expr == 'benar':
            return True
        if expr == 'salah':
            return False
        # Null
        if expr == 'kosong':
            return None
        # Number
        try:
            if '.' in expr:
                return float(expr)
            if expr.isdigit() or (expr.startswith('-') and expr[1:].isdigit()):
                return int(expr)
        except ValueError:
            pass
        # Function calls for built-ins inside expressions
        func_call = re.match(r'^(\w+)\((.*)\)$', expr)
        if func_call:
            name = func_call.group(1)
            args_str = func_call.group(2)
            args = self._parse_args(args_str)
            if name == 'teks':
                return self.runtime.to_string(args[0]) if args else ''
            if name == 'angka':
                return self.runtime.to_number(args[0]) if args else 0
            if name == 'panjang':
                return len(args[0]) if args else 0
        # Arithmetic and logical (simple)
        for op in ['<=', '>=', '==', '!=', '<', '>']:
            if op in expr:
                left, right = expr.split(op, 1)
                l = self.eval(left)
                r = self.eval(right)
                return self._cmp(l, r, op)
        for op in ['+', '-', '*', '/', '%']:
            # avoid negative number split
            if op == '-' and expr.startswith('-'):
                continue
            if op in expr:
                left, right = expr.split(op, 1)
                return self._arith(self.eval(left), self.eval(right), op)
        # Variable
        if re.match(r'^[a-zA-Z_]\w*$', expr):
            return self.runtime.get(expr)
        raise HambaError(f"Tidak dapat mengevaluasi: {expr}")

    def _parse_args(self, args_str: str) -> List[Any]:
        if not args_str.strip():
            return []
        parts = []
        current = ''
        depth = 0
        in_str = False
        quote = ''
        for ch in args_str:
            if ch in ['"', "'"] and not in_str:
                in_str = True
                quote = ch
                current += ch
                continue
            if in_str and ch == quote:
                in_str = False
                current += ch
                continue
            if not in_str:
                if ch in ['(', '[', '{']:
                    depth += 1
                elif ch in [')', ']', '}']:
                    depth -= 1
                elif ch == ',' and depth == 0:
                    parts.append(current.strip())
                    current = ''
                    continue
            current += ch
        if current.strip():
            parts.append(current.strip())
        return [self.eval(p) for p in parts]

    def _cmp(self, l, r, op):
        if op == '==':
            return l == r
        if op == '!=':
            return l != r
        lnum = self.runtime.to_number(l)
        rnum = self.runtime.to_number(r)
        if op == '<':
            return lnum < rnum
        if op == '>':
            return lnum > rnum
        if op == '<=':
            return lnum <= rnum
        if op == '>=':
            return lnum >= rnum
        return False

    def _arith(self, l, r, op):
        if op == '+':
            if isinstance(l, str) or isinstance(r, str):
                return self.runtime.to_string(l) + self.runtime.to_string(r)
            return self.runtime.to_number(l) + self.runtime.to_number(r)
        if op == '-':
            return self.runtime.to_number(l) - self.runtime.to_number(r)
        if op == '*':
            return self.runtime.to_number(l) * self.runtime.to_number(r)
        if op == '/':
            return self.runtime.to_number(l) / max(self.runtime.to_number(r), 1e-9)
        if op == '%':
            return self.runtime.to_number(l) % max(self.runtime.to_number(r), 1e-9)
        return 0


# =====================
# Runtime
# =====================
class Runtime:
    def __init__(self, seed: Optional[int] = None, step_limit: int = 2000, ctf_mode: bool = False, delay: float = 0.0, debug: bool = False):
        self.scopes: List[Dict[str, Any]] = [
            {
                'anggaran': 1_000_000_000,
                'progress': 0,
                'tahun': 2011,
            }
        ]
        self.procedures: Dict[str, ProcDef] = {}
        self.evaluator = ExpressionEvaluator(self)
        self.random = random.Random(seed if seed is not None else 1337)
        self.step_limit = step_limit
        self.steps = 0
        self.ctf_mode = ctf_mode
        self._korupsi_total = 0
        self.delay = delay
        self.debug = debug

    # Scope helpers
    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def set(self, name: str, value: Any):
        self.scopes[-1][name] = value

    def get(self, name: str) -> Any:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise HambaError(f"Variable '{name}' tidak ditemukan")

    # Converters
    def to_number(self, v: Any) -> float:
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                return 0.0
        if isinstance(v, bool):
            return 1.0 if v else 0.0
        return 0.0

    def to_string(self, v: Any) -> str:
        if v is None:
            return 'kosong'
        if isinstance(v, bool):
            return 'benar' if v else 'salah'
        if isinstance(v, float):
            return f"{v:.6g}"
        return str(v)

    # Step control
    def tick(self):
        self.steps += 1
        self.scopes[0]['tahun'] += 0.01  # fake timeline bump
        if self.delay > 0:
            import time
            time.sleep(self.delay)
        if self.steps > self.step_limit:
            raise StepLimitError("Batas langkah terlampaui")

    # Progress helper
    def update_progress(self, delta: float = 1.0):
        self.scopes[0]['progress'] = min(100, self.scopes[0].get('progress', 0) + delta)

    # Korupsi logic with CTF flag
    def korupsi(self, percent: float):
        anggaran = self.to_number(self.get('anggaran'))
        amount = anggaran * (percent / 100.0)
        new_val = anggaran - amount
        self.scopes[0]['anggaran'] = max(new_val, 0)
        self._korupsi_total += amount
        if new_val <= 0:
            raise DanaHabisError("Dana habis akibat korupsi")
        # Hidden flag trigger
        if self.ctf_mode and int(self._korupsi_total) % 424242 == 0:
            print("FLAG{hambalang_ctf_korupsi}")
        return amount


# =====================
# Parser (line-based)
# =====================
class Parser:
    def __init__(self, lines: List[str]):
        self.lines = lines
        self.pos = 0
        self.total = len(lines)

    def parse(self) -> Program:
        body = []
        while self.pos < self.total:
            node = self._parse_statement()
            if node:
                body.append(node)
        return Program(line=1, body=body)

    def _parse_statement(self) -> Optional[Node]:
        if self.pos >= self.total:
            return None
        raw = self.lines[self.pos]
        line_no = self.pos + 1
        line = raw.strip()
        self.pos += 1
        
        # Remove inline comments
        if '//' in line:
            line = line.split('//')[0].strip()
        
        if not line or line.startswith('//'):
            return None

        # Scoped block
        if line == 'mulai':
            block_body = self._parse_block_until('akhir')
            return Block(line=line_no, body=block_body)

        # try-catch
        if line == 'coba':
            try_body = self._parse_block_until('jikaGagal')
            catch_body = self._parse_block_until('akhirCoba')
            return TryCatch(line=line_no, try_body=try_body, catch_body=catch_body)

        # Rapat loop
        rapat_match = re.match(r'^Rapat\((.+)\)$', line)
        if rapat_match:
            count_expr = rapat_match.group(1)
            body = self._parse_block_until('selesaiRapat')
            return RapatLoop(line=line_no, count_expr=count_expr, body=body)

        # Procedure definition
        proc_match = re.match(r'^prosedur\s+(\w+)\s*\(\)$', line)
        if proc_match:
            name = proc_match.group(1)
            body = self._parse_block_until('akhirProsedur')
            return ProcDef(line=line_no, name=name, body=body)

        # Procedure call
        call_match = re.match(r'^(\w+)\(\)$', line)
        if call_match:
            return ProcCall(line=line_no, name=call_match.group(1))

        # Set assignment
        set_match = re.match(r'^set\s+(\w+)\s*=\s*(.+)$', line)
        if set_match:
            return SetStmt(line=line_no, name=set_match.group(1), expr=set_match.group(2))

        # Print / lapor
        lapor_match = re.match(r'^lapor\s+(.+)$', line)
        if lapor_match:
            return PrintStmt(line=line_no, expr=lapor_match.group(1))

        # Korupsi
        kor_match = re.match(r'^Korupsi\((.+)\)$', line)
        if kor_match:
            return KorupsiStmt(line=line_no, percent_expr=kor_match.group(1))

        # Mangkrak
        mang_match = re.match(r'^Mangkrak\((.+)\)$', line)
        if mang_match:
            return MangkrakStmt(line=line_no, info=mang_match.group(1))
        
        # jika conditional
        if_match = re.match(r'^jika\s+(.+)$', line)
        if if_match:
            condition = if_match.group(1)
            if_body = self._parse_block_until('akhir')
            return IfStmt(line=line_no, condition=condition, if_body=if_body)

        raise HambaError(f"Syntax tidak dikenali (baris {line_no}): {line}")

    def _parse_block_until(self, terminator: str) -> List[Node]:
        body = []
        while self.pos < self.total:
            peek = self.lines[self.pos].strip()
            if peek == terminator:
                self.pos += 1
                break
            stmt = self._parse_statement()
            if stmt:
                body.append(stmt)
        return body


# =====================
# Evaluator
# =====================
class Evaluator:
    def __init__(self, runtime: Runtime):
        self.rt = runtime
        self.eval_expr = runtime.evaluator

    def execute(self, node: Node):
        if self.rt.debug:
            print(f"[TRACE L{node.line}] {node.__class__.__name__}")
        if isinstance(node, Program):
            for stmt in node.body:
                self.execute(stmt)
        elif isinstance(node, Block):
            self.rt.push_scope()
            for stmt in node.body:
                self.execute(stmt)
            self.rt.pop_scope()
        elif isinstance(node, SetStmt):
            self.rt.tick()
            value = self.eval_expr.eval(node.expr)
            self.rt.set(node.name, value)
            self.rt.update_progress(0.5)
        elif isinstance(node, PrintStmt):
            self.rt.tick()
            val = self.eval_expr.eval(node.expr)
            print(self.rt.to_string(val))
        elif isinstance(node, KorupsiStmt):
            self.rt.tick()
            percent = self.rt.to_number(self.eval_expr.eval(node.percent_expr))
            amount = self.rt.korupsi(percent)
            print(f"💰 Korupsi {percent}%: Rp {int(amount):,}")
        elif isinstance(node, MangkrakStmt):
            self.rt.tick()
            print(f"⏳ Proyek Mangkrak: {self.eval_expr.eval(node.info)}")
            raise ProyekMangkrakError("Proyek mangkrak terlalu lama")
        elif isinstance(node, RapatLoop):
            self.rt.tick()
            count = int(self.rt.to_number(self.eval_expr.eval(node.count_expr)))
            for _ in range(count):
                for stmt in node.body:
                    self.execute(stmt)
        elif isinstance(node, ProcDef):
            self.rt.procedures[node.name] = node
        elif isinstance(node, ProcCall):
            if node.name not in self.rt.procedures:
                raise HambaError(f"Prosedur '{node.name}' tidak ditemukan")
            self.rt.push_scope()
            for stmt in self.rt.procedures[node.name].body:
                self.execute(stmt)
            self.rt.pop_scope()
        elif isinstance(node, TryCatch):
            try:
                for stmt in node.try_body:
                    self.execute(stmt)
            except (HambaError, ProyekMangkrakError, DanaHabisError, AuditKPKError) as e:
                print(f"⚠️  Exception: {e}")
                for stmt in node.catch_body:
                    self.execute(stmt)
        elif isinstance(node, IfStmt):
            self.rt.tick()
            condition = self.eval_expr.eval(node.condition)
            if condition:
                for stmt in node.if_body:
                    self.execute(stmt)
            elif node.else_body:
                for stmt in node.else_body:
                    self.execute(stmt)
        else:
            raise HambaError(f"Node tidak dikenali: {node}")


# =====================
# Runner
# =====================
def run_file(filepath: str, seed: Optional[int] = None, step_limit: int = 2000, ctf: bool = False, delay: float = 0.0, debug: bool = False):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    parser = Parser(lines)
    program = parser.parse()
    rt = Runtime(seed=seed, step_limit=step_limit, ctf_mode=ctf, delay=delay, debug=debug)
    evaluator = Evaluator(rt)
    evaluator.execute(program)


def main():
    import argparse
    
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        try:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        except:
            pass
    
    parser = argparse.ArgumentParser(description="HambaLang Advanced Interpreter")
    parser.add_argument('file', help='Path to .hl file')
    parser.add_argument('--seed', type=int, default=None, help='Deterministic seed')
    parser.add_argument('--step-limit', type=int, default=2000, help='Execution step limit')
    parser.add_argument('--ctf', action='store_true', help='Enable CTF mode')
    parser.add_argument('--debug', action='store_true', help='Trace execution steps')
    parser.add_argument('--delay', type=float, default=0.0, help='Delay per step (seconds)')
    args = parser.parse_args()

    run_file(args.file, seed=args.seed, step_limit=args.step_limit, ctf=args.ctf, delay=args.delay, debug=args.debug)


if __name__ == '__main__':
    main()
