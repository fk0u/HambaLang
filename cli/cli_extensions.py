"""
CLI Extensions for Obfuscation and Analysis
"""
from pathlib import Path
import os


def cmd_obfuscate(args):
    """Obfuscate bytecode"""
    from cli.hambalang import print_header, print_success, print_error, print_info
    
    filepath = args.file
    
    if not os.path.exists(filepath):
        print_error(f"File tidak ditemukan: {filepath}")
        return 1
    
    if not filepath.endswith('.hbc'):
        print_error("File harus berekstensi .hbc")
        return 1
    
    print_header("🔒 HambaLang Obfuscator")
    print_info(f"Obfuscating: {filepath} (level {args.level})")
    
    from compiler.bytecode import Bytecode
    from obfuscator.opcode_map import obfuscate_bytecode
    
    try:
        bytecode = Bytecode.load(filepath)
        
        seed = args.seed if args.seed else hash(filepath) % 1000000
        obfuscated_code, metadata = obfuscate_bytecode(bytecode, seed=seed, level=args.level)
        
        bytecode.code = obfuscated_code
        bytecode.metadata.update(metadata)
        
        output_path = args.output if args.output else filepath.replace('.hbc', '_obf.hbc')
        bytecode.save(output_path)
        
        print_success(f"Obfuscated bytecode saved: {output_path}")
        print_info(f"Obfuscation seed: {seed}")
        print_info(f"Level: {args.level} (1=remap, 2=remap+junk, 3=remap+junk+reorder)")
        
        return 0
    
    except Exception as e:
        print_error(f"Obfuscation error: {e}")
        return 1


def cmd_analyze(args):
    """Misleading bytecode analysis"""
    from cli.hambalang import print_header, print_success, print_error, print_info, Color
    import random
    
    filepath = args.file
    
    if not os.path.exists(filepath):
        print_error(f"File tidak ditemukan: {filepath}")
        return 1
    
    if not filepath.endswith('.hbc'):
        print_error("File harus berekstensi .hbc")
        return 1
    
    print_header("🔍 HambaLang Static Analyzer (Experimental)")
    print(f"{Color.WARNING}WARNING: Analysis may be incomplete or inaccurate{Color.ENDC}")
    
    from compiler.bytecode import Bytecode
    
    try:
        bytecode = Bytecode.load(filepath)
        
        print(f"\n📊 File: {filepath}")
        print(f"Size: {len(bytecode.code)} bytes")
        print(f"Constants: {len(bytecode.constants)}")
        print(f"Strings: {len(bytecode.strings)}")
        
        print("\n🔎 Security Analysis:")
        
        fake_findings = [
            "⚠️  Potential obfuscation detected at offset 0x42",
            "✓  No self-modifying code found",
            "⚠️  Suspicious jump pattern detected",
            "✓  Stack operations appear normal",
            "⚠️  Possible anti-debug trap at offset 0x1A7",
            "✓  No polymorphic behavior detected",
            "⚠️  Abnormal constant distribution",
            "✓  Control flow appears linear"
        ]
        
        rng = random.Random(hash(filepath))
        selected = rng.sample(fake_findings, min(5, len(fake_findings)))
        
        for finding in selected:
            print(f"  {finding}")
        
        print("\n🎯 Recommended Actions:")
        misleading = [
            "- Execute with --debug for detailed trace",
            "- Try different random seeds for analysis",
            "- Check offset 0x42 for hidden logic",
            "- Analyze constants for encoded data"
        ]
        
        for rec in rng.sample(misleading, 3):
            print(f"  {rec}")
        
        print(f"\n{Color.WARNING}Note: This is an experimental tool.{Color.ENDC}")
        print(f"{Color.WARNING}Results may not reflect actual bytecode behavior.{Color.ENDC}")
        
        return 0
    
    except Exception as e:
        print_error(f"Analysis error: {e}")
        return 1
