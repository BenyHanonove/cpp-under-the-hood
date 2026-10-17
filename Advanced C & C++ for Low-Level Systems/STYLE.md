# Code Conventions

The style rules for all fifteen missions. Pick these once, apply them everywhere, stop thinking about it.

There is no official C++ style. These choices are made to match three things you will actually be reading and linking against: the C++ standard library, C, and the firmware/hardware ecosystem (OpenTitan, Verilator, bare-metal RISC-V).

---

## 1. Files

| Extension | Contains |
|---|---|
| `.cpp` | C++ source |
| `.hpp` | Header only C++ will include — may contain classes, templates, namespaces |
| `.c` | C source |
| `.h` | Header that **C must also be able to include** — stays C-compatible |

- File names are `snake_case`: `packet_buffer.cpp`, `register_map.h`.
- A file that defines one main type is named after it: `PacketBuffer` lives in `packet_buffer.hpp` / `packet_buffer.cpp`.
- One mission per folder, no file shared across missions.
- A pure interface lives in `i<typename>.hpp`: `IPeripheral` is in `iperipheral.hpp`. The `i` prefix marks the file as a virtual struct.
- A mission with many files groups them by layer in subfolders (`hw/`, `devices/`, `bus/`, `demos/`). Includes are relative to the mission folder: `#include "devices/timer.hpp"`. Dependencies point one way, down the layers.

## 2. Naming

| Kind | Style | Example |
|---|---|---|
| Variable | `snake_case` | `last_value`, `head_index` |
| Function | `snake_case` | `read_register()`, `push_back()` |
| Type (class, struct, enum, concept) | `PascalCase` | `PacketBuffer`, `Timer`, `Numeric` |
| Interface (pure virtual struct) | `I` + `PascalCase` | `IPeripheral` |
| Private member (data and constants) | `_snake_case` with leading underscore, lowercase after it (see §4) | `_capacity`, `_buffer` |
| Constant | `snake_case` — **not** ALL_CAPS | `max_slots`, `cache_line_size` |
| Enumerator | `PascalCase` | `Status::ReadyToSend` |
| Namespace | `lowercase` | `hw`, `crypto` |
| Macro | `ALL_CAPS` with a prefix | `MISSION02_ASSERT` |
| Template parameter | `PascalCase` | `T`, `Element` |

The point of the type/variable split: `PacketBuffer buffer;` tells you which word is the type without a lookup.

## 3. Constants and macros

- `constexpr` for constants. Never a macro, never ALL_CAPS.
- ALL_CAPS is reserved for macros precisely *because* macros ignore scope. When your `MAX_SIZE` collides with a vendor header's `MAX_SIZE`, the preprocessor wins and the diagnostic is unreadable. Making ALL_CAPS mean "danger, no scope" is what keeps that rare.
- Prefix every macro you must write, so it cannot collide.
- Hardware register offset and field definitions are the traditional exception — ALL_CAPS there is expected, and they are usually macro-like anyway.

## 4. Reserved identifiers — a real rule, not a preference

Never write:

- an identifier starting with an underscore followed by a capital letter (`_Buffer`)
- an identifier containing a double underscore anywhere (`my__thing`)
- any identifier starting with an underscore at file scope

These are reserved for the implementation. `_PACKET_BUFFER_H_` as an include guard is undefined behaviour, and it is one of the most widely copied mistakes in C and C++.

Private members (`_capacity`) are the one place a leading underscore is allowed: they live in class scope, and the next character is always lowercase.

## 5. Headers

- Include guard named after the path, no leading underscore: `MISSION02_MANUAL_VECTOR_HPP`.
  (`#pragma once` is fine for C++-only headers and every real compiler supports it — but write real guards in any `.h` that C includes, for portability.)
- **Include order**, each group separated by a blank line:
  1. the header this source file implements — *first*, always
  2. C++ standard library
  3. system / third-party
  4. your project headers
  Putting your own header first is not cosmetic: it proves the header compiles standalone and is not silently relying on an include the `.cpp` happened to have above it.
