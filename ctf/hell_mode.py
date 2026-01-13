"""
Hell Mode CTF Challenge Engine
Multi-stage flags with complex unlock conditions
"""
import hashlib
from typing import List, Dict, Optional


class FlagStage:
    """Single stage of multi-stage flag"""
    
    def __init__(self, stage_id: int, partial_flag: str, condition: callable):
        self.stage_id = stage_id
        self.partial_flag = partial_flag
        self.condition = condition
        self.unlocked = False
    
    def check_unlock(self, vm_state: dict) -> bool:
        """Check if this stage should unlock"""
        if self.unlocked:
            return False
        
        if self.condition(vm_state):
            self.unlocked = True
            return True
        
        return False


class MultiStageFlagManager:
    """Manages multi-stage flag distribution"""
    
    def __init__(self, seed: int = None):
        self.stages: List[FlagStage] = []
        self.seed = seed
        self.honeytrap_triggered = False
    
    def add_stage(self, stage_id: int, partial_flag: str, condition: callable):
        """Add a flag stage with unlock condition"""
        stage = FlagStage(stage_id, partial_flag, condition)
        self.stages.append(stage)
    
    def check_stages(self, vm_state: dict) -> List[str]:
        """Check all stages and return unlocked partials"""
        unlocked = []
        
        for stage in self.stages:
            if stage.check_unlock(vm_state):
                unlocked.append(stage.partial_flag)
        
        return unlocked
    
    def get_complete_flag(self) -> Optional[str]:
        """Return complete flag if all stages unlocked"""
        if all(stage.unlocked for stage in self.stages):
            parts = [s.partial_flag for s in sorted(self.stages, key=lambda x: x.stage_id)]
            return ''.join(parts)
        
        return None
    
    def is_complete(self) -> bool:
        """Check if all stages unlocked"""
        return all(stage.unlocked for stage in self.stages)


class HoneytrapDetector:
    """Detect and punish incorrect solutions"""
    
    def __init__(self):
        self.triggers = []
        self.punishments = []
    
    def add_trap(self, condition: callable, punishment: callable):
        """Add honeytrap condition and punishment"""
        self.triggers.append((condition, punishment))
    
    def check_traps(self, vm_state: dict):
        """Check if any trap triggered"""
        for condition, punishment in self.triggers:
            if condition(vm_state):
                punishment(vm_state)


class HellModeCTF:
    """Hell mode CTF challenge orchestrator"""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.flag_manager = MultiStageFlagManager(seed)
        self.honeytrap = HoneytrapDetector()
        self.execution_trace = []
        self._setup_stages()
        self._setup_traps()
    
    def _setup_stages(self):
        """Setup multi-stage flag unlock conditions"""
        
        # Stage 1: Perfect budget within first 50 steps
        self.flag_manager.add_stage(
            1,
            "FLAG{H3LL_",
            lambda state: (
                state.get('anggaran', 100) == 0 and
                state.get('step_count', 0) < 50 and
                state.get('progress', 0) >= 100
            )
        )
        
        # Stage 2: Korupsi total is prime number
        self.flag_manager.add_stage(
            2,
            "M0D3_",
            lambda state: self._is_prime(state.get('korupsi_total', 0))
        )
        
        # Stage 3: Exact opcode sequence executed
        self.flag_manager.add_stage(
            3,
            "CTF_",
            lambda state: self._check_opcode_sequence(state)
        )
        
        # Stage 4: No debug mode used
        self.flag_manager.add_stage(
            4,
            "M4ST3R}",
            lambda state: not state.get('debug_mode', False)
        )
    
    def _setup_traps(self):
        """Setup honeytraps for incorrect solutions"""
        
        # Trap 1: Debug mode triggers fake flag
        self.honeytrap.add_trap(
            lambda state: state.get('debug_mode', False),
            lambda state: print("FLAG{D3BUG_M0D3_US3R_F4K3}")
        )
        
        # Trap 2: Too many steps
        self.honeytrap.add_trap(
            lambda state: state.get('step_count', 0) > 200,
            lambda state: print("FLAG{T00_SL0W_TRY_4G41N}")
        )
        
        # Trap 3: Wrong korupsi pattern
        self.honeytrap.add_trap(
            lambda state: state.get('korupsi_total', 0) % 100 == 0,
            lambda state: print("FLAG{N1C3_GUESS_BUT_N0}")
        )
    
    def check_progress(self, vm_state: dict):
        """Check challenge progress and unlock stages"""
        self.execution_trace.append(vm_state.copy())
        
        self.honeytrap.check_traps(vm_state)
        
        unlocked = self.flag_manager.check_stages(vm_state)
        for partial in unlocked:
            print(f"🔓 Stage unlocked: {partial}")
        
        if self.flag_manager.is_complete():
            complete_flag = self.flag_manager.get_complete_flag()
            print(f"\n🏆 COMPLETE FLAG: {complete_flag}")
            print("🎉 Hell Mode CTF SOLVED!")
    
    def _is_prime(self, n: int) -> bool:
        """Check if number is prime"""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        
        return True
    
    def _check_opcode_sequence(self, state: dict) -> bool:
        """Check if specific opcode sequence was executed"""
        required_sequence = [0x60, 0x10, 0x60, 0x10]
        
        if 'opcode_history' not in state:
            return False
        
        history = state['opcode_history']
        if len(history) < len(required_sequence):
            return False
        
        for i in range(len(history) - len(required_sequence) + 1):
            if history[i:i+len(required_sequence)] == required_sequence:
                return True
        
        return False
    
    def get_hint(self, stage_id: int) -> str:
        """Get encrypted hint for stage"""
        hints = {
            1: "H1nt: P3rf3ct budg3t + sp33d = st4g3 1",
            2: "H1nt: Pr1m3 numb3rs 4r3 sp3c14l",
            3: "H1nt: Opc0d3 p4tt3rn: K0RUPSI PRINT K0RUPSI PRINT",
            4: "H1nt: N0 d3bugg1ng 4ll0w3d"
        }
        
        hint = hints.get(stage_id, "No hint available")
        return self._obfuscate_text(hint)
    
    def _obfuscate_text(self, text: str) -> str:
        """Simple ROT13-like obfuscation"""
        result = []
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                result.append(chr((ord(char) - base + 13) % 26 + base))
            else:
                result.append(char)
        return ''.join(result)


def create_hell_challenge_bytecode():
    """Create bytecode for hell mode challenge"""
    from compiler.bytecode import BytecodeCompiler, Bytecode
    from interpreter.hamba_advanced import Parser
    
    source = '''
lapor "🔥 HELL MODE CTF CHALLENGE 🔥"
mulai
    set progress = 0
    set target = 100
    
    Korupsi(11)
    lapor progress
    set progress = progress + 25
    
    Korupsi(13)
    lapor progress
    set progress = progress + 25
    
    Korupsi(17)
    set progress = progress + 25
    
    Korupsi(19)
    set progress = progress + 25
    
    jika progress >= target
        lapor "Challenge complete!"
    akhir
akhir
'''
    
    lines = source.strip().split('\n')
    parser = Parser(lines)
    ast = parser.parse()
    
    compiler = BytecodeCompiler()
    bytecode = compiler.compile(ast)
    
    return bytecode
