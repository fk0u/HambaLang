# HambaLang Language Specification (Version 5.0)

**Last Updated:** January 13, 2026
**Author:** Chief Language Designer

## 1. Introduction

HambaLang is a satirically-themed, bytecode-compiled, stack-based programming language modeled after the bureaucratic processes of the Indonesian government. Despite its comedic exterior, HambaLang implements rigorous formal semantics, a deterministic execution model, and advanced anti-analysis features suitable for secure runtime environments.

### 1.1 Design Philosophy
- **Bureaucratic Realism**: Every operation incurs a cost (budget). Inefficiency is simulated but controlled.
- **Explicit Corruption**: Side effects (I/O) are modeled as "Korupsi" (Corruption) or "Wacana" (Discourse), treating data output as a leakage of state secrets.
- **Security through Obscurity**: The language runtime includes a "Hell Mode" designed to resist standard reverse engineering techniques, mimicking the opaque nature of illicit bureaucratic operations.

## 2. Execution Model

HambaLang programs undergo a multi-stage compilation and execution pipeline:
1.  **Lexical Analysis**: Source code `.hl` is tokenized.
2.  **Parsing**: Tokens are parsed into an Abstract Syntax Tree (AST).
3.  **Compilation**: AST is compiled into HambaBytecode (`.hbc`).
4.  **Verification**: Bytecode integrity and anti-tamper checks.
5.  **Virtual Machine**: The HambaVM executes the bytecode on a stack-based architecture.

### 2.1 The Global State ($\Sigma$)
The runtime state is defined as a tuple:
$$ \Sigma = \langle S, M, B, P \rangle $$
Where:
- $S$: The Operand Stack.
- $M$: The Memory Store (Variables/Scopes).
- $B$: The Budget (Gas limit).
- $P$: The Program Counter.

## 3. Memory Model

HambaLang uses a block-scoped memory model.

- **Storage**: Variables are stored in a specialized hash map called the "Anggaran" (Budget) storage.
- **Scoping**:
    - **Global Scope**: Accessible everywhere.
    - **Local Scope**: Created upon entering blocks (`Proyek`, procedures). Procedure calls push a new Call Frame onto the Call Stack.
- **Lifetime**: Variables exist from declaration (`Anggaran`) until the end of their scope.
- **Mutability**: All variables are mutable by default.

## 4. Type System

HambaLang employs a **Dynamic, Strong Type System**.

### 4.1 Primitive Types
| Type | Representation | Description |
|------|----------------|-------------|
| **Integer** | 64-bit Signed Int | Primary numeric type. Used for generic funds. |
| **Float** | 64-bit IEEE 754 | Used when precision is required (rarely used in corruption). |
| **String** | UTF-8 Sequence | Text data ("Janji Manis"). |
| **Boolean** | `BENAR` / `SALAH` | Logic flow control constants. |
| **Void** | `None` | Return type of procedures without explicit return. |

### 4.2 Type Rules
1.  **Strict Arithmetic**: Operations between mismatched types (e.g., String + Integer) raise a `TypeError` (represented as `KesalahanBirokrasi`).
2.  **Implicit Truthiness**:
    - Integer `0`, Empty String `""`, and `SALAH` evaluates to `False`.
    - All other values evaluate to `True`.

## 5. Control Flow & Termination

### 5.1 Determinism
The standard HambaLang execution is deterministic. Given the same input and initial seed, the budget consumption and output sequence are identical.

### 5.2 Termination Checks
To prevent infinite loops (infinite bureaucracy), HambaLang enforces a **Budget System**:
- The generic variable `MAX_ANGGARAN` typically sets a step limit (e.g., 100,000 ops).
- Loops (`Proyek`) consume budget per iteration.
- If $B \le 0$, the VM initiates a `BangkrutException`, terminating execution immediately.

### 5.3 Error Semantics
Errors ("Mangkrak") halt execution effectively.
- **Syntax Error**: "SalahKetike"
- **Runtime Error**: "OperasiIlegal"
- **Budget Error**: "NegaraBangkrut"

## 6. Concurrency
HambaLang is single-threaded. Concurrency is considered "Overlapping Projects" and is currently prohibited by regulation (Phase 5 Spec). Future extensions may add "TenagaAhli" (Green Threads).
