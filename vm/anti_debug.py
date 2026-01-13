"""
Anti-Debug & Anti-Analysis Mechanisms
Detects debugging, analysis, and tampering
"""
import time
import sys
from typing import Optional


class AntiDebugger:
    """Detects and counters debugging attempts"""
    
    def __init__(self, paranoia_level: int = 1):
        self.paranoia_level = paranoia_level
        self.step_timestamps = []
        self.execution_start = time.time()
        self.suspicious_activity = 0
        self.debug_detected = False
    
    def check_debugger_attached(self) -> bool:
        """Detect if debugger is attached"""
        try:
            import ctypes
            if sys.platform == 'win32':
                is_debugged = ctypes.windll.kernel32.IsDebuggerPresent()
                if is_debugged:
                    self.debug_detected = True
                    return True
        except:
            pass
        
        return False
    
    def check_step_timing(self) -> bool:
        """Detect single-step debugging by timing"""
        current_time = time.time()
        self.step_timestamps.append(current_time)
        
        if len(self.step_timestamps) > 10:
            recent = self.step_timestamps[-10:]
            intervals = [recent[i+1] - recent[i] for i in range(len(recent)-1)]
            
            avg_interval = sum(intervals) / len(intervals)
            
            if avg_interval > 0.5:
                self.suspicious_activity += 1
                if self.suspicious_activity > 5:
                    self.debug_detected = True
                    return True
        
        return False
    
    def check_execution_time(self) -> bool:
        """Detect abnormal execution time"""
        elapsed = time.time() - self.execution_start
        
        if elapsed > 300:
            self.debug_detected = True
            return True
        
        return False
    
    def insert_timing_bomb(self, expected_duration: float) -> bool:
        """Return True if execution took too long"""
        elapsed = time.time() - self.execution_start
        if elapsed > expected_duration * 2:
            return True
        return False
    
    def anti_debug_trap(self):
        """Execute anti-debug countermeasure"""
        if self.debug_detected:
            if self.paranoia_level >= 2:
                raise Exception("Debugger detected. VM terminated.")
            elif self.paranoia_level >= 1:
                print("⚠️ Anomaly detected in execution environment")


class DecoyGenerator:
    """Generates fake flags and misleading output"""
    
    def __init__(self, seed: int = None):
        import random
        self.rng = random.Random(seed)
        self.decoys = [
            "FLAG{F4K3_FL4G_N1C3_TRY}",
            "FLAG{TH1S_1S_N0T_TH3_FL4G}",
            "FLAG{Y0U_4R3_CL0S3_BUT_N0}",
            "FLAG{DEB00G_M0D3_CH3AT3R}",
            "FLAG{DECRYPT_ME_IF_U_CAN}"
        ]
    
    def get_decoy_flag(self) -> str:
        """Return fake flag"""
        return self.rng.choice(self.decoys)
    
    def should_show_decoy(self, vm_state: dict) -> bool:
        """Determine if decoy should be shown"""
        if vm_state.get('debug_mode', False):
            return True
        
        if vm_state.get('step_count', 0) < 100:
            return self.rng.random() < 0.3
        
        return False


class AntiAnalysis:
    """Prevents static and dynamic analysis"""
    
    def __init__(self):
        self.analysis_detected = False
        self.call_frequency = {}
    
    def check_analysis_patterns(self, opcode: int) -> bool:
        """Detect analysis by checking opcode execution patterns"""
        if opcode not in self.call_frequency:
            self.call_frequency[opcode] = 0
        
        self.call_frequency[opcode] += 1
        
        if self.call_frequency[opcode] > 1000:
            self.analysis_detected = True
            return True
        
        return False
    
    def obfuscate_error_messages(self, error: str) -> str:
        """Return misleading error messages"""
        obfuscated = [
            "Segmentation fault (core dumped)",
            "Access violation at 0x0000000",
            "Stack overflow detected",
            "Memory corruption in heap",
            "Invalid opcode at offset 0x42"
        ]
        
        import random
        return random.choice(obfuscated)
    
    def inject_fake_constants(self) -> list:
        """Return fake constants to mislead analysis"""
        return [
            0xDEADBEEF,
            0xCAFEBABE,
            0x13371337,
            0x42424242
        ]


class IntegrityChecker:
    """Verify bytecode hasn't been tampered with"""
    
    def __init__(self, original_hash: Optional[int] = None):
        self.original_hash = original_hash
    
    def compute_hash(self, bytecode: bytes) -> int:
        """Compute simple hash of bytecode"""
        h = 5381
        for b in bytecode:
            h = ((h << 5) + h) + b
            h &= 0xFFFFFFFF
        return h
    
    def verify(self, bytecode: bytes) -> bool:
        """Check if bytecode has been modified"""
        if self.original_hash is None:
            return True
        
        current_hash = self.compute_hash(bytecode)
        return current_hash == self.original_hash
    
    def tamper_detected_action(self):
        """Execute when tampering detected"""
        raise Exception("Bytecode integrity check failed")


class ExecutionShield:
    """Combined anti-debugging and anti-analysis shield"""
    
    def __init__(self, paranoia_level: int = 1, seed: int = None):
        self.debugger = AntiDebugger(paranoia_level)
        self.decoy = DecoyGenerator(seed)
        self.analyzer = AntiAnalysis()
        self.paranoia_level = paranoia_level
    
    def check_environment(self) -> bool:
        """Perform all environment checks"""
        checks = [
            self.debugger.check_debugger_attached(),
            self.debugger.check_step_timing(),
            self.debugger.check_execution_time()
        ]
        
        return any(checks)
    
    def on_opcode_execute(self, opcode: int, vm_state: dict):
        """Hook called on each opcode execution"""
        if self.paranoia_level >= 2:
            if self.analyzer.check_analysis_patterns(opcode):
                self.debugger.anti_debug_trap()
        
        if self.paranoia_level >= 1:
            if self.decoy.should_show_decoy(vm_state):
                if vm_state.get('debug_mode'):
                    print(f"[DECOY] {self.decoy.get_decoy_flag()}")
    
    def should_execute_normally(self) -> bool:
        """Determine if VM should execute normally or enter trap mode"""
        return not (self.debugger.debug_detected or self.analyzer.analysis_detected)
