# 12-Week Roadmap: Silicon Hardware Security Engineer & Thesis Prep

---

## Month 1: Foundation (C/C++ Mastery, SystemVerilog & RISC-V)

### Weeks 1–2: Advanced C & C++ for Low-Level Systems
- [ ] **Bitwise & Bit Manipulation:** Masking, bit shifts, clearing/toggling bits, Little- vs Big-Endian parsing.
- [ ] **Memory Management:** Raw pointers, double pointers, function pointers, pointer arithmetic, memory alignment, and struct padding.
- [ ] **Low-Level Keywords & Storage:** `volatile` (hardware registers/MMIO), `const`, `static`, `inline`, `register`.
- [ ] **C++ Concurrency & RAII:** RAII idiom, `std::atomic`, smart pointers (`unique_ptr`, `shared_ptr`), mutexes, lock-free basics.
- [ ] **Practical Task:** Implement a custom fixed-block memory allocator and a register-level bit-manipulation utility in C with zero warnings (`-Wall -Wextra -Werror`).

### Weeks 3–4: SystemVerilog RTL & RISC-V Bare-Metal
- [ ] **SystemVerilog Basics:** Modules, combinational vs sequential logic (`always_comb`, `always_ff`), blocking (`=`) vs non-blocking (`<=`).
- [ ] **FSM Design:** Moore and Mealy Finite State Machines, reset logic, clock gating concepts.
- [ ] **Simulation Toolchain:** Install `Verilator` (C++ based testbench) and `GTKWave` on Linux.
- [ ] **RISC-V Architecture (RV32I):** Instruction formats, privilege modes, CSR registers, memory-mapped I/O (MMIO).
- [ ] **Bus Protocols:** AXI4-Lite and TileLink basics (valid/ready handshake).
- [ ] **Practical Task:** Clone the **lowRISC Ibex** core. Design a simple hardware peripheral in SystemVerilog, map it to an MMIO address, write a C driver to read/write to its registers in a Verilator simulation.

---

## Month 2: Post-Quantum Cryptography (PQC) & Hardware Accelerators

### Weeks 5–6: Lattice-Based Cryptography & Algorithms
- [ ] **Theoretical Foundations:** Understand Module Learning with Errors (M-LWE) and Module Short Integer Solution (M-SIS).
- [ ] **NIST Standards:** Study specifications for **ML-KEM** (Kyber) and **ML-DSA** (Dilithium).
- [ ] **NTT Mathematics:** Number Theoretic Transform (NTT), polynomial multiplication over rings, Cooley-Tukey butterfly operations, modular reduction (Montgomery, Barrett).
- [ ] **Reading:**
  - NIST FIPS 203 (ML-KEM) and FIPS 204 (ML-DSA) specifications.
  - *CRYSTALS-Kyber: a CCA-secure module-lattice-based KEM* (Schwabe et al.).
- [ ] **Practical Task:** Write a reference implementation of the NTT forward and inverse transforms in C/C++ and verify correctness against reference vectors.

### Weeks 7–8: Designing the NTT Accelerator in SystemVerilog
- [ ] **Memory Architecture:** Dual-port BRAM organization, conflict-free memory access patterns for NTT stages.
- [ ] **Datapath Design:** Pipelined modular multiplier, adder/subtractor, butterfly unit (BFU).
- [ ] **Control Logic:** Address generation unit (AGU) for bit-reversal and stage progression.
- [ ] **Practical Task:** Write the SystemVerilog RTL for a single-butterfly NTT calculation unit. Verify output cycles and precision against your C model using a C++ Verilator testbench.

---

## Month 3: Physical Attacks (SCA/FI), Defenses & Thesis Proposal

### Weeks 9–10: Physical Attacks (Side-Channel & Fault Injection)
- [ ] **Side-Channel Analysis (SCA):**
  - Timing attacks: Constant-time coding rules in C/assembly and RTL execution invariance.
  - Power & EM analysis: Simple Power Analysis (SPA) vs Differential Power Analysis (DPA).
- [ ] **Fault Injection (FI):**
  - Attack vectors: Clock glitching, voltage manipulation, laser/electromagnetic pulses.
  - Target vulnerabilities: Instruction skipping, control-flow hijacking, loop-counter manipulation, faulty NTT outputs.
- [ ] **Reading:**
  - *Side-Channel Attacks on Post-Quantum Cryptography: A Comprehensive Survey*.
  - *Fault Injection Attacks on Lattice-Based Schemes: Survey and Challenges*.
  - Documentation from the open-source **ChipWhisperer** project.
- [ ] **Practical Task:** Write a C program showing a timing vulnerability and its constant-time remediation. Simulate an instruction-skip/bit-flip in your NTT Verilator testbench to observe cryptographic state leakage.

### Weeks 11–12: Hardware Countermeasures & Final Integration
- [ ] **Silicon Defenses:**
  - Temporal and spatial redundancy (Dual-modular redundancy).
  - Parity/checksum verification pipelines inside NTT modules.
  - Zeroization: Secure state flush and register clearing upon fault detection.
  - OpenTitan Root of Trust (RoT) architecture principles.
- [ ] **Integration Project (Thesis MVP & Portfolio Anchor):**
  - Integrate the protected NTT accelerator with a RISC-V Ibex core over AXI-Lite.
  - Write bare-metal C firmware orchestrating key operations.
  - Implement a fault-detection circuit in RTL that asserts an alert, halts computation, and wipes sensitive registers when an injection is detected.
- [ ] **Final Deliverables:**
  - Public GitHub repository: Documented RTL, C firmware, C++ Verilator testbenches, and automated test suite.
  - 1-Page Academic Thesis Proposal: Problem statement, threat model, proposed fault-tolerant architecture, and simulation results.
