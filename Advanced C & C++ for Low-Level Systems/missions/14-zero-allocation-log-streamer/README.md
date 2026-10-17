# Mission 14: The Zero-Allocation Log Streamer

| | |
|---|---|
| **Topic** | C++20 ranges and views, `std::string_view`, lifetime of non-owning references |
| **Standard** | C++20 |
| **Status** | Not started |

## Mission Brief

You are ingesting multi-gigabyte access logs. You cannot load the file into memory, and you cannot afford a small heap string per token. Build a zero-copy parser as a declarative pipeline over a read-only buffer, where every token is a view into bytes you already have.

## Objectives

- [ ] Read log lines directly out of a read-only buffer or memory-mapped file, never materialising owning strings.
- [ ] Build a view pipeline that:
  - [ ] drops comments and blank lines;
  - [ ] splits each line into fields on a delimiter;
  - [ ] transforms raw slices into typed descriptors;
  - [ ] stops after the first K records meeting a severity condition.
- [ ] Chain the whole thing into a single readable declarative expression rather than a nest of loops.
- [ ] Confirm the pipeline is lazy: with an early stop, the tail of the input is never touched.

## Constraints & Edge Cases

- Zero allocations inside the parsing loop. Measure it rather than trusting it.
- Lifetime is the real hazard here: a view must never outlive the buffer it points into, and it must never point into a temporary that dies at the end of the expression.
- Handle malformed records, empty fields, and a trailing separator without dropping or inventing a record.
- A final line with no terminating newline must still be parsed.
- Numeric conversion from a view must not require a null-terminated copy.

## Definition of Done

Identical results to a straightforward loop-based parser on the same input, with an allocation count of zero in the hot loop and no dangling views under the sanitizer.
