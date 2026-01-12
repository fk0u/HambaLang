#!/usr/bin/env python3
"""
HambaLang Interpreter v2.0
Full-Featured Programming Language - Satir Proyek Hambalang

Features:
- Variables & Data Types (string, number, boolean, array, object)
- Functions & Closures
- Control Flow (if/else, loops)
- Database Support (SQLite, MySQL, PostgreSQL)
- File I/O (read, write, JSON, CSV)
- HTTP/API Client
- Error Handling
"""

import sys
import time
import random
import re
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable


class HambaRuntime:
    def __init__(self):
        # Built-in state
        self.anggaran = 1_000_000_000
        self.status_proyek = "Direncanakan"
        self.progress = 0
        
        # User variables
        self.variables = {}
        
        # Functions
        self.functions = {}
        
        # Output
        self.output = []
        self.terminated = False
        
        # Database connections
        self.db_connections = {}
        
        # HTTP session
        self.http_session = None
    
    def log(self, message):
        self.output.append(str(message))
        print(message)
    
    def get_output(self):
        return "\n".join(self.output)
    
    def set_variable(self, name: str, value: Any):
        """Set a variable in the runtime"""
        self.variables[name] = value
    
    def get_variable(self, name: str) -> Any:
        """Get a variable from the runtime"""
        # Check built-in variables first
        if name == 'anggaran':
            return self.anggaran
        elif name == 'status_proyek':
            return self.status_proyek
        elif name == 'progress':
            return self.progress
        
        # Check user variables
        if name in self.variables:
            return self.variables[name]
        
        raise Exception(f"Variable tidak ditemukan: {name}")
    
    def define_function(self, name: str, params: List[str], body: List[str]):
        """Define a function"""
        self.functions[name] = {
            'params': params,
            'body': body
        }
    
    def call_function(self, name: str, args: List[Any]) -> Any:
        """Call a user-defined function"""
        if name not in self.functions:
            raise Exception(f"Function tidak ditemukan: {name}")
        
        func = self.functions[name]
        
        if len(args) != len(func['params']):
            raise Exception(f"Function {name} membutuhkan {len(func['params'])} parameter, diberikan {len(args)}")
        
        # Save current variables
        saved_vars = self.variables.copy()
        
        # Set parameters as local variables
        for param, arg in zip(func['params'], args):
            self.variables[param] = arg
        
        # Execute function body
        return_value = None
        for line in func['body']:
            if line.strip().startswith('kembalikan '):
                return_value = self._eval_expression(line.strip()[11:])
                break
        
        # Restore variables
        self.variables = saved_vars
        
        return return_value
    
    def _eval_expression(self, expr: str) -> Any:
        """Evaluate expression (placeholder, will be implemented in interpreter)"""
        pass


