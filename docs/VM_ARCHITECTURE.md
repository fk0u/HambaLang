# HambaLang v3.0 - VM & Bytecode Architecture

## 🚀 Phase 3: Professional Runtime

HambaLang telah berkembang dari interpreter sederhana menjadi **custom language runtime** dengan:

- **Bytecode Compiler** (.hl → .hbc)
- **Stack-based Virtual Machine** (HambaVM)
- **WASM Backend** (browser-native execution)
- **Professional CLI Tooling**
- **Interactive Debugger**
- **CTF-grade obfuscation**

---

## 📦 Architecture Overview

```
┌─────────────┐
│  Source.hl  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Parser    │  (hamba_advanced.py)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│     AST     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Bytecode   │  (bytecode.py)
│  Compiler   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   .hbc      │  (Binary format)
└──────┬──────┘
       │
       ├─────────────────┐
       ▼                 ▼
┌─────────────┐   ┌─────────────┐
│  HambaVM    │   │  WASM       │
│  (Python)   │   │  Runtime    │
└─────────────┘   └─────────────┘
```

---

## 🔧 Installation & Setup

```bash
# Clone repository
git clone https://github.com/yourusername/hambalang.git
cd hambalang

# No dependencies needed! Pure Python + WASM
# Optional: Compile WASM (requires wabt)
wat2wasm wasm/hamba_wasm.wat -o wasm/hamba_wasm.wasm
```

---

## 💻 CLI Usage

### Run Source Code
```bash
# Interpreter mode (direct execution)
python cli/hambalang.py run examples/bytecode_demo.hl

# VM mode (compile → execute)
python cli/hambalang.py run examples/bytecode_demo.hl --vm
```

### Compile to Bytecode
```bash
python cli/hambalang.py compile examples/bytecode_demo.hl
# Output: bytecode_demo.hbc
```

### Run Bytecode
```bash
python cli/hambalang.py run examples/bytecode_demo.hbc
```

### Disassemble Bytecode
```bash
python cli/hambalang.py disasm examples/bytecode_demo.hbc
# Shows opcodes, constants, strings
```

### Interactive Debugger
```bash
python cli/hambalang.py debug examples/bytecode_demo.hl

# Debugger commands:
(hdb) step      # Execute one instruction
(hdb) stack     # Show stack contents
(hdb) vars      # Show variables
(hdb) state     # Full VM state
(hdb) run       # Run to completion
(hdb) quit      # Exit
```

### CTF Challenge Mode
```bash
python cli/hambalang.py ctf examples/challenge_vm.hl --seed 42
# Goal: Finish with anggaran == 0 AND progress >= 100
```

---

## 📘 Bytecode Format (.hbc)

### File Structure
```
Header:
  Magic:     "HBC\x00" (4 bytes)
  Version:   uint16 (2 bytes)
  
Code Section:
  Length:    uint32 (4 bytes)
  Code:      [opcodes...] (variable)
  
Constants Section:
  Count:     uint16 (2 bytes)
  Constants: [type + value] (variable)
  
Strings Section:
  Count:     uint16 (2 bytes)
  Strings:   [length + utf-8] (variable)
```

### Opcodes
```
Stack Operations:
  0x01  PUSH <const>       Push constant to stack
  0x02  POP                Pop top of stack
  0x03  LOAD <var>         Load variable to stack
  0x04  STORE <var>        Store stack top to variable

Arithmetic:
  0x20  ADD                Pop b, a; push a + b
  0x21  SUB                Pop b, a; push a - b
  0x22  MUL                Pop b, a; push a * b
  0x23  DIV                Pop b, a; push a / b
  0x24  MOD                Pop b, a; push a % b

Comparison:
  0x30  EQ                 Pop b, a; push a == b
  0x31  LT                 Pop b, a; push a < b
  0x32  GT                 Pop b, a; push a > b

Control Flow:
  0x40  JUMP <addr>        Unconditional jump
  0x41  JUMP_IF_FALSE <addr> Jump if stack top is false

IO:
  0x10  PRINT              Pop and print stack top

Satirical:
  0x60  KORUPSI            Corrupt budget (pop percent)
  0x61  MANGKRAK           Project fail with error
  0x62  RAPAT              Meeting loop

System:
  0xFF  END                Halt execution
```

---

## 🎯 VM Internals

### HambaVM State
```python
{
    'pc': int,              # Program counter
    'stack': List[Any],     # Value stack
    'variables': Dict,      # Variable storage
    'anggaran': int,        # Budget (satirical)
    'progress': int,        # Project progress
    'korupsi_total': int,   # Total corruption
    'step_count': int       # Execution steps
}
```

### Execution Model
1. Load bytecode from .hbc file
2. Initialize VM state (stack, variables, globals)
3. Execute instructions sequentially
4. Update program counter (PC)
5. Check step limit (anti-infinite loop)
6. Handle satirical effects (Korupsi, Mangkrak)
7. Terminate on OP_END or error

---

## 🌐 WASM Backend

### Features
- Browser-native execution (no Pyodide)
- Faster than Python interpreter
- Stack-based architecture matching VM
- Full opcode support

