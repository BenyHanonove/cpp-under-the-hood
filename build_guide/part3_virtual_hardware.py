"""
part3_virtual_hardware.py - Part III: Virtual Hardware Modeling, Dynamic Dispatch & Systems Interoperability
"""

def get_part3_html():
    return r"""
<!-- PART III COVER -->
<div class="part-page">
    <div class="part-number">Part III</div>
    <div class="part-title">Virtual Hardware Modeling, Dynamic Dispatch & Systems Interoperability</div>
    <div class="part-desc">
        Hardware design cycles begin long before silicon tape-out through cycle-accurate software simulation. 
        Engineers model complete Systems-on-Chip (SoCs), memory interconnects, and cryptographic accelerators in C++. 
        This part investigates the hidden memory costs and security vulnerabilities of dynamic dispatch (vtables, object slicing, 
        vptr hijacking), implements a complete virtual peripheral bus tree, bridges the C and C++ ABI boundary across multi-language builds, 
        and leverages C++20 Concepts and compile-time <code>consteval</code> metaprogramming to eliminate runtime verification costs.
    </div>
    <div class="part-chapters-list">
        <h4>Included Curriculum Chapters & Missions:</h4>
        <ul>
            <li><strong>Chapter 11:</strong> Dynamic Dispatch, Vtables, Object Slicing & Security Exploits (Mission 05)</li>
            <li><strong>Chapter 12:</strong> Architectural Simulation: Modeling Peripheral Trees & Buses (Mission 05)</li>
            <li><strong>Chapter 13:</strong> The Two-Language Build: Translation Units, Linkage & C Interoperability (Mission 09)</li>
            <li><strong>Chapter 14:</strong> Compile-Time Metaprogramming with C++20 Concepts & <code>constexpr</code> (Mission 10)</li>
        </ul>
    </div>
</div>

<!-- CHAPTER 11 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 11</span> &bull; 
        <span>Topic: Virtual Dispatch, Vtable Layout, Object Slicing & Vptr Hijacking</span> &bull; 
        <span>Standard: C++20</span> &bull; 
        <span>Codebase Link: Mission 05 (Virtual Peripheral Tree)</span>
    </div>

    <h1>Chapter 11: Dynamic Dispatch, Vtables, Slicing & Security Exploits</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Dynamic Dispatch:</strong> The process of selecting which implementation of a polymorphic function to execute 
            at runtime based on the dynamic type of the object.<br>
            <strong>Virtual Method Table (<code>vtable</code>):</strong> An array of function pointers created by the compiler for 
            every class containing virtual functions. Each entry points to the most derived virtual function implementation.<br>
            <strong>Virtual Pointer (<code>_vptr</code>):</strong> A hidden pointer inserted by the compiler as the first member 
            (offset 0) of every object whose class defines virtual functions. Points directly to the class's <code>vtable</code>.<br>
            <strong>Object Slicing:</strong> The loss of derived-class state that occurs when a derived object is assigned by value 
            to a base-class variable (e.g. <code>Base b = derived;</code>). The compiler copies only the base members and resets 
            the <code>_vptr</code> to <code>Base::vtable</code>, effectively slicing off all derived state.<br>
            <strong>The <code>override</code> Keyword:</strong> Explicit compiler annotation ensuring that a member function matches 
            a base-class virtual function signature. A typo in the parameter types will cause a compilation error instead of silent shadowing.<br>
            <strong>The <code>final</code> Keyword:</strong> Designates that a virtual function cannot be overridden, or a class cannot 
            be inherited from, allowing the compiler to perform <strong>devirtualization</strong> optimizations.
        </p>
    </div>

    <h2>The Physical Memory Cost of Virtualization</h2>
    <p>
        Virtualization is not free. In Mission 05, comparing <code>sizeof(PlainDevice)</code> vs <code>sizeof(VirtualDevice)</code> 
        reveals the hidden hardware overhead:
    </p>

    <div class="diagram">
PLAIN OBJECT MEMORY LAYOUT (No Virtual Functions):
+------------------------------------+------------------------------------+
| uint32_t base_address (4 Bytes)     | uint32_t register_count (4 Bytes)  | Total = 8 Bytes
+------------------------------------+------------------------------------+
Offset: 0                            4

VIRTUAL OBJECT MEMORY LAYOUT (With Virtual Functions):
+-------------------------------------------------------------------------+
| const void* _vptr (8 Bytes) ----&gt; Points to Peripheral::vtable in .rodata|
+------------------------------------+------------------------------------+
| uint32_t base_address (4 Bytes)     | uint32_t register_count (4 Bytes)  | Total = 16 Bytes (100% bloat!)
+------------------------------------+------------------------------------+
Offset: 0                            8                                    12
    </div>

    <h2>The "Why": The Mandatory Virtual Destructor</h2>
    <div class="callout callout-sec">
        <div class="callout-header">The Non-Virtual Destructor Memory Leak</div>
        <p>
            If an object of a derived class (e.g. <code>LeakyDerived</code> owning dynamic heap memory) is deleted through a base-class 
            pointer (<code>Peripheral* p = new LeakyDerived(); delete p;</code>) and <code>Peripheral</code> does NOT declare its 
            destructor <code>virtual</code>:
            <br>
            <strong>The Catastrophe:</strong> The compiler resolves the destructor call statically to <code>Peripheral::~Peripheral()</code>. 
            The derived destructor <code>LeakyDerived::~LeakyDerived()</code> is <em>never called</em>! 
            All resources owned by the derived class leak permanently, and the ISO standard defines this as <strong>Undefined Behavior</strong>.
        </p>
    </div>

    <h2>Silicon Security Vulnerability: Vtable Hijacking</h2>
    <p>
        In low-level security, the <code>_vptr</code> is an attack vector. Because <code>_vptr</code> lives at offset 0 of an object in RAM, 
        a heap buffer overflow in a neighboring buffer can overwrite the <code>_vptr</code> with an arbitrary address. 
        When software subsequently invokes a virtual function (e.g. <code>peripheral-&gt;read32(...)</code>), the CPU dereferences 
        the attacker's counterfeit vtable and jumps to malicious shellcode or Return-Oriented Programming (ROP) gadgets.
    </p>

    <div class="callout callout-arm">
        <div class="callout-header">Hardware Countermeasure: ARM PAC (Pointer Authentication)</div>
        <p>
            To defeat vtable hijacking, modern <strong>ARMv8.3-A / ARMv9-A</strong> architectures introduce 
            <strong>Pointer Authentication Codes (PAC)</strong>. When a virtual function pointer is compiled, instruction 
            <code>PACIA</code> signs the upper unused bits of the 64-bit pointer with a cryptographic MAC using a secret CPU key. 
            Before indirect branch instruction <code>BLRAA</code> executes, the CPU validates the PAC signature with <code>AUTIA</code>. 
            If an attacker modified the vtable pointer, authentication fails and the CPU triggers an immediate kernel panic!
        </p>
    </div>
</div>

<!-- CHAPTER 12 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 12</span> &bull; 
        <span>Topic: Virtual Peripheral Modeling, Address Decoding & System Bus Trees</span> &bull; 
        <span>Standard: C++20</span> &bull; 
        <span>Codebase Link: Mission 05 (Virtual Peripheral Tree)</span>
    </div>

    <h1>Chapter 12: Architectural Simulation: Modeling Peripheral Trees</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Virtual Peripheral Tree:</strong> An object-oriented simulation architecture modeling a memory interconnect 
            and attached hardware devices.<br>
            <strong>System Bus Arbiter:</strong> The simulated interconnect routing read/write transactions from CPU masters 
            to destination peripheral slaves based on physical base address ranges.<br>
            <strong>Address Decoding:</strong> The mathematical hardware logic that checks if transaction address \(A\) falls within 
            \([\text{Base}, \text{Base} + \text{Size})\) and computes relative offset \(A - \text{Base}\).<br>
            <strong>Cycle Stepping (<code>tick()</code>):</strong> Simulating synchronous hardware clock transitions to advance internal 
            finite state machines (FSMs), decrement timers, and shift UART FIFOs.
        </p>
    </div>

    <h2>C++ Implementation: The Abstract Peripheral Interface & Bus</h2>
    <p>
        The following architecture from Mission 05 enables uniform bus dispatch across distinct hardware blocks:
    </p>

    <pre><code><span class="dir">#pragma once</span>

<span class="dir">#include</span> <span class="str">&lt;cstddef&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;cstdint&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;memory&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;stdexcept&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;string&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;vector&gt;</span>

<span class="com">// Abstract base interface representing any hardware peripheral on the SoC</span>
<span class="kwd">class</span> <span class="typ">Peripheral</span> {
<span class="kwd">public</span>:
    <span class="com">// Mandatory virtual destructor</span>
    <span class="kwd">virtual</span> ~<span class="fn">Peripheral</span>() = <span class="kwd">default</span>;

    <span class="com">// Pure virtual bus interface</span>
    <span class="kwd">virtual</span> <span class="typ">uint32_t</span> <span class="fn">read32</span>(std::<span class="typ">size_t</span> offset) <span class="kwd">const</span> = <span class="num">0</span>;
    <span class="kwd">virtual</span> <span class="typ">void</span> <span class="fn">write32</span>(std::<span class="typ">size_t</span> offset, <span class="typ">uint32_t</span> value) = <span class="num">0</span>;
    <span class="kwd">virtual</span> <span class="typ">void</span> <span class="fn">reset</span>() = <span class="num">0</span>;
    <span class="kwd">virtual</span> std::<span class="typ">string</span> <span class="fn">name</span>() <span class="kwd">const</span> = <span class="num">0</span>;
    <span class="kwd">virtual</span> std::<span class="typ">size_t</span> <span class="fn">size</span>() <span class="kwd">const</span> = <span class="num">0</span>;
};

<span class="com">// Concrete Hardware Device 1: Programmable Hardware Timer</span>
<span class="kwd">class</span> <span class="typ">TimerPeripheral</span> : <span class="kwd">public</span> <span class="typ">Peripheral</span> {
<span class="kwd">public</span>:
    <span class="kwd">static</span> <span class="kwd">constexpr</span> std::<span class="typ">size_t</span> reg_ctrl = <span class="num">0x00</span>;
    <span class="kwd">static</span> <span class="kwd">constexpr</span> std::<span class="typ">size_t</span> reg_count = <span class="num">0x04</span>;
    <span class="kwd">static</span> <span class="kwd">constexpr</span> std::<span class="typ">size_t</span> reg_compare = <span class="num">0x08</span>;
    <span class="kwd">static</span> <span class="kwd">constexpr</span> std::<span class="typ">size_t</span> reg_status = <span class="num">0x0C</span>;

    <span class="typ">uint32_t</span> <span class="fn">read32</span>(std::<span class="typ">size_t</span> offset) <span class="kwd">const</span> <span class="kwd">override</span> {
        <span class="kwd">if</span> (offset == reg_ctrl) <span class="kwd">return</span> _ctrl;
        <span class="kwd">if</span> (offset == reg_count) <span class="kwd">return</span> _count;
        <span class="kwd">if</span> (offset == reg_compare) <span class="kwd">return</span> _compare;
        <span class="kwd">if</span> (offset == reg_status) <span class="kwd">return</span> _match ? <span class="num">1u</span> : <span class="num">0u</span>;
        <span class="kwd">throw</span> std::<span class="typ">out_of_range</span>(<span class="str">"Timer: Invalid register offset"</span>);
    }

    <span class="typ">void</span> <span class="fn">write32</span>(std::<span class="typ">size_t</span> offset, <span class="typ">uint32_t</span> val) <span class="kwd">override</span> {
        <span class="kwd">if</span> (offset == reg_ctrl) { _ctrl = val &amp; <span class="num">0x1u</span>; }
        <span class="kwd">else</span> <span class="kwd">if</span> (offset == reg_compare) { _compare = val; }
        <span class="kwd">else</span> <span class="kwd">if</span> (offset == reg_status) {
            <span class="com">// Write-1-to-Clear (W1C) implementation</span>
            <span class="kwd">if</span> (val &amp; <span class="num">0x1u</span>) { _match = <span class="kwd">false</span>; }
        }
    }

    <span class="typ">void</span> <span class="fn">tick</span>() {
        <span class="kwd">if</span> (_ctrl &amp; <span class="num">0x1u</span>) {
            ++_count;
            <span class="kwd">if</span> (_count == _compare) { _match = <span class="kwd">true</span>; }
        }
    }

    <span class="typ">void</span> <span class="fn">reset</span>() <span class="kwd">override</span> { _ctrl = <span class="num">0</span>; _count = <span class="num">0</span>; _compare = <span class="num">0</span>; _match = <span class="kwd">false</span>; }
    std::<span class="typ">string</span> <span class="fn">name</span>() <span class="kwd">const</span> <span class="kwd">override</span> { <span class="kwd">return</span> <span class="str">"SoC_Timer_v1"</span>; }
    std::<span class="typ">size_t</span> <span class="fn">size</span>() <span class="kwd">const</span> <span class="kwd">override</span> { <span class="kwd">return</span> <span class="num">0x10</span>; }

<span class="kwd">private</span>:
    <span class="typ">uint32_t</span> _ctrl{<span class="num">0</span>};
    <span class="typ">uint32_t</span> _count{<span class="num">0</span>};
    <span class="typ">uint32_t</span> _compare{<span class="num">0</span>};
    <span class="typ">bool</span> _match{<span class="kwd">false</span>};
};

<span class="com">// System Bus routing transactions to mapped devices</span>
<span class="kwd">class</span> <span class="typ">Bus</span> {
<span class="kwd">public</span>:
    <span class="kwd">struct</span> <span class="typ">Mapping</span> {
        <span class="typ">uint32_t</span> base;
        <span class="typ">uint32_t</span> limit;
        <span class="typ">Peripheral</span>* dev;
    };

    <span class="typ">void</span> <span class="fn">attach</span>(<span class="typ">uint32_t</span> base_addr, <span class="typ">Peripheral</span>* dev) {
        <span class="kwd">const</span> <span class="typ">uint32_t</span> limit = base_addr + dev-&gt;<span class="fn">size</span>();
        <span class="kwd">for</span> (<span class="kwd">const</span> <span class="kwd">auto</span>&amp; m : _devices) {
            <span class="kwd">if</span> (!(limit &lt;= m.base || base_addr &gt;= m.limit)) {
                <span class="kwd">throw</span> std::<span class="typ">invalid_argument</span>(<span class="str">"Bus: Overlapping address map"</span>);
            }
        }
        _devices.push_back({base_addr, limit, dev});
    }

    <span class="typ">uint32_t</span> <span class="fn">read32</span>(<span class="typ">uint32_t</span> addr) <span class="kwd">const</span> {
        <span class="kwd">for</span> (<span class="kwd">const</span> <span class="kwd">auto</span>&amp; m : _devices) {
            <span class="kwd">if</span> (addr &gt;= m.base &amp;&amp; addr &lt; m.limit) {
                <span class="kwd">return</span> m.dev-&gt;<span class="fn">read32</span>(addr - m.base);
            }
        }
        <span class="kwd">throw</span> std::<span class="typ">out_of_range</span>(<span class="str">"Bus: Unmapped address read access"</span>);
    }

    <span class="typ">void</span> <span class="fn">write32</span>(<span class="typ">uint32_t</span> addr, <span class="typ">uint32_t</span> val) {
        <span class="kwd">for</span> (<span class="kwd">const</span> <span class="kwd">auto</span>&amp; m : _devices) {
            <span class="kwd">if</span> (addr &gt;= m.base &amp;&amp; addr &lt; m.limit) {
                m.dev-&gt;<span class="fn">write32</span>(addr - m.base, val);
                <span class="kwd">return</span>;
            }
        }
        <span class="kwd">throw</span> std::<span class="typ">out_of_range</span>(<span class="str">"Bus: Unmapped address write access"</span>);
    }

<span class="kwd">private</span>:
    std::<span class="typ">vector</span>&lt;<span class="typ">Mapping</span>&gt; _devices;
};</code></pre>
</div>

<!-- CHAPTER 13 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 13</span> &bull; 
        <span>Topic: Translation Units, Linkage, Name Mangling & The C/C++ Boundary</span> &bull; 
        <span>Standard: C++20 / C99</span> &bull; 
        <span>Codebase Link: Mission 09 (Two-Language Build)</span>
    </div>

    <h1>Chapter 13: The Two-Language Build: Linkage & C Interoperability</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Translation Unit (TU):</strong> A single source code file (<code>.c</code> or <code>.cpp</code>) after undergoing 
            preprocessor expansion (including all included headers and expanded macros).<br>
            <strong>One Definition Rule (ODR):</strong> C++ standard requirement stating that any variable, function, class, or template 
            must have exactly one definition across the entire program (unless marked <code>inline</code>).<br>
            <strong>Internal Linkage (<code>static</code> / Anonymous Namespaces):</strong> A symbol whose name is private to its 
            own translation unit and invisible to the external linker.<br>
            <strong>External Linkage:</strong> A symbol visible across different translation units during the linking phase.<br>
            <strong>Name Mangling:</strong> The C++ compiler process of altering function names into encoded symbol strings 
            (e.g., <code>read_register(uint32_t)</code> becomes <code>_Z13read_registerj</code>) to support function overloading.<br>
            <strong>C Linkage (<code>extern "C"</code>):</strong> Directs the C++ compiler to suppress name mangling, emitting standard 
            unmangled C symbol names (e.g. <code>read_register</code>).
        </p>
    </div>

    <h2>The "Why": The Multi-Language Verification Pipeline</h2>
    <p>
        In Month 1 and Month 2 of the roadmap, your verification pipeline takes this exact shape:
    </p>

    <div class="diagram">
+----------------------------+       +-----------------------------+       +----------------------------+
| SystemVerilog RTL Design   |       | C Reference Crypto Model    |       | C++ Simulation Harness     |
| (Synthesizable Accelerator)|       | (Pure ANSI C Math Routines) |       | (Verilator Driver / Bus)   |
+----------------------------+       +-----------------------------+       +----------------------------+
              |                                     |                                     |
              v (Transpiled by Verilator)           v (Compiled by GCC)                   v (Compiled by G++)
+----------------------------+       +-----------------------------+       +----------------------------+
| Verilated C++ Object Files |       | C Object Files (ntt_c.o)    |       | C++ Testbench (driver.o)   |
+----------------------------+       +-----------------------------+       +----------------------------+
              \                                     |                                     /
               \------------------------------------+------------------------------------/
                                                    | (Linked together via ld / g++)
                                                    v
                               +-----------------------------------------+
                               | Single Co-Simulation Binary Executable  |
                               +-----------------------------------------+
    </div>

    <h2>C++ Implementation: Safe Cross-Language Header Design</h2>
    <p>
        To allow a header to be included safely by both pure C compilers (e.g. for bare-metal RISC-V firmware) and C++ compilers 
        (for Verilator testbenches), wrap function declarations using conditional linkage guards:
    </p>

    <pre><code><span class="dir">#ifndef HARDWARE_CRYPTO_BRIDGE_H</span>
<span class="dir">#define HARDWARE_CRYPTO_BRIDGE_H</span>

<span class="dir">#include</span> <span class="str">&lt;stdint.h&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;stddef.h&gt;</span>

<span class="com">/* Enforce C linkage when compiled by a C++ compiler */</span>
<span class="dir">#ifdef __cplusplus</span>
<span class="kwd">extern</span> <span class="str">"C"</span> {
<span class="dir">#endif</span>

<span class="com">/* Binary struct layout guaranteed identical in both C and C++ */</span>
<span class="kwd">typedef</span> <span class="kwd">struct</span> {
    <span class="typ">uint32_t</span> base_address;
    <span class="typ">uint32_t</span> length;
    <span class="typ">uint32_t</span> status_flags;
} <span class="typ">CryptoBridgeConfig</span>;

<span class="com">/* C-compatible functions callable from C++ harnesses */</span>
<span class="typ">int</span> <span class="fn">crypto_bridge_init</span>(<span class="kwd">const</span> <span class="typ">CryptoBridgeConfig</span>* config);
<span class="typ">uint32_t</span> <span class="fn">crypto_bridge_compute_ntt</span>(<span class="kwd">const</span> <span class="typ">uint32_t</span>* input, <span class="typ">uint32_t</span>* output, <span class="typ">size_t</span> len);

<span class="dir">#ifdef __cplusplus</span>
}
<span class="dir">#endif</span>

<span class="dir">#endif</span> <span class="com">/* HARDWARE_CRYPTO_BRIDGE_H */</span></code></pre>
</div>

<!-- CHAPTER 14 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 14</span> &bull; 
        <span>Topic: C++20 Concepts, Compile-Time Constraints & Immediate Functions</span> &bull; 
        <span>Standard: C++20</span> &bull; 
        <span>Codebase Link: Mission 10 (Compile-Time Math Core)</span>
    </div>

    <h1>Chapter 14: Compile-Time Metaprogramming with C++20 Concepts</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>C++20 Concepts:</strong> Named compile-time predicates that evaluate whether template arguments satisfy 
            specific syntactic and semantic constraints. Replaces unreadable SFINAE (<code>std::enable_if_t</code>) with direct compiler errors.<br>
            <strong>The <code>requires</code> Clause:</strong> Language keyword specifying requirements on template parameters 
            (e.g., supported operators, member types, return types).<br>
            <strong><code>constexpr</code>:</strong> Specifies that a function or variable <em>can</em> be evaluated at compile time if all 
            inputs are compile-time constants, but will execute at runtime otherwise.<br>
            <strong><code>consteval</code> (Immediate Function):</strong> C++20 keyword guaranteeing that a function <em>must</em> 
            produce a compile-time constant. Calling a <code>consteval</code> function with runtime arguments produces an immediate compile error.
        </p>
    </div>

    <h2>The "Why": Zero-Cost Crypto Precomputations</h2>
    <p>
        In post-quantum algorithms (ML-KEM / ML-DSA), the Number Theoretic Transform (NTT) requires multiplying polynomials by 
        precomputed powers of the primitive \(256\)-th root of unity (the "twiddle factors" \(\psi^i \pmod q\)). 
        Calculating these twiddle factors at runtime wastes precious clock cycles and battery power. 
        Using C++20 <code>constexpr</code> and <code>consteval</code>, you compute the twiddle factor tables and modular inverses 
        <strong>at compile time</strong>, baking the values directly into the read-only flash memory of the microcontroller.
    </p>

    <h2>C++ Implementation: The Type-Enforced Compile-Time Math Core</h2>
    <pre><code><span class="dir">#pragma once</span>

<span class="dir">#include</span> <span class="str">&lt;concepts&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;cstdint&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;type_traits&gt;</span>

<span class="com">// 1. CONCEPT DEFINITION: Enforces arithmetic and comparison support</span>
<span class="kwd">template</span> &lt;<span class="kwd">typename</span> <span class="typ">T</span>&gt;
<span class="kwd">concept</span> <span class="typ">Numeric</span> = <span class="kwd">requires</span>(<span class="typ">T</span> a, <span class="typ">T</span> b) {
    { a + b } -&gt; std::<span class="typ">convertible_to</span>&lt;<span class="typ">T</span>&gt;;
    { a - b } -&gt; std::<span class="typ">convertible_to</span>&lt;<span class="typ">T</span>&gt;;
    { a * b } -&gt; std::<span class="typ">convertible_to</span>&lt;<span class="typ">T</span>&gt;;
    { a == b } -&gt; std::<span class="typ">convertible_to</span>&lt;<span class="typ">bool</span>&gt;;
} &amp;&amp; std::<span class="typ">is_default_constructible_v</span>&lt;<span class="typ">T</span>&gt;;

<span class="com">// 2. CONSTRAINED TEMPLATE: Rejects unsupported types at the class boundary</span>
<span class="kwd">template</span> &lt;<span class="typ">Numeric</span> <span class="typ">T</span>&gt;
<span class="kwd">struct</span> <span class="typ">Vector3D</span> {
    <span class="typ">T</span> x{};
    <span class="typ">T</span> y{};
    <span class="typ">T</span> z{};

    <span class="kwd">constexpr</span> <span class="fn">Vector3D</span>() = <span class="kwd">default</span>;
    <span class="kwd">constexpr</span> <span class="fn">Vector3D</span>(<span class="typ">T</span> x_, <span class="typ">T</span> y_, <span class="typ">T</span> z_) : x(x_), y(y_), z(z_) {}

    <span class="com">// Immediate function: MUST evaluate at compile time</span>
    <span class="kwd">consteval</span> <span class="typ">T</span> <span class="fn">dot</span>(<span class="kwd">const</span> <span class="typ">Vector3D</span>&amp; other) <span class="kwd">const</span> {
        <span class="kwd">return</span> (x * other.x) + (y * other.y) + (z * other.z);
    }
};

<span class="com">// 3. COMPILE-TIME VERIFICATION: Evaluated by the compiler frontend</span>
<span class="kwd">constexpr</span> <span class="typ">Vector3D</span>&lt;<span class="typ">int32_t</span>&gt; v1{<span class="num">1</span>, <span class="num">2</span>, <span class="num">3</span>};
<span class="kwd">constexpr</span> <span class="typ">Vector3D</span>&lt;<span class="typ">int32_t</span>&gt; v2{<span class="num">4</span>, -<span class="num">5</span>, <span class="num">6</span>};

<span class="com">// (1*4) + (2*-5) + (3*6) = 4 - 10 + 18 = 12</span>
<span class="kwd">static_assert</span>(v1.<span class="fn">dot</span>(v2) == <span class="num">12</span>, <span class="str">"Compile-time dot product math error!"</span>);</code></pre>
</div>
"""
