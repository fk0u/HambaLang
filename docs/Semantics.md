# Operational Semantics of HambaLang

This document defines the formal operational semantics of HambaLang using **Structural Operational Semantics (SOS)** / Small-step semantics style.

**Notation**:
- $\sigma$: The runtime environment (variable store).
- $s$: The operand stack.
- $pc$: Program counter.
- $\langle \text{Cmd}, \sigma, s \rangle \to \langle \sigma', s' \rangle$: Transition relation.

## 1. Expressions

Evaluation of expressions pushes results onto the stack.

$$
\frac{\langle E_1, \sigma, s \rangle \to \langle \sigma, s, v_1 \rangle \quad \langle E_2, \sigma, s, v_1 \rangle \to \langle \sigma, s, v_1, v_2 \rangle}
{\langle E_1 + E_2, \sigma, s \rangle \to \langle \sigma, s, v_1 + v_2 \rangle}
$$

### Literals
$$ \langle n \in \mathbb{Z}, \sigma, s \rangle \to \langle \sigma, s :: n \rangle $$

### Variable Access
$$ \frac{id \in \text{dom}(\sigma)}{\langle id, \sigma, s \rangle \to \langle \sigma, s :: \sigma(id) \rangle} $$

## 2. Statements

### Assignment (Anggaran)
Variable assignment updates the store $\sigma$.

$$
\frac{\langle E, \sigma, s \rangle \to \langle \sigma, s :: v \rangle}
{\langle id = E, \sigma, s \rangle \to \langle \sigma[id \mapsto v], s \rangle}
$$

### Printing (Korupsi)
Modeling explicit side effects as an append to the output stream $\mathcal{O}$.

$$
\frac{\langle E, \sigma, s \rangle \to \langle \sigma, s :: v \rangle}
{\langle \text{Korupsi}(E), \sigma, s, \mathcal{O} \rangle \to \langle \sigma, s, \mathcal{O} :: v \rangle}
$$

### Conditional (Sita)

**True Condition:**
$$
\frac{\langle E, \sigma, s \rangle \to \langle \sigma, s :: \text{true} \rangle}
{\langle \text{Sita } E \{ C_1 \} \text{ Pengadilan } \{ C_2 \}, \sigma, s \rangle \to \langle C_1, \sigma, s \rangle}
$$

**False Condition:**
$$
\frac{\langle E, \sigma, s \rangle \to \langle \sigma, s :: \text{false} \rangle}
{\langle \text{Sita } E \{ C_1 \} \text{ Pengadilan } \{ C_2 \}, \sigma, s \rangle \to \langle C_2, \sigma, s \rangle}
$$

### Loops (Proyek)

$$
\frac{\langle E, \sigma, s \rangle \to \langle \sigma, s :: \text{false} \rangle}
{\langle \text{Proyek } E \{ C \}, \sigma, s \rangle \to \langle \text{skip}, \sigma, s \rangle}
$$

$$
\frac{\langle E, \sigma, s \rangle \to \langle \sigma, s :: \text{true} \rangle}
{\langle \text{Proyek } E \{ C \}, \sigma, s \rangle \to \langle C; \text{Proyek } E \{ C \}, \sigma, s \rangle}
$$

## 3. Budget Consumption (Cost Model)

Every transition consumes a budget unit $B$.

$$
\langle \text{op}, \sigma, s, B \rangle \to \langle \sigma', s', B - Cost(\text{op}) \rangle
$$

If $B < Cost(\text{op})$, the transition is:
$$
\langle \text{op}, \sigma, s, B \rangle \to \text{Abort(Bangkrut)}
$$

## 4. Obfuscation Semantics (Phase 4)

In the Obfuscated VM, the mapping of opcodes is a function of a seed key $K$.
Let $\mathcal{D}$ be the Decoder function.

$$
\text{Fetch}(pc) \xrightarrow{\mathcal{D}(K)} \text{Opcode}_{real}
$$

This ensures that static analysis without knowledge of $K$ (derived from runtime checks or flags) cannot construct the Control Flow Graph (CFG).
