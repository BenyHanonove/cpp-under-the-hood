# Mission 07: The Ownership Toolkit

| | |
|---|---|
| **Topic** | RAII, owning smart pointers, reference counting, exception safety, error handling without exceptions |
| **Standard** | C++17 / C++20 |
| **Why here** | Directly after Mission 06 — it is the payoff for move semantics |
| **Status** | Not started |

## Mission Brief

Missions 02 through 06 made you write ownership logic by hand, over and over, inside each class that happened to own something. That does not scale, and every hand-written cleanup path is a place to forget one.

Now you build the abstractions that make ownership a property of a *type* rather than a discipline you have to remember — and then you confront what happens to all of it when the target platform forbids exceptions.

## Objectives

- [ ] Build a move-only owning pointer: no copying, transfer on move, release on destruction, with operations to relinquish ownership and to replace the held resource.
- [ ] Extend it with a custom deleter, so it can own something released by a function other than the normal deallocator — a file handle, a memory-mapped region, an arena slot from Mission 08.
- [ ] Build a reference-counted owning pointer with a shared control block, releasing the resource when the last owner dies.
- [ ] Make the reference count atomic, and be able to say precisely which operations need which ordering — and why the count being atomic still does not make the pointed-to object thread-safe.
- [ ] Build a generic scope guard that runs an arbitrary action on scope exit, including on the exception path.
- [ ] Study the three exception-safety guarantees — basic, strong, nothrow — and classify each operation you wrote in Missions 02 through 06 into one of them.
- [ ] Build the same API twice: once reporting failure by exception, once returning a value-or-error type, and compare the call sites.

## Constraints & Edge Cases

- Self-assignment and self-move must be safe on every pointer type you write.
- A reference cycle between two counted pointers leaks forever and no sanitizer will call it a bug. Construct one deliberately, observe the leak, then describe the non-owning observer that breaks it.
- An operation that allocates and then throws must leave the object exactly as it was, not half-updated. This is what the strong guarantee costs.
- Compile at least one mission under `-fno-exceptions` and make it work. Firmware and many embedded toolchains build this way, so a design that can only report failure by throwing is unusable there.
- Understand what happens if a destructor throws during stack unwinding, and why destructors are implicitly `noexcept`.

## Why This Matters To You

Bare-metal firmware for your RISC-V core will almost certainly be built with exceptions disabled and no heap at all. Knowing both error-handling styles — and which resources a smart pointer cannot help you with — is what separates portable code from desktop code.

## Definition of Done

Both pointer types pass a stress test that constructs, moves, copies where legal, and destroys under sanitizers with zero leaks; the exception-free build compiles and behaves identically on the failure path.
