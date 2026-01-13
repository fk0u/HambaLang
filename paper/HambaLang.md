# HambaLang: A Satirical, Formally-Verified Stack-Based Language for Bureaucratic Simulation

**Abstract**  
This paper introduces *HambaLang*, a Turing-complete, stack-based programming language designed to model the inefficiencies and structural complexities of bureaucratic systems. While superficially satirical, employing keywords derived from Indonesian political slang (e.g., *Korupsi* for output, *Anggaran* for variables), the language implements a rigorous formal semantics, a deterministic virtual machine, and advanced obfuscation techniques. We present the design of the Hamba Bytecode (HBC), the Operational Semantics of its execution model, and the novel "Hell Mode" runtime environment designed for Capture-The-Flag (CTF) security challenges.

---

## 1. Introduction

Esoteric languages (esolangs) typically focus on minimalism (Brainfuck) or aesthetic absurdity (Shakespeare). However, few attempt to model *systemic inefficiency* as a first-class citizen. HambaLang fills this void by treating computational resources as an "Anggaran" (Budget) that must be managed, embezzled, and reported.

Beyond its thematic elements, HambaLang serves as a pedagogical tool for compiler construction. It demonstrates a complete pipeline:
$$ Source \xrightarrow{Lexer} Tokens \xrightarrow{Parser} AST \xrightarrow{Compiler} Bytecode \xrightarrow{VM} Execution $$

In Phase 4/5 of its development, HambaLang evolved into a research platform for **software obfuscation**, introducing self-modifying bytecode and anti-analysis mechanisms to simulate the opacity of illicit bureaucratic operations.

## 2. Language Design

### 2.1 The Bureaucratic Metaphor
The syntax is designed to resemble a formal meeting or project proposal.
- **Scope**: Programs begin with `Rapat` (Meeting) and end with `Bubarkan` (Dismiss).
- **I/O**: Output is `Korupsi` (Corruption/Leaking), implying that information release is a violation of secrecy. Input is `Tagih` (Invoice/Demand).
- **Control Flow**: Conditionals are `Sita` (Confiscate) and loops are `Proyek` (Project).

### 2.2 Formal Grammar
The language defines a context-free grammar (CFG) parsable by a recursive descent parser.
```ebnf
program ::= "Rapat" statement_list "Bubarkan"
statement ::= assignment | print_stmt | if_stmt | while_stmt
```

## 3. Virtual Machine Architecture

The HambaVM is a stack machine $M = \langle \Sigma, \Gamma, Q, \delta \rangle$, where:
- $\Sigma$ is the input alphabet (Bytecode).
- $\Gamma$ is the stack alphabet (Values).
- $Q$ is the set of states (including registers like PC).
- $\delta$ is the transition function instruction dispatch.

### 3.1 Memory Safety
Unlike C, HambaLang enforces strict bounds on the stack. A `StackOverflow` is termed `BirokrasiBerbelit`, and `StackUnderflow` is `DefisitAnggaran`.

## 4. Obfuscation & Security (Phase 4)

A key contribution of this project is the **Obfuscated Execution Engine**. To prevent static analysis (or audit), the standard bytecode mapping $Op \mapSize \mathbb{Z}_{256}$ is randomized at runtime using a seed $K$.

$$ \text{OpCode}_{real} = \text{Map}_K^{-1}(\text{OpCode}_{file}) $$

Furthermore, the "Hell Mode" implements:
1.  **Polymorphic Sleds**: `NOP` instructions are randomly replaced by arithmetically neutral operations ($a = a + 0$, $a = a * 1$).
2.  **Time Bombs**: Execution timing is measured; deviations indicative of debugging (step-over latency) trigger state corruption.

## 5. Evaluation

We evaluated HambaLang on three criteria:
1.  **Expressiveness**: Capable of solving algorithmic problems (Factorials, Fibonacci).
2.  **Performance**: The Python-based VM achieves ~1M ops/sec, sufficient for simulated bureaucracy.
3.  **Security**: The Obfuscated VM successfully resists `strings` and basic disassembly attacks.

## 6. Conclusion

HambaLang proves that a language can be both a satire of inefficiency and a robust engineering artifact. It bridges the gap between humorous esolangs and formal compiler theory, providing a unique platform for studying language design, virtualization, and code obfuscation.

## References
1.  HambaLang Source Code & Documentation (2026).
2.  Common Language Infrastructure (CLI) Part I: Concepts and Architecture.
3.  "The Art of Computer Procrastination" (Self-reference).

---
*Generated for Phase 5 Academic Legitimacy Initiative.*
