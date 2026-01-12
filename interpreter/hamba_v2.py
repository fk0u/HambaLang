#!/usr/bin/env python3
"""
HambaLang Interpreter v2.0 - COMPLETE EDITION
Full-Featured Programming Language - Satir Proyek Hambalang

Features:
- Variables & Data Types (string, number, boolean, list, dict)
- Functions & Parameters
- Control Flow (if/elif/else, while, for)
- Database Support (SQLite, MySQL, PostgreSQL)
- File I/O (read, write, JSON, CSV)
- HTTP/API Client
- Mathematical Operations
- String Operations
- Array/List Operations
- Error Handling
"""

import sys
import time
import random
import re
import json
import os
import sqlite3
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

# Optional imports for extended features
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import mysql.connector
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False

try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False


class HambaRuntime:
    def __init__(self):
        # Built-in state (satire variables)
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
        
        # Loop control
        self.break_loop = False
        self.continue_loop = False
        
        # Database connections
        self.db_connections = {}
        
        # Function return value
        self.return_value = None
        self.has_return = False
    
    def log(self, message):
        self.output.append(str(message))
        print(message)
    
    def get_output(self):
        return "\n".join(self.output)
    
    def set_variable(self, name: str, value: Any):
        # Update built-in variables
        if name == 'anggaran':
            self.anggaran = self._to_number(value)
        elif name == 'status_proyek':
            self.status_proyek = str(value)
        elif name == 'progress':
            self.progress = self._to_number(value)
        else:
            self.variables[name] = value
    
    def get_variable(self, name: str) -> Any:
        # Check built-in variables
        if name == 'anggaran':
            return self.anggaran
        elif name == 'status_proyek':
            return self.status_proyek
        elif name == 'progress':
            return self.progress
        elif name in self.variables:
            return self.variables[name]
        else:
            raise Exception(f"Variable '{name}' tidak ditemukan")
    
    def _to_number(self, value: Any) -> float:
        try:
            return float(value)
        except:
            return 0.0


