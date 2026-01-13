// HambaLang WASM Loader and Runtime
// Compiles .wat to .wasm and provides JS interface

class HambaWASM {
    constructor() {
        this.instance = null;
        this.memory = null;
        this.decoder = new TextDecoder();
        this.output = [];
    }

    async init() {
        // Load WASM module
        const response = await fetch('hamba_wasm.wasm');
        const buffer = await response.arrayBuffer();
        
        const imports = {
            env: {
                print_num: (val) => {
                    this.output.push(val.toString());
                },
                print_str: (ptr, len) => {
                    const bytes = new Uint8Array(this.memory.buffer, ptr, len);
                    this.output.push(this.decoder.decode(bytes));
                },
                korupsi_effect: (amount) => {
                    const satire = [
                        `🤝 Dana dialihkan untuk 'keperluan mendesak' (-${amount})`,
                        `💼 Budget optimization berhasil (-${amount})`,
                        `🎯 Efisiensi anggaran tercapai (-${amount})`
                    ];
                    this.output.push(satire[Math.floor(Math.random() * satire.length)]);
                }
            }
        };
        
        const result = await WebAssembly.instantiate(buffer, imports);
        this.instance = result.instance;
        this.memory = this.instance.exports.memory;
        
        return this;
    }

    reset() {
        this.output = [];
        this.instance.exports.reset();
    }

    executeOpcode(opcode, operand) {
        return this.instance.exports.execute_opcode(opcode, operand);
    }

    getState() {
        return {
            anggaran: this.instance.exports.get_anggaran(),
            progress: this.instance.exports.get_progress(),
            korupsi_total: this.instance.exports.get_korupsi_total(),
            stack_size: this.instance.exports.get_stack_size()
        };
    }

    getOutput() {
        return this.output.join('\n');
    }

    // Execute bytecode array
    async executeBytecode(bytecode) {
        this.reset();
        
        let pc = 0;
        while (pc < bytecode.length) {
            const opcode = bytecode[pc];
            let operand = 0;
            
            // Read operand for opcodes that need it
            if ([0x01, 0x03, 0x04, 0x40, 0x41, 0x50].includes(opcode)) {
                if (pc + 2 < bytecode.length) {
                    operand = bytecode[pc + 1] | (bytecode[pc + 2] << 8);
                    pc += 3;
                } else {
                    pc += 1;
                }
            } else {
                pc += 1;
            }
            
            const result = this.executeOpcode(opcode, operand);
            
            if (result === 0) {
                // OP_END
                break;
            } else if (result < 0) {
                throw new Error('Runtime error');
            }
        }
        
        return this.getState();
    }
}

// Compile .wat to .wasm using browser or Node.js
async function compileWAT(watSource) {
    // For browser: use wabt.js or server endpoint
    // For Node.js: use wabt npm package
    
    if (typeof window !== 'undefined') {
        // Browser: fetch pre-compiled .wasm
        // Or use wabt.js library
        return null;
    } else {
        // Node.js
        const wabt = require('wabt')();
        const wasmModule = wabt.parseWat('hamba_wasm.wat', watSource);
        const {buffer} = wasmModule.toBinary({});
        return buffer;
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {HambaWASM, compileWAT};
}
