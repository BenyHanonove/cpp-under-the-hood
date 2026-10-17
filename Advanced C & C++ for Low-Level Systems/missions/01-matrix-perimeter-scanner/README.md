# Mission 01: The Matrix Perimeter Scanner

| | |
|---|---|
| **Topic** | Fundamental types, scopes, 2D fixed arrays, conditionals, nested loops |
| **Standard** | C++17 |
| **Status** | Not started |

## Mission Brief

You are tapped to write a spatial scanner for an unmanned probe traversing an N x M grid. You cannot use dynamic memory or any container library. Everything lives on the stack in native fixed arrays.

The point of this mission is control over raw indexing: knowing exactly which cell you are standing on, which neighbours are legal to read, and where every variable begins and ends its life.

## Objectives

- [ ] Define compile-time integer constants for the dimensions `ROWS` and `COLS` (e.g. 6 x 6).
- [ ] Initialise a raw 2D array representing terrain elevation readings.
- [ ] Write a loop engine that walks the outer perimeter of the grid clockwise and calculates:
  - [ ] the total perimeter elevation sum;
  - [ ] the maximum elevation change between two adjacent boundary cells.
- [ ] Implement an inner search loop over the non-boundary cells that detects "peaks" — cells strictly greater than all four direct orthogonal neighbours.
- [ ] Maintain strict scope isolation: variables used inside loop checks must not leak out of the loop body.

## Constraints & Edge Cases

- Zero dynamic allocation. `new` and `malloc` are forbidden.
- Corner cells must be handled without a single out-of-bounds read — walking clockwise means each corner is visited exactly once.
- A flat grid (all values identical) must report zero peaks. Verify this, do not assume it.
- A grid small enough to have no interior (e.g. 2 x 2) must not crash the peak scan.

## Definition of Done

Compiles clean under `-std=c++17 -Wall -Wextra -Wpedantic -Werror -O2`, and you can state out loud why each boundary index is safe.
