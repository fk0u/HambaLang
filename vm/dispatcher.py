"""
Control Flow Flattening Engine
Transforms structured control flow into state machine
"""
from typing import List, Dict, Tuple
from compiler.bytecode import *


class ControlFlowFlattener:
    """Flatten control flow into dispatcher-based state machine"""
    
    def __init__(self, seed: int = None):
        import random
        self.rng = random.Random(seed)
        self.state_counter = 0
        self.state_map = {}
        self.dispatcher_jumps = []
    
    def flatten(self, bytecode: bytes) -> Tuple[bytes, Dict]:
        """
        Transform bytecode with structured control flow
        into flattened state machine
        
        Returns: (flattened_code, state_metadata)
        """
        code = bytearray(bytecode)
        blocks = self._identify_basic_blocks(code)
        states = self._assign_random_states(blocks)
        flattened = self._build_dispatcher(blocks, states)
        
        return flattened, {'states': states, 'dispatcher_offset': 0}
    
    def _identify_basic_blocks(self, code: bytearray) -> List[Tuple[int, int]]:
        """Identify basic blocks (straight-line code segments)"""
        blocks = []
        block_start = 0
        
        i = 0
        while i < len(code):
            opcode = code[i]
            
            if opcode in [OP_JUMP, OP_JUMP_IF_FALSE, OP_END]:
                blocks.append((block_start, i + 3))
                block_start = i + 3
                i += 3
            elif opcode in [OP_PUSH, OP_LOAD, OP_STORE]:
                i += 3
            else:
                i += 1
            
            if i >= len(code):
                if block_start < len(code):
                    blocks.append((block_start, len(code)))
                break
        
        return blocks
    
    def _assign_random_states(self, blocks: List[Tuple[int, int]]) -> Dict[int, int]:
        """Assign randomized state numbers to blocks"""
        state_numbers = list(range(len(blocks)))
        self.rng.shuffle(state_numbers)
        
        state_map = {}
        for i, (start, end) in enumerate(blocks):
            state_map[start] = state_numbers[i]
        
        return state_map
    
    def _build_dispatcher(self, blocks: List[Tuple[int, int]], states: Dict[int, int]) -> bytes:
        """Build dispatcher loop with state machine"""
        result = bytearray()
        
        dispatcher_start = 0
        result.extend(self._generate_dispatcher_header())
        
        for block_idx, (start, end) in enumerate(blocks):
            state_num = states[start]
            result.extend(self._generate_state_case(state_num, block_idx))
        
        result.extend(self._generate_dispatcher_footer())
        
        return bytes(result)
    
    def _generate_dispatcher_header(self) -> bytes:
        """Generate dispatcher loop header"""
        header = bytearray()
        
        header.append(OP_PUSH)
        header.append(0x00)
        header.append(0x00)
        
        return bytes(header)
    
    def _generate_state_case(self, state_num: int, block_idx: int) -> bytes:
        """Generate code for one state case"""
        case = bytearray()
        
        case.append(OP_PUSH)
        case.append(state_num & 0xFF)
        case.append((state_num >> 8) & 0xFF)
        
        return bytes(case)
    
    def _generate_dispatcher_footer(self) -> bytes:
        """Generate dispatcher loop footer"""
        footer = bytearray()
        
        footer.append(OP_END)
        
        return bytes(footer)


class StateObfuscator:
    """Obfuscate state transitions in flattened control flow"""
    
    def __init__(self, seed: int = None):
        import random
        self.rng = random.Random(seed)
    
    def obfuscate_state_number(self, state: int) -> int:
        """Apply mathematical obfuscation to state number"""
        key = self.rng.randint(100, 999)
        obfuscated = (state ^ key) + (state * 17)
        return obfuscated & 0xFFFF
    
    def generate_state_transition_code(self, from_state: int, to_state: int) -> bytes:
        """Generate obfuscated state transition"""
        code = bytearray()
        
        obf_to = self.obfuscate_state_number(to_state)
        
        code.append(OP_PUSH)
        code.append(obf_to & 0xFF)
        code.append((obf_to >> 8) & 0xFF)
        
        code.append(OP_STORE)
        code.append(0xFE)
        code.append(0x00)
        
        return bytes(code)


class DispatcherVM:
    """VM extension for executing flattened control flow"""
    
    def __init__(self, state_metadata: Dict):
        self.state_metadata = state_metadata
        self.current_state = 0
        self.state_history = []
    
    def execute_dispatcher(self, bytecode: bytes, base_vm):
        """Execute flattened bytecode using dispatcher"""
        self.current_state = 0
        
        while self.current_state != -1:
            self._execute_state_block(bytecode, base_vm)
            self.state_history.append(self.current_state)
            
            if len(self.state_history) > 1000:
                raise Exception("Dispatcher loop limit exceeded")
    
    def _execute_state_block(self, bytecode: bytes, base_vm):
        """Execute one state block"""
        pass


def apply_control_flow_flattening(bytecode_obj, seed: int = None):
    """
    Apply control flow flattening to bytecode
    
    Returns: (flattened_bytecode, metadata)
    """
    flattener = ControlFlowFlattener(seed)
    flattened, metadata = flattener.flatten(bytecode_obj.code)
    
    bytecode_obj.code = flattened
    bytecode_obj.metadata['flattened'] = True
    bytecode_obj.metadata['flatten_data'] = metadata
    
    return bytecode_obj
