# Mission 11: The Multi-Stage Concurrent Thread Pipeline

| | |
|---|---|
| **Topic** | Multithreading, `std::jthread`, mutexes, condition variables, worker pools, cooperative cancellation |
| **Standard** | C++20 |
| **Status** | Not started |

## Mission Brief

Build a three-stage data processing pipeline that runs concurrently without races or deadlocks:

- **Stage 1 — Ingestion:** a thread that generates or reads raw events.
- **Stage 2 — Transform:** a pool of worker threads that parse and compute.
- **Stage 3 — Aggregation:** a thread that collects output and produces a summary.

The hard part is not starting threads. It is stopping them.

## Objectives

- [ ] Build thread-safe bounded queues connecting stage 1 to stage 2, and stage 2 to stage 3.
- [ ] Synchronise producers and consumers with a mutex, a lock guard that can be released while waiting, and a condition variable.
- [ ] Use auto-joining threads so that leaving the scope cannot leave a thread running.
- [ ] Implement cooperative cancellation so that a stop request drains the pipeline and shuts every stage down cleanly, including threads currently blocked waiting on an empty queue.

## Constraints & Edge Cases

- Must run clean under the thread sanitizer with zero reported races.
- Establish a single lock acquisition order, or take multiple locks together in one deadlock-free operation.
- Backpressure is required: when a queue is full, the producer waits rather than growing the queue.
- Every wait must re-check its condition on wake — spurious wakeups are real.
- Shutdown must not lose in-flight items silently, and must not hang because a waiter was never notified. Decide whether the pipeline drains or discards on stop, and document which.

## Definition of Done

Thread-sanitizer clean under sustained load, and a shutdown that terminates within a bounded time from any pipeline state — full queues, empty queues, mid-transform.
