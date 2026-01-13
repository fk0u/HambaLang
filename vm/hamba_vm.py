"""
HambaVM - Stack-based Virtual Machine for HambaLang
Executes bytecode with satirical bureaucratic semantics
"""
import sys
import time
import random
from typing import Any, List, Dict
from compiler.bytecode import *


class HambaVM:
    """Stack-based VM with satirical bureaucratic execution"""
    
    def __init__(self, bytecode: Bytecode, seed: int = None, step_limit: int = 100000, debug: bool = False):
        self.bytecode = bytecode
        self.code = bytecode.code
        self.constants = bytecode.constants
        self.strings = bytecode.strings
        
        # VM State
        self.stack: List[Any] = []
        self.variables: Dict[int, Any] = {}
        self.pc = 0  # Program counter
        self.step_count = 0
        self.step_limit = step_limit
        self.debug = debug
        
        # Satirical state
        self.anggaran = 100
        self.progress = 0
        self.korupsi_total = 0
        self.timeline = 0
        self.rng = random.Random(seed if seed is not None else None)
        
        # Initialize built-in variables
        self.variables[self._builtin_var_id('anggaran')] = self.anggaran
        self.variables[self._builtin_var_id('progress')] = self.progress
    
    def _builtin_var_id(self, name: str) -> int:
        """Get variable ID for built-in vars"""
        var_map = self.bytecode.metadata.get('vars', {})
        if name in var_map:
            return var_map[name]
        # Assign high IDs for built-ins
        builtin_map = {'anggaran': 9998, 'progress': 9999}
        return builtin_map.get(name, 0)
    
    def run(self, delay: float = 0.0, ctf_mode: bool = False) -> bool:
        """Execute bytecode"""
        try:
            while self.pc < len(self.code) and self.step_count < self.step_limit:
                self.step_count += 1
                
                if self.step_count > self.step_limit:
                    raise Exception(f"❌ Eksekusi melebihi batas {self.step_limit} langkah (proyek diaudit KPK)")
                
                opcode = self.code[self.pc]
                
                if self.debug:
                    self._print_debug(opcode)
                
                # Execute instruction
                if not self._execute_instruction(opcode):
                    break
                
                if delay > 0:
                    time.sleep(delay)
            
            # CTF FLAG CHECK (hardcore mode)
            if ctf_mode:
                if self.anggaran == 0 and self.progress >= 100:
                    print("\n🚩 FLAG{H4MB4_VM_M4ST3R_PERFECT_BUDGET}")
                elif self.korupsi_total % 424242 == 0 and self.korupsi_total > 0:
                    print("\n🚩 FLAG{K0RUPSI_NUMBER_TH30RY_42}")
            
            return True
        
        except Exception as e:
            print(f"❌ RUNTIME ERROR: {e}")
            return False
    
    def _execute_instruction(self, opcode: int) -> bool:
        """Execute single instruction"""
        if opcode == OP_NOP:
            self.pc += 1
        
        elif opcode == OP_PUSH:
            operand = self._read_operand()
            if operand & 0x8000:  # String
                str_id = operand & 0x7FFF
                self.stack.append(self.strings[str_id])
            else:  # Constant
                self.stack.append(self.constants[operand])
            self.pc += 3
        
        elif opcode == OP_POP:
            self.stack.pop()
            self.pc += 1
        
        elif opcode == OP_LOAD:
            var_id = self._read_operand()
            val = self.variables.get(var_id, 0)
            self.stack.append(val)
            self.pc += 3
        
        elif opcode == OP_STORE:
            var_id = self._read_operand()
            val = self.stack.pop()
            self.variables[var_id] = val
            # Update built-ins
            if var_id == self._builtin_var_id('anggaran'):
                self.anggaran = val
            elif var_id == self._builtin_var_id('progress'):
                self.progress = val
            self.pc += 3
        
        elif opcode == OP_PRINT:
            val = self.stack.pop()
            print(val)
            self.pc += 1
        
        elif opcode == OP_ADD:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a + b)
            self.pc += 1
        
        elif opcode == OP_SUB:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a - b)
            self.pc += 1
        
        elif opcode == OP_MUL:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a * b)
            self.pc += 1
        
        elif opcode == OP_DIV:
            b = self.stack.pop()
            a = self.stack.pop()
            if b == 0:
                raise Exception("Pembagian dengan 0 (kayak bagi anggaran di akhir tahun)")
            self.stack.append(a // b if isinstance(a, int) and isinstance(b, int) else a / b)
            self.pc += 1
        
        elif opcode == OP_LT:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a < b else 0)
            self.pc += 1
        
        elif opcode == OP_GT:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a > b else 0)
            self.pc += 1
        
        elif opcode == OP_EQ:
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a == b else 0)
            self.pc += 1
        
        elif opcode == OP_JUMP:
            addr = self._read_operand()
            self.pc = addr
        
        elif opcode == OP_JUMP_IF_FALSE:
            addr = self._read_operand()
            cond = self.stack.pop()
            if not cond or cond == 0:
                self.pc = addr
            else:
                self.pc += 3
        
        elif opcode == OP_KORUPSI:
            percent = self.stack.pop()
            if not isinstance(percent, (int, float)):
                percent = 0
            
            amount = int(self.anggaran * (percent / 100))
            self.anggaran -= amount
            self.korupsi_total += amount
            self.timeline += self.rng.randint(2, 8)
            
            var_id = self._builtin_var_id('anggaran')
            self.variables[var_id] = self.anggaran
            
            satire = [
                "🤝 Dana dialihkan untuk 'keperluan mendesak'",
                "💼 Budget optimization berhasil (ke rekening pribadi)",
                "🎯 Efisiensi anggaran tercapai",
                "📊 Realisasi anggaran... ke luar negeri"
            ]
            print(f"{self.rng.choice(satire)} (-{amount})")
            
            if self.anggaran < 0:
                raise Exception("💸 Dana habis! Proyek diaudit KPK!")
            
            self.pc += 1
        
        elif opcode == OP_MANGKRAK:
            info_str = self.stack.pop()
            print(f"⚠️ PROYEK MANGKRAK: {info_str}")
            raise Exception(f"Proyek mangkrak: {info_str}")
        
        elif opcode == OP_RAPAT:
            # RAPAT loop implementation
            # Stack top should have remaining iterations
            if len(self.stack) == 0:
                self.pc += 3
            else:
                count = self.stack[-1]
                if count > 1:
                    self.stack[-1] = count - 1
                    loop_addr = self._read_operand()
                    self.pc = loop_addr
                else:
                    self.stack.pop()
                    self.pc += 3
        
        elif opcode == OP_SLEEP:
            duration = self.stack.pop()
            time.sleep(duration / 1000.0)
            self.pc += 1
        
        elif opcode == OP_END:
            return False
        
        else:
            raise Exception(f"Unknown opcode: 0x{opcode:02X} at PC={self.pc}")
        
        return True
    
    def _read_operand(self) -> int:
        """Read 16-bit operand from code"""
        if self.pc + 2 >= len(self.code):
            return 0
        low = self.code[self.pc + 1]
        high = self.code[self.pc + 2]
        return low | (high << 8)
    
    def _print_debug(self, opcode: int):
        """Print debug information"""
        op_name = OPCODE_NAMES.get(opcode, f"UNK({opcode:02X})")
        print(f"[VM {self.pc:04d}] {op_name:12} | Stack: {len(self.stack)} | Anggaran: {self.anggaran} | Progress: {self.progress}")
    
    def step(self) -> bool:
        """Execute single step (for debugger)"""
        if self.pc >= len(self.code):
            return False
        opcode = self.code[self.pc]
        return self._execute_instruction(opcode)
    
    def get_state(self) -> Dict[str, Any]:
        """Get VM state for inspection"""
        return {
            'pc': self.pc,
            'stack': self.stack.copy(),
            'anggaran': self.anggaran,
            'progress': self.progress,
            'korupsi_total': self.korupsi_total,
            'timeline': self.timeline,
            'step_count': self.step_count
        }