- A header includes everything it uses and nothing it does not.
- Never `using namespace std;` in a header. Preferably not in a source file either — write `std::`.
- Headers declare; source files define. The exception is templates and `inline` functions, which must be visible wherever they are used.

## 6. Formatting

- 4 spaces, never tabs.
- Line length 100.
- Braces on **every** control-flow body, including single statements.
  This is a security rule, not a taste rule: Apple's `goto fail` TLS bug was a duplicated line under an unbraced `if` that skipped certificate validation entirely.
- Opening brace on the same line; `else` on the line after the closing brace.
- Pointer and reference bind to the **type**: `int* p`, `const PacketBuffer& buf`.
- One declaration per line. (`int* a, b;` does not do what it looks like — `b` is an `int`.)
- One blank line between functions; no blank line right after `{` or before `}`.

## 7. Types

- Fixed-width types at every hardware, protocol, or file-format boundary: `uint32_t`, `int16_t`. `int` does not promise you a width.
- `size_t` for sizes, counts, and indices into memory.
- `std::byte` or `uint8_t` for raw bytes — never `char`, whose signedness is implementation-defined.
- `nullptr`, never `NULL` or `0`.
- `enum class`, never bare `enum` — bare enumerators leak into the enclosing scope and convert to `int` silently.
- `auto` when the type is obvious from the right-hand side or unspeakable; the explicit type when it is documentation.

## 8. Const correctness

- `const` by default. A parameter, member function, or local that does not need to change is `const`.
- Every member function that does not modify state is `const`-qualified.
- Pass by `const&` for anything larger than a pointer; by value for fundamentals.
- Keep `const` on the left consistently (`const int*`) — just be consistent.

## 9. Functions and classes

- A function does one thing, and its name says what.
- `struct` for a pure interface: only pure virtual functions, no data members, no logic. `class` for everything with private state or invariants.
- Order class sections: `public`, then `protected`, then `private`.
- Initialise members in the member initialiser list, in declaration order — the compiler initialises them in declaration order regardless of what you write, and a mismatch is a warning you should never have to see.
- `explicit` on any single-argument constructor, to stop silent conversions.
- `override` on every override. `final` where it applies.
- Declare `noexcept` where it is true and useful — move operations especially.

## 10. C interoperability (Mission 09 onward)

- Wrap the declarations in a shared header with C linkage, guarded so the C compiler never sees the C++ construct.
- Nothing crosses the boundary that C cannot express: no references, no overloads, no templates, no default arguments, no exceptions escaping.
- A struct shared across the boundary must have identical layout on both sides — verify the size and member offsets rather than assuming.
- Use fixed-width types for every field that crosses.

## 11. Hardware-facing code (Mission 03 onward)

- `volatile` only on actual memory-mapped register access, never as a threading tool — it says nothing about atomicity or inter-thread visibility.
- Name registers and fields after the datasheet, exactly. When the manual says `CTRL.START`, do not invent a better name.
- Never assume host byte order; convert explicitly at the boundary.
- Never let a bitfield declaration define a hardware layout — bitfield ordering and packing are implementation-defined. Masks and shifts only.

## 12. Build and verification

Every mission compiles clean at:

    g++ -std=c++20 -Wall -Wextra -Wpedantic -Werror -O2

Missions 02, 04, 06, 07, 08 additionally:

    g++ -std=c++20 -fsanitize=address,undefined -g

Missions 11, 12 additionally:

    g++ -std=c++20 -fsanitize=thread -g

(If ThreadSanitizer reports `unexpected memory mapping`, that is this machine's ASLR entropy, not your bug — run the binary under `setarch $(uname -m) -R ./binary`.)

`-Werror` is not negotiable. A warning you have decided to ignore is a warning you will stop reading.

## 13. Comments

- One line per comment, 7–10 words at most. No multi-line comment blocks.
- Comment *why*, never *what*. The code already says what.
- Document every non-obvious invariant, ownership rule, and lifetime assumption — especially who frees what.
- Where you rely on a subtle guarantee (a memory ordering, an alignment, an aliasing rule), write down which guarantee and why it holds. In six months that comment is the only thing standing between you and a rewrite.
- No commented-out code. That is what version control is for.
