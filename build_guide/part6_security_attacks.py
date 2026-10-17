"""
part6_security_attacks.py - Part VI: Silicon Hardware Security, Physical Attacks & Countermeasures
"""

def get_part6_html():
    return r"""
<!-- PART VI COVER -->
<div class="part-page">
    <div class="part-number">Part VI</div>
    <div class="part-title">Silicon Hardware Security, Physical Attacks & Countermeasures</div>
    <div class="part-desc">
        Silicon hardware is deployed into untrusted physical environments where adversaries possess physical access, 
        oscilloscopes, EM probes, and glitching lasers. Theoretical cryptographic security collapses if physical implementation 
        leaks secrets through power traces, execution timing, or faulted silicon logic gates. 
        This part equips the engineer with the core disciplines of post-quantum cryptography (NTT mathematics, Montgomery reduction), 
        physical side-channel analysis (SCA), fault injection (FI) attack mechanics, silicon-level countermeasures 
        (Dual-Modular Redundancy, active zeroization, OpenTitan Root of Trust), and assembly-level verification of machine artifacts.
    </div>
    <div class="part-chapters-list">
        <h4>Included Curriculum Chapters & Missions:</h4>
        <ul>
            <li><strong>Chapter 25:</strong> Post-Quantum Cryptography & Hardware Accelerators: NTT Mathematics</li>
            <li><strong>Chapter 26:</strong> Physical Attacks: Side-Channel Analysis (SCA) & Constant-Time Implementation</li>
            <li><strong>Chapter 27:</strong> Physical Attacks: Fault Injection (FI) & Silicon Countermeasures</li>
            <li><strong>Chapter 28:</strong> Hardware Verification & The Machine Artifact: Disassembly, Golden Models & Testing (Mission 13)</li>
        </ul>
    </div>
</div>

<!-- CHAPTER 25 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 25</span> &bull; 
        <span>Topic: Post-Quantum Cryptography, Lattice Rings, NTT Math & Montgomery Reduction</span> &bull; 
        <span>Standard: NIST FIPS 203 (ML-KEM) / FIPS 204 (ML-DSA)</span> &bull; 
        <span>Hardware Context: Cryptographic Accelerator Datapath</span>
    </div>

    <h1>Chapter 25: PQC Accelerators & NTT Mathematics</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Post-Quantum Cryptography (PQC):</strong> Cryptographic algorithms designed to remain secure against attacks 
            by both classical and large-scale quantum computers (which break RSA and ECC via Shor's Algorithm).<br>
            <strong>Module Learning with Errors (M-LWE):</strong> The mathematical hardness assumption underlying 
            NIST <strong>ML-KEM</strong> (formerly CRYSTALS-Kyber), based on the difficulty of finding secret vectors in high-dimensional lattices.<br>
            <strong>Polynomial Ring \(\mathcal{R}_q\):</strong> The algebraic structure \(\mathbb{Z}_q[X]/(X^{256} + 1)\), 
            where polynomials have 256 coefficients modulo prime \(q\) (in ML-KEM, \(q = 3329\)).<br>
            <strong>Number Theoretic Transform (NTT):</strong> A discrete Fourier transform over a finite field \(\mathbb{Z}_q\). 
            Transforms polynomial multiplication from \(O(n^2)\) schoolbook convolution into \(O(n \log n)\) pointwise multiplication.<br>
            <strong>Cooley-Tukey Butterfly Unit (BFU):</strong> The hardware arithmetic building block computing 
            \(A' = A + \omega \cdot B \pmod q\) and \(B' = A - \omega \cdot B \pmod q\), where \(\omega\) is a precomputed twiddle factor.<br>
            <strong>Montgomery Reduction:</strong> An algorithm computing \(a \cdot b \cdot R^{-1} \pmod q\) using only integer additions, 
            multiplications, and bitwise shifts, eliminating expensive hardware division units.
        </p>
    </div>

    <div class="diagram">
NTT HARDWARE ACCELERATOR DATAPATH (Single Butterfly Unit with Dual-Port BRAM):
+-----------------------------------------------------------------------------------+
| Address Generation Unit (AGU): Generates bit-reversed read/write indices          |
+-----------------------------------------------------------------------------------+
       |                                                               |
       v Read Port A                                                   v Read Port B
+-----------------------------------+               +-----------------------------------+
| Dual-Port BRAM Bank 0 (Coeff A)   |               | Dual-Port BRAM Bank 1 (Coeff B)   |
+-----------------------------------+               +-----------------------------------+
       |                                                               |
       |                                                               v
       |                                                    +---------------------------+
       |                                                    | Montgomery Multiplier (xW)|
       |                                                    +---------------------------+
       |                                                               |
       v                                                               v
+-----------------------------------------------------------------------------------+
| Butterfly Unit (BFU): AddSub Datapath:                                             |
|   A' = A + (W * B) mod q                                                          |
|   B' = A - (W * B) mod q                                                          |
+-----------------------------------------------------------------------------------+
       |                                                               |
       v Write Port A                                                  v Write Port B
+-----------------------------------------------------------------------------------+
| Write back to BRAM Banks (Conflict-Free ping-pong banking scheme)                 |
+-----------------------------------------------------------------------------------+
    </div>

    <h2>C++ Implementation: Montgomery Modular Multiplication</h2>
    <p>
        In Kyber/ML-KEM (\(q = 3329\), \(R = 2^{16} = 65536\), \(q^{-1} \equiv -3327 \pmod R\)):
    </p>

    <pre><code><span class="dir">#include</span> <span class="str">&lt;cstdint&gt;</span>

<span class="com">// Kyber / ML-KEM modulus parameters</span>
<span class="kwd">constexpr</span> <span class="typ">int32_t</span> KYBER_Q = <span class="num">3329</span>;
<span class="kwd">constexpr</span> <span class="typ">int32_t</span> QINV = -<span class="num">3327</span>; <span class="com">// q^(-1) mod 2^16</span>

<span class="com">// Constant-time Montgomery reduction: computes (a * R^(-1)) mod q</span>
<span class="kwd">constexpr</span> <span class="typ">int16_t</span> <span class="fn">montgomery_reduce</span>(<span class="typ">int32_t</span> a) {
    <span class="com">// u = (a * QINV) mod 2^16 (simulated by 16-bit integer truncation)</span>
    <span class="kwd">const</span> <span class="typ">int16_t</span> u = <span class="kwd">static_cast</span>&lt;<span class="typ">int16_t</span>&gt;(a * QINV);

    <span class="com">// t = (a - u * q) / 2^16 (simulated by arithmetic right shift 16)</span>
    <span class="kwd">const</span> <span class="typ">int32_t</span> t = (a - <span class="kwd">static_cast</span>&lt;<span class="typ">int32_t</span>&gt;(u) * KYBER_Q) &gt;&gt; <span class="num">16</span>;

    <span class="kwd">return</span> <span class="kwd">static_cast</span>&lt;<span class="typ">int16_t</span>&gt;(t);
}</code></pre>
</div>

<!-- CHAPTER 26 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 26</span> &bull; 
        <span>Topic: Side-Channel Attacks, Timing Invariance & Constant-Time Primitives</span> &bull; 
        <span>Standard: Physical Cryptanalysis</span> &bull; 
        <span>Hardware Context: CMOS Power Dissipation & Microarchitectural Invariance</span>
    </div>

    <h1>Chapter 26: Physical Attacks: Side-Channel Analysis (SCA)</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Side-Channel Analysis (SCA):</strong> Attacks that exploit physical information leaked during cryptographic execution 
            (execution time, instantaneous power consumption, electromagnetic radiation, acoustic emissions) rather than mathematical weaknesses.<br>
            <strong>Timing Attack:</strong> An SCA technique where variations in execution time (due to conditional branches or cache misses) 
            allow an attacker to reconstruct secret keys.<br>
            <strong>Power Analysis (SPA / DPA / CPA):</strong>
            <ul>
                <li><strong>Simple Power Analysis (SPA):</strong> Direct visual inspection of a single power consumption trace to identify cryptographic operations (e.g. distinguishing RSA square vs multiply).</li>
                <li><strong>Differential Power Analysis (DPA):</strong> Statistical analysis of thousands of power traces to detect minute correlation spikes between power consumption and hypothesized key bits.</li>
                <li><strong>Correlation Power Analysis (CPA):</strong> Using a Hamming Weight / Hamming Distance leakage model to extract keys.</li>
            </ul>
            <strong>Constant-Time Programming:</strong> A software discipline ensuring that execution flow, clock cycle count, 
            and memory access addresses are strictly invariant of secret data.
        </p>
    </div>

    <h2>The Physical Physics of Power Leakage</h2>
    <p>
        In CMOS silicon logic gates, power is consumed predominantly during <strong>logic state transitions</strong> 
        (\(0 \to 1\) or \(1 \to 0\)) charging parasitic capacitances:
    </p>
    \[
    P_{\text{dynamic}} = \alpha \cdot C \cdot V_{dd}^2 \cdot f
    \]
    <p>
        Where \(\alpha\) is the switching activity factor. If a register transitions from <code>0x0000</code> to <code>0xFFFF</code> 
        (16 bit-flips), it draws significantly more current from the power rail than transitioning from <code>0x0000</code> to <code>0x0001</code> (1 bit-flip). 
        An oscilloscope on the \(V_{dd}\) shunt resistor detects this difference instantly!
    </p>

    <h2>C++ Implementation: Branchless Constant-Time Primitives</h2>
    <div class="callout callout-sec">
        <div class="callout-header">The Secret Branch Vulnerability</div>
        <pre><code><span class="com">// VULNERABLE: Execution time leaks secret key byte!</span>
<span class="typ">bool</span> <span class="fn">vulnerable_verify</span>(<span class="kwd">const</span> <span class="typ">uint8_t</span>* key, <span class="kwd">const</span> <span class="typ">uint8_t</span>* input, <span class="typ">size_t</span> len) {
    <span class="kwd">for</span> (<span class="typ">size_t</span> i = <span class="num">0</span>; i &lt; len; ++i) {
        <span class="kwd">if</span> (key[i] != input[i]) <span class="kwd">return</span> <span class="kwd">false</span>; <span class="com">// Early exit timing leak!</span>
    }
    <span class="kwd">return</span> <span class="kwd">true</span>;
}</code></pre>
    </div>

    <pre><code><span class="dir">#include</span> <span class="str">&lt;cstdint&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;cstddef&gt;</span>

<span class="com">// CONSTANT-TIME SECURE IMPLEMENTATION</span>

<span class="com">// 1. Constant-time equality: returns 0xFFFFFFFF if a == b, else 0x00000000</span>
<span class="kwd">constexpr</span> <span class="typ">uint32_t</span> <span class="fn">ct_is_equal</span>(<span class="typ">uint32_t</span> a, <span class="typ">uint32_t</span> b) {
    <span class="kwd">const</span> <span class="typ">uint32_t</span> diff = a ^ b;
    <span class="com">// If diff == 0, (diff | -diff) has MSB 0; if diff != 0, MSB is 1</span>
    <span class="kwd">const</span> <span class="typ">uint32_t</span> non_zero = (diff | (~diff + <span class="num">1</span>)) &gt;&gt; <span class="num">31</span>;
    <span class="kwd">return</span> (non_zero ^ <span class="num">1</span>) ? <span class="num">0xFFFFFFFFu</span> : <span class="num">0u</span>;
}

<span class="com">// 2. Constant-time conditional multiplexer: returns 'a' if mask == 0xFFFFFFFF, else 'b'</span>
<span class="com">// Executes identically in constant cycles with zero conditional branch instructions!</span>
<span class="kwd">constexpr</span> <span class="typ">uint32_t</span> <span class="fn">ct_select</span>(<span class="typ">uint32_t</span> mask, <span class="typ">uint32_t</span> a, <span class="typ">uint32_t</span> b) {
    <span class="kwd">return</span> (a &amp; mask) | (b &amp; ~mask);
}

<span class="com">// 3. Constant-time buffer verification: examines all bytes unconditionally</span>
<span class="typ">bool</span> <span class="fn">ct_verify</span>(<span class="kwd">const</span> <span class="typ">uint8_t</span>* a, <span class="kwd">const</span> <span class="typ">uint8_t</span>* b, std::<span class="typ">size_t</span> len) {
    <span class="typ">uint8_t</span> accumulator = <span class="num">0</span>;
    <span class="kwd">for</span> (std::<span class="typ">size_t</span> i = <span class="num">0</span>; i &lt; len; ++i) {
        accumulator |= (a[i] ^ b[i]); <span class="com">// Bitwise accumulate differences</span>
    }
    <span class="kwd">return</span> accumulator == <span class="num">0</span>;
}</code></pre>
</div>

<!-- CHAPTER 27 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 27</span> &bull; 
        <span>Topic: Fault Injection (FI), Glitching Vectors & Silicon Defenses</span> &bull; 
        <span>Standard: Hardware Security Engineering</span> &bull; 
        <span>Hardware Context: Active Tamper Envelopes & DMR Circuits</span>
    </div>

    <h1>Chapter 27: Physical Attacks: Fault Injection & Defenses</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Fault Injection (FI):</strong> Deliberately perturbing the physical operating conditions of a semiconductor chip 
            to induce bit-flips, instruction skips, or invalid intermediate states during security-critical operations.<br>
            <strong>Clock Glitching:</strong> Inserting an ultra-narrow clock pulse that violates flip-flop setup time (\(t_{\text{setup}}\)), 
            causing combinatorial logic outputs to be latched before settling.<br>
            <strong>Voltage Glitching:</strong> Briefly dropping the supply rail (\(V_{dd}\)) below operating margins, 
            slowing CMOS transistor propagation delays and corrupting instructions.<br>
            <strong>Laser Fault Injection (LFI):</strong> Focusing an infrared laser pulse onto the backside silicon substrate, 
            generating electron-hole pairs that flip specific SRAM cells or logic registers.<br>
            <strong>Dual-Modular Redundancy (DMR):</strong> Running two identical hardware cores or execution pipelines in parallel 
            (often with a temporal offset) and continuously comparing outputs; asserting a security trap if a discrepancy is detected.<br>
            <strong>Active Zeroization:</strong> Dedicated hardware circuitry that physically wipes cryptographic keys and SRAM registers 
            (grounding gates or asserting synchronous clear) immediately upon tamper detection.
        </p>
    </div>

    <div class="diagram">
DUAL-MODULAR REDUNDANCY (DMR) SILICON ARCHITECTURE WITH TAMPER ZEROIZATION:
+-----------------------------------+               +-----------------------------------+
| Primary Hardware Core (Ibex A)    |               | Shadow Core (Ibex B - Staggered 2c)|
+-----------------------------------+               +-----------------------------------+
       |                                                               |
       | Bus Output A                                                  | Bus Output B
       \-------------------------------\               /---------------/
                                       v               v
                           +---------------------------------------+
                           | Lockstep Comparator Logic             |
                           +---------------------------------------+
                                        |
                          +-------------+-------------+
                          | Match                     | Discrepancy (Fault Detected!)
                          v                           v
              +-----------------------+   +---------------------------------------------+
              | Commit Bus Operation  |   | 1. Assert Security Alert Interrupt to GIC   |
              +-----------------------+   | 2. Immediately HALT CPU Execution Pipeline |
                                          | 3. Trigger Active Key Zeroization (Ground)  |
                                          +---------------------------------------------+
    </div>

    <h2>SystemVerilog Countermeasure: Hardware Zeroization Circuit</h2>
    <pre><code><span class="com">// Synthesizable SystemVerilog fault-tolerant register block with zeroization</span>
<span class="kwd">module</span> <span class="typ">secure_key_vault</span> (
    <span class="kwd">input</span>  <span class="kwd">logic</span>        clk_i,
    <span class="kwd">input</span>  <span class="kwd">logic</span>        rst_ni,
    <span class="kwd">input</span>  <span class="kwd">logic</span>        tamper_alert_i, <span class="com">// From voltage/clock glitch detector</span>
    <span class="kwd">input</span>  <span class="kwd">logic</span>        key_write_en_i,
    <span class="kwd">input</span>  <span class="kwd">logic</span> [255:0] key_data_i,
    <span class="kwd">output</span> <span class="kwd">logic</span> [255:0] key_data_o
);

    <span class="kwd">logic</span> [255:0] key_reg_q;

    <span class="kwd">always_ff</span> @(<span class="kwd">posedge</span> clk_i <span class="kwd">or</span> <span class="kwd">negedge</span> rst_ni) <span class="kwd">begin</span>
        <span class="kwd">if</span> (!rst_ni) <span class="kwd">begin</span>
            key_reg_q &lt;= 256'h0;
        <span class="kwd">end</span> <span class="kwd">else if</span> (tamper_alert_i) <span class="kwd">begin</span>
            <span class="com">// HARDWARE ZEROIZATION: Immediate single-cycle physical overwrite</span>
            key_reg_q &lt;= 256'h0;
        <span class="kwd">end</span> <span class="kwd">else if</span> (key_write_en_i) <span class="kwd">begin</span>
            key_reg_q &lt;= key_data_i;
        <span class="kwd">end</span>
    <span class="kwd">end</span>

    <span class="kwd">assign</span> key_data_o = key_reg_q;

<span class="kwd">endmodule</span></code></pre>
</div>

<!-- CHAPTER 28 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 28</span> &bull; 
        <span>Topic: Verification Philosophy, Disassembly Inspection & Dead Store Elimination</span> &bull; 
        <span>Standard: C++20 / Assembly</span> &bull; 
        <span>Codebase Link: Mission 13 (Self-Checking Harness)</span>
    </div>

    <h1>Chapter 28: Hardware Verification & The Machine Artifact</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Machine Artifact:</strong> The physical binary machine instructions executed by silicon hardware. 
            <em>In hardware security, the source code is only a proposal; the machine artifact is what actually executes.</em><br>
            <strong>Differential Testing:</strong> A testing methodology where two independent implementations of the same specification 
            (e.g., an ANSI C golden model vs synthesizable SystemVerilog RTL in Verilator) are executed across millions of randomized inputs 
            to detect single-bit divergence.<br>
            <strong>Golden Vectors:</strong> Standardized test vectors providing known, mathematically validated inputs and outputs 
            (e.g., NIST Known Answer Tests / KAT).<br>
            <strong>Dead Store Elimination (DSE):</strong> An optimizing compiler optimization that removes memory writes if the compiler 
            can prove the written memory is never subsequently read before function return or deallocation.<br>
            <strong>Secure Zeroization in Software:</strong> Techniques that force the compiler to preserve sensitive memory wiping.
        </p>
    </div>

    <h2>The Dead Store Elimination Trap</h2>
    <div class="callout callout-sec">
        <div class="callout-header">Why memset() Leaves Cryptographic Keys in RAM</div>
        <p>
            Consider this routine in a cryptographic firmware driver:
            <pre><code><span class="typ">void</span> <span class="fn">crypto_sign</span>(...) {
    <span class="typ">uint8_t</span> secret_key[<span class="num">32</span>];
    <span class="fn">derive_key</span>(secret_key);
    <span class="fn">perform_signature</span>(secret_key);

    <span class="com">// DEVELOPER INTENT: Scrub secret key from stack before returning</span>
    std::<span class="fn">memset</span>(secret_key, <span class="num">0</span>, <span class="kwd">sizeof</span>(secret_key));
}</code></pre>
            <strong>The Catastrophe:</strong> When compiled at <code>-O2</code>, the compiler observes that <code>secret_key</code> 
            is a local stack buffer and is never read again. Under the C++ as-if rule, the compiler's Dead Store Elimination pass 
            <strong>completely removes the <code>memset</code> call!</strong> 
            The secret cryptographic key remains in physical stack SRAM, where it is easily extracted by cold-boot attacks or buffer overflows.
        </p>
    </div>

    <h2>C++ Implementation: Compiler-Guaranteed Secure Zeroization</h2>
    <pre><code><span class="dir">#include</span> <span class="str">&lt;cstddef&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;cstdint&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;cstring&gt;</span>

<span class="com">// Technique 1: Volatile pointer scrub (compiler is forbidden from eliding volatile writes)</span>
<span class="typ">void</span> <span class="fn">secure_wipe_volatile</span>(<span class="typ">void</span>* buffer, std::<span class="typ">size_t</span> len) {
    <span class="kwd">volatile</span> <span class="typ">uint8_t</span>* p = <span class="kwd">static_cast</span>&lt;<span class="kwd">volatile</span> <span class="typ">uint8_t</span>*&gt;(buffer);
    <span class="kwd">while</span> (len--) {
        *p++ = <span class="num">0</span>;
    }
}

<span class="com">// Technique 2: Inline assembly memory clobber barrier</span>
<span class="typ">void</span> <span class="fn">secure_wipe_barrier</span>(<span class="typ">void</span>* buffer, std::<span class="typ">size_t</span> len) {
    <span class="kwd">if</span> (buffer == <span class="kwd">nullptr</span> || len == <span class="num">0</span>) <span class="kwd">return</span>;
    std::<span class="fn">memset</span>(buffer, <span class="num">0</span>, len);
    <span class="com">// Assembly clobber tells compiler that unknown assembly instructions read all memory,</span>
    <span class="com">// completely blocking Dead Store Elimination!</span>
    <span class="kwd">asm</span> <span class="kwd">volatile</span>(<span class="str">""</span> : : <span class="str">"r"</span>(buffer) : <span class="str">"memory"</span>);
}</code></pre>
</div>
"""