def run_bytecode_file(filepath: str, debug: bool = False, seed: int = None, 
                      ctf_mode: bool = False, step_limit: int = 100000, delay: float = 0.0):
    """Load and execute .hbc bytecode file"""
    try:
        bytecode = Bytecode.load(filepath)
        vm = HambaVM(bytecode, seed=seed, step_limit=step_limit, debug=debug)
        
        print(f"🚀 HambaVM v3.0 - Menjalankan {filepath}")
        if ctf_mode:
            print("🎯 CTF MODE: Selesaikan proyek dengan anggaran tepat 0!")
        print("=" * 50)
        
        success = vm.run(delay=delay, ctf_mode=ctf_mode)
        
        print("=" * 50)
        state = vm.get_state()
        print(f"✓ Eksekusi selesai dalam {state['step_count']} langkah")
        print(f"📊 Anggaran akhir: {state['anggaran']}")
        print(f"📈 Progress: {state['progress']}%")
        print(f"💰 Total korupsi: {state['korupsi_total']}")
        
        return success
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python hamba_vm.py <file.hbc> [--debug] [--seed N] [--ctf]")
        sys.exit(1)
    
    filepath = sys.argv[1]
    debug = '--debug' in sys.argv
    ctf_mode = '--ctf' in sys.argv
    seed = None
    
    if '--seed' in sys.argv:
        idx = sys.argv.index('--seed')
        if idx + 1 < len(sys.argv):
            seed = int(sys.argv[idx + 1])
    
    run_bytecode_file(filepath, debug=debug, seed=seed, ctf_mode=ctf_mode)
