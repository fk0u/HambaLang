;; HambaLang WASM Runtime (Basic Implementation)
;; Executes HambaLang bytecode in WebAssembly
;; Target: Faster than Pyodide, browser-native execution

(module
  ;; Memory for stack and variables
  (memory (export "memory") 10)
  
  ;; Global state
  (global $stack_ptr (mut i32) (i32.const 0))
  (global $anggaran (mut i32) (i32.const 100))
  (global $progress (mut i32) (i32.const 0))
  (global $korupsi_total (mut i32) (i32.const 0))
  (global $pc (mut i32) (i32.const 0))
  
  ;; Import console functions from JS
  (import "env" "print_num" (func $print_num (param i32)))
  (import "env" "print_str" (func $print_str (param i32) (param i32)))
  (import "env" "korupsi_effect" (func $korupsi_effect (param i32)))
  
  ;; Stack operations
  (func $push (param $val i32)
    (i32.store 
      (global.get $stack_ptr)
      (local.get $val))
    (global.set $stack_ptr 
      (i32.add (global.get $stack_ptr) (i32.const 4)))
  )
  
  (func $pop (result i32)
    (global.set $stack_ptr 
      (i32.sub (global.get $stack_ptr) (i32.const 4)))
    (i32.load (global.get $stack_ptr))
  )
  
  (func $peek (result i32)
    (i32.load 
      (i32.sub (global.get $stack_ptr) (i32.const 4)))
  )
  
  ;; Bytecode execution
  (func (export "execute_opcode") (param $opcode i32) (param $operand i32) (result i32)
    (local $a i32)
    (local $b i32)
    (local $amount i32)
    
    ;; OP_PUSH (0x01)
    (if (i32.eq (local.get $opcode) (i32.const 0x01))
      (then
        (call $push (local.get $operand))
        (return (i32.const 1))
      )
    )
    
    ;; OP_POP (0x02)
    (if (i32.eq (local.get $opcode) (i32.const 0x02))
      (then
        (drop (call $pop))
        (return (i32.const 1))
      )
    )
    
    ;; OP_PRINT (0x10)
    (if (i32.eq (local.get $opcode) (i32.const 0x10))
      (then
        (call $print_num (call $pop))
        (return (i32.const 1))
      )
    )
    
    ;; OP_ADD (0x20)
    (if (i32.eq (local.get $opcode) (i32.const 0x20))
      (then
        (local.set $b (call $pop))
        (local.set $a (call $pop))
        (call $push (i32.add (local.get $a) (local.get $b)))
        (return (i32.const 1))
      )
    )
    
    ;; OP_SUB (0x21)
    (if (i32.eq (local.get $opcode) (i32.const 0x21))
      (then
        (local.set $b (call $pop))
        (local.set $a (call $pop))
        (call $push (i32.sub (local.get $a) (local.get $b)))
        (return (i32.const 1))
      )
    )
    
    ;; OP_MUL (0x22)
    (if (i32.eq (local.get $opcode) (i32.const 0x22))
      (then
        (local.set $b (call $pop))
        (local.set $a (call $pop))
        (call $push (i32.mul (local.get $a) (local.get $b)))
        (return (i32.const 1))
      )
    )
    
    ;; OP_DIV (0x23)
    (if (i32.eq (local.get $opcode) (i32.const 0x23))
      (then
        (local.set $b (call $pop))
        (local.set $a (call $pop))
        (if (i32.eqz (local.get $b))
          (then (return (i32.const -1)))  ;; Division by zero error
        )
        (call $push (i32.div_s (local.get $a) (local.get $b)))
        (return (i32.const 1))
      )
    )
    
    ;; OP_LT (0x31)
    (if (i32.eq (local.get $opcode) (i32.const 0x31))
      (then
        (local.set $b (call $pop))
        (local.set $a (call $pop))
        (call $push 
          (if (result i32) (i32.lt_s (local.get $a) (local.get $b))
            (then (i32.const 1))
            (else (i32.const 0))
          )
        )
        (return (i32.const 1))
      )
    )
    
    ;; OP_KORUPSI (0x60)
    (if (i32.eq (local.get $opcode) (i32.const 0x60))
      (then
        (local.set $a (call $pop))  ;; percent
        (local.set $amount 
          (i32.div_s 
            (i32.mul (global.get $anggaran) (local.get $a))
            (i32.const 100)
          )
        )
        (global.set $anggaran 
          (i32.sub (global.get $anggaran) (local.get $amount))
        )
        (global.set $korupsi_total
          (i32.add (global.get $korupsi_total) (local.get $amount))
        )
        (call $korupsi_effect (local.get $amount))
        (return (i32.const 1))
      )
    )
    
    ;; OP_END (0xFF)
    (if (i32.eq (local.get $opcode) (i32.const 0xFF))
      (then (return (i32.const 0)))
    )
    
    ;; Unknown opcode
    (return (i32.const 1))
  )
  
  ;; Getters for state inspection
  (func (export "get_anggaran") (result i32)
    (global.get $anggaran)
  )
  
  (func (export "get_progress") (result i32)
    (global.get $progress)
  )
  
  (func (export "get_korupsi_total") (result i32)
    (global.get $korupsi_total)
  )
  
  (func (export "get_stack_size") (result i32)
    (i32.div_u (global.get $stack_ptr) (i32.const 4))
  )
  
  (func (export "set_anggaran") (param $val i32)
    (global.set $anggaran (local.get $val))
  )
  
  (func (export "set_progress") (param $val i32)
    (global.set $progress (local.get $val))
  )
  
  ;; Reset VM state
  (func (export "reset")
    (global.set $stack_ptr (i32.const 0))
    (global.set $anggaran (i32.const 100))
    (global.set $progress (i32.const 0))
    (global.set $korupsi_total (i32.const 0))
    (global.set $pc (i32.const 0))
  )
)
