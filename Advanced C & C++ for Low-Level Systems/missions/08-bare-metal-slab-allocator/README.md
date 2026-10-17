# Mission 08: The Bare-Metal Slab Allocator

| | |
|---|---|
| **Topic** | Custom allocation, placement new, explicit destructor calls, cache alignment |
| **Standard** | C++20 |
| **Status** | Not started |

## Mission Brief

The OS heap allocator is non-deterministic and fragments over time — unacceptable in a system with hard timing requirements. You will build a fixed-size slab allocator that manages one pre-allocated arena and hands out chunks in constant time.

This is the mission where allocation and construction stop being the same thing in your head.

## Objectives

- [ ] Pre-allocate one contiguous block of memory of fixed size, obtained exactly once at initialisation.
- [ ] Implement an intrusive free list: the bookkeeping for free slots lives inside the free slots themselves, using pointer arithmetic, with no secondary data structure.
- [ ] Align every slot boundary to satisfy the alignment requirement of the stored type, and consider cache-line alignment for the arena itself.
- [ ] Implement allocation that returns a free slot in constant time with no system call, then constructs the object in place inside that slot.
- [ ] Implement deallocation that explicitly invokes the object's destructor and returns the raw slot to the free list.

## Constraints & Edge Cases

- After initialisation, zero calls to `malloc` or ordinary `new`.
- Exhaustion must be handled deliberately: decide what happens when every slot is taken, and make it observable rather than undefined.
- Double-free must be either prevented or detected — decide which, and say why.
- Alignment must hold for over-aligned types, not just `int`; an unaligned access here is a real fault on real silicon.
- Constructing in place and forgetting the explicit destructor call is a silent leak of whatever the object owned. Make sure your teardown path cannot skip it.

## Definition of Done

Clean under `-fsanitize=address,undefined`, with a test that fills the arena completely, drains it, and refills it, proving slots are genuinely reused.
