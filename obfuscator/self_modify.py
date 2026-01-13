"""
Self-Modifying Bytecode Engine
Bytecode that modifies itself during execution
"""
import struct
from typing import List, Callable


class SelfModifyEngine:
    """Manages self-modifying bytecode transformations"""
    
    def __init__(self, seed: int = None):
        self.seed = seed
        self.modifications: List[Callable] = []
        self.execution_count = {}
        self.mutation_rules = {}
    
    def add_mutation_rule(self, opcode: int, condition: Callable, transformation: Callable):
        """
        Add rule: when opcode executes and condition met, apply transformation
        
        Args:
            opcode: Target opcode to monitor
            condition: Function(vm_state) -> bool
            transformation: Function(code, pc) -> modified_code
        """
        if opcode not in self.mutation_rules:
            self.mutation_rules[opcode] = []
        
        self.mutation_rules[opcode].append({
            'condition': condition,
            'transformation': transformation
        })
    
    def should_mutate(self, opcode: int, vm_state: dict) -> bool:
        """Check if opcode should mutate given current VM state"""
        if opcode not in self.mutation_rules:
            return False
        
        for rule in self.mutation_rules[opcode]:
            if rule['condition'](vm_state):
                return True
        
        return False
    
    def apply_mutation(self, code: bytearray, pc: int, opcode: int) -> bytearray:
        """Apply mutation transformation to bytecode"""
        if opcode not in self.mutation_rules:
            return code
        
        for rule in self.mutation_rules[opcode]:
            code = rule['transformation'](code, pc)
        
        return code


class PolymorphicTransformer:
    """Creates polymorphic bytecode variants"""
    
    def __init__(self, seed: int = None):
        import random
        self.rng = random.Random(seed)
    
    def create_variant(self, bytecode: bytes) -> bytes:
        """Create functionally equivalent bytecode variant"""
        code = bytearray(bytecode)
        transformations = [
            self._insert_nop_sleds,
            self._swap_commutative_ops,
            self._expand_constants
        ]
        
        for transform in transformations:
            if self.rng.random() < 0.7:
                code = transform(code)
        
        return bytes(code)
    
    def _insert_nop_sleds(self, code: bytearray) -> bytearray:
        """Insert NOP instructions at random positions"""
        from compiler.bytecode import OP_NOP
        
        result = bytearray()
        for i, byte in enumerate(code):
            if self.rng.random() < 0.1:
                result.append(OP_NOP)
            result.append(byte)
        
        return result
    
    def _swap_commutative_ops(self, code: bytearray) -> bytearray:
        """Swap order of commutative operations (ADD, MUL)"""
        from compiler.bytecode import OP_ADD, OP_MUL
        
        i = 0
        while i < len(code):
            if code[i] in [OP_ADD, OP_MUL]:
                if i >= 6:
                    temp = code[i-6:i-3]
                    code[i-6:i-3] = code[i-3:i]
                    code[i-3:i] = temp
            i += 1
        
        return code
    
    def _expand_constants(self, code: bytearray) -> bytearray:
        """Replace constants with computed equivalents"""
        return code


def create_metamorphic_vm_code(base_code: bytes, generations: int = 3, seed: int = None):
    """
    Create multiple generations of self-modifying code
    Each generation produces different bytecode but same behavior
    """
    import random
    rng = random.Random(seed)
    
    variants = [base_code]
    
    for gen in range(generations):
        transformer = PolymorphicTransformer(rng.randint(0, 1000000))
        variant = transformer.create_variant(variants[-1])
        variants.append(variant)
    
    return variants


class RuntimeMutator:
    """Applies mutations during VM execution"""
    
    def __init__(self, seed: int = None):
        import random
        self.rng = random.Random(seed)
        self.mutation_counter = 0
        self.mutated_pcs = set()
    
    def mutate_on_execution(self, code: bytearray, pc: int, opcode: int) -> bytearray:
        """Mutate instruction after execution"""
        from compiler.bytecode import OP_NOP, OP_KORUPSI
        
        if pc in self.mutated_pcs:
            return code
        
        if opcode == OP_KORUPSI:
            if self.mutation_counter >= 1:
                code[pc] = OP_NOP
                self.mutated_pcs.add(pc)
            self.mutation_counter += 1
        
        return code
    
    def mutate_jump_target(self, code: bytearray, pc: int) -> bytearray:
        """Randomly adjust jump targets within safe range"""
        from compiler.bytecode import OP_JUMP, OP_JUMP_IF_FALSE
        
        if pc + 2 >= len(code):
            return code
        
        opcode = code[pc]
        if opcode in [OP_JUMP, OP_JUMP_IF_FALSE]:
            current_target = code[pc + 1] | (code[pc + 2] << 8)
            
            offset = self.rng.randint(-5, 5)
            new_target = max(0, min(len(code) - 1, current_target + offset))
            
            code[pc + 1] = new_target & 0xFF
            code[pc + 2] = (new_target >> 8) & 0xFF
        
        return code


def prepare_self_modifying_bytecode(bytecode_obj, seed: int = None):
    """
    Prepare bytecode with self-modification hooks
    Returns modified bytecode and mutation engine
    """
    engine = SelfModifyEngine(seed)
    
    from compiler.bytecode import OP_KORUPSI, OP_NOP
    
    engine.add_mutation_rule(
        OP_KORUPSI,
        lambda state: state['step_count'] > 5,
        lambda code, pc: _mutate_to_nop(code, pc)
    )
    
    return bytecode_obj.code, engine


def _mutate_to_nop(code: bytearray, pc: int) -> bytearray:
    """Mutation: replace opcode with NOP"""
    from compiler.bytecode import OP_NOP
    code[pc] = OP_NOP
    return code
