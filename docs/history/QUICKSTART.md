# HambaLang v3.0 - Quick Start Guide

## Installation (No Dependencies!)

```bash
git clone https://github.com/yourusername/hambalang.git
cd hambalang
```

That's it! Pure Python 3.8+, no pip install needed.

---

## 5-Minute Tutorial

### 1. Create Your First Program

Create `hello.hl`:
```hl
lapor "Hello, HambaVM!"

mulai
    set x = 10
    set y = 20
    set result = x + y
    lapor "10 + 20 = " + result
    
    jika result == 30
        lapor "✓ Math works!"
    akhir
akhir
```

### 2. Run with Interpreter (Fast)

```bash
python interpreter/hamba_advanced.py hello.hl
```

### 3. Compile to Bytecode

```bash
python cli/hambalang.py compile hello.hl
# Creates hello.hbc
```

### 4. Run on Virtual Machine

```bash
python cli/hambalang.py run hello.hbc
```

### 5. See the Bytecode

```bash
python cli/hambalang.py disasm hello.hbc
```

---

## Advanced Usage

### Interactive Debugger

```bash
python cli/hambalang.py debug hello.hl
```

Commands:
- `step` - Execute one instruction
- `stack` - Show stack contents
- `vars` - Show all variables
- `state` - Full VM state
- `run` - Run to completion
- `quit` - Exit

### CTF Challenge

```bash
python cli/hambalang.py ctf examples/challenge_vm.hl --seed 42
```

Goal: Get budget to exactly 0 while completing the project!

### Debug Tracing

```bash
python cli/hambalang.py run hello.hbc --debug
```

Shows each instruction as it executes.

---

## Language Cheat Sheet

### Variables
```hl
set name = "value"
set number = 42
set anggaran = 1000000  // Built-in budget variable
set progress = 0        // Built-in progress variable
```

### Output
```hl
lapor "Hello!"
lapor variable_name
lapor "Result: " + variable_name
```

### Conditionals
```hl
jika x == 10
    lapor "x is 10"
akhir

jika x < 10
    lapor "x is less than 10"
akhir
```

### Loops
```hl
Rapat(5)
    lapor "Meeting iteration..."
selesaiRapat
```

### Scoped Blocks
```hl
mulai
    set local_var = 42
    lapor local_var
akhir
```

### Satirical Features
```hl
Korupsi(10)  // Corrupt 10% of budget
Mangkrak("Project stopped")  // Throw error
```

### Exception Handling
```hl
coba
    Korupsi(50)
jikaGagal
    lapor "Error handled!"
akhirCoba
```

---

## Opcodes Reference

| Opcode | Mnemonic | Description |
|--------|----------|-------------|
| 0x01 | PUSH | Push constant/string to stack |
| 0x02 | POP | Pop stack top |
| 0x03 | LOAD | Load variable to stack |
| 0x04 | STORE | Store stack top to variable |
| 0x10 | PRINT | Print stack top |
| 0x20 | ADD | a + b |
| 0x21 | SUB | a - b |
| 0x22 | MUL | a * b |
| 0x23 | DIV | a / b |
| 0x30 | EQ | a == b |
| 0x31 | LT | a < b |
| 0x32 | GT | a > b |
| 0x40 | JUMP | Unconditional jump |
| 0x41 | JIF | Jump if false |
| 0x60 | KORUPSI | Corrupt budget |
| 0xFF | END | Halt execution |

---

## CLI Commands

```bash
# Run source (interpreter)
python cli/hambalang.py run file.hl

# Run source on VM
python cli/hambalang.py run file.hl --vm

# Compile to bytecode
python cli/hambalang.py compile file.hl

# Run bytecode
python cli/hambalang.py run file.hbc

# Disassemble
python cli/hambalang.py disasm file.hbc

# Debug
python cli/hambalang.py debug file.hl

# CTF mode
python cli/hambalang.py ctf file.hl --seed 42
```

---

## Flags

- `--vm` - Use VM instead of interpreter
- `--debug` - Show execution trace
- `--seed N` - Set random seed (deterministic)
- `--ctf` - Enable CTF flag detection
- `--step-limit N` - Max execution steps (default: 100000)
- `--delay N` - Delay between steps in seconds

---

## File Extensions

- `.hl` - HambaLang source code
- `.hbc` - HambaLang Bytecode (compiled)

---

## Examples Included

1. **simple_test.hl** - Basic features demo
2. **challenge_vm.hl** - CTF budget challenge
3. **bytecode_demo.hl** - All opcodes showcase
4. **debug_test.hl** - Debugger demo

---

## Tips & Tricks

### Deterministic Execution
Use `--seed` for reproducible results:
```bash
python cli/hambalang.py run file.hl --seed 42
```

### Speed Control
Use `--delay` to slow down execution for visualization:
```bash
python cli/hambalang.py run file.hbc --delay 0.1
```

### Anti-Infinite Loop
Set step limit to prevent runaway programs:
```bash
python cli/hambalang.py run file.hl --step-limit 1000
```

---

## WASM (Advanced)

### Compile WASM
```bash
wat2wasm wasm/hamba_wasm.wat -o wasm/hamba_wasm.wasm
```

### Use in Browser
```html
<script src="wasm/hamba_wasm_loader.js"></script>
<script>
  const wasm = new HambaWASM();
  await wasm.init();
  const bytecode = [...]; // Your bytecode array
  const state = await wasm.executeBytecode(bytecode);
  console.log(wasm.getOutput());
</script>
```

---

## Troubleshooting

### "No module named 'interpreter'"
Make sure you're in the project root directory.

### "Syntax tidak dikenali"
- Remove full-line comments (`//` at line start)
- Inline comments work: `set x = 5 // comment`

### UTF-8 Encoding Errors
Already fixed for Windows. If issues persist, check file encoding.

---

## Learning Resources

- **VM Architecture**: `docs/VM_ARCHITECTURE.md`
- **Language Features**: `docs/ADVANCED.md`
- **Phase 3 Summary**: `PHASE3_COMPLETE.md`

---

## Next Steps

1. ✅ Write your first HambaLang program
2. ✅ Compile and run on VM
3. ✅ Try the debugger
4. ✅ Solve the CTF challenge
5. ✅ Examine the bytecode
6. ✅ Add custom opcodes
7. ✅ Extend the VM
8. ✅ Build WASM features

---

## Support

For bugs, features, or questions:
- GitHub Issues: [hambalang/issues](https://github.com/yourusername/hambalang/issues)
- Documentation: `docs/`

---

**Happy Coding with HambaLang! 🚀**

*Where bureaucratic satire meets serious compiler engineering.*
