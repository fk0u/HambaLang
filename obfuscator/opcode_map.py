"""
Dynamic Opcode Remapping - Anti-Static Analysis
Maps standard opcodes to randomized values at runtime
"""
import random
from typing import Dict, Tuple
from compiler.bytecode import *


class OpcodeMapper:
    """Dynamic opcode remapping engine"""
    
    def __init__(self, seed: int = None):
        self.seed = seed
        self.rng = random.Random(seed)
        self.forward_map: Dict[int, int] = {}
        self.reverse_map: Dict[int, int] = {}
        self._generate_mapping()
    
    def _generate_mapping(self):
        """Generate randomized opcode mapping"""
        standard_opcodes = [
            OP_NOP, OP_PUSH, OP_POP, OP_LOAD, OP_STORE,
            OP_PRINT, OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_MOD,
            OP_EQ, OP_LT, OP_GT, OP_JUMP, OP_JUMP_IF_FALSE,
            OP_CALL, OP_RET, OP_KORUPSI, OP_MANGKRAK, OP_RAPAT,
            OP_SLEEP, OP_END
        ]
        
        available = list(range(0x10, 0xF0))
        self.rng.shuffle(available)
        
        for i, opcode in enumerate(standard_opcodes):
            obfuscated = available[i]
            self.forward_map[opcode] = obfuscated
            self.reverse_map[obfuscated] = opcode
    
    def obfuscate(self, opcode: int) -> int:
        """Map standard opcode to obfuscated value"""
        return self.forward_map.get(opcode, opcode)
    
    def deobfuscate(self, opcode: int) -> int:
        """Map obfuscated opcode back to standard"""
        return self.reverse_map.get(opcode, opcode)
    
    def get_decoy_opcodes(self, count: int = 10) -> list:
        """Generate fake opcodes for junk insertion"""
        used = set(self.forward_map.values())
        available = [x for x in range(0x10, 0xF0) if x not in used]
        return self.rng.sample(available, min(count, len(available)))


class JunkInjector:
    """Inject fake instructions into bytecode"""
    
    def __init__(self, seed: int = None):
        self.rng = random.Random(seed)
        self.mapper = OpcodeMapper(seed)
    
    def inject(self, bytecode: bytes, ratio: float = 0.3) -> bytes:
        """Inject junk instructions into bytecode"""
        result = bytearray()
        decoy_opcodes = self.mapper.get_decoy_opcodes()
        
        i = 0
        while i < len(bytecode):
            if self.rng.random() < ratio:
                decoy = self.rng.choice(decoy_opcodes)
                result.append(decoy)
                if self.rng.random() < 0.5:
                    result.append(0x00)
                    result.append(0x00)
            
            result.append(bytecode[i])
            i += 1
        
        return bytes(result)


def obfuscate_bytecode(bytecode_obj, seed: int = None, level: int = 1) -> Tuple[bytes, Dict]:
    """
    Obfuscate bytecode with multiple techniques
    
    Args:
        bytecode_obj: Bytecode object
        seed: Random seed for deterministic obfuscation
        level: 1=remap, 2=remap+junk, 3=remap+junk+reorder
    
    Returns:
        (obfuscated_code, metadata)
    """
    mapper = OpcodeMapper(seed)
    code = bytearray(bytecode_obj.code)
    
    # Level 1: Opcode remapping
    for i in range(len(code)):
        original = code[i]
        if original in mapper.forward_map:
            code[i] = mapper.forward_map[original]
    
    obfuscated = bytes(code)
    
    # Level 2: Junk injection
    if level >= 2:
        injector = JunkInjector(seed)
        obfuscated = injector.inject(obfuscated, ratio=0.2)
    
    # Level 3: Instruction reordering with jump fixup
    if level >= 3:
        obfuscated = _reorder_with_jumps(obfuscated, seed)
    
    metadata = {
        'obfuscation_seed': seed,
        'obfuscation_level': level,
        'mapper': mapper.forward_map
    }
    
    return obfuscated, metadata


def _reorder_with_jumps(code: bytes, seed: int) -> bytes:
    """Reorder instructions and fix jump targets"""
    rng = random.Random(seed)
    
    blocks = []
    i = 0
    current_block = bytearray()
    
    while i < len(code):
        current_block.append(code[i])
        
        if len(current_block) > 10 and rng.random() < 0.3:
            blocks.append(bytes(current_block))
            current_block = bytearray()
        
        i += 1
    
    if current_block:
        blocks.append(bytes(current_block))
    
    indices = list(range(len(blocks)))
    rng.shuffle(indices)
    
    reordered = bytearray()
    for idx in indices:
        reordered.extend(blocks[idx])
    
    return bytes(reordered)


def create_opcode_table_file(seed: int, filepath: str):
    """Save opcode mapping table (for VM runtime)"""
    mapper = OpcodeMapper(seed)
    
    with open(filepath, 'wb') as f:
        f.write(b'HBOP')
        f.write(seed.to_bytes(4, 'little'))
        
        for orig, obf in mapper.forward_map.items():
            f.write(orig.to_bytes(1, 'little'))
            f.write(obf.to_bytes(1, 'little'))


def load_opcode_table(filepath: str) -> OpcodeMapper:
    """Load opcode mapping from file"""
    with open(filepath, 'rb') as f:
        magic = f.read(4)
        if magic != b'HBOP':
            raise ValueError("Invalid opcode table file")
        
        seed = int.from_bytes(f.read(4), 'little')
        mapper = OpcodeMapper(seed)
        
        return mapper
