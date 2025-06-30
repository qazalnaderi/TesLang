# TesLang Compiler Project

A three-phase academic compiler project for a custom language called **TesLang**, implemented using Python and PLY.  
The final output runs on the [tsvm virtual machine](https://github.com/aligrudi/tsvm).

---

## 📌 Phases Overview

### 🔹 Phase 1: Lexical Analysis  
- Defined tokens (keywords, identifiers, numbers, symbols)  
- Implemented with `PLY.lex`

### 🔹 Phase 2: Parsing & Semantic Analysis  
- Wrote full TesLang grammar with `PLY.yacc`  
- Built AST nodes  
- Performed semantic checks (e.g. undeclared variables, type checks)

### 🔹 Phase 3: Intermediate Code Generation  
- Generated tsvm-compatible intermediate code  
- Implemented register allocation & function call handling  
- Mapped built-ins:  
  - `scan()` → `call iget, rX`  
  - `print(x)` → `call iput, rX`  
- Final code runs directly on `tsvm`

---

## ▶️ How to Run

1. Compile [`tsvm.c`](https://github.com/aligrudi/tsvm) (use GCC or Dev-C++)
2. Generate TesLang code (e.g., `main.tes`)
3. Run Python compiler to produce `output.ts`
4. Run on tsvm:

```bash
python main.py
```
#📂 Project Structure
Lexer/ → token definitions

Parser/ → grammar + AST builder

SemanticAnalyzer/ → semantic checks

CodeGenerator/ → IR code generation

output.ts → final intermediate code

tsvm.c → virtual machine to run output

#👨‍💻 Authors & Thanks
Developed by me, with massive help from:

🤖 ChatGPT — for logic checks, refactors, and moral support

🤖 Claude — for thoughtful suggestions and occasional brilliant catches

🧠 Myself — for the late-night debugging and edge-case nightmares

