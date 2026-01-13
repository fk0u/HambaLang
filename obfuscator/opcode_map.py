"""
Dynamic Opcode Remapping - Anti-Static Analysis
Maps standard opcodes to randomized values at runtime
"""
import random
import struct
from typing import Dict, Tuple, List, Optional
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


class Instruction:
    def __init__(self, opcode: int, operand: bytes = b'', original_addr: int = 0):
        self.opcode = opcode
        self.operand = operand
        self.original_addr = original_addr
        self.new_addr = 0
        self.is_junk = False

    def size(self):
        return 1 + len(self.operand)

class BytecodeAnalyzer:
    """Parses bytecode into instructions to enable structure-aware modification"""
    
    def parse(self, code: bytes) -> List[Instruction]:
        instructions = []
        i = 0
        while i < len(code):
            opcode = code[i]
            addr = i
            i += 1
            
            # Determine arguments based on opcode
            # Opcodes with 2-byte argument (unsigned short)
            if opcode in [OP_PUSH, OP_LOAD, OP_STORE, OP_JUMP, OP_JUMP_IF_FALSE, OP_CALL]:
                if i + 2 <= len(code):
                    operand = code[i:i+2]
                    i += 2
                else:
                    # EOF - shouldn't happen in valid code
                    operand = b''
            else:
                operand = b''
            
            instructions.append(Instruction(opcode, operand, addr))
        
        return instructions

def obfuscate_bytecode(bytecode_obj, seed: int = None, level: int = 1) -> Tuple[bytes, Dict]:
    mapper = OpcodeMapper(seed)
    rng = random.Random(seed)
    
    # 1. Parse original bytecode to get structure
    # NOTE: We parse the RAW (Original) bytecode BEFORE any remapping
    # So we can identify JUMPs correctly.
    analyzer = BytecodeAnalyzer()
    
    # If bytecode is already bytes, use it, else bytecode_obj.code
    code_bytes = bytes(bytecode_obj.code)
    instructions = analyzer.parse(code_bytes)
    
    final_instructions = []
    
    # LEVEL 2: Junk Injection
    if level >= 2:
        for instr in instructions:
            # Inject Junk (NOP or remapped junk)
            if rng.random() < 0.2:
                # Insert a NOP that will be obfuscated later
                # Mark as junk so we don't fixup its jump if it was a jump (unlikely)
                junk = Instruction(OP_NOP, b'', -1)
                junk.is_junk = True
                final_instructions.append(junk)
                
                # Double junk sometimes
                if rng.random() < 0.3:
                     final_instructions.append(Instruction(OP_NOP, b'', -1))
            
            final_instructions.append(instr)
    else:
        final_instructions = instructions

    # LEVEL 3: Reordering (Simplistic Block Shuffle)
    # WARNING: To support reordering safely, we need basic block analysis.
    # Without it, reordering arbitrary instructions breaks execution flow (e.g. splitting PUSH/ADD).
    # Since Phase 5 demands correctness, we will SKIP Reordering for now and focus on Junk Injection correctness.
    # Or we can just reorder independent sequences.
    # We will stick to Junk Injection which shifts addresses, which is enough to break naive analysis.
    
    # 3. Address Recalculation
    current_addr = 0
    addr_map = {} # old_addr -> new_addr
    
    for instr in final_instructions:
        instr.new_addr = current_addr
        if instr.original_addr != -1:
            addr_map[instr.original_addr] = current_addr
        current_addr += instr.size()
        
    # 4. Jump Target Fixup
    for instr in final_instructions:
        if instr.opcode in [OP_JUMP, OP_JUMP_IF_FALSE]:
            if len(instr.operand) == 2:
                old_target = struct.unpack('<H', instr.operand)[0]
                
                if old_target in addr_map:
                    new_target = addr_map[old_target]
                    instr.operand = struct.pack('<H', new_target)
                else:
                    # Target might be end of code (e.g. exit)
                    # If old_target == len(code_bytes), map directly
                    if old_target == len(code_bytes):
                         # Map to end of new code
                         new_target = current_addr
                         instr.operand = struct.pack('<H', new_target)

    # 5. Serialization and Opcode Remapping
    final_code = bytearray()
    for instr in final_instructions:
        # Remap opcode
        obf_opcode = mapper.obfuscate(instr.opcode)
        final_code.append(obf_opcode)
        final_code.extend(instr.operand)

    metadata = {
        'obfuscation_seed': seed,
        'obfuscation_level': level,
        'mapper': mapper.forward_map
    }
    
    return bytes(final_code), metadata


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
