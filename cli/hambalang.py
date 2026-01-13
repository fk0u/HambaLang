#!/usr/bin/env python3
"""
HambaLang CLI - Professional tooling for .hl language
Commands: run, compile, debug, disasm, ctf
"""
import sys
import os
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Color codes for terminal
class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(msg):
    print(f"{Color.HEADER}{Color.BOLD}{msg}{Color.ENDC}")

def print_success(msg):
    print(f"{Color.OKGREEN}✓ {msg}{Color.ENDC}")

def print_error(msg):
    print(f"{Color.FAIL}✗ {msg}{Color.ENDC}")

def print_info(msg):
    print(f"{Color.OKCYAN}ℹ {msg}{Color.ENDC}")


def cmd_run(args):
    """Run HambaLang source or bytecode"""
    filepath = args.file
    
    if not os.path.exists(filepath):
        print_error(f"File tidak ditemukan: {filepath}")
        return 1
    
    # Check file extension
    ext = Path(filepath).suffix
    
    if ext == '.hbc':
        # Run bytecode
        from vm.hamba_vm import run_bytecode_file
        print_header("🚀 HambaVM - Bytecode Execution")
        success = run_bytecode_file(
            filepath,
            debug=args.debug,
            seed=args.seed,
            ctf_mode=args.ctf,
            step_limit=args.step_limit,
            delay=args.delay
        )
        return 0 if success else 1
    
    elif ext == '.hl':
        # Run source (via interpreter or compile first)
        if args.vm:
            # Compile to bytecode first, then run
            print_info("Compiling to bytecode...")
            if cmd_compile_internal(filepath, args) != 0:
                return 1
            # Run the compiled bytecode
            bytecode_path = filepath.replace('.hl', '.hbc')
            from vm.hamba_vm import run_bytecode_file
            print_header("🚀 HambaVM - Bytecode Execution")
            success = run_bytecode_file(
                bytecode_path,
                debug=args.debug,
                seed=args.seed,
                ctf_mode=args.ctf,
                step_limit=args.step_limit,
                delay=args.delay
            )
            return 0 if success else 1
        else:
            # Use interpreter directly
            print_header("🎭 HambaLang Interpreter")
            cmd_parts = ['python', 'interpreter/hamba_advanced.py', filepath]
            if args.debug:
                cmd_parts.append('--debug')
            if args.seed is not None:
                cmd_parts.extend(['--seed', str(args.seed)])
            if args.ctf:
                cmd_parts.append('--ctf')
            if args.delay > 0:
                cmd_parts.extend(['--delay', str(args.delay)])
            
            import subprocess
            result = subprocess.run(cmd_parts)
            return result.returncode
    
    else:
        print_error(f"Format file tidak didukung: {ext}")
        print_info("Gunakan .hl (source) atau .hbc (bytecode)")
        return 1


def cmd_compile_internal(filepath, args):
    """Internal compile function"""
    # Parse source
    from interpreter.hamba_advanced import Parser
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        print_error(f"Gagal membaca file: {e}")
        return 1
    
    # Parse to AST
    try:
        lines = source.split('\n')
        parser = Parser(lines)
        ast = parser.parse()
    except Exception as e:
        print_error(f"Parse error: {e}")
        return 1
    
    # Compile to bytecode
    from compiler.bytecode import BytecodeCompiler
    try:
        compiler = BytecodeCompiler()
        bytecode = compiler.compile(ast)
    except Exception as e:
        print_error(f"Compile error: {e}")
        return 1
    
    # Save bytecode
    output_path = filepath.replace('.hl', '.hbc')
    try:
        bytecode.save(output_path)
        print_success(f"Bytecode saved: {output_path}")
        print_info(f"Size: {len(bytecode.code)} bytes code, {len(bytecode.constants)} constants, {len(bytecode.strings)} strings")
        return 0
    except Exception as e:
        print_error(f"Failed to save bytecode: {e}")
        return 1


def cmd_compile(args):
    """Compile .hl source to .hbc bytecode"""
    filepath = args.file
    
    if not os.path.exists(filepath):
        print_error(f"File tidak ditemukan: {filepath}")
        return 1
    
    if not filepath.endswith('.hl'):
        print_error("File harus berekstensi .hl")
        return 1
    
    print_header("🔧 HambaLang Compiler")
    print_info(f"Compiling: {filepath}")
    
    return cmd_compile_internal(filepath, args)


def cmd_disasm(args):
    """Disassemble bytecode"""
    filepath = args.file
    
    if not os.path.exists(filepath):
        print_error(f"File tidak ditemukan: {filepath}")
        return 1
    
    if not filepath.endswith('.hbc'):
        print_error("File harus berekstensi .hbc")
        return 1
    
    print_header("🔍 HambaLang Disassembler")
    
    from compiler.bytecode import Bytecode, disassemble
    try:
        bytecode = Bytecode.load(filepath)
        output = disassemble(bytecode)
        print(output)
        return 0
    except Exception as e:
        print_error(f"Disassembly error: {e}")
        return 1


