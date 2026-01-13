# Hamba Virtual Machine (HambaVM) Specification

## 1. Overview
The HambaVM is a deterministic, stack-based virtual machine designed to execute Hamba Bytecode (`.hbc`). It features a separated operand stack and call stack, with built-in protections against reverse engineering (in Phase 4+).

**Architecture**: Stack Machine
**Word Size**: 64-bit
**Endianness**: Little-endian
**File Magic**: `\xDE\xAD\xBE\xEF` (standard) or `\xCA\xFE\xBA\xBE` (obfuscated)

## 2. Bytecode Format

A `.hbc` file consists of:

| Component | Size (Bytes) | Description |
|-----------|--------------|-------------|
| **Header** | 4 | Magic Number |
| **Version** | 4 | VM Version (e.g., 4.0) |
| **Timestamp**| 8 | Compilation Time |
| **Flags** | 4 | Bitmask (0x1: Obfuscated, 0x2: HellMode) |
| **Const Pool** | Variable | Serialized list of constants |
| **Code** | Variable | Sequence of instructions |

## 3. Instruction Set Architecture (ISA)

The current HambaVM implements ~30 opcodes. Opcodes are 1 byte. Arguments are variable length (typically 2-4 bytes).

### 3.1 Stack Manipulation
| Opcode | Mnemonic | Arg | Description |
|--------|----------|-----|-------------|
| 0x01 | `LOAD_CONST` | index | Pushes `ConstPool[index]` to stack. |
| 0x02 | `LOAD_VAR` | name_id | Pushes value of variable `name` to stack. |
| 0x03 | `STORE_VAR` | name_id | Pops value and stores in variable `name`. |
| 0x04 | `POP` | - | Discards top of stack. |

### 3.2 Arithmetic & Logic
| Opcode | Mnemonic | Arg | Description |
|--------|----------|-----|-------------|
| 0x10 | `ADD` | - | `b = pop, a = pop, push(a + b)` |
| 0x11 | `SUB` | - | `b = pop, a = pop, push(a - b)` |
| 0x12 | `MUL` | - | `b = pop, a = pop, push(a * b)` |
| 0x13 | `DIV` | - | `b = pop, a = pop, push(a / b)` |
| 0x14 | `MOD` | - | `b = pop, a = pop, push(a % b)` |
| 0x15 | `EQ` | - | `push(a == b)` |
| 0x16 | `NEQ` | - | `push(a != b)` |
| 0x17 | `GT` | - | `push(a > b)` |
| 0x18 | `LT` | - | `push(a < b)` |

### 3.3 Control Flow
| Opcode | Mnemonic | Arg | Description |
|--------|----------|-----|-------------|
| 0x30 | `JUMP` | offset | Relative jump by `offset`. |
| 0x31 | `JUMP_IF_FALSE` | offset | Pop `cond`. If false, jump by `offset`. True falls through. |
| 0x32 | `CALL` | name_id | Call procedure `name`. Pushes return address. |
| 0x33 | `RETURN` | - | Pop current stack frame, return to caller. |
| 0x3F | `EXIT` | - | Stop execution. |

### 3.4 I/O & System
| Opcode | Mnemonic | Arg | Description |
|--------|----------|-----|-------------|
| 0x40 | `PRINT` | - | Pop and print to stdout (`Korupsi`). |
| 0x41 | `INPUT` | - | Read stdin to stack (`Tagih`). |
| 0x50 | `DEBUG` | - | Dump stack state (Disabled in Hell Mode). |

### 3.5 Obfuscation Specials (Phase 4)
| Opcode | Mnemonic | Arg | Description |
|--------|----------|-----|-------------|
| 0x90 | `OBF_NOP` | - | No operation (NOP Sled). |
| 0x91 | `OBF_SWAP` | - | Swap top 2 stack items (Polymorphic junk). |
| 0x92 | `OBF_JUNK` | - | Non-functional math op (Entropy generation). |
| 0xFE | `HELL_CHECK` | - | Validate CTF flag stage. |

## 4. Stack Frame Structure

```text
+------------------+
| Return Address   |
+------------------+
| Local Variables  | Map<String, Value>
+------------------+
| Operand Stack    | List<Value>
+------------------+
```

## 5. Security Invariants (Phase 5)

1.  **Stack Balance**: A basic block must result in a net stack change of 0 unless it consumes/produces values for the next block. (Verified by formal analysis in strict mode).
2.  **Budget Monotonicity**: The remaining budget $B$ must strictly decrease with every instruction executed.
3.  **Address Bounds**: All `JUMP` targets must strictly fall within the bytecode segment $[0, \text{len}(code))$.

## 6. Error Handling

When the VM traps (e.g., Stack Underflow):
1.  Execution is halted.
2.  IP (Instruction Pointer) is logged.
3.  "Mangkrak" state is returned.
