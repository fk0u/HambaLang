"""
Obfuscated VM - VM with anti-analysis and self-modification
"""
import sys
import time
import random
from typing import Any, List, Dict
from compiler.bytecode import *
from vm.anti_debug import ExecutionShield
from obfuscator.opcode_map import OpcodeMapper
from obfuscator.self_modify import RuntimeMutator


class ObfuscatedVM:
    """VM with obfuscation, anti-debug, and self-modification"""
    
    def __init__(self, bytecode, seed: int = None, step_limit: int = 100000, 
                 debug: bool = False, paranoia: int = 1, obfuscated: bool = False):
        self.bytecode = bytecode
        self.code = bytearray(bytecode.code)
        self.constants = bytecode.constants
        self.strings = bytecode.strings
        
        self.stack: List[Any] = []
        self.variables: Dict[int, Any] = {}
        self.pc = 0
        self.step_count = 0
        self.step_limit = step_limit
        self.debug = debug
        
        self.anggaran = 100
        self.progress = 0
        self.korupsi_total = 0
        self.timeline = 0
        self.rng = random.Random(seed if seed is not None else None)
        
        self.shield = ExecutionShield(paranoia, seed)
        self.mutator = RuntimeMutator(seed)
        self.opcode_mapper = OpcodeMapper(seed) if obfuscated else None
        self.obfuscated = obfuscated
        
        self.opcode_history = []
        
        self.variables[self._builtin_var_id('anggaran')] = self.anggaran
        self.variables[self._builtin_var_id('progress')] = self.progress
    
    def _builtin_var_id(self, name: str) -> int:
        var_map = self.bytecode.metadata.get('vars', {})
        if name in var_map:
            return var_map[name]
        builtin_map = {'anggaran': 9998, 'progress': 9999}
        return builtin_map.get(name, 0)
    
    def run(self, delay: float = 0.0, ctf_mode: bool = False, hell_mode: bool = False) -> bool:
        """Execute bytecode with obfuscation"""
        try:
            from ctf.hell_mode import HellModeCTF
            hell_ctf = HellModeCTF(self.rng.randint(0, 999999)) if hell_mode else None
            
            while self.pc < len(self.code) and self.step_count < self.step_limit:
                self.step_count += 1
                
                if self.step_count > self.step_limit:
                    raise Exception(f"Execution limit reached: {self.step_limit}")
                
                if not self.shield.should_execute_normally():
                    print("🚨 Abnormal execution environment detected")
                    if self.shield.debugger.paranoia_level >= 2:
                        raise Exception("Execution terminated by security shield")
                    break
                
                original_opcode = self.code[self.pc]
                opcode = self._deobfuscate_opcode(original_opcode)
                
                self.opcode_history.append(opcode)
                
                vm_state = self.get_state()
                vm_state['debug_mode'] = self.debug
                vm_state['opcode_history'] = self.opcode_history
                
                self.shield.on_opcode_execute(opcode, vm_state)
                
                if hell_mode and hell_ctf:
                    hell_ctf.check_progress(vm_state)
                
                if self.debug:
                    self._print_debug(opcode)
                
                if not self._execute_instruction(opcode):
                    break
                
                if self.step_count % 10 == 0:
                    self.code = self.mutator.mutate_on_execution(
                        self.code, self.pc, opcode
                    )
                
                if delay > 0:
                    time.sleep(delay)
            
            if ctf_mode and not hell_mode:
                if self.anggaran == 0 and self.progress >= 100:
                    print("\n🚩 FLAG{H4MB4_VM_M4ST3R_PERFECT_BUDGET}")
                elif self.korupsi_total % 424242 == 0 and self.korupsi_total > 0:
                    print("\n🚩 FLAG{K0RUPSI_NUMBER_TH30RY_42}")
            
            return True
        
        except Exception as e:
            print(f"❌ RUNTIME ERROR: {e}")
            return False
    
    def _deobfuscate_opcode(self, opcode: int) -> int:
        """Deobfuscate opcode if obfuscation enabled"""
        if self.obfuscated and self.opcode_mapper:
            return self.opcode_mapper.deobfuscate(opcode)
        return opcode
    
    def _execute_instruction(self, opcode: int) -> bool:
        """Execute single instruction (same as base VM)"""
        if opcode == OP_NOP:
            self.pc += 1
        
        elif opcode == OP_PUSH:
            operand = self._read_operand()
            if operand & 0x8000:
                str_id = operand & 0x7FFF
                self.stack.append(self.strings[str_id])
            else:
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
                raise Exception("Division by zero")
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
                "💼 Budget optimization berhasil",
                "🎯 Efisiensi anggaran tercapai"
            ]
            print(f"{self.rng.choice(satire)} (-{amount})")
            
            if self.anggaran < 0:
                raise Exception("Dana habis! Proyek diaudit!")
            
            self.pc += 1
        
        elif opcode == OP_MANGKRAK:
            info_str = self.stack.pop()
            print(f"⚠️ PROYEK MANGKRAK: {info_str}")
            raise Exception(f"Proyek mangkrak: {info_str}")
        
        elif opcode == OP_RAPAT:
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
        
        elif opcode == OP_END:
            return False
        
        else:
            raise Exception(f"Unknown opcode: 0x{opcode:02X}")
        
        return True
    
    def _read_operand(self) -> int:
        if self.pc + 2 >= len(self.code):
            return 0
        low = self.code[self.pc + 1]
        high = self.code[self.pc + 2]
        return low | (high << 8)
    
    def _print_debug(self, opcode: int):
        op_name = OPCODE_NAMES.get(opcode, f"UNK({opcode:02X})")
        print(f"[OVM {self.pc:04d}] {op_name:12} | Stack: {len(self.stack)} | Ang: {self.anggaran}")
    
    def get_state(self) -> Dict[str, Any]:
        return {
            'pc': self.pc,
            'stack': self.stack.copy(),
            'anggaran': self.anggaran,
            'progress': self.progress,
            'korupsi_total': self.korupsi_total,
            'timeline': self.timeline,
            'step_count': self.step_count
        }
