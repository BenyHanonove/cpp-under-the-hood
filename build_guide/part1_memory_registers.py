"""
part1_memory_registers.py - Part I: Low-Level Memory Physics, Pointers & Hardware Registers
"""

def get_part1_html():
    return r"""
<!-- PART I COVER -->
<div class="part-page">
    <div class="part-number">Part I</div>
    <div class="part-title">Low-Level Memory Physics, Pointers & Hardware Registers</div>
    <div class="part-desc">
        Before an engineer can architect secure cryptographic hardware or write bare-metal firmware, they must master 
        the exact physical reality of digital memory. This part explores contiguous multi-dimensional layouts, raw pointer arithmetic, 
        hardware register maps (MMIO), the true mechanics of <code>volatile</code>, bitwise manipulation primitives, 
        struct alignment, padding holes, and the strict aliasing rules that govern modern optimizing compilers.
    </div>
    <div class="part-chapters-list">
        <h4>Included Curriculum Chapters & Missions:</h4>
        <ul>
            <li><strong>Chapter 1:</strong> Contiguous Memory Layout, Pointer Arithmetic & Cache Locality (Mission 01)</li>
            <li><strong>Chapter 2:</strong> Dynamic Heap Management & Vector Growth Mechanics (Mission 02)</li>
            <li><strong>Chapter 3:</strong> Memory-Mapped I/O (MMIO), Hardware Registers & the <code>volatile</code> Keyword (Mission 03)</li>
            <li><strong>Chapter 4:</strong> Bit Manipulation, BitFields & Endianness Parsing (Mission 03)</li>
            <li><strong>Chapter 5:</strong> Struct Memory Layout, Natural Alignment, Padding & Type Punning (Mission 03)</li>
        </ul>
    </div>
</div>

<!-- CHAPTER 1 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 1</span> &bull; 
        <span>Topic: Contiguous 2D Memory, Pointer Striding & Microarchitectural Locality</span> &bull; 
        <span>Standard: C++20</span> &bull; 
        <span>Codebase Link: Mission 01 (Matrix Perimeter Scanner)</span>
    </div>

    <h1>Chapter 1: Contiguous Memory Layout, Pointer Arithmetic & Cache Locality</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Contiguous Memory:</strong> A block of physical or virtual address space where sequential elements 
            are located at strictly adjacent byte offsets with zero unallocated gaps.<br>
            <strong>Row-Major Order:</strong> The standard C/C++ multi-dimensional array storage scheme where entire consecutive rows 
            are placed end-to-end in linear memory. Given <code>T array[R][C]</code>, element <code>(r, c)</code> is mapped to flat byte 
            offset <code>(r * C + c) * sizeof(T)</code>.<br>
            <strong>Spatial Locality:</strong> The microarchitectural principle that accessing memory address \(A\) strongly implies 
            that addresses \(A+1, A+2, \dots\) will be accessed in the immediate future.<br>
            <strong>Temporal Locality:</strong> The principle that accessing memory address \(A\) strongly implies that the same address 
            \(A\) will be accessed again shortly.<br>
            <strong>Cache Line:</strong> The minimum unit of data transfer between the CPU cache hierarchy and main memory (SRAM/DRAM). 
            On modern ARM64 (Cortex-A53/A72/Neoverse) and x86_64 cores, a cache line is exactly <strong>64 bytes</strong> (512 bits).<br>
            <strong>Pointer Arithmetic:</strong> Arithmetic performed directly on memory addresses. Adding integer \(n\) to a typed pointer 
            <code>T* p</code> advances the raw memory address by \(n \times \text{sizeof}(T)\) bytes.
        </p>
    </div>

    <h2>The "Why": Microarchitectural Latency and Hardware Physics</h2>
    <p>
        In digital logic, retrieving data from off-chip DRAM requires driving external address pins, charging capacitive bitlines, 
        and waiting for row buffer activation (CAS latency), taking <strong>150 to 300 CPU clock cycles</strong>. In contrast, 
        retrieving data from on-chip Level 1 Data Cache (L1D) takes only <strong>4 clock cycles</strong>.
    </p>

    <div class="callout callout-hw">
        <div class="callout-header">Hardware Reality: Row-Major Traversal vs Column-Major Striding</div>
        <p>
            When a CPU core executes an instruction loading address \(A\), the cache controller fetches the entire 64-byte cache line 
            enclosing \(A\). If you traverse an array in <strong>row-major order</strong>, each 64-byte fetch brings in 16 adjacent 
            <code>int32_t</code> elements, yielding 1 cache miss followed by 15 lightning-fast cache hits (93.75% hit rate). 
            If you mistakenly traverse in <strong>column-major order</strong> across large dimensions, every single access jumps 
            by an entire row stride, causing a compulsory cache miss on <em>every single read</em> and destroying memory throughput.
        </p>
    </div>

    <div class="diagram">
+---------------------------------------------------------------------------------------------------+
| 64-Byte Cache Line Fetched From L2 / DRAM into L1 Data Cache (Contains 16 x int32_t elements)    |
+-------------------+-------------------+-------------------+-------------------+-------------------+
| Index [r][0] (4B) | Index [r][1] (4B) | Index [r][2] (4B) | Index [r][3] (4B) | ... [r][15] (4B)  |
+-------------------+-------------------+-------------------+-------------------+-------------------+
  ^ Read (MISS: 200c) ^ Read (HIT: 4c)    ^ Read (HIT: 4c)    ^ Read (HIT: 4c)    ^ Read (HIT: 4c)
    </div>

    <h2>C++ Implementation: The Perimeter Scanner Pattern</h2>
    <p>
        The following implementation (derived from Mission 01) demonstrates strict bounds checking via <code>static_assert</code>, 
        scope isolation of loop variables, avoidance of integer signedness bugs when computing differences, and cache-conscious 
        iteration around matrix boundaries.
    </p>

    <pre><code><span class="dir">#include</span> <span class="str">&lt;iostream&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;cstddef&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;cstdint&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;cstdlib&gt;</span>

<span class="typ">int</span> <span class="fn">main</span>() {
    <span class="kwd">constexpr</span> std::<span class="typ">size_t</span> rows = <span class="num">6</span>;
    <span class="kwd">constexpr</span> std::<span class="typ">size_t</span> cols = <span class="num">6</span>;

    <span class="com">// Compile-time safety: enforce geometric invariants</span>
    <span class="kwd">static_assert</span>(rows &gt;= <span class="num">2</span> &amp;&amp; cols &gt;= <span class="num">2</span>, <span class="str">"grid needs at least 2 rows and 2 cols"</span>);

    <span class="com">// Contiguous 2D array allocated on stack; rows stored sequentially</span>
    <span class="typ">int32_t</span> terrain[rows][cols]{
        { <span class="num">1</span>,  <span class="num">2</span>,  <span class="num">3</span>,  <span class="num">4</span>,  <span class="num">5</span>,  <span class="num">6</span>},
        { <span class="num">7</span>,  <span class="num">8</span>,  <span class="num">9</span>, <span class="num">10</span>, <span class="num">11</span>, <span class="num">12</span>},
        {<span class="num">13</span>, <span class="num">14</span>, <span class="num">25</span>, <span class="num">16</span>, <span class="num">17</span>, <span class="num">18</span>},
        {<span class="num">19</span>, <span class="num">20</span>, <span class="num">21</span>, <span class="num">22</span>, <span class="num">23</span>, <span class="num">24</span>},
        {<span class="num">25</span>, <span class="num">26</span>, <span class="num">27</span>, <span class="num">28</span>, <span class="num">29</span>, <span class="num">30</span>},
        {<span class="num">31</span>, <span class="num">32</span>, <span class="num">33</span>, <span class="num">34</span>, <span class="num">35</span>, <span class="num">36</span>}
    };

    <span class="typ">int64_t</span> perimeter_sum{<span class="num">0</span>};
    <span class="typ">int64_t</span> max_gap{<span class="num">0</span>};
    <span class="typ">int32_t</span> prev{terrain[<span class="num">1</span>][<span class="num">0</span>]}; <span class="com">// Starting sentinel for continuous loop</span>

    <span class="com">// Lambda visitor isolating calculation; passed by value for fundamentals</span>
    <span class="kwd">auto</span> visit = [&amp;](<span class="typ">int32_t</span> current) {
        perimeter_sum += current;

        <span class="com">// Prevention of arithmetic underflow: cast to int64_t before subtraction</span>
        <span class="kwd">const</span> <span class="typ">int64_t</span> diff{std::<span class="fn">abs</span>(<span class="kwd">static_cast</span>&lt;<span class="typ">int64_t</span>&gt;(current) - prev)};
        <span class="kwd">if</span> (diff &gt; max_gap) {
            max_gap = diff;
        }
        prev = current;
    };

    <span class="com">// 1. Top row (left to right) - Pure contiguous forward striding</span>
    <span class="kwd">for</span> (std::<span class="typ">size_t</span> c = <span class="num">0</span>; c &lt; cols; ++c) { visit(terrain[<span class="num">0</span>][c]); }

    <span class="com">// 2. Right column (top+1 to bottom) - Strided striding across row boundaries</span>
    <span class="kwd">for</span> (std::<span class="typ">size_t</span> r = <span class="num">1</span>; r &lt; rows; ++r) { visit(terrain[r][cols - <span class="num">1</span>]); }

    <span class="com">// 3. Bottom row (right-1 down to 0)</span>
    <span class="kwd">for</span> (std::<span class="typ">size_t</span> c = cols - <span class="num">2</span>; c &lt; cols; --c) { visit(terrain[rows - <span class="num">1</span>][c]); }

    <span class="com">// 4. Left column (bottom-1 up to 1)</span>
    <span class="kwd">for</span> (std::<span class="typ">size_t</span> r = rows - <span class="num">2</span>; r &gt;= <span class="num">1</span>; --r) { visit(terrain[r][<span class="num">0</span>]); }

    <span class="kwd">return</span> <span class="num">0</span>;
}</code></pre>

    <div class="callout callout-sec">
        <div class="callout-header">Security Implication: The Arithmetic Underflow Hazard</div>
        <p>
            Notice line 35: <code>std::abs(static_cast&lt;int64_t&gt;(current) - prev)</code>. In hardware and low-level C++, 
            subtracting two <code>uint32_t</code> values where \(B > A\) results in <strong>unsigned integer underflow</strong> 
            (wrapping around modulo \(2^{32}\) to a gigantic positive number \(\approx 4.29 \times 10^9\)). 
            If such an underflow is used as an array size or cryptographic buffer length check, it creates a fatal 
            remote buffer overflow vulnerability.
        </p>
    </div>
</div>

<!-- CHAPTER 2 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 2</span> &bull; 
        <span>Topic: Dynamic Heap Allocation, Capacity Amortization & Invalidation</span> &bull; 
        <span>Standard: C++20</span> &bull; 
        <span>Codebase Link: Mission 02 (Manual Heap Vector)</span>
    </div>

    <h1>Chapter 2: Dynamic Heap Management & Vector Growth Mechanics</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Heap Memory:</strong> Dynamically allocated memory managed at runtime via operating system system calls 
            (e.g., <code>mmap</code>, <code>brk</code> in POSIX) or bare-metal runtime routines.<br>
            <strong>Allocation Triad:</strong> The three fundamental member variables required to manage any dynamic array:
            (1) a raw pointer to the heap buffer (<code>T* _data</code>), (2) the current count of active elements (<code>size_t _size</code>), 
            and (3) the total allocated capacity (<code>size_t _capacity</code>).<br>
            <strong>Geometric Growth:</strong> Reallocation strategy where capacity grows by a constant multiplication factor 
            (typically \(2\times\) or \(1.5\times\)). This guarantees that inserting \(N\) elements requires only \(O(\log N)\) reallocations, 
            yielding an <strong>amortized \(O(1)\)</strong> insertion time.<br>
            <strong>Pointer & Reference Invalidation:</strong> The phenomenon where references or raw pointers pointing to elements 
            in a dynamic buffer become <strong>dangling pointers</strong> immediately following a reallocation, because the old buffer 
            was freed and elements were migrated to a new memory address.
        </p>
    </div>

    <h2>The "Why": The Peril of Raw Heap in Low-Level Firmware</h2>
    <p>
        In desktop applications, developers take <code>std::vector</code> for granted. However, in safety-critical silicon firmware 
        and hardware security modules (HSMs), dynamic heap allocation is either strictly restricted or completely banned. Why?
    </p>
    <ul>
        <li><strong>Heap Fragmentation:</strong> Repeated allocations and frees of varying sizes fragment SRAM, eventually causing allocation failures even when total free memory is sufficient.</li>
        <li><strong>Non-Deterministic Latency:</strong> When a vector triggers a reallocation, it must pause execution, request memory, and copy all existing elements. A time-critical interrupt handler that triggers a vector reallocation will violate real-time deadlines.</li>
        <li><strong>Dangling Pointer Exploits:</strong> If code holds a reference to an element inside a vector and another thread or function pushes data causing capacity expansion, that reference points to deallocated memory—an immediate <em>Use-After-Free (UAF)</em> vulnerability.</li>
    </ul>

    <h2>C++ Implementation: The Manual Heap Vector</h2>
    <p>
        Below is the implementation of <code>IntVector</code> from Mission 02, illustrating raw heap allocation, geometric doubling, 
        and defensive nullification on release:
    </p>

    <pre><code><span class="dir">#pragma once</span>

<span class="dir">#include</span> <span class="str">&lt;cstddef&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;cstdint&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;stdexcept&gt;</span>

<span class="com">// Manages dynamic heap storage. Demonstrates raw heap invariants.</span>
<span class="kwd">struct</span> <span class="typ">IntVector</span> {
<span class="kwd">public</span>:
    <span class="fn">IntVector</span>() : _data(<span class="kwd">nullptr</span>), _size(<span class="num">0</span>), _capacity(<span class="num">0</span>) {}

    <span class="com">// Clean up allocated memory upon destruction</span>
    ~<span class="fn">IntVector</span>() { <span class="fn">release</span>(); }

    std::<span class="typ">size_t</span> <span class="fn">get_size</span>() <span class="kwd">const</span> { <span class="kwd">return</span> _size; }
    std::<span class="typ">size_t</span> <span class="fn">get_capacity</span>() <span class="kwd">const</span> { <span class="kwd">return</span> _capacity; }

    <span class="com">// Returns reference: allows both reading and writing (lvalue semantics)</span>
    <span class="com">// DANGEROUS: Returned reference dangles after any subsequent push() that triggers grow()</span>
    <span class="typ">int32_t</span>&amp; <span class="fn">at</span>(std::<span class="typ">size_t</span> index) {
        <span class="kwd">if</span> (index &gt;= _size) {
            <span class="kwd">throw</span> std::<span class="typ">out_of_range</span>(<span class="str">"IntVector::at: index out of bounds"</span>);
        }
        <span class="kwd">return</span> _data[index];
    }

    <span class="kwd">const</span> <span class="typ">int32_t</span>&amp; <span class="fn">at</span>(std::<span class="typ">size_t</span> index) <span class="kwd">const</span> {
        <span class="kwd">if</span> (index &gt;= _size) {
            <span class="kwd">throw</span> std::<span class="typ">out_of_range</span>(<span class="str">"IntVector::at: index out of bounds"</span>);
        }
        <span class="kwd">return</span> _data[index];
    }

    <span class="typ">void</span> <span class="fn">push</span>(<span class="typ">int32_t</span> value) {
        <span class="kwd">if</span> (_size == _capacity) {
            <span class="fn">grow</span>();
        }
        _data[_size] = value;
        ++_size;
    }

    <span class="com">// Explicit release; resetting pointer prevents double-free vulnerabilities</span>
    <span class="typ">void</span> <span class="fn">release</span>() {
        <span class="kwd">delete</span>[] _data;
        _data = <span class="kwd">nullptr</span>;
        _size = <span class="num">0</span>;
        _capacity = <span class="num">0</span>;
    }

<span class="kwd">private</span>:
    <span class="typ">void</span> <span class="fn">grow</span>() {
        <span class="com">// Geometric expansion: double capacity (initialise to 2 if empty)</span>
        <span class="kwd">const</span> std::<span class="typ">size_t</span> new_capacity = (_capacity == <span class="num">0</span>) ? <span class="num">2</span> : _capacity * <span class="num">2</span>;
        <span class="typ">int32_t</span>* new_data = <span class="kwd">new</span> <span class="typ">int32_t</span>[new_capacity];

        <span class="com">// Copy elements across manually</span>
        <span class="kwd">for</span> (std::<span class="typ">size_t</span> i = <span class="num">0</span>; i &lt; _size; ++i) {
            new_data[i] = _data[i];
        }

        <span class="com">// Deallocate old memory and swap pointer</span>
        <span class="kwd">delete</span>[] _data;
        _data = new_data;
        _capacity = new_capacity;
    }

    <span class="typ">int32_t</span>* _data;
    std::<span class="typ">size_t</span> _size;
    std::<span class="typ">size_t</span> _capacity;
};</code></pre>

    <div class="callout callout-hw">
        <div class="callout-header">Hardware Reality: What Happens Under the Hood During new[]</div>
        <p>
            When <code>new int32_t[new_capacity]</code> executes in user space, the C++ runtime's memory allocator 
            (e.g., <code>ptmalloc</code> in glibc) searches its thread-local cache (tcache) or bins. If no suitable free chunk exists, 
            it issues an operating system kernel transition via the <code>brk</code> or <code>mmap</code> system call. 
            The OS kernel updates page table entries, incurring translation lookaside buffer (TLB) shootdowns and page faults. 
            This single line of code can trigger thousands of CPU cycles of kernel execution!
        </p>
    </div>
</div>

<!-- CHAPTER 3 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 3</span> &bull; 
        <span>Topic: MMIO, Hardware Registers, volatile & Read-Modify-Write Hazards</span> &bull; 
        <span>Standard: C++20</span> &bull; 
        <span>Codebase Link: Mission 03 (Register Map Autopsy)</span>
    </div>

    <h1>Chapter 3: Memory-Mapped I/O (MMIO), Hardware Registers & `volatile`</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Memory-Mapped I/O (MMIO):</strong> A computer architecture technique where physical peripheral registers 
            (timers, UARTs, cryptographic accelerators) are assigned addresses within the CPU's physical memory address space. 
            The CPU accesses hardware registers using standard load and store assembly instructions (<code>LDR</code>/<code>STR</code> in ARM, 
            <code>lw</code>/<code>sw</code> in RISC-V).<br>
            <strong>The <code>volatile</code> Keyword:</strong> A C/C++ type qualifier indicating that the value of an object may change 
            due to factors outside the compiler's knowledge (such as hardware logic or asynchronous interrupts). 
            <strong>Strict Semantics:</strong> The compiler is forbidden from optimizing away (eliding), caching in registers, 
            or reordering accesses to <code>volatile</code> memory locations.<br>
            <strong>Read-Modify-Write (RMW):</strong> The sequence of reading a register, masking/updating specific bitfields in a CPU general register, 
            and writing the updated word back to physical hardware.<br>
            <strong>Write-1-to-Clear (W1C):</strong> A hardware register convention where writing a binary '1' to a bit position 
            resets that hardware latch to '0' (used extensively for interrupt acknowledgment), while writing a '0' leaves the bit unaffected.<br>
            <strong>Reserved Bits:</strong> Bit positions inside a hardware register marked as reserved by silicon architects. 
            Firmware must preserve their existing values during RMW cycles to prevent undefined behavior in future silicon revisions.
        </p>
    </div>

    <h2>The "Why": The Fatal Myth of `volatile`</h2>
    <p>
        One of the most catastrophic, widespread mistakes in low-level systems engineering is confusing <code>volatile</code> with multithreading synchronization.
    </p>

    <table>
        <thead>
            <tr>
                <th style="width: 25%;">Property</th>
                <th style="width: 35%;">The `volatile` Keyword</th>
                <th style="width: 40%;">Hardware Reality & Requirements</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Compiler Elision</strong></td>
                <td>Guarantees every read/write produces an assembly instruction.</td>
                <td><strong>Sufficient for MMIO:</strong> Prevents compiler from discarding writes to hardware FIFOs.</td>
            </tr>
            <tr>
                <td><strong>Instruction Reordering</strong></td>
                <td>Prevents compiler from reordering two <code>volatile</code> accesses relative to each other.</td>
                <td><strong>Insufficient for CPU pipelines:</strong> The out-of-order CPU hardware itself can reorder memory transactions! Requires hardware memory barriers.</td>
            </tr>
            <tr>
                <td><strong>Atomicity</strong></td>
                <td><strong>NONE.</strong> A 64-bit access on a 32-bit bus splits into two 32-bit instructions.</td>
                <td>Requires atomic bus transactions or lock-free instructions (<code>LDREX/STREX</code>, <code>LR/SC</code>).</td>
            </tr>
            <tr>
                <td><strong>Cache Coherency</strong></td>
                <td><strong>NONE.</strong> Does not flush, invalidate, or bypass CPU caches.</td>
                <td>Requires memory to be mapped as <strong>Device Memory</strong> in the CPU MMU page tables.</td>
            </tr>
        </tbody>
    </table>

    <div class="callout callout-sec">
        <div class="callout-header">The RMW Race Hazard on W1C Registers</div>
        <p>
            Consider a status register containing two interrupt flags: <code>bit 0 = RX_READY</code>, <code>bit 1 = TX_DONE</code>, 
            both defined as <strong>Write-1-to-Clear (W1C)</strong>.
            Suppose you want to acknowledge <code>RX_READY</code>. If you perform a naive Read-Modify-Write cycle:
            <ol>
                <li>Read status register: CPU receives <code>0b00000011</code> (both RX_READY and TX_DONE are currently active).</li>
                <li>Mask bit 0: CPU register contains <code>0b00000001</code>.</li>
                <li>Write back to status register: You write <code>0b00000001</code>. <em>This clears RX_READY correctly.</em></li>
            </ol>
            <strong>The Catastrophe:</strong> What if step 1 read <code>0b00000011</code>, and you wrote back the entire word? 
            Writing a '1' to bit 1 clears <code>TX_DONE</code> before your driver ever handled the transmission! 
            <strong>Rule:</strong> Never use Read-Modify-Write on W1C registers! Write <em>only</em> the specific bit you intend to clear.
        </p>
    </div>

    <h2>C++ Implementation: Physical Register Block Model</h2>
    <p>
        The following implementation from Mission 03 provides an aligned, bounds-checked physical register block standing in for 
        physical MMIO address space:
    </p>

    <pre><code><span class="dir">#pragma once</span>

<span class="dir">#include</span> <span class="str">&lt;cstddef&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;cstdint&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;stdexcept&gt;</span>

<span class="com">// Models physical hardware MMIO memory. Enforces 32-bit alignment and volatile semantics.</span>
<span class="kwd">struct</span> <span class="typ">RegisterBlock</span> {
    <span class="kwd">static</span> <span class="kwd">constexpr</span> std::<span class="typ">size_t</span> register_count = <span class="num">64</span>;
    <span class="kwd">static</span> <span class="kwd">constexpr</span> std::<span class="typ">size_t</span> size_bytes = register_count * <span class="kwd">sizeof</span>(<span class="typ">uint32_t</span>);

    <span class="typ">uint32_t</span> <span class="fn">read32</span>(std::<span class="typ">size_t</span> offset) <span class="kwd">const</span> {
        <span class="fn">validate_bounds</span>(offset, <span class="kwd">sizeof</span>(<span class="typ">uint32_t</span>));
        <span class="fn">validate_alignment</span>(offset, <span class="kwd">sizeof</span>(<span class="typ">uint32_t</span>));

        <span class="com">// volatile pointer: guarantees compiler will not elide read or cache in register</span>
        <span class="kwd">const</span> <span class="kwd">volatile</span> <span class="typ">uint32_t</span>* ptr = <span class="kwd">reinterpret_cast</span>&lt;<span class="kwd">const</span> <span class="kwd">volatile</span> <span class="typ">uint32_t</span>*&gt;(_memory + offset);
        <span class="kwd">return</span> *ptr;
    }

    <span class="typ">void</span> <span class="fn">write32</span>(std::<span class="typ">size_t</span> offset, <span class="typ">uint32_t</span> val) {
        <span class="fn">validate_bounds</span>(offset, <span class="kwd">sizeof</span>(<span class="typ">uint32_t</span>));
        <span class="fn">validate_alignment</span>(offset, <span class="kwd">sizeof</span>(<span class="typ">uint32_t</span>));

        <span class="com">// volatile store: compiler MUST emit physical store instruction</span>
        <span class="kwd">volatile</span> <span class="typ">uint32_t</span>* ptr = <span class="kwd">reinterpret_cast</span>&lt;<span class="kwd">volatile</span> <span class="typ">uint32_t</span>*&gt;(_memory + offset);
        *ptr = val;
    }

<span class="kwd">private</span>:
    <span class="typ">void</span> <span class="fn">validate_bounds</span>(std::<span class="typ">size_t</span> offset, std::<span class="typ">size_t</span> access_size) <span class="kwd">const</span> {
        <span class="kwd">if</span> (access_size &gt; size_bytes || offset &gt; size_bytes - access_size) {
            <span class="kwd">throw</span> std::<span class="typ">out_of_range</span>(<span class="str">"MMIO offset out of physical bounds"</span>);
        }
    }

    <span class="typ">void</span> <span class="fn">validate_alignment</span>(std::<span class="typ">size_t</span> offset, std::<span class="typ">size_t</span> alignment) <span class="kwd">const</span> {
        <span class="kwd">if</span> (offset % alignment != <span class="num">0</span>) {
            <span class="kwd">throw</span> std::<span class="typ">invalid_argument</span>(<span class="str">"Unaligned MMIO register access attempt"</span>);
        }
    }

    <span class="com">// Hardware alignment requirement: 32-bit registers must sit on 4-byte boundaries</span>
    <span class="kwd">alignas</span>(<span class="typ">uint32_t</span>) <span class="typ">uint8_t</span> _memory[size_bytes]{};
};</code></pre>
</div>

<!-- CHAPTER 4 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 4</span> &bull; 
        <span>Topic: Bit Manipulation, BitField Abstractions & Compile-Time Endianness</span> &bull; 
        <span>Standard: C++20</span> &bull; 
        <span>Codebase Link: Mission 03 (BitField & ByteOrder)</span>
    </div>

    <h1>Chapter 4: Bit Manipulation, BitFields & Endianness Parsing</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Bitmask:</strong> A binary pattern used in bitwise operations (AND, OR, XOR) to isolate, set, or clear specific bit fields.<br>
            <strong>Bit Extraction:</strong> Isolating a contiguous sub-range of bits from an integer word and right-shifting them to index 0: 
            <code>(word &amp; mask) &gt;&gt; shift</code>.<br>
            <strong>Bit Insertion:</strong> Clearing an existing sub-range of bits in a destination word and inserting a new value aligned to that range: 
            <code>(word &amp; ~mask) | ((val &lt;&lt; shift) &amp; mask)</code>.<br>
            <strong>Endianness:</strong> The ordering of individual bytes representing a multi-byte scalar within computer memory.
            <ul>
                <li><strong>Little-Endian (LE):</strong> Least Significant Byte (LSB) stored at the lowest memory address (Standard on x86, ARM64, RISC-V).</li>
                <li><strong>Big-Endian (BE):</strong> Most Significant Byte (MSB) stored at the lowest memory address (Standard in Network Protocols, IBM Power, SPARC).</li>
            </ul>
            <strong>Compile-Time Endian Detection:</strong> Querying the hardware CPU byte order at build time using C++20's <code>std::endian::native</code>.
        </p>
    </div>

    <h2>The "Why": Why C-Style Bitfields Are Banned in Silicon Engineering</h2>
    <p>
        Novice embedded engineers often attempt to declare hardware registers using C-style bitfields:
    </p>
    <pre><code><span class="com">// NEVER DO THIS IN HARDWARE DRIVERS</span>
<span class="kwd">struct</span> <span class="typ">BadControlRegister</span> {
    <span class="typ">uint32_t</span> enable : <span class="num">1</span>;
    <span class="typ">uint32_t</span> start  : <span class="num">1</span>;
    <span class="typ">uint32_t</span> mode   : <span class="num">3</span>;
};</code></pre>
    <div class="callout callout-sec">
        <div class="callout-header">The ISO C/C++ Standard Traps on Bitfields</div>
        <p>
            According to the ISO C and C++ standards, the packing order of bitfield members inside storage units is 
            <strong>strictly implementation-defined</strong>. 
            On GCC for ARM, <code>enable</code> might be placed at bit 0; on a different compiler or architecture, it may be placed 
            at bit 31. Furthermore, compilers are permitted to emit unaligned byte-level accesses to bitfields, triggering hardware bus faults 
            on peripheral registers. 
            <strong>Mandatory Rule:</strong> In hardware engineering, register layouts must be defined strictly using integer masks and shifts.
        </p>
    </div>

    <h2>C++ Implementation: The BitField Abstraction</h2>
    <p>
        The following <code>BitField</code> class provides zero-cost, compile-time verified bitfield manipulations:
    </p>

    <pre><code><span class="dir">#pragma once</span>

<span class="dir">#include</span> <span class="str">&lt;cstdint&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;stdexcept&gt;</span>

<span class="com">// Robust, zero-overhead bit manipulation primitive</span>
<span class="kwd">struct</span> <span class="typ">BitField</span> {
<span class="kwd">public</span>:
    <span class="kwd">constexpr</span> <span class="fn">BitField</span>(<span class="typ">uint32_t</span> shift, <span class="typ">uint32_t</span> width) : _shift(shift), _width(width) {
        <span class="kwd">if</span> (width == <span class="num">0</span> || width &gt; <span class="num">32</span>) {
            <span class="kwd">throw</span> std::<span class="typ">invalid_argument</span>(<span class="str">"BitField: width must be 1..32"</span>);
        }
        <span class="kwd">if</span> (shift &gt; <span class="num">32</span> - width) {
            <span class="kwd">throw</span> std::<span class="typ">invalid_argument</span>(<span class="str">"BitField: field exceeds 32 bits"</span>);
        }
    }

    <span class="com">// Generate bitmask without shift-by-32 Undefined Behavior</span>
    <span class="kwd">constexpr</span> <span class="typ">uint32_t</span> <span class="fn">mask</span>() <span class="kwd">const</span> {
        <span class="kwd">const</span> <span class="typ">uint32_t</span> base = (_width == <span class="num">32</span>) ? <span class="num">0xFFFFFFFFu</span> : ((<span class="num">1u</span> &lt;&lt; _width) - <span class="num">1u</span>);
        <span class="kwd">return</span> base &lt;&lt; _shift;
    }

    <span class="com">// Extract field from raw register word</span>
    <span class="kwd">constexpr</span> <span class="typ">uint32_t</span> <span class="fn">extract</span>(<span class="typ">uint32_t</span> word) <span class="kwd">const</span> {
        <span class="kwd">return</span> (word &amp; <span class="fn">mask</span>()) &gt;&gt; _shift;
    }

    <span class="com">// Insert value into register word preserving neighboring bits</span>
    <span class="kwd">constexpr</span> <span class="typ">uint32_t</span> <span class="fn">insert</span>(<span class="typ">uint32_t</span> word, <span class="typ">uint32_t</span> value) <span class="kwd">const</span> {
        <span class="kwd">const</span> <span class="typ">uint32_t</span> cleared = word &amp; ~<span class="fn">mask</span>();
        <span class="kwd">const</span> <span class="typ">uint32_t</span> placed  = (value &lt;&lt; _shift) &amp; <span class="fn">mask</span>();
        <span class="kwd">return</span> cleared | placed;
    }

    <span class="kwd">constexpr</span> <span class="typ">bool</span> <span class="fn">test</span>(<span class="typ">uint32_t</span> word) <span class="kwd">const</span> { <span class="kwd">return</span> (word &amp; <span class="fn">mask</span>()) != <span class="num">0</span>; }
    <span class="kwd">constexpr</span> <span class="typ">uint32_t</span> <span class="fn">set</span>(<span class="typ">uint32_t</span> word) <span class="kwd">const</span> { <span class="kwd">return</span> word | <span class="fn">mask</span>(); }
    <span class="kwd">constexpr</span> <span class="typ">uint32_t</span> <span class="fn">clear</span>(<span class="typ">uint32_t</span> word) <span class="kwd">const</span> { <span class="kwd">return</span> word &amp; ~<span class="fn">mask</span>(); }
    <span class="kwd">constexpr</span> <span class="typ">uint32_t</span> <span class="fn">toggle</span>(<span class="typ">uint32_t</span> word) <span class="kwd">const</span> { <span class="kwd">return</span> word ^ <span class="fn">mask</span>(); }

<span class="kwd">private</span>:
    <span class="typ">uint32_t</span> _shift;
    <span class="typ">uint32_t</span> _width;
};</code></pre>

    <h2>Compile-Time Endianness & Wire Parsing</h2>
    <p>
        Silicon systems frequently receive Big-Endian wire packets over AXI/PCIe/Ethernet while executing on Little-Endian ARM64 cores. 
        The byte order parsing must be explicit and verified at compile time:
    </p>

    <pre><code><span class="dir">#include</span> <span class="str">&lt;bit&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;cstdint&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;span&gt;</span>

<span class="com">// Compile-time verification of host architecture</span>
<span class="kwd">constexpr</span> <span class="typ">bool</span> host_is_little_endian = (std::<span class="typ">endian</span>::native == std::<span class="typ">endian</span>::little);
<span class="kwd">static_assert</span>(host_is_little_endian || std::<span class="typ">endian</span>::native == std::<span class="typ">endian</span>::big, 
              <span class="str">"PDP-endian / mixed-endian systems are not supported"</span>);

<span class="com">// Parse Big-Endian integer from wire buffer regardless of CPU host endianness</span>
<span class="kwd">template</span> &lt;<span class="kwd">typename</span> <span class="typ">T</span>&gt;
<span class="kwd">constexpr</span> <span class="typ">T</span> <span class="fn">read_be</span>(std::<span class="typ">span</span>&lt;<span class="kwd">const</span> <span class="typ">uint8_t</span>&gt; bytes, std::<span class="typ">size_t</span> offset) {
    <span class="typ">T</span> value = <span class="num">0</span>;
    <span class="kwd">for</span> (std::<span class="typ">size_t</span> i = <span class="num">0</span>; i &lt; <span class="kwd">sizeof</span>(<span class="typ">T</span>); ++i) {
        <span class="kwd">const</span> <span class="typ">T</span> byte = <span class="kwd">static_cast</span>&lt;<span class="typ">T</span>&gt;(bytes[offset + i]);
        <span class="kwd">const</span> std::<span class="typ">size_t</span> shift = (<span class="kwd">sizeof</span>(<span class="typ">T</span>) - <span class="num">1</span> - i) * <span class="num">8</span>;
        value = <span class="kwd">static_cast</span>&lt;<span class="typ">T</span>&gt;(value | (<span class="kwd">static_cast</span>&lt;<span class="typ">T</span>&gt;(byte &lt;&lt; shift)));
    }
    <span class="kwd">return</span> value;
}</code></pre>
</div>

<!-- CHAPTER 5 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 5</span> &bull; 
        <span>Topic: Struct Layout, Padding, Natural Alignment & Type Punning Rules</span> &bull; 
        <span>Standard: C++20</span> &bull; 
        <span>Codebase Link: Mission 03 (Packet & Punning)</span>
    </div>

    <h1>Chapter 5: Struct Memory Layout, Alignment & Type Punning</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Alignment Requirement:</strong> The integer multiple of bytes to which an object's memory address must conform when allocated. 
            On 64-bit systems, a 32-bit integer (<code>uint32_t</code>) requires 4-byte alignment (address modulo 4 == 0); 
            a 64-bit pointer requires 8-byte alignment.<br>
            <strong>Natural Alignment:</strong> Placing an \(N\)-byte scalar at an address evenly divisible by \(N\).<br>
            <strong>Struct Padding Holes:</strong> Unused padding bytes inserted automatically by the compiler between struct members 
            or at the end of the struct to ensure every member satisfies its alignment requirement.<br>
            <strong>Strict Aliasing Rule:</strong> C++ standard rule stating that two pointers of different types cannot point to the same 
            memory location, with very narrow exceptions (e.g., <code>char*</code>, <code>std::byte*</code>). Violating this allows 
            the compiler's optimizer to reorder reads and writes, generating catastrophic silent bugs.<br>
            <strong>Type Punning:</strong> Reading the underlying binary representation of one data type as another data type.
        </p>
    </div>

    <h2>The "Why": Memory Waste and Hardware Alignment Traps</h2>
    <p>
        CPUs access memory through bus transactions sized to word widths (32 or 64 bits). 
        When software requests a 32-bit integer from an unaligned address (e.g. <code>0x1001</code>), one of two things happens:
    </p>
    <ul>
        <li><strong>Hardware Bus Fault:</strong> Strict architectures (many ARM Cortex-M and RISC-V cores) immediately trigger a hardware trap (UsageFault / Alignment Trap), halting the processor.</li>
        <li><strong>Severe Performance Penalty:</strong> Tolerant architectures (x86_64, modern ARM64) split the request into two separate bus transactions, merge the bytes in CPU registers, and incur an 8x latency penalty.</li>
    </ul>

    <div class="diagram">
UNOPTIMIZED STRUCT (PacketSparse: 16 Bytes total, 4 Bytes wasted padding)
+-----------+-------------------------+-----------+-----------+-------------------------+
| Type (1B) | PADDING HOLE (3 Bytes)  | Addr (4B) | Flag (1B) | PAD(1B) | Length (2B)   | Checksum (4B)
+-----------+-------------------------+-----------+-----------+---------+---------------+-----------+
Offset: 0   1                         4           8           9         10              12         16

OPTIMIZED REORDERED STRUCT (PacketCompact: 12 Bytes total, ZERO padding)
+-------------------------+-------------------------+---------------+-----------+-----------+
| Address (4 Bytes)       | Checksum (4 Bytes)      | Length (2B)   | Type (1B) | Flag (1B) |
+-------------------------+-------------------------+---------------+-----------+-----------+
Offset: 0                 4                         8               10          11         12
    </div>

    <h2>Type Punning: The Defined vs Undefined Spectrum</h2>
    <p>
        In low-level security code, you frequently convert 4 raw incoming bytes into a <code>uint32_t</code> word. 
        How you do this determines whether your code is standard-compliant or contains critical undefined behavior.
    </p>

    <pre><code><span class="dir">#include</span> <span class="str">&lt;array&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;bit&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;cstdint&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;cstring&gt;</span>

<span class="kwd">using</span> <span class="typ">FourBytes</span> = std::<span class="typ">array</span>&lt;<span class="typ">uint8_t</span>, <span class="num">4</span>&gt;;

<span class="com">// METHOD 1: DEFINED (The classic standard-compliant method)</span>
<span class="com">// Modern compilers (GCC/Clang) recognize this pattern and optimize it directly into a single LDR instruction!</span>
<span class="kwd">inline</span> <span class="typ">uint32_t</span> <span class="fn">pun_memcpy</span>(<span class="kwd">const</span> <span class="typ">FourBytes</span>&amp; bytes) {
    <span class="typ">uint32_t</span> value = <span class="num">0</span>;
    std::<span class="fn">memcpy</span>(&amp;value, bytes.<span class="fn">data</span>(), <span class="kwd">sizeof</span>(value));
    <span class="kwd">return</span> value;
}

<span class="com">// METHOD 2: DEFINED &amp; CONSTEXPR (Modern C++20 Best Practice)</span>
<span class="com">// Fast, type-safe, evaluated at compile time if inputs are known</span>
<span class="kwd">constexpr</span> <span class="typ">uint32_t</span> <span class="fn">pun_bit_cast</span>(<span class="kwd">const</span> <span class="typ">FourBytes</span>&amp; bytes) {
    <span class="kwd">return</span> std::<span class="fn">bit_cast</span>&lt;<span class="typ">uint32_t</span>&gt;(bytes);
}

<span class="com">// METHOD 3: STRICT UNDEFINED BEHAVIOR (BANNED!)</span>
<span class="com">// Violates the strict aliasing rule, and 'bytes' may be misaligned (causing hardware bus faults).</span>
<span class="kwd">inline</span> <span class="typ">uint32_t</span> <span class="fn">pun_pointer_cast</span>(<span class="kwd">const</span> <span class="typ">uint8_t</span>* bytes) {
    <span class="kwd">return</span> *<span class="kwd">reinterpret_cast</span>&lt;<span class="kwd">const</span> <span class="typ">uint32_t</span>*&gt;(bytes); <span class="com">// UB!</span>
}</code></pre>

    <div class="callout callout-sec">
        <div class="callout-header">The Compiler Optimization Trap of Method 3</div>
        <p>
            When you compile <code>pun_pointer_cast</code> with <code>-O2</code> optimization, the compiler assumes 
            pointers of type <code>uint32_t*</code> and <code>uint8_t*</code> never alias the same memory. 
            Consequently, if you store through an integer pointer and read through a float pointer (as demonstrated in 
            Mission 03's <code>aliasing_demo.cpp</code>), the compiler may hoist the read <em>before</em> the write, 
            returning stale or garbage data. In security modules, this causes subtle authentication bypasses.
        </p>
    </div>
</div>
"""
