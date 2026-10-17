# C++ Under the Hood

**Hands-on missions for learning what the compiler really does with your C++.**

Fifteen self-contained missions that take you from raw arrays and pointers to lock-free queues and
coroutines. Each one asks you to build something real, then shows you what the optimizer, the
memory model, and the hardware do with it. Each finished mission includes my own worked solution.

> Created and maintained by **Benjamin** · [@BenyHanonove](https://github.com/BenyHanonove)
>
> I built this while teaching myself low-level C++ for hardware-security work. The solutions are
> mine, written as I went. They aren't the only correct answers, so read them after you have tried
> the mission yourself.

---

## Who this is for

You already know basic C++ syntax and want to understand it below the surface:

- what a copy, a move, or a virtual call **costs**, and when the compiler removes it
- why code that works at `-O0` breaks at `-O2` (undefined behaviour, strict aliasing)
- how objects are laid out in memory: padding, alignment, vtables, endianness
- how to write code that talks to hardware registers, owns memory safely, and runs concurrently
  without races

## How each mission works

Every mission folder contains a `README.md` with:

| Section | What it gives you |
|---|---|
| **Mission Brief** | The scenario and what you are building |
| **Objectives** | A checklist of concrete tasks |
| **Constraints & Edge Cases** | The traps, many of them undefined behaviour the optimizer will exploit |
| **Why This Matters** | Where this shows up in real low-level and hardware work |
| **Definition of Done** | How you know you are finished: clean build, passing tests, clean sanitizers |

Try the mission from the brief first. Open the solution files only after you have your own
version, or when you are stuck.

## The missions

| # | Mission | Topics | Solution |
|---|---|---|---|
| 01 | [Matrix Perimeter Scanner](<Advanced C & C++ for Low-Level Systems/missions/01-matrix-perimeter-scanner/>) | Fundamental types, fixed 2D arrays, loops | ✅ Solved |
| 02 | [Manual Heap Vector](<Advanced C & C++ for Low-Level Systems/missions/02-manual-heap-vector/>) | Raw pointers, `new`/`delete`, dynamic resizing | ✅ Solved |
| 03 | [Register Map Autopsy](<Advanced C & C++ for Low-Level Systems/missions/03-register-map-autopsy/>) | Bit manipulation, `volatile`, MMIO, endianness, padding, type punning, UB | ✅ Solved |
| 04 | [Armored Entity Engine](<Advanced C & C++ for Low-Level Systems/missions/04-armored-entity-engine/>) | Classes, const-correctness, Rule of Three | ✅ Solved |
| 05 | [Virtual Peripheral Tree](<Advanced C & C++ for Low-Level Systems/missions/05-virtual-peripheral-tree/>) | Inheritance, virtual dispatch, object layout, slicing | ✅ Solved |
| 06 | [Zero-Copy Buffer Vault](<Advanced C & C++ for Low-Level Systems/missions/06-zero-copy-buffer-vault/>) | Move semantics, Rule of Five, copy elision at `-O2` | ✅ Solved |
| 07 | [Ownership Toolkit](<Advanced C & C++ for Low-Level Systems/missions/07-ownership-toolkit/>) | RAII, `unique_ptr`/`shared_ptr`/`weak_ptr` from scratch, exception safety | 🚧 In progress |
| 08 | [Bare-Metal Slab Allocator](<Advanced C & C++ for Low-Level Systems/missions/08-bare-metal-slab-allocator/>) | Placement new, custom allocation, cache alignment | 📝 Coming soon |
| 09 | [Two-Language Build](<Advanced C & C++ for Low-Level Systems/missions/09-two-language-build/>) | Linkage, ODR, name mangling, C interop | 📝 Coming soon |
| 10 | [Compile-Time Math Core](<Advanced C & C++ for Low-Level Systems/missions/10-compile-time-math-core/>) | Templates, concepts, `constexpr`, `consteval` | 📝 Coming soon |
| 11 | [Concurrent Thread Pipeline](<Advanced C & C++ for Low-Level Systems/missions/11-concurrent-thread-pipeline/>) | `std::jthread`, mutexes, condition variables | 📝 Coming soon |
| 12 | [Lock-Free Ring Buffer](<Advanced C & C++ for Low-Level Systems/missions/12-lock-free-ring-buffer/>) | `std::atomic`, memory ordering, false sharing | 📝 Coming soon |
| 13 | [Self-Checking Harness](<Advanced C & C++ for Low-Level Systems/missions/13-self-checking-harness/>) | Golden vectors, randomized testing, reading generated assembly | 📝 Coming soon |
| 14 | [Zero-Allocation Log Streamer](<Advanced C & C++ for Low-Level Systems/missions/14-zero-allocation-log-streamer/>) | Ranges, views, `std::string_view` lifetimes | 📝 Coming soon |
| 15 | [Coroutine Task Dispatcher](<Advanced C & C++ for Low-Level Systems/missions/15-coroutine-task-dispatcher/>) | C++20 coroutines, promises, awaitables, schedulers | 📝 Coming soon |

**✅ Solved:** brief plus my full solution. **🚧 In progress:** brief plus a partial solution.
**📝 Coming soon:** the brief is ready, so you can do the mission now; my solution is added when it is done.

## Getting started

You need a C++20 compiler (GCC 11+ or Clang 14+) and `make`. On Ubuntu/Debian:

```bash
sudo apt install build-essential
```

Clone the repo:

```bash
git clone https://github.com/BenyHanonove/cpp-under-the-hood.git
```

Missions with a `Makefile` have two builds. `make test` uses AddressSanitizer and
UndefinedBehaviorSanitizer, and `make release` is an optimized `-O2` build:

```bash
make test
```

Single-file missions build with one command:

```bash
g++ -std=c++20 -Wall -Wextra -Wpedantic -Werror -O2 main.cpp -o main
```

Every solution must compile with **zero warnings** under `-Werror`, and the memory-handling missions
must also pass the sanitizers.

## Compiler optimization: the running thread

Several missions are built around seeing the optimizer at work instead of trusting claims about it:

- **Mission 03:** reproduce a strict-aliasing bug that only appears at `-O2`.
- **Mission 05:** what virtual functions cost you: the hidden vtable pointer in every object.
- **Mission 06:** measure which copies the compiler elides at `-O2` and which it keeps.
- **Mission 10:** move work to compile time with `constexpr` and `consteval`.
- **Mission 12:** replace mutexes with atomics and choose exactly the memory ordering you need.
- **Mission 13:** read the generated assembly to check claims about your code.

[Compiler Explorer (godbolt.org)](https://godbolt.org) is a good companion for every mission.

## Repository layout

```
.
├── Advanced C & C++ for Low-Level Systems/
│   ├── STYLE.md          # code conventions used by every mission
│   └── missions/         # the 15 missions, one folder each
├── build_guide/          # Python scripts that generate the companion guide
├── Silicon_Hardware_Security_Engineering_Guide.{html,pdf}   # companion reference guide
└── ROADMAP.md            # the wider learning plan these missions belong to
```

- **[STYLE.md](<Advanced C & C++ for Low-Level Systems/STYLE.md>)** explains the naming, formatting,
  and safety conventions, with the reason behind each rule.
- **The companion guide** (HTML/PDF) covers memory and registers, object layout, concurrency,
  ARM/RISC-V hardware, and security attacks in more depth.
- **[ROADMAP.md](ROADMAP.md)** shows where this goes next: RISC-V, SystemVerilog, and hardware
  security.

## Contributing

Found a bug in a solution, a clearer explanation, or a trap I missed? Open an issue or a pull
request. Alternative solutions are welcome too.

---

Made by **Benjamin** ([@BenyHanonove](https://github.com/BenyHanonove)). If this helped you, a ⭐ on the repo is appreciated.
