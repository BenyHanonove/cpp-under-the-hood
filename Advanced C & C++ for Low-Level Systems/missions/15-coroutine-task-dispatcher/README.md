# Mission 15: The Asynchronous Coroutine Task Dispatcher

| | |
|---|---|
| **Topic** | C++20 coroutines, promise types, awaitables, schedulers, resumable workflows |
| **Standard** | C++20 |
| **Status** | Not started |

## Mission Brief

Cooperative multitasking built out of callbacks degenerates into unreadable nesting. You will implement the coroutine machinery from scratch — the return type, the promise, the awaitable, and the scheduler that drives them — so that suspension and resumption are things you control rather than magic.

This is the capstone: it uses the ownership discipline from Missions 02 through 08 and the concurrency reasoning from 11 and 12.

## Objectives

- [ ] Build a custom coroutine return type, `Task`, carrying a result.
- [ ] Implement its promise type, including:
  - [ ] the initial suspension policy — decide lazy or eager, and justify it;
  - [ ] a final suspension that prevents the frame from leaking;
  - [ ] result delivery to the caller;
  - [ ] capture of an escaping exception.
- [ ] Build a custom awaitable implementing the ready / suspend / resume contract.
- [ ] Build a scheduler that holds suspended coroutine handles in a queue and resumes them across ticks.
- [ ] Demonstrate several worker tasks that suspend on an await and report intermediate progress by yielding values.

## Constraints & Edge Cases

- No third-party coroutine libraries and no experimental headers.
- Every coroutine frame must be destroyed exactly once, on both the success and failure paths — a frame that is never resumed to completion still owns memory.
- An exception thrown inside a coroutine body must be captured by the promise and re-surface at the caller, not terminate the process.
- Be careful what a coroutine holds by reference: arguments bound by reference do not outlive the first suspension point.
- Resuming an already-completed coroutine is undefined behaviour — make that unreachable by construction.

## Definition of Done

Multiple tasks interleave under the scheduler in an observable order, every result and every exception reaches the caller, and the run is leak-free under the sanitizer.
