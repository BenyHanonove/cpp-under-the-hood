# Mission 02: The Manual Heap Vector

| | |
|---|---|
| **Topic** | Raw pointers, manual heap allocation, reference semantics, dynamic resizing |
| **Standard** | C++17 |
| **Status** | Not started |

## Mission Brief

`std::vector` has been decommissioned. You must build your own growing array of 32-bit integers from first principles, owning every byte of the buffer yourself.

This mission is where the ownership question first appears: who allocated this memory, who is allowed to hand it out, and who is responsible for giving it back.

## Objectives

- [ ] Build a struct or class holding exactly three raw members: a pointer to a heap buffer, a current element count, and an allocated capacity.
- [ ] Implement manual growth logic:
  - [ ] when an insert exceeds capacity, allocate a new buffer of double the capacity (starting at 2 when empty);
  - [ ] copy the existing elements across by hand;
  - [ ] release the old buffer.
- [ ] Implement append-at-the-end insertion.
- [ ] Implement indexed access that returns a reference, so callers can both read and write through it, with bounds checking.
- [ ] Implement cleanup that releases the buffer and resets the pointer and counters to a safe state.

## Constraints & Edge Cases

- No `std::vector`, no `std::allocator`, no smart pointers.
- Every array allocation must be matched by exactly one array deallocation — zero leaks under the sanitizer.
- Out-of-bounds access must take a distinct, deliberate error path rather than reading past the buffer.
- Growth must preserve element order and values exactly; reallocating invalidates any reference you previously handed out — know that this is true and be able to explain when it bites.
- Cleaning up twice must not corrupt the heap.

## Definition of Done

Runs clean under `-fsanitize=address,undefined` with no leaks reported, after a workload that forces at least three separate reallocations.
