# 🏗️ HambaLang v3.0 - VM & Bytecode Edition

**Professional Esoteric Programming Language with Custom Runtime**

HambaLang telah berkembang dari meme interpreter menjadi **custom language runtime** yang lengkap dengan bytecode compiler, virtual machine, dan WASM backend. Perfect untuk portfolio, CTF challenges, dan pembelajaran compiler design.

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-yellow)

---

## 🌟 What's New in v3.0?

### 🚀 Professional Runtime Architecture

**Bytecode Compiler:**
- ✅ Compile `.hl` source to `.hbc` bytecode
- ✅ Binary format with constants pool
- ✅ Optimized instruction encoding
- ✅ Deterministic compilation

**Virtual Machine:**
- ✅ Stack-based execution model
- ✅ 20+ opcodes (arithmetic, control flow, I/O)
- ✅ Step execution & debugging
- ✅ Execution budget (anti-abuse)
- ✅ Satirical runtime effects

**WASM Backend:**
- ✅ Browser-native execution
- ✅ 3-5x faster than Python VM
- ✅ No Pyodide dependency
- ✅ WebAssembly Text format (.wat)

**Professional Tooling:**
- ✅ CLI with colored output
- ✅ Interactive debugger
- ✅ Bytecode disassembler
- ✅ CTF challenge mode
- ✅ Error reporting with line numbers

---

## 📦 Architecture

```
.hl source → Parser → AST → Bytecode Compiler → .hbc
                                                   ↓
                                   ┌───────────────┴────────────┐
                                   ▼                            ▼
                              HambaVM (Python)           WASM Runtime
```

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/yourusername/hambalang.git
cd hambalang

# No dependencies! Pure Python + WASM
# Optional: Compile WASM
wat2wasm wasm/hamba_wasm.wat -o wasm/hamba_wasm.wasm
```

### Hello HambaVM

```hl
// hello_vm.hl
lapor "🚀 Hello from HambaVM!"

mulai
    set x = 42
    set y = 58
    set result = x + y
    lapor "42 + 58 = " + result
    
    jika result == 100
        lapor "✅ Perfect computation!"
    akhir
akhir
```

**Run with Interpreter:**
```bash
python cli/hambalang.py run hello_vm.hl
```

**Compile & Run on VM:**
```bash
python cli/hambalang.py compile hello_vm.hl
python cli/hambalang.py run hello_vm.hbc
```

**Debug Mode:**
```bash
python cli/hambalang.py debug hello_vm.hl
```

---

## 💻 CLI Usage

### Available Commands

```bash
# Run source (interpreter mode)
python cli/hambalang.py run demo.hl

# Run with VM (compile first)
python cli/hambalang.py run demo.hl --vm

# Compile to bytecode
python cli/hambalang.py compile demo.hl

# Run bytecode
python cli/hambalang.py run demo.hbc

# Disassemble bytecode
python cli/hambalang.py disasm demo.hbc

# Interactive debugger
python cli/hambalang.py debug demo.hl

# CTF challenge mode
python cli/hambalang.py ctf challenge.hl --seed 42
```

### Flags

- `--vm` - Use virtual machine execution
- `--debug` - Enable execution tracing
- `--seed N` - Set random seed (deterministic)
- `--ctf` - CTF mode with hidden flags
- `--step-limit N` - Max execution steps
- `--delay N` - Delay between steps (seconds)

---

## 📘 Bytecode Format

### Opcodes

```
Stack:      PUSH, POP, LOAD, STORE
Arithmetic: ADD, SUB, MUL, DIV, MOD
Compare:    EQ, LT, GT
Control:    JUMP, JUMP_IF_FALSE
I/O:        PRINT
Satirical:  KORUPSI, MANGKRAK, RAPAT
System:     END
```

### Example Disassembly

```
=== CONSTANTS ===
  #0: 10
  #1: 5

=== STRINGS ===
  @0: "Hello"

=== DISASSEMBLY ===
0000  PUSH #0          // Push 10
0003  STORE #1         // x = 10
0006  PUSH #1          // Push 5
0009  LOAD #1          // Load x
0012  ADD              // x + 5
0013  PRINT            // Output
0014  END
```

---

## 🎯 Interactive Debugger

```bash
python cli/hambalang.py debug examples/bytecode_demo.hl

