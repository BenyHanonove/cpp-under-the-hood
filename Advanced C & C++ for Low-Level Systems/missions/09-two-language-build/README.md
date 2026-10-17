# Mission 09: The Two-Language Build

| | |
|---|---|
| **Topic** | Translation units, headers, the one-definition rule, linkage, name mangling, C interoperability, build systems |
| **Standard** | C++20 with a C component |
| **Why here** | After Mission 08 — the first point where you have enough code to justify splitting it |
| **Status** | Not started |

## Mission Brief

Every mission so far has been a single source file. Real work is not: your thesis project is a C reference model, a C++ test harness, and thousands of lines of generated simulation code, compiled separately and linked together.

This mission is about what happens between compilation and a running binary — and about the fact that C and C++ do not speak to each other for free.

## Objectives

- [ ] Take one finished mission and split it properly into headers and implementation files, with a build of at least four translation units.
- [ ] Write a small numerical routine in **C**, and call it from a **C++** harness across a language boundary that actually links.
- [ ] Declare the boundary with C linkage, and inspect the symbol tables on both sides to see exactly what name mangling did.
- [ ] Design a header that is safe to include from both languages and from multiple translation units.
- [ ] Demonstrate the difference between internal and external linkage by creating a symbol collision at link time, then fixing it two different ways.
- [ ] Write a build file — Make or CMake — that compiles each unit separately, links them, and rebuilds only what changed.
- [ ] Build the same code once as a static library and once as a shared library, and observe how linking differs.

## Constraints & Edge Cases

- The one-definition rule is the core of this mission: understand which entities may appear in a header included many times and which may not, and what the linker does when the rule is broken.
- A definition placed in a header without the right specifier gives you a duplicate-symbol error; the same definition made *inconsistent* across units gives you no error at all and a corrupted program. The second failure mode is the dangerous one.
- A struct shared between the C and C++ sides must have identical layout in both, so Mission 03's padding rules apply directly.
- Nothing may cross the C boundary that C cannot represent — no references, no overloads, no templates, no exceptions escaping.
- Include order must never matter. If it does, a header is missing an include it depends on.
- Decide what belongs in the header versus the implementation file, and keep the header's dependencies minimal — compile time is a real cost at simulation scale.

## Why This Matters To You

The Verilator flow is precisely this shape: generated C++ model, your C++ testbench, your C reference implementation of the NTT, all linked into one binary that has to agree bit-for-bit on the data crossing between them.

## Definition of Done

A clean multi-unit build from a single command, an incremental rebuild that recompiles only the changed unit, and a working call in both directions across the C boundary with a struct passed intact.
