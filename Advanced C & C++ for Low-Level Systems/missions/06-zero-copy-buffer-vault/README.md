# Mission 06: The Zero-Copy Buffer Vault

| | |
|---|---|
| **Topic** | Rvalue references, move semantics, ownership transfer, Rule of Five |
| **Standard** | C++17 / C++20 |
| **Status** | Done |

## Mission Brief

You are designing a high-throughput network packet buffer. Copying large payloads across boundaries is the bottleneck. Ownership must be able to move instantaneously, with no duplication of the underlying bytes.

Mission 04 taught you to copy correctly. This one teaches you when not to copy at all.

## Objectives

- [x] Build a `PacketBuffer` class managing a heap-allocated byte buffer and a size field.
- [x] Implement the complete Rule of Five:
  - [x] destructor;
  - [x] copy constructor (deep copy);
  - [x] copy assignment (deep copy);
  - [x] move constructor (steal the pointer, blank the source);
  - [x] move assignment (release what you hold, steal the pointer, blank the source).
- [x] Add static telemetry counters for copies and moves, so you can prove which operation actually ran.
- [x] Write a factory function that builds a buffer and returns it by value, then use the counters to observe whether a move happened or the compiler elided the operation entirely.

## Constraints & Edge Cases

- A moved-from object must remain valid and destructible: null pointer, zero size, no surprises.
- Destroying a moved-from object must not touch the buffer that was transferred away.
- Self-move-assignment must not destroy the object's own buffer.
- Move operations should be marked `noexcept`, and you should be able to say why containers care about that.
- Note honestly in your own notes when the counters show zero moves because of return value optimisation — that is a correct result, not a failed one.

## Definition of Done

Sanitizer-clean, plus a printed telemetry summary you can interpret: which paths copied, which moved, which were elided.
