# Mission 12: The Lock-Free Ring Buffer

| | |
|---|---|
| **Topic** | `std::atomic`, memory ordering, false sharing, single-producer single-consumer queues |
| **Standard** | C++20 |
| **Status** | Not started |

## Mission Brief

Mutexes cost context switches. For low-latency telemetry you will build a single-producer, single-consumer circular buffer that relies only on atomic operations and the ordering guarantees they carry.

This is the mission that forces you to reason about what one core can see of another core's writes, and when.

## Objectives

- [ ] Allocate a power-of-two capacity buffer so that index wrapping is a bitwise operation rather than a division.
- [ ] Keep separate write and read indices, each held in an atomic.
- [ ] Place the two indices on separate cache lines so the producer and consumer do not fight over the same line.
- [ ] Implement a non-blocking push: read the consumer's index, decide whether space exists, write the element, then publish the new write index with release ordering.
- [ ] Implement a non-blocking pop: read the producer's index with acquire ordering, read the element, then publish the new read index with release ordering.
- [ ] For each atomic operation, be able to justify the ordering you chose and why a weaker one would break.

## Constraints & Edge Cases

- No mutexes, no locks, no sleeping or spinning in the critical path.
- Full and empty must be distinguishable — a naive equal-indices scheme makes them ambiguous, so choose your scheme and defend it.
- Index arithmetic must stay correct when the counters wrap around their own type's range.
- The element write must be visible to the consumer before the index that publishes it — that ordering is the entire correctness argument.
- Verify across genuinely parallel threads, not just interleaved execution on one core.

## Definition of Done

A long-running two-thread test transfers a known sequence with every item received exactly once, in order, with no duplicates or gaps — and the structure holds up under the thread sanitizer.
