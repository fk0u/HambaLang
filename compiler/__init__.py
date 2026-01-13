"""
Initialize compiler package
"""
from compiler.bytecode import (
    BytecodeCompiler,
    Bytecode,
    disassemble,
    OP_NOP, OP_PUSH, OP_POP, OP_LOAD, OP_STORE,
    OP_PRINT, OP_ADD, OP_SUB, OP_MUL, OP_DIV,
    OP_JUMP, OP_JUMP_IF_FALSE, OP_KORUPSI, OP_END
)

__all__ = [
    'BytecodeCompiler',
    'Bytecode',
    'disassemble',
]