(hdb) step          # Execute one instruction
(hdb) stack         # Show stack
(hdb) vars          # Show variables
(hdb) state         # Full VM state
(hdb) run           # Run to completion
(hdb) quit          # Exit
```

---

## 🎮 CTF Challenges

### Hidden Flags

**Flag 1: Perfect Budget**
```
Condition: anggaran == 0 AND progress >= 100
Flag: FLAG{H4MB4_VM_M4ST3R_PERFECT_BUDGET}
```

**Flag 2: Number Theory**
```
Condition: korupsi_total % 424242 == 0
Flag: FLAG{K0RUPSI_NUMBER_TH30RY_42}
```

### Run Challenge

```bash
python cli/hambalang.py ctf examples/challenge_vm.hl --seed 42
```

Goal: Balance budget perfectly to unlock the flag!

---

## 🌐 WASM Backend

### Compile & Run

```bash
# Compile .wat to .wasm
wat2wasm wasm/hamba_wasm.wat -o wasm/hamba_wasm.wasm

# Use in browser
<script src="hamba_wasm_loader.js"></script>
<script>
  const wasm = new HambaWASM();
  await wasm.init();
  const bytecode = [...]; // Your bytecode
  const state = await wasm.executeBytecode(bytecode);
</script>
```

### Performance

| Mode | Speed | Use Case |
|------|-------|----------|
| Interpreter | 1x | Development |
| Python VM | 1.5-2x | Production |
| WASM | 3-5x | Web apps |

---

## 📚 Documentation

- **[VM Architecture](docs/VM_ARCHITECTURE.md)** - Deep dive into bytecode & VM
- **[Language Reference](docs/ADVANCED.md)** - Phase 2 language features
- **[Examples](examples/)** - Sample programs

---

## 🛠️ Project Structure

```
hambalang/
├── cli/
│   └── hambalang.py           # Professional CLI
├── compiler/
│   └── bytecode.py            # Bytecode compiler
├── vm/
│   └── hamba_vm.py            # Virtual machine
├── wasm/
│   ├── hamba_wasm.wat         # WASM implementation
│   └── hamba_wasm_loader.js   # JS loader
├── interpreter/
│   ├── hamba_v2.py            # v2.0 full language
│   └── hamba_advanced.py      # v3.0 advanced features
├── examples/
│   ├── bytecode_demo.hl       # VM showcase
│   ├── challenge_vm.hl        # CTF challenge
│   └── advanced_*.hl          # Advanced features
└── docs/
    └── VM_ARCHITECTURE.md     # Technical docs
```

---

## 🎓 Educational Value

Learn by building:
- ✅ Lexer & Parser implementation
- ✅ AST design patterns
- ✅ Bytecode compilation
- ✅ Stack-based VM execution
- ✅ Binary file formats
- ✅ WASM integration
- ✅ CLI tool design
- ✅ Interactive debuggers
- ✅ CTF challenge creation

Perfect for:
- Compiler design courses
- CTF challenges
- Portfolio projects
- Language enthusiasts

---

## 📊 Version History

**v3.0 (Current)** - VM & Bytecode
- Bytecode compiler & virtual machine
- WASM backend
- Professional CLI tooling
- Interactive debugger
- CTF-grade features

**v2.0** - Full Language
- Complete programming language
- Database & HTTP support
- File I/O
- Web playground

**v1.0** - Meme Interpreter
- Basic satirical interpreter
- Mangkrak, Korupsi, Rapat

---

## 🚀 Future Roadmap

- [ ] JIT compilation
- [ ] Optimization passes
- [ ] Garbage collection
- [ ] LSP server for IDE support
- [ ] Package manager
- [ ] Standard library
- [ ] REPL mode
- [ ] Profiler

---

## 🤝 Contributing

Contributions welcome! Areas:
- Optimizer implementation
- More opcodes
- WASM optimizations
- CTF challenges
- Documentation

---

## 📜 License

MIT License - See LICENSE file

---

## 👨‍💻 Author

**HambaLang Team**

Where Indonesian bureaucracy satire meets serious compiler engineering! 🎭

---

## 🔗 Quick Links

- 📖 [Full Documentation](docs/VM_ARCHITECTURE.md)
- 🎯 [CTF Challenges](examples/challenge_vm.hl)
- 🚀 [Getting Started](#quick-start)
- 💻 [CLI Reference](#cli-usage)

---

**HambaLang v3.0** - From satire to bytecode! 🚀