class HambaInterpreter:
    def __init__(self, runtime=None):
        self.runtime = runtime or HambaRuntime()
    
    def execute(self, code: str):
        """Execute HambaLang code"""
        lines = code.split('\n')
        self._execute_block(lines, 0, len(lines))
    
    def _execute_block(self, lines: List[str], start: int, end: int) -> int:
        """Execute a block of code and return next line index"""
        i = start
        while i < end and not self.runtime.terminated:
            if self.runtime.break_loop or self.runtime.continue_loop or self.runtime.has_return:
                break
            
            line = lines[i].strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('//'):
                i += 1
                continue
            
            # Check for block statements
            if line.startswith('fungsi '):
                i = self._parse_function(lines, i)
            elif line.startswith('jika '):
                i = self._parse_if(lines, i)
            elif line.startswith('selama '):
                i = self._parse_while(lines, i)
            elif line.startswith('untuk '):
                i = self._parse_for(lines, i)
            else:
                try:
                    self._execute_line(line)
                except Exception as e:
                    raise Exception(f"Error pada baris {i+1}: {str(e)}")
                i += 1
        
        return i
    
    def _execute_line(self, line: str):
        """Execute a single line of code"""
        
        # Return statement
        if line.startswith('kembalikan '):
            expr = line[11:].strip()
            self.runtime.return_value = self._eval_expression(expr)
            self.runtime.has_return = True
            return
        
        # Break
        if line == 'hentikan':
            self.runtime.break_loop = True
            return
        
        # Continue
        if line == 'lanjut':
            self.runtime.continue_loop = True
            return
        
        # lapor / print
        if line.startswith('lapor ') or line.startswith('print '):
            content = line.split(' ', 1)[1].strip()
            message = self._eval_expression(content)
            self.runtime.log(self._to_string(message))
            return
        
        # Mangkrak(ms)
        match = re.match(r'Mangkrak\((.+?)\)', line)
        if match:
            ms = self._eval_expression(match.group(1))
            self._mangkrak(self._to_number(ms))
            return
        
        # Korupsi(percent)
        match = re.match(r'Korupsi\((.+?)\)', line)
        if match:
            percent = self._eval_expression(match.group(1))
            self._korupsi(self._to_number(percent))
            return
        
        # RapatInfinite()
        if line == 'RapatInfinite()':
            self._rapat_infinite()
            return
        
        # selesai() or selesai
        if line == 'selesai()' or line == 'selesai':
            self._selesai()
            return
        
        # File operations
        if line.startswith('tulisFile(') or line.startswith('bacaFile('):
            self._handle_file_operation(line)
            return
        
        # Database operations
        if line.startswith('sambungDB(') or line.startswith('queryDB(') or line.startswith('tutupDB('):
            self._handle_db_operation(line)
            return
        
        # HTTP operations
        if line.startswith('httpGet(') or line.startswith('httpPost('):
            self._handle_http_operation(line)
            return
        
        # Function call (user-defined or built-in)
        func_name_match = re.match(r'^(\w+)\s*\(', line)
        if func_name_match:
            func_name = func_name_match.group(1)
            # User-defined functions
            if func_name in self.runtime.functions:
                args_str = self._extract_function_args(line, line.index('(') + 1)
                args = self._parse_arguments(args_str) if args_str.strip() else []
                self._call_function(func_name, args)
                return
            # Built-in functions (just evaluate as expression, may have side effects)
            elif func_name in ['tambahArray', 'hapusArray', 'panjang', 'tipe', 'angka', 'teks']:
                self._eval_expression(line)
                return
        
        # Variable assignment
        if '=' in line and not any(op in line for op in ['==', '!=', '<=', '>=', '<', '>']):
            self._assign_variable(line)
            return
        
        raise Exception(f"Syntax tidak dikenali: {line}")
    
    def _parse_function(self, lines: List[str], start: int) -> int:
        """Parse function definition"""
        line = lines[start].strip()
        
        # fungsi namaFungsi(param1, param2)
        match = re.match(r'fungsi\s+(\w+)\s*\(([^)]*)\)', line)
        if not match:
            raise Exception("Format fungsi salah. Gunakan: fungsi nama(param1, param2)")
        
        func_name = match.group(1)
        params_str = match.group(2).strip()
        params = [p.strip() for p in params_str.split(',')] if params_str else []
        
        # Find function body (until 'akhir')
        body_start = start + 1
        body_end = body_start
        indent_level = 0
        
        for i in range(body_start, len(lines)):
            line = lines[i].strip()
            if line == 'akhir':
                if indent_level == 0:
                    body_end = i
                    break
                else:
                    indent_level -= 1
            elif line.startswith('fungsi ') or line.startswith('jika ') or line.startswith('selama '):
                indent_level += 1
        
        if body_end == body_start:
            raise Exception(f"Function {func_name} tidak memiliki 'akhir'")
        
        # Store function
        self.runtime.functions[func_name] = {
            'params': params,
            'body': lines[body_start:body_end]
        }
        
        return body_end + 1
    
    def _parse_if(self, lines: List[str], start: int) -> int:
        """Parse if/elif/else statement"""
        i = start
        executed = False
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('jika '):
                # jika condition
                condition = line[5:].strip()
                result = self._eval_expression(condition)
                
                # Find block end
                block_end = self._find_block_end(lines, i + 1, ['ataujika', 'atau', 'akhir'])
                
                if self._to_boolean(result) and not executed:
                    self._execute_block(lines, i + 1, block_end)
                    executed = True
                
                i = block_end
                
            elif line.startswith('ataujika '):
                # elif condition
                condition = line[8:].strip()
                result = self._eval_expression(condition)
                
                block_end = self._find_block_end(lines, i + 1, ['ataujika', 'atau', 'akhir'])
                
                if self._to_boolean(result) and not executed:
                    self._execute_block(lines, i + 1, block_end)
                    executed = True
                
                i = block_end
                
            elif line == 'atau':
                # else
                block_end = self._find_block_end(lines, i + 1, ['akhir'])
                
                if not executed:
                    self._execute_block(lines, i + 1, block_end)
                
                i = block_end
                
            elif line == 'akhir':
                return i + 1
            else:
                i += 1
        
        return i
    
    def _parse_while(self, lines: List[str], start: int) -> int:
        """Parse while loop"""
        line = lines[start].strip()
        condition = line[7:].strip()
        
        # Find loop body
        body_start = start + 1
        body_end = self._find_block_end(lines, body_start, ['akhir'])
        
        # Execute loop
        max_iterations = 10000  # Safety limit
        iterations = 0
        
        while self._to_boolean(self._eval_expression(condition)) and iterations < max_iterations:
            self.runtime.break_loop = False
            self.runtime.continue_loop = False
            
            self._execute_block(lines, body_start, body_end)
            
            if self.runtime.break_loop:
                self.runtime.break_loop = False
                break
            
            iterations += 1
        
        if iterations >= max_iterations:
            self.runtime.log("⚠️ Loop dihentikan: Mencapai batas maksimum iterasi")
        
        return body_end + 1
    
    def _parse_for(self, lines: List[str], start: int) -> int:
        """Parse for loop"""
        line = lines[start].strip()
        
        # untuk i dalam [1, 2, 3]
        # untuk i dari 1 sampai 10
        
        if ' dalam ' in line:
            parts = line.split(' dalam ', 1)
            var_name = parts[0].replace('untuk', '').strip()
            array_expr = parts[1].strip()
            
            array = self._eval_expression(array_expr)
            if not isinstance(array, list):
                raise Exception("'dalam' membutuhkan array/list")
            
            body_start = start + 1
            body_end = self._find_block_end(lines, body_start, ['akhir'])
            
            for item in array:
                self.runtime.set_variable(var_name, item)
                self.runtime.break_loop = False
                self.runtime.continue_loop = False
                
                self._execute_block(lines, body_start, body_end)
                
                if self.runtime.break_loop:
                    self.runtime.break_loop = False
                    break
            
            return body_end + 1
            
        elif ' dari ' in line and ' sampai ' in line:
            match = re.match(r'untuk\s+(\w+)\s+dari\s+(.+?)\s+sampai\s+(.+)', line)
            if not match:
                raise Exception("Format loop salah")
            
            var_name = match.group(1)
            start_val = self._to_number(self._eval_expression(match.group(2)))
            end_val = self._to_number(self._eval_expression(match.group(3)))
            
            body_start = start + 1
            body_end = self._find_block_end(lines, body_start, ['akhir'])
            
            current = start_val
            while current <= end_val:
                self.runtime.set_variable(var_name, current)
                self.runtime.break_loop = False
                self.runtime.continue_loop = False
                
                self._execute_block(lines, body_start, body_end)
                
                if self.runtime.break_loop:
                    self.runtime.break_loop = False
                    break
                
                current += 1
            
            return body_end + 1
        
        raise Exception("Format loop tidak valid")
    
    def _find_block_end(self, lines: List[str], start: int, end_keywords: List[str]) -> int:
        """Find the end of a block"""
        indent_level = 0
        
        for i in range(start, len(lines)):
            line = lines[i].strip()
            
            if line in end_keywords and indent_level == 0:
                return i
            elif line == 'akhir':
                if indent_level == 0 and 'akhir' in end_keywords:
                    return i
                else:
                    indent_level -= 1
            elif line.startswith(('fungsi ', 'jika ', 'selama ', 'untuk ')):
                indent_level += 1
        
        return len(lines)
    
    def _call_function(self, name: str, args: List[Any]) -> Any:
        """Call a user-defined function"""
        if name not in self.runtime.functions:
            raise Exception(f"Function '{name}' tidak ditemukan")
        
        func = self.runtime.functions[name]
        
        if len(args) != len(func['params']):
            raise Exception(f"Function {name} butuh {len(func['params'])} parameter, diberikan {len(args)}")
        
        # Save state
        saved_vars = self.runtime.variables.copy()
        self.runtime.has_return = False
        self.runtime.return_value = None
        
        # Set parameters
        for param, arg in zip(func['params'], args):
            self.runtime.set_variable(param, arg)
        
        # Execute function body
        self._execute_block(func['body'], 0, len(func['body']))
        
        result = self.runtime.return_value
        
        # Restore state
        self.runtime.variables = saved_vars
        self.runtime.has_return = False
        
        return result
    
    def _assign_variable(self, line: str):
        """Handle variable assignment"""
        parts = line.split('=', 1)
        if len(parts) != 2:
            raise Exception(f"Assignment tidak valid: {line}")
        
        var_name = parts[0].strip()
        value_expr = parts[1].strip()
        
        # Special case: array index assignment
        if '[' in var_name and ']' in var_name:
            match = re.match(r'(\w+)\[(.+?)\]', var_name)
            if match:
                arr_name = match.group(1)
                index_expr = match.group(2)
                
                arr = self.runtime.get_variable(arr_name)
                index = int(self._to_number(self._eval_expression(index_expr)))
                value = self._eval_expression(value_expr)
                
                if not isinstance(arr, list):
                    raise Exception(f"{arr_name} bukan array")
                
                if index < 0 or index >= len(arr):
                    raise Exception(f"Index {index} di luar jangkauan")
                
                arr[index] = value
                return
        
        value = self._eval_expression(value_expr)
        self.runtime.set_variable(var_name, value)
    
    def _eval_expression(self, expr: str) -> Any:
        """Evaluate an expression"""
        expr = expr.strip()
        
        # String literal (MUST BE FIRST to handle quoted strings)
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        
        # Boolean literals
        if expr == 'benar':
            return True
        if expr == 'salah':
            return False
        
        # Null
        if expr == 'kosong':
            return None
        
        # Array literal
        if expr.startswith('[') and expr.endswith(']'):
            inner = expr[1:-1].strip()
            if not inner:
                return []
            
            items = self._split_arguments(inner)
            return [self._eval_expression(item) for item in items]
        
        # Object/Dict literal
        if expr.startswith('{') and expr.endswith('}'):
            inner = expr[1:-1].strip()
            if not inner:
                return {}
            
            result = {}
            pairs = self._split_arguments(inner)
            
            for pair in pairs:
                if ':' not in pair:
                    raise Exception(f"Format object salah: {pair}")
                
                key_expr, val_expr = pair.split(':', 1)
                key = self._eval_expression(key_expr.strip())
                val = self._eval_expression(val_expr.strip())
                result[str(key)] = val
            
            return result
        
        # Function call (with proper nested parentheses handling)
        if '(' in expr and expr.endswith(')'):
            func_name_match = re.match(r'^(\w+)\(', expr)
            if func_name_match:
                func_name = func_name_match.group(1)
                # Extract arguments with balanced parentheses
                args_str = self._extract_function_args(expr, len(func_name) + 1)
                
                # Built-in functions
                if func_name == 'panjang':
                    args = self._parse_arguments(args_str)
                    if len(args) != 1:
                        raise Exception("panjang() butuh 1 parameter")
                    val = args[0]
                    if isinstance(val, (str, list, dict)):
                        return len(val)
                    raise Exception("panjang() hanya untuk string/array/object")
                
                elif func_name == 'tipe':
                    args = self._parse_arguments(args_str)
                    if len(args) != 1:
                        raise Exception("tipe() butuh 1 parameter")
                    return type(args[0]).__name__
                
                elif func_name == 'angka':
                    args = self._parse_arguments(args_str)
                    if len(args) != 1:
                        raise Exception("angka() butuh 1 parameter")
                    return self._to_number(args[0])
                
                elif func_name == 'teks':
                    args = self._parse_arguments(args_str)
                    if len(args) != 1:
                        raise Exception("teks() butuh 1 parameter")
                    return self._to_string(args[0])
                
                elif func_name == 'tambahArray':
                    args = self._parse_arguments(args_str)
                    if len(args) != 2:
                        raise Exception("tambahArray() butuh 2 parameter")
                    if not isinstance(args[0], list):
                        raise Exception("Parameter pertama harus array")
                    args[0].append(args[1])
                    return args[0]
                
                elif func_name == 'hapusArray':
                    args = self._parse_arguments(args_str)
                    if len(args) != 2:
                        raise Exception("hapusArray() butuh 2 parameter")
                    if not isinstance(args[0], list):
                        raise Exception("Parameter pertama harus array")
                    index = int(self._to_number(args[1]))
                    if 0 <= index < len(args[0]):
                        return args[0].pop(index)
                    raise Exception(f"Index {index} di luar jangkauan")
                
                # User functions
                elif func_name in self.runtime.functions:
                    args = self._parse_arguments(args_str) if args_str.strip() else []
                    return self._call_function(func_name, args)
        
        # Array/Object access
        access_match = re.match(r'(\w+)\[(.+?)\]', expr)
        if access_match:
            var_name = access_match.group(1)
            key_expr = access_match.group(2)
            
            obj = self.runtime.get_variable(var_name)
            key = self._eval_expression(key_expr)
            
            if isinstance(obj, list):
                index = int(self._to_number(key))
                if 0 <= index < len(obj):
                    return obj[index]
                raise Exception(f"Index {index} di luar jangkauan")
            elif isinstance(obj, dict):
                key_str = str(key)
                if key_str in obj:
                    return obj[key_str]
                raise Exception(f"Key '{key_str}' tidak ditemukan")
            else:
                raise Exception(f"{var_name} bukan array atau object")
        
        # Number literal (BEFORE variable check!)
        try:
            return float(expr) if '.' in expr else int(expr)
        except ValueError:
            pass
        
        # Variable reference (AFTER number check!)
        if re.match(r'^[a-zA-Z_]\w*$', expr):
            return self.runtime.get_variable(expr)
        
        # Comparison and logical operators
        for op in ['==', '!=', '<=', '>=', '<', '>', ' dan ', ' atau ']:
            if op in expr:
                return self._eval_binary_operation(expr, op)
        
        # Arithmetic operators
        for op in ['+', '-', '*', '/', '%']:
            if op in expr:
                # Avoid splitting negative numbers
                if op == '-' and expr.startswith('-'):
                    continue
                return self._eval_binary_operation(expr, op)
        
        raise Exception(f"Tidak dapat mengevaluasi: {expr}")
    
    def _eval_binary_operation(self, expr: str, op: str) -> Any:
        """Evaluate binary operation"""
        parts = expr.split(op, 1)
        if len(parts) != 2:
            raise Exception(f"Operasi binary tidak valid: {expr}")
        
        left = self._eval_expression(parts[0].strip())
        right = self._eval_expression(parts[1].strip())
        
        if op == '+':
            return left + right
        elif op == '-':
            return self._to_number(left) - self._to_number(right)
        elif op == '*':
            return self._to_number(left) * self._to_number(right)
        elif op == '/':
            return self._to_number(left) / self._to_number(right)
        elif op == '%':
            return self._to_number(left) % self._to_number(right)
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '<':
            return self._to_number(left) < self._to_number(right)
        elif op == '>':
            return self._to_number(left) > self._to_number(right)
        elif op == '<=':
            return self._to_number(left) <= self._to_number(right)
        elif op == '>=':
            return self._to_number(left) >= self._to_number(right)
        elif op == ' dan ':
            return self._to_boolean(left) and self._to_boolean(right)
        elif op == ' atau ':
            return self._to_boolean(left) or self._to_boolean(right)
        
        raise Exception(f"Operator tidak dikenal: {op}")
    
    def _extract_function_args(self, expr: str, start_pos: int) -> str:
        """Extract function arguments with balanced parentheses"""
        depth = 0
        in_string = False
        string_char = None
        result = ""
        
        for i in range(start_pos, len(expr)):
            char = expr[i]
            
            if char in ('"', "'") and not in_string:
                in_string = True
                string_char = char
                result += char  # ADD QUOTE TO RESULT
            elif char == string_char and in_string:
                in_string = False
                result += char  # ADD CLOSING QUOTE TO RESULT
            elif not in_string:
                if char == '(':
                    depth += 1
                    result += char
                elif char == ')':
                    if depth == 0:
                        return result
                    depth -= 1
                    result += char
                else:
                    result += char
            else:
                result += char
        
        raise Exception(f"Unclosed parentheses in: {expr}")
    
    def _parse_arguments(self, args_str: str) -> List[Any]:
        """Parse function arguments"""
        if not args_str.strip():
            return []
        
        args = self._split_arguments(args_str)
        return [self._eval_expression(arg.strip()) for arg in args]
    
    def _split_arguments(self, args_str: str) -> List[str]:
        """Split arguments by comma, respecting nested structures"""
        args = []
        current = ""
        depth = 0
        in_string = False
        string_char = None
        
        for char in args_str:
            if char in ('"', "'") and not in_string:
                in_string = True
                string_char = char
            elif char == string_char and in_string:
                in_string = False
            elif not in_string:
                if char in ('(', '[', '{'):
                    depth += 1
                elif char in (')', ']', '}'):
                    depth -= 1
                elif char == ',' and depth == 0:
                    args.append(current.strip())
                    current = ""
                    continue
            
            current += char
        
        if current.strip():
            args.append(current.strip())
        
        return args
    
    def _to_number(self, value: Any) -> float:
        """Convert value to number"""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return 0.0
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        return 0.0
    
    def _to_string(self, value: Any) -> str:
        """Convert value to string"""
        if value is None:
            return "kosong"
        if isinstance(value, bool):
            return "benar" if value else "salah"
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)
    
    def _to_boolean(self, value: Any) -> bool:
        """Convert value to boolean"""
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0 and value != "salah"
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return True
    
    # Satire functions (original)
    
    def _mangkrak(self, ms: float):
        """Mangkrak: Delay dengan event random"""
        seconds = ms / 1000
        self.runtime.log(f"⏳ Proyek mangkrak selama {seconds} detik...")
        
        time.sleep(min(seconds, 2))
        
        events = [
            "💸 Dana habis untuk operasional!",
            "🏃 Vendor kabur dengan uang muka!",
            "🌧️ Longsor menghancurkan pondasi!",
            "🚨 Audit mendadak dari KPK!",
            "📄 Dokumen perizinan bermasalah!",
            "👷 Pekerja mogok kerja!",
        ]
        
        if random.random() < 0.3:
            event = random.choice(events)
            self.runtime.log(f"🚧 EVENT: {event}")
            self.runtime.anggaran -= random.randint(10_000_000, 100_000_000)
            if self.runtime.anggaran < 0:
                self.runtime.anggaran = 0
    
    def _korupsi(self, percent: float):
        """Korupsi: Menghilangkan anggaran"""
        if percent < 0 or percent > 100:
            raise Exception("Persentase korupsi harus 0-100")
        
        actual_percent = random.uniform(percent * 0.8, percent * 1.2)
        amount = self.runtime.anggaran * (actual_percent / 100)
        self.runtime.anggaran -= amount
        
        if self.runtime.anggaran < 0:
            self.runtime.anggaran = 0
        
        self.runtime.log(f"💰 Korupsi {actual_percent:.1f}%: Rp {amount:,.0f} menguap!")
        self.runtime.log(f"📊 Sisa anggaran: Rp {self.runtime.anggaran:,.0f}")
    
    def _rapat_infinite(self):
        """RapatInfinite: Loop rapat"""
        self.runtime.log("🔄 Memulai RapatInfinite()...")
        self.runtime.log("⚠️ Program terjebak dalam rapat berkepanjangan!")
        
        for i in range(5):
            self.runtime.log(f"📋 Rapat sesi ke-{i+1}: Belum ada keputusan...")
            time.sleep(0.5)
        
        self.runtime.log("⏸️ (RapatInfinite dihentikan paksa untuk demo)")
    
    def _selesai(self):
        """selesai: End program"""
        self.runtime.status_proyek = "Selesai (di atas kertas)"
        self.runtime.progress = 100
        
        bar = "█" * 9 + "░"
        self.runtime.log(f"\n✅ PROYEK SELESAI!")
        self.runtime.log(f"Progress: 100% [{bar}]")
        self.runtime.log(f"Status: {self.runtime.status_proyek}")
        self.runtime.log(f"Sisa Anggaran: Rp {self.runtime.anggaran:,.0f}")
        self.runtime.log(f"(Kondisi fisik: Data tidak tersedia)")
        
        self.runtime.terminated = True
    
    # File operations
    
    def _handle_file_operation(self, line: str):
        """Handle file I/O operations"""
        
        # tulisFile(path, content)
        match = re.match(r'tulisFile\((.+?),\s*(.+)\)', line)
        if match:
            path = self._to_string(self._eval_expression(match.group(1)))
            content = self._to_string(self._eval_expression(match.group(2)))
            
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.runtime.log(f"✅ File ditulis: {path}")
            except Exception as e:
                raise Exception(f"Gagal menulis file: {str(e)}")
            return
        
        # bacaFile(path)
        match = re.match(r'(\w+)\s*=\s*bacaFile\((.+?)\)', line)
        if match:
            var_name = match.group(1)
            path = self._to_string(self._eval_expression(match.group(2)))
            
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.runtime.set_variable(var_name, content)
                self.runtime.log(f"✅ File dibaca: {path}")
            except Exception as e:
                raise Exception(f"Gagal membaca file: {str(e)}")
            return
    
    # Database operations
    
    def _handle_db_operation(self, line: str):
        """Handle database operations"""
        
        # sambungDB(nama, tipe, path/connection_string)
        match = re.match(r'sambungDB\((.+?),\s*(.+?),\s*(.+)\)', line)
        if match:
            name = self._to_string(self._eval_expression(match.group(1)))
            db_type = self._to_string(self._eval_expression(match.group(2)))
            conn_str = self._to_string(self._eval_expression(match.group(3)))
            
            try:
                if db_type == 'sqlite':
                    conn = sqlite3.connect(conn_str)
                    self.runtime.db_connections[name] = conn
                    self.runtime.log(f"✅ Terhubung ke SQLite: {name}")
                elif db_type == 'mysql':
                    if not HAS_MYSQL:
                        raise Exception("mysql-connector-python tidak terinstall")
                    # Parse connection string
                    conn = mysql.connector.connect(conn_str)
                    self.runtime.db_connections[name] = conn
                    self.runtime.log(f"✅ Terhubung ke MySQL: {name}")
                else:
                    raise Exception(f"Tipe database tidak didukung: {db_type}")
            except Exception as e:
                raise Exception(f"Gagal koneksi database: {str(e)}")
            return
        
        # queryDB(nama, query)
        match = re.match(r'(\w+)\s*=\s*queryDB\((.+?),\s*(.+)\)', line)
        if match:
            var_name = match.group(1)
            db_name = self._to_string(self._eval_expression(match.group(2)))
            query = self._to_string(self._eval_expression(match.group(3)))
            
            if db_name not in self.runtime.db_connections:
                raise Exception(f"Database '{db_name}' tidak terhubung")
            
            try:
                conn = self.runtime.db_connections[db_name]
                cursor = conn.cursor()
                cursor.execute(query)
                
                if query.strip().upper().startswith('SELECT'):
                    results = cursor.fetchall()
                    self.runtime.set_variable(var_name, list(results))
                else:
                    conn.commit()
                    self.runtime.set_variable(var_name, cursor.rowcount)
                
                cursor.close()
                self.runtime.log(f"✅ Query dijalankan: {var_name}")
            except Exception as e:
                raise Exception(f"Gagal menjalankan query: {str(e)}")
            return
        
        # tutupDB(nama)
        match = re.match(r'tutupDB\((.+?)\)', line)
        if match:
            db_name = self._to_string(self._eval_expression(match.group(1)))
            
            if db_name in self.runtime.db_connections:
                self.runtime.db_connections[db_name].close()
                del self.runtime.db_connections[db_name]
                self.runtime.log(f"✅ Koneksi ditutup: {db_name}")
            return
    
    # HTTP operations
    
    def _handle_http_operation(self, line: str):
        """Handle HTTP operations"""
        if not HAS_REQUESTS:
            raise Exception("Library 'requests' tidak terinstall")
        
        # httpGet(url)
        match = re.match(r'(\w+)\s*=\s*httpGet\((.+?)\)', line)
        if match:
            var_name = match.group(1)
            url = self._to_string(self._eval_expression(match.group(2)))
            
            try:
                response = requests.get(url, timeout=10)
                result = {
                    'status': response.status_code,
                    'body': response.text,
                    'json': response.json() if 'application/json' in response.headers.get('content-type', '') else None
                }
                self.runtime.set_variable(var_name, result)
                self.runtime.log(f"✅ HTTP GET: {url} - Status {response.status_code}")
            except Exception as e:
                raise Exception(f"HTTP request gagal: {str(e)}")
            return
        
        # httpPost(url, data)
        match = re.match(r'(\w+)\s*=\s*httpPost\((.+?),\s*(.+)\)', line)
        if match:
            var_name = match.group(1)
            url = self._to_string(self._eval_expression(match.group(2)))
            data = self._eval_expression(match.group(3))
            
            try:
                response = requests.post(url, json=data, timeout=10)
                result = {
                    'status': response.status_code,
                    'body': response.text,
                    'json': response.json() if 'application/json' in response.headers.get('content-type', '') else None
                }
                self.runtime.set_variable(var_name, result)
                self.runtime.log(f"✅ HTTP POST: {url} - Status {response.status_code}")
            except Exception as e:
                raise Exception(f"HTTP request gagal: {str(e)}")
            return


def run_file(filepath: str):
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
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        try:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        except:
            pass
    
    if len(sys.argv) < 2:
        print("Usage: python hamba_v2.py <file.hl>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not filepath.endswith('.hl'):
        print("❌ File harus berekstensi .hl")
        sys.exit(1)
    
    run_file(filepath)


if __name__ == '__main__':
    main()
