"""
front_matter.py - Cover page, Roadmap, and Table of Contents
"""

def get_front_matter_html():
    return r"""
<!-- COVER PAGE -->
<div class="cover-page">
    <div>
        <div class="cover-badge">Master Engineering Reference & Curriculum Guide</div>
        <h1 class="cover-title">SILICON HARDWARE SECURITY ENGINEERING</h1>
        <p class="cover-subtitle">
            The Definitive C++20 Low-Level Systems and Hardware Architecture Guide:
            From Bit-Twiddling and Memory Models to ARM64/RISC-V Virtual Modeling and Silicon Security
        </p>
        <div class="cover-divider"></div>
        <div class="cover-meta-grid">
            <div class="cover-meta-item">
                <h4>Specialization Track</h4>
                <p>Silicon Hardware Security & Cryptographic Systems</p>
            </div>
            <div class="cover-meta-item">
                <h4>Core Standards</h4>
                <p>ISO/IEC C++20, ARMv8-A/ARMv9-A, RISC-V RV32I</p>
            </div>
            <div class="cover-meta-item">
                <h4>Cryptographic Targets</h4>
                <p>NIST FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), NTT</p>
            </div>
            <div class="cover-meta-item">
                <h4>Verification & Tooling</h4>
                <p>Verilator C++ Testbenches, GICv3, AXI4-Lite, TileLink</p>
            </div>
        </div>
    </div>
    <div class="cover-footer">
        <span>Hardware Security Engineering Research Group</span>
        <span>Academic & Industry Systems Handbook &bull; 2026 Edition</span>
    </div>
</div>

<!-- EXECUTIVE ROADMAP & THESIS PREPARATION -->
<div class="page-break" style="padding: 10mm 5mm;">
    <h1>Curriculum Roadmap & Hardware Engineering Mental Model</h1>
    <p>
        Modern silicon engineering operates at the razor edge between physical physics, semiconductor logic gates, 
        and high-performance systems software. As a <strong>Silicon Hardware Security Engineer</strong>, your primary challenge 
        is that hardware does not exist in isolation: every cryptographic accelerator, register bank, and bus interconnect 
        is driven by firmware and exposed to physical observation and malicious manipulation.
    </p>

    <div class="callout callout-why">
        <div class="callout-header">The Unifying Engineering Principle</div>
        <p>
            High-level software abstracts memory as an infinite, flat array of bytes with uniform access latency. 
            <strong>Hardware security engineering violently shatters this abstraction.</strong> In physical silicon:
            every memory access is an electrical charge transfer along capacitive copper traces; every register write is 
            a latch transition that draws instantaneous dynamic power (\(P = \alpha C V^2 f\)); every conditional branch is 
            an instruction pipeline hazard observable through microarchitectural side channels; and every unaligned pointer cast 
            violates physical bus transaction alignment or invokes compiler-level undefined behavior that silently deletes security checks.
        </p>
    </div>

    <h2>The 12-Week Specialization Trajectory</h2>
    <p>
        This guide is engineered to serve as your permanent, definitive desktop reference across all three phases of your 
        specialization and master's thesis preparation:
    </p>

    <table>
        <thead>
            <tr>
                <th style="width: 15%;">Phase</th>
                <th style="width: 35%;">Core Disciplines</th>
                <th style="width: 50%;">Practical Artifacts & Verification Milestones</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Month 1: Foundations</strong></td>
                <td>
                    &bull; Advanced C & C++20 Low-Level Systems<br>
                    &bull; Raw Memory, Cache Locality, Struct Padding<br>
                    &bull; MMIO, BitFields, Compile-Time Endianness<br>
                    &bull; RAII, Move Semantics, Slab Allocators<br>
                    &bull; SystemVerilog RTL & RISC-V (RV32I) Bare-Metal
                </td>
                <td>
                    &bull; 15 Core Systems Engineering Missions.<br>
                    &bull; Fixed-block bare-metal memory allocator.<br>
                    &bull; Register-level bit manipulation engine with <code>-Wall -Wextra -Werror</code>.<br>
                    &bull; lowRISC Ibex core integration with MMIO peripheral driven by C firmware in Verilator.
                </td>
            </tr>
            <tr>
                <td><strong>Month 2: PQC Accelerators</strong></td>
                <td>
                    &bull; Lattice-Based Cryptography (M-LWE, M-SIS)<br>
                    &bull; NIST Standards: ML-KEM (Kyber), ML-DSA (Dilithium)<br>
                    &bull; Number Theoretic Transform (NTT) Math<br>
                    &bull; Montgomery & Barrett Modular Reduction<br>
                    &bull; SystemVerilog Accelerator Datapaths
                </td>
                <td>
                    &bull; Bit-exact C/C++ reference NTT forward & inverse model.<br>
                    &bull; Dual-port BRAM memory conflict-free banking scheme.<br>
                    &bull; Pipelined modular multiplier and Butterfly Units (BFU).<br>
                    &bull; C++ Verilator co-simulation testbench comparing RTL cycle counts and outputs against golden C vectors.
                </td>
            </tr>
            <tr>
                <td><strong>Month 3: Physical Attacks & Defenses</strong></td>
                <td>
                    &bull; Side-Channel Analysis (SCA: Timing, Power, EM)<br>
                    &bull; Constant-Time Coding & Microarchitectural Invariance<br>
                    &bull; Fault Injection (FI: Clock/Voltage Glitching, Laser)<br>
                    &bull; Instruction Skipping & Loop Counter Corruption<br>
                    &bull; Dual-Modular Redundancy & Active Zeroization
                </td>
                <td>
                    &bull; Constant-time branchless cryptographic software primitives.<br>
                    &bull; Verilator fault-injection harness observing cryptographic state corruption.<br>
                    &bull; Protected NTT accelerator integrated with Ibex core over AXI4-Lite.<br>
                    &bull; Hardware tamper-detection circuit asserting alert, halting execution, and zeroizing keys.
                </td>
            </tr>
        </tbody>
    </table>

    <div class="callout callout-hw">
        <div class="callout-header">The Crucial Role of C++ in Hardware Engineering</div>
        <p>
            Why C++? High-level designers might expect Python or pure C, but silicon modeling at modern scale relies on C++:
            <strong>Verilator</strong> transpiles synthesizable SystemVerilog RTL into high-speed cycle-accurate C++ classes; 
            <strong>QEMU</strong> and <strong>gem5</strong> model CPU pipelines, memory controllers, and peripheral trees in C++; and 
            modern firmware test harnesses require the deterministic ownership guarantees of <strong>RAII</strong>, the zero-cost 
            abstractions of <strong>C++20 Concepts</strong>, and the compile-time verification of <code>constexpr</code>/<code>consteval</code>.
        </p>
    </div>
</div>

<!-- TABLE OF CONTENTS -->
<div class="toc-page">
    <div class="toc-title">Table of Contents</div>

    <div class="toc-part-row">
        <span>PART I: LOW-LEVEL MEMORY PHYSICS, POINTERS & HARDWARE REGISTERS</span>
        <span>Page 4</span>
    </div>
    <div class="toc-chapter-row"><span>Chapter 1: Contiguous Memory Layout, Pointer Arithmetic & Cache Locality (Mission 01)</span><span class="toc-dots"></span><span>4</span></div>
    <div class="toc-chapter-row"><span>Chapter 2: Dynamic Heap Management & Vector Growth Mechanics (Mission 02)</span><span class="toc-dots"></span><span>8</span></div>
    <div class="toc-chapter-row"><span>Chapter 3: Memory-Mapped I/O (MMIO), Hardware Registers & the `volatile` Keyword (Mission 03)</span><span class="toc-dots"></span><span>12</span></div>
    <div class="toc-chapter-row"><span>Chapter 4: Bit Manipulation, BitFields & Endianness Parsing (Mission 03)</span><span class="toc-dots"></span><span>16</span></div>
    <div class="toc-chapter-row"><span>Chapter 5: Struct Memory Layout, Natural Alignment, Padding & Type Punning (Mission 03)</span><span class="toc-dots"></span><span>21</span></div>

    <div class="toc-part-row">
        <span>PART II: MODERN C++ OBJECT ARCHITECTURE, RESOURCE DISCIPLINE & ALLOCATORS</span>
        <span>Page 26</span>
    </div>
    <div class="toc-chapter-row"><span>Chapter 6: Encapsulation, Invariants & The Rule of Three (Mission 04)</span><span class="toc-dots"></span><span>26</span></div>
    <div class="toc-chapter-row"><span>Chapter 7: Value Categories, Move Semantics & The Rule of Five (Mission 06)</span><span class="toc-dots"></span><span>30</span></div>
    <div class="toc-chapter-row"><span>Chapter 8: The RAII Paradigm, Custom Smart Pointers & Scope Guards (Mission 07)</span><span class="toc-dots"></span><span>35</span></div>
    <div class="toc-chapter-row"><span>Chapter 9: Embedded & Bare-Metal Error Handling: Exceptions vs Monadic Types (Mission 07)</span><span class="toc-dots"></span><span>40</span></div>
    <div class="toc-chapter-row"><span>Chapter 10: Deterministic Bare-Metal Memory: The Slab Allocator & Placement New (Mission 08)</span><span class="toc-dots"></span><span>44</span></div>

    <div class="toc-part-row">
        <span>PART III: VIRTUAL HARDWARE MODELING, DYNAMIC DISPATCH & SYSTEMS INTEROPERABILITY</span>
        <span>Page 49</span>
    </div>
    <div class="toc-chapter-row"><span>Chapter 11: Dynamic Dispatch, Vtables, Object Slicing & Security Exploits (Mission 05)</span><span class="toc-dots"></span><span>49</span></div>
    <div class="toc-chapter-row"><span>Chapter 12: Architectural Simulation: Modeling Peripheral Trees & Buses (Mission 05)</span><span class="toc-dots"></span><span>54</span></div>
    <div class="toc-chapter-row"><span>Chapter 13: The Two-Language Build: Translation Units, Linkage & C Interoperability (Mission 09)</span><span class="toc-dots"></span><span>59</span></div>
    <div class="toc-chapter-row"><span>Chapter 14: Compile-Time Metaprogramming with C++20 Concepts & `constexpr` (Mission 10)</span><span class="toc-dots"></span><span>64</span></div>

    <div class="toc-part-row">
        <span>PART IV: CONCURRENCY, MEMORY ORDERING & LOW-LATENCY SYSTEMS</span>
        <span>Page 69</span>
    </div>
    <div class="toc-chapter-row"><span>Chapter 15: Multithreaded Pipelines, Worker Pools & Cooperative Cancellation (Mission 11)</span><span class="toc-dots"></span><span>69</span></div>
    <div class="toc-chapter-row"><span>Chapter 16: The C++ Memory Model, Atomics & Memory Ordering (Mission 12)</span><span class="toc-dots"></span><span>74</span></div>
    <div class="toc-chapter-row"><span>Chapter 17: The Lock-Free Single-Producer Single-Consumer (SPSC) Ring Buffer (Mission 12)</span><span class="toc-dots"></span><span>79</span></div>
    <div class="toc-chapter-row"><span>Chapter 18: C++20 Coroutines & Stackless Task Dispatchers (Mission 15)</span><span class="toc-dots"></span><span>84</span></div>
    <div class="toc-chapter-row"><span>Chapter 19: Zero-Allocation Log Streaming with C++20 Ranges & Views (Mission 14)</span><span class="toc-dots"></span><span>89</span></div>

    <div class="toc-part-row">
        <span>PART V: HARDWARE ARCHITECTURES: ARM64 (AArch64) & RISC-V DEEP DIVE</span>
        <span>Page 94</span>
    </div>
    <div class="toc-chapter-row"><span>Chapter 20: ARM64 (AArch64) Architecture, Exception Levels & System Registers</span><span class="toc-dots"></span><span>94</span></div>
    <div class="toc-chapter-row"><span>Chapter 21: ARM64 Memory Management, MMU & Device-nGnRnE Memory</span><span class="toc-dots"></span><span>99</span></div>
    <div class="toc-chapter-row"><span>Chapter 22: ARM64 Memory Barriers, Synchronization & GIC Interrupts</span><span class="toc-dots"></span><span>104</span></div>
    <div class="toc-chapter-row"><span>Chapter 23: RISC-V (RV32I / RV64I) Architecture & Bare-Metal Verilator Simulation</span><span class="toc-dots"></span><span>109</span></div>
    <div class="toc-chapter-row"><span>Chapter 24: On-Chip Bus Interconnects: AXI4-Lite & TileLink Protocols</span><span class="toc-dots"></span><span>114</span></div>

    <div class="toc-part-row">
        <span>PART VI: SILICON HARDWARE SECURITY, PHYSICAL ATTACKS & COUNTERMEASURES</span>
        <span>Page 119</span>
    </div>
    <div class="toc-chapter-row"><span>Chapter 25: Post-Quantum Cryptography (PQC) & Hardware Accelerators: NTT Mathematics</span><span class="toc-dots"></span><span>119</span></div>
    <div class="toc-chapter-row"><span>Chapter 26: Physical Attacks: Side-Channel Analysis (SCA) & Constant-Time Implementation</span><span class="toc-dots"></span><span>124</span></div>
    <div class="toc-chapter-row"><span>Chapter 27: Physical Attacks: Fault Injection (FI) & Silicon Countermeasures</span><span class="toc-dots"></span><span>129</span></div>
    <div class="toc-chapter-row"><span>Chapter 28: Hardware Verification & The Machine Artifact: Disassembly, Golden Models & Testing (Mission 13)</span><span class="toc-dots"></span><span>134</span></div>

    <div class="toc-part-row">
        <span>PART VII: THE MASTER LEXICON & DEFINITION INDEX</span>
        <span>Page 139</span>
    </div>
    <div class="toc-chapter-row"><span>Comprehensive Alphabetical Dictionary of Types, Keywords, Registers, Protocols & Concepts</span><span class="toc-dots"></span><span>139</span></div>
</div>
"""
