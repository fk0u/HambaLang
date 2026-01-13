"""
HambaLang Bytecode Compiler
Compiles AST to stack-based bytecode (.hbc format)
"""
import struct
from typing import List, Dict, Any
from dataclasses import dataclass

# Bytecode Opcodes
OP_NOP = 0x00
OP_PUSH = 0x01
OP_POP = 0x02
OP_LOAD = 0x03      # Load variable
OP_STORE = 0x04     # Store variable
OP_PRINT = 0x10
OP_ADD = 0x20
OP_SUB = 0x21
OP_MUL = 0x22
OP_DIV = 0x23
OP_MOD = 0x24
OP_EQ = 0x30
OP_LT = 0x31
OP_GT = 0x32
OP_JUMP = 0x40
OP_JUMP_IF_FALSE = 0x41
OP_CALL = 0x50
OP_RET = 0x51
OP_KORUPSI = 0x60   # Satire: Corrupt budget
OP_MANGKRAK = 0x61  # Satire: Project fail
OP_RAPAT = 0x62     # Satire: Meeting loop
OP_SLEEP = 0x70     # Delay execution
OP_END = 0xFF

OPCODE_NAMES = {
    OP_NOP: 'NOP',
    OP_PUSH: 'PUSH',
    OP_POP: 'POP',
    OP_LOAD: 'LOAD',
    OP_STORE: 'STORE',
    OP_PRINT: 'PRINT',
    OP_ADD: 'ADD',
    OP_SUB: 'SUB',
    OP_MUL: 'MUL',
    OP_DIV: 'DIV',
    OP_MOD: 'MOD',
    OP_EQ: 'EQ',
    OP_LT: 'LT',
    OP_GT: 'GT',
    OP_JUMP: 'JUMP',
    OP_JUMP_IF_FALSE: 'JIF',
    OP_CALL: 'CALL',
    OP_RET: 'RET',
    OP_KORUPSI: 'KORUPSI',
    OP_MANGKRAK: 'MANGKRAK',
    OP_RAPAT: 'RAPAT',
    OP_SLEEP: 'SLEEP',
    OP_END: 'END'
}

@dataclass
class Bytecode:
    """Compiled bytecode container"""
    code: bytes
    constants: List[Any]
    strings: List[str]
    metadata: Dict[str, Any]
    
    def save(self, filepath: str):
        """Save bytecode to .hbc file"""
        with open(filepath, 'wb') as f:
            # Magic header: HBC\x00
            f.write(b'HBC\x00')
            # Version
            f.write(struct.pack('H', 3))
            # Code length
            f.write(struct.pack('I', len(self.code)))
            f.write(self.code)
            # Constants count
            f.write(struct.pack('H', len(self.constants)))
            for c in self.constants:
                self._write_constant(f, c)
            # Strings count
            f.write(struct.pack('H', len(self.strings)))
            for s in self.strings:
                encoded = s.encode('utf-8')
                f.write(struct.pack('H', len(encoded)))
                f.write(encoded)
    
    def _write_constant(self, f, val):
        if isinstance(val, int):
            f.write(b'I')
            f.write(struct.pack('q', val))
        elif isinstance(val, float):
            f.write(b'F')
            f.write(struct.pack('d', val))
        elif isinstance(val, str):
            f.write(b'S')
            encoded = val.encode('utf-8')
            f.write(struct.pack('H', len(encoded)))
            f.write(encoded)
        else:
            f.write(b'N')
    
    @classmethod
    def load(cls, filepath: str):
        """Load bytecode from .hbc file"""
        with open(filepath, 'rb') as f:
            magic = f.read(4)
            if magic != b'HBC\x00':
                raise ValueError("Invalid bytecode file")
            version = struct.unpack('H', f.read(2))[0]
            code_len = struct.unpack('I', f.read(4))[0]
            code = f.read(code_len)
            const_count = struct.unpack('H', f.read(2))[0]
            constants = [cls._read_constant(f) for _ in range(const_count)]
            str_count = struct.unpack('H', f.read(2))[0]
            strings = []
            for _ in range(str_count):
                str_len = struct.unpack('H', f.read(2))[0]
                strings.append(f.read(str_len).decode('utf-8'))
            return cls(code=code, constants=constants, strings=strings, metadata={'version': version})
    
    @classmethod
    def _read_constant(cls, f):
        typ = f.read(1)
        if typ == b'I':
            return struct.unpack('q', f.read(8))[0]
        elif typ == b'F':
            return struct.unpack('d', f.read(8))[0]
        elif typ == b'S':
            str_len = struct.unpack('H', f.read(2))[0]
            return f.read(str_len).decode('utf-8')
        else:
            return None


