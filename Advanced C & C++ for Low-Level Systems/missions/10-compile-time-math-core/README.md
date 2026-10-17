# Mission 10: The Type-Enforced Compile-Time Math Core

| | |
|---|---|
| **Topic** | Template metaprogramming, C++20 concepts, `constexpr`, `consteval` |
| **Standard** | C++20 |
| **Status** | Not started |

## Mission Brief

You are writing a coordinate and matrix transformation library for a guidance system. Where the inputs are known ahead of time, the arithmetic should be finished before the program ever runs — and a caller who passes a nonsensical type should be stopped by the compiler with a diagnostic a human can read.

## Objectives

- [ ] Define a `Numeric` concept: the type supports arithmetic operators, default construction, and comparison.
- [ ] Define a `Transformable` concept: the type exposes coordinate accessors returning something that satisfies `Numeric`.
- [ ] Write a `Vector3D` class template constrained so its element type must satisfy `Numeric`.
- [ ] Write dot product and cross product operations that are required to evaluate at compile time.
- [ ] Implement fixed-size matrix multiplication evaluated at compile time using ordinary loops in a `constexpr` context.

## Constraints & Edge Cases

- Instantiating the vector with an unsupported type (a string, for instance) must fail at compile time on the concept, not deep inside a template body.
- Be deliberate about the difference between "may run at compile time" and "must run at compile time", and pick each one on purpose.
- Verify the compile-time claim rather than assuming it: a value that truly is a compile-time constant can be used where the language demands one.
- Integer overflow is not permitted in a constant evaluation — know what your compiler does when it happens.
- Must build clean under `-std=c++20 -Wall -Wextra -Werror`.

## Definition of Done

Correct results for the runtime path, a compile-time path proven to be compile-time, and a deliberately broken instantiation whose error message you can read and explain.
