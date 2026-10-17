"""
part5_hardware_arm_riscv.py - Part V: Hardware Architectures: ARM64 (AArch64) & RISC-V Deep Dive
"""

def get_part5_html():
    return r"""
<!-- PART V COVER -->
<div class="part-page">
    <div class="part-number">Part V</div>
    <div class="part-title">Hardware Architectures: ARM64 & RISC-V Deep Dive</div>
    <div class="part-desc">
        To build high-fidelity virtual hardware models and design secure silicon accelerators, an engineer must operate 
        at the architectural specification level. This part provides an exhaustive exploration of 64-bit ARM (AArch64) 
        and 32-bit RISC-V (RV32I) architectures: privilege exception levels (EL0–EL3), TrustZone security isolation, 
        system registers, translation table paging (MMU), the critical <code>Device-nGnRnE</code> memory type, 
        hardware memory barriers (<code>DMB</code>, <code>DSB</code>, <code>ISB</code>), the ARM Generic Interrupt Controller (GICv3), 
        the open-source lowRISC Ibex core, and AXI4-Lite / TileLink bus handshake protocols.
    </div>
    <div class="part-chapters-list">
        <h4>Included Curriculum Chapters:</h4>
        <ul>
            <li><strong>Chapter 20:</strong> ARM64 (AArch64) Architecture, Exception Levels & System Registers</li>
            <li><strong>Chapter 21:</strong> ARM64 Memory Management, MMU & Device-nGnRnE Memory</li>
            <li><strong>Chapter 22:</strong> ARM64 Memory Barriers, Synchronization & GIC Interrupts</li>
            <li><strong>Chapter 23:</strong> RISC-V (RV32I / RV64I) Architecture & Bare-Metal Verilator Simulation</li>
            <li><strong>Chapter 24:</strong> On-Chip Bus Interconnects: AXI4-Lite & TileLink Protocols</li>
        </ul>
    </div>
</div>

<!-- CHAPTER 20 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 20</span> &bull; 
        <span>Topic: ARM64 (AArch64) Privilege Rings, TrustZone & System Control Registers</span> &bull; 
        <span>Standard: ARMv8-A / ARMv9-A Architecture</span> &bull; 
        <span>Hardware Context: Physical Silicon Security Architecture</span>
    </div>

    <h1>Chapter 20: ARM64 Architecture: Privilege Levels & System Registers</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>AArch64:</strong> The 64-bit execution state of the ARMv8-A and ARMv9-A processor architectures, featuring thirty-one 
            64-bit general-purpose registers (<code>X0</code>–<code>X30</code>), a dedicated zero register (<code>XZR</code>), and 64-bit program counter.<br>
            <strong>Exception Levels (EL):</strong> The hardware privilege hierarchy in ARM64:
            <ul>
                <li><strong>EL0 (Application):</strong> Unprivileged user-space execution. Cannot execute privileged system instructions.</li>
                <li><strong>EL1 (OS Kernel):</strong> Operating system kernel and guest OSes in virtualized environments. Manages MMU page tables.</li>
                <li><strong>EL2 (Hypervisor):</strong> Virtualization layer managing stage-2 address translations and hypervisor guests.</li>
                <li><strong>EL3 (Secure Monitor):</strong> Highest hardware privilege. Executes trusted firmware (ATF) and switches security states.</li>
            </ul>
            <strong>ARM TrustZone:</strong> A hardware security architecture that partitions the physical SoC into two distinct worlds: 
            the <strong>Non-Secure World (Normal World)</strong> and the <strong>Secure World</strong>, enforced by the bus interconnect and CPU core.<br>
            <strong>System Registers (<code>sysreg</code>):</strong> Internal configuration registers (e.g., <code>SCTLR_EL1</code>, <code>TTBR0_EL1</code>) 
            accessed strictly via specialized instructions: <code>MRS</code> (Move from System Register) and <code>MSR</code> (Move to System Register).
        </p>
    </div>

    <div class="diagram">
ARM64 PRIVILEGE ARCHITECTURE & TRUSTZONE ISOLATION:
+---------------------------------------+---------------------------------------+
| NORMAL WORLD (Non-Secure)             | SECURE WORLD (TrustZone)              |
+---------------------------------------+---------------------------------------+
| EL0: User Space Apps (e.g., Browser)  | EL0: Secure Apps (e.g., Keymaster)    |
+---------------------------------------+---------------------------------------+
| EL1: Normal OS (e.g., Linux Kernel)   | EL1: Secure OS (e.g., OP-TEE)         |
+---------------------------------------+---------------------------------------+
| EL2: Hypervisor (e.g., KVM)           | EL2: Secure Virtualization (ARMv8.4)  |
+---------------------------------------+---------------------------------------+
                    \                               /
                     \                             /
                      v                           v
              +-------------------------------------------+
              | EL3: Secure Monitor (e.g., TF-A Firmware) |
              +-------------------------------------------+
    </div>

    <h2>System Register Inspection & Transition Mechanics</h2>
    <p>
        Moving between privilege levels requires hardware exception events:
    </p>
    <ul>
        <li><code>SVC</code> (Supervisor Call): User space (EL0) requests OS services from EL1.</li>
        <li><code>HVC</code> (Hypervisor Call): Guest OS (EL1) requests hypervisor services from EL2.</li>
        <li><code>SMC</code> (Secure Monitor Call): Normal world software requests services from Secure World (EL3).</li>
        <li><code>ERET</code> (Exception Return): Atomically restores the Program Counter from <code>ELR_ELx</code> and processor state from <code>SPSR_ELx</code>.</li>
    </ul>

    <pre><code><span class="com">// Reading and writing system registers in AArch64 assembly</span>
<span class="com">// 1. Read System Control Register (SCTLR_EL1) into general-purpose register X0</span>
<span class="kwd">mrs</span> <span class="reg">x0</span>, <span class="reg">sctlr_el1</span>

<span class="com">// 2. Enable Data Cache (Bit 2) and MMU (Bit 0) via bitwise OR</span>
<span class="kwd">orr</span> <span class="reg">x0</span>, <span class="reg">x0</span>, #(<span class="num">1</span> &lt;&lt; <span class="num">2</span>)   <span class="com">// Bit 2: C bit (Data / unified cache enable)</span>
<span class="kwd">orr</span> <span class="reg">x0</span>, <span class="reg">x0</span>, #(<span class="num">1</span> &lt;&lt; <span class="num">0</span>)   <span class="com">// Bit 0: M bit (MMU enable)</span>

<span class="com">// 3. Write back to system register</span>
<span class="kwd">msr</span> <span class="reg">sctlr_el1</span>, <span class="reg">x0</span>

<span class="com">// 4. Synchronize pipeline: guarantees instruction fetch uses updated MMU state</span>
<span class="kwd">isb</span></code></pre>
</div>

<!-- CHAPTER 21 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 21</span> &bull; 
        <span>Topic: MMU Page Translation & The Device-nGnRnE Memory Attribute</span> &bull; 
        <span>Standard: ARM64 Architecture</span> &bull; 
        <span>Hardware Context: Physical Memory Interconnect Physics</span>
    </div>

    <h1>Chapter 21: ARM64 MMU & Device-nGnRnE Memory</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Memory Management Unit (MMU):</strong> Hardware module that translates Virtual Addresses (VA) to Physical Addresses (PA) 
            via multi-level page table lookups, checking read/write/execute permissions and memory type attributes.<br>
            <strong>Translation Table Base Register (<code>TTBR0_EL1</code> / <code>TTBR1_EL1</code>):</strong> System registers holding 
            the physical base addresses of Level 0 / Level 1 page table translation trees.<br>
            <strong>Normal Memory:</strong> Memory configured for maximum execution performance (RAM/SRAM). Allows hardware caching, 
            speculative out-of-order execution, load/store coalescing, and prefetching.<br>
            <strong>Device Memory:</strong> Memory configured for hardware registers and MMIO peripherals. 
            Strictly disables CPU caching and speculative loads.
        </p>
    </div>

    <h2>The Four Device Memory Types: Understanding nG, nR, and nE</h2>
    <p>
        In ARM64, the Memory Attribute Indirection Register (<code>MAIR_EL1</code>) partitions Device Memory into four subtypes based on three letters:
    </p>

    <table>
        <thead>
            <tr>
                <th style="width: 20%;">Memory Attribute</th>
                <th style="width: 25%;">Gathering (G / nG)</th>
                <th style="width: 25%;">Reordering (R / nR)</th>
                <th style="width: 30%;">Early Write Ack (E / nE)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><code>Device-nGnRnE</code></td>
                <td><strong>Non-Gathering:</strong> Multiple accesses to the same address or adjacent bytes cannot be merged into a single bus burst.</td>
                <td><strong>Non-Reordering:</strong> Access sequence cannot be reordered by the CPU memory pipeline.</td>
                <td><strong>Non-Early-Ack:</strong> Write acknowledgment must originate from the destination peripheral endpoint, not an intermediate bus buffer.</td>
            </tr>
            <tr>
                <td><code>Device-nGnRE</code></td>
                <td>Non-Gathering</td>
                <td>Non-Reordering</td>
                <td><strong>Early-Ack:</strong> Write response can be returned by an intermediate bus buffer before reaching peripheral.</td>
            </tr>
            <tr>
                <td><code>Device-nGRE</code></td>
                <td>Non-Gathering</td>
                <td><strong>Reordering Allowed:</strong> Accesses to different registers may be reordered.</td>
                <td>Early-Ack</td>
            </tr>
            <tr>
                <td><code>Device-GRE</code></td>
                <td><strong>Gathering Allowed:</strong> Writes may be coalesced into single wider bus transactions.</td>
                <td>Reordering Allowed</td>
                <td>Early-Ack</td>
            </tr>
        </tbody>
    </table>

    <div class="callout callout-sec">
        <div class="callout-header">Why Peripheral MMIO MUST Use Device-nGnRnE</div>
        <p>
            Suppose you map a hardware cryptographic accelerator's registers as <strong>Normal Memory</strong> or <strong>Device-GRE</strong>:
            <ol>
                <li><strong>Gathering Disaster:</strong> If you write <code>KEY[0] = 0xAA</code> and <code>KEY[1] = 0xBB</code>, the bus coalesces them into a single 64-bit write. If the peripheral FIFO expects sequential 32-bit strobes, it drops the key!</li>
                <li><strong>Reordering Disaster:</strong> If you write <code>DATA_IN = 0x1234</code> followed by <code>CTRL_START = 1</code>, the out-of-order CPU may issue the <code>START</code> write <em>before</em> the <code>DATA_IN</code> write completes, causing the accelerator to encrypt stale data!</li>
                <li><strong>Speculative Read Disaster:</strong> If the CPU speculatively fetches from an address (e.g. <code>UART_RXDATA</code>), it triggers a hardware read strobe, <em>popping a byte off the FIFO</em> before software ever intended to read it!</li>
            </ol>
            <strong>Golden Silicon Rule:</strong> All hardware control, status, and FIFO registers must be mapped as <strong>Device-nGnRnE</strong>.
        </p>
    </div>
</div>

<!-- CHAPTER 22 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 22</span> &bull; 
        <span>Topic: ARM64 Memory Barriers, Synchronization Primitives & GIC Interrupts</span> &bull; 
        <span>Standard: ARMv8-A / ARMv9-A Architecture</span> &bull; 
        <span>Hardware Context: Bus Synchronization & Interrupt Controllers</span>
    </div>

    <h1>Chapter 22: ARM64 Barriers, Atomics & GIC Interrupts</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Weak Memory Architecture:</strong> A CPU memory architecture (standard on ARM64 and RISC-V) where the processor 
            pipeline and interconnect may reorder memory reads and writes unless explicit memory barrier instructions are inserted.<br>
            <strong><code>DMB</code> (Data Memory Barrier):</strong> Ensures that all memory accesses appearing before the <code>DMB</code> 
            instruction are committed to the memory system before any memory accesses appearing after the <code>DMB</code>.<br>
            <strong><code>DSB</code> (Data Synchronization Barrier):</strong> Stalls execution of subsequent CPU instructions until 
            all pending memory transactions (including cache maintenance and TLB invalidations) have completed across the entire bus.<br>
            <strong><code>ISB</code> (Instruction Synchronization Barrier):</strong> Flushes the CPU instruction fetch pipeline, 
            forcing subsequent instructions to be re-fetched from the instruction cache or memory.<br>
            <strong>ARM GIC (Generic Interrupt Controller):</strong> The standardized hardware interrupt router in ARM SoCs. 
            Currently at versions GICv3 and GICv4.<br>
            <strong>Interrupt Types:</strong>
            <ul>
                <li><strong>SGI (Software Generated Interrupts, 0–15):</strong> Inter-processor interrupts (IPIs) triggered by software.</li>
                <li><strong>PPI (Private Peripheral Interrupts, 16–31):</strong> Per-core interrupts (e.g. core-local timer).</li>
                <li><strong>SPI (Shared Peripheral Interrupts, 32–1019):</strong> Global interrupts routed from peripherals to any core.</li>
                <li><strong>LPI (Locality-specific Peripheral Interrupts):</strong> Message-Signaled Interrupts (MSI/MSI-X).</li>
            </ul>
        </p>
    </div>

    <h2>Hardware Assembly: The Complete Barrier Spectrum</h2>
    <pre><code><span class="com">// 1. Data Memory Barrier (Inner Shareable domain, full loads &amp; stores)</span>
<span class="kwd">dmb</span> <span class="reg">ish</span>

<span class="com">// 2. Data Synchronization Barrier: Used before halting core with WFI (Wait For Interrupt)</span>
<span class="kwd">dsb</span> <span class="reg">sy</span>
<span class="kwd">wfi</span>  <span class="com">// Core enters low-power sleep state until an interrupt fires</span>

<span class="com">// 3. Load-Acquire (LDAR) and Store-Release (STLR): Hardware 1-way barriers</span>
<span class="kwd">ldar</span> <span class="reg">w0</span>, [<span class="reg">x1</span>]  <span class="com">// All subsequent memory reads/writes cannot be reordered before this load</span>
<span class="kwd">stlr</span> <span class="reg">w0</span>, [<span class="reg">x1</span>]  <span class="com">// All prior memory reads/writes must complete before this store</span></code></pre>

    <h2>Virtual Hardware Modeling: Simulating an Interrupt to the GIC</h2>
    <p>
        When you model an ARM64-compatible virtual peripheral in C++, you must model its interrupt line asserting an active-high 
        signal to the virtual GIC Distributor:
    </p>

    <pre><code><span class="com">// C++ Virtual Peripheral IRQ Line Model</span>
<span class="kwd">class</span> <span class="typ">VirtualUart</span> {
<span class="kwd">public</span>:
    <span class="com">// Function pointer or callback simulating the physical copper IRQ trace</span>
    <span class="kwd">using</span> <span class="typ">IrqLineCallback</span> = <span class="typ">void</span>(*)(<span class="typ">uint32_t</span> irq_num, <span class="typ">bool</span> level);

    <span class="typ">void</span> <span class="fn">connect_irq</span>(<span class="typ">uint32_t</span> irq_num, <span class="typ">IrqLineCallback</span> cb) {
        _irq_number = irq_num;
        _irq_cb = cb;
    }

    <span class="typ">void</span> <span class="fn">receive_byte_hardware_hook</span>(<span class="typ">uint8_t</span> byte) {
        _rx_fifo.push(byte);
        <span class="com">// Assert level-sensitive active-high interrupt (SPI 42) to Virtual GIC</span>
        <span class="kwd">if</span> (_irq_cb) {
            _irq_cb(_irq_number, <span class="kwd">true</span>);
        }
    }

    <span class="typ">uint32_t</span> <span class="fn">read_rxdata</span>() {
        <span class="kwd">const</span> <span class="typ">uint8_t</span> b = _rx_fifo.front();
        _rx_fifo.pop();
        <span class="com">// De-assert interrupt line if FIFO is empty</span>
        <span class="kwd">if</span> (_rx_fifo.empty() &amp;&amp; _irq_cb) {
            _irq_cb(_irq_number, <span class="kwd">false</span>);
        }
        <span class="kwd">return</span> b;
    }

<span class="kwd">private</span>:
    <span class="typ">uint32_t</span> _irq_number{<span class="num">42</span>};
    <span class="typ">IrqLineCallback</span> _irq_cb{<span class="kwd">nullptr</span>};
    std::<span class="typ">queue</span>&lt;<span class="typ">uint8_t</span>&gt; _rx_fifo;
};</code></pre>
</div>

<!-- CHAPTER 23 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 23</span> &bull; 
        <span>Topic: RISC-V RV32I Architecture, CSRs & The lowRISC Ibex Verilator Flow</span> &bull; 
        <span>Standard: RISC-V ISA / SystemVerilog</span> &bull; 
        <span>Hardware Context: Synthesizable Silicon Testbenches</span>
    </div>

    <h1>Chapter 23: RISC-V RV32I & Verilator Simulation</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>RISC-V (RV32I):</strong> An open, modular Reduced Instruction Set Computer architecture featuring thirty-two 32-bit 
            registers (<code>x0</code>–<code>x31</code>), fixed 32-bit instruction encodings, and a load-store architecture.<br>
            <strong>CSR (Control and Status Registers):</strong> 12-bit address space registers controlling CPU operating modes, 
            traps, and interrupts (e.g., <code>mstatus</code>, <code>mie</code>, <code>mtvec</code>, <code>mepc</code>).<br>
            <strong>lowRISC Ibex:</strong> A widely adopted, production-grade 32-bit open-source RISC-V core written in synthesizable 
            SystemVerilog, featuring a 2-stage/3-stage in-order pipeline, used in OpenTitan Root of Trust silicon.<br>
            <strong>Verilator:</strong> An open-source EDA tool that transpiles synthesizable SystemVerilog RTL directly into highly 
            optimized cycle-accurate C++ simulation classes.
        </p>
    </div>

    <div class="diagram">
VERILATOR CO-SIMULATION TESTBENCH ARCHITECTURE:
+---------------------------------------------------------------------------------+
| C++ Testbench Harness (main.cpp)                                                |
|                                                                                 |
|  1. Instantiate Verilated Core:                                                |
|     Vibex_top* top = new Vibex_top();                                           |
|                                                                                 |
|  2. Clock &amp; Reset Generation:                                                   |
|     top-&gt;clk_i = 1; top-&gt;eval();                                                |
|     top-&gt;clk_i = 0; top-&gt;eval();                                                |
|                                                                                 |
|  3. Intercept Memory Bus:                                                       |
|     if (top-&gt;data_req_o &amp;&amp; top-&gt;data_we_o) {                                    |
|         bus.write32(top-&gt;data_addr_o, top-&gt;data_wdata_o);                       |
|     }                                                                           |
|                                                                                 |
|  4. Waveform Tracing:                                                           |
|     tfp-&gt;dump(sim_time++); // Writes VCD/FST file for GTKWave waveform viewing  |
+---------------------------------------------------------------------------------+
    </div>

    <h2>C++ Implementation: The Verilator Driver Loop</h2>
    <pre><code><span class="dir">#include</span> <span class="str">&lt;memory&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;verilated.h&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;verilated_vcd_c.h&gt;</span>
<span class="dir">#include</span> <span class="str">"Vibex_top.h"</span>

<span class="typ">int</span> <span class="fn">main</span>(<span class="typ">int</span> argc, <span class="typ">char</span>** argv) {
    <span class="typ">Verilated</span>::<span class="fn">commandArgs</span>(argc, argv);
    <span class="typ">Verilated</span>::<span class="fn">traceEverOn</span>(<span class="kwd">true</span>);

    <span class="kwd">auto</span> top = std::<span class="fn">make_unique</span>&lt;<span class="typ">Vibex_top</span>&gt;();
    <span class="kwd">auto</span> tfp = std::<span class="fn">make_unique</span>&lt;<span class="typ">VerilatedVcdC</span>&gt;();
    top-&gt;<span class="fn">trace</span>(tfp.<span class="fn">get</span>(), <span class="num">99</span>);
    tfp-&gt;<span class="fn">open</span>(<span class="str">"trace.vcd"</span>);

    <span class="typ">uint64_t</span> sim_time = <span class="num">0</span>;

    <span class="com">// 1. Assert Reset for 5 clock cycles</span>
    top-&gt;rst_ni = <span class="num">0</span>;
    <span class="kwd">for</span> (<span class="typ">int</span> i = <span class="num">0</span>; i &lt; <span class="num">10</span>; ++i) {
        top-&gt;clk_i = !top-&gt;clk_i;
        top-&gt;<span class="fn">eval</span>();
        tfp-&gt;<span class="fn">dump</span>(sim_time++);
    }
    top-&gt;rst_ni = <span class="num">1</span>; <span class="com">// Release reset</span>

    <span class="com">// 2. Execution loop driving Ibex core through MMIO accesses</span>
    <span class="kwd">while</span> (sim_time &lt; <span class="num">100000</span> &amp;&amp; !<span class="typ">Verilated</span>::<span class="fn">gotFinish</span>()) {
        top-&gt;clk_i = !top-&gt;clk_i;

        <span class="com">// Rising edge: sample outputs and evaluate combinational logic</span>
        <span class="kwd">if</span> (top-&gt;clk_i) {
            <span class="kwd">if</span> (top-&gt;data_req_o) {
                <span class="com">// Intercept bus transaction from Ibex core</span>
                <span class="typ">uint32_t</span> addr = top-&gt;data_addr_o;
                <span class="kwd">if</span> (top-&gt;data_we_o) {
                    <span class="com">// Hardware MMIO write</span>
                    std::printf(<span class="str">"MMIO Write: 0x%08X = 0x%08X\n"</span>, addr, top-&gt;data_wdata_o);
                }
                top-&gt;data_gnt_i = <span class="num">1</span>;   <span class="com">// Bus acknowledge</span>
                top-&gt;data_rvalid_i = <span class="num">1</span>;<span class="com">// Data valid response</span>
            }
        }
        top-&gt;<span class="fn">eval</span>();
        tfp-&gt;<span class="fn">dump</span>(sim_time++);
    }

    tfp-&gt;<span class="fn">close</span>();
    <span class="kwd">return</span> <span class="num">0</span>;
}</code></pre>
</div>

<!-- CHAPTER 24 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 24</span> &bull; 
        <span>Topic: On-Chip Bus Interconnects: AXI4-Lite & TileLink Protocol Handshakes</span> &bull; 
        <span>Standard: AMBA AXI4 / SiFive TileLink</span> &bull; 
        <span>Hardware Context: Silicon IP Bus Handshakes</span>
    </div>

    <h1>Chapter 24: On-Chip Bus Protocols: AXI4-Lite & TileLink</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>AMBA AXI4-Lite:</strong> A standardized, subset protocol of ARM's Advanced eXtensible Interface designed for 
            low-overhead, memory-mapped register access. Features 5 independent physical channels, 32-bit data widths, and no burst support.<br>
            <strong>VALID / READY Handshake:</strong> The fundamental transfer rule governing AXI and TileLink. 
            A transfer occurs <em>if and only if</em> both <code>VALID</code> and <code>READY</code> are asserted high on the same rising clock edge.<br>
            <strong>TileLink:</strong> An open-source, high-performance chip-scale interconnect standard developed by SiFive and UC Berkeley. 
            Features point-to-point channels (Channel A for requests, Channel D for responses).
        </p>
    </div>

    <h2>The Five Channels of AXI4-Lite</h2>
    <div class="diagram">
+-----------------------------------------------------------------------------------------+
| MASTER (CPU / DMA Engine)                                  SLAVE (Peripheral / Crypto)   |
|                                                                                         |
| Write Address Channel:  AWADDR, AWPROT, AWVALID ==========&gt; AWREADY                    |
| Write Data Channel:     WDATA, WSTRB, WVALID    ==========&gt; WREADY                      |
| Write Response Channel: BREADY                  &lt;========== BVALID, BRESP               |
|                                                                                         |
| Read Address Channel:   ARADDR, ARPROT, ARVALID ==========&gt; ARREADY                    |
| Read Data Channel:      RREADY                  &lt;========== RVALID, RDATA, RRESP        |
+-----------------------------------------------------------------------------------------+
    </div>

    <div class="callout callout-sec">
        <div class="callout-header">Critical Bus Deadlock Rule: The VALID/READY Constraint</div>
        <p>
            Under the ARM AMBA AXI specification:
            <ul>
                <li>A master is permitted to wait for <code>READY</code> to be asserted before or after asserting <code>VALID</code>.</li>
                <li><strong>Strict Rule:</strong> A slave must NEVER wait for the master to assert <code>READY</code> before asserting <code>VALID</code>. 
                Doing so creates a circular dependency where master and slave each wait for the other, permanently deadlocking the hardware SoC!</li>
            </ul>
        </p>
    </div>

    <h2>C++ Simulation Model: Cycle-Accurate AXI4-Lite Slave Handshake</h2>
    <pre><code><span class="com">// C++ model of an AXI4-Lite Slave Peripheral state machine</span>
<span class="kwd">struct</span> <span class="typ">AxiLiteSlaveModel</span> {
    <span class="com">// Bus inputs from master</span>
    <span class="typ">uint32_t</span> awaddr{<span class="num">0</span>};
    <span class="typ">bool</span> awvalid{<span class="kwd">false</span>};
    <span class="typ">uint32_t</span> wdata{<span class="num">0</span>};
    <span class="typ">bool</span> wvalid{<span class="kwd">false</span>};
    <span class="typ">bool</span> bready{<span class="kwd">false</span>};

    <span class="com">// Bus outputs to master</span>
    <span class="typ">bool</span> awready{<span class="kwd">true</span>};
    <span class="typ">bool</span> wready{<span class="kwd">true</span>};
    <span class="typ">bool</span> bvalid{<span class="kwd">false</span>};
    <span class="typ">uint8_t</span> bresp{<span class="num">0</span>}; <span class="com">// 0b00 = OKAY, 0b10 = SLVERR</span>

    <span class="com">// Hardware clock tick</span>
    <span class="typ">void</span> <span class="fn">clock_tick</span>(<span class="typ">uint32_t</span>* memory_registers) {
        <span class="com">// Complete write handshake when both AW and W channels are VALID and READY</span>
        <span class="kwd">if</span> (awvalid &amp;&amp; awready &amp;&amp; wvalid &amp;&amp; wready) {
            <span class="kwd">const</span> <span class="typ">uint32_t</span> offset = (awaddr &gt;&gt; <span class="num">2</span>) &amp; <span class="num">0x3F</span>;
            memory_registers[offset] = wdata; <span class="com">// Latch register value</span>

            bvalid = <span class="kwd">true</span>;  <span class="com">// Assert write response</span>
            bresp = <span class="num">0</span>;      <span class="com">// OKAY status</span>
            awready = <span class="kwd">false</span>;<span class="com">// De-assert until response accepted</span>
            wready = <span class="kwd">false</span>;
        }

        <span class="com">// Response accepted by master</span>
        <span class="kwd">if</span> (bvalid &amp;&amp; bready) {
            bvalid = <span class="kwd">false</span>;
            awready = <span class="kwd">true</span>;
            wready = <span class="kwd">true</span>;
        }
    }
};</code></pre>
</div>
"""
