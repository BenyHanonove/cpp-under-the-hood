#pragma once

#include <cstdio>

// How much a failed operation leaves intact
enum class Guarantee { Basic, Strong, Nothrow };

// Printable name of a guarantee level
inline const char* to_string([[maybe_unused]] Guarantee guarantee) {
    // TODO: return the matching name
    return "unknown";
}

// Print each Mission 02-06 operation with its guarantee
inline void print_guarantee_table() {
    // TODO: print header, then one line per classified operation
}
