"""
part2_object_architecture.py - Part II: Modern C++ Object Architecture, Resource Discipline & Custom Allocators
"""

def get_part2_html():
    return r"""
<!-- PART II COVER -->
<div class="part-page">
    <div class="part-number">Part II</div>
    <div class="part-title">Modern C++ Object Architecture, Resource Discipline & Allocators</div>
    <div class="part-desc">
        Hardware security engineering requires uncompromising resource control. Software running close to silicon 
        cannot afford leaks, double-frees, or non-deterministic garbage collection. 
        This part establishes the foundational object lifecycle patterns of modern C++: encapsulation invariants, 
        the Rule of Three, value categories, zero-copy move semantics (Rule of Five), RAII smart pointer design, 
        exception-free monadic error architectures, and high-performance bare-metal slab allocators using intrusive free lists 
        and placement <code>new</code>.
    </div>
    <div class="part-chapters-list">
        <h4>Included Curriculum Chapters & Missions:</h4>
        <ul>
            <li><strong>Chapter 6:</strong> Encapsulation, Invariants & The Rule of Three (Mission 04)</li>
            <li><strong>Chapter 7:</strong> Value Categories, Move Semantics & The Rule of Five (Mission 06)</li>
            <li><strong>Chapter 8:</strong> The RAII Paradigm, Custom Smart Pointers & Scope Guards (Mission 07)</li>
            <li><strong>Chapter 9:</strong> Embedded & Bare-Metal Error Handling: Exceptions vs Monadic Types (Mission 07)</li>
            <li><strong>Chapter 10:</strong> Deterministic Bare-Metal Memory: The Slab Allocator & Placement New (Mission 08)</li>
        </ul>
    </div>
</div>

<!-- CHAPTER 6 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 6</span> &bull; 
        <span>Topic: Class Invariants, Initializer Lists & The Rule of Three</span> &bull; 
        <span>Standard: C++20</span> &bull; 
        <span>Codebase Link: Mission 04 (Armored Entity Engine)</span>
    </div>

    <h1>Chapter 6: Encapsulation, Invariants & The Rule of Three</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Encapsulation:</strong> The bundling of state variables within a class and restricting direct access 
            to enforce structural invariants through member functions.<br>
            <strong>Class Invariant:</strong> A condition regarding the state of an object that must hold true throughout its lifetime 
            (established by constructors and preserved across public member calls).<br>
            <strong>Member Initializer List:</strong> The constructor syntax (<code>: member(init)</code>) that initializes class fields 
            directly upon memory allocation. <strong>Critical Rule:</strong> Members are always initialized in the exact order they are 
            declared in the class definition, <em>regardless</em> of the order written in the initializer list.<br>
            <strong>Const-Correctness:</strong> The discipline of declaring member functions <code>const</code> when they do not alter 
            the logical state of the object. Within a <code>const</code> member function, the <code>this</code> pointer is typed 
            as <code>const ClassName* const</code>.<br>
            <strong>The Rule of Three:</strong> A fundamental C++ guideline: If a class manages a dynamically allocated resource 
            and implements a custom <strong>Destructor</strong>, it must also explicitly implement a custom <strong>Copy Constructor</strong> 
            and a custom <strong>Copy Assignment Operator</strong>.
        </p>
    </div>

    <h2>The "Why": The Double-Free Vulnerability</h2>
    <p>
        If a class manages a raw heap pointer (e.g. <code>uint32_t* _items</code>) and relies on compiler-generated copy operations, 
        the compiler performs a shallow bitwise copy (memberwise copy). 
        Both objects now hold pointers to the <em>exact same physical memory address</em>.
    </p>

    <div class="diagram">
SHALLOW COPY (Default Compiler Behavior - CATASTROPHIC):
Object A: [ _items: 0x5000 ] -----\
                                   +---> [ Heap Memory: Item Buffer ]
Object B: [ _items: 0x5000 ] -----/
When Object A goes out of scope -> delete[] 0x5000 (Memory freed).
When Object B goes out of scope -> delete[] 0x5000 (DOUBLE FREE CRASH / HEAP EXPLOIT!)

DEEP COPY (Rule of Three Implementation):
Object A: [ _items: 0x5000 ] ---------> [ Heap Buffer A (0x5000) ]
Object B: [ _items: 0x8000 ] ---------> [ Heap Buffer B (0x8000) ] (Independent clone)
    </div>

    <h2>C++ Implementation: The Armored Entity Engine</h2>
    <p>
        The following implementation from Mission 04 showcases full Rule of Three compliance, parameter validation, 
        and defensive deep copying:
    </p>

    <pre><code><span class="dir">#pragma once</span>

<span class="dir">#include</span> <span class="str">&lt;cstddef&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;cstdint&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;stdexcept&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;string&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;utility&gt;</span>

<span class="kwd">class</span> <span class="typ">Entity</span> {
<span class="kwd">public</span>:
    <span class="com">// Parameterised constructor: Enforces invariants before allocation</span>
    <span class="fn">Entity</span>(std::<span class="typ">string</span> name, <span class="kwd">const</span> <span class="typ">int</span> health, <span class="kwd">const</span> <span class="typ">int</span> armour)
        : _name(std::<span class="fn">move</span>(name)), _health(health), _armour(armour), 
          _items(<span class="kwd">nullptr</span>), _capacity(<span class="num">1</span>), _item_counter(<span class="num">0</span>) {
        <span class="kwd">if</span> (armour &lt; <span class="num">0</span>) { <span class="kwd">throw</span> std::<span class="typ">invalid_argument</span>(<span class="str">"armour must be &gt;= 0"</span>); }
        <span class="kwd">if</span> (health &lt; <span class="num">0</span> || health &gt; <span class="num">100</span>) { <span class="kwd">throw</span> std::<span class="typ">invalid_argument</span>(<span class="str">"health must be 0..100"</span>); }

        _items = <span class="kwd">new</span> <span class="typ">uint32_t</span>[_capacity];
    }

    <span class="com">// 1. DESTRUCTOR: Releases owned resource</span>
    ~<span class="fn">Entity</span>() {
        <span class="kwd">delete</span>[] _items;
    }

    <span class="com">// 2. COPY CONSTRUCTOR: Deep copy allocation guarantees independent ownership</span>
    <span class="fn">Entity</span>(<span class="kwd">const</span> <span class="typ">Entity</span>&amp; other)
        : _name(other._name), _health(other._health), _armour(other._armour),
          _items(<span class="kwd">nullptr</span>), _capacity(other._capacity), _item_counter(other._item_counter) {
        _items = <span class="kwd">new</span> <span class="typ">uint32_t</span>[_capacity];
        <span class="kwd">for</span> (std::<span class="typ">size_t</span> i = <span class="num">0</span>; i &lt; _item_counter; ++i) {
            _items[i] = other._items[i];
        }
    }

    <span class="com">// 3. COPY ASSIGNMENT OPERATOR: Self-assignment guarded &amp; exception-safe</span>
    <span class="typ">Entity</span>&amp; <span class="kwd">operator</span>=(<span class="kwd">const</span> <span class="typ">Entity</span>&amp; other) {
        <span class="kwd">if</span> (<span class="kwd">this</span> == &amp;other) {
            <span class="kwd">return</span> *<span class="kwd">this</span>; <span class="com">// Guard against self-destruction</span>
        }

        <span class="com">// Allocate new storage before releasing old; guarantees strong exception safety</span>
        <span class="typ">uint32_t</span>* new_items = <span class="kwd">new</span> <span class="typ">uint32_t</span>[other._capacity];
        <span class="kwd">for</span> (std::<span class="typ">size_t</span> i = <span class="num">0</span>; i &lt; other._item_counter; ++i) {
            new_items[i] = other._items[i];
        }

        <span class="kwd">delete</span>[] _items;
        _items = new_items;
        _name = other._name;
        _health = other._health;
        _armour = other._armour;
        _capacity = other._capacity;
        _item_counter = other._item_counter;

        <span class="kwd">return</span> *<span class="kwd">this</span>;
    }

    <span class="com">// Queries marked const: guarantees logical state remains immutable</span>
    <span class="kwd">const</span> std::<span class="typ">string</span>&amp; <span class="fn">get_name</span>() <span class="kwd">const</span> { <span class="kwd">return</span> _name; }
    <span class="typ">int</span> <span class="fn">get_health</span>() <span class="kwd">const</span> { <span class="kwd">return</span> _health; }
    <span class="typ">bool</span> <span class="fn">is_alive</span>() <span class="kwd">const</span> { <span class="kwd">return</span> _health &gt; <span class="num">0</span>; }

<span class="kwd">private</span>:
    std::<span class="typ">string</span> _name;
    <span class="typ">int</span> _health;
    <span class="typ">int</span> _armour;
    <span class="typ">uint32_t</span>* _items;
    std::<span class="typ">size_t</span> _capacity;
    std::<span class="typ">size_t</span> _item_counter;
};</code></pre>
</div>

<!-- CHAPTER 7 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 7</span> &bull; 
        <span>Topic: Value Categories, Rvalue References, Move Semantics & The Rule of Five</span> &bull; 
        <span>Standard: C++20</span> &bull; 
        <span>Codebase Link: Mission 06 (Zero-Copy Buffer Vault)</span>
    </div>

    <h1>Chapter 7: Value Categories, Move Semantics & The Rule of Five</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Value Categories:</strong> In C++, every expression is classified along two axes:
            <ul>
                <li><strong>Identity:</strong> Does the expression refer to a specific memory location whose address can be taken (<code>&amp;expr</code>)?</li>
                <li><strong>Movable:</strong> Can the expression's resources be safely stolen because the value will expire?</li>
                <li><strong>lvalue:</strong> Has identity and cannot be moved from (e.g. named variables <code>int x;</code>).</li>
                <li><strong>prvalue (Pure Rvalue):</strong> Computes a value that does not have identity and is temporary (e.g. literals <code>42</code>, function return by value).</li>
                <li><strong>xvalue (Expiring Value):</strong> Has identity and can be moved from (e.g. result of <code>std::move(x)</code>).</li>
            </ul>
            <strong>Rvalue Reference (<code>T&amp;&amp;</code>):</strong> A reference type that binds specifically to rvalues (temporaries or xvalues), 
            enabling the definition of move operations.<br>
            <strong>Move Semantics:</strong> Transferring ownership of an underlying resource (pointers, file handles, DMA buffers) 
            from an expiring source object to a target object in \(O(1)\) time without performing deep memory copies.<br>
            <strong>The <code>std::move</code> Cast:</strong> An unconditional static cast that converts an expression to an rvalue reference 
            (<code>static_cast&lt;T&amp;&amp;&gt;(x)</code>). <em>Crucial Reality:</em> <code>std::move</code> does NOT move anything itself; 
            it merely signals that the resource may be stolen.<br>
            <strong>The Rule of Five:</strong> If a class defines a custom destructor, copy constructor, or copy assignment operator, 
            it should explicitly declare all five lifecycle functions: (1) Destructor, (2) Copy Constructor, (3) Copy Assignment, 
            (4) Move Constructor, and (5) Move Assignment Operator.<br>
            <strong>Copy Elision / RVO:</strong> Return Value Optimization where the compiler constructs a return value directly in 
            the caller's memory frame, omitting both copy and move constructors entirely.
        </p>
    </div>

    <h2>The "Why": Eliminating Memory Bandwidth Bottlenecks</h2>
    <p>
        In network packet processing and post-quantum cryptographic schemes, buffers can span hundreds of kilobytes. 
        Deep-copying buffers across function boundaries floods the memory bus and wastes CPU cycles. 
        Move semantics transforms a multi-megabyte memory copy into a <strong>3-instruction pointer swap</strong>.
    </p>

    <h2>C++ Implementation: The Zero-Copy Buffer Vault</h2>
    <p>
        Below is the production implementation from Mission 06, complete with telemetry tracking:
    </p>

    <pre><code><span class="dir">#pragma once</span>

<span class="dir">#include</span> <span class="str">&lt;cstddef&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;cstdint&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;cstring&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;utility&gt;</span>

<span class="kwd">class</span> <span class="typ">PacketBuffer</span> {
<span class="kwd">public</span>:
    <span class="com">// Telemetry counters to physically verify move vs copy execution</span>
    <span class="kwd">inline</span> <span class="kwd">static</span> std::<span class="typ">size_t</span> copy_count = <span class="num">0</span>;
    <span class="kwd">inline</span> <span class="kwd">static</span> std::<span class="typ">size_t</span> move_count = <span class="num">0</span>;

    <span class="kwd">explicit</span> <span class="fn">PacketBuffer</span>(std::<span class="typ">size_t</span> size)
        : _data(<span class="kwd">new</span> <span class="typ">uint8_t</span>[size]{}), _size(size) {}

    <span class="com">// 1. DESTRUCTOR</span>
    ~<span class="fn">PacketBuffer</span>() <span class="kwd">noexcept</span> {
        <span class="kwd">delete</span>[] _data;
    }

    <span class="com">// 2. COPY CONSTRUCTOR (O(N) Deep Copy)</span>
    <span class="fn">PacketBuffer</span>(<span class="kwd">const</span> <span class="typ">PacketBuffer</span>&amp; other)
        : _data(<span class="kwd">new</span> <span class="typ">uint8_t</span>[other._size]), _size(other._size) {
        std::<span class="fn">memcpy</span>(_data, other._data, _size);
        ++copy_count;
    }

    <span class="com">// 3. COPY ASSIGNMENT (O(N) Deep Copy)</span>
    <span class="typ">PacketBuffer</span>&amp; <span class="kwd">operator</span>=(<span class="kwd">const</span> <span class="typ">PacketBuffer</span>&amp; other) {
        <span class="kwd">if</span> (<span class="kwd">this</span> != &amp;other) {
            <span class="typ">uint8_t</span>* new_data = <span class="kwd">new</span> <span class="typ">uint8_t</span>[other._size];
            std::<span class="fn">memcpy</span>(new_data, other._data, other._size);
            <span class="kwd">delete</span>[] _data;
            _data = new_data;
            _size = other._size;
            ++copy_count;
        }
        <span class="kwd">return</span> *<span class="kwd">this</span>;
    }

    <span class="com">// 4. MOVE CONSTRUCTOR (O(1) Pointer Theft)</span>
    <span class="com">// Must be noexcept so STL containers (std::vector) use moves instead of copies during reallocation</span>
    <span class="fn">PacketBuffer</span>(<span class="typ">PacketBuffer</span>&amp;&amp; other) <span class="kwd">noexcept</span>
        : _data(other._data), _size(other._size) {
        <span class="com">// Leave source object in valid, destructible, empty state</span>
        other._data = <span class="kwd">nullptr</span>;
        other._size = <span class="num">0</span>;
        ++move_count;
    }

    <span class="com">// 5. MOVE ASSIGNMENT (O(1) Pointer Theft)</span>
    <span class="typ">PacketBuffer</span>&amp; <span class="kwd">operator</span>=(<span class="typ">PacketBuffer</span>&amp;&amp; other) <span class="kwd">noexcept</span> {
        <span class="kwd">if</span> (<span class="kwd">this</span> != &amp;other) {
            <span class="com">// Release current resource first</span>
            <span class="kwd">delete</span>[] _data;

            <span class="com">// Steal pointer and state</span>
            _data = other._data;
            _size = other._size;

            <span class="com">// Blank source object</span>
            other._data = <span class="kwd">nullptr</span>;
            other._size = <span class="num">0</span>;
            ++move_count;
        }
        <span class="kwd">return</span> *<span class="kwd">this</span>;
    }

<span class="kwd">private</span>:
    <span class="typ">uint8_t</span>* _data;
    std::<span class="typ">size_t</span> _size;
};</code></pre>
</div>

<!-- CHAPTER 8 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 8</span> &bull; 
        <span>Topic: RAII, Smart Pointers, Custom Deleters & Atomic Reference Counting</span> &bull; 
        <span>Standard: C++20</span> &bull; 
        <span>Codebase Link: Mission 07 (Ownership Toolkit)</span>
    </div>

    <h1>Chapter 8: The RAII Paradigm, Custom Smart Pointers & Scope Guards</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>RAII (Resource Acquisition Is Initialization):</strong> A core C++ design pattern where resource acquisition 
            (memory allocation, hardware register locking, file opening) is tied to object construction, and resource release 
            is tied to object destruction. When an object leaves scope, its destructor is guaranteed to execute.<br>
            <strong>Move-Only Owning Pointer (<code>UniquePtr&lt;T, Deleter&gt;</code>):</strong> A zero-overhead smart pointer that 
            retains exclusive ownership of a resource. Copying is deleted; ownership transfer requires explicit moves.<br>
            <strong>Custom Deleter:</strong> A callable policy passed to a smart pointer to execute non-standard deallocation logic 
            (e.g., closing file descriptors with <code>close()</code>, unmapping hardware MMIO pages with <code>munmap()</code>, 
            or returning slots to a custom slab arena).<br>
            <strong>Shared Pointer (<code>SharedPtr&lt;T&gt;</code>):</strong> A reference-counted smart pointer managing a shared heap-allocated 
            <strong>Control Block</strong> containing strong and weak reference counts.<br>
            <strong>Scope Guard:</strong> A lightweight utility that executes an arbitrary lambda function upon scope exit, 
            guaranteeing rollback or cleanup actions.
        </p>
    </div>

    <h2>The "Why": The Myth of Thread-Safe Smart Pointers</h2>
    <div class="callout callout-sec">
        <div class="callout-header">Critical Security Distinction: Control Block vs Managed Object</div>
        <p>
            A common, dangerous mistake among systems programmers is assuming that because <code>std::shared_ptr</code> 
            uses atomic reference counting, access to the pointed-to object is thread-safe. 
            <strong>It is not.</strong> 
            The atomic operations protect <em>only</em> the reference counter inside the control block. 
            Simultaneous reads and writes to the underlying hardware device or object data from two different threads 
            without a mutex or lock-free synchronization constitutes a <strong>data race (Undefined Behavior)</strong>.
        </p>
    </div>

    <h2>C++ Implementation: UniquePtr with Custom Deleters & ScopeGuard</h2>
    <pre><code><span class="dir">#pragma once</span>

<span class="dir">#include</span> <span class="str">&lt;utility&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;type_traits&gt;</span>

<span class="com">// Default deleter utilizing standard delete</span>
<span class="kwd">template</span> &lt;<span class="kwd">typename</span> <span class="typ">T</span>&gt;
<span class="kwd">struct</span> <span class="typ">DefaultDeleter</span> {
    <span class="typ">void</span> <span class="kwd">operator</span>()(<span class="typ">T</span>* ptr) <span class="kwd">const</span> <span class="kwd">noexcept</span> {
        <span class="kwd">delete</span> ptr;
    }
};

<span class="com">// Move-only exclusive smart pointer supporting hardware/MMIO custom deleters</span>
<span class="kwd">template</span> &lt;<span class="kwd">typename</span> <span class="typ">T</span>, <span class="kwd">typename</span> <span class="typ">Deleter</span> = <span class="typ">DefaultDeleter</span>&lt;<span class="typ">T</span>&gt;&gt;
<span class="kwd">class</span> <span class="typ">UniquePtr</span> {
<span class="kwd">public</span>:
    <span class="kwd">explicit</span> <span class="fn">UniquePtr</span>(<span class="typ">T</span>* ptr = <span class="kwd">nullptr</span>, <span class="typ">Deleter</span> deleter = <span class="typ">Deleter</span>{})
        : _ptr(ptr), _deleter(std::<span class="fn">move</span>(deleter)) {}

    ~<span class="fn">UniquePtr</span>() <span class="kwd">noexcept</span> {
        <span class="fn">reset</span>();
    }

    <span class="com">// Copy semantics strictly disabled</span>
    <span class="fn">UniquePtr</span>(<span class="kwd">const</span> <span class="typ">UniquePtr</span>&amp;) = <span class="kwd">delete</span>;
    <span class="typ">UniquePtr</span>&amp; <span class="kwd">operator</span>=(<span class="kwd">const</span> <span class="typ">UniquePtr</span>&amp;) = <span class="kwd">delete</span>;

    <span class="com">// Move constructor: transfer ownership</span>
    <span class="fn">UniquePtr</span>(<span class="typ">UniquePtr</span>&amp;&amp; other) <span class="kwd">noexcept</span>
        : _ptr(other._ptr), _deleter(std::<span class="fn">move</span>(other._deleter)) {
        other._ptr = <span class="kwd">nullptr</span>;
    }

    <span class="com">// Move assignment: clean existing resource and steal</span>
    <span class="typ">UniquePtr</span>&amp; <span class="kwd">operator</span>=(<span class="typ">UniquePtr</span>&amp;&amp; other) <span class="kwd">noexcept</span> {
        <span class="kwd">if</span> (<span class="kwd">this</span> != &amp;other) {
            <span class="fn">reset</span>();
            _ptr = other._ptr;
            _deleter = std::<span class="fn">move</span>(other._deleter);
            other._ptr = <span class="kwd">nullptr</span>;
        }
        <span class="kwd">return</span> *<span class="kwd">this</span>;
    }

    <span class="typ">T</span>* <span class="fn">get</span>() <span class="kwd">const</span> <span class="kwd">noexcept</span> { <span class="kwd">return</span> _ptr; }
    <span class="typ">T</span>* <span class="fn">release</span>() <span class="kwd">noexcept</span> { <span class="typ">T</span>* temp = _ptr; _ptr = <span class="kwd">nullptr</span>; <span class="kwd">return</span> temp; }

    <span class="typ">void</span> <span class="fn">reset</span>(<span class="typ">T</span>* new_ptr = <span class="kwd">nullptr</span>) <span class="kwd">noexcept</span> {
        <span class="kwd">if</span> (_ptr) {
            _deleter(_ptr);
        }
        _ptr = new_ptr;
    }

    <span class="typ">T</span>&amp; <span class="kwd">operator</span>*() <span class="kwd">const</span> { <span class="kwd">return</span> *_ptr; }
    <span class="typ">T</span>* <span class="kwd">operator</span>-&gt;() <span class="kwd">const</span> { <span class="kwd">return</span> _ptr; }

<span class="kwd">private</span>:
    <span class="typ">T</span>* _ptr;
    <span class="typ">Deleter</span> _deleter;
};

<span class="com">// ScopeGuard: Executes lambda on scope exit</span>
<span class="kwd">template</span> &lt;<span class="kwd">typename</span> <span class="typ">F</span>&gt;
<span class="kwd">class</span> <span class="typ">ScopeGuard</span> {
<span class="kwd">public</span>:
    <span class="kwd">explicit</span> <span class="fn">ScopeGuard</span>(<span class="typ">F</span>&amp;&amp; f) : _func(std::<span class="fn">forward</span>&lt;<span class="typ">F</span>&gt;(f)), _active(<span class="kwd">true</span>) {}
    ~<span class="fn">ScopeGuard</span>() { <span class="kwd">if</span> (_active) { _func(); } }
    <span class="typ">void</span> <span class="fn">dismiss</span>() <span class="kwd">noexcept</span> { _active = <span class="kwd">false</span>; }
<span class="kwd">private</span>:
    <span class="typ">F</span> _func;
    <span class="typ">bool</span> _active;
};</code></pre>
</div>

<!-- CHAPTER 9 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 9</span> &bull; 
        <span>Topic: Bare-Metal Error Handling, -fno-exceptions & Monadic Expected Types</span> &bull; 
        <span>Standard: C++20</span> &bull; 
        <span>Codebase Link: Mission 07 (Ownership Toolkit)</span>
    </div>

    <h1>Chapter 9: Embedded Error Handling: Exceptions vs Monadic Types</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>C++ Exceptions:</strong> A language mechanism allowing errors to propagate across stack frames via <code>throw</code> 
            and <code>catch</code>, invoking automatic stack unwinding and destructor execution.<br>
            <strong>Zero-Cost Exception Model:</strong> The implementation strategy (e.g. Itanium C++ ABI) where normal execution paths 
            incur zero CPU instruction overhead, but throwing an exception incurs massive overhead by consulting read-only 
            DWARF unwinding tables to reconstruct the call stack.<br>
            <strong>Bare-Metal Flag (<code>-fno-exceptions</code>):</strong> Compiler flag disabling exception handling entirely. 
            Attempts to <code>throw</code> result in an immediate call to <code>std::abort()</code> or compile errors.<br>
            <strong>Monadic Error Handling (<code>std::expected&lt;T, E&gt;</code> / <code>Result&lt;T, E&gt;</code>):</strong> 
            A vocabulary type that contains either a valid result of type <code>T</code> or an error descriptor of type <code>E</code>. 
            Forces the caller to inspect and unwrap the result without exceptions.
        </p>
    </div>

    <h2>The "Why": Why Silicon Firmware Bans Exceptions</h2>
    <p>
        In bare-metal embedded systems (e.g., RISC-V Ibex core or ARM Cortex-M), exceptions are universally prohibited for three reasons:
    </p>
    <ol>
        <li><strong>Binary Footprint:</strong> Exception unwinding tables (<code>.eh_frame</code> in ELF) increase the binary size by 20% to 50%, exceeding micro-SRAM and ROM limits.</li>
        <li><strong>Non-Deterministic Timing:</strong> Unwinding the stack can take thousands of cycles depending on the depth of the call chain, destroying real-time determinism.</li>
        <li><strong>Interrupt Service Routines (ISRs):</strong> Microcontroller hardware interrupt routines execute on isolated interrupt stacks; throwing an exception across a hardware interrupt boundary causes an immediate system reset or double fault.</li>
    </ol>

    <h2>C++ Implementation: The Lightweight Result Type</h2>
    <pre><code><span class="dir">#pragma once</span>

<span class="dir">#include</span> <span class="str">&lt;utility&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;variant&gt;</span>

<span class="com">// Embedded-friendly Result type: Zero heap, zero exceptions, deterministic</span>
<span class="kwd">template</span> &lt;<span class="kwd">typename</span> <span class="typ">T</span>, <span class="kwd">typename</span> <span class="typ">E</span>&gt;
<span class="kwd">class</span> <span class="typ">Result</span> {
<span class="kwd">public</span>:
    <span class="kwd">static</span> <span class="typ">Result</span> <span class="fn">ok</span>(<span class="typ">T</span> value) { <span class="kwd">return</span> <span class="typ">Result</span>(std::<span class="fn">in_place_index</span>&lt;<span class="num">0</span>&gt;, std::<span class="fn">move</span>(value)); }
    <span class="kwd">static</span> <span class="typ">Result</span> <span class="fn">err</span>(<span class="typ">E</span> error) { <span class="kwd">return</span> <span class="typ">Result</span>(std::<span class="fn">in_place_index</span>&lt;<span class="num">1</span>&gt;, std::<span class="fn">move</span>(error)); }

    <span class="typ">bool</span> <span class="fn">is_ok</span>() <span class="kwd">const</span> <span class="kwd">noexcept</span> { <span class="kwd">return</span> _storage.index() == <span class="num">0</span>; }
    <span class="typ">bool</span> <span class="fn">is_err</span>() <span class="kwd">const</span> <span class="kwd">noexcept</span> { <span class="kwd">return</span> _storage.index() == <span class="num">1</span>; }

    <span class="kwd">const</span> <span class="typ">T</span>&amp; <span class="fn">value</span>() <span class="kwd">const</span> { <span class="kwd">return</span> std::<span class="fn">get</span>&lt;<span class="num">0</span>&gt;(_storage); }
    <span class="kwd">const</span> <span class="typ">E</span>&amp; <span class="fn">error</span>() <span class="kwd">const</span> { <span class="kwd">return</span> std::<span class="fn">get</span>&lt;<span class="num">1</span>&gt;(_storage); }

<span class="kwd">private</span>:
    <span class="kwd">template</span> &lt;std::<span class="typ">size_t</span> I, <span class="kwd">typename</span> <span class="typ">Arg</span>&gt;
    <span class="fn">Result</span>(std::<span class="typ">in_place_index_t</span>&lt;I&gt; tag, <span class="typ">Arg</span>&amp;&amp; arg)
        : _storage(tag, std::<span class="fn">forward</span>&lt;<span class="typ">Arg</span>&gt;(arg)) {}

    std::<span class="typ">variant</span>&lt;<span class="typ">T</span>, <span class="typ">E</span>&gt; _storage;
};</code></pre>
</div>

<!-- CHAPTER 10 -->
<div class="page-break" style="padding: 10mm 5mm;">
    <div class="chapter-meta">
        <span class="chapter-meta-tag">Chapter 10</span> &bull; 
        <span>Topic: Fixed-Block Slab Allocators, Intrusive Free Lists & Placement New</span> &bull; 
        <span>Standard: C++20</span> &bull; 
        <span>Codebase Link: Mission 08 (Bare-Metal Slab Allocator)</span>
    </div>

    <h1>Chapter 10: Deterministic Bare-Metal Memory: The Slab Allocator</h1>

    <div class="callout callout-def">
        <div class="callout-header">Core Definitions</div>
        <p>
            <strong>Slab Allocator:</strong> A custom memory management architecture that pre-allocates a contiguous memory arena 
            and carves it into fixed-size uniform slots. Yields guaranteed \(O(1)\) constant-time allocation and deallocation.<br>
            <strong>Intrusive Free List:</strong> A zero-overhead data structure where the pointers connecting unallocated slots 
            are stored <em>directly inside the free memory slots themselves</em>. When a slot is free, its first 8 bytes represent 
            a pointer (<code>FreeNode* next</code>) to the next available slot. When allocated, the slot holds user data.<br>
            <strong>Placement New (<code>::new (ptr) T(...)</code>):</strong> A C++ syntax that constructs an object in-place 
            at a specific, pre-existing memory address without allocating heap storage.<br>
            <strong>Explicit Destructor Invocation (<code>ptr-&gt;~T()</code>):</strong> Explicitly calling the destructor of an object 
            constructed via placement new to execute its cleanup logic without deallocating the backing memory block.<br>
            <strong>Cache-Line Alignment (<code>alignas(64)</code>):</strong> Aligning the arena memory buffer to a 64-byte boundary, 
            guaranteeing that slot boundaries never straddle hardware cache lines.
        </p>
    </div>

    <div class="diagram">
INTRUSIVE FREE LIST MEMORY ARENA ARCHITECTURE:
+------------------------------------+------------------------------------+------------------------------------+
| Slot 0 (Unallocated)               | Slot 1 (ALLOCATED by User)         | Slot 2 (Unallocated)               |
| +-----------------+--------------+ | +--------------------------------+ | +-----------------+--------------+ |
| | next: &amp;Slot 2   | Unused (56B) | | | Object Data (64 Bytes)          | | | next: nullptr   | Unused (56B) | |
| +-----------------+--------------+ | +--------------------------------+ | +-----------------+--------------+ |
+------------------------------------+------------------------------------+------------------------------------+
  ^ _free_head points here
    </div>

    <h2>C++ Implementation: The Production Bare-Metal Slab Allocator</h2>
    <pre><code><span class="dir">#pragma once</span>

<span class="dir">#include</span> <span class="str">&lt;cstddef&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;cstdint&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;new&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;stdexcept&gt;</span>
<span class="dir">#include</span> <span class="str">&lt;utility&gt;</span>

<span class="kwd">template</span> &lt;<span class="kwd">typename</span> <span class="typ">T</span>, std::<span class="typ">size_t</span> SlotCount&gt;
<span class="kwd">class</span> <span class="typ">SlabAllocator</span> {
<span class="kwd">private</span>:
    <span class="com">// Node structure stored INSIDE the free slot itself</span>
    <span class="kwd">struct</span> <span class="typ">FreeNode</span> {
        <span class="typ">FreeNode</span>* next;
    };

    <span class="kwd">static</span> <span class="kwd">constexpr</span> std::<span class="typ">size_t</span> slot_size = (<span class="kwd">sizeof</span>(<span class="typ">T</span>) &gt; <span class="kwd">sizeof</span>(<span class="typ">FreeNode</span>)) ? <span class="kwd">sizeof</span>(<span class="typ">T</span>) : <span class="kwd">sizeof</span>(<span class="typ">FreeNode</span>);
    <span class="kwd">static</span> <span class="kwd">constexpr</span> std::<span class="typ">size_t</span> slot_alignment = <span class="kwd">alignof</span>(<span class="typ">T</span>);

    <span class="com">// Arena buffer aligned to 64-byte hardware cache line boundary</span>
    <span class="kwd">alignas</span>(<span class="num">64</span>) <span class="typ">uint8_t</span> _arena[SlotCount * slot_size];
    <span class="typ">FreeNode</span>* _free_head{<span class="kwd">nullptr</span>};

<span class="kwd">public</span>:
    <span class="fn">SlabAllocator</span>() {
        <span class="com">// Initialise intrusive list linking all free slots together</span>
        <span class="kwd">for</span> (std::<span class="typ">size_t</span> i = <span class="num">0</span>; i &lt; SlotCount; ++i) {
            <span class="typ">uint8_t</span>* slot_ptr = _arena + (i * slot_size);
            <span class="typ">FreeNode</span>* node = <span class="kwd">reinterpret_cast</span>&lt;<span class="typ">FreeNode</span>*&gt;(slot_ptr);
            node-&gt;next = _free_head;
            _free_head = node;
        }
    }

    <span class="com">// O(1) allocation + in-place placement new construction</span>
    <span class="kwd">template</span> &lt;<span class="kwd">typename</span>... <span class="typ">Args</span>&gt;
    <span class="typ">T</span>* <span class="fn">allocate</span>(<span class="typ">Args</span>&amp;&amp;... args) {
        <span class="kwd">if</span> (!_free_head) {
            <span class="kwd">throw</span> std::<span class="typ">bad_alloc</span>(); <span class="com">// Fixed pool exhausted</span>
        }

        <span class="com">// Pop slot from intrusive head</span>
        <span class="typ">FreeNode</span>* node = _free_head;
        _free_head = _free_head-&gt;next;

        <span class="com">// Placement new: construct object directly inside arena slot</span>
        <span class="kwd">return</span> ::<span class="kwd">new</span> (<span class="kwd">static_cast</span>&lt;<span class="typ">void</span>*&gt;(node)) <span class="typ">T</span>(std::<span class="fn">forward</span>&lt;<span class="typ">Args</span>&gt;(args)...);
    }

    <span class="com">// O(1) deallocation: explicitly call destructor and return slot to intrusive list</span>
    <span class="typ">void</span> <span class="fn">deallocate</span>(<span class="typ">T</span>* ptr) <span class="kwd">noexcept</span> {
        <span class="kwd">if</span> (!ptr) <span class="kwd">return</span>;

        <span class="com">// 1. Explicitly invoke destructor</span>
        ptr-&gt;~<span class="typ">T</span>();

        <span class="com">// 2. Push slot back onto intrusive free list</span>
        <span class="typ">FreeNode</span>* node = <span class="kwd">reinterpret_cast</span>&lt;<span class="typ">FreeNode</span>*&gt;(ptr);
        node-&gt;next = _free_head;
        _free_head = node;
    }
};</code></pre>
</div>
"""