def cmd_debug(args):
    """Interactive debugger"""
    filepath = args.file
    
    if not os.path.exists(filepath):
        print_error(f"File tidak ditemukan: {filepath}")
        return 1
    
    # Compile if source
    if filepath.endswith('.hl'):
        print_info("Compiling for debug...")
        if cmd_compile_internal(filepath, args) != 0:
            return 1
        filepath = filepath.replace('.hl', '.hbc')
    
    print_header("🐛 HambaLang Debugger")
    print_info("Commands: step, run, stack, vars, state, quit")
    
    from compiler.bytecode import Bytecode
    from vm.hamba_vm import HambaVM
    
    try:
        bytecode = Bytecode.load(filepath)
        vm = HambaVM(bytecode, seed=args.seed, debug=True)
        
        while True:
            cmd = input(f"{Color.OKCYAN}(hdb){Color.ENDC} ").strip().lower()
            
            if cmd == 'quit' or cmd == 'q':
                break
            
            elif cmd == 'step' or cmd == 's':
                if vm.pc >= len(vm.code):
                    print_info("Program selesai")
                else:
                    vm.step()
            
            elif cmd == 'run' or cmd == 'r':
                print_info("Running to completion...")
                vm.run()
            
            elif cmd == 'stack':
                print(f"Stack ({len(vm.stack)} items): {vm.stack}")
            
            elif cmd == 'vars':
                print(f"Variables: {vm.variables}")
            
            elif cmd == 'state':
                state = vm.get_state()
                for k, v in state.items():
                    print(f"  {k}: {v}")
            
            elif cmd == 'help' or cmd == 'h':
                print("Commands:")
                print("  step/s    - Execute one instruction")
                print("  run/r     - Run to completion")
                print("  stack     - Show stack")
                print("  vars      - Show variables")
                print("  state     - Show VM state")
                print("  quit/q    - Exit debugger")
            
            else:
                print_error(f"Unknown command: {cmd}")
        
        return 0
    
    except Exception as e:
        print_error(f"Debugger error: {e}")
        return 1


def cmd_ctf(args):
    """Run in CTF mode with hints"""
    filepath = args.file
    
    if not os.path.exists(filepath):
        print_error(f"File tidak ditemukan: {filepath}")
        return 1
    
    print_header("🎯 HambaLang CTF Challenge")
    print(f"{Color.WARNING}GOAL: Selesaikan proyek dengan anggaran tepat 0{Color.ENDC}")
    print(f"{Color.WARNING}HINT: Gunakan --seed untuk deterministic execution{Color.ENDC}")
    print("=" * 60)
    
    args.ctf = True
    # Add missing attributes for cmd_run
    if not hasattr(args, 'debug'):
        args.debug = False
    if not hasattr(args, 'delay'):
        args.delay = 0.0
    if not hasattr(args, 'step_limit'):
        args.step_limit = 100000
    
    if args.seed is None:
        print_info("Tip: Coba --seed 42 atau --seed 1337")
    
    return cmd_run(args)


def main():
    parser = argparse.ArgumentParser(
        prog='hambalang',
        description='HambaLang - Esoteric bureaucratic programming language',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hambalang run demo.hl                  # Run with interpreter
  hambalang run demo.hl --vm             # Compile & run on VM
  hambalang compile demo.hl              # Compile to bytecode
  hambalang run demo.hbc                 # Run bytecode
  hambalang disasm demo.hbc              # Disassemble bytecode
  hambalang debug demo.hl                # Interactive debugger
  hambalang ctf challenge.hl --seed 42   # CTF mode
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # run command
    run_parser = subparsers.add_parser('run', help='Run source or bytecode')
    run_parser.add_argument('file', help='File to run (.hl or .hbc)')
    run_parser.add_argument('--vm', action='store_true', help='Use VM (compile first if .hl)')
    run_parser.add_argument('--debug', action='store_true', help='Enable debug trace')
    run_parser.add_argument('--seed', type=int, help='Random seed')
    run_parser.add_argument('--ctf', action='store_true', help='CTF mode')
    run_parser.add_argument('--step-limit', type=int, default=100000, help='Max execution steps')
    run_parser.add_argument('--delay', type=float, default=0.0, help='Delay between steps (seconds)')
    
    # compile command
    compile_parser = subparsers.add_parser('compile', help='Compile .hl to .hbc')
    compile_parser.add_argument('file', help='Source file (.hl)')
    
    # disasm command
    disasm_parser = subparsers.add_parser('disasm', help='Disassemble bytecode')
    disasm_parser.add_argument('file', help='Bytecode file (.hbc)')
    
    # debug command
    debug_parser = subparsers.add_parser('debug', help='Interactive debugger')
    debug_parser.add_argument('file', help='File to debug (.hl or .hbc)')
    debug_parser.add_argument('--seed', type=int, help='Random seed')
    
    # ctf command
    ctf_parser = subparsers.add_parser('ctf', help='Run in CTF challenge mode')
    ctf_parser.add_argument('file', help='Challenge file')
    ctf_parser.add_argument('--seed', type=int, help='Random seed')
    ctf_parser.add_argument('--vm', action='store_true', help='Use VM')
    ctf_parser.add_argument('--step-limit', type=int, default=100000, help='Max execution steps')
    ctf_parser.add_argument('--delay', type=float, default=0.0, help='Delay between steps')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to command handlers
    commands = {
        'run': cmd_run,
        'compile': cmd_compile,
        'disasm': cmd_disasm,
        'debug': cmd_debug,
        'ctf': cmd_ctf
    }
    
    handler = commands.get(args.command)
    if handler:
        try:
            return handler(args)
        except KeyboardInterrupt:
            print(f"\n{Color.WARNING}⚠ Interrupted{Color.ENDC}")
            return 130
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return 1
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
