# Mission 13: The Self-Checking Harness

| | |
|---|---|
| **Topic** | Test harness construction, golden vectors, randomised and directed testing, reading generated assembly |
| **Standard** | C++20 |
| **Why here** | Before Month 3 — its claims are about the machine, not the source |
| **Status** | Not started |

## Mission Brief

Nothing in Missions 01 through 12 asked you to prove your code works — you checked it by looking at output. That does not survive contact with a hardware project, where the reference model and the simulated design must agree on thousands of vectors and a single mismatched bit is the whole result.

You will build the harness yourself, with no external framework, and then learn to read what the compiler actually emitted — because for the security work ahead, the source code is not the artifact that runs.

## Objectives

- [ ] Build a minimal test runner: registered named cases, assertions that report file and line on failure, a pass/fail summary, and a process exit status a build system can act on.
- [ ] Add an assertion for comparing buffers that reports the first differing index and both values, not just "not equal".
- [ ] Drive one earlier mission from golden vectors held in a data file rather than hard-coded in the test.
- [ ] Add randomised testing with a seeded generator, where a failing seed is printed and can be replayed exactly.
- [ ] Cross-check two independent implementations of the same operation against each other on random input — the differential testing pattern your C model and RTL will use.
- [ ] Compile a small function and read the generated assembly: at no optimisation, then at `-O2`, and account for the differences.
- [ ] Write a comparison that branches on a secret value, inspect the emitted branch, then write the branch-free version and confirm in the assembly that the branch is gone at `-O2`.
- [ ] Write a routine that clears a sensitive buffer before returning, and check whether the optimiser deleted your clearing entirely.

## Constraints & Edge Cases

- A test that cannot fail is worse than no test. For every case, break the implementation on purpose and confirm the harness catches it.
- Randomised tests must be reproducible. An unseeded generator gives you a failure you can never see again.
- Timing measured in a loop from the host clock is not evidence of constant-time behaviour — the compiler, the cache, and the operating system all sit in the way. The emitted instruction stream is the evidence.
- The compiler is permitted to delete a write to memory that is never read again, which is exactly what secure zeroization looks like to it. Find out what your toolchain does and what defeats it.
- A constant-time source construct can be undone by the optimiser at any level. Anything you claim about timing must be re-verified at the optimisation level you actually ship.
- Test the boundaries, not the middle: empty input, one element, maximum capacity, capacity plus one.

## Why This Matters To You

Month 3 asks you to write a timing vulnerability and its constant-time fix, and to observe faulted state in a Verilator testbench. Both are claims about the machine, not about the source. This mission is where you learn to check the machine.

## Definition of Done

A reusable harness you will actually carry into the hardware missions, a deliberately broken implementation that it catches, a replayable random failure, and a before-and-after assembly listing where you can point to the branch that disappeared.
