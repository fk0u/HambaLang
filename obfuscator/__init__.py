"""
Initialize obfuscator package
"""
from obfuscator.opcode_map import OpcodeMapper, obfuscate_bytecode
from obfuscator.self_modify import SelfModifyEngine, PolymorphicTransformer

__all__ = ['OpcodeMapper', 'obfuscate_bytecode', 'SelfModifyEngine', 'PolymorphicTransformer']
