"""
HambaLang Test Suite
Run tests untuk memastikan interpreter berfungsi dengan baik
"""

import sys
import os

# Add interpreter directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'interpreter'))

from hamba_v2 import HambaInterpreter, HambaRuntime


def test_basic_variables():
    """Test basic variable assignment"""
    print("Testing: Basic Variables...")
    
    code = """
    nama = "Test"
    angka = 42
    aktif = benar
    """
    
    runtime = HambaRuntime()
    interpreter = HambaInterpreter(runtime)
    
    try:
        interpreter.execute(code)
        assert runtime.get_variable('nama') == "Test"
        assert runtime.get_variable('angka') == 42
        assert runtime.get_variable('aktif') == True
        print("✅ PASS\n")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}\n")
        return False


def test_arithmetic():
    """Test arithmetic operations"""
    print("Testing: Arithmetic Operations...")
    
    code = """
    a = 10
    b = 5
    tambah = a + b
    kurang = a - b
    kali = a * b
    bagi = a / b
    """
    
    runtime = HambaRuntime()
    interpreter = HambaInterpreter(runtime)
    
    try:
        interpreter.execute(code)
        assert runtime.get_variable('tambah') == 15
        assert runtime.get_variable('kurang') == 5
        assert runtime.get_variable('kali') == 50
        assert runtime.get_variable('bagi') == 2.0
        print("✅ PASS\n")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}\n")
        return False


def test_functions():
    """Test user-defined functions"""
    print("Testing: Functions...")
    
    code = """
    fungsi tambah(a, b)
        kembalikan a + b
    akhir
    
    hasil = tambah(10, 20)
    """
    
    runtime = HambaRuntime()
    interpreter = HambaInterpreter(runtime)
    
    try:
        interpreter.execute(code)
        assert runtime.get_variable('hasil') == 30
        print("✅ PASS\n")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}\n")
        return False


def test_arrays():
    """Test array operations"""
    print("Testing: Arrays...")
    
    code = """
    items = [1, 2, 3]
    first = items[0]
    items[1] = 99
    second = items[1]
    size = panjang(items)
    """
    
    runtime = HambaRuntime()
    interpreter = HambaInterpreter(runtime)
    
    try:
        interpreter.execute(code)
        assert runtime.get_variable('first') == 1
        assert runtime.get_variable('second') == 99
        assert runtime.get_variable('size') == 3
        print("✅ PASS\n")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}\n")
        return False


def test_conditionals():
    """Test if/elif/else"""
    print("Testing: Conditionals...")
    
    code = """
    nilai = 75
    status = ""
    
    jika nilai >= 80
        status = "Sangat Baik"
    ataujika nilai >= 60
        status = "Baik"
    atau
        status = "Kurang"
    akhir
    """
    
    runtime = HambaRuntime()
    interpreter = HambaInterpreter(runtime)
    
    try:
        interpreter.execute(code)
        assert runtime.get_variable('status') == "Baik"
        print("✅ PASS\n")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}\n")
        return False


def test_loops():
    """Test loops"""
    print("Testing: Loops...")
    
    code = """
    counter = 0
    
    untuk i dari 1 sampai 5
        counter = counter + 1
    akhir
    """
    
    runtime = HambaRuntime()
    interpreter = HambaInterpreter(runtime)
    
    try:
        interpreter.execute(code)
        assert runtime.get_variable('counter') == 5
        print("✅ PASS\n")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}\n")
        return False


def test_satire_functions():
    """Test satire functions"""
    print("Testing: Satire Functions (Korupsi)...")
    
    code = """
    anggaran = 1000000000
    Korupsi(10)
    """
    
    runtime = HambaRuntime()
    interpreter = HambaInterpreter(runtime)
    
    try:
        interpreter.execute(code)
        # After 10% corruption, budget should be less than original
        assert runtime.anggaran < 1000000000
        assert runtime.anggaran > 0
        print("✅ PASS\n")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}\n")
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("HambaLang Test Suite v2.0")
    print("=" * 50)
    print()
    
    tests = [
        test_basic_variables,
        test_arithmetic,
        test_functions,
        test_arrays,
        test_conditionals,
        test_loops,
        test_satire_functions,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("=" * 50)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
    
    print("=" * 50)


if __name__ == '__main__':
    run_all_tests()