class BytecodeCompiler:
    """Compiles AST nodes to bytecode"""
    
    def __init__(self):
        self.code = bytearray()
        self.constants = []
        self.strings = []
        self.labels = {}
        self.var_map = {}
        self.next_var_id = 0
    
    def compile(self, ast) -> Bytecode:
        """Compile AST to bytecode"""
        from interpreter.hamba_advanced import Program, Block, SetStmt, PrintStmt, KorupsiStmt
        from interpreter.hamba_advanced import MangkrakStmt, RapatLoop, ProcDef, ProcCall, TryCatch, IfStmt
        
        self._compile_node(ast)
        self.emit(OP_END)
        
        return Bytecode(
            code=bytes(self.code),
            constants=self.constants,
            strings=self.strings,
            metadata={'vars': self.var_map}
        )
    
    def _compile_node(self, node):
        from interpreter.hamba_advanced import Program, Block, SetStmt, PrintStmt, KorupsiStmt
        from interpreter.hamba_advanced import MangkrakStmt, RapatLoop, ProcDef, ProcCall, TryCatch, IfStmt
        
        if isinstance(node, Program):
            for stmt in node.body:
                self._compile_node(stmt)
        
        elif isinstance(node, Block):
            for stmt in node.body:
                self._compile_node(stmt)
        
        elif isinstance(node, SetStmt):
            # Compile expression
            self._compile_expr(node.expr)
            # Store to variable
            var_id = self._get_var_id(node.name)
            self.emit(OP_STORE, var_id)
        
        elif isinstance(node, PrintStmt):
            self._compile_expr(node.expr)
            self.emit(OP_PRINT)
        
        elif isinstance(node, KorupsiStmt):
            self._compile_expr(node.percent_expr)
            self.emit(OP_KORUPSI)
        
        elif isinstance(node, MangkrakStmt):
            # Push string info
            str_id = self._add_string(node.info)
            self.emit(OP_PUSH, str_id | 0x8000)  # High bit = string
            self.emit(OP_MANGKRAK)
        
        elif isinstance(node, RapatLoop):
            # Push count
            self._compile_expr(node.count_expr)
            # RAPAT opcode with jump back
            loop_start = len(self.code)
            for stmt in node.body:
                self._compile_node(stmt)
            self.emit(OP_RAPAT, loop_start)
        
        elif isinstance(node, IfStmt):
            self._compile_expr(node.condition)
            # Jump if false
            jif_pos = len(self.code)
            self.emit(OP_JUMP_IF_FALSE, 0)  # Placeholder
            # If body
            for stmt in node.if_body:
                self._compile_node(stmt)
            # Patch jump
            self.code[jif_pos + 1] = len(self.code) & 0xFF
            self.code[jif_pos + 2] = (len(self.code) >> 8) & 0xFF
    
    def _compile_expr(self, expr: str):
        """Compile expression to bytecode"""
        expr = expr.strip()
        
        # String literal
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            str_val = expr[1:-1]
            str_id = self._add_string(str_val)
            self.emit(OP_PUSH, str_id | 0x8000)
            return
        
        # Number literal
        try:
            if '.' in expr:
                val = float(expr)
                const_id = self._add_constant(val)
                self.emit(OP_PUSH, const_id)
                return
            else:
                val = int(expr)
                const_id = self._add_constant(val)
                self.emit(OP_PUSH, const_id)
                return
        except ValueError:
            pass
        
        # Variable
        if expr.isalpha() or '_' in expr:
            var_id = self._get_var_id(expr)
            self.emit(OP_LOAD, var_id)
            return
        
        # Binary operations
        for op_str, opcode in [('+', OP_ADD), ('-', OP_SUB), ('*', OP_MUL), ('/', OP_DIV), ('==', OP_EQ), ('<', OP_LT), ('>', OP_GT)]:
            if op_str in expr:
                parts = expr.split(op_str, 1)
                self._compile_expr(parts[0])
                self._compile_expr(parts[1])
                self.emit(opcode)
                return
    
    def emit(self, opcode: int, operand: int = 0):
        """Emit bytecode instruction"""
        self.code.append(opcode)
        if operand != 0 or opcode in [OP_PUSH, OP_LOAD, OP_STORE, OP_JUMP, OP_JUMP_IF_FALSE]:
            self.code.append(operand & 0xFF)
            self.code.append((operand >> 8) & 0xFF)
    
    def _add_constant(self, val: Any) -> int:
        if val not in self.constants:
            self.constants.append(val)
        return self.constants.index(val)
    
    def _add_string(self, s: str) -> int:
        if s not in self.strings:
            self.strings.append(s)
        return self.strings.index(s)
    
    def _get_var_id(self, name: str) -> int:
        if name not in self.var_map:
            self.var_map[name] = self.next_var_id
            self.next_var_id += 1
        return self.var_map[name]


def disassemble(bytecode: Bytecode) -> str:
    """Disassemble bytecode for debugging"""
    output = []
    output.append("=== HAMBALANG BYTECODE ===")
    output.append(f"Version: {bytecode.metadata.get('version', 0)}")
    output.append(f"Code size: {len(bytecode.code)} bytes")
    output.append(f"Constants: {len(bytecode.constants)}")
    output.append(f"Strings: {len(bytecode.strings)}")
    output.append("\n=== CONSTANTS ===")
    for i, c in enumerate(bytecode.constants):
        output.append(f"  #{i}: {c}")
    output.append("\n=== STRINGS ===")
    for i, s in enumerate(bytecode.strings):
        output.append(f"  @{i}: \"{s}\"")
    output.append("\n=== DISASSEMBLY ===")
    
    pc = 0
    code = bytecode.code
    while pc < len(code):
        opcode = code[pc]
        op_name = OPCODE_NAMES.get(opcode, f"UNK({opcode:02X})")
        line = f"{pc:04d}  {op_name}"
        
        if opcode in [OP_PUSH, OP_LOAD, OP_STORE, OP_JUMP, OP_JUMP_IF_FALSE, OP_CALL]:
            if pc + 2 < len(code):
                operand = code[pc + 1] | (code[pc + 2] << 8)
                if opcode == OP_PUSH and operand & 0x8000:
                    str_id = operand & 0x7FFF
                    line += f" @{str_id}"
                    if str_id < len(bytecode.strings):
                        line += f' "{bytecode.strings[str_id]}"'
                else:
                    line += f" #{operand}"
                pc += 3
            else:
                pc += 1
        else:
            pc += 1
        
        output.append(line)
    
    return '\n'.join(output)