### Usage
```javascript
// Load WASM module
const wasm = new HambaWASM();
await wasm.init();

// Execute bytecode
const bytecode = [0x01, 0x05, 0x00, 0x10, 0xFF]; // PUSH 5, PRINT, END
const state = await wasm.executeBytecode(bytecode);

console.log('Output:', wasm.getOutput());
console.log('State:', state);
```

### Compile .wat → .wasm
```bash
# Using wabt tools
wat2wasm wasm/hamba_wasm.wat -o wasm/hamba_wasm.wasm

# Or use online tool: https://webassembly.github.io/wabt/demo/wat2wasm/
```

---

## 🎮 CTF Challenges

### Hidden Flags
1. **Perfect Budget Flag**
   - Condition: `anggaran == 0 AND progress >= 100`
   - Flag: `FLAG{H4MB4_VM_M4ST3R_PERFECT_BUDGET}`

2. **Number Theory Flag**
   - Condition: `korupsi_total % 424242 == 0 AND korupsi_total > 0`
   - Flag: `FLAG{K0RUPSI_NUMBER_TH30RY_42}`

### Obfuscation Features
- Deterministic RNG with seed
- Hidden bytecode behavior
- Execution step limit
- Satirical error messages
- Non-obvious winning conditions

---

## 🧪 Examples

### Bytecode Demo
```bash
python cli/hambalang.py run examples/bytecode_demo.hl --vm
```
Tests all opcodes: stack ops, arithmetic, control flow, loops, exceptions.

### CTF Challenge
```bash
python cli/hambalang.py ctf examples/challenge_vm.hl --seed 42
```
Solve the budget balancing puzzle to get the flag.

---

## 🔍 Debugging

### Trace Mode
```bash
python cli/hambalang.py run examples/bytecode_demo.hbc --debug
```
Shows each instruction execution:
```
[VM 0000] PUSH         | Stack: 0 | Anggaran: 100 | Progress: 0
[VM 0003] PRINT        | Stack: 1 | Anggaran: 100 | Progress: 0
```

### Disassembly
```bash
python cli/hambalang.py disasm examples/bytecode_demo.hbc
```
Output:
```
=== CONSTANTS ===
  #0: 10
  #1: 5

=== STRINGS ===
  @0: "Test string"

=== DISASSEMBLY ===
0000  PUSH #0
0003  STORE #1
0006  PRINT
0007  END
```

---

## 📊 Performance

| Mode | Speed | Use Case |
|------|-------|----------|
| Interpreter | Baseline | Development, debugging |
| VM (Python) | 1.5-2x faster | Production, CTF |
| WASM | 3-5x faster | Web, browser apps |

---

## 🛠️ Development

### Project Structure
```
hambalang/
├── cli/
│   └── hambalang.py           # Professional CLI tool
├── compiler/
│   └── bytecode.py            # Bytecode compiler
├── vm/
│   └── hamba_vm.py            # Virtual machine
├── wasm/
│   ├── hamba_wasm.wat         # WASM implementation
│   └── hamba_wasm_loader.js   # JS loader
├── interpreter/
│   └── hamba_advanced.py      # Original interpreter
├── examples/
│   ├── bytecode_demo.hl       # VM feature showcase
│   └── challenge_vm.hl        # CTF challenge
└── docs/
    └── VM_ARCHITECTURE.md     # This file
```

### Adding New Opcodes
1. Add opcode constant to `compiler/bytecode.py`
2. Implement compilation in `BytecodeCompiler._compile_node()`
3. Add execution in `HambaVM._execute_instruction()`
4. Update WASM implementation if needed
5. Add to `OPCODE_NAMES` for disassembly

---

## 🎓 Educational Value

HambaLang v3.0 demonstrates:
- **Compiler Design**: Lexing, parsing, AST, code generation
- **Virtual Machine**: Stack-based execution, instruction dispatch
- **Bytecode Format**: Binary serialization, constant pools
- **WASM**: Low-level compilation, browser integration
- **Tooling**: CLI design, debuggers, disassemblers
- **CTF Design**: Hidden flags, obfuscation, reverse engineering

Perfect for:
- Compiler course projects
- CTF challenges
- Language runtime learning
- Portfolio showcase
- Esoteric language enthusiasts

---

## 🚀 Future Enhancements

- [ ] JIT compilation (basic)
- [ ] Optimization passes
- [ ] Function calls with return values
- [ ] Garbage collection
- [ ] Profiler
- [ ] REPL mode
- [ ] IDE extension (syntax highlight, LSP)
- [ ] Package manager
- [ ] Standard library

---

## 📜 License

MIT License - See LICENSE file

---

## 👨‍💻 Author

**HambaLang Team**  
A satirical esoteric programming language about Indonesian bureaucracy.

---

## 🔗 Links

- GitHub: [hambalang-lang](https://github.com/yourusername/hambalang)
- Documentation: [docs/](docs/)
- Web Playground: [hambalang.dev](https://hambalang.dev)

---

**HambaLang v3.0** - Where bureaucracy meets bytecode! 🎭
