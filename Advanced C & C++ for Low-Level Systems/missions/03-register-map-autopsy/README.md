# Mission 03: The Register Map Autopsy

| | |
|---|---|
| **Topic** | Bit manipulation, `volatile` and MMIO, endianness, struct layout and padding, type punning, undefined behaviour |
| **Standard** | C++20 |
| **Why here** | Before Mission 08 — alignment and layout are prerequisites for the allocator |
| **Status** | Done |

## Mission Brief

Every other mission treats memory as a place to put objects. This one treats it as what it actually is on your target: a physical address space where a read has side effects, a write can start a state machine, and the byte order is a property of the wire rather than a detail you get to ignore.

You will model a peripheral's register map over a raw byte array, then deliberately walk into the undefined behaviour that eats low-level code, and learn to recognise each trap by sight.

## Objectives

- [x] Model a device register block over a raw, suitably aligned byte array standing in for physical memory.
- [x] Write field accessors built from masks and shifts: extract a bit range, insert a bit range without disturbing neighbours, set, clear, toggle, and test single bits.
- [x] Handle a status register whose bits are write-one-to-clear, and a control register with reserved bits that must be preserved on every read-modify-write.
- [x] Use `volatile` for the register accesses and be able to say precisely what it does and does not guarantee — specifically that it is about elision and reordering by the compiler, not about atomicity or visibility between threads.
- [x] Parse a multi-byte field from a buffer in both byte orders, without assuming the host's order, and detect the host's order at compile time.
- [x] Lay out a struct that mirrors a hardware packet, inspect its size, the offset of every member, and its padding; then reorder the members to shrink it without changing its contents.
- [x] Reinterpret a group of bytes as a typed value three ways — a byte-copy, a bit-level reinterpretation, and a pointer cast — and determine which are defined and which are not.

## Constraints & Edge Cases

- Shifting by an amount greater than or equal to the type's width is undefined, as is shifting a signed value into or past its sign bit. Both are routine in naive bit-field code.
- Signed integer overflow is undefined; unsigned wraps. Know which of your masks and counters is which, and remember that small integer types promote to `int` before the operation.
- Reading a value through a pointer to an unrelated type violates strict aliasing, and optimisers exploit this — the code will work at `-O0` and break at `-O2`. Reproduce this, do not take it on faith.
- Reading from a union member other than the one last written is not a portable punning technique in C++, whatever C allows.
- An unaligned access is undefined in the language and a fault or a silent penalty on real silicon.
- Never let a bitfield declaration be your hardware register layout: order, packing, and padding of bitfields are implementation-defined.
- A non-owning view over a buffer is the right parameter type here — pass a pointer-plus-length as one object rather than two arguments that can disagree.

## Why This Matters To You

Your Month-1 practical task is a C driver poking MMIO registers in a Verilator simulation, and Month 2 is polynomial arithmetic where a single misread word is an invisible cryptographic failure. Undefined behaviour in this layer does not crash — it produces a plausible wrong answer.

## Definition of Done

Every accessor is verified against hand-computed expected words; the whole mission is clean under `-fsanitize=undefined` at `-O2`; and you can point at each construct you tried and say whether the standard permits it.
