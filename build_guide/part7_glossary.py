"""
part7_glossary.py - Part VII: The Master Lexicon & Comprehensive Definition Index
"""

def get_part7_html():
    return r"""
<!-- PART VII COVER -->
<div class="part-page">
    <div class="part-number">Part VII</div>
    <div class="part-title">The Master Lexicon & Comprehensive Definition Index</div>
    <div class="part-desc">
        A definitive, cross-referenced alphabetical glossary defining every technical concept, C++ language keyword, 
        CPU architecture register, bus protocol signal, cryptographic primitive, and physical security attack vector 
        encountered throughout the Silicon Hardware Security Engineering curriculum.
    </div>
</div>

<div class="page-break" style="padding: 10mm 5mm;">
    <h1>Comprehensive Definition Index & Lexicon</h1>

    <div class="glossary-entry">
        <span class="glossary-term">alignas / alignof</span>
        <span class="glossary-category">C++ Keywords &bull; Memory Alignment</span>
        <p class="glossary-desc">
            <code>alignof(T)</code> queries the byte alignment required by type <code>T</code>. 
            <code>alignas(N)</code> forces a variable or struct to be allocated at an address evenly divisible by \(N\). 
            Crucial in hardware drivers to prevent bus alignment faults and false sharing (e.g. <code>alignas(64)</code>).
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">always_comb / always_ff</span>
        <span class="glossary-category">SystemVerilog &bull; RTL Synthesis</span>
        <p class="glossary-desc">
            SystemVerilog keywords replacing legacy <code>always @*</code> and <code>always @(posedge clk)</code>. 
            <code>always_comb</code> guarantees pure combinational logic with zero inferred latches; 
            <code>always_ff</code> guarantees synchronous sequential flip-flops with explicit reset logic.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">AMBA AXI4-Lite</span>
        <span class="glossary-category">Hardware Bus Protocol &bull; ARM AMBA</span>
        <p class="glossary-desc">
            A standardized 5-channel point-to-point bus protocol for memory-mapped peripheral control: 
            Read Address (AR), Read Data (R), Write Address (AW), Write Data (W), and Write Response (B). 
            Governed by the fundamental <code>VALID / READY</code> handshake rule.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">ARM TrustZone</span>
        <span class="glossary-category">Silicon Security Architecture &bull; ARM64</span>
        <p class="glossary-desc">
            Hardware security partitioning built into ARM CPU cores and bus fabrics. Divides the physical SoC into 
            a Secure World and a Normal (Non-Secure) World, isolated by bus line <code>NS</code> and arbitrated at Exception Level 3.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">atomic (std::atomic)</span>
        <span class="glossary-category">C++ Standard Library &bull; Concurrency</span>
        <p class="glossary-desc">
            Type template ensuring all load, store, and read-modify-write operations are indivisible at the machine level, 
            preventing data races and supporting explicit memory orderings (relaxed, acquire, release, seq_cst).
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Barrett Reduction</span>
        <span class="glossary-category">Cryptographic Mathematics &bull; Modular Arithmetic</span>
        <p class="glossary-desc">
            An algorithm that computes \(a \pmod q\) by approximating \(1/q\) with precomputed fixed-point arithmetic, 
            replacing division with integer multiplications and bit shifts.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">BitField</span>
        <span class="glossary-category">Low-Level C++ &bull; Register Mapping</span>
        <p class="glossary-desc">
            A software abstraction defined by a bit shift offset and width that extracts, sets, clears, and inserts 
            contiguous bits into a register word without triggering the compiler-defined packing traps of C-style bitfields.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Butterfly Unit (BFU)</span>
        <span class="glossary-category">Hardware Accelerator Architecture &bull; Datapaths</span>
        <p class="glossary-desc">
            The core arithmetic circuit in FFT/NTT accelerators. Computes \(A' = A + \omega B \pmod q\) and 
            \(B' = A - \omega B \pmod q\) in pipelined execution stages.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Cache Line</span>
        <span class="glossary-category">Computer Microarchitecture &bull; Memory</span>
        <p class="glossary-desc">
            The fundamental unit of memory transfer between the CPU cache hierarchy and main memory. 
            Fixed at exactly 64 bytes (512 bits) on ARM64 and modern x86_64 processors.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Clock Glitching</span>
        <span class="glossary-category">Physical Attack &bull; Fault Injection</span>
        <p class="glossary-desc">
            Injecting an ultra-narrow clock pulse shorter than the minimum setup time (\(t_{\text{setup}}\)) of logic flip-flops, 
            causing state registers to latch unresolved combinational values or skip instruction fetches.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Cooley-Tukey Butterfly</span>
        <span class="glossary-category">Algorithms &bull; Number Theoretic Transform</span>
        <p class="glossary-desc">
            Decimation-in-time NTT algorithm structure reducing polynomial multiplication complexity from \(O(n^2)\) to \(O(n \log n)\).
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Coroutine (co_await, co_yield, co_return)</span>
        <span class="glossary-category">C++20 &bull; Asynchronous Execution</span>
        <p class="glossary-desc">
            Stackless functions that can suspend execution, preserve local variables in a coroutine frame, 
            and resume execution cooperatively without OS thread context switch overhead.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Control and Status Register (CSR)</span>
        <span class="glossary-category">Processor Architecture &bull; RISC-V</span>
        <p class="glossary-desc">
            Internal CPU registers controlling operating modes, trap handling, interrupt masks, and performance counters 
            (e.g., <code>mstatus</code>, <code>mie</code>, <code>mtvec</code>). Accessed via <code>csrr</code> and <code>csrw</code>.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Dead Store Elimination (DSE)</span>
        <span class="glossary-category">Compiler Optimization &bull; Security Hazard</span>
        <p class="glossary-desc">
            An optimization where the compiler deletes writes to memory if it can prove the memory is not read subsequently. 
            Causes standard <code>memset</code> calls scrubbing cryptographic keys to be silently erased!
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Device-nGnRnE</span>
        <span class="glossary-category">ARM64 Architecture &bull; Memory Types</span>
        <p class="glossary-desc">
            The strictest memory attribute in ARM64: Non-Gathering, Non-Reordering, Non-Early-Write-Ack. 
            Mandatory for MMIO hardware registers to prevent bus transaction merging, CPU reordering, and speculative reads.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Differential Testing</span>
        <span class="glossary-category">Hardware Verification &bull; Methodology</span>
        <p class="glossary-desc">
            Executing two distinct implementations of the same specification (C golden reference model vs SystemVerilog RTL in Verilator) 
            across millions of pseudo-random inputs to verify bit-level output identity.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Dual-Modular Redundancy (DMR)</span>
        <span class="glossary-category">Silicon Security Defense &bull; Fault Tolerance</span>
        <p class="glossary-desc">
            Duplicating CPU cores or cryptographic datapaths with a temporal/spatial offset and feeding outputs to a lockstep comparator. 
            A single-bit discrepancy halts computation and triggers zeroization.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Endianness (Little vs Big)</span>
        <span class="glossary-category">Computer Architecture &bull; Byte Ordering</span>
        <p class="glossary-desc">
            Little-Endian stores the least-significant byte at the lowest address (ARM64, RISC-V, x86). 
            Big-Endian stores the most-significant byte at the lowest address (Network wire protocols).
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Exception Levels (EL0, EL1, EL2, EL3)</span>
        <span class="glossary-category">ARM64 Architecture &bull; Privilege Hierarchy</span>
        <p class="glossary-desc">
            EL0: User applications; EL1: OS Kernel; EL2: Hypervisor; EL3: Secure Monitor. 
            Transitions occur via <code>SVC</code>, <code>HVC</code>, <code>SMC</code>, and return via <code>ERET</code>.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">explicit_bzero</span>
        <span class="glossary-category">Security Standard &bull; Memory Sanitization</span>
        <p class="glossary-desc">
            A memory wiping function guaranteed not to be eliminated by compiler Dead Store Elimination passes.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">extern "C"</span>
        <span class="glossary-category">C++ Language &bull; Linkage</span>
        <p class="glossary-desc">
            Disables C++ name mangling, giving functions standard C linkage and symbol names for interoperability with C and assembly.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">False Sharing</span>
        <span class="glossary-category">Microarchitecture &bull; Concurrency Pathology</span>
        <p class="glossary-desc">
            Two distinct threads concurrently modifying separate variables that happen to reside on the same 64-byte cache line, 
            causing cache lines to bounce between CPU cores and destroying multi-core performance.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Fault Injection (FI)</span>
        <span class="glossary-category">Physical Attack &bull; Silicon Security</span>
        <p class="glossary-desc">
            Inducing hardware malfunctions via voltage glitching, clock glitching, or lasers to skip instructions or flip bits in cryptographic state.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">FENCE / FENCE.I</span>
        <span class="glossary-category">RISC-V Architecture &bull; Synchronization</span>
        <p class="glossary-desc">
            <code>FENCE</code> orders memory accesses between hardware threads. 
            <code>FENCE.I</code> synchronizes instruction fetch streams with memory stores.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Generic Interrupt Controller (GIC)</span>
        <span class="glossary-category">ARM Architecture &bull; Hardware IP</span>
        <p class="glossary-desc">
            Standard interrupt controller routing interrupts (SGI, PPI, SPI, LPI) across multi-core ARM SoCs.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Ibex Core</span>
        <span class="glossary-category">Open-Source Silicon &bull; lowRISC</span>
        <p class="glossary-desc">
            A 32-bit RISC-V RV32I core written in synthesizable SystemVerilog, used in OpenTitan Root of Trust silicon.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Intrusive Free List</span>
        <span class="glossary-category">Memory Architecture &bull; Data Structures</span>
        <p class="glossary-desc">
            A free-list implementation where pointer linkages are stored directly inside unallocated memory blocks, 
            achieving \(O(1)\) memory allocation with zero auxiliary memory overhead.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">ISB / DSB / DMB</span>
        <span class="glossary-category">ARM64 Architecture &bull; Memory Barriers</span>
        <p class="glossary-desc">
            <code>DMB</code> orders memory data accesses. <code>DSB</code> halts instruction execution until memory operations complete. 
            <code>ISB</code> flushes and re-fetches the CPU instruction pipeline.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Lock-Free SPSC Queue</span>
        <span class="glossary-category">Concurrency &bull; Data Structures</span>
        <p class="glossary-desc">
            Single-Producer Single-Consumer circular queue relying purely on atomic acquire-release semantics without mutexes.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Memory-Mapped I/O (MMIO)</span>
        <span class="glossary-category">Computer Architecture &bull; Bus Interface</span>
        <p class="glossary-desc">
            Mapping physical peripheral registers into the CPU's memory address space, accessed via standard load/store instructions.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">ML-KEM (Kyber) & ML-DSA (Dilithium)</span>
        <span class="glossary-category">NIST PQC Standards &bull; Lattice Cryptography</span>
        <p class="glossary-desc">
            NIST FIPS 203 (Key Encapsulation Mechanism) and FIPS 204 (Digital Signature Algorithm) based on Module Lattice Learning with Errors.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Montgomery Reduction</span>
        <span class="glossary-category">Cryptographic Math &bull; Modular Arithmetic</span>
        <p class="glossary-desc">
            Computes \(a \cdot b \cdot R^{-1} \pmod q\) using multiplications and bitwise shifts without division.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">MRS / MSR</span>
        <span class="glossary-category">ARM64 Assembly &bull; System Registers</span>
        <p class="glossary-desc">
            Instructions to read (<code>MRS</code>) and write (<code>MSR</code>) internal system registers (e.g. <code>SCTLR_EL1</code>).
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Name Mangling</span>
        <span class="glossary-category">Compilers &bull; C++ ABI</span>
        <p class="glossary-desc">
            Encoding parameter types and namespaces into linker symbols to support function overloading in C++.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Number Theoretic Transform (NTT)</span>
        <span class="glossary-category">Algorithms &bull; Lattice Cryptography</span>
        <p class="glossary-desc">
            Discrete Fourier Transform over finite rings \(\mathbb{Z}_q\), transforming polynomial convolution from \(O(n^2)\) to \(O(n \log n)\).
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">One Definition Rule (ODR)</span>
        <span class="glossary-category">C++ Standard &bull; Linkage</span>
        <p class="glossary-desc">
            Mandates that non-inline entities must have exactly one definition across an entire linked executable.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">OpenTitan Root of Trust (RoT)</span>
        <span class="glossary-category">Silicon Security Architecture &bull; Hardware Trust</span>
        <p class="glossary-desc">
            An open-source silicon Root of Trust chip design incorporating cryptographic accelerators, active mesh sensors, and secure boot.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Override & Final</span>
        <span class="glossary-category">C++ Keywords &bull; Object Orientation</span>
        <p class="glossary-desc">
            <code>override</code> forces compiler verification of virtual function signatures. 
            <code>final</code> prevents further overriding or inheritance, enabling devirtualization optimizations.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Placement New</span>
        <span class="glossary-category">C++ Language &bull; Memory Allocation</span>
        <p class="glossary-desc">
            Constructing an object at a pre-existing memory address without allocating heap storage (<code>::new (ptr) T(...)</code>).
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Pointer Authentication Code (PAC)</span>
        <span class="glossary-category">ARMv8.3-A Security &bull; Hardware CFI</span>
        <p class="glossary-desc">
            Signing upper bits of pointers with cryptographic MACs to prevent vtable hijacking and Return-Oriented Programming (ROP).
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">RAII</span>
        <span class="glossary-category">C++ Paradigm &bull; Resource Management</span>
        <p class="glossary-desc">
            Resource Acquisition Is Initialization: binding resource lifecycle (memory, hardware locks, file handles) to object scope.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Read-Modify-Write (RMW)</span>
        <span class="glossary-category">Hardware Registers &bull; Atomic Operations</span>
        <p class="glossary-desc">
            Reading a register, modifying bits in a CPU register, and writing back. Hazardous on Write-1-to-Clear registers.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Result&lt;T, E&gt; / std::expected</span>
        <span class="glossary-category">C++23 &bull; Embedded Error Handling</span>
        <p class="glossary-desc">
            Monadic vocabulary type holding either a value or an error, enabling exception-free deterministic error propagation.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Row-Major Order</span>
        <span class="glossary-category">Memory Layout &bull; C/C++ Arrays</span>
        <p class="glossary-desc">
            Storing multi-dimensional arrays with contiguous rows end-to-end, maximizing cache hit rates during row-wise traversal.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Rule of Three & Rule of Five</span>
        <span class="glossary-category">C++ Idiom &bull; Lifecycle Management</span>
        <p class="glossary-desc">
            Rule of Three: Destructor, Copy Constructor, Copy Assignment. 
            Rule of Five: adds Move Constructor and Move Assignment for zero-copy resource ownership transfer.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Side-Channel Analysis (SCA)</span>
        <span class="glossary-category">Physical Cryptanalysis &bull; Hardware Security</span>
        <p class="glossary-desc">
            Extracting cryptographic secrets by observing execution timing, power consumption (DPA/CPA), or EM radiation.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Slab Allocator</span>
        <span class="glossary-category">Bare-Metal Memory &bull; Determinism</span>
        <p class="glossary-desc">
            Pre-allocated memory pool partitioned into uniform slots, providing guaranteed \(O(1)\) allocation with zero heap fragmentation.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Slicing (Object Slicing)</span>
        <span class="glossary-category">C++ OOP Hazard &bull; Memory Layout</span>
        <p class="glossary-desc">
            Assigning a derived object by value to a base variable, discarding derived state and resetting the vtable pointer to base.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">std::jthread & std::stop_token</span>
        <span class="glossary-category">C++20 &bull; Concurrency</span>
        <p class="glossary-desc">
            Auto-joining thread primitive with cooperative cancellation tokens, preventing crashes from unjoined threads on scope exit.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">std::string_view & C++20 Ranges</span>
        <span class="glossary-category">C++20 &bull; Zero-Copy Data Pipelines</span>
        <p class="glossary-desc">
            Non-owning buffer view (pointer + length) combined with composable range adaptors for zero-allocation stream parsing.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Strict Aliasing Rule</span>
        <span class="glossary-category">C++ Standard &bull; Optimizer Invariants</span>
        <p class="glossary-desc">
            Rule forbidding two pointers of distinct types from referencing the same memory location. Violating this produces undefined behavior.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">TileLink</span>
        <span class="glossary-category">Chip-Scale Bus Fabric &bull; RISC-V Interconnect</span>
        <p class="glossary-desc">
            Open-source bus standard featuring Channel A (requests) and Channel D (responses) with VALID/READY handshakes.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Type Punning</span>
        <span class="glossary-category">C++ Low-Level &bull; Binary Reinterpretation</span>
        <p class="glossary-desc">
            Reinterpreting raw bytes of one type as another. Standard-compliant via <code>std::memcpy</code> and <code>std::bit_cast</code>; 
            undefined via <code>reinterpret_cast</code> pointer dereferencing.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">VALID / READY Handshake</span>
        <span class="glossary-category">Digital Logic &bull; Bus Protocols</span>
        <p class="glossary-desc">
            Data transfers on AXI and TileLink occur if and only if both VALID and READY are asserted high on the same clock edge.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Virtual Method Table (vtable) & vptr</span>
        <span class="glossary-category">C++ Runtime Mechanics &bull; Dynamic Dispatch</span>
        <p class="glossary-desc">
            Compiler-generated array of function pointers (<code>vtable</code>) and hidden object pointer (<code>_vptr</code> at offset 0) 
            enabling runtime polymorphism.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">volatile</span>
        <span class="glossary-category">C/C++ Keyword &bull; Memory Qualifier</span>
        <p class="glossary-desc">
            Forces the compiler to emit an actual machine load/store instruction for every access. Does NOT provide atomicity or thread barriers.
        </p>
    </div>

    <div class="glossary-entry">
        <span class="glossary-term">Write-1-to-Clear (W1C)</span>
        <span class="glossary-category">Hardware Register Conventions &bull; MMIO</span>
        <p class="glossary-desc">
            Writing binary '1' clears the hardware flag; writing '0' is a no-op. Must not be updated with Read-Modify-Write cycles.
        </p>
    </div>
</div>
"""
