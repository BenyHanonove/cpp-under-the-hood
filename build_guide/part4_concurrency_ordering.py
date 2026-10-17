"""
part4_concurrency_ordering.py - Part IV: Concurrency, Memory Ordering & Low-Latency Systems
"""

def get_part4_html():
    return r"""
<!-- PART IV COVER -->
<div class="part-page">
    <div class="part-number">Part IV</div>
    <div class="part-title">Concurrency, Memory Ordering & Low-Latency Systems</div>
    <div class="part-desc">
        Modern SoCs feature multiple processor cores, autonomous DMA engines, and hardware accelerators concurrently accessing 
        shared memory fabrics. Writing correct low-level software in such environments requires mastering the C++ Memory Model, 
        instruction-level memory orderings (relaxed, acquire, release, sequential consistency), CPU cache coherence protocols (MESI), 
        and false-sharing mitigation. This part dissects concurrent pipelines with <code>std::jthread</code>, lock-free SPSC circular buffers, 
        C++20 stackless coroutines, and zero-allocation range views.
    </div>
    <div class="part-chapters-list">
        <h4>Included Curriculum Chapters & Missions:</h4>
        <ul>
            <li><strong>Chapter 15:</strong> Multithreaded Pipelines, Worker Pools & Cooperative Cancellation (Mission 11)</li>
            <li><strong>Chapter 16:</strong> The C++ Memory Model, Atomics & Memory Ordering (Mission 12)</li>
            <li><strong>Chapter 17:</strong> The Lock-Free Single-Producer Single-Consumer (SPSC) Ring Buffer (Mission 12)</li>
            <li><strong>Chapter 18:</strong> C++20 Coroutines & Stackless Task Dispatchers (Mission 15)</li>
            <li><strong>Chapter 19:</strong> Zero-Allocation Log Streaming with C++20 Ranges & Views (Mission 14)</li>
        </ul>
    </div>
</div>

<!-- CHAPTER 15 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 15</span> &bull; 
        <span>Topic: Multithreaded Pipelines, std::jthread & Cooperative Cancellation</span> &bull; 
        <span>Standard: C++20</span> &bull; 
        <span>Codebase Link: Mission 11 (Concurrent Thread Pipeline)</span>
    </div>

    <h1>Chapter 15: Concurrent Pipelines & Cooperative Cancellation</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong><code>std::jthread</code>:</strong> C++20 auto-joining thread wrapper. Upon destruction, 
            it automatically issues a cooperative cancellation request (via <code>request_stop()</code>) and calls <code>join()</code>, 
            preventing <code>std::terminate()</code> crashes caused by dangling joinable threads.<br>
            <strong>Cooperative Cancellation:</strong> A thread-safe shutdown pattern where a worker thread periodically queries 
            an atomic token (<code>std::stop_token</code>) to gracefully exit its work loop, rather than being violently terminated 
            by the operating system.<br>
            <strong>Thread-Safe Bounded Queue:</strong> A fixed-capacity FIFO queue synchronized via a mutex and two condition variables 
            (<code>not_full</code>, <code>not_empty</code>) to regulate producer and consumer rates.<br>
            <strong>Deadlock (Coffman Conditions):</strong> A state where execution permanently freezes because two or more threads 
            are each waiting for a mutex held by the other.<br>
            <strong>Priority Inversion:</strong> A real-time systems hazard where a low-priority thread holds a mutex needed by a 
            high-priority thread, and a medium-priority thread preempts the low-priority thread, effectively stalling the high-priority task.
        </p>
    </div>

    <h2>The "Why": The Hard Part Is Stopping</h2>
    <p>
        Starting threads is trivial; shutting down multi-stage concurrent pipelines without deadlocks or buffer truncation is difficult. 
        If worker threads are blocked inside <code>condition_variable::wait()</code> waiting for an empty queue, issuing a stop request 
        is useless unless the condition variable is explicitly notified to wake up the blocked workers.
    </p>

    <h2>C++ Implementation: The Thread-Safe Bounded Queue</h2>
    <p>
        The core building block of the multi-stage pipeline from Mission 11:
    </p>

    <pre><code><span class="dir">#pragma once</span>

<span class="dir">#include</span> <span class="str">&lt;condition_variable&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;mutex&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;optional&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;queue&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;stop_token&gt;</span>

<span class="kwd">template</span> &lt;<span class="kwd">typename</span> <span class="typ">T</span>&gt;
<span class="kwd">class</span> <span class="typ">BoundedQueue</span> {
<span class="kwd">public</span>:
    <span class="kwd">explicit</span> <span class="fn">BoundedQueue</span>(std::<span class="typ">size_t</span> max_capacity) : _max_capacity(max_capacity), _stopped(<span class="kwd">false</span>) {}

    <span class="com">// Push item onto queue; blocks if queue is full</span>
    <span class="typ">bool</span> <span class="fn">push</span>(<span class="typ">T</span> item) {
        std::<span class="typ">unique_lock</span>&lt;std::<span class="typ">mutex</span>&gt; lock(_mtx);
        _cv_not_full.<span class="fn">wait</span>(lock, [<span class="kwd">this</span>]() { <span class="kwd">return</span> _queue.size() &lt; _max_capacity || _stopped; });

        <span class="kwd">if</span> (_stopped) { <span class="kwd">return</span> <span class="kwd">false</span>; }

        _queue.push(std::<span class="fn">move</span>(item));
        _cv_not_empty.<span class="fn">notify_one</span>();
        <span class="kwd">return</span> <span class="kwd">true</span>;
    }

    <span class="com">// Pop item from queue; blocks if queue is empty; supports stop_token</span>
    std::<span class="typ">optional</span>&lt;<span class="typ">T</span>&gt; <span class="fn">pop</span>(std::<span class="typ">stop_token</span> stop_tok) {
        std::<span class="typ">unique_lock</span>&lt;std::<span class="typ">mutex</span>&gt; lock(_mtx);

        <span class="com">// Wait until item available or stop requested</span>
        _cv_not_empty.<span class="fn">wait</span>(lock, [<span class="kwd">this</span>, &amp;stop_tok]() {
            <span class="kwd">return</span> !_queue.empty() || _stopped || stop_tok.<span class="fn">stop_requested</span>();
        });

        <span class="kwd">if</span> (_queue.empty()) {
            <span class="kwd">return</span> std::<span class="typ">nullopt</span>; <span class="com">// Drained and shutting down</span>
        }

        <span class="typ">T</span> val = std::<span class="fn">move</span>(_queue.front());
        _queue.pop();
        _cv_not_full.<span class="fn">notify_one</span>();
        <span class="kwd">return</span> val;
    }

    <span class="com">// Wake up all blocked threads and prevent further pushes</span>
    <span class="typ">void</span> <span class="fn">stop</span>() {
        {
            std::<span class="typ">lock_guard</span>&lt;std::<span class="typ">mutex</span>&gt; lock(_mtx);
            _stopped = <span class="kwd">true</span>;
        }
        _cv_not_empty.<span class="fn">notify_all</span>();
        _cv_not_full.<span class="fn">notify_all</span>();
    }

<span class="kwd">private</span>:
    <span class="kwd">mutable</span> std::<span class="typ">mutex</span> _mtx;
    std::<span class="typ">condition_variable</span> _cv_not_empty;
    std::<span class="typ">condition_variable</span> _cv_not_full;
    std::<span class="typ">queue</span>&lt;<span class="typ">T</span>&gt; _queue;
    std::<span class="typ">size_t</span> _max_capacity;
    <span class="typ">bool</span> _stopped;
};</code></pre>
</div>

<!-- CHAPTER 16 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 16</span> &bull; 
        <span>Topic: The C++ Memory Model, Atomics & Hardware Memory Ordering</span> &bull; 
        <span>Standard: C++20</span> &bull; 
        <span>Codebase Link: Mission 12 (Lock-Free Ring Buffer)</span>
    </div>

    <h1>Chapter 16: The C++ Memory Model & Hardware Ordering</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Data Race:</strong> Two concurrent threads accessing the same physical memory location simultaneously, 
            where at least one access is a write, and neither access is an atomic operation. Under the C++ standard, 
            a data race is <strong>instantaneous Undefined Behavior</strong>.<br>
            <strong><code>std::atomic&lt;T&gt;</code>:</strong> A template ensuring that all reads, writes, and read-modify-write 
            operations on an object are indivisible (atomic) at the machine level.<br>
            <strong>Happens-Before Relationship:</strong> A formal ordering guarantee established by the C++ memory model. 
            If operation \(A\) happens-before operation \(B\), the memory modifications made by \(A\) are guaranteed to be visible to \(B\).<br>
            <strong>Synchronizes-With:</strong> The relationship formed when an atomic store with <code>release</code> ordering 
            is paired with an atomic load of that same atomic variable with <code>acquire</code> ordering in a different thread.
        </p>
    </div>

    <h2>The Six Memory Orderings Explained</h2>
    <table>
        <thead>
            <tr>
                <th style="width: 25%;">Memory Order</th>
                <th style="width: 40%;">Semantic Guarantee</th>
                <th style="width: 35%;">Emitted Machine Instructions</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><code>memory_order_relaxed</code></td>
                <td>Guarantees atomicity only. <strong>Zero ordering constraints.</strong> The CPU and compiler may freely reorder surrounding memory accesses.</td>
                <td>Plain load/store instructions (<code>LDR</code>, <code>STR</code> in ARM; <code>mov</code> in x86). Zero bus barrier penalty.</td>
            </tr>
            <tr>
                <td><code>memory_order_release</code></td>
                <td><strong>Store barrier:</strong> All prior memory stores (both atomic and non-atomic) in the current thread must be committed and visible before this store completes.</td>
                <td>ARM64: <code>STLR</code> (Store-Release) or <code>DMB ISHST</code>.<br>x86: Plain <code>mov</code> (x86 hardware enforces release stores naturally).</td>
            </tr>
            <tr>
                <td><code>memory_order_acquire</code></td>
                <td><strong>Load barrier:</strong> All subsequent memory loads in the current thread are forbidden from being reordered before this load.</td>
                <td>ARM64: <code>LDAR</code> (Load-Acquire) or <code>DMB ISHLD</code>.<br>x86: Plain <code>mov</code> (x86 hardware enforces acquire loads naturally).</td>
            </tr>
            <tr>
                <td><code>memory_order_acq_rel</code></td>
                <td>Combines acquire and release semantics on Read-Modify-Write operations (e.g. <code>fetch_add</code>, <code>exchange</code>).</td>
                <td>ARM64: <code>LDREX/STREX</code> loops with barriers or LSE <code>LDADDAL</code>.<br>x86: <code>lock xadd</code>.</td>
            </tr>
            <tr>
                <td><code>memory_order_seq_cst</code></td>
                <td><strong>Sequential Consistency:</strong> Enforces a single, globally visible total order of operations across all threads. Default in C++.</td>
                <td>ARM64: <code>STLR</code> followed by <code>DMB ISH</code>.<br>x86: <code>lock</code> prefixed instructions or <code>mfence</code>. High latency!</td>
            </tr>
        </tbody>
    </table>

    <div class="diagram">
ACQUIRE-RELEASE SYNCHRONIZATION BARRIER:
Thread 1 (Producer):                          Thread 2 (Consumer):
--------------------                          --------------------
data_buffer[i] = crypto_key; (Non-atomic)
write_idx.store(i+1, memory_order_release);   
            \
             \==== Synchronizes-With ====&gt;   r = write_idx.load(memory_order_acquire);
                                             read_key = data_buffer[r-1]; // GUARANTEED VISIBLE!
    </div>
</div>

<!-- CHAPTER 17 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 17</span> &bull; 
        <span>Topic: Lock-Free Single-Producer Single-Consumer Queues & False Sharing</span> &bull; 
        <span>Standard: C++20</span> &bull; 
        <span>Codebase Link: Mission 12 (Lock-Free Ring Buffer)</span>
    </div>

    <h1>Chapter 17: The Lock-Free SPSC Ring Buffer</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Lock-Free Data Structure:</strong> A concurrent data structure that guarantees system-wide progress without 
            employing mutual exclusion locks (mutexes). If one thread is preempted or crashes, other threads continue unobstructed.<br>
            <strong>Single-Producer Single-Consumer (SPSC):</strong> A concurrency topology where exactly one thread writes data 
            and exactly one thread reads data.<br>
            <strong>Power-of-Two Mask Wrapping:</strong> Allocating capacity as an exact power of two (\(C = 2^k\)). 
            Index wrapping simplifies from an expensive integer division/modulo instruction (<code>idx % C</code>, 20-40 CPU cycles) 
            to an instantaneous single-cycle bitwise AND instruction (<code>idx &amp; (C - 1)</code>).<br>
            <strong>False Sharing:</strong> A microarchitectural performance pathology where two distinct variables accessed by different 
            CPU cores reside on the <em>same 64-byte cache line</em>. Writing to one variable invalidates the entire cache line across 
            all other cores, causing catastrophic cache line bouncing.<br>
            <strong><code>std::hardware_destructive_interference_size</code>:</strong> C++17 constant defining the minimum byte padding 
            required to guarantee two variables occupy distinct physical cache lines (64 bytes on ARM64/x86).
        </p>
    </div>

    <div class="diagram">
FALSE SHARING (Single Cache Line Bounces Between Cores):
+-------------------------------------------------------------------------+
| Cache Line (64 Bytes): Core 0 writes _head (4B) | Core 1 writes _tail (4B)|
+-------------------------------------------------------------------------+
  ^ Core 0 writes -&gt; MESI Invalidates Core 1 L1 Cache -&gt; Severe Bus Stalls!

CACHE PADDING SOLUTION (Zero Interference):
+-------------------------------------------------------------------------+
| Cache Line 0: _head (alignas(64)) (64 Bytes Dedicated)                 |
+-------------------------------------------------------------------------+
+-------------------------------------------------------------------------+
| Cache Line 1: _tail (alignas(64)) (64 Bytes Dedicated)                 |
+-------------------------------------------------------------------------+
    </div>

    <h2>C++ Implementation: Production Lock-Free SPSC Queue</h2>
    <pre><code><span class="dir">#pragma once</span>

<span class="dir">#include</span> <span class="str">&lt;atomic&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;cstddef&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;new&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;optional&gt;</span>

<span class="com">// High-throughput lock-free circular queue for hardware telemetry</span>
<span class="kwd">template</span> &lt;<span class="kwd">typename</span> <span class="typ">T</span>, std::<span class="typ">size_t</span> Capacity&gt;
<span class="kwd">class</span> <span class="typ">LockFreeRingBuffer</span> {
    <span class="com">// Capacity must be power of two</span>
    <span class="kwd">static_assert</span>((Capacity &gt; <span class="num">0</span>) &amp;&amp; ((Capacity &amp; (Capacity - <span class="num">1</span>)) == <span class="num">0</span>), <span class="str">"Capacity must be a power of 2"</span>);
    <span class="kwd">static</span> <span class="kwd">constexpr</span> std::<span class="typ">size_t</span> mask = Capacity - <span class="num">1</span>;

    <span class="com">// Cache-line alignment prevents false sharing across cores</span>
    <span class="kwd">alignas</span>(<span class="num">64</span>) std::<span class="typ">atomic</span>&lt;std::<span class="typ">size_t</span>&gt; _write_idx{<span class="num">0</span>};
    <span class="kwd">alignas</span>(<span class="num">64</span>) std::<span class="typ">atomic</span>&lt;std::<span class="typ">size_t</span>&gt; _read_idx{<span class="num">0</span>};
    <span class="typ">T</span> _buffer[Capacity];

<span class="kwd">public</span>:
    <span class="typ">bool</span> <span class="fn">push</span>(<span class="kwd">const</span> <span class="typ">T</span>&amp; item) {
        <span class="kwd">const</span> std::<span class="typ">size_t</span> current_write = _write_idx.<span class="fn">load</span>(std::<span class="typ">memory_order_relaxed</span>);
        <span class="kwd">const</span> std::<span class="typ">size_t</span> current_read  = _read_idx.<span class="fn">load</span>(std::<span class="typ">memory_order_acquire</span>);

        <span class="com">// Buffer full check</span>
        <span class="kwd">if</span> (current_write - current_read == Capacity) {
            <span class="kwd">return</span> <span class="kwd">false</span>;
        }

        <span class="com">// Bitwise power-of-two wrapping (1 CPU cycle vs 30 cycles for modulo)</span>
        _buffer[current_write &amp; mask] = item;

        <span class="com">// Release store: guarantees written element is visible before index advances</span>
        _write_idx.<span class="fn">store</span>(current_write + <span class="num">1</span>, std::<span class="typ">memory_order_release</span>);
        <span class="kwd">return</span> <span class="kwd">true</span>;
    }

    std::<span class="typ">optional</span>&lt;<span class="typ">T</span>&gt; <span class="fn">pop</span>() {
        <span class="kwd">const</span> std::<span class="typ">size_t</span> current_read  = _read_idx.<span class="fn">load</span>(std::<span class="typ">memory_order_relaxed</span>);
        <span class="kwd">const</span> std::<span class="typ">size_t</span> current_write = _write_idx.<span class="fn">load</span>(std::<span class="typ">memory_order_acquire</span>);

        <span class="com">// Buffer empty check</span>
        <span class="kwd">if</span> (current_read == current_write) {
            <span class="kwd">return</span> std::<span class="typ">nullopt</span>;
        }

        <span class="typ">T</span> item = _buffer[current_read &amp; mask];

        <span class="com">// Release store: signals to producer that slot is now free</span>
        _read_idx.<span class="fn">store</span>(current_read + <span class="num">1</span>, std::<span class="typ">memory_order_release</span>);
        <span class="kwd">return</span> item;
    }
};</code></pre>
</div>

<!-- CHAPTER 18 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 18</span> &bull; 
        <span>Topic: C++20 Coroutines, Resumable Functions & Cooperative Schedulers</span> &bull; 
        <span>Standard: C++20</span> &bull; 
        <span>Codebase Link: Mission 15 (Coroutine Task Dispatcher)</span>
    </div>

    <h1>Chapter 18: C++20 Coroutines & Stackless Task Dispatchers</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Coroutine:</strong> A function that can suspend its execution to return control to a caller, 
            and later be resumed at the exact point of suspension, preserving its local variables.<br>
            <strong>Stackless Coroutine:</strong> Modern C++ coroutines do not allocate a dedicated CPU stack. 
            Instead, local state and suspension points are packed into a heap/arena-allocated <strong>Coroutine Frame</strong>.<br>
            <strong>The Three Keywords:</strong> <code>co_await</code> (suspends execution until an awaitable completes), 
            <code>co_yield</code> (suspends execution and returns an intermediate value), and <code>co_return</code> (completes execution and returns a final value).<br>
            <strong><code>promise_type</code>:</strong> The internal controller object defined within the coroutine return type 
            that dictates initial suspension, final suspension, result delivery, and exception handling.<br>
            <strong><code>coroutine_handle&lt;P&gt;</code>:</strong> A non-owning, type-erased handle used by schedulers to resume 
            (<code>handle.resume()</code>) or destroy (<code>handle.destroy()</code>) a suspended coroutine.
        </p>
    </div>

    <h2>The "Why": Discrete-Event Simulation Without Threads</h2>
    <p>
        Simulating an SoC with 50 peripheral devices in Verilator using standard OS threads incurs thousands of context switches 
        per simulated clock tick, bringing simulation speed to a crawl. 
        C++20 stackless coroutines model each peripheral as a cooperative state machine. Resuming a coroutine is as cheap as a 
        single indirect function call (5 nanoseconds), enabling millions of simulated clock transitions per second.
    </p>

    <h2>C++ Implementation: Minimal Coroutine Task & Scheduler</h2>
    <pre><code><span class="dir">#pragma once</span>

<span class="dir">#include</span> <span class="str">&lt;coroutine&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;queue&gt;</span>

<span class="kwd">struct</span> <span class="typ">Task</span> {
    <span class="kwd">struct</span> <span class="typ">promise_type</span> {
        <span class="typ">Task</span> <span class="fn">get_return_object</span>() {
            <span class="kwd">return</span> <span class="typ">Task</span>{std::<span class="typ">coroutine_handle</span>&lt;<span class="typ">promise_type</span>&gt;::<span class="fn">from_promise</span>(*<span class="kwd">this</span>)};
        }
        std::<span class="typ">suspend_always</span> <span class="fn">initial_suspend</span>() <span class="kwd">noexcept</span> { <span class="kwd">return</span> {}; } <span class="com">// Lazy evaluation</span>
        std::<span class="typ">suspend_always</span> <span class="fn">final_suspend</span>() <span class="kwd">noexcept</span> { <span class="kwd">return</span> {}; }   <span class="com">// Preserve frame for caller</span>
        <span class="typ">void</span> <span class="fn">return_void</span>() <span class="kwd">noexcept</span> {}
        <span class="typ">void</span> <span class="fn">unhandled_exception</span>() { std::<span class="fn">terminate</span>(); }
    };

    std::<span class="typ">coroutine_handle</span>&lt;<span class="typ">promise_type</span>&gt; handle;
    ~<span class="fn">Task</span>() { <span class="kwd">if</span> (handle) handle.<span class="fn">destroy</span>(); }
};

<span class="com">// Cooperative hardware clock event scheduler</span>
<span class="kwd">class</span> <span class="typ">HardwareScheduler</span> {
<span class="kwd">public</span>:
    <span class="typ">void</span> <span class="fn">enqueue</span>(std::<span class="typ">coroutine_handle</span>&lt;&gt; h) { _ready_queue.push(h); }

    <span class="typ">void</span> <span class="fn">tick_clock_cycle</span>() {
        <span class="kwd">const</span> std::<span class="typ">size_t</span> count = _ready_queue.size();
        <span class="kwd">for</span> (std::<span class="typ">size_t</span> i = <span class="num">0</span>; i &lt; count; ++i) {
            <span class="kwd">auto</span> h = _ready_queue.front();
            _ready_queue.pop();
            <span class="kwd">if</span> (!h.<span class="fn">done</span>()) {
                h.<span class="fn">resume</span>();
                <span class="kwd">if</span> (!h.<span class="fn">done</span>()) { _ready_queue.push(h); } <span class="com">// Re-enqueue for next clock tick</span>
            }
        }
    }

<span class="kwd">private</span>:
    std::<span class="typ">queue</span>&lt;std::<span class="typ">coroutine_handle</span>&lt;&gt;&gt; _ready_queue;
};</code></pre>
</div>

<!-- CHAPTER 19 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 19</span> &bull; 
        <span>Topic: Non-Owning string_view, C++20 Ranges & Lazy Pipeline Composition</span> &bull; 
        <span>Standard: C++20</span> &bull; 
        <span>Codebase Link: Mission 14 (Zero-Allocation Log Streamer)</span>
    </div>

    <h1>Chapter 19: Zero-Allocation Processing with Ranges & Views</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong><code>std::string_view</code>:</strong> A lightweight, non-owning view over a contiguous character buffer. 
            Consists of exactly two fields: a raw pointer (<code>const char*</code>) and a length (<code>size_t</code>). 
            Total footprint: 16 bytes.<br>
            <strong>C++20 Views (<code>std::views</code>):</strong> Lightweight, non-owning range adaptors that produce elements 
            lazily on demand without copying underlying data.<br>
            <strong>Pipeline Operator (<code>|</code>):</strong> Syntax allowing views to be composed sequentially into readable, 
            declarative transformation pipelines (e.g. <code>input | std::views::filter(...) | std::views::transform(...)</code>).<br>
            <strong>Dangling View Hazard:</strong> The critical bug where a <code>string_view</code> references a temporary 
            <code>std::string</code> that is destroyed at the semicolon, leaving the view's internal pointer pointing to freed memory.
        </p>
    </div>

    <h2>C++ Implementation: Declarative Zero-Copy Stream Parser</h2>
    <pre><code><span class="dir">#include</span> <span class="str">&lt;iostream&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;ranges&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;string_view&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;vector&gt;</span>

<span class="typ">int</span> <span class="fn">main</span>() {
    <span class="com">// Raw telemetry trace stored in static buffer (standing in for memory-mapped log)</span>
    <span class="kwd">constexpr</span> std::<span class="typ">string_view</span> raw_log = 
        <span class="str">"DEBUG:0x1000:INIT\n"</span>
        <span class="str">"# Comment line\n"</span>
        <span class="str">"ERROR:0x2004:BUS_FAULT\n"</span>
        <span class="str">"WARN:0x1008:TIMEOUT\n"</span>
        <span class="str">"ERROR:0x3000:CRYPTO_MISMATCH\n"</span>;

    <span class="com">// Zero-allocation pipeline: parses lines without allocating heap memory</span>
    <span class="kwd">auto</span> lines = raw_log 
        | std::<span class="typ">views</span>::<span class="fn">split</span>(<span class="str">'\n'</span>)
        | std::<span class="typ">views</span>::<span class="fn">transform</span>([](<span class="kwd">auto</span>&amp;&amp; rng) {
            <span class="kwd">return</span> std::<span class="typ">string_view</span>(&amp;*rng.<span class="fn">begin</span>(), std::<span class="typ">ranges</span>::<span class="fn">distance</span>(rng));
        })
        | std::<span class="typ">views</span>::<span class="fn">filter</span>([](std::<span class="typ">string_view</span> line) {
            <span class="kwd">return</span> !line.<span class="fn">empty</span>() &amp;&amp; !line.<span class="fn">starts_with</span>(<span class="str">'#'</span>);
        })
        | std::<span class="typ">views</span>::<span class="fn">filter</span>([](std::<span class="typ">string_view</span> line) {
            <span class="kwd">return</span> line.<span class="fn">starts_with</span>(<span class="str">"ERROR"</span>);
        });

    <span class="com">// Lazy iteration: lines are parsed only as the loop advances</span>
    <span class="kwd">for</span> (std::<span class="typ">string_view</span> err : lines) {
        std::cout &lt;&lt; <span class="str">"Active Security Alert: "</span> &lt;&lt; err &lt;&lt; <span class="str">"\n"</span>;
    }
    <span class="kwd">return</span> <span class="num">0</span>;
}</code></pre>
</div>
"""