class HambaInterpreter:
    def __init__(self, runtime=None):
        self.runtime = runtime or HambaRuntime()
        self.in_rapat_infinite = False
    
    def execute(self, code):
        """Execute HambaLang code"""
        lines = code.strip().split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if self.runtime.terminated:
                break
            
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('//'):
                continue
            
            try:
                self._execute_line(line)
            except Exception as e:
                error_msg = f"Error Birokrasi pada baris {line_num}: {str(e)}"
                self.runtime.log(error_msg)
                raise Exception(error_msg)
    
    def _execute_line(self, line):
        """Execute a single line of HambaLang code"""
        
        # lapor (print)
        if line.startswith('lapor '):
            content = line[6:].strip()
            message = self._eval_expression(content)
            self.runtime.log(message)
            return
        
        # print
        if line.startswith('print '):
            content = line[6:].strip()
            message = self._eval_expression(content)
            self.runtime.log(message)
            return
        
        # Mangkrak(ms)
        match = re.match(r'Mangkrak\((\d+)\)', line)
        if match:
            ms = int(match.group(1))
            self._mangkrak(ms)
            return
        
        # Korupsi(percent)
        match = re.match(r'Korupsi\((\d+)\)', line)
        if match:
            percent = int(match.group(1))
            self._korupsi(percent)
            return
        
        # RapatInfinite()
        if line == 'RapatInfinite()':
            self._rapat_infinite()
            return
        
        # selesai()
        if line == 'selesai()':
            self._selesai()
            return
        
        # jika ... maka ...
        if line.startswith('jika '):
            self._execute_conditional(line)
            return
        
        # Variable assignment
        if '=' in line and not any(op in line for op in ['>', '<', '==']):
            self._assign_variable(line)
            return
        
        raise Exception(f"Syntax tidak dikenali: {line}")
    
    def _eval_expression(self, expr):
        """Evaluate expression (string or variable)"""
        expr = expr.strip()
        
        # String literal
        if (expr.startswith('"') and expr.endswith('"')) or \
           (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        
        # Variable reference
        if expr == 'anggaran':
            return f"Rp {self.runtime.anggaran:,.0f}"
        
        if expr == 'status_proyek':
            return self.runtime.status_proyek
        
        if expr == 'progress':
            return f"{self.runtime.progress}%"
        
        # Try to evaluate as Python expression
        try:
            return str(eval(expr))
        except:
            return expr
    
    def _mangkrak(self, ms):
        """Mangkrak: Delay dengan kemungkinan event random"""
        seconds = ms / 1000
        self.runtime.log(f"⏳ Proyek mangkrak selama {seconds} detik...")
        
        time.sleep(min(seconds, 2))  # Cap at 2 seconds for demo
        
        # Random catastrophic events
        events = [
            "💸 Dana habis untuk operasional!",
            "🏃 Vendor kabur dengan uang muka!",
            "🌧️ Longsor menghancurkan pondasi!",
            "🚨 Audit mendadak dari KPK!",
            "📄 Dokumen perizinan bermasalah!",
            "👷 Pekerja mogok kerja!",
        ]
        
        if random.random() < 0.3:  # 30% chance
            event = random.choice(events)
            self.runtime.log(f"🚧 EVENT: {event}")
            self.runtime.anggaran -= random.randint(10_000_000, 100_000_000)
            if self.runtime.anggaran < 0:
                self.runtime.anggaran = 0
    
    def _korupsi(self, percent):
        """Korupsi: Menghilangkan anggaran secara acak"""
        if percent < 0 or percent > 100:
            raise Exception("Persentase korupsi harus 0-100")
        
        # Random amount within the percentage
        actual_percent = random.uniform(percent * 0.8, percent * 1.2)
        amount = self.runtime.anggaran * (actual_percent / 100)
        self.runtime.anggaran -= amount
        
        if self.runtime.anggaran < 0:
            self.runtime.anggaran = 0
        
        self.runtime.log(f"💰 Korupsi {actual_percent:.1f}%: Rp {amount:,.0f} menguap!")
        self.runtime.log(f"📊 Sisa anggaran: Rp {self.runtime.anggaran:,.0f}")
    
    def _rapat_infinite(self):
        """RapatInfinite: Loop rapat tanpa akhir"""
        self.runtime.log("🔄 Memulai RapatInfinite()...")
        self.runtime.log("⚠️ Program terjebak dalam rapat berkepanjangan!")
        
        # Simulate a few iterations then stop to prevent actual infinite loop
        for i in range(5):
            self.runtime.log(f"📋 Rapat sesi ke-{i+1}: Belum ada keputusan...")
            time.sleep(0.5)
        
        self.runtime.log("⏸️ (RapatInfinite dihentikan paksa untuk demo)")
    
    def _selesai(self):
        """selesai: Mengakhiri program secara administratif"""
        self.runtime.status_proyek = "Selesai (di atas kertas)"
        self.runtime.progress = 100
        
        # Fake progress bar
        bar = "█" * 9 + "░"
        self.runtime.log(f"\n✅ PROYEK SELESAI!")
        self.runtime.log(f"Progress: 100% [{bar}]")
        self.runtime.log(f"Status: {self.runtime.status_proyek}")
        self.runtime.log(f"Sisa Anggaran: Rp {self.runtime.anggaran:,.0f}")
        self.runtime.log(f"(Kondisi fisik: Data tidak tersedia)")
        
        self.runtime.terminated = True
    
    def _execute_conditional(self, line):
        """Execute jika ... maka ... statement"""
        # Parse: jika <condition> maka <action>
        match = re.match(r'jika\s+(.+?)\s+maka\s+(.+)', line)
        if not match:
            raise Exception("Format: jika <kondisi> maka <aksi>")
        
        condition = match.group(1).strip()
        action = match.group(2).strip()
        
        # Evaluate condition
        # Replace 'anggaran' with actual value
        condition_eval = condition.replace('anggaran', str(self.runtime.anggaran))
        
        try:
            result = eval(condition_eval)
        except:
            raise Exception(f"Kondisi tidak valid: {condition}")
        
        if result:
            self._execute_line(action)
    
    def _assign_variable(self, line):
        """Handle variable assignment"""
        parts = line.split('=', 1)
        if len(parts) != 2:
            raise Exception(f"Assignment tidak valid: {line}")
        
        var_name = parts[0].strip()
        value = parts[1].strip()
        
        # Only support built-in variables
        if var_name == 'anggaran':
            try:
                self.runtime.anggaran = float(eval(value))
            except:
                raise Exception(f"Nilai anggaran tidak valid: {value}")
        elif var_name == 'status_proyek':
            self.runtime.status_proyek = self._eval_expression(value)
        elif var_name == 'progress':
            try:
                self.runtime.progress = int(eval(value))
            except:
                raise Exception(f"Nilai progress tidak valid: {value}")
        else:
            raise Exception(f"Variable tidak dikenal: {var_name}")


def run_file(filepath):
    """Run a HambaLang file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        print(f"🏗️  Menjalankan: {filepath}\n")
        print("=" * 50)
        
        interpreter = HambaInterpreter()
        interpreter.execute(code)
        
        print("=" * 50)
        print("\n✅ Eksekusi selesai\n")
        
    except FileNotFoundError:
        print(f"❌ File tidak ditemukan: {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python hamba.py <file.hl>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not filepath.endswith('.hl'):
        print("❌ File harus berekstensi .hl")
        sys.exit(1)
    
    run_file(filepath)


if __name__ == '__main__':
    main()
