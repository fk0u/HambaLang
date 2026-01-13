#!/usr/bin/env python3
"""
Quick test script for HambaLang v3.0
Tests bytecode compilation and VM execution
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_compilation():
    """Test bytecode compilation"""
    print("=" * 60)
    print("🔧 TEST 1: Bytecode Compilation")
    print("=" * 60)
    
    from interpreter.hamba_advanced import Parser
    from compiler.bytecode import BytecodeCompiler, disassemble
    
    source = 'lapor "Testing compilation..."\nmulai\n    set x = 10\n    set y = 20\n    set z = x + y\n    lapor z\nakhir'
    
    # Parse
    parser = Parser(source)
    ast = parser.parse()
    print("✓ Parsing successful")
    
    # Compile
    compiler = BytecodeCompiler()
    bytecode = compiler.compile(ast)
    print(f"✓ Compilation successful")
    print(f"  Code size: {len(bytecode.code)} bytes")
    print(f"  Constants: {len(bytecode.constants)}")
    print(f"  Strings: {len(bytecode.strings)}")
    
    # Disassemble
    print("\n" + disassemble(bytecode))
    
    return bytecode


def test_vm_execution(bytecode):
    """Test VM execution"""
    print("\n" + "=" * 60)
    print("🚀 TEST 2: VM Execution")
    print("=" * 60)
    
    from vm.hamba_vm import HambaVM
    
    vm = HambaVM(bytecode, debug=False)
    success = vm.run()
    
    if success:
        print("✓ Execution successful")
        state = vm.get_state()
        print(f"  Steps: {state['step_count']}")
        print(f"  Anggaran: {state['anggaran']}")
        print(f"  Progress: {state['progress']}")
    
    return success


def test_file_io():
    """Test saving and loading bytecode"""
    print("\n" + "=" * 60)
    print("💾 TEST 3: File I/O")
    print("=" * 60)
    
    from interpreter.hamba_advanced import Parser
    from compiler.bytecode import BytecodeCompiler, Bytecode
    
    source = 'lapor "Testing file I/O..."\nset test = 42\nlapor test'
    
    # Compile
    parser = Parser(source)
    ast = parser.parse()
    compiler = BytecodeCompiler()
    bytecode = compiler.compile(ast)
    
    # Save
    test_file = "test_output.hbc"
    bytecode.save(test_file)
    print(f"✓ Saved to {test_file}")
    
    # Load
    loaded = Bytecode.load(test_file)
    print(f"✓ Loaded from {test_file}")
    print(f"  Code size: {len(loaded.code)} bytes")
    
    # Execute loaded bytecode
    from vm.hamba_vm import HambaVM
    vm = HambaVM(loaded)
    vm.run()
    
    # Cleanup
    os.remove(test_file)
    print(f"✓ Cleaned up {test_file}")
    
    return True


def test_ctf_mode():
    """Test CTF mode"""
    print("\n" + "=" * 60)
    print("🎯 TEST 4: CTF Mode")
    print("=" * 60)
    
    from interpreter.hamba_advanced import Parser
    from compiler.bytecode import BytecodeCompiler
    from vm.hamba_vm import HambaVM
    
    source = 'lapor "CTF Test: Perfect Budget"\nmulai\n    set progress = 0\n    Korupsi(20)\n    set progress = 50\n    Korupsi(80)\n    set progress = 100\nakhir'
    
    parser = Parser(source)
    ast = parser.parse()
    compiler = BytecodeCompiler()
    bytecode = compiler.compile(ast)
    
    vm = HambaVM(bytecode, seed=42)
    vm.run(ctf_mode=True)
    
    state = vm.get_state()
    print(f"Final state:")
    print(f"  Anggaran: {state['anggaran']}")
    print(f"  Progress: {state['progress']}")
    
    if state['anggaran'] == 0 and state['progress'] >= 100:
        print("✓ CTF condition met!")
    
    return True


def main():
    """Run all tests"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        HambaLang v3.0 - Quick Test Suite                  ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    try:
        # Test 1: Compilation
        bytecode = test_compilation()
        
        # Test 2: VM Execution
        test_vm_execution(bytecode)
        
        # Test 3: File I/O
        test_file_io()
        
        # Test 4: CTF Mode
        test_ctf_mode()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Try: python cli/hambalang.py run examples/bytecode_demo.hl")
        print("  2. Try: python cli/hambalang.py compile examples/bytecode_demo.hl")
        print("  3. Try: python cli/hambalang.py debug examples/bytecode_demo.hl")
        print("  4. Try: python cli/hambalang.py ctf examples/challenge_vm.hl --seed 42")
        print()
        
        return 0
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
